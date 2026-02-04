#!/bin/bash
# ============================================================================
# 主升段加速突破選股報告生成腳本
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORT_SCRIPT="${SCRIPT_DIR}/generate_report.py"

echo "=========================================="
echo "主升段加速突破選股報告生成"
echo "=========================================="
echo ""

# 檢查 Python 腳本是否存在
if [ ! -f "$REPORT_SCRIPT" ]; then
    echo "❌ 找不到報告生成腳本: $REPORT_SCRIPT"
    exit 1
fi

# 檢查 Docker 容器是否運行
if ! docker ps | grep -q tw-stock-postgres; then
    echo "❌ PostgreSQL 容器未運行，請先啟動容器"
    echo "   docker start tw-stock-postgres"
    exit 1
fi

# 決定查詢日期
if [ -n "$1" ]; then
    DATE_ARG="--date $1"
    echo "📅 查詢日期: $1"
else
    DATE_ARG=""
    echo "📅 查詢日期: 今天"
fi

echo ""
echo "🚀 開始生成報告..."
echo ""

# 執行報告生成
python3 "$REPORT_SCRIPT" $DATE_ARG

echo ""
echo "=========================================="
echo "✅ 報告生成完成"
echo "=========================================="
