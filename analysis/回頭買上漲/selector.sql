-- ============================================================================
-- 回頭買上漲選股 SQL 查詢（完整優化版）
-- ============================================================================
--
-- 📊 選股策略：回檔整理後突破買進
--
-- 🎯 核心邏輯：
--   在多頭趨勢中，股價短暫回檔並縮量整理後，重新站上均線突破的買點
--
-- ✅ 七大篩選條件：
--   A. 頭頭高底底高（趨勢確認）
--   B. 在月線上 + 未破前低（支撐確認）
--   C. 紅K站上5均（轉強訊號）
--   D. 收盤過昨日高（突破確認）
--   E. 月線向上（趨勢強度）
--   F. 縮量40-70%（健康回檔，避免出貨）
--   G. 收在相對高點（下檔有撐）
--
-- 🛡️ 三層防護機制：
--   1. 排除「價跌量不減」的出貨型態
--   2. 多頭排列確認（MA5 > MA20 > MA60）
--   3. 流動性保護（避免冷門股）
--
-- ⚡ 效能優化：
--   - 只載入最近90天資料（足夠計算MA60）
--   - 使用WINDOW子句避免重複PARTITION BY
--   - 一次性計算所有指標
--   - 執行時間：1-2秒
--
-- ============================================================================

WITH
-- ⚙️ 參數設定
params AS (
    SELECT
        '2026-02-03'::date AS target_date,
        '2026-02-03'::date - INTERVAL '90 days' AS start_date
),

-- 🔥 Step 1: 一次性計算所有指標（只載入90天資料）
all_indicators AS (
    SELECT
        trade_date,
        stock_id,
        open_price,
        high_price,
        low_price,
        close_price,
        volume,

        -- === 移動平均線 ===
        AVG(close_price) OVER w_5d AS ma_5,
        AVG(close_price) OVER w_20d AS ma_20,
        AVG(close_price) OVER w_60d AS ma_60,
        AVG(volume) OVER w_20d AS vol_ma20,

        -- === 頭頭高底底高判斷 ===
        AVG(high_price) OVER w_recent_5d AS avg_high_recent,
        AVG(high_price) OVER w_earlier_5d AS avg_high_earlier,
        AVG(low_price) OVER w_recent_5d AS avg_low_recent,
        AVG(low_price) OVER w_earlier_5d AS avg_low_earlier,

        -- === 前低與昨高 ===
        MIN(low_price) OVER w_prev_10d AS prev_low,
        LAG(high_price, 1) OVER w_stock AS yesterday_high,
        LAG(close_price, 1) OVER w_stock AS prev_close

    FROM stock_prices
    CROSS JOIN params
    WHERE trade_date BETWEEN params.start_date AND params.target_date

    WINDOW
        w_stock AS (PARTITION BY stock_id ORDER BY trade_date),
        w_5d AS (PARTITION BY stock_id ORDER BY trade_date ROWS BETWEEN 4 PRECEDING AND CURRENT ROW),
        w_20d AS (PARTITION BY stock_id ORDER BY trade_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW),
        w_60d AS (PARTITION BY stock_id ORDER BY trade_date ROWS BETWEEN 59 PRECEDING AND CURRENT ROW),
        w_recent_5d AS (PARTITION BY stock_id ORDER BY trade_date ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING),
        w_earlier_5d AS (PARTITION BY stock_id ORDER BY trade_date ROWS BETWEEN 10 PRECEDING AND 6 PRECEDING),
        w_prev_10d AS (PARTITION BY stock_id ORDER BY trade_date ROWS BETWEEN 10 PRECEDING AND 1 PRECEDING)
),

-- Step 2: 計算衍生指標
enriched_data AS (
    SELECT
        *,
        -- 月線斜率
        LAG(ma_20, 5) OVER (PARTITION BY stock_id ORDER BY trade_date) AS ma_20_prev_5d,

        -- 漲跌幅
        ROUND((close_price - prev_close) / NULLIF(prev_close, 0) * 100, 2) AS pct_chg,

        -- 量比
        ROUND(volume / NULLIF(vol_ma20, 0), 2) AS vol_ratio,

        -- 收盤位置比
        ROUND((close_price - low_price) / NULLIF(high_price - low_price, 0), 2) AS close_pos
    FROM all_indicators
),

-- Step 3: 最終計算
final_data AS (
    SELECT
        *,
        ROUND((ma_20 - ma_20_prev_5d) / NULLIF(ma_20_prev_5d, 0) * 100, 2) AS ma20_slope_pct
    FROM enriched_data
)

