-- ============================================================================
-- 多策略綜合選股 SQL 查詢
-- ============================================================================
--
-- 包含三種策略類型：
-- 1. 強勢多頭（適合積極投資者）
-- 2. 穩健多頭（適合穩健投資者）
-- 3. 突破型（適合短線交易者）
--
-- 資料表：technical_indicators
-- 輸出：三種策略的推薦標的清單，並計算綜合評分
--
-- ============================================================================

WITH
-- Step 1: 載入目標日期的技術指標資料
target_data AS (
    SELECT
        ti.trade_date,
        ti.stock_id,
        sp.stock_name,
        ti.open_price AS open,
        ti.high_price AS high,
        ti.low_price AS low,
        ti.close_price AS close,
        ti.volume,
        ti.ma_5,
        ti.ma_10,
        ti.ma_20,
        ti.ma_60,
        ti.rsi_6,
        ti.rsi_14,
        ti.macd_dif,
        ti.macd_dea,
        ti.macd_hist,
        ti.dmi_pdi,
        ti.dmi_mdi,
        ti.dmi_adx,
        ti.bb_upper,
        ti.bb_mid,
        ti.bb_lower,
        ti.vol_ma5,
        ti.vol_ma20,
        ti.vol_ratio,
        ti.vwap
    FROM technical_indicators ti
    LEFT JOIN stock_prices sp
        ON ti.trade_date = sp.trade_date
        AND ti.stock_id = sp.stock_id
    WHERE ti.trade_date = '2026-02-02'
),

-- Step 2: 策略一 - 強勢多頭
strong_bullish AS (
    SELECT
        stock_id,
        stock_name,
        close,
        ma_5,
        ma_10,
        ma_20,
        rsi_14,
        macd_hist,
        dmi_adx,
        dmi_pdi,
        dmi_mdi,
        vol_ratio,
        '強勢多頭' AS strategy_type
    FROM target_data
    WHERE
        -- 均線完整多頭排列（MA5 > MA10 > MA20）
        close > ma_5
        AND ma_5 > ma_10
        AND ma_10 > ma_20

        -- RSI 強勢區間（60-75）
        AND rsi_14 >= 60
        AND rsi_14 <= 75

        -- MACD 黃金交叉且柱狀圖強勁（> 0.05）
        AND macd_dif > macd_dea
        AND macd_hist > 0.05

        -- ADX > 30（趨勢非常強勁）
        AND dmi_adx > 30

        -- +DI 明顯大於 -DI（多頭力道強，差距 > 15）
        AND dmi_pdi > dmi_mdi + 15

        -- 價格在布林通道中軌之上
        AND close > bb_mid

        -- 成交量放大（量比 > 1.3）
        AND vol_ratio > 1.3

        -- 排除 ETF 和小型股
        AND stock_id >= 1000
        AND volume > 1000000
),

-- Step 3: 策略二 - 穩健多頭
steady_bullish AS (
    SELECT
        stock_id,
        stock_name,
        close,
        ma_5,
        ma_10,
        ma_20,
        rsi_14,
        macd_hist,
        dmi_adx,
        dmi_pdi,
        dmi_mdi,
        vol_ratio,
        '穩健多頭' AS strategy_type
    FROM target_data
    WHERE
        -- 均線多頭排列（收盤 > MA5 > MA20）
        close > ma_5
        AND ma_5 > ma_20

        -- RSI 中性偏強（50-65）
        AND rsi_14 >= 50
        AND rsi_14 <= 65

        -- MACD 黃金交叉
        AND macd_dif > macd_dea
        AND macd_hist > 0

        -- ADX > 25（趨勢明確）
        AND dmi_adx > 25

        -- +DI > -DI
        AND dmi_pdi > dmi_mdi

        -- 價格在布林通道中上軌（中軌到上軌之間）
        AND close > bb_mid
        AND close < bb_upper

        -- 成交量適中（量比 > 1.0）
        AND vol_ratio > 1.0

        -- 排除 ETF 和小型股
        AND stock_id >= 1000
        AND volume > 1000000
),

-- Step 4: 策略三 - 突破型
breakout AS (
    SELECT
        stock_id,
        stock_name,
        close,
        ma_5,
        ma_10,
        ma_20,
        rsi_14,
        macd_hist,
        dmi_adx,
        dmi_pdi,
        dmi_mdi,
        vol_ratio,
        '突破型' AS strategy_type
    FROM target_data
    WHERE
        -- 價格突破 MA20
        AND close > ma_20

        -- RSI 快速上升（55-70）
        AND rsi_14 >= 55
        AND rsi_14 <= 70

        -- MACD 剛黃金交叉（柱狀圖 0-0.3）
        AND macd_dif > macd_dea
        AND macd_hist > 0
        AND macd_hist < 0.3

        -- ADX 上升中（20-35）
        AND dmi_adx > 20
        AND dmi_adx < 35

        -- +DI 快速上升（差距 > 10）
        AND dmi_pdi > dmi_mdi + 10

        -- 突破布林通道中軌
        AND close > bb_mid

        -- 大量突破（量比 > 1.5）
        AND vol_ratio > 1.5

        -- 排除 ETF 和小型股
        AND stock_id >= 1000
        AND volume > 1000000
),

-- Step 5: 合併所有策略
all_strategies AS (
    SELECT * FROM strong_bullish
    UNION ALL
    SELECT * FROM steady_bullish
    UNION ALL
    SELECT * FROM breakout
),

