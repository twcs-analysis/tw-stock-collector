#!/bin/bash
###############################################################################
# 個股期貨資料收集腳本
#
# 用途：收集 TAIFEX 個股期貨每日交易資料
#
# 使用方式：
#   ./collect_stock_futures.sh                    # 收集今天的資料
#   ./collect_stock_futures.sh 2026-03-13         # 收集指定日期的資料
#   ./collect_stock_futures.sh 2026-03-13 --no-validation  # 不執行驗證
#
# 作者：Claude Sonnet 4.5
# 日期：2026-03-15
###############################################################################

set -e  # 遇到錯誤立即停止

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
DATE=""
VALIDATION_FLAG=""

if [ $# -ge 1 ]; then
    DATE="--date $1"
fi

if [ $# -ge 2 ] && [ "$2" = "--no-validation" ]; then
    VALIDATION_FLAG="--no-validation"
fi

# 顯示收集資訊
echo "=================================="
echo "個股期貨資料收集"
echo "=================================="
if [ -n "$DATE" ]; then
    echo "日期: $1"
else
    echo "日期: 今天"
fi
echo ""

# 執行收集
python3.11 scripts/data-collector/collect_stock_futures.py $DATE $VALIDATION_FLAG

# 顯示結果
echo ""
echo "✅ 收集完成"
