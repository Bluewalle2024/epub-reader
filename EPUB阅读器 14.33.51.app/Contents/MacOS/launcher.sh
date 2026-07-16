#!/bin/bash
# EPUB 阅读器启动脚本
# 等待已有服务器或启动新服务器

# 先检查服务器是否已经在运行
for i in $(seq 1 30); do
  if curl -s http://localhost:8765 > /dev/null 2>&1; then
    open http://localhost:8765
    exit 0
  fi
  sleep 0.5
done

# 启动服务器
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PARENT_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"

if [ -f "$PARENT_DIR/epub_reader.py" ]; then
  cd "$PARENT_DIR"
  python3 epub_reader.py &
  sleep 3
  open http://localhost:8765
elif [ -f "$HOME/Downloads/epub_reader.py" ]; then
  cd "$HOME/Downloads"
  python3 epub_reader.py &
  sleep 3
  open http://localhost:8765
else
  osascript -e 'display notification "找不到 epub_reader.py，请确认文件位置" with title "EPUB 阅读器"'
fi
