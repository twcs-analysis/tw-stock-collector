#!/bin/bash
###############################################################################
# 平行化回補個股期貨歷史資料
#
# 使用方式：
#   ./backfill_stock_futures.sh 2026              # 收集 2026 年全年
#   ./backfill_stock_futures.sh 2026-01-01 2026-12-31  # 指定日期範圍
#   ./backfill_stock_futures.sh 2026 --workers 10  # 使用 10 個執行緒
#
# 作者：Claude Sonnet 4.5
# 日期：2026-03-15
###############################################################################

set -e

# 切換到專案根目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

# 檢查 Python 版本
if ! command -v python3.11 &> /dev/null; then
    echo "❌ 錯誤: 找不到 python3.11"
    echo "請安裝 Python 3.11 或更新版本"
    exit 1
fi

# 解析參數
if [ $# -eq 0 ]; then
    echo "用法:"
    echo "  $0 YEAR                      # 收集整年資料"
    echo "  $0 START_DATE END_DATE       # 收集日期範圍"
    echo ""
    echo "範例:"
    echo "  $0 2026                      # 收集 2026 年全年"
    echo "  $0 2026-01-01 2026-12-31     # 指定日期範圍"
    echo "  $0 2026 --workers 10         # 使用 10 個執行緒"
    exit 1
fi

# 顯示開始訊息
echo "=================================="
echo "個股期貨歷史資料回補（平行化）"
echo "=================================="
echo ""

# 執行收集
if [[ $1 =~ ^[0-9]{4}$ ]]; then
    # 第一個參數是年份
    echo "收集年份: $1"
    python3.11 scripts/data-collector/backfill_stock_futures_parallel.py --year $1 "${@:2}"
else
    # 第一個參數是日期
    echo "日期範圍: $1 ~ $2"
    python3.11 scripts/data-collector/backfill_stock_futures_parallel.py --start $1 --end $2 "${@:3}"
fi

# 顯示完成訊息
echo ""
echo "✅ 回補完成"
