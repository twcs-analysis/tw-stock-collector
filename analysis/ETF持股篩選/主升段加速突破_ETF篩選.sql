-- ============================================================================
-- 📊 主升段加速突破選股策略 + ETF 持股篩選
-- ============================================================================
--
-- 策略說明：
-- 1. 使用「主升段加速突破」策略篩選符合條件的股票
-- 2. 再篩選出被 ETF 持有的標的（提高流動性與機構認可度）
-- 3. 可選擇篩選條件：
--    - 被至少 1 個 ETF 持有
--    - 被至少 2 個 ETF 持有（更穩健）
--    - ETF 總權重 > 某個門檻
--
-- ============================================================================

-- 📅 參數設定
WITH params AS (
    SELECT
        '2026-02-04'::date AS target_date,  -- 查詢日期
        ('2026-02-04'::date - INTERVAL '90 days')::date AS start_date,  -- 90天窗口
        1 AS min_etf_count  -- 最少被幾個 ETF 持有（可調整為 2, 3...）
),

-- 📊 計算所有技術指標
all_indicators AS (
    SELECT
        sp.stock_id,
        sp.trade_date,
        sp.open_price,
        sp.high_price,
        sp.low_price,
        sp.close_price,
        sp.volume,

        -- 計算日漲跌幅
        LAG(sp.close_price) OVER w_stock AS prev_close,
        ROUND(
            (sp.close_price - LAG(sp.close_price) OVER w_stock) /
            NULLIF(LAG(sp.close_price) OVER w_stock, 0) * 100,
            2
        ) AS pct_chg,

        -- 均線系統
        AVG(sp.close_price) OVER w_5d AS ma_5,
        AVG(sp.close_price) OVER w_20d AS ma_20,
        AVG(sp.close_price) OVER w_60d AS ma_60,

        -- 量能指標
        AVG(sp.volume) OVER w_20d AS vol_ma20,
        ROUND(
            sp.volume::numeric / NULLIF(AVG(sp.volume) OVER w_20d, 0),
            2
        ) AS vol_ratio,

        -- 收盤位置（日內強度）
        CASE
            WHEN sp.high_price - sp.low_price > 0 THEN
                ROUND(
                    (sp.close_price - sp.low_price) /
                    NULLIF(sp.high_price - sp.low_price, 0),
                    2
                )
            ELSE 0
        END AS close_position,

        -- 20日最高價
        MAX(sp.high_price) OVER w_20d AS high_20d,

        -- 60日最高價與最低價（計算漲幅）
        MAX(sp.high_price) OVER w_60d AS high_60d,
        MIN(sp.low_price) OVER w_60d AS low_60d

    FROM stock_prices sp
    CROSS JOIN params
    WHERE sp.trade_date BETWEEN params.start_date AND params.target_date

    WINDOW
        w_stock AS (PARTITION BY sp.stock_id ORDER BY sp.trade_date),
        w_5d AS (PARTITION BY sp.stock_id ORDER BY sp.trade_date ROWS BETWEEN 4 PRECEDING AND CURRENT ROW),
        w_20d AS (PARTITION BY sp.stock_id ORDER BY sp.trade_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW),
        w_60d AS (PARTITION BY sp.stock_id ORDER BY sp.trade_date ROWS BETWEEN 59 PRECEDING AND CURRENT ROW)
),

-- 🎯 主升段加速突破策略篩選
strategy_signals AS (
    SELECT
        ai.stock_id,
        ai.trade_date,
        ai.close_price,
        ai.volume,
        ai.pct_chg,
        ai.vol_ratio,
        ai.close_position,
        ai.ma_20,
        ai.ma_60,

        -- 計算60日最大漲幅
        ROUND(
            (ai.high_60d - ai.low_60d) / NULLIF(ai.low_60d, 0) * 100,
            2
        ) AS max_gain_60d

    FROM all_indicators ai
    CROSS JOIN params
    WHERE ai.trade_date = params.target_date

    -- 五大核心條件
    AND ai.close_price > ai.ma_20  -- 條件A: 收盤價 > MA20
    AND ai.ma_20 >= ai.ma_60       -- 條件A: MA20 >= MA60
    AND ai.close_price > ai.high_20d  -- 條件B: 創20日新高
    AND ai.vol_ratio >= 1.5        -- 條件C: 失控式放量
    AND ai.pct_chg >= 4.0          -- 條件D: 當日漲幅 >= 4%
    AND ai.close_position >= 0.75  -- 條件E: 收在日內高檔

    -- 兩層防護機制
    AND (ai.high_60d - ai.low_60d) / NULLIF(ai.low_60d, 0) * 100 <= 35  -- 防護1: 排除末升段過熱股
    AND ai.volume >= 3000000       -- 防護2: 成交量 >= 3,000張
    AND ai.vol_ma20 >= 1500000     -- 防護2: 20日均量 >= 1,500張
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
    WHERE esu.etf_count >= params.min_etf_count  -- 篩選: 至少被 N 個 ETF 持有
)

-- 📋 最終輸出
SELECT
    stock_id AS "股票代碼",
    stock_name AS "股票名稱",
    ROUND(close_price::numeric, 2) AS "收盤價",
    pct_chg AS "漲幅%",
    ROUND(volume::numeric / 1000, 0) AS "成交量(張)",
    vol_ratio AS "量比",
    close_position AS "收盤位置",
    etf_count AS "ETF持有數",
    ROUND(total_weight::numeric, 2) AS "ETF總權重%",
    ROUND(ma_20::numeric, 2) AS "MA20",
    ROUND(ma_60::numeric, 2) AS "MA60"
FROM etf_filtered_stocks
ORDER BY
    etf_count DESC,      -- 優先顯示被多個 ETF 持有的標的
    pct_chg DESC         -- 次要排序: 漲幅由大到小
LIMIT 20;

-- ============================================================================
-- 📌 使用說明
-- ============================================================================
--
-- 1. 調整參數:
--    - target_date: 修改為要查詢的日期
--    - min_etf_count: 最少被幾個 ETF 持有（建議值: 1-3）
--
-- 2. 篩選條件調整:
--    - 想要更嚴格篩選: 設定 min_etf_count = 2 或 3
--    - 想要加入權重門檻: 在 WHERE 加上 `AND esu.total_weight >= 5.0`
--
-- 3. 查看特定 ETF 的持股:
--    可以 JOIN etf_holdings 表來查看是哪些 ETF 持有該股票
--
-- ============================================================================