-- Step 6: 計算評分
scored_strategies AS (
    SELECT
        stock_id,
        stock_name,
        close,
        ma_5,
        ma_20,
        rsi_14,
        macd_hist,
        dmi_adx,
        dmi_pdi,
        dmi_mdi,
        vol_ratio,
        strategy_type,
        -- RSI 評分（越接近 60 越好）
        100 - ABS(rsi_14 - 60) AS rsi_score,
        -- MACD 評分
        macd_hist * 20 AS macd_score,
        -- ADX 評分
        dmi_adx AS adx_score,
        -- 多頭力道評分
        (dmi_pdi - dmi_mdi) AS dmi_score,
        -- 成交量評分
        (vol_ratio - 1) * 30 AS vol_score,
        -- 均線排列評分
        ((ma_5 - ma_20) / ma_20) * 100 AS ma_score
    FROM all_strategies
)

-- Step 7: 計算總分並輸出
SELECT
    ROW_NUMBER() OVER (PARTITION BY strategy_type ORDER BY total_score DESC) AS "排名",
    strategy_type AS "策略類型",
    stock_id AS "股票代號",
    stock_name AS "股票名稱",
    ROUND(close, 2) AS "收盤價",
    ROUND(rsi_14, 2) AS "RSI(14)",
    ROUND(macd_hist, 4) AS "MACD柱狀圖",
    ROUND(dmi_adx, 2) AS "ADX",
    ROUND(dmi_pdi - dmi_mdi, 2) AS "多頭力道",
    ROUND(vol_ratio, 2) AS "量比",
    ROUND(total_score, 2) AS "綜合評分"
FROM (
    SELECT
        *,
        -- 綜合評分（加權平均）
        (
            rsi_score * 0.15 +
            macd_score * 0.20 +
            adx_score * 0.20 +
            dmi_score * 0.20 +
            vol_score * 0.15 +
            ma_score * 0.10
        ) AS total_score
    FROM scored_strategies
) AS final_scores
WHERE ROW_NUMBER() OVER (PARTITION BY strategy_type ORDER BY total_score DESC) <= 5
ORDER BY strategy_type, total_score DESC;


-- ============================================================================
-- 策略摘要統計
-- ============================================================================

WITH
target_data AS (
    SELECT
        ti.trade_date,
        ti.stock_id,
        sp.stock_name,
        ti.close_price AS close,
        ti.volume,
        ti.ma_5,
        ti.ma_10,
        ti.ma_20,
        ti.rsi_14,
        ti.macd_dif,
        ti.macd_dea,
        ti.macd_hist,
        ti.dmi_pdi,
        ti.dmi_mdi,
        ti.dmi_adx,
        ti.bb_upper,
        ti.bb_mid,
        ti.bb_lower,
        ti.vol_ratio
    FROM technical_indicators ti
    LEFT JOIN stock_prices sp
        ON ti.trade_date = sp.trade_date
        AND ti.stock_id = sp.stock_id
    WHERE ti.trade_date = '2026-02-02'
)

SELECT
    '強勢多頭' AS "策略類型",
    COUNT(*) AS "符合條件檔數",
    LEAST(5, COUNT(*)) AS "推薦標的數"
FROM target_data
WHERE
    close > ma_5 AND ma_5 > ma_10 AND ma_10 > ma_20
    AND rsi_14 >= 60 AND rsi_14 <= 75
    AND macd_dif > macd_dea AND macd_hist > 0.05
    AND dmi_adx > 30
    AND dmi_pdi > dmi_mdi + 15
    AND close > bb_mid
    AND vol_ratio > 1.3
    AND stock_id >= 1000
    AND volume > 1000000

UNION ALL

SELECT
    '穩健多頭' AS "策略類型",
    COUNT(*) AS "符合條件檔數",
    LEAST(5, COUNT(*)) AS "推薦標的數"
FROM target_data
WHERE
    close > ma_5 AND ma_5 > ma_20
    AND rsi_14 >= 50 AND rsi_14 <= 65
    AND macd_dif > macd_dea AND macd_hist > 0
    AND dmi_adx > 25
    AND dmi_pdi > dmi_mdi
    AND close > bb_mid AND close < bb_upper
    AND vol_ratio > 1.0
    AND stock_id >= 1000
    AND volume > 1000000

UNION ALL

SELECT
    '突破型' AS "策略類型",
    COUNT(*) AS "符合條件檔數",
    LEAST(5, COUNT(*)) AS "推薦標的數"
FROM target_data
WHERE
    close > ma_20
    AND rsi_14 >= 55 AND rsi_14 <= 70
    AND macd_dif > macd_dea AND macd_hist > 0 AND macd_hist < 0.3
    AND dmi_adx > 20 AND dmi_adx < 35
    AND dmi_pdi > dmi_mdi + 10
    AND close > bb_mid
    AND vol_ratio > 1.5
    AND stock_id >= 1000
    AND volume > 1000000;


-- ============================================================================
-- 使用範例
-- ============================================================================
--
-- 1. 執行完整查詢（需要 technical_indicators 表）：
--    psql -U postgres -d tw_stock -f multi_strategy_selector.sql
--
-- 2. 修改目標日期：
--    將所有 '2026-02-02' 替換為目標日期
--
-- 3. 調整推薦數量：
--    修改 WHERE ROW_NUMBER() ... <= 5 的數字
--
-- 4. 調整評分權重：
--    修改綜合評分的權重比例
--
-- 5. 調整策略條件：
--    修改各策略的 WHERE 子句條件
--
-- ============================================================================
