#!/bin/bash

# 影音轉文字腳本工具 - Shell 包裝器
#
# 使用方式：
#   ./video_to_transcript.sh <影音網址> [選項]
#
# 範例：
#   ./video_to_transcript.sh "https://www.youtube.com/watch?v=xxx"
#   ./video_to_transcript.sh "https://www.youtube.com/watch?v=xxx" --output "meeting_notes"
#   ./video_to_transcript.sh "https://www.youtube.com/watch?v=xxx" --model large

set -e  # 遇到錯誤時停止執行

# 取得腳本所在目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Python 腳本路徑
PYTHON_SCRIPT="$SCRIPT_DIR/video_to_transcript.py"

# 檢查 Python 腳本是否存在
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "❌ 找不到 Python 腳本: $PYTHON_SCRIPT"
    exit 1
fi

# 檢查是否提供網址參數
if [ $# -eq 0 ]; then
    echo "❌ 請提供影音網址"
    echo ""
    echo "使用方式："
    echo "  $0 <影音網址> [選項]"
    echo ""
    echo "範例："
    echo "  $0 \"https://www.youtube.com/watch?v=xxx\""
    echo "  $0 \"https://www.youtube.com/watch?v=xxx\" --output \"meeting_notes\""
    echo "  $0 \"https://www.youtube.com/watch?v=xxx\" --model large"
    echo ""
    exit 1
fi

# 執行 Python 腳本
cd "$PROJECT_ROOT"
python3.11 "$PYTHON_SCRIPT" "$@"
