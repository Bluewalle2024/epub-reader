#!/usr/bin/env python3
"""EPUB 整本书阅读器 v2.2 — Python FastAPI 后端"""

# ======================================================================
# 区域 1: 配置常量
# ======================================================================
import os
import re
import io
import json
import pickle
import hashlib
import asyncio
import tempfile
import zipfile
import logging
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import httpx
import tiktoken
import regex
from ebooklib import epub
from bs4 import BeautifulSoup
from starlette.middleware.base import BaseHTTPMiddleware

PORT = 8765
OLLAMA_URL = "http://localhost:11434"
DEFAULT_CONTEXT_LIMIT = 48000
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB

# 从环境变量读取，否则稍后从 vault API Key.md 读取
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY") or ""
VAULT_PATH = os.environ.get("OBSIDIAN_VAULT_PATH") or ""

# ======================================================================
# 区域 1b: 启动时动态获取的配置
# ======================================================================
_default_ollama_model = ""
_ollama_context_length = 32768
_ollama_tokens_api_ok = True  # 首次 404 后置 False，避免重复无效请求

# ======================================================================
# FastAPI 应用
# ======================================================================
app = FastAPI(title="EPUB 整本书阅读器")

# ======================================================================
# 区域 1c: Pydantic 模型
# ======================================================================
class CountTokensRequest(BaseModel):
    text: str
    model: str = ""

class CountTokensBatchRequest(BaseModel):
    texts: list[str]
    model: str = ""

class LoadEpubRequest(BaseModel):
    book_name: str = ""
    from_cache: bool = False

class ChatRequest(BaseModel):
    model: str
    chapters_text: str = ""
    book_name: str = ""
    history: list[dict] = []
    question: str = ""
    context_limit: int = 48000
    system_prompt: str = ""

class SaveRequest(BaseModel):
    book_name: str
    messages: list[dict]

# ======================================================================
# 缓存存储（服务重启后可从磁盘恢复，内存中加速访问）
# ======================================================================
_loaded_books: dict[str, dict] = {}  # name → parsed result (LRU, max 3)
_loaded_books_order: list[str] = []  # LRU 访问顺序，最近使用的在末尾

# ======================================================================
# 区域 2: 纯函数（无副作用，不依赖全局状态）
# ======================================================================

# ── 2.1 Token 估算 ──

def heuristic_token_count(text: str, model: str = "") -> int:
    """
    纯本地快速 token 估算。解析阶段使用，避免调 Ollama API 阻塞。
    根据模型族使用不同的 char/token 系数。

    Qwen 系列:   中文 ~1.7 char/token, 英文 ~3.5 char/token
    Llama/Mistral: 中文 ~0.8 char/token (BPE 对中文不友好), 英文 ~3.8 char/token
    其他:          中文 ~1.2 char/token, 英文 ~3.8 char/token (通用保守估算)
    """
    cn = len(regex.findall(r'\p{Han}', text))
    other = len(text) - cn

    m = model.lower()
    if 'qwen' in m:
        return int(cn / 1.7 + other / 3.5)
    elif any(x in m for x in ('llama', 'mistral', 'mixtral')):
        return int(cn / 0.8 + other / 3.8)
    else:
        return int(cn / 1.2 + other / 3.8)


# DeepSeek 用 cl100k_base（偏差 <5%）
_ENC_DS = tiktoken.get_encoding("cl100k_base")

def _estimate_tokens_deepseek(text: str) -> int:
    """DeepSeek 用 cl100k_base（偏差 <5%）"""
    return len(_ENC_DS.encode(text))


async def _estimate_tokens_ollama(text: str, model: str) -> int:
    """
    通过 Ollama 原生 API 获取准确 token 数。
    API: POST /api/tokens  (Ollama >= 0.4.0 支持)
    超时 5s，失败或 404 回退到 heuristic_token_count。
    首次 404 后缓存结果，后续不再尝试 API。
    """
    global _ollama_tokens_api_ok

    if not model or not _ollama_tokens_api_ok:
        return heuristic_token_count(text, model)

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{OLLAMA_URL}/api/tokens",
                json={"model": model, "prompt": text},
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                tokens = data.get("tokens", [])
                return len(tokens) if isinstance(tokens, list) else int(tokens)
            elif resp.status_code == 404:
                _ollama_tokens_api_ok = False
                logging.info("Ollama /api/tokens 不可用（404），后续将使用启发式估算")
    except Exception:
        pass

    return heuristic_token_count(text, model)


async def estimate_tokens(text: str, model: str = "") -> int:
    """
    统一入口：根据 model 前缀选择 tokenizer。
    - "deepseek:xxx" → tiktoken cl100k_base
    - "ollama:xxx" / 无前缀 → Ollama 原生 API（回退启发式）
    """
    if model.startswith("deepseek"):
        return _estimate_tokens_deepseek(text)
    else:
        if model.startswith("ollama:"):
            ollama_model = model.replace("ollama:", "")
        elif _default_ollama_model:
            ollama_model = _default_ollama_model
        else:
            return heuristic_token_count(text)
        return await _estimate_tokens_ollama(text, ollama_model)


# ── 2.2 中文过滤 ──

