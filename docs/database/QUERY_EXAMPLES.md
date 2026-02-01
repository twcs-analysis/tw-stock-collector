# PostgreSQL 查詢範例與驗證 SQL

本文檔提供台股資料庫的常用查詢 SQL 語句。

---

## 🔍 基本查詢

### 1. 查看所有資料表

```sql
-- 方法 1: 使用 psql 指令
\dt

-- 方法 2: 使用 SQL 查詢
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

### 2. 查看表格結構

```sql
-- 查看 stocks 表結構
\d stocks

-- 查看 stock_analysis_daily 表結構
\d stock_analysis_daily

-- 查看所有欄位詳細資訊
SELECT
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'stock_analysis_daily'
ORDER BY ordinal_position;
```

### 3. 查看索引

```sql
-- 查看所有索引
\di

-- 查看特定表的索引
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'stock_analysis_daily';
```

---

## 📊 資料統計查詢

### 統計所有表格的記錄數

```sql
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
UNION ALL
SELECT 'import_logs', COUNT(*) FROM import_logs
ORDER BY table_name;
```

### 查看資料庫大小

```sql
-- 查看資料庫總大小
SELECT pg_size_pretty(pg_database_size('tw_stock')) as database_size;

-- 查看各表大小
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    pg_total_relation_size(schemaname||'.'||tablename) AS size_bytes
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY size_bytes DESC;
```

---

## 🏦 股票基本資料查詢

### 查詢所有股票

```sql
SELECT * FROM stocks ORDER BY stock_id;
```

### 查詢特定市場的股票

```sql
-- 上市股票
SELECT * FROM stocks WHERE market_type = 'twse' ORDER BY stock_id;

-- 上櫃股票
SELECT * FROM stocks WHERE market_type = 'tpex' ORDER BY stock_id;
```

### 股票數量統計

```sql
SELECT
    market_type,
    COUNT(*) as count
FROM stocks
GROUP BY market_type;
```

---

## 💰 價格資料查詢

### 查詢特定股票的歷史價格

```sql
-- 查詢台積電最近 10 天的價格
SELECT
    trade_date,
    open_price,
    high_price,
    low_price,
    close_price,
    volume
FROM stock_prices
WHERE stock_id = '2330'
ORDER BY trade_date DESC
LIMIT 10;
```

### 查詢特定日期的所有股票價格

```sql
SELECT
    sp.stock_id,
    s.stock_name,
    sp.close_price,
    sp.volume,
    sp.amount
FROM stock_prices sp
JOIN stocks s ON sp.stock_id = s.stock_id
WHERE sp.trade_date = '2024-12-27'
ORDER BY sp.amount DESC
LIMIT 20;
```

### 價格漲跌排行

```sql
-- 今日漲幅前 20 名
WITH price_change AS (
    SELECT
        stock_id,
        trade_date,
        close_price,
        LAG(close_price) OVER (PARTITION BY stock_id ORDER BY trade_date) as prev_close,
        (close_price - LAG(close_price) OVER (PARTITION BY stock_id ORDER BY trade_date)) /
        LAG(close_price) OVER (PARTITION BY stock_id ORDER BY trade_date) * 100 as change_pct
    FROM stock_prices
)
SELECT
    pc.stock_id,
    s.stock_name,
    pc.close_price,
    pc.prev_close,
    ROUND(pc.change_pct, 2) as change_pct
FROM price_change pc
JOIN stocks s ON pc.stock_id = s.stock_id
WHERE pc.trade_date = '2024-12-27'
  AND pc.prev_close IS NOT NULL
ORDER BY pc.change_pct DESC
LIMIT 20;
```

---

## 📈 技術分析查詢

### 查詢技術指標

```sql
-- 查詢台積電的技術指標
SELECT
    trade_date,
    close_price,
    ma_5, ma_20, ma_60,
    rsi_14,
    macd_dif, macd_dea, macd_hist,
    dmi_adx,
    vol_ratio
