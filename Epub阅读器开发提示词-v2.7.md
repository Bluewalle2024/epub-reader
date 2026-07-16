# EPUB 整本书阅读器 — 开发提示词 v2.7

> 更新：2026-07-16
>
> v2.7.2 变更（消息气泡右上角图标优化 — Gemini 风格）：
> 1. **Toolbar 移入气泡内部**：复制/保存图标从气泡上方移至右上角 (`top:8px; right:10px`)，不再遮挡
> 2. **图标缩小**：按钮 30×30→24×24px，SVG 16→13px，更精致
> 3. **右侧强制预留空间**：`.msg-bubble` padding-right 16→72px，文字永不进入图标区域
> 4. **毛玻璃背景**：toolbar 背景 `rgba(255,255,255,0.82)` + `blur(10px)`，轻量阴影
> 5. **修复流式更新图标丢失**：`updateMessageContent` innerHTML 后恢复 toolbar，AI 回复栏图标不再消失
>
> v2.7.1 变更（代码校验修复）：
> 1. **跨浏览器 dots 动画**：CSS `@keyframes dots` + `content` 仅 Chrome 支持 → 改为 JS `setInterval` 驱动
> 2. **死变量清理**：移除未使用的 `--warning-yellow` / `--danger-red`
> 3. **重复调用修复**：`checkContextAndHandle()` 内移除冗余 `updateWarningBar()` 调用
>
> Git: `d526dc7` → `62210d7` → `e2e9f10` → `cf994bd` → (v2.7.2)
>
> ---
>
> v2.7 变更（CSS 全面重构 — Apple 风格 + 橙色主题）：
> 1. **Apple 设计语言**：背景体系改为 #f5f5f7 / 纯白，毛玻璃顶栏，胶囊输入框，视网膜多层阴影
> 2. **橙色主题保留**：#e8500c 主色不变，新增 --accent-bg / --accent-ring 等辅助变量
> 3. **模型选择器改为本地/云端标签**：胶囊按钮切换，隐藏下拉框，本地选中红框、云端选中橙框
> 4. **设置按钮改为 macOS 齿轮图标**：SVG 图标替代文字
> 5. **字体按钮改为 A-/A+**：替代「缩小」「放大」文字
> 6. **字号统一**：主内容 16px，UI 标签 12px，列表项 13px，章节元数据 11px
> 7. **用户消息气泡风格同步 AI**：白/灰底黑字 + 细边框，不再橙底白字
> 8. **打开 EPUB / 保存 Obsidian 按钮**：黑色加粗胶囊风格，与 A-/A+ 一致
> 9. **历史记录 / 当前书籍 / summary 字色**：全部改为纯黑
> 10. **搜索栏 X 按钮常驻**：始终可见，点击清空搜索
> 11. **保存模式点击空白退出**：不勾选时点击任意空白处自动取消
> 12. **拖拽分割线防蓝影**：mousedown e.preventDefault() + drag-resizing class 禁止选中
> 13. **切换模型清理流式状态**：隐藏思考条 + 移除 .streaming class
> 14. **书名后模型名称移除**：状态栏仅显示《书名》
>
> Git: `d526dc7` → `62210d7` → `f2fa1a4`
>
> ---
>
> v2.6 变更（搜索增强 + DeepSeek + 稳定性）：
> 1. **全内容搜索**：搜索栏匹配章节标题 + 正文内容，阅读区搜索词黄色高亮
> 2. **搜索栏清除按钮**：右侧 ✕ 按钮，点击清空搜索词
> 3. **全选复选框**：搜索栏下方，与章节勾选框对齐，支持全选/取消/半选状态
> 4. **DeepSeek V4 Flash 上下文上限 128K**：切换模型时自动调整滑条上限，不受 48K 约束
> 5. **删除 deepseek-chat 模型**：仅保留 deepseek-v4-flash
> 6. **按模型分别记忆上下文设置**：Ollama / DeepSeek 各自独立保存，切换不互相影响
> 7. **上下文超出上限不再阻塞发送**：按钮仅在没有章节时灰色，超出上限时警告但仍可发送，后端自动截断
> 8. **防卡死**：API 调用加 10-15s 超时；切换模型/重置书籍时强制中止流式输出
> 9. **章节勾选即时响应**：用 tokens_approx 立即更新进度条和按钮，不等 API 返回
>
> Git: `6b8caa9` → `0435fc6` → `687e61b` → `72e41f0` → `d26b154` → `d526dc7`
>
> ---
>
> v2.4.1 变更（Bug 修复）：
> 1. **VAULT_PATH 独立于 DEEPSEEK_API_KEY**：启动逻辑中 VAULT_PATH 的设置不再包裹在 `if not DEEPSEEK_API_KEY` 条件内，确保无论是否配置 API Key 都能正常保存到 Obsidian
> 2. **默认 vault 路径修正**：从 `~/Documents/Obsidian` 改为 iCloud 实际路径 `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/BWObsidianVault`
> 3. **Git 版本控制**：项目纳入 git 管理，commit 6b8caa9 作为 v2.4 基线备份
>
> ---
>
> v2.4 变更（UI 精简）：
> 1. **移除空状态图标和文字**：阅读区空状态不再显示 📖 + "请在左侧选择要阅读的章节"，对话区空状态不再显示 💬 + "加载 EPUB 并选择章节后开始对话"，改为纯空白区域（涉及 HTML 模板 + clearReader/clearChatMessages/updateBookInfo 共 5 处 JS 动态赋值）
>
> ---
>
> v2.3 变更（交互优化 + Bug 修复）：
> 1. **Enter 发送消息**：直接 Enter 发送（原 Ctrl/Cmd+Enter），Shift+Enter 换行；IME 组合输入时（`e.isComposing`）不触发发送
> 2. **清空按钮行为变更**：清空历史时间时同时重置当前书籍和所有章节（`resetBookState()`）
> 3. **系统提示词优化**：鼓励模型结合通用知识回答，但需区分原文信息 vs 自身知识，不知道时诚实说明
> 4. **前端错误上报**：新增 `POST /api/log-error` 端点 + `window.onerror`，浏览器 JS 错误自动上报到服务端日志
> 5. **章节自动选择优化**：跳过 < 200 字的扉页/版权页，优先选中正文章节
> 6. **进度条精度**：百分比 < 1% 时显示一位小数（如 0.5%），避免始终显示 0%
> 7. **发送按钮流式状态**：流式输出中不禁用按钮（改为 spinner + 点击停止），确保用户能中断生成
> 8. **Token 计算防抖**：`recalcChapterTokensDebounced(400ms)` 防止快速勾选章节时发起大量 API 请求
> 9. **流式超时保护**：前端 5 分钟安全超时强制重置 streaming 状态
> 10. **后端超时增加**：Ollama httpx timeout 从 120s 增至 300s
> 11. **章节文本截断**：后端 `/api/chat` 接收 `context_limit`，章节原文超过 `context_limit - 4000` 时自动截断
> 12. **Ollama /api/tokens 404 缓存**：API 不可用时静默回退启发式估算，不再重复请求
> 13. **loadFromHistory 修复**：函数声明补上 `async` 关键字（原缺失导致整个 JS 脚本解析失败）
> 14. **DeprecationWarning 修复**：`asyncio.run()` 替代 `asyncio.get_event_loop().run_until_complete()`
> 15. **缓存 key 修复**：使用 `hashlib.md5()` 替代 `hash()`（后者受 PYTHONHASHSEED 影响，进程重启后值不同）
>
> ---
>
> v2.2 变更（代码健壮性 + 简化）：
> 1. **parse_epub 不阻塞事件循环**：CPU 密集解析用 `run_in_executor` 放入线程池
> 2. **解析阶段不再调 Ollama API**：token 改用快速启发式估算（标注 approximate），加载后前端异步调用 `/api/count-tokens-batch` 批量重算
> 3. **SSE chunk 缓冲区**：前端 `reader.read()` 跨 chunk 断行处理，不再丢消息
> 4. **上传大小限制**：中间件检查 Content-Length，超过 100MB 返回 413
> 5. **三层策略简化为两层**：去掉 AI 压缩（策略 2），仅保留自动滑动窗口 + 手动重置
> 6. **联网搜索简化为 DuckDuckGo 单一方案**：去掉 SearXNG/Bing 备用方案；去掉独立搜索按钮，切换 DeepSeek 后自动启用
> 7. **章节对象精简**：不再预存 tokens/chars/is_bilingual，token 统一通过 API 实时计算
> 8. **filter_chinese_only 改用 regex 库 `\p{Han}`**：自动覆盖 CJK Extension A~H
> 9. **sanitize_filename 加固**：新增控制字符过滤（`\x00-\x1f`）
> 10. **新增 EPUB3 nav.xhtml 支持**：TOC 提取同时检查 EPUB2/3 两种格式
> 11. **全局字号统一**：阅读区 + 对话气泡 + 输入框通过 CSS 变量 `--content-font-size` 统一缩放
> 12. **解析结果缓存**：tempfile 缓存已解析的 EPUB，服务重启后可恢复
> 13. **发送按钮嵌入 textarea**：右下角内嵌橙色圆角方块，与 ChatGPT/Claude 一致
> 14. **设置面板模态窗**：点击「设置」弹出完整设置面板（滑块 + 开关 + 路径 + 恢复默认）
> 15. **保存模式多选**：进入保存模式后每条消息（含用户提问）左侧出现勾选框

---

## 请帮我开发一个 EPUB 整本书阅读器

Python FastAPI + 独立 HTML 前端（`index.html`），运行在 `localhost:8765`，仅本地使用。

### 零、核心约束

- **Python 脚本 + 独立 HTML 前端**：`epub_reader.py` + `index.html`，同目录放置。Python 启动时用 `pathlib` 动态读取 HTML 返回，前端在 VS Code 中享受完整语法高亮和格式化
- **仅本地使用**：绑定 `127.0.0.1`，不暴露到网络
- **本地 AI 为主**：Ollama + Qwen 2.5 7B 做日常对话，DeepSeek v4 flash 仅用于联网搜索
- **Git 版本控制**：每完成一个功能模块 commit 一次，功能完成后跑验证清单
- **代码分层**：文件内严格分区域（纯函数 → API 路由 → HTML 读取 → 启动逻辑），修改一个区域不碰其他区域

### 一、依赖

```
fastapi uvicorn ebooklib beautifulsoup4 httpx python-multipart tiktoken regex
```

