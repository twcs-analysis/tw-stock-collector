#!/bin/bash
#
# Revenue Pipeline 獨立執行腳本
#
# 功能：
#   - 直接執行月營收資料處理流程（不透過 Claude CLI）
#   - 1. 檢查 monthly 完整資料
#   - 2. 收集目標月營收資料（智慧模式）
#   - 3. 匯入資料庫
#   - 4. 展示最新月份營收資料
#
# 使用方式：
#   ./execute.sh [--year-month YYYY-MM] [--sample N] [--dry-run]
#

set -e

# 取得腳本所在目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 切換到專案根目錄
cd "$PROJECT_ROOT"

# 解析參數
YEAR_MONTH=""
SAMPLE=8
DRY_RUN=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --year-month)
            YEAR_MONTH="$2"
            shift 2
            ;;
        --sample)
            SAMPLE="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN="--dry-run"
            shift
            ;;
        *)
            echo "未知參數: $1"
            exit 1
            ;;
    esac
done

# 設定環境變數
export DB_PASSWORD="${DB_PASSWORD:-tw_stock_dev_password_2024}"

echo "============================================================"
echo "Revenue Pipeline 執行開始"
echo "============================================================"
echo "時間: $(date '+%Y-%m-%d %H:%M:%S')"
echo "專案: $PROJECT_ROOT"
echo "參數: year-month=$YEAR_MONTH, sample=$SAMPLE, dry-run=$DRY_RUN"
echo ""

# ============================================================
# Step 1: 確認 PostgreSQL 啟動
# ============================================================
echo "[Step 1] 確認 PostgreSQL 狀態..."
if brew services list | grep -q "postgresql@17.*started"; then
    echo "✓ PostgreSQL 已啟動"
else
    echo "⚠️  PostgreSQL 未啟動，正在啟動..."
    brew services start postgresql@17
    sleep 3
    echo "✓ PostgreSQL 已啟動"
fi
echo ""

# ============================================================
# Step 2: 檢查 monthly 完整資料（選擇性保存）
# ============================================================
echo "[Step 2] 檢查 monthly 完整資料..."

# 嘗試收集 monthly 資料（允許失敗）
set +e
MONTHLY_OUTPUT=$(python3.11 scripts/data-collector/collect_revenue.py --mode monthly 2>&1)
MONTHLY_EXIT_CODE=$?
set -e

echo "$MONTHLY_OUTPUT"

# 檢查執行結果
if [ $MONTHLY_EXIT_CODE -eq 0 ]; then
    # 解析 API 返回的年月
    API_YEAR_MONTH=$(echo "$MONTHLY_OUTPUT" | grep -oE "實際年月: [0-9]{4}-[0-9]{2}" | head -1 | cut -d' ' -f2 || echo "")

    if [ -n "$API_YEAR_MONTH" ]; then
        YEAR=$(echo "$API_YEAR_MONTH" | cut -d'-' -f1)
        TARGET_FILE="data/raw/revenue-monthly/$YEAR/$API_YEAR_MONTH.json"

        if [ -f "$TARGET_FILE" ]; then
            # 比對本地檔案的年月
            LOCAL_YEAR_MONTH=$(cat "$TARGET_FILE" | jq -r '.metadata.year_month' 2>/dev/null || echo "")

            if [ "$LOCAL_YEAR_MONTH" == "$API_YEAR_MONTH" ]; then
                echo "⚠️  本地已有相同年月 ($API_YEAR_MONTH) 的資料，跳過保存"
            else
                echo "✓ 發現新的年月資料 ($API_YEAR_MONTH)，已保存"
            fi
        else
            echo "✓ 本地無此年月資料 ($API_YEAR_MONTH)，已保存"
        fi
    else
        echo "⚠️  無法解析 API 返回的年月，跳過此步驟"
    fi
else
    echo "⚠️  Step 2 執行失敗（可能是網路問題或 API 暫時不可用），繼續執行後續步驟"
fi
echo ""

# ============================================================
# Step 3: 收集目標月營收資料（智慧模式）
# ============================================================
echo "[Step 3] 收集目標月營收資料..."

COLLECT_CMD="python3.11 scripts/data-collector/collect_revenue.py"
[ -n "$YEAR_MONTH" ] && COLLECT_CMD="$COLLECT_CMD --year-month $YEAR_MONTH"
[ -n "$DRY_RUN" ] && COLLECT_CMD="$COLLECT_CMD $DRY_RUN"

echo "執行指令: $COLLECT_CMD"
COLLECT_OUTPUT=$($COLLECT_CMD 2>&1)
echo "$COLLECT_OUTPUT"

# 解析收集結果
COLLECTED_YEAR_MONTH=$(echo "$COLLECT_OUTPUT" | grep -oE "年月: [0-9]{4}-[0-9]{2}" | head -1 | cut -d' ' -f2 || echo "")
TOTAL_COUNT=$(echo "$COLLECT_OUTPUT" | grep -oE "總計: [0-9,]+" | head -1 | cut -d' ' -f2 | tr -d ',' || echo "0")
COLLECT_MODE=$(echo "$COLLECT_OUTPUT" | grep -oE "模式: (daily|monthly)" | head -1 | cut -d' ' -f2 || echo "unknown")

echo ""
echo "收集完成："
echo "  年月: $COLLECTED_YEAR_MONTH"
echo "  總計: $TOTAL_COUNT 檔"
echo "  模式: $COLLECT_MODE"
echo ""

