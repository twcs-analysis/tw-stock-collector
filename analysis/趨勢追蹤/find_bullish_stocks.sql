-- ============================================================================
-- 多頭市場技術分析選股 SQL 查詢
-- ============================================================================
--
-- 選股條件：
-- 1. 價格在均線之上（多頭排列）
-- 2. RSI 在 50-70 之間（強勢但未超買）
-- 3. MACD 黃金交叉（DIF > DEA）且柱狀圖為正
-- 4. ADX > 25（趨勢強勁）
-- 5. 價格在布林通道中上軌
-- 6. 成交量大於 20 日均量（活躍）
--
-- 資料表：technical_indicators（假設已包含所有技術指標）
-- 如果技術指標尚未計算，請先使用 services/transformers/technical_indicators_calculator.py
--
-- ============================================================================

WITH
-- Step 1: 從技術指標資料中篩選目標日期
target_date_data AS (
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
    WHERE ti.trade_date = '2026-01-30'
),

-- Step 2: 篩選符合多頭條件的股票
bullish_stocks AS (
    SELECT
        stock_id,
        stock_name,
        close,
        open,
        high,
        low,
        ma_5,
        ma_10,
        ma_20,
        ma_60,
        rsi_14,
        macd_dif,
        macd_dea,
        macd_hist,
        dmi_pdi,
        dmi_mdi,
        dmi_adx,
        bb_upper,
        bb_mid,
        bb_lower,
        volume,
        vol_ma20,
        vol_ratio,
        vwap
    FROM target_date_data
    WHERE
        -- 1. 均線多頭排列：收盤價 > MA5 > MA20
        close > ma_5
        AND ma_5 > ma_20

        -- 2. RSI 強勢但未超買（50-70）
        AND rsi_14 > 50
        AND rsi_14 < 70

        -- 3. MACD 黃金交叉（DIF > DEA）且柱狀圖為正
        AND macd_dif > macd_dea
        AND macd_hist > 0

        -- 4. ADX 趨勢強勁（> 25）
        AND dmi_adx > 25

        -- 5. +DI > -DI（多頭趨勢）
        AND dmi_pdi > dmi_mdi

        -- 6. 價格在布林通道中上軌（中線到上軌之間）
        AND close > bb_mid
        AND close < bb_upper

        -- 7. 成交量活躍（大於 20 日均量）
        AND volume > vol_ma20

        -- 8. 排除 ETF（代碼以 0 開頭）和小型股（成交量低於 100 萬）
        AND stock_id >= 1000
        AND volume > 1000000
),

-- Step 3: 計算綜合評分
scored_stocks AS (
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
        -- RSI 評分（越接近 60 越好）
        100 - ABS(rsi_14 - 60) AS rsi_score,
        -- MACD 評分
        macd_hist * 10 AS macd_score,
        -- ADX 評分
        dmi_adx AS adx_score,
        -- 多頭力道評分
        (dmi_pdi - dmi_mdi) AS dmi_score,
        -- 成交量評分
        (vol_ratio - 1) * 50 AS vol_score
    FROM bullish_stocks
)

-- Step 4: 計算總分並排序
SELECT
    stock_id AS "股票代號",
    stock_name AS "股票名稱",
    close AS "收盤價",
    ROUND(ma_5, 2) AS "MA5",
    ROUND(ma_20, 2) AS "MA20",
    ROUND(rsi_14, 2) AS "RSI(14)",
    ROUND(macd_hist, 4) AS "MACD柱狀圖",
    ROUND(dmi_adx, 2) AS "ADX",
    ROUND(dmi_pdi - dmi_mdi, 2) AS "多頭力道",
    ROUND(vol_ratio, 2) AS "量比",
    -- 綜合評分（加權平均）
    ROUND(
        rsi_score * 0.2 +
        macd_score * 0.2 +
        adx_score * 0.2 +
        dmi_score * 0.2 +
        vol_score * 0.2,
        2
    ) AS "綜合評分",
    -- 狀態描述
    CASE
        WHEN rsi_14 > 60 THEN '強勢'
        ELSE '偏強'
    END AS "RSI狀態",
    CASE
        WHEN dmi_adx > 30 THEN '強勁'
        ELSE '中等'
    END AS "趨勢狀態",
    CASE
        WHEN vol_ratio > 1.2 THEN '放量'
        ELSE '正常'
    END AS "成交量狀態"
FROM scored_stocks
ORDER BY
    (
        rsi_score * 0.2 +
        macd_score * 0.2 +
        adx_score * 0.2 +
        dmi_score * 0.2 +
        vol_score * 0.2
    ) DESC
LIMIT 10;


-- ============================================================================
-- 簡化版查詢（僅顯示關鍵資訊）
-- ============================================================================

SELECT
    ti.stock_id AS "股票代號",
    sp.stock_name AS "股票名稱",
    ti.close_price AS "收盤價",
    ROUND(ti.ma_5, 2) AS "MA5",
    ROUND(ti.ma_20, 2) AS "MA20",
    ROUND(ti.rsi_14, 2) AS "RSI(14)",
    ROUND(ti.dmi_adx, 2) AS "ADX",
    ROUND(ti.vol_ratio, 2) AS "量比"
FROM technical_indicators ti
LEFT JOIN stock_prices sp
    ON ti.trade_date = sp.trade_date
    AND ti.stock_id = sp.stock_id
WHERE
    ti.trade_date = '2026-01-30'
    AND ti.close_price > ti.ma_5
    AND ti.ma_5 > ti.ma_20
    AND ti.rsi_14 > 50
    AND ti.rsi_14 < 70
    AND ti.macd_dif > ti.macd_dea
    AND ti.macd_hist > 0
    AND ti.dmi_adx > 25
    AND ti.dmi_pdi > ti.dmi_mdi
    AND ti.close_price > ti.bb_mid
    AND ti.close_price < ti.bb_upper
    AND ti.volume > ti.vol_ma20
    AND ti.stock_id >= 1000
    AND ti.volume > 1000000
ORDER BY ti.close_price DESC
LIMIT 10;


-- ============================================================================
-- 使用範例
-- ============================================================================
--
-- 1. 執行完整查詢（需要 technical_indicators 表）：
--    psql -U postgres -d tw_stock -f find_bullish_stocks.sql
--
-- 2. 修改目標日期：
--    將所有 '2026-01-30' 替換為目標日期
--
-- 3. 調整篩選條件：
--    - RSI 範圍：修改 rsi_14 > 50 AND rsi_14 < 70
--    - ADX 門檻：修改 dmi_adx > 25
--    - 成交量門檻：修改 volume > 1000000
--
-- 4. 調整評分權重：
--    修改綜合評分的權重（目前各佔 20%）
--
-- ============================================================================
