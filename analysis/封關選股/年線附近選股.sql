-- ============================================================================
-- 封關選股：年線附近安全選股策略
-- ============================================================================
--
-- 策略來源：錢線百分百技術面分析建議
-- 核心理念：「買在年線，睡得安穩」「年線是主力成本線」
--
-- 選股條件：
-- 1. 股價在年線（240MA）附近 (±3%)
-- 2. 年線向上或走平（斜率 ≥ 0）
-- 3. 排除下跌趨勢（股價未連續創新低）
-- 4. 成交量穩定（避免人氣太低）
-- 5. 產業趨勢向上（AI、金融、高股息）
--
-- 風險控管：
-- - 停損：跌破年線立即出場
-- - 資金：單一個股 < 15%
-- - 目標：反彈 10-20% 獲利了結
--
-- ============================================================================

WITH
-- Step 1: 取得最新交易日期
latest_date AS (
    SELECT MAX(trade_date) AS max_date
    FROM stock_analysis_daily
),

-- Step 2: 計算年線斜率（比較今日年線 vs 5 天前年線）
ma240_slope AS (
    SELECT
        ti1.stock_id,
        ti1.trade_date,
        ti1.ma_240 AS current_ma240,
        ti2.ma_240 AS prev_ma240,
        -- 年線斜率 = (今日年線 - 5日前年線) / 5日前年線
        CASE
            WHEN ti2.ma_240 > 0 THEN
                (ti1.ma_240 - ti2.ma_240) / ti2.ma_240 * 100
            ELSE 0
        END AS ma240_slope_pct
    FROM stock_analysis_daily ti1
    LEFT JOIN stock_analysis_daily ti2
        ON ti1.stock_id = ti2.stock_id
        AND ti2.trade_date = ti1.trade_date - INTERVAL '5 days'
    CROSS JOIN latest_date
    WHERE ti1.trade_date = latest_date.max_date
        AND ti1.ma_240 IS NOT NULL
),

-- Step 3: 檢查是否為下跌趨勢（比較近 10 天的低點）
downtrend_check_temp AS (
    SELECT
        stock_id,
        trade_date,
        low_price,
        LAG(low_price) OVER (PARTITION BY stock_id ORDER BY trade_date) AS prev_low_price
    FROM stock_analysis_daily
    CROSS JOIN latest_date
    WHERE trade_date >= latest_date.max_date - INTERVAL '10 days'
        AND trade_date <= latest_date.max_date
),
downtrend_check AS (
    SELECT
        stock_id,
        COUNT(*) AS total_days,
        SUM(CASE WHEN low_price < prev_low_price THEN 1 ELSE 0 END) AS new_low_count
    FROM downtrend_check_temp
    GROUP BY stock_id
),

-- Step 4: 主查詢 - 篩選年線附近的股票
target_stocks AS (
    SELECT
        ti.stock_id,
        sp.stock_name,
        ti.trade_date,
        ti.close_price AS close,
        ti.open_price AS open,
        ti.high_price AS high,
        ti.low_price AS low,
        ti.volume,
        ti.ma_5,
        ti.ma_20,
        ti.ma_60,
        ti.ma_240,
        slope.ma240_slope_pct,
        ti.rsi_14,
        ti.macd_dif,
        ti.macd_dea,
        ti.vol_ma20,
        ti.vol_ratio,
        -- 計算股價與年線的比率
        ROUND((ti.close_price / NULLIF(ti.ma_240, 0)) * 100, 2) AS price_to_ma240_pct,
        -- 計算距離年線的百分比
        ROUND(((ti.close_price - ti.ma_240) / NULLIF(ti.ma_240, 0)) * 100, 2) AS distance_to_ma240_pct,
        dt.new_low_count,
        dt.total_days
    FROM stock_analysis_daily ti
    LEFT JOIN stocks sp
        ON ti.stock_id = sp.stock_id
    LEFT JOIN ma240_slope slope
        ON ti.stock_id = slope.stock_id
        AND ti.trade_date = slope.trade_date
    LEFT JOIN downtrend_check dt
        ON ti.stock_id = dt.stock_id
    CROSS JOIN latest_date
    WHERE
        ti.trade_date = latest_date.max_date
        AND ti.ma_240 IS NOT NULL
        AND ti.ma_240 > 0
),