FROM stock_analysis_daily
WHERE stock_id = '2330'
ORDER BY trade_date DESC
LIMIT 10;
```

### 均線多頭排列選股

```sql
-- 選股條件：收盤價 > MA5 > MA20 > MA60
SELECT
    sad.stock_id,
    s.stock_name,
    sad.close_price,
    sad.ma_5,
    sad.ma_20,
    sad.ma_60,
    sad.vol_ratio,
    ROUND((sad.close_price - sad.ma_20) / sad.ma_20 * 100, 2) as above_ma20_pct
FROM stock_analysis_daily sad
JOIN stocks s ON sad.stock_id = s.stock_id
WHERE sad.trade_date = '2024-12-27'
  AND sad.close_price > sad.ma_5
  AND sad.ma_5 > sad.ma_20
  AND sad.ma_20 > sad.ma_60
ORDER BY sad.vol_ratio DESC;
```

### RSI 超買超賣選股

```sql
-- RSI < 30 (超賣)
SELECT
    sad.stock_id,
    s.stock_name,
    sad.close_price,
    sad.rsi_14,
    sad.macd_hist,
    sad.vol_ratio
FROM stock_analysis_daily sad
JOIN stocks s ON sad.stock_id = s.stock_id
WHERE sad.trade_date = '2024-12-27'
  AND sad.rsi_14 < 30
ORDER BY sad.rsi_14 ASC;

-- RSI > 70 (超買)
SELECT
    sad.stock_id,
    s.stock_name,
    sad.close_price,
    sad.rsi_14,
    sad.macd_hist
FROM stock_analysis_daily sad
JOIN stocks s ON sad.stock_id = s.stock_id
WHERE sad.trade_date = '2024-12-27'
  AND sad.rsi_14 > 70
ORDER BY sad.rsi_14 DESC;
```

### MACD 黃金交叉選股

```sql
-- MACD 黃金交叉：DIF 向上穿越 DEA
WITH macd_cross AS (
    SELECT
        stock_id,
        trade_date,
        macd_dif,
        macd_dea,
        LAG(macd_dif) OVER (PARTITION BY stock_id ORDER BY trade_date) as prev_dif,
        LAG(macd_dea) OVER (PARTITION BY stock_id ORDER BY trade_date) as prev_dea
    FROM stock_analysis_daily
)
SELECT
    mc.stock_id,
    s.stock_name,
    mc.macd_dif,
    mc.macd_dea,
    mc.prev_dif,
    mc.prev_dea
FROM macd_cross mc
JOIN stocks s ON mc.stock_id = s.stock_id
WHERE mc.trade_date = '2024-12-27'
  AND mc.prev_dif < mc.prev_dea  -- 前一日 DIF < DEA
  AND mc.macd_dif > mc.macd_dea  -- 今日 DIF > DEA (黃金交叉)
ORDER BY mc.macd_dif - mc.macd_dea DESC;
```

### 布林帶突破選股

```sql
-- 收盤價突破上軌
SELECT
    sad.stock_id,
    s.stock_name,
    sad.close_price,
    sad.bb_upper,
    sad.bb_mid,
    sad.bb_lower,
    ROUND((sad.close_price - sad.bb_upper) / sad.bb_upper * 100, 2) as above_upper_pct
FROM stock_analysis_daily sad
JOIN stocks s ON sad.stock_id = s.stock_id
WHERE sad.trade_date = '2024-12-27'
  AND sad.close_price > sad.bb_upper
ORDER BY above_upper_pct DESC;

-- 收盤價跌破下軌
SELECT
    sad.stock_id,
    s.stock_name,
    sad.close_price,
    sad.bb_lower,
    ROUND((sad.bb_lower - sad.close_price) / sad.bb_lower * 100, 2) as below_lower_pct
FROM stock_analysis_daily sad
JOIN stocks s ON sad.stock_id = s.stock_id
WHERE sad.trade_date = '2024-12-27'
  AND sad.close_price < sad.bb_lower