# ============================================================
# Step 4: 匯入資料庫（如果非 dry-run）
# ============================================================
if [ -z "$DRY_RUN" ]; then
    echo "[Step 4] 匯入資料庫..."

    if [ -n "$COLLECTED_YEAR_MONTH" ]; then
        # 計算匯入日期（使用該月的 15 號）
        IMPORT_DATE="$COLLECTED_YEAR_MONTH-15"

        echo "執行指令: scripts/data-importer/import.sh revenue --date $IMPORT_DATE"
        scripts/data-importer/import.sh revenue --date "$IMPORT_DATE"

        echo "✓ 資料庫匯入完成"
    else
        echo "⚠️  無法取得收集的年月，跳過匯入"
    fi
    echo ""
else
    echo "[Step 4] Dry-run 模式，跳過資料庫匯入"
    echo ""
fi

# ============================================================
# Step 5: 展示最新月份營收資料
# ============================================================
echo "[Step 5] 展示最新月份營收資料..."

DISPLAY_SQL="
WITH latest_month AS (
    SELECT MAX(year_month) as max_year_month
    FROM stock_revenues
)
SELECT
    sr.stock_id,
    s.stock_name,
    s.market_type,
    sr.current_month_revenue,
    sr.last_month_revenue,
    sr.last_year_revenue,
    sr.mom_change_pct,
    sr.yoy_change_pct,
    sr.ytd_revenue,
    sr.ytd_yoy_change_pct,
    sr.year_month,
    sr.note,
    sr.collection_date
FROM stock_revenues sr
JOIN stocks s ON sr.stock_id = s.stock_id
WHERE sr.year_month = (SELECT max_year_month FROM latest_month)
ORDER BY RANDOM()
LIMIT $SAMPLE;
"

# 執行查詢
QUERY_RESULT=$(psql-17 -h localhost -U postgres -d tw_stock -t -A -F'|' -c "$DISPLAY_SQL" 2>/dev/null || echo "")

if [ -n "$QUERY_RESULT" ]; then
    # 取得最新年月
    LATEST_YEAR_MONTH=$(psql-17 -h localhost -U postgres -d tw_stock -t -A -c "SELECT MAX(year_month) FROM stock_revenues;" 2>/dev/null || echo "")

    echo ""
    echo "最新月份營收資料 ($LATEST_YEAR_MONTH) - 隨機展示 $SAMPLE 檔"
    echo "================================================================================"
    echo ""
    printf "| %-6s | %-8s | %-4s | %-12s | %-8s | %-9s | %-11s | %-9s |\n" \
        "代碼" "名稱" "市場" "當月營收(億)" "月增率" "年增率" "YTD營收(億)" "YTD年增率"
    echo "|--------|----------|------|--------------|----------|-----------|-------------|-----------|"

    # 處理查詢結果
    echo "$QUERY_RESULT" | while IFS='|' read -r stock_id stock_name market_type \
        current_revenue last_month_revenue last_year_revenue \
        mom_pct yoy_pct ytd_revenue ytd_yoy_pct \
        year_month note collection_date; do

        # 單位轉換：千元 → 億元 (除以 100,000)
        current_billion=$(echo "scale=0; $current_revenue / 100000" | bc)
        ytd_billion=$(echo "scale=0; $ytd_revenue / 100000" | bc)

        # 格式化百分比
        mom_formatted=$(printf "%+.2f%%" "$mom_pct")
        yoy_formatted=$(printf "%+.2f%%" "$yoy_pct")
        ytd_yoy_formatted=$(printf "%+.2f%%" "$ytd_yoy_pct")

        # 市場類型轉換
        market_display="上市"
        [ "$market_type" == "OTC" ] && market_display="上櫃"

        printf "| %-6s | %-8s | %-4s | %12s | %8s | %9s | %11s | %9s |\n" \
            "$stock_id" "$stock_name" "$market_display" \
            "$current_billion" "$mom_formatted" "$yoy_formatted" \
            "$ytd_billion" "$ytd_yoy_formatted"
    done

    echo ""
    echo "================================================================================"
    echo ""
    echo "詳細資料（前 3 檔）："
    echo ""

    # 顯示詳細資料（前 3 檔）
    echo "$QUERY_RESULT" | head -3 | awk -F'|' '{
        printf "\n[%d] %s %s (%s)\n", NR, $1, $2, ($3 == "TWSE" ? "上市" : "上櫃")
        printf "    當月營收: %s 千元 (%.0f 億)\n", $4, $4/100000
        printf "    上月營收: %s 千元 (%.0f 億) | 月增率: %+.2f%%\n", $5, $5/100000, $7
        printf "    去年同期: %s 千元 (%.0f 億) | 年增率: %+.2f%%\n", $6, $6/100000, $8
        printf "    年初至今: %s 千元 (%.0f 億) | YTD年增率: %+.2f%%\n", $9, $9/100000, $10
        printf "    收集日期: %s | 備註: %s\n", $13, ($12 == "" ? "-" : $12)
    }'

    echo ""
    echo "================================================================================"
else
    echo "⚠️  無法從資料庫查詢資料"
fi

echo ""
echo "============================================================"
echo "Revenue Pipeline 執行完成"
echo "============================================================"
echo "結束時間: $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"