新增 `regex`（支持 Unicode `\p{Han}` 属性，替代标准库 `re` 做中文过滤）。均为纯 pip 安装，无系统依赖。

---

### 二、整体架构

- FastAPI + uvicorn，端口 8765，host `127.0.0.1`
- 启动自动打开浏览器：`webbrowser.open(f"http://localhost:{PORT}")`
- 三栏布局：左侧章节列表（260px + 可拖拽调整） + 中间原文阅读区（可拖拽调整） + 右侧对话区（剩余宽度）
- 配色 Apple Books 暖色风格：CSS 变量
  ```
  --bg: #faf8f2
  --bg-sidebar: #f3efe7
  --bg-card: #ffffff
  --accent: #e8500c
  --accent-hover: #c4450a
  --text-primary: #1d1d1f
  --text-secondary: #6e6e73
  --text-tertiary: #aeaeb2
  --border: #e5e0d8
  --border-focus: #e8500c
  --msg-user-bg: #e8500c
  --msg-user-text: #ffffff
  --msg-ai-bg: #ffffff
  --msg-ai-border: #e5e0d8
  ```
- 字体：`-apple-system, BlinkMacSystemFont, "SF Pro Text", "PingFang SC", "Microsoft YaHei", sans-serif`
- 滚动条：6px 宽，圆角，暖灰色

---

### 三、代码区域划分（强制，修改时不得跨区域）

```python
# ===== epub_reader.py =====

# ── 区域 1: 配置常量 ──
import os
PORT = 8765
VAULT_PATH = os.environ.get("OBSIDIAN_VAULT_PATH") or ""        # Obsidian vault 路径，优先环境变量，否则启动时自动设为 iCloud 路径
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY") or ""    # 优先环境变量，否则从 vault API Key.md 读取
OLLAMA_URL = "http://localhost:11434"
DEFAULT_CONTEXT_LIMIT = 48000
MAX_UPLOAD_SIZE = 100 * 1024 * 1024                             # 100MB

# ── 区域 1b: 启动时动态获取的配置 ──
# 启动时调 GET /api/tags 获取本地模型名和 context_length
# - _default_ollama_model: 从 API 返回的第一个模型名（如 huihui_ai/qwen2.5-abliterate:7b）
# - _ollama_context_length: 从模型 details.context_length 读取（Ollama modelfile 默认值，仅信息展示）
# - 如果 Ollama 不可用: _default_ollama_model = ""，context_limit 默认 48000

_default_ollama_model = ""
_ollama_context_length = 32768

# ── 区域 2: 纯函数（无副作用，不依赖全局状态）──
def heuristic_token_count(text: str, model: str = "") -> int: ...   # 纯本地快速估算（解析阶段用）
async def estimate_tokens(text: str, model: str = "") -> int: ...   # 按模型选择 tokenizer（API 调用，精度高）
def _parse_epub_sync(file_data: bytes) -> dict: ...                  # 同步 EPUB 解析（在线程池中运行）
async def parse_epub(file_data: bytes) -> dict: ...                  # 异步包装：run_in_executor
def extract_chapter_text(html_content: str) -> str: ...
def filter_chinese_only(text: str, threshold: float = 0.5) -> str: ...

# ── 区域 3: API 路由（每个端点独立，互不影响）──
@app.get("/")                       # pathlib 读取 index.html 并返回
@app.post("/api/count-tokens")      # 前端防抖请求 token 计数（单文本，按模型选择 tokenizer）
@app.post("/api/count-tokens-batch")# 批量 token 计数（多文本并发，章节加载后一次性获取精确值）
@app.post("/api/load-epub")         # 上传 EPUB → 章节列表（含 text + text_cn + tokens_approx）
@app.post("/api/chat")              # SSE 流式对话
@app.post("/api/save-obsidian")     # 保存到 Obsidian（含路径穿越防护）
@app.get("/api/ollama-models")      # 本地模型列表
@app.post("/api/log-error")        # 前端 JS 错误上报（window.onerror 自动发送）

# ── 区域 4: HTML 读取 ──
from pathlib import Path
INDEX_HTML = Path(__file__).parent / "index.html"
@app.get("/") → return HTMLResponse(INDEX_HTML.read_text(encoding="utf-8"))

# ── 区域 5: 启动逻辑 ──
if __name__ == "__main__":
    # 1. 尝试连接 Ollama → 获取 _default_ollama_model + _ollama_context_length
    # 2. 设置 VAULT_PATH（独立于 API Key，始终需要）
    #    - 如果环境变量 OBSIDIAN_VAULT_PATH 已设置，使用环境变量
    #    - 否则自动设为 iCloud Obsidian 路径: ~/Library/Mobile Documents/iCloud~md~obsidian/Documents/BWObsidianVault
    # 3. 如果 DEEPSEEK_API_KEY 为空，尝试从 vault API Key.md 读取
    # 3. 添加上传大小限制中间件
    # 4. webbrowser.open + uvicorn.run
```

```
===== index.html（独立文件，VS Code 完整语法支持）=====
<!DOCTYPE html>
<html lang="zh-CN">
  <!-- 所有 HTML/CSS/JS 在此文件中 -->
</html>
```

---

### 四、页面布局

```
┌───────────────────────────────────────────────────┐
│  EPUB 阅读器     [huihui_ai/qwen2.5-abliterate:7b ▼] [设置]│
├──────────┬──────────────────┬─────────────────────┤
│ 打开EPUB │  原文阅读区        │  书名 · 当前模型      │
│ ──────── │  第X章 标题 [缩小|放大]│ 上下文 ████░░ 46%  重置│
│ 历史记录  │                  │  ⚠️ 章节超40K        │
│ 三体     │  正文内容...      │  ┌──────────────┐   │
│ 活着     │  正文内容...      │  │ 消息1    [⎘][⊞]│   │
│ ──────── │  正文内容...      │  │ 消息2    [⎘][⊞]│   │
│ 当前:三体 │  正文内容...      │  │ 消息3    [⎘][⊞]│   │
│ 搜索章节  │                  │  └──────────────┘   │
│ ☑ 第1章  │                  │                     │
│ ☑ 第2章  │                  │  ┌──────────────┐   │
│ ☐ 第3章  │                  │  │  输入区域     ➤│   │
│  ...     │                  │  └──────────────┘   │
│ ──────── │                  │                     │
│ 已选3章  │                  │                     │
│ 26K !   │                  │                     │
│ 保存到..│                  │                     │
└──────────┴──────────────────┴─────────────────────┘
```

#### 4.1 左侧：侧边栏（aside, 260px 默认宽，可拖拽调整）

侧边栏从上到下分为 5 个区域：

**区域 A：上传按钮**
- 「打开 EPUB」文字按钮（始终可见，Apple 风格：橙色文字，无边框无背景）
- 隐藏的 `<input type="file" accept=".epub">`（通过按钮 click 事件间接触发）

**区域 B：历史记录**
- 标题「历史记录」+ 清空链接（点击后确认弹窗，确认后同时清除历史 + 当前书籍 + 对话）
- 列表：每个条目显示 📖 + 书名 + 章节数 + 上次打开时间
- 数据来源：localStorage（仅存储元信息：书名、章节标题列表、token 数，不含全文）
- 点击历史条目 → 在后端内存中查找该书（如已缓存）或提示「需要重新上传 EPUB 文件」
- 每个条目右侧 ✕ 按钮可删除该条历史
- 最多保留 10 条，超出自动清理最旧的
- localStorage key: `epub-reader-history`

**区域 C：当前书籍指示**
- 加载书籍后显示：`当前: 《书名》`
- 样式：橙色文字，分隔线

**区域 D：章节搜索 + 列表**
- 搜索框：输入关键词实时过滤章节标题（debounce 150ms）
- 章节列表：每行 `<label><input type="checkbox"> 章节标题 <span class="meta">token数</span></label>`
  - token 数为近似值（解析时启发式估算），加载完成后自动切换为精确值
  - 加载后自动选中前 2 个有实质内容的章节（跳过 < 200 字的扉页/版权页）
  - 如果所有章节都太短，至少选中前 2 个
- 搜索结果为空时显示「无匹配章节」
- 搜索不影响已选中的勾选状态

**区域 E：底部汇总栏（sticky 贴底）**
- 已选章节数 / 总章节数 · 已选章节 token 数
- 两档警告：
  - **🟡 40K 警告**：选中章节 token > 40000 时，token 数后显示 ⚠️ 标记，汇总栏黄色，同时在对话区顶部显示可关闭的警告条
  - **🔴 超出限制**：选中章节 token > contextLimit - 8000（预留对话空间）时，汇总栏变红，发送按钮禁用
- 底部 **「保存」** 文字按钮：点击进入保存模式（消息左侧出现 ☐ 勾选框），再次点击或按 Esc 退出

注：上下文总用量（章节 + 对话）的进度条在右侧对话区顶部展示，不在侧栏。

#### 4.2 中间：原文阅读区（section, ~400px 默认宽，可拖拽调整）

- 空状态：无文字和图标（v2.4 移除）
- 选中章节后：显示选中章节的完整原文
  - 章节标题用 `<h2>` + 橙色下划线
  - 正文段落用 `<p>` 标签，1.8 行高，适合长时间阅读
  - 章节之间用分隔线 `───` 隔开
- 阅读区右上角显示字号调节按钮「缩小」「放大」（Apple 分段控件风格），统一缩放阅读区、对话气泡、输入框的字号。范围 14px–22px，默认 16px，通过 CSS 变量 `--content-font-size` 统一控制，保存到 localStorage
- 支持 `Ctrl/Cmd+F` 在原文区搜索
- 滚动位置：仅在显示的章节内容发生变化时重置到顶部；仅勾选/取消勾选（被显示的章节不变）时保持滚动位置

#### 4.3 右侧：对话区（section, 剩余宽度）

**顶部状态栏**
- 书名 + 当前模型（左对齐）
- 上下文进度条（居中）：
  - track + fill + 百分比文字
  - 颜色：🟢 <60% / 🟡 60-80% / 🔴 80-90% / ⚫ 90-100%
- 「重置」文字按钮（右对齐，进度条右侧，仅在上下文 > 80% 时显示）：
  - 点击弹确认框「确定要重置对话吗？章节选择和原文不受影响。」
  - 确认后清空 chat-area，conversationTokens = 0，插入系统消息
- 章节超过 40K 时的警告条（进度条下方，可关闭）

