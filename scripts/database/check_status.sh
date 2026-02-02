#!/bin/bash
#
# 資料庫狀態查詢腳本
#
# 功能：
#   - 檢查資料庫連線
#   - 查看資料表統計
#   - 顯示資料範圍
#
# 使用方式：
#   ./scripts/database/check_status.sh
#

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 日誌函式
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 檢查資料庫密碼
if [ -z "$DB_PASSWORD" ]; then
    log_error "請設定 DB_PASSWORD 環境變數"
    echo ""
    echo "範例："
    echo "  export DB_PASSWORD=your_password"
    echo "  $0"
    exit 1
fi

echo -e "${CYAN}======================================================================${NC}"
echo -e "${CYAN}資料庫狀態查詢${NC}"
echo -e "${CYAN}======================================================================${NC}"
echo ""

# 檢查連線並顯示資料庫資訊
python3 << 'EOF'
import os
import sys
from sqlalchemy import create_engine, text, inspect
from datetime import datetime

# 資料庫連線參數
db_host = os.environ.get('DB_HOST', 'localhost')
db_port = os.environ.get('DB_PORT', '5432')
db_name = os.environ.get('DB_NAME', 'tw_stock')
db_user = os.environ.get('DB_USER', 'postgres')
db_password = os.environ['DB_PASSWORD']

try:
    # 建立連線
    engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

    print("\033[0;32m✓ 資料庫連線成功\033[0m")
    print()
    print(f"\033[1;33m資料庫資訊:\033[0m")
    print(f"  主機: {db_host}:{db_port}")
    print(f"  資料庫: {db_name}")
    print(f"  使用者: {db_user}")
    print()

    # 取得所有資料表
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    print(f"\033[1;33m資料表統計:\033[0m")
    print(f"  總數: {len(tables)} 個資料表")
    print()

    with engine.connect() as conn:
        # 核心資料表統計
        core_tables = {
            'stocks': '股票基本資訊',
            'stock_prices': '每日價格資料',
            'institutional_investors': '三大法人買賣超',
            'margin_trading': '融資融券',
            'securities_lending': '借券賣出',
            'top20_volume': '成交量前 20 名',
            'stock_analysis_daily': '技術分析寬表',
            'import_logs': '匯入記錄'
        }

        print(f"\033[1;33m核心資料表:\033[0m")

        for table_name, description in core_tables.items():
            if table_name in tables:
                result = conn.execute(text(f'SELECT COUNT(*) FROM {table_name}'))
                count = result.scalar()

                # 取得欄位數和索引數
                columns = inspector.get_columns(table_name)
                indexes = inspector.get_indexes(table_name)

                status = "\033[0;32m✓\033[0m"
                print(f"  {status} {table_name}")
                print(f"      描述: {description}")
                print(f"      記錄數: {count:,}")
                print(f"      結構: {len(columns)} 欄位, {len(indexes)} 索引")

                # 顯示日期範圍（如果有 trade_date 欄位）
                col_names = [col['name'] for col in columns]
                if 'trade_date' in col_names and count > 0:
                    result = conn.execute(text(f'''
                        SELECT
                            MIN(trade_date)::text as first_date,
                            MAX(trade_date)::text as last_date,
                            COUNT(DISTINCT trade_date) as trading_days
                        FROM {table_name}
                    '''))
                    row = result.fetchone()
                    if row and row[0]:
                        print(f"      日期範圍: {row[0]} ~ {row[1]} ({row[2]} 個交易日)")
                print()
            else:
                status = "\033[0;31m✗\033[0m"
                print(f"  {status} {table_name} - {description} (不存在)")
                print()

        # stock_prices 詳細統計
        if 'stock_prices' in tables:
            print(f"\033[1;33mstock_prices 詳細統計:\033[0m")

            result = conn.execute(text('''
                SELECT
                    COUNT(DISTINCT stock_id) as stock_count,
                    COUNT(*) as total_records,
                    COUNT(DISTINCT trade_date) as trading_days,
                    MIN(trade_date)::text as first_date,
                    MAX(trade_date)::text as last_date
                FROM stock_prices
            '''))
            row = result.fetchone()

            if row:
                print(f"  股票總數: {row[0]:,} 檔")
                print(f"  總記錄數: {row[1]:,} 筆")
                print(f"  交易日數: {row[2]:,} 天")
                print(f"  日期範圍: {row[3]} ~ {row[4]}")
                print()

                # 按年份統計
                result = conn.execute(text('''
                    SELECT
                        EXTRACT(YEAR FROM trade_date)::int as year,
                        COUNT(DISTINCT trade_date) as trading_days,
                        COUNT(*) as records
                    FROM stock_prices
                    GROUP BY year
                    ORDER BY year
                '''))

                print(f"  年度分布:")
                for row in result:
                    print(f"    {row[0]}: {row[1]:3} 個交易日, {row[2]:,} 筆記錄")
                print()

        # 最近更新時間
        print(f"\033[1;33m最近匯入記錄:\033[0m")
        if 'import_logs' in tables:
            result = conn.execute(text('''
                SELECT
                    import_date,
                    data_type,
                    status,
                    records_count,
                    start_time
                FROM import_logs
                ORDER BY start_time DESC
                LIMIT 5
            '''))

            rows = result.fetchall()
            if rows:
                for row in rows:
                    status_icon = "✓" if row[2] == 'completed' else "✗"
                    print(f"  {status_icon} {row[0]} - {row[1]}: {row[3]:,} 筆 ({row[4]})")
            else:
                print(f"  (無匯入記錄)")
        print()

    print("\033[0;36m======================================================================\033[0m")
    print("\033[0;32m✓ 資料庫狀態查詢完成\033[0m")
    print("\033[0;36m======================================================================\033[0m")

except Exception as e:
    print(f"\033[0;31m✗ 查詢失敗: {e}\033[0m", file=sys.stderr)
    sys.exit(1)
EOF
