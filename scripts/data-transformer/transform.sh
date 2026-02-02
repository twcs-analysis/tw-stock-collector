#!/bin/bash
#
# 技術分析轉換工具 - Shell 包裝腳本
#
# 功能：
#   - 提供簡化的命令介面
#   - 自動設定環境變數
#   - 支援常用轉換場景
#
# 使用方式：
#   ./scripts/data-transformer/transform.sh today              # 轉換今天的資料
#   ./scripts/data-transformer/transform.sh 2026-02-02         # 轉換指定日期
#   ./scripts/data-transformer/transform.sh 2026-02-02 2330    # 轉換指定股票
#   ./scripts/data-transformer/transform.sh range 2026-01-01 2026-01-31  # 轉換區間
#

set -e  # 遇到錯誤立即退出

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 取得腳本所在目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Python 腳本路徑
PYTHON_SCRIPT="$SCRIPT_DIR/run_technical_analysis.py"

# 輸出目錄
OUTPUT_DIR="$PROJECT_ROOT/data/transformed/technical"

# 日誌函式
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 顯示使用說明
show_usage() {
    cat << EOF
技術分析轉換工具 - Shell 包裝腳本

使用方式:
  $0 <command> [options]

命令:
  today                     轉換今天的資料
  yesterday                 轉換昨天的資料
  <YYYY-MM-DD>             轉換指定日期
  <YYYY-MM-DD> <股票代碼>   轉換指定日期的特定股票
  range <開始日> <結束日>    轉換日期區間
  latest <天數>             轉換最近 N 天的資料

範例:
  # 轉換今天的資料
  $0 today

  # 轉換 2026-02-02 的資料
  $0 2026-02-02

  # 轉換台積電 (2330) 在 2026-02-02 的資料
  $0 2026-02-02 2330

  # 轉換 2026 年 1 月的資料
  $0 range 2026-01-01 2026-01-31

  # 轉換最近 7 天的資料
  $0 latest 7

環境變數:
  DB_HOST      資料庫主機 (預設: localhost)
  DB_PORT      資料庫埠號 (預設: 5432)
  DB_NAME      資料庫名稱 (預設: tw_stock)
  DB_USER      資料庫使用者 (預設: postgres)
  DB_PASSWORD  資料庫密碼 (必要)

選項:
  --output <路徑>    輸出檔案路徑
  --no-save          不儲存到檔案，僅顯示結果
  --verbose          顯示詳細日誌
  -h, --help         顯示此說明

EOF
}

# 檢查 Python 是否可用
check_python() {
    if ! command -v python3 &> /dev/null; then
        log_error "找不到 python3，請先安裝 Python 3"
        exit 1
    fi
}

# 檢查資料庫密碼
check_db_password() {
    if [ -z "$DB_PASSWORD" ]; then
        log_error "請設定 DB_PASSWORD 環境變數"
        echo ""
        echo "範例："
        echo "  export DB_PASSWORD=your_password"
        echo "  $0 today"
        exit 1
    fi
}

# 取得今天的日期
get_today() {
    date +%Y-%m-%d
}

# 取得昨天的日期
get_yesterday() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        date -v-1d +%Y-%m-%d
    else
        # Linux
        date -d "yesterday" +%Y-%m-%d
    fi
}

# 取得 N 天前的日期
get_date_days_ago() {
    local days=$1
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        date -v-${days}d +%Y-%m-%d
    else
        # Linux
        date -d "$days days ago" +%Y-%m-%d
    fi
}