-- Step 5: 應用篩選條件
filtered_stocks AS (
    SELECT
        stock_id,
        stock_name,
        close,
        ma_240,
        price_to_ma240_pct,
        distance_to_ma240_pct,
        ma240_slope_pct,
        rsi_14,
        macd_dif,
        macd_dea,
        volume,
        vol_ma20,
        vol_ratio,
        new_low_count,
        total_days
    FROM target_stocks
    WHERE
        -- 1. 股價在年線 ±3% 範圍內
        price_to_ma240_pct >= 97
        AND price_to_ma240_pct <= 103

        -- 2. 年線向上或走平（斜率 >= -0.5%，允許小幅下降）
        AND ma240_slope_pct >= -0.5

        -- 3. 排除嚴重下跌趨勢（10天內創新低次數 < 6 次）
        AND (new_low_count IS NULL OR new_low_count < 6)

        -- 4. 成交量穩定（大於 20 日均量的 50%）
        AND volume > vol_ma20 * 0.5

        -- 5. 排除 ETF 和小型股
        AND stock_id::int >= 1000
        AND volume > 500000

        -- 6. 股價 > 10 元（排除雞蛋水餃股）
        AND close > 10
),

-- Step 6: 計算安全評分
scored_stocks AS (
    SELECT
        stock_id,
        stock_name,
        close,
        ma_240,
        distance_to_ma240_pct,
        ma240_slope_pct,
        rsi_14,
        macd_dif - macd_dea AS macd_diff,
        vol_ratio,
        -- 評分項目
        -- 1. 距離年線評分（越接近年線分數越高）
        (100 - ABS(distance_to_ma240_pct) * 10) AS distance_score,
        -- 2. 年線斜率評分（向上 > 走平 > 向下）
        CASE
            WHEN ma240_slope_pct > 1 THEN 100
            WHEN ma240_slope_pct > 0 THEN 80
            WHEN ma240_slope_pct > -0.5 THEN 50
            ELSE 20
        END AS slope_score,
        -- 3. RSI 評分（30-50 為佳，準備反彈）
        CASE
            WHEN rsi_14 BETWEEN 30 AND 50 THEN 100
            WHEN rsi_14 BETWEEN 50 AND 60 THEN 80
            WHEN rsi_14 BETWEEN 20 AND 30 THEN 60
            ELSE 40
        END AS rsi_score,
        -- 4. MACD 評分（接近黃金交叉）
        CASE
            WHEN macd_dif > macd_dea AND (macd_dif - macd_dea) < 0.5 THEN 100
            WHEN macd_dif > macd_dea THEN 80
            WHEN (macd_dea - macd_dif) < 0.2 THEN 60
            ELSE 40
        END AS macd_score,
        -- 5. 成交量評分（量縮為佳）
        CASE
            WHEN vol_ratio BETWEEN 0.5 AND 0.8 THEN 100
            WHEN vol_ratio BETWEEN 0.8 AND 1.2 THEN 80
            WHEN vol_ratio > 1.2 THEN 60
            ELSE 40
        END AS vol_score
    FROM filtered_stocks
)

-- Step 7: 最終結果輸出
SELECT
    stock_id AS "股票代號",
    stock_name AS "股票名稱",
    ROUND(close, 2) AS "收盤價",
    ROUND(ma_240, 2) AS "年線(240MA)",
    distance_to_ma240_pct AS "距離年線(%)",
    ROUND(ma240_slope_pct, 2) AS "年線斜率(%)",
    ROUND(rsi_14, 2) AS "RSI(14)",
    ROUND(macd_diff, 4) AS "MACD差值",
    ROUND(vol_ratio, 2) AS "量比",
    -- 綜合評分（加權平均）
    ROUND(
        distance_score * 0.3 +  -- 距離年線權重 30%
        slope_score * 0.25 +     -- 年線斜率權重 25%
        rsi_score * 0.2 +        -- RSI 權重 20%
        macd_score * 0.15 +      -- MACD 權重 15%
        vol_score * 0.1,         -- 成交量權重 10%
        2
    ) AS "安全評分",
    -- 推薦操作
    CASE
        WHEN distance_to_ma240_pct > 0 THEN '站上年線，可考慮'
        WHEN distance_to_ma240_pct BETWEEN -1 AND 0 THEN '接近年線，觀察'
        WHEN distance_to_ma240_pct BETWEEN -3 AND -1 THEN '回測年線，優質'
        ELSE '略低於年線，等待'
    END AS "操作建議",
    -- 風險等級
    CASE
        WHEN ma240_slope_pct > 1 AND rsi_14 < 50 THEN '低風險'
        WHEN ma240_slope_pct > 0 THEN '中低風險'
        WHEN ma240_slope_pct > -0.5 THEN '中等風險'
        ELSE '偏高風險'
    END AS "風險等級",
    -- 停損參考
    ROUND(ma_240 * 0.97, 2) AS "建議停損價",
    -- 目標價參考（年線 +10%）
    ROUND(ma_240 * 1.10, 2) AS "目標價(保守)",
    ROUND(ma_240 * 1.20, 2) AS "目標價(積極)"