def filter_chinese_only(text: str, threshold: float = 0.5) -> str:
    """
    过滤非中文内容，仅保留中文为主的段落。

    策略（按段落处理）:
    1. 将文本按换行符拆分为段落
    2. 每个段落用 regex.findall(r'\\p{Han}', line) 计算中文字符数
       - \\p{Han} 自动覆盖 CJK 基本区 + Extension A~H + 兼容汉字
    3. 占比 >= threshold 的段落保留，否则丢弃
    4. 保留的段落重新拼接
    """
    lines = text.split('\n')
    result = []

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            result.append('')
            continue

        cn_chars = len(regex.findall(r'\p{Han}', line_stripped))
        total_chars = len(regex.sub(r'\s', '', line_stripped))

        if total_chars == 0:
            result.append('')
        elif cn_chars / total_chars >= threshold:
            result.append(line_stripped)

    return '\n'.join(result)


# ── 2.3 章节文本提取 ──

def extract_chapter_text(html_content: str) -> str:
    """从 HTML 内容中提取纯文本，保留段落结构。"""
    soup = BeautifulSoup(html_content, 'html.parser')

    # 移除脚本和样式
    for tag in soup.find_all(['script', 'style', 'nav', 'header', 'footer']):
        tag.decompose()

    # 提取文本，用换行分隔块级元素
    block_tags = {'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'br', 'tr', 'blockquote'}
    parts = []

    for element in soup.descendants:
        if element.name in block_tags:
            parts.append('\n')
        if isinstance(element, str):
            text = element.strip()
            if text:
                parts.append(text)

    raw = ''.join(parts)
    # 合并多余空行
    raw = re.sub(r'\n{3,}', '\n\n', raw)
    return raw.strip()


# ── 2.4 书名提取 ──

def extract_book_name(epub_book, fallback_filename: str = "") -> str:
    """
    优先级:
    1. EPUB metadata dc:title（通过 ebooklib 获取）
    2. content.opf 中的 <dc:title>
    3. toc.ncx 中的 <docTitle> / nav.xhtml 中的 <title>
    4. 文件名（去掉扩展名）
    """
    # 方法 1: ebooklib metadata
    try:
        titles = epub_book.get_metadata('DC', 'title')
        if titles:
            return titles[0][0]
    except Exception:
        pass

    # 方法 2: 直接从 OPF 读取
    try:
        for item in epub_book.get_items():
            if item.get_type() == 9 and ('nav' in item.get_name().lower() or 'title' in item.get_name().lower()):
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                title_tag = soup.find('title')
                if title_tag and title_tag.get_text(strip=True):
                    return title_tag.get_text(strip=True)
    except Exception:
        pass

    # 方法 3: 文件名
    if fallback_filename:
        name = fallback_filename
        # 去掉扩展名
        if '.' in name:
            name = name.rsplit('.', 1)[0]
        return name

    return "未命名"


# ── 2.5 EPUB3 nav.xhtml 目录提取 ──

def extract_toc(epub_book, spine_items: list) -> list[dict]:
    """
    TOC 提取优先级:
    1. nav.xhtml (EPUB3) — 解析 <nav epub:type="toc"> 中的 <ol>/<li>/<a>
    2. toc.ncx (EPUB2) — 通过 ebooklib 内置 toc
    3. spine 中的 <h1>-<h6> 标签 — 自动生成章节标题
    4. 数字序号兜底 — "第N章"
    """
    # 方法 1: EPUB3 nav.xhtml
    for item in epub_book.get_items_of_type(9):  # ITEM_DOCUMENT = 9
        try:
            if 'nav' in item.get_name().lower():
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                toc_nav = soup.find('nav', attrs={'epub:type': 'toc'})
                if toc_nav:
                    ol = toc_nav.find('ol')
                    if ol:
                        return _parse_nav_list(ol)
        except Exception:
            continue

    # 方法 2: EPUB2 toc.ncx（通过 ebooklib 内置方法）
    if epub_book.toc:
        try:
            return _parse_ebooklib_toc(epub_book.toc)
        except Exception:
            pass

    # 方法 3: 从 spine 文档的 h1-h6 提取
    return _extract_from_headings(spine_items)


def _parse_nav_list(ol) -> list[dict]:
    """解析 EPUB3 nav.xhtml 中的 <ol> 列表。"""
    chapters = []
    if not ol:
        return chapters

    for li in ol.find_all('li', recursive=False):
        a_tag = li.find('a')
        if a_tag:
            title = a_tag.get_text(strip=True)
            href = a_tag.get('href', '')
            chapters.append({'title': title, 'href': href})

        # 递归处理嵌套列表
        nested_ol = li.find('ol')
        if nested_ol:
            chapters.extend(_parse_nav_list(nested_ol))

    return chapters


def _parse_ebooklib_toc(toc) -> list[dict]:
    """解析 ebooklib 的 TOC 对象。"""
    chapters = []

    def walk(items):
        for item in items:
            if isinstance(item, tuple):
                # epub.Section
                chapters.append({'title': item[0].title or '', 'href': item[0].href or ''})
                if len(item) > 1 and item[1]:
                    walk(item[1])
            elif isinstance(item, epub.Link):
                chapters.append({'title': item.title or '', 'href': item.href or ''})

    walk(toc)
    return chapters


def _extract_from_headings(spine_items: list) -> list[dict]:
    """从 spine 文档的 h1-h6 提取章节标题。"""
    chapters = []
    for item in spine_items:
        try:
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            for heading in soup.find_all(['h1', 'h2', 'h3']):
                title = heading.get_text(strip=True)
                if title and len(title) > 1:
                    chapters.append({'title': title, 'href': ''})
        except Exception:
            continue

    # 如果什么都没提取到，用数字序号
    if not chapters:
        chapters = [{'title': f'第{i+1}章', 'href': ''} for i in range(len(spine_items))]

    return chapters


# ── 2.6 EPUB 解析（同步，运行在线程池中）──

def _parse_epub_sync(file_data: bytes, filename: str = "") -> dict:
    """
    四级降级策略，每一级失败自动进入下一级:
    Level 0: ebooklib 标准解析
    Level 1: OPF 修复 → 重建 content.opf 后再用 ebooklib
    Level 2: ZIP 修复 → 修复损坏的 ZIP 结构后提取
    Level 3: 原始 ZIP 遍历 → 放弃 EPUB 结构，直接从 zip 提取所有文本

    返回: {name, chapters, repair_level}
    """

    # ── Level 0: 标准解析 ──
    try:
        book = epub.read_epub(io.BytesIO(file_data))
        spine_items = _get_spine_items(book)
        chapters = _extract_chapters_from_items(book, spine_items)

        if len(chapters) > 0 and sum(len(ch.get('text', '')) for ch in chapters) > 500:
            name = extract_book_name(book, filename)
            return {
                "name": name,
                "chapters": chapters,
                "repair_level": 0
            }
    except Exception as e:
        logging.warning(f"Level 0 解析失败: {e}")

    # ── Level 1: OPF 修复 ──
    try:
        book = _repair_opf_and_parse(file_data)
        if book:
            spine_items = _get_spine_items(book)
            chapters = _extract_chapters_from_items(book, spine_items)
            if len(chapters) > 0:
                name = extract_book_name(book, filename) + " [OPF已修复]"
                return {
                    "name": name,
                    "chapters": chapters,
                    "repair_level": 1
                }
    except Exception as e:
        logging.warning(f"Level 1 OPF 修复失败: {e}")

    # ── Level 2: ZIP 宽松提取 ──
    try:
        chapters = _extract_from_zip_loose(file_data)
        if len(chapters) > 0:
            name = filename + " [ZIP已修复]" if filename else "未知 [ZIP已修复]"
            return {
                "name": name,
                "chapters": chapters,
                "repair_level": 2
            }
    except Exception as e:
        logging.warning(f"Level 2 ZIP 修复失败: {e}")

    # ── Level 3: 原始字节级提取 ──
    try:
        chapters = _extract_raw_text(file_data)
        if len(chapters) > 0:
            name = filename + " [原始提取]" if filename else "未知 [原始提取]"
            return {
                "name": name,
                "chapters": chapters,
                "repair_level": 3
            }
    except Exception as e:
        logging.warning(f"Level 3 原始提取失败: {e}")

    # 彻底失败
    raise HTTPException(
        status_code=422,
        detail="无法解析此 EPUB，文件可能受 DRM 保护或为纯图片格式"
    )


def _get_spine_items(book) -> list:
    """按 spine 顺序获取文档项。"""
    spine_ids = []
    for item_id, _ in book.spine:
        spine_ids.append(item_id)

    items = []
    for item_id in spine_ids:
        item = book.get_item_with_id(item_id)
        if item:
            items.append(item)

    # 如果 spine 为空，获取所有文档
    if not items:
        items = list(book.get_items_of_type(9))  # ITEM_DOCUMENT

    return items


def _extract_chapters_from_items(book, spine_items: list) -> list[dict]:
    """从 spine items 提取章节，使用 TOC 标题。"""
    toc = extract_toc(book, spine_items)

    chapters = []
    for i, item in enumerate(spine_items):
        try:
            content = item.get_content().decode('utf-8', errors='replace')
        except Exception:
            try:
                content = item.get_content().decode('gbk', errors='replace')
            except Exception:
                content = item.get_content().decode('latin-1', errors='replace')

        raw_text = extract_chapter_text(content)
        if not raw_text or len(raw_text) < 20:
            continue

        cn_text = filter_chinese_only(raw_text)
        if not cn_text.strip():
            cn_text = raw_text

        # 标题：优先用 TOC，其次用 heading，最后用序号
        title = ""
        if i < len(toc):
            title = toc[i].get('title', '')
        if not title:
            title = f"第{i+1}章"

        chapters.append({
            "title": title,
            "text": raw_text,
            "text_cn": cn_text,
            "tokens_approx": heuristic_token_count(raw_text, "")
        })

    # 清理重复标题
    _deduplicate_titles(chapters)

    return chapters


def _deduplicate_titles(chapters: list):
    """去重章节标题。"""
    seen = {}
    for i, ch in enumerate(chapters):
        title = ch['title']
        if title in seen:
            seen[title] += 1
            ch['title'] = f"{title} ({seen[title]})"
        else:
            seen[title] = 1


def _repair_opf_and_parse(file_data: bytes):
    """
    Level 1: 重建 OPF。扫描所有 .xhtml/.html，自动生成 spine，
    从 toc.ncx 或 nav.xhtml 提取目录，重建最小可用的 content.opf。
    """
    try:
        zf = zipfile.ZipFile(io.BytesIO(file_data), 'r')
        file_list = zf.namelist()

        # 找所有文档文件
        doc_files = [f for f in file_list if f.lower().endswith(('.xhtml', '.html', '.htm'))]
        if not doc_files:
            zf.close()
            return None

        # 找 TOC 文件
        toc_ncx = next((f for f in file_list if f.lower().endswith('.ncx')), None)
        nav_file = next((f for f in doc_files if 'nav' in f.lower()), None)

        # 构建最小 OPF
        opf_xml = _build_minimal_opf(doc_files, toc_ncx or nav_file)
        opf_path = 'OEBPS/content.opf'

        # 重新打包为内存中的 EPUB
        new_buf = io.BytesIO()
        with zipfile.ZipFile(new_buf, 'w', zipfile.ZIP_DEFLATED) as new_zf:
            # 添加 mimetype
            new_zf.writestr('mimetype', 'application/epub+zip')
            # 复制原有文件
            for name in file_list:
                if name == 'mimetype':
                    continue
                try:
                    data = zf.read(name)
                    new_zf.writestr(name, data)
                except Exception:
                    continue
            # 写入修复后的 OPF
            new_zf.writestr(opf_path, opf_xml)

        zf.close()
        new_buf.seek(0)

        # 尝试用修复后的文件解析
        book = epub.read_epub(new_buf)
        return book
    except Exception:
        return None


def _build_minimal_opf(doc_files: list, toc_file: str = None) -> str:
    """生成最小可用的 content.opf。"""
    import xml.etree.ElementTree as ET

    package = ET.Element('package', {
        'xmlns': 'http://www.idpf.org/2007/opf',
        'version': '3.0',
        'unique-identifier': 'book-id'
    })

    metadata = ET.SubElement(package, 'metadata')
    ET.SubElement(metadata, 'dc:identifier', {'id': 'book-id'}).text = 'repaired-epub'
    ET.SubElement(metadata, 'dc:title').text = '已修复的 EPUB'

    manifest = ET.SubElement(package, 'manifest')
    spine = ET.SubElement(package, 'spine')

    if toc_file:
        ET.SubElement(manifest, 'item', {
            'id': 'toc', 'href': toc_file, 'media-type': 'application/xhtml+xml'
        })

    for i, f in enumerate(doc_files):
        item_id = f'item_{i}'
        ET.SubElement(manifest, 'item', {
            'id': item_id, 'href': f, 'media-type': 'application/xhtml+xml'
        })
        ET.SubElement(spine, 'itemref', {'idref': item_id})

    return ET.tostring(package, encoding='unicode')


def _extract_from_zip_loose(file_data: bytes) -> list[dict]:
    """
    Level 2: ZIP 宽松提取。
    用 zipfile 打开，逐个 try/except 提取每个成员（跳过损坏文件），
    对每个成功提取的 .xhtml/.html 用 BeautifulSoup 解析。
    """
    chapters = []
    try:
        zf = zipfile.ZipFile(io.BytesIO(file_data), 'r')
        members = zf.infolist()

        doc_members = [m for m in members if m.filename.lower().endswith(('.xhtml', '.html', '.htm'))]

        for i, member in enumerate(doc_members):
            try:
                data = zf.read(member.filename)
                # 尝试多种编码
                content = None
                for enc in ['utf-8', 'gbk', 'latin-1', 'cp1252']:
                    try:
                        content = data.decode(enc)
                        break
                    except Exception:
                        continue
                if not content:
                    content = data.decode('utf-8', errors='replace')

                raw_text = extract_chapter_text(content)
                if not raw_text or len(raw_text) < 20:
                    continue

                cn_text = filter_chinese_only(raw_text)
                if not cn_text.strip():
                    cn_text = raw_text

                chapters.append({
                    "title": f"片段{i+1}",
                    "text": raw_text,
                    "text_cn": cn_text,
                    "tokens_approx": heuristic_token_count(raw_text, "")
                })
            except Exception:
                continue

        zf.close()
    except Exception:
        pass

    return chapters


def _extract_raw_text(file_data: bytes) -> list[dict]:
    """
    Level 3: 原始字节级提取。
    放弃 EPUB 结构，暴力提取所有可见文本片段。
    """
    chunks = []
    # 尝试多种编码
    for encoding in ['utf-8', 'gbk', 'latin-1', 'cp1252']:
        try:
            text = file_data.decode(encoding, errors='replace')
            break
        except Exception:
            continue
    else:
        text = file_data.decode('utf-8', errors='replace')

    # 正则匹配 HTML 标签之间的可见文本
    # 移除标签，提取文本块
    clean = re.sub(r'<[^>]+>', '\n', text)
    clean = re.sub(r'&[a-z]+;', ' ', clean)
    clean = re.sub(r'\n{3,}', '\n\n', clean)

    # 按段落分割，过滤短碎片
    paragraphs = [p.strip() for p in clean.split('\n') if len(p.strip()) >= 20]
    if not paragraphs:
        return chunks

    # 简单分组（每 5 段一组）
    group_size = max(5, len(paragraphs) // 20)
    for i in range(0, len(paragraphs), group_size):
        chunk_text = '\n\n'.join(paragraphs[i:i + group_size])
        cn_text = filter_chinese_only(chunk_text)
        if not cn_text.strip():
            cn_text = chunk_text
        chunks.append({
            "title": f"片段{i // group_size + 1}",
            "text": chunk_text,
            "text_cn": cn_text,
            "tokens_approx": heuristic_token_count(chunk_text, "")
        })

    return chunks


# ── 2.7 异步包装 ──

async def parse_epub(file_data: bytes, filename: str = "") -> dict:
    """
    CPU 密集的 EPUB 解析放入线程池，不阻塞 asyncio 事件循环。
    解析完成后缓存到临时文件，服务重启后可从缓存恢复。
    """
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, _parse_epub_sync, file_data, filename)

    # 缓存到持久化目录 ~/.epub-reader/cache/（服务重启/系统重启后仍可恢复）
    # 注意：必须用 hashlib 而非 hash()——后者受 PYTHONHASHSEED 影响，进程重启后值不同
    try:
        cache_key = hashlib.md5(result['name'].encode()).hexdigest()
        cache_dir = Path.home() / ".epub-reader" / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path = cache_dir / f"{cache_key}.cache"
        cache_path.write_bytes(pickle.dumps(result))
    except Exception:
        pass  # 缓存失败不影响主流程

    # 内存缓存（LRU，最多 3 本）
    _add_to_memory_cache(result['name'], result)

    return result


def _add_to_memory_cache(name: str, data: dict):
    """将书籍加入内存缓存，LRU 淘汰超出 3 本的最久未用书籍。"""
    if name in _loaded_books_order:
        _loaded_books_order.remove(name)
    _loaded_books_order.append(name)
    _loaded_books[name] = data

    # 淘汰最久未用的（超出 3 本）
    while len(_loaded_books_order) > 3:
        old_name = _loaded_books_order.pop(0)
        if old_name in _loaded_books:
            del _loaded_books[old_name]
            logging.info(f"LRU 淘汰内存缓存: {old_name}")


def load_cached_epub(book_name: str) -> dict | None:
    """尝试从缓存恢复已解析的 EPUB。"""
    # 先检查内存缓存
    if book_name in _loaded_books:
        return _loaded_books[book_name]

    # 再检查磁盘缓存（~/.epub-reader/cache/）
    cache_key = hashlib.md5(book_name.encode()).hexdigest()
    cache_dir = Path.home() / ".epub-reader" / "cache"
    cache_path = cache_dir / f"{cache_key}.cache"
    if cache_path.exists():
        try:
            data = pickle.loads(cache_path.read_bytes())
            _add_to_memory_cache(book_name, data)
            return data
        except Exception:
            cache_path.unlink(missing_ok=True)
    return None


def _save_raw_epub(file_data: bytes, book_name: str):
    """保存原始 EPUB 文件到 ~/.epub-reader/books/，供后续自动重解析。"""
    try:
        books_dir = Path.home() / ".epub-reader" / "books"
        books_dir.mkdir(parents=True, exist_ok=True)
        safe_name = sanitize_filename(book_name)
        epub_path = books_dir / f"{safe_name}.epub"
        epub_path.write_bytes(file_data)
        logging.info(f"原始 EPUB 已保存: {epub_path}")
    except Exception as e:
        logging.warning(f"保存原始 EPUB 失败: {e}")


async def _reparse_from_saved_epub(book_name: str) -> dict | None:
    """从本地保存的原始 EPUB 文件重新解析。"""
    books_dir = Path.home() / ".epub-reader" / "books"
    safe_name = sanitize_filename(book_name)
    epub_path = books_dir / f"{safe_name}.epub"
    if not epub_path.exists():
        return None
    try:
        file_data = epub_path.read_bytes()
        result = await parse_epub(file_data, f"{book_name}.epub")
        logging.info(f"从本地 EPUB 重新解析成功: {book_name}")
        return result
    except Exception as e:
        logging.warning(f"从本地 EPUB 重新解析失败: {e}")
        return None


# ── 2.8 安全文件名 ──

def sanitize_filename(name: str, max_length: int = 80) -> str:
    """
    三层安全过滤：
    1. 移除所有控制字符、路径分隔符和特殊字符
    2. 防止 .. 路径穿越和隐藏文件写入
    3. 长度截断 + 空文件名兜底
    """
    # 第一层：移除控制字符 + 危险字符
    # 注意：用双引号 raw string 避免 r'...\'...' 中 \' 提前终止字符串
    safe = re.sub(r"[\x00-\x1f<>:\"/\\|?*'`$&;!@#%^(){}\[\]~]", '', name)

    # 第二层：防止路径穿越
    safe = re.sub(r'\.{2,}', '.', safe)
    safe = re.sub(r'^\.+', '', safe)
    safe = safe.strip()

    # 第三层：空文件名兜底 + 长度截断
    if not safe:
        safe = "untitled"
    if len(safe) > max_length:
        safe = safe[:max_length]

    return safe


def build_save_path(vault_path: str, book_name: str, timestamp: str) -> Path:
    """
    构造安全的保存路径。
    确保最终文件始终在 vault_path 范围内，防止路径穿越攻击。
    """
    vault = Path(vault_path).resolve()
    safe_name = sanitize_filename(book_name)
    filename = f"{safe_name}_对话_{timestamp}.md"

    target_dir = vault / "Inbox" / "Epub阅读"
    filepath = (target_dir / filename).resolve()

    # 最终防线：确保结果在 vault 内
    if not str(filepath).startswith(str(vault) + os.sep) and str(filepath) != str(vault):
        raise ValueError(f"路径穿越检测：{filepath} 不在 vault 范围内")

    return filepath


# ======================================================================
# 区域 2b: 流式对话
# ======================================================================

async def stream_ollama(model: str, messages: list, num_ctx: int = 48000):
    """
    num_ctx 从设置面板读取，直接覆盖 Ollama modelfile 中默认的 context_length。
    Qwen 2.5 7B 原生支持 128K。
    """
    ollama_model = model.replace("ollama:", "") if model.startswith("ollama:") else model

    # 如果 messages 已经包含 system prompt（来自 /api/chat 的自定义提示词），不再重复添加
    if messages and messages[0].get("role") == "system":
        full_messages = messages
    else:
        full_messages = [
            {"role": "system", "content": "你是博学的阅读助手。优先基于提供的原文内容回答，引用原文作为依据。如果问题超出原文范围，可以结合你的知识回答，但要明确区分哪些来自原文、哪些来自你的知识。如果完全不知道答案，请诚实说明，不要编造信息。"}
        ] + messages

    async with httpx.AsyncClient(timeout=300) as client:
        try:
            async with client.stream('POST', f'{OLLAMA_URL}/api/chat', json={
                'model': ollama_model,
                'messages': full_messages,
                'stream': True,
                'options': {'num_ctx': num_ctx}
            }) as resp:
                if resp.status_code != 200:
                    body = await resp.aread()
                    yield f"data: {json.dumps({'error': f'Ollama 响应错误 (HTTP {resp.status_code})'})}\n\n"
                    yield "data: [DONE]\n\n"
                    return

                async for line in resp.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            content = data.get('message', {}).get('content', '')
                            if content:
                                yield f"data: {json.dumps({'content': content})}\n\n"
                        except json.JSONDecodeError:
                            continue
        except httpx.TimeoutException:
            yield f"data: {json.dumps({'error': 'Ollama 响应超时'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': f'Ollama 连接错误: {str(e)}'})}\n\n"


async def stream_deepseek(model: str, messages: list):
    """
    DeepSeek Chat Completions API 流式调用。
    联网搜索由前端在发送消息前完成，搜索结果已拼入 messages。
    """
    if not DEEPSEEK_API_KEY:
        yield f"data: {json.dumps({'error': 'DeepSeek API Key 未设置，请设置环境变量 DEEPSEEK_API_KEY'})}\n\n"
        yield "data: [DONE]\n\n"
        return

    ds_model = model.replace("deepseek:", "")

    headers = {
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json'
    }
    body = {
        'model': ds_model,
        'messages': messages,
        'temperature': 0.7,
        'max_tokens': 4096,
        'stream': True
    }

    async with httpx.AsyncClient(timeout=120) as client:
        try:
            async with client.stream('POST', 'https://api.deepseek.com/v1/chat/completions',
                                      json=body, headers=headers) as resp:
                if resp.status_code == 401:
                    yield f"data: {json.dumps({'error': 'DeepSeek API Key 无效，请设置环境变量 DEEPSEEK_API_KEY'})}\n\n"
                    yield "data: [DONE]\n\n"
                    return
                elif resp.status_code == 429:
                    yield f"data: {json.dumps({'error': '请求过于频繁，请稍后重试'})}\n\n"
                    yield "data: [DONE]\n\n"
                    return
                elif resp.status_code != 200:
                    yield f"data: {json.dumps({'error': f'DeepSeek API 错误 (HTTP {resp.status_code})'})}\n\n"
                    yield "data: [DONE]\n\n"
                    return

                async for line in resp.aiter_lines():
                    if line.startswith('data: '):
                        try:
                            data = json.loads(line[6:])
                            delta = (data.get('choices') or [{}])[0].get('delta') or {}
                            content = delta.get('content', '')
                            if content:
                                yield f"data: {json.dumps({'content': content})}\n\n"
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue
        except httpx.TimeoutException:
            yield f"data: {json.dumps({'error': '无法连接 DeepSeek API，请检查网络'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': f'DeepSeek 连接错误: {str(e)}'})}\n\n"


# ======================================================================
# 区域 3: API 路由
# ======================================================================

class ErrorReport(BaseModel):
    message: str = ""
    source: str = ""
    lineno: int = 0
    colno: int = 0
    stack: str = ""


@app.post("/api/log-error")
async def log_error(report: ErrorReport):
    """前端 JS 错误上报。"""
    logging.warning(f"🔥 前端 JS 错误: {report.message} ({report.source}:{report.lineno}:{report.colno})")
    if report.stack:
        logging.warning(f"   堆栈: {report.stack[:500]}")
    return {"ok": True}


@app.get("/")
async def index():
    """pathlib 读取 index.html 并返回。"""
    html_path = Path(__file__).parent / "index.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="index.html 未找到，请确保与 epub_reader.py 同目录")
    return HTMLResponse(html_path.read_text(encoding="utf-8"))


@app.get("/api/ollama-models")
async def get_models():
    """返回本地 Ollama 模型列表 + 每个模型的 context_length。"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{OLLAMA_URL}/api/tags", timeout=5)
            data = resp.json()
            models = []
            for m in data.get("models", []):
                models.append({
                    "name": m["name"],
                    "context_length": m.get("details", {}).get("context_length", 32768),
                    "parameter_size": m.get("details", {}).get("parameter_size", "unknown")
                })
            return {"models": models}
    except Exception:
        return {"models": []}


@app.post("/api/count-tokens")
async def count_tokens(request: CountTokensRequest):
    """单文本 token 计数（按模型选择 tokenizer）。"""
    tokens = await estimate_tokens(request.text, request.model)
    return {"tokens": tokens}


@app.post("/api/count-tokens-batch")
async def count_tokens_batch(request: CountTokensBatchRequest):
    """批量 token 计数（多文本并发计算）。"""
    tasks = [estimate_tokens(text, request.model) for text in request.texts]
    results = await asyncio.gather(*tasks)
    return {"tokens": list(results)}


@app.post("/api/load-epub")
async def load_epub(request: Request, file: UploadFile = File(None)):
    """
    上传 EPUB → 章节列表 + 书名。
    支持两种模式：
    1. 上传文件: multipart/form-data with file
    2. 从缓存加载: JSON body with book_name + from_cache=true
    """
    # 判断请求类型：有 file 是上传，否则尝试解析 JSON body
    if file and file.filename:
        # ── 模式 1: 上传文件 ──
        if not file.filename.lower().endswith('.epub'):
            raise HTTPException(status_code=400, detail="文件格式不支持，请上传 .epub 文件")

        file_data = await file.read()
        if len(file_data) > MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=413, detail="文件过大，请上传小于 100MB 的 EPUB")

        try:
            result = await parse_epub(file_data, file.filename)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=422, detail=str(e))

        # 保存原始 EPUB 到本地，供后续重解析（无需用户重新上传）
        _save_raw_epub(file_data, result['name'])

        # 检查字符总数
        total_chars = sum(len(ch.get('text', '')) for ch in result.get('chapters', []))
        if total_chars < 500:
            logging.warning(f"文本内容极少（{total_chars} 字符），可能为图片型 EPUB")

        return result

    # ── 模式 2: 从缓存加载 ──
    try:
        body = await request.json()
        book_name = body.get('book_name', '')
        from_cache = body.get('from_cache', False)
    except Exception:
        book_name = ''
        from_cache = False

    if from_cache and book_name:
        cached = load_cached_epub(book_name)
        if cached:
            return cached
        # 缓存未命中：尝试从本地保存的原始 EPUB 重新解析
        result = await _reparse_from_saved_epub(book_name)
        if result:
            return result
        raise HTTPException(status_code=404, detail="缓存中未找到该书，请重新上传 EPUB")

    raise HTTPException(status_code=400, detail="请上传 EPUB 文件")


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    SSE 流式对话。
    根据 model 前缀分流: "ollama:" → stream_ollama(), "deepseek:" → stream_deepseek()
    """
    if not request.model:
        raise HTTPException(status_code=400, detail="请选择模型")

    # 构造消息
    # 截断章节文本以适应上下文窗口（留 4000 tokens 给对话）
    max_chapter_tokens = max(2000, (request.context_limit or DEFAULT_CONTEXT_LIMIT) - 4000)
    chapters_text = request.chapters_text or ""
    if chapters_text:
        # 粗略截断：按字符数估算（中文 ~1.2 char/token）
        max_chars = max_chapter_tokens * 2
        if len(chapters_text) > max_chars:
            chapters_text = chapters_text[:max_chars] + "\n\n[章节内容已截断，超出上下文窗口限制]"
            logging.info(f"章节文本从 {len(request.chapters_text)} 字符截断至 {max_chars} 字符")

    if request.system_prompt:
        system_content = request.system_prompt.replace("{book_name}", request.book_name)
    else:
        system_content = (
            f"你是博学的阅读助手。以下是《{request.book_name}》中用户选中的章节原文。"
            f"优先基于原文内容回答并引用原文。如果问题超出原文范围，可以结合你的知识回答，"
            f"但要明确区分原文信息和你自己的知识。不知道就说不知道，不要编造信息。"
        )
    if chapters_text:
        system_content += f"\n\n{chapters_text}"

    messages = [{"role": "system", "content": system_content}] + request.history
    if request.question:
        messages.append({"role": "user", "content": request.question})

    async def generate():
        full_reply = ""
        user_text = request.question or ""

        if request.model.startswith("deepseek"):
            stream = stream_deepseek(request.model, messages)
        else:
            num_ctx = request.context_limit or DEFAULT_CONTEXT_LIMIT
            stream = stream_ollama(request.model, messages, num_ctx)

        async for chunk in stream:
            full_reply += _extract_content_from_sse(chunk)
            yield chunk

        # 计算 token 用量
        try:
            tokens_used = await estimate_tokens(user_text + full_reply, request.model)
            yield f"data: {json.dumps({'tokens_used': tokens_used})}\n\n"
        except Exception:
            pass

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


def _extract_content_from_sse(chunk: str) -> str:
    """从 SSE chunk 中提取 content 文本（用于累积 token 计算）。"""
    if chunk.startswith('data: ') and chunk.strip() != 'data: [DONE]':
        try:
            data = json.loads(chunk[6:])
            return data.get('content', '')
        except json.JSONDecodeError:
            pass
    return ''


@app.post("/api/save-obsidian")
async def save_obsidian(request: SaveRequest):
    """保存选中的对话消息到 Obsidian vault（含路径穿越防护）。"""
    if not VAULT_PATH:
        raise HTTPException(status_code=500, detail="未设置 Obsidian vault 路径，请设置环境变量 OBSIDIAN_VAULT_PATH")

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filepath = build_save_path(VAULT_PATH, request.book_name, timestamp)

        lines = [
            f"# 《{request.book_name}》阅读对话",
            f"> 保存时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            ""
        ]
        for msg in request.messages:
            role = msg.get('role', '')
            content = msg.get('content', '')
            if role == "user":
                lines.append("**🧑 你**")
            else:
                lines.append("**🤖 AI**")
            lines.append(content)
            lines.append("")
            lines.append("---")
            lines.append("")

        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text('\n'.join(lines), encoding="utf-8")

        return {"success": True, "path": str(filepath)}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError:
        raise HTTPException(status_code=500, detail="无法写入文件，请检查 Obsidian vault 文件夹权限")
    except OSError as e:
        if "File exists" in str(e) or "file already exists" in str(e):
            alt_path = filepath.parent / f"{filepath.stem}_2{filepath.suffix}"
            alt_path.write_text('\n'.join(lines), encoding="utf-8")
            return {"success": True, "path": str(alt_path)}
        raise HTTPException(status_code=500, detail=f"文件写入失败: {e}")


# ======================================================================
# 区域 3b: 上传大小限制中间件
# ======================================================================

class MaxUploadSizeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.method == "POST":
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > MAX_UPLOAD_SIZE:
                return JSONResponse(
                    status_code=413,
                    content={"error": "文件过大，请上传小于 100MB 的 EPUB"}
                )
        return await call_next(request)


app.add_middleware(MaxUploadSizeMiddleware)


# ======================================================================
# 区域 4: 读取 API Key（Ollama 不可用时从 vault 读取）
# ======================================================================

def _read_api_key_from_vault() -> str:
    """从 Obsidian vault 的 API Key.md 读取 API Keys。"""
    if not VAULT_PATH:
        return ""
    try:
        key_file = Path(VAULT_PATH) / "API Key.md"
        if key_file.exists():
            content = key_file.read_text(encoding="utf-8")
            for line in content.split('\n'):
                if 'DEEPSEEK' in line.upper() and '=' in line:
                    return line.split('=', 1)[1].strip().strip('"').strip("'")
    except Exception:
        pass
    return ""


# ======================================================================
# 区域 5: 启动逻辑
# ======================================================================

if __name__ == "__main__":
    import webbrowser

    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    # 1. 尝试连接 Ollama，获取本地模型列表
    async def _startup():
        global _default_ollama_model, _ollama_context_length, DEEPSEEK_API_KEY, VAULT_PATH

        loop = asyncio.get_running_loop()

        # 尝试获取 Ollama 模型
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{OLLAMA_URL}/api/tags", timeout=5)
                data = resp.json()
                models = data.get("models", [])
                if models:
                    _default_ollama_model = models[0]["name"]
                    _ollama_context_length = models[0].get("details", {}).get("context_length", 32768)
        except Exception:
            pass

        # 2. 设置 Vault 路径（独立于 API Key）
        if not VAULT_PATH:
            VAULT_PATH = os.path.expanduser("~/Library/Mobile Documents/iCloud~md~obsidian/Documents/BWObsidianVault")

        # 3. 读取 API Key
        if not DEEPSEEK_API_KEY and VAULT_PATH:
            DEEPSEEK_API_KEY = _read_api_key_from_vault()

    # 异步运行启动检测
    try:
        asyncio.run(_startup())
    except RuntimeError:
        pass

    # 3. 打印启动信息
    print("📚 EPUB 整本书阅读器 v2.2")
    if _default_ollama_model:
        print(f"  本地模型: {_default_ollama_model} (默认上下文 {_ollama_context_length} tokens)")
    else:
        print("  ⚠️ Ollama 未运行，请先执行 ollama serve")
    if DEEPSEEK_API_KEY:
        print(f"  DeepSeek API: 已配置")
    else:
        print("  ⚠️ DeepSeek API Key 未配置")
    print(f"  默认上下文窗口: {min(48000, _ollama_context_length) if _ollama_context_length else 48000} tokens")
    print(f"  本地: http://localhost:{PORT}")

    webbrowser.open(f"http://localhost:{PORT}")

    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")
