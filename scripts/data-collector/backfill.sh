#!/bin/bash
#
# 歷史資料回補腳本
#
# 功能：
#   - 回補指定日期區間的歷史資料
#   - 自動收集 → 匯入資料庫 → 轉換技術指標
#   - 支援指定資料類型
#
# 使用方式：
#   ./scripts/data-collector/backfill.sh 2026-01-01 2026-01-31
#   ./scripts/data-collector/backfill.sh 2026-01-01 2026-01-31 price institutional
#   ./scripts/data-collector/backfill.sh 2026-01-01 2026-01-31 --skip-transform
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

# 檢查參數
if [ $# -lt 2 ]; then
    echo -e "${YELLOW}用法: $0 <開始日期> <結束日期> [資料類型...] [--skip-transform]${NC}"
    echo ""
    echo "範例:"
    echo "  $0 2026-01-01 2026-01-31                    # 回補 1 月所有類型"
    echo "  $0 2026-01-01 2026-01-31 price              # 只回補 price"
    echo "  $0 2026-01-01 2026-01-31 price institutional # 回補多種類型"
    echo "  $0 2026-01-01 2026-01-31 --skip-transform   # 跳過技術指標轉換"
    echo ""
    echo "支援的資料類型: price, institutional, margin, lending, top20_volume"
    exit 1
fi

START_DATE=$1
END_DATE=$2
shift 2

# 解析參數
TYPES=""
SKIP_TRANSFORM=false

for arg in "$@"; do
    if [ "$arg" = "--skip-transform" ]; then
        SKIP_TRANSFORM=true
    else
        TYPES="$TYPES $arg"
    fi
done

# 檢查日期格式
if ! [[ $START_DATE =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    echo -e "${RED}✗ 開始日期格式錯誤，請使用 YYYY-MM-DD 格式${NC}"
    exit 1
fi

if ! [[ $END_DATE =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    echo -e "${RED}✗ 結束日期格式錯誤，請使用 YYYY-MM-DD 格式${NC}"
    exit 1
fi

echo -e "${CYAN}======================================================================${NC}"
echo -e "${CYAN}歷史資料回補${NC}"
echo -e "${CYAN}======================================================================${NC}"
echo ""
echo "開始日期: $START_DATE"
echo "結束日期: $END_DATE"
if [ -n "$TYPES" ]; then
    echo "資料類型: $TYPES"
else
    echo "資料類型: 全部"
fi
echo "技術指標: $([ "$SKIP_TRANSFORM" = true ] && echo "跳過" || echo "轉換")"
echo ""

# ============================================================
# Step 1: 收集原始資料
# ============================================================
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Step 1/3: 收集原始資料${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

TYPES_ARG=""
if [ -n "$TYPES" ]; then
    TYPES_ARG="--types$TYPES"
fi

python3 "$PROJECT_ROOT/scripts/backfill.py" \
    --start "$START_DATE" \
    --end "$END_DATE" \
    $TYPES_ARG

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ 原始資料收集失敗${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✓ 原始資料收集完成${NC}"
echo ""

# ============================================================
# Step 2: 匯入資料庫
# ============================================================
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Step 2/3: 匯入資料到資料庫${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

"$PROJECT_ROOT/scripts/data-importer/import_date_range.sh" \
    "$START_DATE" \
    "$END_DATE" \
    $TYPES

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ 資料匯入失敗${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✓ 資料匯入完成${NC}"
echo ""

# ============================================================
# Step 3: 轉換技術指標
# ============================================================
if [ "$SKIP_TRANSFORM" = false ]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Step 3/3: 轉換技術指標${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""

    "$PROJECT_ROOT/scripts/data-transformer/transform.sh" \
        range \
        "$START_DATE" \
        "$END_DATE"

    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ 技術指標轉換失敗${NC}"
        exit 1
    fi

    echo ""
    echo -e "${GREEN}✓ 技術指標轉換完成${NC}"
    echo ""
else
    echo -e "${YELLOW}⊘ 跳過技術指標轉換${NC}"
    echo ""
fi

# ============================================================
# 完成
# ============================================================
echo -e "${GREEN}======================================================================${NC}"
echo -e "${GREEN}✓ 歷史資料回補完成${NC}"
echo -e "${GREEN}======================================================================${NC}"
echo ""
echo -e "${CYAN}回補摘要:${NC}"
echo "  日期範圍: $START_DATE ~ $END_DATE"
if [ -n "$TYPES" ]; then
    echo "  資料類型: $TYPES"
else
    echo "  資料類型: 全部"
fi
echo "  ✓ 原始資料已收集到 data/raw/"
echo "  ✓ 資料已匯入 PostgreSQL"
if [ "$SKIP_TRANSFORM" = false ]; then
    echo "  ✓ 技術指標已轉換到 data/transformed/technical/"
fi
echo ""
echo -e "${YELLOW}查看結果:${NC}"
echo "  資料庫狀態: ./scripts/database/check_status.sh"
echo "  技術指標: ls -lh data/transformed/technical/"
