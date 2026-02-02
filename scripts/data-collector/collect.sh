#!/bin/bash
#
# 單日資料收集腳本
#
# 功能：
#   - 收集指定日期的台股資料
#   - 支援指定資料類型
#   - 自動判斷交易日
#
# 使用方式：
#   ./scripts/data-collector/collect.sh                           # 收集當天所有資料
#   ./scripts/data-collector/collect.sh 2026-02-02                # 收集指定日期所有資料
#   ./scripts/data-collector/collect.sh 2026-02-02 price margin   # 收集指定類型
#

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 取得專案根目錄
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

# 解析參數
DATE_ARG=""
TYPES_ARG=""

if [ $# -ge 1 ]; then
    # 第一個參數是日期
    if [[ $1 =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
        DATE_ARG="--date $1"
        shift
    fi
fi

# 剩餘參數是資料類型
if [ $# -ge 1 ]; then
    TYPES_ARG="--types"
    for type in "$@"; do
        TYPES_ARG="$TYPES_ARG $type"
    done
fi

echo -e "${CYAN}======================================================================${NC}"
echo -e "${CYAN}台股資料收集${NC}"
echo -e "${CYAN}======================================================================${NC}"
echo ""

# 檢查 Python 環境
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ 找不到 python3${NC}"
    exit 1
fi

echo -e "${BLUE}[INFO]${NC} 執行資料收集..."
echo ""

# 優先使用 services/data-collector 版本，否則使用 scripts 版本
if [ -f "$PROJECT_ROOT/services/data-collector/app/main.py" ]; then
    python3 "$PROJECT_ROOT/services/data-collector/app/main.py" $DATE_ARG $TYPES_ARG
else
    python3 "$PROJECT_ROOT/scripts/run_collection.py" $DATE_ARG $TYPES_ARG
fi

RESULT=$?

echo ""
if [ $RESULT -eq 0 ]; then
    echo -e "${GREEN}======================================================================${NC}"
    echo -e "${GREEN}✓ 資料收集完成${NC}"
    echo -e "${GREEN}======================================================================${NC}"
    echo ""
    echo -e "${YELLOW}下一步：${NC}"
    echo "  1. 匯入資料庫: ./scripts/data-importer/import_date_range.sh <開始日期> <結束日期>"
    echo "  2. 轉換技術指標: ./scripts/data-transformer/transform.sh <日期>"
else
    echo -e "${RED}======================================================================${NC}"
    echo -e "${RED}✗ 資料收集失敗${NC}"
    echo -e "${RED}======================================================================${NC}"
    exit 1
fi
