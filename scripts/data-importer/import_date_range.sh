#!/bin/bash
# 匯入日期區間的資料腳本

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 檢查參數
if [ $# -lt 2 ]; then
    echo -e "${YELLOW}用法: $0 <開始日期> <結束日期> [資料類型...]${NC}"
    echo ""
    echo "範例:"
    echo "  $0 2026-01-01 2026-01-31                    # 匯入 1 月所有類型"
    echo "  $0 2026-01-01 2026-01-31 price              # 只匯入 price"
    echo "  $0 2026-01-01 2026-01-31 price institutional # 匯入多種類型"
    echo ""
    echo "支援的資料類型: price, institutional, margin, lending, top20_volume"
    exit 1
fi

START_DATE=$1
END_DATE=$2
shift 2  # 移除前兩個參數
TYPES="$@"

# 檢查日期格式
if ! [[ $START_DATE =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    echo -e "${RED}✗ 開始日期格式錯誤，請使用 YYYY-MM-DD 格式${NC}"
    exit 1
fi

if ! [[ $END_DATE =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    echo -e "${RED}✗ 結束日期格式錯誤，請使用 YYYY-MM-DD 格式${NC}"
    exit 1
fi

# 檢查資料庫密碼
if [ -z "$DB_PASSWORD" ]; then
    echo -e "${YELLOW}⚠ 未設定 DB_PASSWORD，使用預設密碼${NC}"
    export DB_PASSWORD=tw_stock_dev_password_2024
fi

# 檢查資料庫是否運行（支援本地和 Docker）
if command -v psql &> /dev/null; then
    # 嘗試連線本地資料庫
    if PGPASSWORD="$DB_PASSWORD" psql -h localhost -U postgres -d tw_stock -c "SELECT 1" &> /dev/null; then
        echo -e "${GREEN}✓ 使用本地 PostgreSQL${NC}"
    else
        echo -e "${RED}✗ 無法連線到本地 PostgreSQL${NC}"
        exit 1
    fi
elif docker ps | grep -q tw-stock-postgres; then
    echo -e "${GREEN}✓ 使用 Docker PostgreSQL${NC}"
else
    echo -e "${RED}✗ PostgreSQL 未運行${NC}"
    echo -e "${YELLOW}請先啟動資料庫${NC}"
    exit 1
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}批次匯入資料到 PostgreSQL${NC}"
echo -e "${GREEN}========================================${NC}"
echo "開始日期: $START_DATE"
echo "結束日期: $END_DATE"
echo "類型: ${TYPES:-所有類型}"
echo ""

# 執行匯入
cd "$(dirname "$0")/../.."  # 回到專案根目錄

if [ -z "$TYPES" ]; then
    # 匯入所有類型
    DB_PASSWORD="$DB_PASSWORD" python scripts/data-importer/import_data.py \
        --start "$START_DATE" --end "$END_DATE"
else
    # 匯入指定類型
    DB_PASSWORD="$DB_PASSWORD" python scripts/data-importer/import_data.py \
        --start "$START_DATE" --end "$END_DATE" --types $TYPES
fi

RESULT=$?

if [ $RESULT -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ 批次匯入完成！${NC}"

    # 驗證資料
    echo ""
    echo -e "${GREEN}驗證匯入結果:${NC}"
    if command -v psql &> /dev/null; then
        PGPASSWORD="$DB_PASSWORD" psql -h localhost -U postgres -d tw_stock -c \
            "SELECT
                COUNT(DISTINCT trade_date) as total_dates,
                MIN(trade_date) as first_date,
                MAX(trade_date) as last_date,
                COUNT(*) as total_records
             FROM stock_prices
             WHERE trade_date BETWEEN '${START_DATE}' AND '${END_DATE}';"
    else
        docker exec tw-stock-postgres psql -U postgres -d tw_stock -c \
            "SELECT
                COUNT(DISTINCT trade_date) as total_dates,
                MIN(trade_date) as first_date,
                MAX(trade_date) as last_date,
                COUNT(*) as total_records
             FROM stock_prices
             WHERE trade_date BETWEEN '${START_DATE}' AND '${END_DATE}';"
    fi
else
    echo ""
    echo -e "${RED}✗ 匯入失敗，請檢查錯誤訊息${NC}"
    exit 1
fi