ORDER BY below_lower_pct DESC;
```

### 量價齊揚選股

```sql
-- 價漲量增
SELECT
    sad.stock_id,
    s.stock_name,
    sad.close_price,
    sad.ma_20,
    sad.vol_ratio,
    sad.volume,
    ROUND((sad.close_price - sad.ma_20) / sad.ma_20 * 100, 2) as above_ma20_pct
FROM stock_analysis_daily sad
JOIN stocks s ON sad.stock_id = s.stock_id
WHERE sad.trade_date = '2024-12-27'
  AND sad.close_price > sad.ma_20  -- 價格在 MA20 之上
  AND sad.vol_ratio > 1.5          -- 量能放大 1.5 倍
ORDER BY sad.vol_ratio DESC;
```

### DMI 趨勢啟動選股

```sql
-- DMI 趨勢強勁：+DI > -DI 且 ADX > 25
SELECT
    sad.stock_id,
    s.stock_name,
    sad.close_price,
    sad.dmi_pdi,
    sad.dmi_mdi,
    sad.dmi_adx,
    ROUND(sad.dmi_pdi - sad.dmi_mdi, 2) as di_diff
FROM stock_analysis_daily sad
JOIN stocks s ON sad.stock_id = s.stock_id
WHERE sad.trade_date = '2024-12-27'
  AND sad.dmi_pdi > sad.dmi_mdi  -- 多頭趨勢
  AND sad.dmi_adx > 25           -- 趨勢強度夠強
ORDER BY sad.dmi_adx DESC;
```

---

## 👥 三大法人查詢

### 外資買賣超排行

```sql
-- 外資買超前 20 名
SELECT
    ii.stock_id,
    s.stock_name,
    ii.foreign_net,
    ii.trust_net,
    ii.dealer_net,
    ii.total_net,
    sp.close_price
FROM institutional_investors ii
JOIN stocks s ON ii.stock_id = s.stock_id
LEFT JOIN stock_prices sp ON ii.stock_id = sp.stock_id AND ii.trade_date = sp.trade_date
WHERE ii.trade_date = '2024-12-27'
ORDER BY ii.foreign_net DESC
LIMIT 20;

-- 外資賣超前 20 名
SELECT
    ii.stock_id,
    s.stock_name,
    ii.foreign_net,
    sp.close_price
FROM institutional_investors ii
JOIN stocks s ON ii.stock_id = s.stock_id
LEFT JOIN stock_prices sp ON ii.stock_id = sp.stock_id AND ii.trade_date = sp.trade_date
WHERE ii.trade_date = '2024-12-27'
ORDER BY ii.foreign_net ASC
LIMIT 20;
```

### 三大法人同步買超

```sql
-- 外資、投信、自營商同時買超
SELECT
    ii.stock_id,
    s.stock_name,
    ii.foreign_net,
    ii.trust_net,
    ii.dealer_net,
    ii.total_net,
    sp.close_price
FROM institutional_investors ii
JOIN stocks s ON ii.stock_id = s.stock_id
LEFT JOIN stock_prices sp ON ii.stock_id = sp.stock_id AND ii.trade_date = sp.trade_date
WHERE ii.trade_date = '2024-12-27'
  AND ii.foreign_net > 0
  AND ii.trust_net > 0
  AND ii.dealer_net > 0
ORDER BY ii.total_net DESC;
```

---

## 💼 融資融券查詢

### 融資增減排行

```sql
-- 融資增加前 20 名
SELECT
    mt.stock_id,
    s.stock_name,
    mt.margin_change,
    mt.margin_balance,
    sp.close_price
FROM margin_trading mt
JOIN stocks s ON mt.stock_id = s.stock_id
LEFT JOIN stock_prices sp ON mt.stock_id = sp.stock_id AND mt.trade_date = sp.trade_date
WHERE mt.trade_date = '2024-12-27'
ORDER BY mt.margin_change DESC
LIMIT 20;
```

### 融券增減排行

```sql
-- 融券增加前 20 名（可能有放空壓力）
SELECT
    mt.stock_id,
    s.stock_name,
    mt.short_change,
    mt.short_balance,
    sp.close_price
