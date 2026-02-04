-- ============================================================================
-- 📊 回頭買上漲選股策略 + ETF 持股篩選
-- ============================================================================
--
-- 策略說明：
-- 1. 使用「回頭買上漲」策略篩選符合條件的股票
-- 2. 再篩選出被 ETF 持有的標的
-- 3. 降低選股風險，提高機構認可度
--
-- ============================================================================

-- 📅 參數設定
WITH params AS (
    SELECT
        '2026-02-04'::date AS target_date,
        ('2026-02-04'::date - INTERVAL '120 days')::date AS start_date,
        1 AS min_etf_count  -- 最少被幾個 ETF 持有
),

-- 📊 計算技術指標
all_indicators AS (
    SELECT
        sp.stock_id,
        sp.trade_date,
        sp.close_price,
        sp.volume,

        LAG(sp.close_price, 1) OVER w_stock AS prev_close,

        -- 均線系統
        AVG(sp.close_price) OVER w_5d AS ma_5,
        AVG(sp.close_price) OVER w_10d AS ma_10,
        AVG(sp.close_price) OVER w_20d AS ma_20,
        AVG(sp.close_price) OVER w_60d AS ma_60,

        -- 量能指標
        AVG(sp.volume) OVER w_5d AS vol_ma5,
        AVG(sp.volume) OVER w_20d AS vol_ma20

    FROM stock_prices sp
    CROSS JOIN params
    WHERE sp.trade_date BETWEEN params.start_date AND params.target_date

    WINDOW
        w_stock AS (PARTITION BY sp.stock_id ORDER BY sp.trade_date),
        w_5d AS (PARTITION BY sp.stock_id ORDER BY sp.trade_date ROWS BETWEEN 4 PRECEDING AND CURRENT ROW),
        w_10d AS (PARTITION BY sp.stock_id ORDER BY sp.trade_date ROWS BETWEEN 9 PRECEDING AND CURRENT ROW),
        w_20d AS (PARTITION BY sp.stock_id ORDER BY sp.trade_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW),
        w_60d AS (PARTITION BY sp.stock_id ORDER BY sp.trade_date ROWS BETWEEN 59 PRECEDING AND CURRENT ROW)
),

-- 🎯 回頭買上漲策略篩選
strategy_signals AS (
    SELECT
        ai.stock_id,
        ai.trade_date,
        ai.close_price,
        ai.volume,
        ai.ma_5,
        ai.ma_20,
        ai.ma_60,
        ai.vol_ma5,

        -- 計算漲跌幅
        ROUND(
            (ai.close_price - ai.prev_close) / NULLIF(ai.prev_close, 0) * 100,
            2
        ) AS pct_chg,

        -- 計算量比
        ROUND(
            ai.volume::numeric / NULLIF(ai.vol_ma5, 0),
            2
        ) AS vol_ratio

    FROM all_indicators ai
    CROSS JOIN params
    WHERE ai.trade_date = params.target_date

    -- 核心條件
    AND ai.close_price > ai.ma_5          -- 站上5日線
    AND ai.ma_5 > ai.ma_20                -- 5日線 > 20日線
    AND ai.ma_20 > ai.ma_60               -- 20日線 > 60日線（多頭排列）
    AND ai.volume > ai.vol_ma5 * 1.2      -- 量能放大（至少1.2倍）
    AND (ai.close_price - ai.prev_close) / NULLIF(ai.prev_close, 0) > 0  -- 收紅K

    -- 流動性門檻
    AND ai.volume >= 500000                -- 至少500張
    AND ai.vol_ma5 >= 300000               -- 5日均量至少300張
),

-- 🎯 ETF 持股篩選
etf_filtered_stocks AS (
    SELECT
        ss.*,
        s.stock_name,
        esu.etf_count,
        esu.total_weight
    FROM strategy_signals ss
    INNER JOIN stocks s ON ss.stock_id = s.stock_id
    INNER JOIN etf_stock_union esu ON ss.stock_id = esu.stock_id
    CROSS JOIN params
    WHERE esu.etf_count >= params.min_etf_count
)

-- 📋 最終輸出
SELECT
    stock_id AS "股票代碼",
    stock_name AS "股票名稱",
    ROUND(close_price::numeric, 2) AS "收盤價",
    pct_chg AS "漲幅%",
    ROUND(volume::numeric / 1000, 0) AS "成交量(張)",
    vol_ratio AS "量比",
    etf_count AS "ETF持有數",
    ROUND(total_weight::numeric, 2) AS "ETF總權重%",
    ROUND(ma_5::numeric, 2) AS "MA5",
    ROUND(ma_20::numeric, 2) AS "MA20",
    ROUND(ma_60::numeric, 2) AS "MA60"
FROM etf_filtered_stocks
ORDER BY
    etf_count DESC,
    vol_ratio DESC
LIMIT 20;
