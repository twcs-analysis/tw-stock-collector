#!/bin/bash
# 快速匯入單一日期的資料腳本

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 檢查參數
if [ $# -eq 0 ]; then
    echo -e "${YELLOW}用法: $0 <日期> [資料類型...]${NC}"
    echo ""
    echo "範例:"
    echo "  $0 2026-01-02                    # 匯入所有類型"
    echo "  $0 2026-01-02 price              # 只匯入 price"
    echo "  $0 2026-01-02 price institutional # 匯入多種類型"
    echo ""
    echo "支援的資料類型: price, institutional, margin, lending, top20_volume"
    exit 1
fi

DATE=$1
shift  # 移除第一個參數（日期）
TYPES="$@"

# 檢查日期格式
if ! [[ $DATE =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    echo -e "${RED}✗ 日期格式錯誤，請使用 YYYY-MM-DD 格式${NC}"
    exit 1
fi

# 檢查資料庫密碼
if [ -z "$DB_PASSWORD" ]; then
    echo -e "${YELLOW}⚠ 未設定 DB_PASSWORD，使用預設密碼${NC}"
    export DB_PASSWORD=tw_stock_dev_password_2024
fi

# 檢查資料庫是否運行
if ! docker ps | grep -q tw-stock-postgres; then
    echo -e "${RED}✗ PostgreSQL 容器未運行${NC}"
    echo -e "${YELLOW}請先啟動資料庫:${NC}"
    echo "  cd deployment/database/postgresql"
    echo "  docker-compose up -d"
    exit 1
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}匯入資料到 PostgreSQL${NC}"
echo -e "${GREEN}========================================${NC}"
echo "日期: $DATE"
echo "類型: ${TYPES:-所有類型}"
echo ""

# 執行匯入
cd "$(dirname "$0")/../.."  # 回到專案根目錄

if [ -z "$TYPES" ]; then
    # 匯入所有類型
    DB_PASSWORD="$DB_PASSWORD" python scripts/data-importer/import_data.py --date "$DATE"
else
    # 匯入指定類型
    DB_PASSWORD="$DB_PASSWORD" python scripts/data-importer/import_data.py --date "$DATE" --types $TYPES
fi

RESULT=$?

if [ $RESULT -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ 匯入完成！${NC}"

    # 驗證資料
    echo ""
    echo -e "${GREEN}驗證匯入結果:${NC}"
    docker exec tw-stock-postgres psql -U postgres -d tw_stock -c \
        "SELECT
            '${DATE}' as date,
            COUNT(*) as total_records,
            COUNT(DISTINCT stock_id) as unique_stocks
         FROM stock_prices
         WHERE trade_date = '${DATE}';"
else
    echo ""
    echo -e "${RED}✗ 匯入失敗，請檢查錯誤訊息${NC}"
    exit 1
fi
