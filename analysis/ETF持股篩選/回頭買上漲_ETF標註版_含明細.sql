-- ============================================================================
-- 📊 回頭買上漲選股策略 + ETF 持股標註版（含 ETF 明細）(2026-02-05)
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
        AVG(sp.close_price) OVER w_20d AS ma_20,
        AVG(sp.close_price) OVER w_60d AS ma_60,
        AVG(sp.volume) OVER w_5d AS vol_ma5
    FROM stock_prices sp
    CROSS JOIN params
    WHERE sp.trade_date BETWEEN params.start_date AND params.target_date
    WINDOW
        w_stock AS (PARTITION BY sp.stock_id ORDER BY sp.trade_date),
        w_5d AS (PARTITION BY sp.stock_id ORDER BY sp.trade_date ROWS BETWEEN 4 PRECEDING AND CURRENT ROW),
        w_20d AS (PARTITION BY sp.stock_id ORDER BY sp.trade_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW),
        w_60d AS (PARTITION BY sp.stock_id ORDER BY sp.trade_date ROWS BETWEEN 59 PRECEDING AND CURRENT ROW)
),

strategy_signals AS (
    SELECT
        ai.stock_id,
        ai.close_price,
        ai.volume,
        ai.ma_5,
        ai.ma_20,
        ai.ma_60,
        ROUND((ai.close_price - ai.prev_close) / NULLIF(ai.prev_close, 0) * 100, 2) AS pct_chg,
        ROUND(ai.volume::numeric / NULLIF(ai.vol_ma5, 0), 2) AS vol_ratio
    FROM all_indicators ai
    CROSS JOIN params
    WHERE ai.trade_date = params.target_date
        AND ai.close_price > ai.ma_5
        AND ai.ma_5 > ai.ma_20
        AND ai.ma_20 > ai.ma_60
        AND ai.volume > ai.vol_ma5 * 1.2
        AND (ai.close_price - ai.prev_close) / NULLIF(ai.prev_close, 0) > 0
        AND ai.volume >= 500000
        AND ai.vol_ma5 >= 300000
),

-- 彙整 ETF 持股明細
etf_details AS (
    SELECT
        eh.stock_id,
        STRING_AGG(
            e.etf_name || '(' || ROUND(eh.weight::numeric, 2) || '%)',
            ', '
            ORDER BY eh.weight DESC
        ) AS etf_list
    FROM etf_holdings eh
    JOIN etfs e ON eh.etf_id = e.etf_id
    GROUP BY eh.stock_id
),

annotated_stocks AS (
    SELECT
        ss.*,
        s.stock_name,
        COALESCE(esu.etf_count, 0) AS etf_count,
        COALESCE(esu.total_weight, 0) AS total_weight,
        COALESCE(ed.etf_list, '-') AS etf_list,
        CASE
            WHEN esu.etf_count IS NULL THEN '❌'
            WHEN esu.etf_count >= 2 THEN '✅✅'
            ELSE '✅'
        END AS etf_status,
        -- 綜合評分
        LEAST(ss.pct_chg * 4, 40) +
        LEAST(ss.vol_ratio * 10, 30) +
        CASE
            WHEN esu.etf_count >= 2 THEN 20
            WHEN esu.etf_count = 1 THEN 15
            ELSE 0
        END +
        LEAST(ss.volume::numeric / 1000000, 10) AS score
    FROM strategy_signals ss
    INNER JOIN stocks s ON ss.stock_id = s.stock_id
    LEFT JOIN etf_stock_union esu ON ss.stock_id = esu.stock_id
    LEFT JOIN etf_details ed ON ss.stock_id = ed.stock_id
)

SELECT
    stock_id AS "代碼",
    stock_name AS "名稱",
    ROUND(close_price::numeric, 2) AS "收盤",
    pct_chg AS "漲%",
    ROUND(volume::numeric / 1000, 0) AS "量(張)",
    vol_ratio AS "量比",
    etf_status AS "ETF",
    etf_count AS "數",
    ROUND(total_weight::numeric, 2) AS "權重%",
    etf_list AS "ETF明細",
    ROUND(score::numeric, 1) AS "評分"
FROM annotated_stocks
ORDER BY
    score DESC,
    etf_count DESC,
    pct_chg DESC
LIMIT 30;
