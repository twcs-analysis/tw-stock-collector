#!/bin/bash
# ====================================
# PostgreSQL 資料庫驗證腳本
# ====================================

echo "=== PostgreSQL 資料庫驗證 ==="
echo ""

# 1. 查看所有資料表
echo "1. 所有資料表"
echo "----------------------------------------"
docker exec tw-stock-postgres psql -U postgres -d tw_stock -c "\dt"
echo ""

# 2. 統計各表記錄數
echo "2. 各表記錄數統計"
echo "----------------------------------------"
docker exec tw-stock-postgres psql -U postgres -d tw_stock <<'SQL'
SELECT
    'stocks' as table_name,
    COUNT(*) as count
FROM stocks
UNION ALL
SELECT 'stock_prices', COUNT(*) FROM stock_prices
UNION ALL
SELECT 'stock_analysis_daily', COUNT(*) FROM stock_analysis_daily
UNION ALL
SELECT 'institutional_investors', COUNT(*) FROM institutional_investors
UNION ALL
SELECT 'margin_trading', COUNT(*) FROM margin_trading
UNION ALL
SELECT 'securities_lending', COUNT(*) FROM securities_lending
UNION ALL
SELECT 'top20_volume', COUNT(*) FROM top20_volume
ORDER BY table_name;
SQL
echo ""

# 3. 查看股票列表
echo "3. 股票列表"
echo "----------------------------------------"
docker exec tw-stock-postgres psql -U postgres -d tw_stock -c "SELECT * FROM stocks ORDER BY stock_id;"
echo ""

# 4. 查看技術分析資料
echo "4. 技術分析資料（最近5筆）"
echo "----------------------------------------"
docker exec tw-stock-postgres psql -U postgres -d tw_stock <<'SQL'
SELECT
    trade_date,
    stock_id,
    close_price,
    ma_5, ma_20, ma_60,
    rsi_14,
    macd_hist,
    vol_ratio
FROM stock_analysis_daily
ORDER BY trade_date DESC, stock_id
LIMIT 5;
SQL
echo ""

# 5. 資料庫大小
echo "5. 資料庫大小"
echo "----------------------------------------"
docker exec tw-stock-postgres psql -U postgres -d tw_stock -c "SELECT pg_size_pretty(pg_database_size('tw_stock')) as database_size;"
echo ""

# 6. 索引數量統計
echo "6. 索引數量統計"
echo "----------------------------------------"
docker exec tw-stock-postgres psql -U postgres -d tw_stock <<'SQL'
SELECT
    tablename,
    COUNT(*) as index_count
FROM pg_indexes
WHERE schemaname = 'public'
GROUP BY tablename
ORDER BY index_count DESC;
SQL
echo ""

echo "=== 驗證完成 ==="
