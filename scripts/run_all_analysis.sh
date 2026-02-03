#!/bin/bash

# 執行所有分析腳本 - Shell 包裝
#
# 用法:
#   ./scripts/run_all_analysis.sh
#   ./scripts/run_all_analysis.sh 2026-02-03
#   ./scripts/run_all_analysis.sh 2026-02-03 custom/output/dir

# 設定顏色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 取得專案根目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 切換到專案根目錄
cd "$PROJECT_ROOT" || exit 1

# 檢查 Python 環境
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ 找不到虛擬環境 venv${NC}"
    echo "請先執行: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# 啟用虛擬環境
source venv/bin/activate

# 解析參數
DATE=$1
OUTPUT_DIR=$2

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}執行所有分析腳本${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 建立命令
CMD="python scripts/run_all_analysis.py"

if [ -n "$DATE" ]; then
    echo -e "${GREEN}指定日期: $DATE${NC}"
    CMD="$CMD --date $DATE"
else
    echo -e "${YELLOW}使用今天日期${NC}"
fi

if [ -n "$OUTPUT_DIR" ]; then
    echo -e "${GREEN}輸出目錄: $OUTPUT_DIR${NC}"
    CMD="$CMD --output $OUTPUT_DIR"
fi

echo ""
echo -e "${BLUE}執行命令: $CMD${NC}"
echo ""

# 執行
$CMD

exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}✓ 所有分析執行完成！${NC}"
else
    echo -e "${RED}✗ 執行過程中發生錯誤 (退出碼: $exit_code)${NC}"
fi

echo ""

exit $exit_code