**消息区（chat-area）**
- flex column, overflow-y:auto
- 空状态：无文字和图标（v2.4 移除）
- 用户气泡：右对齐，橙色底白字，border-bottom-right-radius: 4px
- AI 气泡：左对齐，白底灰边框，border-bottom-left-radius: 4px，box-shadow
  - **AI 回复内容支持 Markdown 渲染**：使用轻量库（如 marked.js ~20KB 或手写正则）渲染加粗、斜体、列表、代码块、引用、标题
- 系统消息：居中，灰色小字，12px
- 每条消息 hover 时，气泡右上角浮现简约图标（Apple SF Symbols 风格，16px，灰色，hover 变 accent 色）：
  - 用户消息：⎘ 复制图标
  - AI 回复：⎘ 复制图标 + ⊞ 保存图标
  - 点击后图标短暂变为「✓ 已复制」「✓ 已保存」反馈
- 保存模式时：每条消息左侧出现 ☐ 勾选框

**输入区（chat-input-area）**
- 多行 textarea，默认 4 行高度，可手动拖拽调整
- **发送按钮位于 textarea 右下角内部**（橙色圆角方块 + 向上箭头 SVG 图标，绝对定位），与 ChatGPT/Claude 等 AI 界面一致
- 支持 `Enter` 发送（有内容+有章节时），`Shift+Enter` 换行
- IME 组合输入时（`e.isComposing`）不触发发送，确保中文输入法正常使用
- 发送中按钮变为 spinner 动画，可再次点击停止（不禁用按钮）
- 发送新消息时 AbortController 取消旧流
- **输入区只保留 textarea + 内嵌发送按钮，无其他控件**

**发送按钮禁用条件**
- 没有选中章节
- 上下文已满且用户未确认重置
- 正在等待 AI 回复（按钮变为「停止」）

---

### 五、EPUB 解析（后端）

使用 `ebooklib` + `BeautifulSoup`，不用正则。包含主解析器 + 4 级修复降级策略 + 双语过滤 + 解析结果缓存。

#### 5.1 异步包装（防止阻塞事件循环）

```python
import asyncio
import pickle
import tempfile
from pathlib import Path

async def parse_epub(file_data: bytes) -> dict:
    """
    CPU 密集的 EPUB 解析放入线程池，不阻塞 asyncio 事件循环。
    解析完成后缓存到临时文件，服务重启后可从缓存恢复。
    """
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None, _parse_epub_sync, file_data
    )

    # 缓存到临时文件（服务重启后可恢复）
    # 注意：必须用 hashlib 而非 hash()——后者受 PYTHONHASHSEED 影响，进程重启后值不同
    import hashlib
    cache_key = hashlib.md5(result['name'].encode()).hexdigest()
    cache_path = Path(tempfile.gettempdir()) / f"epub_reader_{cache_key}.cache"
    try:
        cache_path.write_bytes(pickle.dumps(result))
    except Exception:
        pass  # 缓存失败不影响主流程

    return result


def load_cached_epub(book_name: str) -> dict | None:
    """尝试从缓存恢复已解析的 EPUB"""
    import hashlib
    cache_key = hashlib.md5(book_name.encode()).hexdigest()
    cache_path = Path(tempfile.gettempdir()) / f"epub_reader_{cache_key}.cache"
    if cache_path.exists():
        try:
            return pickle.loads(cache_path.read_bytes())
        except Exception:
            cache_path.unlink(missing_ok=True)
    return None
```

#### 5.2 主解析器（同步，运行在线程池中）

```python
from ebooklib import epub
from bs4 import BeautifulSoup

def _parse_epub_sync(file_data: bytes) -> dict:
    """
    四级降级策略，每一级失败自动进入下一级:
    Level 0: ebooklib 标准解析
    Level 1: OPF 修复 → 重建 content.opf 后再用 ebooklib
    Level 2: ZIP 修复 → 修复损坏的 ZIP 结构后提取
    Level 3: 原始 ZIP 遍历 → 放弃 EPUB 结构，直接从 zip 提取所有文本

    Token 估算使用纯本地启发式方法（不调 Ollama API，避免阻塞），
    前端加载完成后通过 /api/count-tokens-batch 批量获取精确值。

    返回: {
        "name": "书名",
        "chapters": [
            {
                "title": "第X章 标题",
                "text": "正文...",          # 原始全文（始终保留，不可变）
                "text_cn": "正文...",       # 仅中文版本（解析时预计算，供前端即时切换）
                "tokens_approx": 1234,      # 启发式估算值（heuristic_token_count 计算，侧栏初始展示）
            },
            ...
        ],
        "repair_level": 0  # 0=正常, 1=OPF修复, 2=ZIP修复, 3=原始提取
    }
    """
```

> **v2.2 精简**：章节对象不再包含 `chars`、`chars_cn`、`tokens`、`tokens_cn`、`is_bilingual` 字段。Token 数由前端在加载完成后通过 `/api/count-tokens-batch` 批量获取，切换「仅中文」时前端重新请求对应文本版本的 token 数。解析阶段不需要任何网络 I/O，解析速度大幅提升。

#### 5.3 四级修复降级策略

```
_parse_epub_sync(file_data):
    ┌─ Level 0: ebooklib 标准解析
    │   epub.read_epub(io.BytesIO(file_data))
    │   按 spine 顺序提取章节
    │   EPUB3: 优先从 nav.xhtml 提取 TOC；EPUB2: 从 toc.ncx 提取
    │   检查: 章节数 > 0 且总字符数 > 500?
    │   ├─ ✅ 成功 → 返回结果，repair_level = 0
    │   └─ ❌ 失败 → 进入 Level 1
    │
    ├─ Level 1: OPF 修复重建
    │   尝试用 ZipFile 打开，找 content.opf
    │   如果 OPF 缺失或格式错误:
    │     - 扫描所有 .xhtml/.html，自动生成 spine
    │     - 从 toc.ncx 或 nav.xhtml 提取目录（如有）
    │     - 重建最小可用的 content.opf
    │     - 用修复后的 OPF 重新走 ebooklib 流程
    │   检查: 章节数 > 0?
    │   ├─ ✅ 成功 → 返回结果，repair_level = 1
    │   └─ ❌ 失败 → 进入 Level 2
    │
    ├─ Level 2: ZIP 结构修复
    │   用 ZipFile 打开失败（ZIP 损坏）时:
    │     - 用 zipfile.ZipFile(io.BytesIO(data), 'r') 重新打开
    │     - 遍历 infolist()，逐个 try/except 提取每个成员（跳过损坏文件）
    │     - 对每个成功提取的 .xhtml/.html 用 BeautifulSoup 解析
    │   检查: 提取到文本的章节数 > 0?
    │   ├─ ✅ 成功 → 返回结果，repair_level = 2
    │   └─ ❌ 失败 → 进入 Level 3
    │
    └─ Level 3: 原始字节级提取
        放弃 EPUB 结构，暴力提取:
        1. 尝试所有编码打开文件中的文本片段
           (utf-8 → gbk → latin-1 → cp1252)
        2. 正则匹配 HTML 标签之间的可见文本
        3. 过滤长度 < 20 字符的碎片
        4. 按出现顺序分组为「片段1」「片段2」...
        5. 书名从文件名提取
        检查: 提取到任何文本?
        ├─ ✅ 成功 → 返回结果，repair_level = 3
        └─ ❌ 彻底失败 → 返回 422 错误
```

**各 Level 的返回标识**：

| repair_level | 含义 | 前端行为 |
|---|---|---|
| 0 | 正常解析 | 无提示 |
| 1 | OPF 修复成功 | toast「EPUB 目录结构已自动修复，章节顺序可能与原书略有差异」 |
| 2 | ZIP 修复成功 | toast「EPUB 文件存在损坏，已尽力修复并提取可读内容」 |
| 3 | 原始提取 | toast「⚠️ EPUB 严重损坏，已使用原始模式提取文本片段，无章节结构」 |
| -1 | 彻底失败 | 错误弹窗（见 19.3 节错误处理） |

**重要**：repair_level > 0 时，返回的 `name` 字段后追加修复标记，如 `书名 [OPF已修复]`。

#### 5.4 EPUB3 nav.xhtml 目录提取

```python
def extract_toc(epub_book: epub.EpubBook, spine_items: list) -> list[dict]:
    """
    TOC 提取优先级:
    1. nav.xhtml (EPUB3) — 解析 <nav epub:type="toc"> 中的 <ol>/<li>/<a>
    2. toc.ncx (EPUB2) — 解析 <navMap>/<navPoint>/<navLabel>/<text>
    3. spine 中的 <h1>-<h6> 标签 — 自动生成章节标题
    4. 数字序号兜底 — "第N章"
    """
    # 方法 1: EPUB3 nav.xhtml
    for item in epub_book.get_items_of_type(9):  # ITEM_DOCUMENT
        if 'nav' in item.get_name().lower():
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            toc_nav = soup.find('nav', attrs={'epub:type': 'toc'})
            if toc_nav:
                return _parse_nav_list(toc_nav.find('ol'))

    # 方法 2: EPUB2 toc.ncx（通过 ebooklib 内置方法）
    # ebooklib 的 epub_book.toc 已解析 ncx，直接使用
    if epub_book.toc:
        return _parse_ebooklib_toc(epub_book.toc)

    # 方法 3: 从 spine 文档的 h1-h6 提取
    return _extract_from_headings(spine_items)
```

#### 5.5 双语书籍：仅提取中文（支持即时切换，无需重新上传）

**设计原则**：过滤逻辑在 EPUB 解析时预计算 `text_cn`，切换开关由前端即时执行，**无需重新上传 EPUB**。

##### 5.5.1 章节对象结构（v2.2 精简 + 初始估算）

```python
chapter = {
    "title": "第1章 标题",
    "text": "...",              # 原始全文（始终保留，不可变）
    "text_cn": "...",           # 仅中文版本（解析时预计算，供前端即时切换）
    "tokens_approx": 1234,      # 启发式估算值（解析时由 heuristic_token_count 计算，侧栏初始展示用）
}
```

`tokens_approx` 用于侧栏章节列表的初始展示，前端加载完成后通过 `/api/count-tokens-batch` 批量获取精确值并替换。切换「仅中文」后，前端需用 `text_cn` 重新请求精确 token，`tokens_approx` 不再更新（仅作初始占位）。

##### 5.5.2 `filter_chinese_only` 函数（使用 regex 库 `\p{Han}`）

