#!/bin/bash
# ============================================================================
# 主升段加速突破選股 - 快速執行腳本
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SQL_FILE="${SCRIPT_DIR}/selector.sql"

echo "=========================================="
echo "主升段加速突破選股策略"
echo "=========================================="
echo ""

# 檢查 SQL 檔案是否存在
if [ ! -f "$SQL_FILE" ]; then
    echo "❌ 找不到 SQL 檔案: $SQL_FILE"
    exit 1
fi

# 檢查 Docker 容器是否運行
if ! docker ps | grep -q tw-stock-postgres; then
    echo "❌ PostgreSQL 容器未運行，請先啟動容器"
    echo "   docker start tw-stock-postgres"
    exit 1
fi

echo "📊 執行主升段加速突破選股查詢..."
echo ""

# 複製 SQL 到容器
docker cp "$SQL_FILE" tw-stock-postgres:/tmp/selector.sql

# 執行 SQL
docker exec -i tw-stock-postgres psql -U postgres -d tw_stock -f /tmp/selector.sql

echo ""
echo "=========================================="
echo "✅ 查詢完成"
echo "=========================================="