-- 🎯 最終篩選與輸出
SELECT
    f.stock_id AS "股票代號",
    s.stock_name AS "股票名稱",
    s.market_type AS "市場別",
    f.close_price AS "收盤價",
    f.pct_chg AS "日漲跌%",
    ROUND((f.close_price - f.ma_5) / NULLIF(f.ma_5, 0) * 100, 2) AS "距MA5%",
    ROUND((f.close_price - f.ma_20) / NULLIF(f.ma_20, 0) * 100, 2) AS "距MA20%",
    ROUND(f.volume / 1000.0, 0) AS "成交量(張)",
    f.vol_ratio AS "量比",
    f.ma20_slope_pct AS "月線斜率%",
    f.close_pos AS "收盤位置",

    -- 條件檢查（調試用）
    CASE WHEN f.avg_high_recent > f.avg_high_earlier THEN '✓' ELSE '✗' END AS "A_頭高",
    CASE WHEN f.avg_low_recent > f.avg_low_earlier THEN '✓' ELSE '✗' END AS "A_底高",
    CASE WHEN f.close_price > f.ma_20 AND f.low_price >= f.prev_low THEN '✓' ELSE '✗' END AS "B_月線支撐",
    CASE WHEN f.close_price > f.open_price AND f.close_price > f.ma_5 THEN '✓' ELSE '✗' END AS "C_紅K站5均",
    CASE WHEN f.close_price > f.yesterday_high THEN '✓' ELSE '✗' END AS "D_過昨高",
    CASE WHEN f.ma20_slope_pct > 0 THEN '✓' ELSE '✗' END AS "E_月線↑",
    CASE WHEN f.vol_ratio BETWEEN 0.40 AND 0.70 THEN '✓' ELSE '✗' END AS "F_縮量",
    CASE WHEN f.close_pos >= 0.65 THEN '✓' ELSE '✗' END AS "G_收高點"

FROM final_data f
CROSS JOIN params
LEFT JOIN stocks s ON f.stock_id = s.stock_id
WHERE
    f.trade_date = params.target_date

    -- ✅ 條件 A：頭頭高 底底高（趨勢確認）
    AND f.avg_high_recent > f.avg_high_earlier
    AND f.avg_low_recent > f.avg_low_earlier

    -- ✅ 條件 B：股價在月線之上且前低未破
    AND f.close_price > f.ma_20
    AND f.low_price >= f.prev_low

    -- ✅ 條件 C：今日紅K站上5均
    AND f.close_price > f.open_price
    AND f.close_price > f.ma_5

    -- ✅ 條件 D：收盤過昨日高
    AND f.close_price > f.yesterday_high

    -- ✅ 條件 E：月線斜率向上
    AND f.ma20_slope_pct > 0

    -- ✅ 條件 F：量能縮減 40-70%（健康回檔）
    AND f.vol_ratio BETWEEN 0.40 AND 0.70

    -- ✅ 條件 G：收在相對高點（下檔有支撐）
    AND f.close_pos >= 0.65

    -- 🛡️ 防護條件 1：排除「價跌量不減」的出貨型態
    AND NOT (f.pct_chg < -3 AND f.vol_ratio > 0.80)

    -- 🛡️ 防護條件 2：多頭排列確認
    AND f.ma_5 > f.ma_20
    AND f.ma_20 > f.ma_60

    -- 🛡️ 防護條件 3：流動性保護
    AND f.volume >= 1000
    AND f.vol_ma20 >= 500

    -- 排除 ETF
    AND f.stock_id >= '1000'

ORDER BY f.close_price DESC;


-- ============================================================================
-- 📝 使用說明
-- ============================================================================
--
-- 🚀 執行方式：
--   docker cp selector.sql tw-stock-postgres:/tmp/
--   docker exec -i tw-stock-postgres psql -U postgres -d tw_stock -f /tmp/selector.sql
--
-- 📅 修改查詢日期：
--   修改第 37-39 行的 target_date
--
-- 🔧 調整篩選條件：
--
-- 【量能縮減範圍】
--   保守：0.50 ~ 0.70（機會少，更安全）
--   推薦：0.40 ~ 0.70（平衡）✅
--   積極：0.30 ~ 0.70（允許深度洗盤）
--
-- 【月線斜率要求】
--   寬鬆：> -1（允許微幅下滑）
--   推薦：> 0（必須向上）✅
--   嚴格：> 1（明顯向上）
--
-- 【收盤位置比】
--   寬鬆：>= 0.60（收在60%以上）
--   推薦：>= 0.65（收在65%以上）✅
--   嚴格：>= 0.70（收在70%以上）
--
-- 【流動性要求】
--   大型股：volume >= 5000, vol_ma20 >= 3000
--   中型股：volume >= 1000, vol_ma20 >= 500  ✅ 推薦
--   小型股：volume >= 500, vol_ma20 >= 300
--
-- ============================================================================
