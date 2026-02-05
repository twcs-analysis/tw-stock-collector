-- ============================================================================
-- 📊 回頭買上漲選股策略 + ETF 持股標註版 (2026-02-05)
-- ============================================================================
--
-- 特色：
-- 1. 不強制要求 ETF 持有（保留所有技術面合格標的）
-- 2. 標註是否被 ETF 持有（作為加分參考）
-- 3. 顯示 ETF 持有明細
-- ============================================================================

WITH params AS (
    SELECT
        '2026-02-05'::date AS target_date,
        ('2026-02-05'::date - INTERVAL '120 days')::date AS start_date
),

all_indicators AS (
    SELECT
        sp.stock_id,
        sp.trade_date,
        sp.close_price,
        sp.volume,

        LAG(sp.close_price, 1) OVER w_stock AS prev_close,

        AVG(sp.close_price) OVER w_5d AS ma_5,
        AVG(sp.close_price) OVER w_10d AS ma_10,
        AVG(sp.close_price) OVER w_20d AS ma_20,
        AVG(sp.close_price) OVER w_60d AS ma_60,

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

        ROUND(
            (ai.close_price - ai.prev_close) / NULLIF(ai.prev_close, 0) * 100,
            2
        ) AS pct_chg,

        ROUND(
            ai.volume::numeric / NULLIF(ai.vol_ma5, 0),
            2
        ) AS vol_ratio

    FROM all_indicators ai
    CROSS JOIN params
    WHERE ai.trade_date = params.target_date

    -- 核心技術條件（不含 ETF 篩選）
    AND ai.close_price > ai.ma_5          -- 站上5日線
    AND ai.ma_5 > ai.ma_20                -- 5日線 > 20日線
    AND ai.ma_20 > ai.ma_60               -- 20日線 > 60日線（多頭排列）
    AND ai.volume > ai.vol_ma5 * 1.2      -- 量能放大（至少1.2倍）
    AND (ai.close_price - ai.prev_close) / NULLIF(ai.prev_close, 0) > 0  -- 收紅K

    -- 流動性門檻
    AND ai.volume >= 500000                -- 至少500張
    AND ai.vol_ma5 >= 300000               -- 5日均量至少300張
),

-- 標註 ETF 持股資訊（使用 LEFT JOIN，保留所有標的）
annotated_stocks AS (
    SELECT
        ss.*,
        s.stock_name,
        COALESCE(esu.etf_count, 0) AS etf_count,
        COALESCE(esu.total_weight, 0) AS total_weight,
        CASE
            WHEN esu.etf_count IS NULL THEN '❌'
            WHEN esu.etf_count >= 2 THEN '✅✅'
            ELSE '✅'
        END AS etf_status
    FROM strategy_signals ss
    INNER JOIN stocks s ON ss.stock_id = s.stock_id
    LEFT JOIN etf_stock_union esu ON ss.stock_id = esu.stock_id  -- LEFT JOIN 保留所有標的
),

-- 計算綜合評分
scored_stocks AS (
    SELECT
        *,
        -- 綜合評分邏輯：
        -- 1. 漲幅分數（最高 40 分）
        LEAST(pct_chg * 4, 40) +
        -- 2. 量比分數（最高 30 分）
        LEAST(vol_ratio * 10, 30) +
        -- 3. ETF 持有分數（最高 20 分）
        CASE
            WHEN etf_count >= 2 THEN 20
            WHEN etf_count = 1 THEN 15
            ELSE 0
        END +
        -- 4. 流動性分數（最高 10 分）
        LEAST(volume::numeric / 1000000, 10) AS score
    FROM annotated_stocks
)

-- 📋 最終輸出（完整版，含所有技術面合格標的）
SELECT
    stock_id AS "股票代碼",
    stock_name AS "股票名稱",
    ROUND(close_price::numeric, 2) AS "收盤價",
    pct_chg AS "漲幅%",
    ROUND(volume::numeric / 1000, 0) AS "成交量(張)",
    vol_ratio AS "量比",
    etf_status AS "ETF",
    etf_count AS "ETF數",
    ROUND(total_weight::numeric, 2) AS "ETF權重%",
    ROUND(score::numeric, 1) AS "綜合評分",
    ROUND(ma_5::numeric, 2) AS "MA5",
    ROUND(ma_20::numeric, 2) AS "MA20",
    ROUND(ma_60::numeric, 2) AS "MA60"
FROM scored_stocks
ORDER BY
    score DESC,          -- 優先：綜合評分
    etf_count DESC,      -- 次要：ETF 持有數
    pct_chg DESC         -- 最後：漲幅
LIMIT 30;

-- ============================================================================
-- 📌 欄位說明
-- ============================================================================
--
-- ETF:
--   ✅✅ = 被 2 個以上 ETF 持有（高度機構認可）
--   ✅  = 被 1 個 ETF 持有（機構認可）
--   ❌  = 未被 ETF 持有（但技術面優異）
--
-- 綜合評分（滿分 100）:
--   - 漲幅分數（40%）: 漲幅越高越好
--   - 量比分數（30%）: 量能爆發越強越好
--   - ETF 持有（20%）: 機構持股加分
--   - 流動性（10%）: 成交量越大越好
--
-- ============================================================================
