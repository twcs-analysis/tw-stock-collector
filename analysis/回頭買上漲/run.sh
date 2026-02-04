#!/bin/bash
# ============================================================================
# 回頭買上漲選股 - 快速執行腳本
# ============================================================================

set -e

cd "$(dirname "$0")"

echo "🚀 執行回頭買上漲選股策略"
echo "預計執行時間：1-2 秒"
echo ""

# 將 SQL 複製到容器並執行
docker cp selector.sql tw-stock-postgres:/tmp/selector.sql

echo "⏱️  開始查詢..."
time docker exec -i tw-stock-postgres psql -U postgres -d tw_stock -f /tmp/selector.sql

echo ""
echo "✅ 查詢完成！"
