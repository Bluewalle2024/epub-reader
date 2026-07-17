# EPUB Reader — AI-Powered EPUB Reader

Electron-free EPUB 整书阅读器。Python FastAPI 后端 + HTML/CSS 单页前端 + AI 聊天，
PyInstaller 打包为 macOS .app。

## Quick Start

```bash
# 开发运行
python3 epub_reader.py
# 或双击 start.command

# 打包为 .app
./pack.sh
# 输出: dist/EPUB阅读器.app
```

## Architecture

```
epub_reader.py          # FastAPI 后端(约 48KB): 解析 EPUB, API 路由, AI 聊天
index.html              # 单页前端(约 99KB): HTML+CSS+JS, 阅读器 UI + 聊天面板
pack.sh                 # PyInstaller 打包脚本
start.command           # 双击启动(调用 python3 epub_reader.py)
tiktoken_cache/         # tiktoken 分词器缓存(打包时需包含)
scripts/                # 构建辅助脚本
```

## Key Dependencies

- `fastapi` + `uvicorn` — Web 框架
- `ebooklib` + `bs4` — EPUB 解析
- `webview` — 原生窗口嵌入浏览器
- `tiktoken` — Token 计数
- `PyInstaller` — 打包为 .app

## Development Notes

- 开发提示词和 changelog 在 `Epub阅读器开发提示词-v2.7.md` / `-v2.8.md` 文件里
- 前端是全栈单文件 `index.html`，包含了完整的阅读器 UI 和 AI 聊天功能
- `tiktoken_cache/` 目录必须在打包时通过 `--add-data` 包含，否则首次运行会下载失败
- 打包用 `--windowed` 模式(无终端窗口)，调试时直接用 `python3 epub_reader.py` 看输出

## Git

```bash
origin  https://github.com/Bluewalle2024/epub-reader.git
```