```python
import regex  # 不是标准库 re，支持 Unicode \p{Han}

def filter_chinese_only(text: str, threshold: float = 0.5) -> str:
    """
    过滤非中文内容，仅保留中文为主的段落。

    策略（按段落处理）:
    1. 将文本按换行符拆分为段落
    2. 每个段落用 regex.findall(r'\p{Han}', line) 计算中文字符数
       - \p{Han} 自动覆盖 CJK 基本区 + Extension A~H + 兼容汉字
       - 无需手动维护 [一-鿿㐀-䶿...] 硬编码范围
    3. 占比 >= threshold 的段落保留，否则丢弃
    4. 保留的段落重新拼接
    """
    lines = text.split('\n')
    result = []

    for line in lines:
        line = line.strip()
        if not line:
            result.append('')  # 保留空行作为段落分隔
            continue

        cn_chars = len(regex.findall(r'\p{Han}', line))
        total_chars = len(regex.sub(r'\s', '', line))

        if total_chars == 0:
            result.append('')
        elif cn_chars / total_chars >= threshold:
            result.append(line)

    return '\n'.join(result)
```

##### 5.5.3 在 `_parse_epub_sync` 中的使用位置

```python
def _parse_epub_sync(file_data: bytes) -> dict:
    # ... 每个章节处理完成后:
    raw_text = extract_chapter_text(chapter_html)
    cn_text = filter_chinese_only(raw_text)

    chapter["text"] = raw_text
    chapter["text_cn"] = cn_text if cn_text.strip() else raw_text  # 纯英文书保留原文
    chapter["tokens_approx"] = heuristic_token_count(raw_text, "")  # 初始估算，前端异步更新为精确值
```

##### 5.5.4 前端：开关即时切换，无需重新上传

```javascript
// 全局状态
let chineseOnly = true;  // 默认开启，从 localStorage 恢复

// 切换开关时：重新渲染原文区 + 异步重算 token
async function toggleChineseOnly() {
    chineseOnly = !chineseOnly;
    localStorage.setItem('chineseOnly', chineseOnly);
    renderReaderArea();        // 用 text_cn 或 text 重新渲染原文区
    await recalcChapterTokens(); // POST /api/count-tokens-batch 批量重算
    updateContextBar();
}

// 获取当前应该显示的文本
function getDisplayText(chapter) {
    return chineseOnly ? chapter.text_cn : chapter.text;
}

// 异步重算所有已选章节的 token 数（使用批量接口，一次请求完成）
async function recalcChapterTokens() {
    const texts = selectedChapters.map(ch => getDisplayText(ch));
    if (texts.length === 0) { chapterTokens = 0; return; }
    const resp = await fetch('/api/count-tokens-batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ texts, model: currentModel })
    });
    const { tokens } = await resp.json();
    chapterTokens = tokens.reduce((a, b) => a + b, 0);
}
```

##### 5.5.5 开关 UI

在设置面板中：
```
双语处理
☑ 仅显示中文内容
```

> **v2.2 变更**：前端不再假设章节对象自带 token 数。切换开关时，前端对已选章节的当前显示文本（text 或 text_cn）调用 `/api/count-tokens-batch` 批量重算 token。章节列表中的 token 数在加载完成后异步更新为精确值。

#### 5.6 书名提取

```python
def extract_book_name(epub_book, fallback_filename: str = "") -> str:
    """
    优先级:
    1. EPUB metadata dc:title（通过 ebooklib 获取）
    2. content.opf 中的 <dc:title>
    3. toc.ncx 中的 <docTitle> / nav.xhtml 中的 <title>
    4. 文件名（去掉扩展名）
    """
```

---

### 六、Token 估算（按模型选择 tokenizer，前端通过 API 获取）

所有 token 计算统一由 Python 后端完成，**根据当前使用的模型选择对应的 tokenizer**。前端通过带防抖的异步请求获取结果。

#### 6.1 两种 token 计算方式

| 方式 | 函数 | 精度 | 使用场景 |
|------|------|------|----------|
| 启发式估算 | `heuristic_token_count()` | 偏差 ~15% | EPUB 解析阶段（不阻塞）+ 侧栏章节列表初始展示 |
| 精确计算 | `estimate_tokens()` | 偏差 <5% | `/api/count-tokens` API 响应（前端加载后异步更新） |

#### 6.2 启发式估算（纯本地，无网络 I/O）

```python
import regex

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
```

#### 6.3 精确计算（按模型选择 tokenizer）

```python
import tiktoken
import httpx

# DeepSeek 用 cl100k_base（偏差 <5%）
_ENC_DS = tiktoken.get_encoding("cl100k_base")

# 全局标记：Ollama /api/tokens 是否可用（避免重复 404 请求）
_ollama_tokens_api_ok = True

async def estimate_tokens_ollama(text: str, model: str) -> int:
    """
    通过 Ollama 原生 API 获取准确 token 数。
    API: POST /api/tokens  (Ollama >= 0.4.0 支持)
    超时 5s，失败回退到 heuristic_token_count。
    如果 API 返回 404（版本不支持），全局缓存该状态，后续不再请求。
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
                return len(resp.json().get("tokens", []))
            elif resp.status_code == 404:
                _ollama_tokens_api_ok = False
                logging.info("Ollama /api/tokens 不可用（404），后续将使用启发式估算")
    except Exception:
        pass

    return heuristic_token_count(text, model)


def estimate_tokens_deepseek(text: str) -> int:
    """DeepSeek 用 cl100k_base（偏差 <5%）"""
    return len(_ENC_DS.encode(text))


async def estimate_tokens(text: str, model: str = "") -> int:
    """
    统一入口：根据 model 前缀选择 tokenizer。
    - "deepseek:xxx" → tiktoken cl100k_base
    - "ollama:xxx" / 无前缀 → Ollama 原生 API（回退启发式）
    """
    if model.startswith("deepseek"):
        return estimate_tokens_deepseek(text)
    else:
        ollama_model = model.replace("ollama:", "") if model.startswith("ollama:") else _default_ollama_model
        return await estimate_tokens_ollama(text, ollama_model)
```

#### 6.4 后端 API 端点

```python
@app.post("/api/count-tokens")
async def count_tokens(request: CountTokensRequest):
    """
    前端通过此端点获取 token 数（单文本）。

    body: {"text": "...", "model": "ollama:qwen2.5:7b"}
    返回: {"tokens": 1234}
    """
    tokens = await estimate_tokens(request.text, request.model)
    return {"tokens": tokens}


@app.post("/api/count-tokens-batch")
async def count_tokens_batch(request: CountTokensBatchRequest):
    """
    批量 token 计数（多文本并发计算，避免 N 章发 N 次请求）。

    body: {"texts": ["第1章内容...", "第2章内容..."], "model": "ollama:qwen2.5:7b"}
    返回: {"tokens": [1234, 5678]}  (顺序与 texts 一致)
    """
    tasks = [estimate_tokens(text, request.model) for text in request.texts]
    results = await asyncio.gather(*tasks)
    return {"tokens": list(results)}
```

> **推荐**：章节加载完成后前端优先使用 `/api/count-tokens-batch` 一次性获取所有章节精确 token，速度快于逐章单独请求。

#### 6.5 前端防抖调用

章节勾选变更时使用 400ms 防抖避免大量并发 API 请求：

```javascript
let recalcTimer = null;

function recalcChapterTokensDebounced(delay = 400) {
    if (recalcTimer) clearTimeout(recalcTimer);
    recalcTimer = setTimeout(() => {
        recalcTimer = null;
        recalcChapterTokens();
    }, delay);
}
```

单文本输入框 token 提示使用 300ms 防抖：

```javascript
let tokenDebounceTimer = null;

async function onInputChange(text) {
    clearTimeout(tokenDebounceTimer);
    tokenDebounceTimer = setTimeout(async () => {
        const resp = await fetch('/api/count-tokens', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, model: currentModel })
        });
        const { tokens } = await resp.json();
        updateTokenDisplay(tokens);
    }, 300);
}
```

#### 6.6 Token 数据流

```
EPUB 上传:
  _parse_epub_sync() → 章节对象 {title, text, text_cn, tokens_approx}
  前端收到后 → 侧栏显示章节列表 + tokens_approx 初始 token 数
  加载完成后 → 前端 POST /api/count-tokens-batch 批量获取精确 token → 更新侧栏 + 汇总

对话消息:
  后端 /api/chat SSE 流结束 → 用 estimate_tokens() 按实际模型计算 → SSE 发送 {"tokens_used": N}
  前端收到 → conversationTokens += N → updateContextBar()

切换模型:
  前端对已选章节 + 对话历史 → 重新调用 /api/count-tokens-batch → 更新全部 token 数

切换仅中文:
  前端对已选章节 → 用 getDisplayText() 取 text_cn → 调用 /api/count-tokens-batch → 更新
```

---

### 七、AI 对话（SSE 流式）

#### 7.1 前端发送消息（JS）

```
async function sendMessage():
    1. 检查是否有选中章节，无则提示
    2. 获取 question, model, webSearch
    3. 如果有上一个正在流式的请求，abortController.abort() 取消它
    4. 创建新的 AbortController
    5. addMessage('user', question) → 更新 UI
    6. 构造请求体:
       {
         model: "ollama:huihui_ai/qwen2.5-abliterate:7b" | "deepseek:deepseek-v4-flash",
         chapters_text: "选中的章节原文拼接",
         book_name: "书名",
         history: [{role, content}, ...],
         question: "用户问题",
         context_limit: 48000  // 用于后端章节截断判断
       }
    7. fetch POST /api/chat，signal = abortController.signal
    8. 用 resp.body.getReader() 读取 SSE 流（含跨 chunk 缓冲区，见 7.5）
    9. 逐条解析 data: 行 → 提取 content → 追加到 AI 气泡
    10. 流结束事件 data: {"tokens_used": N} → conversationTokens += N → updateContextBar()
    11. 安全超时：5 分钟（300000ms）后强制重置 isStreaming 状态，防止网络卡死导致按钮永久不可用
```

#### 7.2 后端 `/api/chat`

