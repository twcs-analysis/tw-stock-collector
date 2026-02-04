-- ============================================================================
-- 📊 回頭買上漲策略 - 預備池（ETF 背書版）- 修正版
-- ============================================================================
--
-- 策略說明：
-- 1. 中期多頭趨勢（MA20 > MA60）
-- 2. 股價回測不破 MA20（允許 2% 震盪空間）
-- 3. 量能不能過度萎縮（≥ 80% 的 5 日均量）
-- 4. 當日不跌（允許小紅或平盤）
-- 5. ETF 持有加持（降低選股風險）
--
-- ============================================================================

WITH params AS (
    SELECT
        '2026-02-04'::date AS target_date,
        ('2026-02-04'::date - INTERVAL '120 days')::date AS start_date,
        1 AS min_etf_count
),

-- 📊 技術指標計算
all_indicators AS (
    SELECT
        sp.stock_id,
        sp.trade_date,
        sp.close_price,
        sp.volume,

        LAG(sp.close_price, 1) OVER w_stock AS prev_close,

        AVG(sp.close_price) OVER w_5d  AS ma_5,
        AVG(sp.close_price) OVER w_20d AS ma_20,
        AVG(sp.close_price) OVER w_60d AS ma_60,

        AVG(sp.volume) OVER w_5d  AS vol_ma5,
        AVG(sp.volume) OVER w_20d AS vol_ma20

    FROM stock_prices sp
    CROSS JOIN params
    WHERE sp.trade_date BETWEEN params.start_date AND params.target_date

    WINDOW
        w_stock AS (PARTITION BY sp.stock_id ORDER BY sp.trade_date),
        w_5d  AS (PARTITION BY sp.stock_id ORDER BY sp.trade_date ROWS BETWEEN 4 PRECEDING  AND CURRENT ROW),
        w_20d AS (PARTITION BY sp.stock_id ORDER BY sp.trade_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW),
        w_60d AS (PARTITION BY sp.stock_id ORDER BY sp.trade_date ROWS BETWEEN 59 PRECEDING AND CURRENT ROW)
),

-- 🎯 回頭買「預備池」條件
strategy_pool_b AS (
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

    -- ✅ 趨勢成立（中期多頭）
    AND ai.ma_20 > ai.ma_60

    -- ✅ 回測不破（允許 2% 震盪）
    AND ai.close_price >= ai.ma_20 * 0.98

    -- ✅ 量能不能太萎縮（至少 80% 的 5 日均量）
    AND ai.volume >= ai.vol_ma5 * 0.8

    -- ✅ 當日不跌（至少平盤或小紅）
    AND ai.close_price >= ai.prev_close

    -- ✅ 基本流動性
    AND ai.volume >= 300000
),

-- 🎯 ETF 背書
etf_filtered AS (
    SELECT
        b.*,
        s.stock_name,
        esu.etf_count,
        esu.total_weight
    FROM strategy_pool_b b
    INNER JOIN stocks s ON b.stock_id = s.stock_id
    INNER JOIN etf_stock_union esu ON b.stock_id = esu.stock_id
    CROSS JOIN params
    WHERE esu.etf_count >= params.min_etf_count
)

-- 📋 輸出
SELECT
    stock_id      AS "股票代碼",
    stock_name    AS "股票名稱",
    ROUND(close_price::numeric, 2) AS "收盤價",
    pct_chg       AS "漲跌幅%",
    ROUND(volume::numeric / 1000, 0) AS "成交量(張)",
    vol_ratio     AS "量比",
    etf_count     AS "ETF持有數",
    ROUND(total_weight::numeric, 2) AS "ETF總權重%",
    ROUND(ma_5::numeric, 2)  AS "MA5",
    ROUND(ma_20::numeric, 2) AS "MA20",
    ROUND(ma_60::numeric, 2) AS "MA60"
FROM etf_filtered
ORDER BY
    etf_count DESC,
    close_price / ma_20 ASC,   -- 越靠近 MA20 越像「回頭」
    vol_ratio DESC
LIMIT 30;

-- ============================================================================
-- 📌 使用說明
-- ============================================================================
--
-- 與嚴格版差異：
-- 1. 不要求 MA5 > MA20（允許短期回測）
-- 2. 不要求站上 MA5（允許在 MA20 附近震盪）
-- 3. 量能門檻從 1.2 倍降為 0.8 倍（不縮量即可）
-- 4. 允許平盤或小紅（不一定要大漲）
-- 5. 流動性降為 300 張（涵蓋更多中小型股）
--
-- 適用場景：
-- - 建立觀察預備池
-- - 尋找即將啟動的標的
-- - 中期趨勢確立，等待短期回測買點
--
-- ============================================================================
