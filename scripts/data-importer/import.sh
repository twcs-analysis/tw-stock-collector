#!/bin/bash
################################################################################
# 台股資料匯入工具 - 統一入口腳本
#
# 用法:
#   ./import.sh <類型> <日期選項> [其他參數]
#
# 範例:
#   # 匯入單日 price 資料
#   ./import.sh price --date 2026-02-03
#
#   # 匯入區間 technical 資料
#   ./import.sh technical --start 2026-01-01 --end 2026-01-31
#
#   # 匯入多種類型
#   ./import.sh price,institutional --date 2026-02-03
################################################################################

set -e  # 遇到錯誤立即退出

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 腳本目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 顯示使用說明
show_usage() {
    cat << EOF
${BLUE}台股資料匯入工具${NC}

${YELLOW}用法:${NC}
  $0 <資料類型> <日期選項> [其他參數]

${YELLOW}資料類型:${NC}
  price                單一資料類型
  institutional
  margin
  lending
  top20_volume
  revenue             月營收資料
  technical           技術分析指標

  price,institutional  多個類型（逗號分隔）
  all                  所有類型（不含 technical）

${YELLOW}日期選項:${NC}
  --date YYYY-MM-DD              匯入單一日期
  --start YYYY-MM-DD --end ...   匯入日期區間

${YELLOW}其他參數:${NC}
  --db-password PASSWORD         資料庫密碼
  --data-dir PATH               資料目錄（僅 technical 使用）
  --data-root PATH              原始資料根目錄（其他類型使用）
  --log-level LEVEL             日誌等級 (DEBUG/INFO/WARNING/ERROR)
  -h, --help                    顯示此說明

${YELLOW}範例:${NC}
  # 匯入單日價格資料
  $0 price --date 2026-02-03

  # 匯入區間技術分析資料
  $0 technical --start 2026-01-01 --end 2026-01-31

  # 匯入多種類型（單日）
  $0 price,institutional,margin --date 2026-02-03

  # 匯入所有原始資料類型
  $0 all --date 2026-02-03

  # 使用環境變數設定密碼
  export DB_PASSWORD=your_password
  $0 price --date 2026-02-03

${YELLOW}環境變數:${NC}
  DB_PASSWORD    資料庫密碼（推薦使用此方式）
  DB_HOST        資料庫主機（預設: localhost）
  DB_PORT        資料庫埠號（預設: 5432）
  DB_NAME        資料庫名稱（預設: tw_stock）
  DB_USER        資料庫使用者（預設: postgres）

EOF
}

# 錯誤訊息
error() {
    echo -e "${RED}錯誤: $1${NC}" >&2
    exit 1
}

# 資訊訊息
info() {
    echo -e "${GREEN}$1${NC}"
}

# 警告訊息
warn() {
    echo -e "${YELLOW}$1${NC}"
}

# 檢查參數數量
if [ $# -lt 2 ]; then
    show_usage
    exit 1
fi

# 檢查 help 參數
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_usage
    exit 0
fi

# 解析資料類型
DATA_TYPE="$1"
shift

# 檢查是否為 technical 類型
IS_TECHNICAL=false
if [ "$DATA_TYPE" = "technical" ]; then
    IS_TECHNICAL=true
fi

# 檢查是否為 all 類型
if [ "$DATA_TYPE" = "all" ]; then
    DATA_TYPE="price,institutional,margin,lending,top20_volume,revenue"
    info "匯入所有原始資料類型: $DATA_TYPE"
fi

# 確保密碼已設定
if [ -z "$DB_PASSWORD" ]; then
    warn "警告: DB_PASSWORD 環境變數未設定"
    warn "您可以使用以下方式設定："
    warn "  export DB_PASSWORD=your_password"
    warn "或使用 --db-password 參數"
    echo
fi

# 執行對應的匯入腳本
cd "$PROJECT_ROOT"

if [ "$IS_TECHNICAL" = true ]; then
    # 技術分析資料匯入
    info "匯入技術分析資料..."
    python3.11 scripts/data-importer/import_technical_analysis.py "$@"

else
    # 原始資料匯入（price, institutional, margin, lending, top20_volume, revenue）
    info "匯入原始資料類型: $DATA_TYPE"

    # 將逗號分隔的類型轉換為空格分隔
    TYPES=$(echo "$DATA_TYPE" | tr ',' ' ')

    python3.11 scripts/data-importer/import_data.py --types $TYPES "$@"
fi

# 檢查執行結果
if [ $? -eq 0 ]; then
    echo
    info "✅ 匯入完成！"
else
    error "匯入失敗，請檢查錯誤訊息"
fi
