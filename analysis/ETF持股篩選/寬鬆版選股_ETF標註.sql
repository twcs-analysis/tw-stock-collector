-- ============================================================================
-- 📊 寬鬆版選股策略 + ETF 標註 (2026-02-05)
-- ============================================================================
--
-- 特色：
-- 1. 不強制「完美多頭排列」（只要站上 MA5 即可）
-- 2. 降低流動性門檻（300張 → 100張）
-- 3. 保留更多候選標的
-- 4. 標註 ETF 持有作為參考
-- ============================================================================

WITH params AS (
    SELECT
        '2026-02-05'::date AS target_date,
        ('2026-02-05'::date - INTERVAL '60 days')::date AS start_date
),

all_indicators AS (
    SELECT
        sp.stock_id,
        sp.trade_date,
        sp.close_price,
        sp.volume,

        LAG(sp.close_price, 1) OVER w_stock AS prev_close,

        AVG(sp.close_price) OVER w_5d AS ma_5,
        AVG(sp.close_price) OVER w_20d AS ma_20,

        AVG(sp.volume) OVER w_5d AS vol_ma5

    FROM stock_prices sp
    CROSS JOIN params
    WHERE sp.trade_date BETWEEN params.start_date AND params.target_date

    WINDOW
        w_stock AS (PARTITION BY sp.stock_id ORDER BY sp.trade_date),
        w_5d AS (PARTITION BY sp.stock_id ORDER BY sp.trade_date ROWS BETWEEN 4 PRECEDING AND CURRENT ROW),
        w_20d AS (PARTITION BY sp.stock_id ORDER BY sp.trade_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW)
),

strategy_signals AS (
    SELECT
        ai.stock_id,
        ai.close_price,
        ai.volume,
        ai.ma_5,
        ai.ma_20,

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

    -- 🔻 寬鬆條件（不要求完美多頭排列）
    AND (ai.close_price - ai.prev_close) / NULLIF(ai.prev_close, 0) > 0  -- 收紅K
    AND ai.close_price > ai.ma_5          -- 站上5日線（只要這條！）
    AND ai.volume > ai.vol_ma5 * 1.2      -- 量能放大

    -- 🔻 降低流動性門檻
    AND ai.volume >= 300000               -- 至少300張（原本 500）
    AND ai.vol_ma5 >= 100000              -- 5日均量至少100張（原本 300）
),

annotated_stocks AS (
    SELECT
        ss.*,
        s.stock_name,
        COALESCE(esu.etf_count, 0) AS etf_count,
        COALESCE(esu.total_weight, 0) AS total_weight,
        COALESCE(
            (SELECT STRING_AGG(e.etf_name || '(' || ROUND(eh.weight::numeric, 2) || '%)', ', ')
             FROM etf_holdings eh
             JOIN etfs e ON eh.etf_id = e.etf_id
             WHERE eh.stock_id = ss.stock_id),
            '-'
        ) AS etf_list,
        CASE
            WHEN esu.etf_count >= 2 THEN '✅✅'
            WHEN esu.etf_count = 1 THEN '✅'
            ELSE '❌'
        END AS etf_status,
        -- 趨勢標註
        CASE
            WHEN ss.ma_5 > ss.ma_20 THEN '📈 多'
            ELSE '📉 整'
        END AS trend
    FROM strategy_signals ss
    INNER JOIN stocks s ON ss.stock_id = s.stock_id
    LEFT JOIN etf_stock_union esu ON ss.stock_id = esu.stock_id
),

scored_stocks AS (
    SELECT
        *,
        -- 綜合評分
        LEAST(pct_chg * 4, 40) +                    -- 漲幅分數
        LEAST(vol_ratio * 10, 30) +                 -- 量比分數
        CASE
            WHEN etf_count >= 2 THEN 20
            WHEN etf_count = 1 THEN 15
            ELSE 0
        END +                                        -- ETF 持有分數
        LEAST(volume::numeric / 1000000, 10) +      -- 流動性分數
        CASE WHEN ma_5 > ma_20 THEN 10 ELSE 0 END   -- 趨勢加分
        AS score
    FROM annotated_stocks
)

SELECT
    stock_id AS "代碼",
    stock_name AS "名稱",
    ROUND(close_price::numeric, 2) AS "收盤",
    pct_chg AS "漲%",
    ROUND(volume::numeric / 1000, 0) AS "量(張)",
    vol_ratio AS "量比",
    trend AS "趨勢",
    etf_status AS "ETF",
    etf_count AS "數",
    etf_list AS "ETF明細",
    ROUND(score::numeric, 1) AS "評分"
FROM scored_stocks
ORDER BY
    score DESC,
    pct_chg DESC
LIMIT 100;  -- 顯示前 100 名

-- ============================================================================
-- 📌 說明
-- ============================================================================
--
-- 與嚴格版的差異：
-- 1. 不要求「MA5 > MA20 > MA60」多頭排列
-- 2. 只要「收紅K + 站上MA5 + 量能放大」
-- 3. 流動性門檻降低：500張 → 300張，300張 → 100張
-- 4. 顯示前 100 名（嚴格版只有 25 檔）
--
-- 趨勢標註：
-- 📈 多 = MA5 > MA20（短期多頭）
-- 📉 整 = MA5 <= MA20（整理或空頭）
--
-- ============================================================================