# 驗證日期格式
validate_date() {
    local date=$1
    if ! [[ $date =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
        log_error "日期格式錯誤: $date (應為 YYYY-MM-DD)"
        exit 1
    fi
}

# 建立輸出目錄
ensure_output_dir() {
    if [ ! -d "$OUTPUT_DIR" ]; then
        log_info "建立輸出目錄: $OUTPUT_DIR"
        mkdir -p "$OUTPUT_DIR"
    fi
}

# 轉換單日資料
transform_single_date() {
    local date=$1
    local stock_id=$2
    local output_path=$3
    local verbose=$4

    validate_date "$date"

    local args="--date $date"

    if [ -n "$stock_id" ]; then
        args="$args --stock-id $stock_id"
    fi

    if [ -n "$output_path" ]; then
        args="$args --output $output_path"
    elif [ "$NO_SAVE" != "true" ]; then
        # 自動產生輸出檔名
        ensure_output_dir
        if [ -n "$stock_id" ]; then
            output_path="$OUTPUT_DIR/${date}_${stock_id}.csv"
        else
            output_path="$OUTPUT_DIR/${date}_all.csv"
        fi
        args="$args --output $output_path"
    fi

    if [ "$verbose" = "true" ]; then
        args="$args --verbose"
    fi

    log_info "執行轉換: $date $([ -n "$stock_id" ] && echo "股票 $stock_id")"
    python3 "$PYTHON_SCRIPT" $args
}

# 轉換日期區間
transform_date_range() {
    local start_date=$1
    local end_date=$2
    local output_path=$3
    local verbose=$4

    validate_date "$start_date"
    validate_date "$end_date"

    local args="--start $start_date --end $end_date"

    if [ -n "$output_path" ]; then
        args="$args --output $output_path"
    elif [ "$NO_SAVE" != "true" ]; then
        # 自動產生輸出檔名
        ensure_output_dir
        output_path="$OUTPUT_DIR/${start_date}_to_${end_date}.csv"
        args="$args --output $output_path"
    fi

    if [ "$verbose" = "true" ]; then
        args="$args --verbose"
    fi

    log_info "執行區間轉換: $start_date 到 $end_date"
    python3 "$PYTHON_SCRIPT" $args
}

# 轉換最近 N 天
transform_latest() {
    local days=$1
    local verbose=$2

    if ! [[ $days =~ ^[0-9]+$ ]]; then
        log_error "天數必須為正整數"
        exit 1
    fi

    local end_date=$(get_today)
    local start_date=$(get_date_days_ago $days)

    log_info "轉換最近 $days 天的資料 ($start_date 到 $end_date)"
    transform_date_range "$start_date" "$end_date" "" "$verbose"
}

# 主程式
main() {
    # 檢查 Python
    check_python

    # 檢查參數
    if [ $# -eq 0 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        show_usage
        exit 0
    fi

    # 檢查資料庫密碼
    check_db_password

    # 解析選項
    OUTPUT_PATH=""
    NO_SAVE="false"
    VERBOSE="false"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --output)
                OUTPUT_PATH="$2"
                shift 2
                ;;
            --no-save)
                NO_SAVE="true"
                shift
                ;;
            --verbose)
                VERBOSE="true"
                shift
                ;;
            *)
                break
                ;;
        esac
    done

    # 解析命令
    local command=$1
    shift

    case "$command" in
        today)
            local date=$(get_today)
            transform_single_date "$date" "${1:-}" "$OUTPUT_PATH" "$VERBOSE"
            ;;
        yesterday)
            local date=$(get_yesterday)
            transform_single_date "$date" "${1:-}" "$OUTPUT_PATH" "$VERBOSE"
            ;;
        range)
            if [ $# -lt 2 ]; then
                log_error "range 命令需要提供開始日期和結束日期"
                show_usage
                exit 1
            fi
            transform_date_range "$1" "$2" "$OUTPUT_PATH" "$VERBOSE"
            ;;
        latest)
            if [ $# -lt 1 ]; then
                log_error "latest 命令需要提供天數"
                show_usage
                exit 1
            fi
            transform_latest "$1" "$VERBOSE"
            ;;
        [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9])
            # 日期格式
            transform_single_date "$command" "${1:-}" "$OUTPUT_PATH" "$VERBOSE"
            ;;
        *)
            log_error "未知的命令: $command"
            show_usage
            exit 1
            ;;
    esac

    log_success "轉換完成"
}

# 執行主程式
main "$@"