```python
@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    根据 model 前缀分流:
    - "ollama:" → stream_ollama()
    - "deepseek:" → stream_deepseek()

    system_prompt:
      "你是博学的阅读助手。以下是《{book}》中用户选中的章节原文。优先基于原文内容回答并引用原文。如果问题超出原文范围，可以结合你的知识回答，但要明确区分原文信息和你自己的知识。不知道就说不知道，不要编造信息。"

    响应: StreamingResponse, Content-Type: text/event-stream
    流结束前发送 data: {"tokens_used": N} 供前端更新 conversationTokens

    步骤:
    1. 构造 messages（system + history + 用户消息含章节原文）
    2. 根据 model 前缀选择流式函数
    3. 收集 AI 完整回复文本
    4. 流结束后计算 tokens_used:
       - 用户消息 token 数 + AI 回复 token 数（均用 estimate_tokens 按实际模型计算）
       - 通过 SSE 发送 data: {"tokens_used": N}
       - 最后发送 data: [DONE]
    """
```

#### 7.3 Ollama 流式

```python
async def stream_ollama(model: str, messages: list, num_ctx: int = 48000):
    """
    num_ctx 从设置面板读取，等于用户设置的 contextLimit
    直接覆盖 Ollama modelfile 中默认的 context_length
    Qwen 2.5 7B 原生支持 128K，num_ctx 设到 48K-64K 完全没问题
    """
    async with httpx.AsyncClient(timeout=300) as client:
        async with client.stream('POST', f'{OLLAMA_URL}/api/chat', json={
            'model': model,
            'messages': messages,
            'stream': True,
            'options': {'num_ctx': num_ctx}
        }) as resp:
            async for line in resp.aiter_lines():
                if line:
                    data = json.loads(line)
                    content = data.get('message', {}).get('content', '')
                    if content:
                        yield f"data: {json.dumps({'content': content})}\n\n"
```

#### 7.4 DeepSeek 流式 + 联网搜索

```python
async def stream_deepseek(model: str, messages: list):
    """
    DeepSeek Chat Completions API 流式调用。
    联网搜索由前端在发送消息前完成（见 7.6 节），搜索结果已拼入 messages。
    """
    headers = {
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json'
    }
    body = {
        'model': model,
        'messages': messages,
        'temperature': 0.7,
        'max_tokens': 4096,
        'stream': True
    }
    async with httpx.AsyncClient(timeout=120) as client:
        async with client.stream('POST', 'https://api.deepseek.com/v1/chat/completions',
                                  json=body, headers=headers) as resp:
            async for line in resp.aiter_lines():
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])
                        delta = (data.get('choices') or [{}])[0].get('delta') or {}
                        content = delta.get('content', '')
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue
                    if content:
                        yield f"data: {json.dumps({'content': content})}\n\n"
```

#### 7.5 前端 SSE 解析：跨 chunk 断行处理（重要）

`resp.body.getReader()` 读取的是原始字节流，一行 JSON 可能被切成两个 chunk。必须维护行缓冲区：

```javascript
async function streamResponse(response, onToken, onDone) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';  // 行缓冲区：跨 chunk 保留不完整的行

    while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();  // 最后一行可能不完整，保留到下次

        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const payload = line.slice(6);
                if (payload === '[DONE]') {
                    onDone();
                    return;
                }
                try {
                    const data = JSON.parse(payload);
                    if (data.content) onToken(data.content);
                    if (data.tokens_used) onTokensUsed(data.tokens_used);
                } catch (e) {
                    // 静默跳过非 JSON 行，不影响已接收内容
                }
            }
        }
    }
}
```

关键点：
- `decoder.decode(value, { stream: true })` — 多字节 UTF-8 字符跨 chunk 时不会出乱码
- `buffer = lines.pop()` — 保留不完整的最后一行到下次循环
- 空行和非 `data:` 行被静默跳过

#### 7.6 前端：联网搜索实现（仅 DuckDuckGo）

```javascript
async function searchWeb(query) {
    try {
        const resp = await fetch(
            `https://api.duckduckgo.com/?q=${encodeURIComponent(query)}&format=json&no_html=1&skip_disambig=1`,
            { signal: AbortSignal.timeout(8000) }
        );
        const data = await resp.json();
        const results = [];

        if (data.AbstractText) {
            results.push({
                title: data.Heading || '摘要',
                snippet: data.AbstractText,
                url: data.AbstractURL
            });
        }
        for (const topic of (data.RelatedTopics || [])) {
            if (topic.Text && topic.FirstURL) {
                results.push({
                    title: topic.Text.split(' - ')[0],
                    snippet: topic.Text,
                    url: topic.FirstURL
                });
            }
        }
        return results.slice(0, 5);
    } catch (err) {
        console.warn('联网搜索失败:', err);
        return [];
    }
}

function buildMessagesWithSearch(userQuestion, searchResults, chapterText, bookName, history) {
    let augmentedQuestion = userQuestion;
    if (searchResults.length > 0) {
        const ctx = searchResults.map((r, i) =>
            `[搜索结果 ${i + 1}]\n标题: ${r.title}\n来源: ${r.url}\n内容: ${r.snippet}`
        ).join('\n\n');
        augmentedQuestion =
`以下是与问题相关的网络搜索结果，请结合这些信息和《${bookName}》原文回答：

${ctx}

---
用户问题: ${userQuestion}

要求: 优先使用原文内容回答。如果原文信息不足，再参考搜索结果。引用搜索结果时需注明来源。`;
    }
    return [
        { role: "system", content: systemPrompt },
        ...history,
        { role: "user", content: augmentedQuestion }
    ];
}

// sendMessage 中集成搜索
async function sendMessage() {
    let searchResults = [];
    if (webSearchEnabled && currentModel.startsWith('deepseek')) {
        showThinkingIndicator('正在搜索...');
        searchResults = await searchWeb(question);
        hideThinkingIndicator();
    }
    const messages = buildMessagesWithSearch(question, searchResults, selectedChapterText, bookName, conversationHistory);
    // ... fetch POST /api/chat
}
```

**搜索失败降级**：

| 情况 | 处理 |
|------|------|
| 搜索超时 (8s) | 降级为普通对话，前端追加系统消息「联网搜索超时，已切换为仅基于原文回答」 |
| 搜索返回空结果 | 降级为普通对话，前端追加系统消息「未找到相关搜索结果」 |
| 网络离线 | 静默跳过搜索（fetch 本身抛错被 catch） |

---

### 八、上下文管理

#### 8.1 上下文窗口配置

```
// 启动时后端调 GET /api/tags → 返回模型名 + API 报告的 context_length
// context_length 是 Ollama modelfile 中设的默认值（如 32768），不是模型上限
// Qwen 2.5 7B 真正上限是 128K，通过 num_ctx 参数覆盖即可

// contextLimit (用户可调整):
// - 默认值: 48000
// - 范围: 8000 ~ 128000
// - 滑块上限: 128000（模型真正上限）

// API 报告的 context_length (32768) 仅在前端展示为"Ollama 默认值: 32768"，不影响滑块上限
// 如果 Ollama 不可用，兜底: contextLimit = 48000
```

#### 8.2 Token 追踪（JS 端，数据来自后端 API）

```
let conversationTokens = 0;  // 来自后端 SSE 流结束时的 tokens_used 通知
let chapterTokens = 0;       // 通过 POST /api/count-tokens-batch 异步计算

const CHAPTER_WARN_LIMIT = 40000;
let contextLimit = 48000;

// 发送消息后: SSE 流结束时收到 {"tokens_used": N} → conversationTokens += N
// 勾选/取消章节时: POST /api/count-tokens-batch 批量重算已选章节 → chapterTokens 更新
// 用户输入时: 防抖 300ms → POST /api/count-tokens（单文本） → 更新输入框旁的 token 提示
// 重置对话时: conversationTokens = 0（chapterTokens 不变）
// 切换「仅中文」时: 用 getDisplayText() → POST /api/count-tokens-batch → chapterTokens 更新
// 切换模型时: POST /api/count-tokens-batch（不同 tokenizer）→ chapterTokens 重算

// 两档检查:
// 1. chapterTokens > 40K → 侧栏汇总 + 对话区顶部同时显示 ⚠️ 警告
// 2. chapterTokens + conversationTokens > contextLimit → 拒绝发送，提示重置
```

#### 8.3 上下文进度条

```
updateContextBar():
    total = chapterTokens + conversationTokens
    pct = total / contextLimit * 100
    颜色: 🟢<60% / 🟡60-80% / 🔴80-90% / ⚫90-100%
    百分比 < 1% 时显示一位小数（如 0.5%），避免始终显示 0%

    chapterTokens > 40K 时:
      对话区顶部显示警告条 "⚠️ 选中章节超过 40K tokens（XX K），建议减少章节选择以确保对话空间"
      警告条可关闭
```

#### 8.4 上下文管理策略（两层渐进式，v2.2 去掉 AI 压缩）

> **v2.2 简化**：去掉 AI 压缩策略（策略 2），仅保留自动滑动窗口 + 手动重置。两层策略足够覆盖所有实际场景，减少约 100 行代码和一个后端压缩步骤。

##### 策略 1：自动滑动窗口（默认，80% 时触发）

保留最近 N 轮对话，自动移除最早的消息，插入摘要。

```javascript
const MAX_CONVERSATION_ROUNDS = 8;

function applySlidingWindow(history) {
    const userMessages = history.filter(m => m.role === 'user');
    const rounds = userMessages.length;

    if (rounds <= MAX_CONVERSATION_ROUNDS) {
        return { history, dropped: 0 };
    }

    const cutoffIndex = history.findIndex(
        (m, i) => m.role === 'user' &&
        history.slice(0, i + 1).filter(x => x.role === 'user').length > rounds - MAX_CONVERSATION_ROUNDS
    );

    const dropped = history.slice(0, cutoffIndex);
    const recent = history.slice(cutoffIndex);

    const topicList = dropped
        .filter(m => m.role === 'user')
        .map(m => m.content.slice(0, 80))
        .join('；');

    return {
        history: [
            { role: 'system', content: `[早期讨论摘要] 此前讨论了：${topicList || '无'}` },
            ...recent
        ],
        dropped: Math.floor(dropped.filter(m => m.role === 'user').length)
    };
}
```

##### 策略 2：完全重置（手动触发）

```
resetConversation():
    1. showConfirm("确定要重置对话吗？章节选择和原文不受影响。")
    2. 用户确认后:
       - chatArea.innerHTML = ''（清空对话 DOM）
       - 插入系统消息 "📝 对话已重置，可以开始新的讨论"
       - conversationTokens = 0
       - updateContextBar()
       - 发送按钮恢复可用
