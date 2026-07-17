# EPUB 整本书阅读器 — 开发提示词 v2.8

> 更新：2026-07-17
>
> v2.8 变更（阅读与 AI 上下文解耦 + 章节联动高亮）：
> 1. **原文区显示全书**：`renderReaderArea()` 始终渲染全部章节，不再受勾选状态限制。无勾选也能自由翻阅全书。
> 2. **勾选仅影响 AI 上下文**：章节勾选（checkbox）只决定发给 AI 的上下文范围，与阅读无关。
> 3. **章节点击独立跳转**：点击章节文字直接跳转原文，不自动勾选，不改变选中状态。
> 4. **侧边栏章节联动高亮**：滚动原文时，左侧章节列表同步高亮当前阅读章节（accent 色左侧竖线 + 浅色背景）。
> 5. **阅读区标题同步**：左上角章节名随滚动实时更新（`updateReaderChapterNav` 增强）。
> 6. **章节搜索联动**：搜索/清除搜索时原文区始终同步刷新，不受勾选限制。

> Git: (v2.8)

---

## 技术要点

### 阅读与上下文完全解耦
- `selectedChapters`（Set）→ 仅用于 AI 上下文 token 计算和发送
- `chapters`（Array）→ 原文区渲染全部章节
- `renderReaderArea()` 空状态仅在没有加载书籍时显示（`chapters.length === 0`）

### 章节联动高亮
- CSS: `.chapter-item.viewing { background: var(--accent-bg); box-shadow: inset 2px 0 0 var(--accent); }`
- JS: `updateReaderChapterNav()` 在滚动时计算当前章节 idx，更新 sidebar 中 `.viewing` class

### 章节交互拆分
- **勾选框/圆圈** → `handleChapterToggle(idx, checked)` → 更新 `selectedChapters`
- **章节文字点击** → `scrollToChapter(idx)` → 仅跳转，不改勾选

---

## 文件清单

| 文件 | 说明 |
|------|------|
| `index.html` | 主应用（持续开发中） |
| `index-v2.8.html` | v2.8 版本快照 |
| `epub_reader.py` | FastAPI 后端 |
| `start.command` | 启动脚本 |