FROM margin_trading mt
JOIN stocks s ON mt.stock_id = s.stock_id
LEFT JOIN stock_prices sp ON mt.stock_id = sp.stock_id AND mt.trade_date = sp.trade_date
WHERE mt.trade_date = '2024-12-27'
ORDER BY mt.short_change DESC
LIMIT 20;
```

---

## 🔄 綜合選股策略

### 策略一：多頭趨勢 + 法人買超 + 量能放大

```sql
SELECT
    sad.stock_id,
    s.stock_name,
    sad.close_price,
    sad.ma_5, sad.ma_20, sad.ma_60,
    sad.rsi_14,
    sad.vol_ratio,
    ii.foreign_net,
    ii.trust_net,
    ii.total_net
FROM stock_analysis_daily sad
JOIN stocks s ON sad.stock_id = s.stock_id
LEFT JOIN institutional_investors ii ON sad.stock_id = ii.stock_id AND sad.trade_date = ii.trade_date
WHERE sad.trade_date = '2024-12-27'
  -- 均線多頭
  AND sad.close_price > sad.ma_5
  AND sad.ma_5 > sad.ma_20
  AND sad.ma_20 > sad.ma_60
  -- 量能放大
  AND sad.vol_ratio > 1.2
  -- 法人買超
  AND ii.total_net > 1000000
ORDER BY ii.total_net DESC, sad.vol_ratio DESC;
```

### 策略二：超跌反彈 (RSI 超賣 + MACD 翻多)

```sql
SELECT
    sad.stock_id,
    s.stock_name,
    sad.close_price,
    sad.rsi_14,
    sad.macd_dif,
    sad.macd_dea,
    sad.macd_hist,
    sad.vol_ratio
FROM stock_analysis_daily sad
JOIN stocks s ON sad.stock_id = s.stock_id
WHERE sad.trade_date = '2024-12-27'
  -- RSI 超賣
  AND sad.rsi_14 < 30
  -- MACD 柱狀體轉正
  AND sad.macd_hist > 0
  -- 量能放大
  AND sad.vol_ratio > 1.0
ORDER BY sad.rsi_14 ASC;
```

---

## 🔧 資料驗證查詢

### 檢查資料完整性

```sql
-- 檢查是否有空值
SELECT
    'stock_prices' as table_name,
    COUNT(*) as total_rows,
    COUNT(CASE WHEN close_price IS NULL THEN 1 END) as null_close_price,
    COUNT(CASE WHEN volume IS NULL THEN 1 END) as null_volume
FROM stock_prices
WHERE trade_date = '2024-12-27'

UNION ALL

SELECT
    'stock_analysis_daily',
    COUNT(*),
    COUNT(CASE WHEN ma_20 IS NULL THEN 1 END),
    COUNT(CASE WHEN rsi_14 IS NULL THEN 1 END)
FROM stock_analysis_daily
WHERE trade_date = '2024-12-27';
```

### 檢查資料範圍

```sql
-- 檢查價格資料的日期範圍
SELECT
    MIN(trade_date) as earliest_date,
    MAX(trade_date) as latest_date,
    COUNT(DISTINCT trade_date) as trading_days,
    COUNT(DISTINCT stock_id) as stock_count
FROM stock_prices;

-- 檢查技術分析資料的日期範圍
SELECT
    MIN(trade_date) as earliest_date,
    MAX(trade_date) as latest_date,
    COUNT(DISTINCT trade_date) as trading_days
FROM stock_analysis_daily;
```

---

## 📊 效能分析查詢

### 查詢執行計畫

```sql
-- 分析查詢效能
EXPLAIN ANALYZE
SELECT stock_id, close_price, ma_5, ma_20, vol_ratio
FROM stock_analysis_daily
WHERE trade_date = '2024-12-27'
  AND close_price > ma_5
  AND vol_ratio > 1.5;
```

### 索引使用統計

```sql
-- 查看索引使用情況
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

---

**最後更新**: 2026-02-01
**維護者**: tw-stock-collector 專案團隊
