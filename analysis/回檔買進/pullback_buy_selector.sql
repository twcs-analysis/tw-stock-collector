-- ============================================================================
-- 回檔買上漲選股 SQL 查詢
-- ============================================================================
--
-- 選股條件：
-- 條件 A：股票型態是否為 頭頭高 底底高
-- 條件 B：股價是否在月線之上且前低未破？
-- 條件 C：今日紅 K 是否站上 5 均？
-- 條件 D：收盤是否過昨日高？
--
-- 資料表：stock_prices
-- 欄位：trade_date, stock_id, open_price, high_price, low_price, close_price, volume
--
-- ============================================================================

WITH
-- ⚙️ 參數設定：修改這裡的日期即可
params AS (
    SELECT
        '2026-02-03'::date AS target_date  -- 📅 目標查詢日期（修改這裡）
),


-- Step 1: 計算移動平均線（MA5, MA20）
moving_averages AS (
    SELECT
        trade_date,
        stock_id,
        open_price,
        high_price,
        low_price,
        close_price,
        volume,
        -- MA5: 5日均線
        AVG(close_price) OVER (
            PARTITION BY stock_id
            ORDER BY trade_date
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ) AS ma_5,
        -- MA20: 20日均線（月線）
        AVG(close_price) OVER (
            PARTITION BY stock_id
            ORDER BY trade_date
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) AS ma_20,
        -- 20日平均成交量
        AVG(volume) OVER (
            PARTITION BY stock_id
            ORDER BY trade_date
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) AS vol_ma20
    FROM stock_prices, params
    WHERE trade_date <= params.target_date
),

-- Step 2: 計算最近10天的高點和低點（用於判斷頭頭高底底高）
recent_highs_lows AS (
    SELECT
        trade_date,
        stock_id,
        close_price,
        high_price,
        low_price,
        -- 最近5天（不含今天）的平均高點
        AVG(high_price) OVER (
            PARTITION BY stock_id
            ORDER BY trade_date
            ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING
        ) AS avg_high_recent,
        -- 前5天的平均高點
        AVG(high_price) OVER (
            PARTITION BY stock_id
            ORDER BY trade_date
            ROWS BETWEEN 10 PRECEDING AND 6 PRECEDING
        ) AS avg_high_earlier,
        -- 最近5天（不含今天）的平均低點
        AVG(low_price) OVER (
            PARTITION BY stock_id
            ORDER BY trade_date
            ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING
        ) AS avg_low_recent,
        -- 前5天的平均低點
        AVG(low_price) OVER (
            PARTITION BY stock_id
            ORDER BY trade_date
            ROWS BETWEEN 10 PRECEDING AND 6 PRECEDING
        ) AS avg_low_earlier
    FROM stock_prices, params
    WHERE trade_date <= params.target_date
),

-- Step 3: 計算前低（最近10天最低點，不含今天）
prev_lows AS (
    SELECT
        trade_date,
        stock_id,
        low_price,
        MIN(low_price) OVER (
            PARTITION BY stock_id
            ORDER BY trade_date
            ROWS BETWEEN 10 PRECEDING AND 1 PRECEDING
        ) AS prev_low
    FROM stock_prices, params
    WHERE trade_date <= params.target_date
),

-- Step 4: 取得昨日高點
yesterday_highs AS (
    SELECT
        trade_date,
        stock_id,
        high_price,
        LAG(high_price, 1) OVER (
            PARTITION BY stock_id
            ORDER BY trade_date
        ) AS yesterday_high
    FROM stock_prices, params
    WHERE trade_date <= params.target_date
),

-- Step 5: 整合所有資料
integrated_data AS (
    SELECT
        ma.trade_date,
        ma.stock_id,
        ma.open_price,
        ma.high_price,
        ma.low_price,
        ma.close_price,
        ma.volume,
        ma.ma_5,
        ma.ma_20,
        ma.vol_ma20,
        rhl.avg_high_recent,
        rhl.avg_high_earlier,
        rhl.avg_low_recent,
        rhl.avg_low_earlier,
        pl.prev_low,
        yh.yesterday_high,
        -- 計算量比
        CASE
            WHEN ma.vol_ma20 > 0 THEN ma.volume / ma.vol_ma20
            ELSE 0
        END AS vol_ratio
    FROM moving_averages ma
    JOIN recent_highs_lows rhl
        ON ma.trade_date = rhl.trade_date
        AND ma.stock_id = rhl.stock_id
    JOIN prev_lows pl
        ON ma.trade_date = pl.trade_date
        AND ma.stock_id = pl.stock_id
    JOIN yesterday_highs yh
        ON ma.trade_date = yh.trade_date
        AND ma.stock_id = yh.stock_id
    CROSS JOIN params
    WHERE ma.trade_date = params.target_date
)

