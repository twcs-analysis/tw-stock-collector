#!/bin/bash
#
# 資料庫初始化腳本
#
# 功能：
#   - 建立所有資料表
#   - 建立索引和約束
#   - 驗證資料庫結構
#
# 使用方式：
#   ./scripts/database/init_database.sh
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
資料庫初始化腳本

使用方式:
  $0 [選項]

選項:
  --drop-existing    刪除現有資料表（謹慎使用！）
  -h, --help         顯示此說明

環境變數:
  DB_HOST      資料庫主機 (預設: localhost)
  DB_PORT      資料庫埠號 (預設: 5432)
  DB_NAME      資料庫名稱 (預設: tw_stock)
  DB_USER      資料庫使用者 (預設: postgres)
  DB_PASSWORD  資料庫密碼 (必要)

範例:
  # 初始化資料庫
  export DB_PASSWORD=your_password
  $0

  # 刪除現有資料表並重新建立
  export DB_PASSWORD=your_password
  $0 --drop-existing

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
        echo "  $0"
        exit 1
    fi
}

# 檢查資料庫連線
check_db_connection() {
    log_info "檢查資料庫連線..."

    python3 << EOF
import sys
from sqlalchemy import create_engine, text

try:
    engine = create_engine('postgresql://${DB_USER:-postgres}:${DB_PASSWORD}@${DB_HOST:-localhost}:${DB_PORT:-5432}/${DB_NAME:-tw_stock}')
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    print("✓ 資料庫連線成功")
    sys.exit(0)
except Exception as e:
    print(f"✗ 資料庫連線失敗: {e}", file=sys.stderr)
    sys.exit(1)
EOF

    if [ $? -ne 0 ]; then
        log_error "無法連線到資料庫"
        exit 1
    fi
}

# 刪除現有資料表
drop_existing_tables() {
    log_warning "準備刪除所有現有資料表..."
    echo ""
    read -p "確定要刪除所有資料表嗎？此操作無法復原！(yes/no) " -r
    echo ""

    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        log_info "已取消刪除操作"
        return 1
    fi

    log_info "刪除現有資料表..."

    python3 << EOF
import sys
from sqlalchemy import create_engine, text, inspect

try:
    engine = create_engine('postgresql://${DB_USER:-postgres}:${DB_PASSWORD}@${DB_HOST:-localhost}:${DB_PORT:-5432}/${DB_NAME:-tw_stock}')

    # 取得所有表格
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if not tables:
        print("沒有需要刪除的資料表")
        sys.exit(0)

    print(f"找到 {len(tables)} 個資料表")

    # 刪除所有表格
    with engine.connect() as conn:
        # 先停用外鍵約束
        conn.execute(text('SET session_replication_role = replica;'))
        conn.commit()

        for table in tables:
            print(f"  刪除: {table}")
            conn.execute(text(f'DROP TABLE IF EXISTS {table} CASCADE'))

        # 恢復外鍵約束
        conn.execute(text('SET session_replication_role = DEFAULT;'))
        conn.commit()

    print(f"✓ 成功刪除 {len(tables)} 個資料表")
    sys.exit(0)
except Exception as e:
    print(f"✗ 刪除失敗: {e}", file=sys.stderr)
    sys.exit(1)
EOF

    if [ $? -eq 0 ]; then
        log_success "資料表刪除完成"
        return 0
    else
        log_error "資料表刪除失敗"
        return 1
    fi
}

# 初始化資料庫
init_database() {
    log_info "開始初始化資料庫..."

    cd "$PROJECT_ROOT"
    python3 services/common/database/init_db.py

    if [ $? -eq 0 ]; then
        log_success "資料庫初始化完成"
        return 0
    else
        log_error "資料庫初始化失敗"
        return 1
    fi
}

# 驗證資料庫結構
verify_database() {
    log_info "驗證資料庫結構..."

    python3 << EOF
import sys
from sqlalchemy import create_engine, inspect

try:
    engine = create_engine('postgresql://${DB_USER:-postgres}:${DB_PASSWORD}@${DB_HOST:-localhost}:${DB_PORT:-5432}/${DB_NAME:-tw_stock}')

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    print(f"\n✓ 資料庫包含 {len(tables)} 個資料表:")

    expected_tables = [
        'stocks',
        'stock_prices',
        'institutional_investors',
        'margin_trading',
        'securities_lending',
        'top20_volume',
        'stock_analysis_daily',
        'import_logs'
    ]

    for table in sorted(expected_tables):
        if table in tables:
            # 取得欄位數量
            columns = inspector.get_columns(table)
            indexes = inspector.get_indexes(table)
            print(f"  ✓ {table} ({len(columns)} 欄位, {len(indexes)} 索引)")
        else:
            print(f"  ✗ {table} (缺少)")

    missing = set(expected_tables) - set(tables)
    if missing:
        print(f"\n⚠ 缺少 {len(missing)} 個預期的資料表")
        sys.exit(1)
    else:
        print(f"\n✓ 所有預期的資料表都已建立")
        sys.exit(0)

except Exception as e:
    print(f"✗ 驗證失敗: {e}", file=sys.stderr)
    sys.exit(1)
EOF

    return $?
}

# 主程式
main() {
    local DROP_EXISTING=false

    # 解析參數
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --drop-existing)
                DROP_EXISTING=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                log_error "未知的參數: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}資料庫初始化腳本${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""

    # 檢查前置條件
    check_python
    check_db_password
    check_db_connection

    # 刪除現有資料表（如果需要）
    if [ "$DROP_EXISTING" = true ]; then
        if ! drop_existing_tables; then
            exit 1
        fi
        echo ""
    fi

    # 初始化資料庫
    if ! init_database; then
        exit 1
    fi

    echo ""

    # 驗證資料庫結構
    if ! verify_database; then
        log_warning "資料庫結構驗證失敗"
        exit 1
    fi

    echo ""
    echo -e "${GREEN}========================================${NC}"
    log_success "資料庫初始化完成"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "下一步："
    echo "  1. 匯入資料："
    echo "     ./scripts/data-importer/import_date_range.sh 2024-01-02 2026-02-02"
    echo ""
    echo "  2. 轉換技術指標："
    echo "     ./scripts/data-transformer/transform.sh today"
    echo ""
}

# 執行主程式
main "$@"
