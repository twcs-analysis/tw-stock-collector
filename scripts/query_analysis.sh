#!/bin/bash

# 股票技術分析查詢工具 - Shell 包裝腳本
#
# 用法:
#   ./scripts/query_analysis.sh 2330
#   ./scripts/query_analysis.sh 2330 2539 --simple
#   ./scripts/query_analysis.sh 2330 --date 2026-02-03

# 設定顏色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
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

# 檢查參數
if [ $# -eq 0 ]; then
    echo -e "${YELLOW}用法: $0 <股票代號> [選項]${NC}"
    echo ""
    echo "選項:"
    echo "  --date DATE         指定日期 (YYYY-MM-DD)"
    echo "  --source {db,csv}   資料來源 (預設: db)"
    echo "  --simple            簡化輸出"
    echo ""
    echo "範例:"
    echo "  $0 2330"
    echo "  $0 2330 2539 --simple"
    echo "  $0 2330 --date 2026-02-03"
    echo "  $0 2330 --source csv"
    exit 1
fi

# 執行 Python 腳本
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}股票技術分析查詢工具${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

python scripts/query_stock_analysis.py "$@"

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ 查詢完成！${NC}"
else
    echo ""
    echo -e "${RED}✗ 查詢失敗 (退出碼: $exit_code)${NC}"
fi

exit $exit_code
