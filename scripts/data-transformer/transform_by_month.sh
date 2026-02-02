#!/bin/bash
#
# 按月份轉換技術指標資料
#
# 使用方式:
#   ./scripts/data-transformer/transform_by_month.sh 2025-01 2026-01
#   ./scripts/data-transformer/transform_by_month.sh 2025-01        # 只轉換單月
#

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;36m'
NC='\033[0m' # No Color

# 取得專案根目錄
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# 解析參數
START_MONTH="$1"
END_MONTH="${2:-$START_MONTH}"  # 如果沒有指定結束月份，則只轉換單月

if [ -z "$START_MONTH" ]; then
    echo -e "${RED}錯誤: 請指定起始月份 (YYYY-MM)${NC}"
    echo "使用方式: $0 <起始月份> [結束月份]"
    echo "範例:"
    echo "  $0 2025-01"
    echo "  $0 2025-01 2026-01"
    exit 1
fi

# 驗證日期格式
if ! [[ "$START_MONTH" =~ ^[0-9]{4}-[0-9]{2}$ ]]; then
    echo -e "${RED}錯誤: 日期格式錯誤 (應為 YYYY-MM)${NC}"
    exit 1
fi

if ! [[ "$END_MONTH" =~ ^[0-9]{4}-[0-9]{2}$ ]]; then
    echo -e "${RED}錯誤: 日期格式錯誤 (應為 YYYY-MM)${NC}"
    exit 1
fi

# 檢查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ 找不到 python3${NC}"
    exit 1
fi

# 設定資料庫密碼
if [ -z "$DB_PASSWORD" ]; then
    echo -e "${YELLOW}[WARNING]${NC} 未設定 DB_PASSWORD 環境變數，使用預設密碼"
    export DB_PASSWORD="tw_stock_dev_password_2024"
fi

echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}按月份轉換技術指標資料${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo -e "起始月份: ${START_MONTH}"
echo -e "結束月份: ${END_MONTH}"
echo -e "${BLUE}======================================================================${NC}"
echo ""

# 生成月份列表
generate_months() {
    local start="$1"
    local end="$2"

    python3 << EOF
from datetime import datetime
from dateutil.relativedelta import relativedelta

start = datetime.strptime('$start', '%Y-%m')
end = datetime.strptime('$end', '%Y-%m')

current = start
while current <= end:
    print(current.strftime('%Y-%m'))
    current += relativedelta(months=1)
EOF
}

# 取得月份的第一天和最後一天
get_month_range() {
    local month="$1"

    python3 << EOF
from datetime import datetime
from calendar import monthrange

month = datetime.strptime('$month', '%Y-%m')
year = month.year
month_num = month.month

# 第一天
first_day = f"{year:04d}-{month_num:02d}-01"

# 最後一天
last_day_num = monthrange(year, month_num)[1]
last_day = f"{year:04d}-{month_num:02d}-{last_day_num:02d}"

print(f"{first_day},{last_day}")
EOF
}

# 統計
total_months=0
success_months=0
failed_months=0

# 迭代每個月份
for month in $(generate_months "$START_MONTH" "$END_MONTH"); do
    total_months=$((total_months + 1))

    echo -e "${BLUE}[${month}]${NC} 開始轉換..."

    # 取得月份範圍
    month_range=$(get_month_range "$month")
    start_date=$(echo "$month_range" | cut -d',' -f1)
    end_date=$(echo "$month_range" | cut -d',' -f2)

    echo "  日期範圍: $start_date ~ $end_date"

    # 執行轉換（使用現有的 transform.sh 腳本）
    if "$PROJECT_ROOT/scripts/data-transformer/transform.sh" range "$start_date" "$end_date" > /dev/null 2>&1; then
        # 檢查輸出檔案
        output_file="$PROJECT_ROOT/data/transformed/technical/${start_date}_to_${end_date}.csv"

        if [ -f "$output_file" ]; then
            # 重新命名為月份格式
            month_file="$PROJECT_ROOT/data/transformed/technical/${month}.csv"
            mv "$output_file" "$month_file"

            # 統計記錄數
            record_count=$(tail -n +2 "$month_file" | wc -l | tr -d ' ')
            file_size=$(ls -lh "$month_file" | awk '{print $5}')

            echo -e "  ${GREEN}✓${NC} 轉換成功: $record_count 筆記錄, 檔案大小: $file_size"
            echo -e "  ${GREEN}✓${NC} 檔案: $month_file"
            success_months=$((success_months + 1))
        else
            echo -e "  ${YELLOW}⚠${NC}  找不到輸出檔案"
            failed_months=$((failed_months + 1))
        fi
    else
        echo -e "  ${RED}✗${NC} 轉換失敗"
        failed_months=$((failed_months + 1))
    fi

    echo ""
done

# 輸出總結
echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}轉換總結${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo -e "總月份數: ${total_months}"
echo -e "成功: ${GREEN}${success_months}${NC}"
echo -e "失敗: ${RED}${failed_months}${NC}"
echo -e "${BLUE}======================================================================${NC}"

# 回傳狀態碼
if [ $failed_months -eq 0 ]; then
    exit 0
else
    exit 1
fi
