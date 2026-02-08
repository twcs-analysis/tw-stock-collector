#!/bin/bash
# ============================================================================
# 封關選股執行腳本
# ============================================================================

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 取得腳本所在目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "============================================================"
echo "封關選股：年線附近安全選股策略"
echo "============================================================"
echo "策略來源：錢線百分百技術面分析建議"
echo "核心理念：買在年線，睡得安穩"
echo ""

# 檢查資料庫密碼
if [ -z "$DB_PASSWORD" ]; then
    echo -e "${YELLOW}⚠️  未設定 DB_PASSWORD 環境變數${NC}"
    echo "請輸入資料庫密碼："
    read -s DB_PASSWORD
    export PGPASSWORD="$DB_PASSWORD"
else
    export PGPASSWORD="$DB_PASSWORD"
fi

# 資料庫連線資訊
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="tw_stock"
DB_USER="postgres"

# 檢查資料庫連線
echo -e "${BLUE}[1/3] 檢查資料庫連線...${NC}"
if psql-17 -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 資料庫連線成功${NC}"
else
    echo -e "${RED}✗ 資料庫連線失敗${NC}"
    echo "請檢查："
    echo "  - PostgreSQL 是否啟動"
    echo "  - 資料庫密碼是否正確"
    echo "  - 資料庫名稱是否為 tw_stock"
    exit 1
fi

# 檢查技術指標資料
echo -e "${BLUE}[2/3] 檢查技術指標資料...${NC}"
LATEST_DATE=$(psql-17 -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
    -t -c "SELECT MAX(trade_date) FROM stock_analysis_daily" 2>/dev/null | tr -d ' ')

if [ -z "$LATEST_DATE" ] || [ "$LATEST_DATE" = "" ]; then
    echo -e "${RED}✗ 找不到技術指標資料${NC}"
    echo "請先執行技術指標轉換："
    echo "  export DB_PASSWORD=your_password"
    echo "  scripts/data-transformer/transform.sh today"
    exit 1
fi

echo -e "${GREEN}✓ 最新資料日期：$LATEST_DATE${NC}"

# 執行 SQL 查詢
echo -e "${BLUE}[3/3] 執行選股查詢...${NC}"

# 建立輸出目錄（按日期分層）
# 目錄結構: analysis/reports/封關選股/YYYY-MM-DD/
REPORT_BASE_DIR="$PROJECT_ROOT/analysis/reports/封關選股"
REPORT_DATE_DIR="$REPORT_BASE_DIR/$LATEST_DATE"
mkdir -p "$REPORT_DATE_DIR"

# 輸出檔案名稱
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_TXT="$REPORT_DATE_DIR/年線選股_${LATEST_DATE}_${TIMESTAMP}.txt"
OUTPUT_CSV="$REPORT_DATE_DIR/年線選股_${LATEST_DATE}_${TIMESTAMP}.csv"

# 執行查詢（文字格式）
echo "  執行 SQL 查詢..."
psql-17 -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
    -f "$SCRIPT_DIR/年線附近選股.sql" > "$OUTPUT_TXT" 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 查詢完成${NC}"

    # 顯示結果摘要
    RESULT_COUNT=$(grep -c "^[[:space:]]*[0-9]\{4\}" "$OUTPUT_TXT" || echo "0")
    echo ""
    echo "============================================================"
    echo "查詢結果摘要"
    echo "============================================================"
    echo "資料日期：$LATEST_DATE"
    echo "符合條件股票數：$RESULT_COUNT 檔"
    echo ""
    echo "輸出檔案："
    echo "  - 文字檔：$OUTPUT_TXT"
    echo ""

    # 顯示前 10 筆結果
    echo "============================================================"
    echo "前 10 檔推薦股票（依安全評分排序）"
    echo "============================================================"
    head -20 "$OUTPUT_TXT" | tail -15
    echo ""

    # 產生 CSV 格式（重新執行查詢）
    echo -e "${BLUE}產生 CSV 格式...${NC}"
    psql-17 -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        -f "$SCRIPT_DIR/年線附近選股.sql" \
        --csv > "$OUTPUT_CSV" 2>&1

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ CSV 已產生：$OUTPUT_CSV${NC}"
    fi

    echo ""
    echo "============================================================"
    echo "✅ 封關選股完成！"
    echo "============================================================"
    echo ""
    echo "📊 操作建議："
    echo "  1. 優先選擇「安全評分」> 70 分的股票"
    echo "  2. 注意「操作建議」欄位的提示"
    echo "  3. 嚴格執行停損（跌破年線 3%）"
    echo "  4. 單一個股 < 15% 總資金"
    echo "  5. 保留至少 20% 現金"
    echo ""
    echo "📋 下一步："
    echo "  - 查看完整結果：cat \"$OUTPUT_TXT\""
    echo "  - 開啟 CSV：open \"$OUTPUT_CSV\""
    echo "  - 查看策略說明：cat \"$SCRIPT_DIR/README.md\""
    echo ""

else
    echo -e "${RED}✗ 查詢失敗${NC}"
    echo "錯誤訊息："
    cat "$OUTPUT_TXT"
    exit 1
fi