```

##### 上下文监控与触发逻辑

```javascript
function checkContextAndHandle() {
    const total = chapterTokens + conversationTokens;
    const pct = total / contextLimit;

    if (pct >= 0.95) {
        // 95% 弹窗（不可关闭），提供两个选项
        showContextFullDialog();
    } else if (pct >= 0.85) {
        // 85% 温和提示，建议重置
        showContextWarningBar('上下文接近上限，建议重置对话以释放空间');
    }

    if (pct >= 0.80 && conversationTokens > 0) {
        // 80% 静默自动滑动窗口
        const result = applySlidingWindow(conversationHistory);
        if (result.dropped > 0) {
            conversationHistory = result.history;
            recalcConversationTokens();
            insertSystemMessage(`📝 已自动移除 ${result.dropped} 轮较早对话，保留最近讨论`);
            updateContextBar();
        }
    }
}
```

##### 上下文满弹窗 UI（简化后，两个选项）

```
┌─────────────────────────────────────────────────────┐
│  ⚠️ 上下文已接近上限 (95%)                           │
│                                                     │
│  请选择处理方式：                                    │
│                                                     │
│  ○ 启用自动滑动窗口（推荐）                          │
│    保留最近 8 轮对话 + 早期讨论摘要，释放空间          │
│                                                     │
│  ○ 完全重置对话                                      │
│    清空所有对话历史，仅保留章节选择                     │
│                                                     │
│                              [确认]  [稍后再说]       │
└─────────────────────────────────────────────────────┘
```

##### 设置面板中的上下文管理选项

```
上下文管理策略:
☑ 自动滑动窗口（到达 80% 时自动移除早期对话，推荐）
☐ 80% 时弹窗询问（不自动滑动窗口）
  滑动窗口保留轮数: [8] 轮
```

---

### 九、模型切换

#### 9.1 模型选择下拉

- **本地 Ollama**：页面加载时通过 `GET /api/ollama-models` 动态填充
  - 启动时后端调 Ollama API，返回模型名（如 `huihui_ai/qwen2.5-abliterate:7b`）和 `context_length`
  - 前端自动设为默认模型，`context_length` 仅作为"Ollama 默认值"展示，滑块上限固定 128000
- **DeepSeek (云端)**：手动切换，固定选项 `deepseek-v4-flash` / `deepseek-chat`
- 切换回 Ollama 时，恢复之前的 Ollama 模型选择

```
<select id="model-select">
  <optgroup label="本地 Ollama">
    <!-- 动态填充，仅显示模型原始名称 -->
    <option value="ollama:huihui_ai/qwen2.5-abliterate:7b">
      huihui_ai/qwen2.5-abliterate:7b
    </option>
  </optgroup>
  <optgroup label="DeepSeek (云端)">
    <option value="deepseek:deepseek-v4-flash">deepseek-v4-flash</option>
    <option value="deepseek:deepseek-chat">deepseek-chat</option>
  </optgroup>
</select>
```

#### 9.2 联网搜索（切换 DeepSeek 后自动启用）

- 用户从模型下拉切换到 DeepSeek 后，联网搜索**自动开启**，无需独立按钮
- 选择 Ollama 时自动关闭联网搜索
- 启用后，前端 JS 调 DuckDuckGo Instant Answer API 获取搜索结果 → 拼入 messages → 后端正常流式生成
- 切换回 Ollama 时自动关闭联网搜索
- 搜索超时/失败时静默降级为普通对话，追加系统提示
- 前端 toast 提示「已切换到 DeepSeek，发送消息时将自动开启联网搜索」

#### 9.3 Ollama 模型列表获取（后端）

```python
@app.get("/api/ollama-models")
async def get_models():
    """
    返回本地 Ollama 模型列表 + 每个模型的 context_length
    """
    import httpx
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
```

---

### 十、保存到 Obsidian

#### 10.1 两种保存方式

**方式一：快捷保存单条消息**
- 每条 AI 回复 hover 时气泡右上角浮现保存图标（⊞）
- 点击后将本条消息作为 Markdown 追加到 vault
- 点击后图标短暂变为「✓」确认反馈

**方式二：多选保存（保存模式）**
- 点击侧栏底部「保存」按钮 → 进入保存模式
- 每条消息左侧出现 ☐ 勾选框
- 用户勾选要保存的消息
- 点击「确认保存」→ POST /api/save-obsidian
- 按 Esc 或再次点击「保存」按钮退出保存模式

#### 10.2 后端保存（含路径穿越防护）

##### 10.2.1 安全文件名过滤函数

```python
import os
import re
from pathlib import Path