FROM scored_stocks
ORDER BY
    (
        distance_score * 0.3 +
        slope_score * 0.25 +
        rsi_score * 0.2 +
        macd_score * 0.15 +
        vol_score * 0.1
    ) DESC,
    distance_to_ma240_pct ASC  -- 距離年線越近越優先
LIMIT 30;


-- ============================================================================
-- 簡化版查詢（快速篩選）
-- ============================================================================

-- 註解掉簡化版，執行完整版即可
/*
SELECT
    ti.stock_id AS "股票代號",
    sp.stock_name AS "股票名稱",
    ROUND(ti.close_price, 2) AS "收盤價",
    ROUND(ti.ma_240, 2) AS "年線",
    ROUND(((ti.close_price / ti.ma_240) - 1) * 100, 2) AS "距離年線(%)",
    ROUND(ti.rsi_14, 2) AS "RSI",
    ROUND(ti.vol_ratio, 2) AS "量比"
FROM stock_analysis_daily ti
LEFT JOIN stocks sp
    ON ti.trade_date = sp.trade_date
    AND ti.stock_id = sp.stock_id
WHERE
    ti.trade_date = (SELECT MAX(trade_date) FROM stock_analysis_daily)
    AND ti.close_price / ti.ma_240 BETWEEN 0.97 AND 1.03
    AND ti.ma_240 > 0
    AND ti.stock_id >= 1000
    AND ti.volume > 500000
ORDER BY ABS((ti.close_price / ti.ma_240) - 1) ASC
LIMIT 30;
*/


-- ============================================================================
-- 使用說明
-- ============================================================================
--
-- 1. 執行查詢：
--    psql-17 -U postgres -d tw_stock -f "analysis/封關選股/年線附近選股.sql"
--
-- 2. 設定密碼（如需要）：
--    export PGPASSWORD=your_password
--    psql-17 -U postgres -d tw_stock -f "analysis/封關選股/年線附近選股.sql"
--
-- 3. 輸出到檔案：
--    psql-17 -U postgres -d tw_stock -f "analysis/封關選股/年線附近選股.sql" > result.txt
--
-- 4. 調整條件（修改 WHERE 子句）：
--    - 年線範圍：price_to_ma240_pct >= 97 AND <= 103
--    - 年線斜率：ma240_slope_pct >= -0.5
--    - 成交量門檻：volume > 500000
--    - 結果數量：LIMIT 30
--
-- 5. 評分權重調整（修改綜合評分公式）：
--    - distance_score * 0.3   (距離年線)
--    - slope_score * 0.25     (年線斜率)
--    - rsi_score * 0.2        (RSI)
--    - macd_score * 0.15      (MACD)
--    - vol_score * 0.1        (成交量)
--
-- ============================================================================
--
-- 策略說明：
--
-- 【買進時機】
-- 1. 股價回測年線（距離 -1% ~ -3%）
-- 2. 年線向上（斜率 > 0）
-- 3. RSI < 50（尚未超買）
-- 4. 量能萎縮（賣壓減輕）
--
-- 【停損點】
-- - 跌破年線 3%（約 ma_240 * 0.97）
-- - 或跌破年線後連續 2 天無法站回
--
-- 【停利點】
-- - 保守：年線 +10%（風險報酬比 1:3）
-- - 積極：年線 +20%（風險報酬比 1:6）
-- - 動態：獲利 10% 先賣 1/2，鎖住利潤
--
-- 【資金配置】
-- - 單一個股：< 15% 總資金
-- - 分散投資：5-8 檔股票
-- - 保留現金：至少 20%
--
-- 【節目金句】
-- "買在年線，睡得安穩"
-- "年線是主力的成本線，不會輕易放棄"
-- "跌破年線就走，不要猶豫"
--
-- ============================================================================