-- Step 6: 篩選符合四個條件的股票
SELECT
    stock_id,
    close_price,
    open_price,
    high_price,
    low_price,
    ma_5,
    ma_20,
    volume,
    vol_ratio,
    -- 條件檢查結果
    CASE WHEN avg_high_recent > avg_high_earlier THEN '✓' ELSE '✗' END AS condition_a_higher_highs,
    CASE WHEN avg_low_recent > avg_low_earlier THEN '✓' ELSE '✗' END AS condition_a_higher_lows,
    CASE WHEN close_price > ma_20 THEN '✓' ELSE '✗' END AS condition_b_above_ma20,
    CASE WHEN low_price >= prev_low THEN '✓' ELSE '✗' END AS condition_b_not_break_prev_low,
    CASE WHEN close_price > open_price THEN '✓' ELSE '✗' END AS condition_c_red_k,
    CASE WHEN close_price > ma_5 THEN '✓' ELSE '✗' END AS condition_c_above_ma5,
    CASE WHEN close_price > yesterday_high THEN '✓' ELSE '✗' END AS condition_d_break_yesterday_high
FROM integrated_data
WHERE
    -- 條件 A：頭頭高 底底高
    avg_high_recent > avg_high_earlier
    AND avg_low_recent > avg_low_earlier

    -- 條件 B：股價在月線之上且前低未破
    AND close_price > ma_20
    AND low_price >= prev_low

    -- 條件 C：今日紅 K 站上 5 均
    AND close_price > open_price  -- 紅 K
    AND close_price > ma_5         -- 站上 MA5

    -- 條件 D：收盤過昨日高
    AND close_price > yesterday_high

    -- 排除 ETF 和小型股
    AND stock_id >= '1000'  -- 字串比較（排除 ETF 代碼 00XX）
    AND volume >= 1000000

ORDER BY close_price DESC;


-- ============================================================================
-- 簡化版查詢（僅顯示關鍵資訊）
-- ============================================================================

WITH
-- ⚙️ 參數設定
params AS (
    SELECT '2026-02-03'::date AS target_date
),

moving_averages AS (
    SELECT
        trade_date,
        stock_id,
        open_price,
        high_price,
        low_price,
        close_price,
        volume,
        AVG(close_price) OVER (PARTITION BY stock_id ORDER BY trade_date ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS ma_5,
        AVG(close_price) OVER (PARTITION BY stock_id ORDER BY trade_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS ma_20,
        MIN(low_price) OVER (PARTITION BY stock_id ORDER BY trade_date ROWS BETWEEN 10 PRECEDING AND 1 PRECEDING) AS prev_low,
        LAG(high_price, 1) OVER (PARTITION BY stock_id ORDER BY trade_date) AS yesterday_high
    FROM stock_prices, params
    WHERE trade_date <= params.target_date
)

SELECT
    stock_id AS "股票代號",
    close_price AS "收盤價",
    ROUND((close_price - ma_5) / ma_5 * 100, 2) AS "距MA5(%)",
    ROUND((close_price - ma_20) / ma_20 * 100, 2) AS "距MA20(%)",
    ROUND(volume / 1000000.0, 2) AS "成交量(百萬)",
    '✓' AS "條件確認"
FROM moving_averages, params
WHERE
    trade_date = params.target_date
    AND close_price > open_price      -- 紅 K
    AND close_price > ma_5             -- 站上 MA5
    AND close_price > ma_20            -- 在月線上
    AND low_price >= prev_low          -- 未破前低
    AND close_price > yesterday_high   -- 突破昨日高
    AND stock_id >= '1000'  -- 字串比較（排除 ETF 代碼 00XX）
    AND volume >= 1000000
ORDER BY close_price DESC;


-- ============================================================================
-- 進階版：加入 RSI 和 MACD（需要有技術指標表）
-- ============================================================================
--
-- 如果你的資料庫中有 technical_indicators 表，可以使用以下查詢：
--
-- SELECT
--     sp.stock_id,
--     sp.close_price,
--     ti.rsi_14,
--     ti.macd_hist,
--     ...
-- FROM stock_prices sp
-- JOIN technical_indicators ti
--     ON sp.trade_date = ti.trade_date
--     AND sp.stock_id = ti.stock_id
-- WHERE ...
--
-- ============================================================================


-- ============================================================================
-- 使用範例
-- ============================================================================
--
-- 📅 修改查詢日期：
--    在每個查詢的 params CTE 中修改 target_date
--    例如：SELECT '2026-02-03'::date AS target_date
--
-- 🚀 執行方式：
--    1. psql -U postgres -d tw_stock -f pullback_buy_selector.sql
--    2. 在 PostgreSQL 互動模式中：\i pullback_buy_selector.sql
--
-- 🔧 調整篩選條件：
--    修改最終 SELECT 的 WHERE 子句
--
-- ============================================================================