def sanitize_filename(name: str, max_length: int = 80) -> str:
    """
    三层安全过滤：
    1. 移除所有控制字符、路径分隔符和特殊字符
    2. 防止 .. 路径穿越和隐藏文件写入
    3. 长度截断 + 空文件名兜底

    设计原则：白名单 > 黑名单。只保留明确安全的字符。
    """
    # 第一层：移除控制字符 + 危险字符
    # \x00-\x1f: 控制字符（\t \n \r \0 等会导致文件系统问题）
    # 注意：用双引号 raw string 避免 r'...\'...' 中 \' 提前终止字符串
    safe = re.sub(r"[\x00-\x1f<>:\"/\\|?*'`$&;!@#%^(){}\[\]~]", '', name)

    # 第二层：防止路径穿越
    safe = re.sub(r'\.{2,}', '.', safe)      # ".." → "."
    safe = re.sub(r'^\.+', '', safe)         # 去掉开头的点（防止隐藏文件如 .bashrc）
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
```

##### 10.2.2 API 端点

```python
@app.post("/api/save-obsidian")
async def save_obsidian(request: SaveRequest):
    """
    body: {
        book_name: "书名",
        messages: [
            {role: "user", content: "..."},
            {role: "assistant", content: "..."},
            ...
        ]
    }
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filepath = build_save_path(VAULT_PATH, request.book_name, timestamp)

        lines = [f"# 《{request.book_name}》阅读对话",
                 f"> 保存时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ""]
        for msg in request.messages:
            if msg.role == "user":
                lines.append("**🧑 你**")
            else:
                lines.append("**🤖 AI**")
            lines.append(msg.content)
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
```

##### 10.2.3 安全加固检查点

| 防护层 | 作用 |
|--------|------|
| `\x00-\x1f` 控制字符过滤 | 移除 `\t` `\n` `\r` `\0` 等会导致文件系统异常的字符 |
| `<>:"/\|?*...` 特殊字符过滤 | 移除路径分隔符和 shell 特殊字符 |
| `re.sub(r'\.{2,}', '.', safe)` | 连续点号压缩为单个（`....` → `.`） |
| `re.sub(r'^\.+', '', safe)` | 去掉开头点号（防止 `.bashrc` 等隐藏文件） |
| `Path.resolve()` | 规范化路径，解析符号链接 |
| `startswith(vault)` 检查 | **最后防线**：确保最终路径在 vault 范围内 |
| `max_length=80` | 防止超长文件名导致文件系统问题 |

---

### 十一、UX 增强

#### 11.1 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Enter` | 发送消息（仅在输入框有内容、已加载书籍且有选中章节时发送；空输入/无章节时正常换行） |
| `Shift + Enter` | 换行 |
| `Esc` | 关闭设置面板 / 退出保存模式 / 关闭确认弹窗 |
| `Ctrl/Cmd + F` | 在原文阅读区搜索（浏览器默认行为，需确保焦点在阅读区） |
| `Ctrl/Cmd + =` | 阅读区字体放大（+1px） |
| `Ctrl/Cmd + -` | 阅读区字体缩小（-1px） |

#### 11.2 全局字体大小调节（阅读区 + 对话气泡 + 输入框统一）

使用 CSS 变量 `--content-font-size` 统一控制，一个变量改动全局生效：

```javascript
const FONT_MIN = 14, FONT_MAX = 22, FONT_DEFAULT = 16;
let globalFontSize = parseInt(localStorage.getItem('readerFontSize')) || FONT_DEFAULT;

function applyFontSize(size) {
    globalFontSize = size;
    localStorage.setItem('readerFontSize', size);
    document.documentElement.style.setProperty('--content-font-size', size + 'px');
}
function adjustFont(delta) { applyFontSize(Math.max(FONT_MIN, Math.min(FONT_MAX, globalFontSize + delta))); }

// 快捷键
document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === '=') { e.preventDefault(); adjustFont(1); }
    if ((e.ctrlKey || e.metaKey) && e.key === '-') { e.preventDefault(); adjustFont(-1); }
});

applyFontSize(globalFontSize);
```

对应的 CSS：
```css
:root { --content-font-size: 16px; }
#reader-content, .msg-bubble, #chat-input-area textarea { font-size: var(--content-font-size); }
```

阅读区右上角有「缩小」「放大」按钮（Apple 分段控件风格），点击调节。

#### 11.3 localStorage 缓存

```
页面加载时恢复:
  - contextLimit (设置)
  - 最近加载的书名和章节列表（不含原文全文，仅元信息）
  - 最近一次对话历史（最多 20 条消息）
  - readerFontSize (阅读区字号)

页面关闭/刷新前自动保存当前状态到 localStorage

恢复后:
  - 章节列表重新显示
  - 对话历史重新渲染
  - 但原文需要重新从 EPUB 加载（因文件较大不适合存 localStorage）
  - 如果 EPUB 文件已不可用，尝试从服务端缓存恢复；如果缓存也不可用，显示提示 + 仅恢复对话记录
```

#### 11.4 AbortController（流式取消）

```
let activeAbortController = null;

async function sendMessage():
    if (activeAbortController):
        activeAbortController.abort()    // 取消上一个流
    activeAbortController = new AbortController()

    try:
        response = await fetch(url, {signal: activeAbortController.signal})
        // ... 流式读取
    catch (err):
        if (err.name === 'AbortError'):
            return  // 正常的取消操作，不报错
        // 其他错误处理
```

#### 11.5 可拖拽分栏

```
实现方式: CSS + 少量 JS
- 在 aside 和 reader 之间放一条 4px 的拖拽手柄 (grabber)
- 在 reader 和 chat 之间同样放一条
- 拖拽时实时调整相邻两列的 flex-basis
- 最小宽度保护: 侧栏 ≥180px, 阅读区 ≥250px, 对话区 ≥300px
- 拖拽手柄 hover 时改变颜色和光标样式
```

#### 11.6 章节搜索

```
- 侧栏顶部搜索框
- 输入时实时过滤（debounce 150ms）
- 匹配规则: chapter.title.toLowerCase().includes(query.toLowerCase())
- 无匹配结果时显示 "无匹配章节"
- 搜索不影响已选中的章节勾选状态
```

#### 11.7 消息快捷操作

```
每条消息 hover 时，气泡上方浮现工具栏（白色浮层卡片，带阴影）：
  用户消息: 复制图标（SF Symbols 风格 SVG：两个重叠矩形）
  AI 回复:  复制图标 + 保存图标（向下箭头到托盘 SVG）

图标 30×30px 触控区域，线条 1.8px 灰色 stroke，hover 变 accent 橙色。
点击后图标短暂变为 ✓ 勾号 + toast 反馈。
工具栏仅在 hover 时出现，opacity 渐变过渡。
```

---

### 十二、设置面板

点击右上角 ⚙ 图标打开模态面板：

```
┌──────────────────────────────────────┐
│  ⚙ 设置                          ✕  │
│                                      │
│  上下文窗口大小                        │
│  ┌───────┬──────────────────┐        │
│  │ 48000 │ ●━━━━━━━━━○ 128000│       │
│  └───────┴──────────────────┘        │
│  当前: 48000 tokens                   │
│  Ollama 默认: 32768 (num_ctx 可覆盖)  │
│  (建议 48K-64K，M3 16GB 上限约 64K)   │
│                                      │
│  双语处理                             │
│  ☑ 仅显示中文内容（即时切换）            │
│                                      │
│  上下文管理策略                         │
│  ☑ 自动滑动窗口（80% 时移除早期对话）     │
│  ☐ 80% 时弹窗询问（不自动滑动）          │
│  保留最近 [8] 轮对话                    │
│                                      │
│  Obsidian 保存路径                     │
│  ┌──────────────────────────────┐    │
│  │ Inbox/Epub阅读/               │    │
│  └──────────────────────────────┘    │
│                                      │
│  [恢复默认设置]                        │
└──────────────────────────────────────┘
```

- 上下文窗口大小滑块
  - 范围：8000 ~ 128000（模型真正上限）
  - 默认值：48000
  - 步长：2000
  - 显示 Ollama API 报告的默认值（如 32768）仅供信息参考，不影响实际使用
  - 建议标注："建议 48K-64K，M3 16GB 内存建议不超过 64K"
- 设置实时生效，change 事件触发 `updateContextBar()`
- 自动保存到 localStorage
- 切换为 DeepSeek 时：滑块自动扩展到 128000
- 切换回 Ollama 时：恢复之前的设置值

---

### 十三、API 端点汇总

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | pathlib 读取 index.html 并返回 |
| GET | `/api/ollama-models` | 获取本地 Ollama 模型列表 |
| POST | `/api/count-tokens` | 单文本 token 计数（按模型选择 tokenizer，POST body 避免 URL 长度限制） |
| POST | `/api/count-tokens-batch` | 批量 token 计数（多文本并发，前端加载章节后一次性获取精确值） |
| POST | `/api/load-epub` | 上传 EPUB，返回章节列表 + 书名（章节含 tokens_approx） |
| POST | `/api/chat` | 发送对话，SSE 流式返回 AI 回复（流结束时返回 tokens_used）；body 含 `context_limit` 用于章节截断 |
| POST | `/api/save-obsidian` | 保存选中的对话消息到 Obsidian vault（含路径穿越防护） |
| POST | `/api/log-error` | 前端 JS 错误上报（`window.onerror` 自动发送） |

共 8 个端点。

---

### 十四、EPUB 上传与历史记录

#### 14.1 上传流程

1. 点击「打开 EPUB」按钮 → 触发隐藏的 `<input type="file" accept=".epub">`
2. 选择文件后自动上传：FormData → `POST /api/load-epub`
3. 后端检查文件大小（Content-Length > 100MB → 413），通过后 `run_in_executor` 解析
4. 后端解析成功 → 返回章节列表 + 书名
5. 前端更新侧栏：显示章节列表（token 数初始为 tokens_approx 启发式估算值）+ 更新历史记录
6. 前端异步调用 `/api/count-tokens-batch` 批量获取精确 token → 更新侧栏数字
7. 后端解析异常（触发修复降级）→ 返回章节列表 + `repair_level: 1~3`（见 5.3 节）
8. 前端根据 repair_level 显示对应 toast
9. 服务重启后：前端尝试从后端缓存恢复；缓存未命中则提示重新上传

#### 14.2 历史记录存储

```javascript
// localStorage key: 'epub-reader-history'
// 结构:
[
  {
    name: "三体",
    chapters: [{title: "第1章"}, ...],
    totalChapters: 34,
    lastOpened: "2026-07-16T12:00:00"
  },
  ...
]
// 最多 10 条，超出自动删除最旧的
// 注意：仅存元信息，不含全文（全文在服务端内存/缓存中）
```

#### 14.3 从历史记录加载

- 点击历史条目 → 前端 `async function loadFromHistory(name)` 发起请求检查服务端是否有该书全文
  - 有 → 直接显示章节列表
  - 无 → 尝试从 tempfile 缓存恢复（`load_cached_epub`）
  - 缓存也不可用 → 提示「需要重新上传 EPUB 文件」+ 上传按钮高亮
- 加载历史书时，之前选中但未保存的章节选择不保留

#### 14.4 加载新书时的状态处理

- 当前有活跃对话 → 弹窗确认「加载新书将清空当前对话，是否继续？」
- 用户确认 → 清空对话 + 重置 token 计数 + 加载新书章节
- 用户取消 → 保持当前状态

#### 14.5 文件输入注意

- file input 不能使用 `display:none`（Safari 下 click() 失效）
- 不能使用极小尺寸（部分浏览器限制 click()）
- 使用按钮 click → fileInput.click() 间接触发

---

### 十五、启动逻辑

#### 15.1 上传大小限制中间件

```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

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
```

#### 15.2 Python 启动代码

```python
if __name__ == "__main__":
    import webbrowser

    # 1. 启动时尝试连接 Ollama，获取本地模型列表
    #    GET /api/tags → 获取模型名 + context_length
    #    设置全局 _default_ollama_model 和 _ollama_context_length
    #    如果不可用：打印警告，_default_ollama_model = ""

    # 2. 设置 VAULT_PATH（独立于 API Key，始终需要，保存 Obsidian 功能依赖此路径）
    #    优先级: 环境变量 OBSIDIAN_VAULT_PATH > iCloud 默认路径
    #    iCloud 默认路径: ~/Library/Mobile Documents/iCloud~md~obsidian/Documents/BWObsidianVault
    if not VAULT_PATH:
        VAULT_PATH = os.path.expanduser(
            "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/BWObsidianVault"
        )

    # 3. 如果 DEEPSEEK_API_KEY 为空，尝试从 Obsidian vault 的 API Key.md 读取
    if not DEEPSEEK_API_KEY and VAULT_PATH:
        DEEPSEEK_API_KEY = _read_api_key_from_vault()

    # 4. 打印启动信息
    print("📚 EPUB 整本书阅读器 v2.2")
    if _default_ollama_model:
        print(f"  本地模型: {_default_ollama_model} (上下文 {_ollama_context_length} tokens)")
    else:
        print("  ⚠️ Ollama 未运行，请先执行 ollama serve")
    print(f"  默认上下文窗口: {min(48000, _ollama_context_length) if _ollama_context_length else 48000} tokens")
    print(f"  本地: http://localhost:{PORT}")

    webbrowser.open(f"http://localhost:{PORT}")
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")
```

#### 15.3 macOS 一键启动脚本 `start.command`

```bash
#!/bin/bash
cd "$(dirname "$0")"
echo "📚 正在启动 EPUB 阅读器..."
python3 epub_reader.py
```

```bash
chmod +x start.command
```

---

### 十六、Git 版本控制规约

```
每个功能模块完成后 commit:

1. feat: epub 解析和章节列表       → 测试: 打开 EPUB → 章节显示
2. feat: 原文阅读面板               → 测试: 勾选章节 → 原文显示
3. feat: ollama 流式对话            → 测试: 发消息 → SSE 流式输出
4. feat: deepseek 模型切换和联网    → 测试: 切换模型 → 联网搜索
5. feat: 上下文管理和重置            → 测试: 进度条 → 满时弹窗 → 重置
6. feat: obsidian 保存              → 测试: 勾选消息 → 保存到 vault
7. feat: 设置面板和 localStorage    → 测试: 调滑块 → 刷新恢复
8. feat: ux 增强(快捷键/拖拽/搜索)   → 测试: 快捷键 → 面板拖拽
```

每次 commit 前确保当前功能可用，再开始下一个。

---

### 十七、验证清单

每次修改代码后快速确认：

```
□ EPUB 拖拽/选择加载 → 章节列表正常显示 (repair_level=0)
□ EPUB3 nav.xhtml → TOC 正确提取
□ EPUB OPF 损坏 → Level 1 重建 OPF 成功 + toast 提示
□ EPUB ZIP 损坏 → Level 2 宽松模式修复成功 + toast 提示
□ EPUB 严重损坏 → Level 3 原始提取文本片段 + toast 提示
□ DRM 加密 EPUB → 四级降级全部失败，显示明确错误提示
□ 纯图片 EPUB → 返回「未提取到文本内容」
□ 文件 >100MB → 返回 413 错误
□ 双语 EPUB → 「仅中文」开关即时切换（无需重新上传）
□ 历史记录 → 加载后显示在侧栏，点击可恢复
□ 服务重启后 → 缓存命中，无需重新上传
□ 删除历史条目 → 确认后移除
□ 加载新书时正在对话 → 弹窗确认
□ 章节搜索框 → 能过滤章节
□ 勾选/取消章节 → token 计数异步更新
□ 章节超过 40K → 侧栏 + 对话区双警告
□ 超出 contextLimit → 变红 + 发送按钮禁用
□ 原文阅读区 → 显示选中章节内容
□ 字体大小调节 → 阅读区 + 对话气泡 + 输入框三者同步缩放，刷新后恢复
□ 可拖拽分栏 → 拖拽手柄可调整列宽
□ Ollama 对话 → SSE 流式输出正常
□ SSE 跨 chunk 断行 → 不丢消息
□ AI 回复 Markdown 渲染 → 加粗/列表/代码块正常
□ Ctrl+Enter → 发送消息
□ 切换 DeepSeek → 联网搜索自动启用，toast 提示
□ DuckDuckGo 搜索 → 结果拼入对话上下文
□ 搜索超时/失败 → 静默降级为普通对话
□ 上下文进度条 → 颜色随百分比变化
□ 上下文 80% → 自动滑动窗口触发
□ 上下文 85% → 温和提示条出现
□ 上下文 95% → 弹窗（两选项：滑动窗口 / 重置）
□ 仅中文开关 → 即时切换原文/中文版（无需重新上传）
□ 模型切换 → token 重新计算（不同 tokenizer）
□ 重置后 → 对话清空但章节保持
□ 消息 hover → 复制/保存按钮出现
□ 保存模式 → 多选消息 → 保存到 Obsidian
□ 设置面板 → 调整上下文窗口大小生效
□ 刷新页面 → localStorage 恢复历史列表和对话
□ 发送中切换模型 → 不中断，下次发送生效
□ Ollama 未启动 → 前端明确提示
□ 关闭流式 → 发新消息 abort 旧请求
```

---

### 十八、版本间的主要区别

#### v2.2 vs v2.1

| 项目 | v2.1 | v2.2 |
|------|------|------|
| EPUB 解析并发 | `async def parse_epub` 直接执行 CPU 密集操作 | `run_in_executor` 放入线程池 |
| 解析时 token 计算 | 调 Ollama API（阻塞、慢） | 纯本地启发式估算（快速） |
| 章节对象 | `{title, text, text_cn, chars, chars_cn, tokens, tokens_cn, is_bilingual}` | `{title, text, text_cn, tokens_approx}`（精简 4 个字段，增加 tokens_approx 占位） |
| Token 精确值 | 解析时计算 | 加载后前端通过 `/api/count-tokens-batch` 批量获取 |
| 中文过滤 | `re` + 硬编码范围 `[一-鿿㐀-䶿豈-﫿]` | `regex` + `\p{Han}`（覆盖全部扩展区） |
| 上下文管理 | 三层：滑动窗口 + AI 压缩 + 手动重置 | 两层：滑动窗口 + 手动重置（去掉 AI 压缩） |
| 联网搜索 | DuckDuckGo / SearXNG / Bing 三方案 | 仅 DuckDuckGo 单一方案 |
| SSE 流解析 | 未处理跨 chunk 断行 | 行缓冲区 + TextDecoder stream 模式 |
| 上传限制 | 文档提及 100MB，代码未实现 | 中间件检查 Content-Length，超限返回 413 |
| EPUB3 支持 | 仅 toc.ncx | 同时检查 nav.xhtml（EPUB3）+ toc.ncx（EPUB2） |
| 文件名安全 | 过滤 `<>:"/\|?*...` | 新增 `\x00-\x1f` 控制字符过滤 |
| 解析缓存 | 无 | tempfile pickle 缓存（hashlib.md5 做 key），服务重启后可恢复 |
| 字体调节 | 无 | 阅读区 Ctrl+/- 和按钮调节字号 (14-22px) |
| API 端点数 | 6 个 | 7 个（新增 `/api/count-tokens-batch` 批量接口） |
| 依赖 | fastapi uvicorn ebooklib beautifulsoup4 httpx python-multipart tiktoken | 新增 `regex` |
| ZIP 修复 | `zipfile.ZipFile(strict=False)`（不存在） | `ZipFile + try/except` 逐个提取（修复无效参数） |

#### v2.3 vs v2.2

| 项目 | v2.2 | v2.3 |
|------|------|------|
| 发送快捷键 | `Ctrl/Cmd+Enter` | `Enter`（有内容+有章节时发送），`Shift+Enter` 换行 |
| IME 安全 | 无 | `e.isComposing` 检查，中文输入法不误触发 |
| 清空按钮 | 仅清空历史列表 | 同时清空当前书籍、章节、对话 |
| 系统提示词 | 「严格基于原文内容回答」 | 「优先基于原文 + 可结合知识回答 + 诚实说明不确定」 |
| 前端错误上报 | 无 | `window.onerror` → `POST /api/log-error`（8 个端点） |
| 章节自动选择 | 前 2 章 | 跳过 < 200 字章节，优先选正文 |
| 进度条 | 百分比取整 | < 1% 时显示一位小数 |
| 发送按钮流式状态 | 流式输出时禁用按钮 | 改为 spinner + 可点击停止 |
| Token 重算 | 每次勾选立即调 API | 400ms 防抖，避免批量请求 |
| 流式超时 | 无保护 | 5 分钟安全超时强制重置 |
| Ollama HTTP 超时 | 120s | 300s |
| 章节截断 | 无 | 后端 `/api/chat` 根据 `context_limit` 自动截断 |
| `/api/tokens` 404 | 每次都重试 | 全局缓存 404，后续不再请求 |
| `loadFromHistory` | `function`（缺 `async`） | `async function`（修复语法错误） |
| `run_in_executor` | `asyncio.get_event_loop()` | `asyncio.get_running_loop()`（修复 DeprecationWarning） |
| `marked.js` CDN | 头同步加载 | 移除 CDN 依赖，纯文本降级显示 |

---

### 十九、错误处理与边界情况

#### 19.1 Ollama 相关

| 情况 | 处理 |
|------|------|
| Ollama 未启动（`/api/tags` 超时） | 后端打印警告，`_default_ollama_model = ""`，前端模型下拉显示「Ollama 未运行」+ 提示 `ollama serve` |
| Ollama 模型不存在 | 启动时检查，模型列表为空时提示用户先 `ollama pull <model>` |
| Ollama 生成超时 | `httpx.AsyncClient(timeout=120)`，超时后 SSE 流发送 `{"error": "ollama 响应超时"}` |
| Ollama 流中断 | 前端已收到的内容保留在气泡中 + 追加系统消息「⚠️ 连接中断，回复不完整」 |
| Ollama `/api/tokens` 不可用 | 静默回退 `heuristic_token_count()` |

#### 19.2 DeepSeek 相关

| 情况 | 处理 |
|------|------|
| 401 鉴权失败 | 显示「DeepSeek API Key 无效，请设置环境变量 DEEPSEEK_API_KEY」 |
| 429 频率限制 | 显示「请求过于频繁，请稍后重试」+ 建议切回 Ollama |
| 网络超时 | 显示「无法连接 DeepSeek API，请检查网络」+ 自动切回 Ollama |
| DuckDuckGo 搜索不可用 | 降级为普通对话（不带搜索上下文），追加系统消息「联网搜索暂不可用」 |

#### 19.3 EPUB 解析相关

| 情况 | 处理 |
|------|------|
| 文件非 EPUB 格式（非 ZIP 或无 mimetype） | 返回 400 `{"error": "文件格式不支持，请上传 .epub 文件"}` |
| 文件过大（>100MB） | 中间件拦截，返回 413 `{"error": "文件过大，请上传小于 100MB 的 EPUB"}` |
| Level 0 失败 → Level 1 OPF 修复 | 自动重建 OPF 并重试，成功后返回 `repair_level: 1` + toast |
| Level 1 失败 → Level 2 ZIP 修复 | `ZipFile + try/except` 逐个提取成员，跳过损坏文件，返回 `repair_level: 2` + toast |
| Level 2 失败 → Level 3 原始提取 | 多编码尝试 + 正则提取文本片段，返回 `repair_level: 3` + toast |
| Level 3 也失败（无任何可读文本） | 返回 422 `{"error": "无法解析此 EPUB，文件可能受 DRM 保护或为纯图片格式"}` |
| 解析成功但总字符 < 500 | 警告 toast「文本内容极少，可能为图片型 EPUB」 |
| 编码检测失败（非 UTF-8） | 依次尝试 gbk → latin-1 → cp1252，选择产生最多中文字符的编码 |
| TOC 提取为空 | 从 nav.xhtml（EPUB3）→ toc.ncx（EPUB2）→ `<h1>-<h6>` 自动生成 → 数字序号兜底 |
| `run_in_executor` 中线程异常 | 捕获后返回 422 错误，不泄漏 traceback |
| pickle 缓存写入失败 | 静默跳过，不影响主流程 |

#### 19.4 保存 Obsidian 相关

| 情况 | 处理 |
|------|------|
| Vault 路径不存在 | 返回 500 + 提示用户检查路径 |
| 写入权限不足 | 返回 500 + 提示检查文件夹权限 |
| sanitize_filename 后为空文件名 | 兜底用 `untitled` |
| 路径穿越检测（最终路径不在 vault 内） | 返回 400 `{"error": "路径无效"}` |
| 同名文件已存在 | 时间戳精确到秒，极小概率冲突；冲突时追加 `_2` 后缀 |

#### 19.5 前端边界情况

| 情况 | 处理 |
|------|------|
| localStorage 满了 | 清理最旧的历史记录，仅保留最近 5 条 |
| 浏览器不支持 Clipboard API | 降级到 `document.execCommand('copy')` |
| 网络断开 | fetch 失败时显示「网络连接失败，请检查服务是否运行」 |
| SSE 流解析到非 JSON 行 | 静默跳过，不影响已接收内容 |
| SSE 单行 JSON 跨两个 chunk | 行缓冲区积累不完整行，等下一个 chunk 拼接（见 7.5 节） |
| 用户快速连击发送按钮 | 发送按钮首次点击后立即 disabled，等回复完成再恢复 |
| `/api/count-tokens-batch` 调用失败 | 整体失败时回退到逐章 `/api/count-tokens` 单独请求；单章失败保留 tokens_approx |
| JS 脚本解析错误 | `window.onerror` 自动上报到 `POST /api/log-error`，服务端日志记录消息、行号、堆栈 |
| `marked.js` CDN 加载失败 | 降级为纯文本渲染（`typeof marked !== 'undefined'` 检查），不影响页面功能 |

#### 19.6 状态冲突处理

| 情况 | 处理 |
|------|------|
| 加载新 EPUB 时正在对话 | 弹窗确认「加载新书将清空当前对话」→ 用户确认后才加载 |
| 切换模型时正在流式输出 | 不中断当前流，模型切换在下次发送时生效 |
| 章节选择改变时正在对话 | 不影响当前对话，新选择在下次发送时生效（提示用户「章节已变更，请重置对话」） |
| 刷新页面后恢复状态 | localStorage 恢复历史列表 + 最近对话，服务端缓存恢复 EPUB 数据 |
| 服务重启 | 尝试从 tempfile pickle 缓存恢复；缓存未命中则提示重新上传 |
