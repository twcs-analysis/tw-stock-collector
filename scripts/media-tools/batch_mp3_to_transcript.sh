#!/bin/bash

# 批次 MP3 轉逐字稿工具
# 使用 whisper-cpp 批次將 2026-* 目錄下的 mp3 檔案轉換為中文逐字稿

set -e

# 取得腳本所在目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函數：顯示使用說明
show_usage() {
    cat << EOF
使用方式:
    $0 <目錄路徑> [選項]

範例:
    # 基本使用（使用預設 base 模型）
    $0 /Users/jasonhuang/yt-video/yt-moneyline

    # 使用不同的 Whisper 模型
    $0 /Users/jasonhuang/yt-video/yt-moneyline --model small

    # 強制重新轉換（忽略已存在的逐字稿）
    $0 /Users/jasonhuang/yt-video/yt-moneyline --force

    # 組合選項
    $0 /Users/jasonhuang/yt-video/yt-moneyline --model small --force

可用的 Whisper 模型:
    - tiny: 最快，準確度較低
    - base: 平衡速度與準確度（預設）
    - small: 較慢，準確度較高
    - medium: 更慢，準確度更高
    - large: 最慢，最高準確度

選項:
    -m, --model <model>    指定 Whisper 模型（預設: base）
    -f, --force            強制重新轉換（忽略已存在的逐字稿）
    -h, --help             顯示此說明
EOF
}

# 檢查參數
if [ $# -eq 0 ]; then
    echo -e "${RED}錯誤: 請提供目錄路徑${NC}"
    echo ""
    show_usage
    exit 1
fi

# 處理 help 參數
if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
    show_usage
    exit 0
fi

# 檢查 Python 3.11
if ! command -v python3.11 &> /dev/null; then
    echo -e "${RED}❌ 找不到 python3.11${NC}"
    echo -e "${YELLOW}請先安裝 Python 3.11：brew install python@3.11${NC}"
    exit 1
fi

# 檢查 whisper-cli
if ! command -v whisper-cli &> /dev/null; then
    echo -e "${RED}❌ 找不到 whisper-cli${NC}"
    echo -e "${YELLOW}請先安裝 whisper-cpp：brew install whisper-cpp${NC}"
    exit 1
fi

# 執行 Python 腳本
echo -e "${BLUE}執行批次 MP3 轉逐字稿工具...${NC}"
echo ""

python3.11 "$SCRIPT_DIR/batch_mp3_to_transcript.py" "$@"

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ 執行完成${NC}"
else
    echo ""
    echo -e "${RED}❌ 執行失敗（錯誤碼: $exit_code）${NC}"
fi

exit $exit_code
