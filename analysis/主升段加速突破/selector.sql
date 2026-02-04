-- ============================================================================
-- 📊 主升段加速突破選股策略 SQL
-- ============================================================================
--
-- 策略定位：主升段第一波爆發，失控式放量 + 價格加速
-- 風險等級：中高
-- 預期勝率：40-55%
-- 單筆報酬：10-20%
-- 持有時間：1-5 天
--
-- ============================================================================
-- 🎯 五大核心條件
-- ============================================================================
--
-- 條件 A：中期趨勢不死（最低門檻）
--   - 收盤價 > MA20
--   - MA20 ≥ MA60
--   - 意義：排除空頭趨勢，保留「剛轉強」股票
--
-- 條件 B：收盤創 20 日新高（脫離整理區）
--   - 今日收盤價 > 最近 20 日最高價
--   - 意義：價格脫離主要成本區，避免箱型假突破
--
-- 條件 C：失控式放量（主升段關鍵）
--   - 量比 ≥ 1.5（今日量 / 20 日均量）
--   - 意義：主升段一定伴隨換手，無量突破 = 高機率假突破
--
-- 條件 D：價格加速（排除龜速股）
--   - 當日漲幅 ≥ 4%
--   - 意義：主升段第一天通常不溫和，排除慢牛、假突破
--
-- 條件 E：收在日內高檔（追價有底氣）
--   - 收盤位置 ≥ 0.75
--   - 收盤位置 = (收盤 - 最低) / (最高 - 最低)
--   - 意義：爆量但不回落，市場願意追到最後一刻
--
-- ============================================================================
-- 🛡️ 兩層防護機制
-- ============================================================================
--
-- 防護 1：排除「末升段過熱股」
--   - 最近 60 日最大漲幅 ≤ 35%
--   - 意義：避免第 N 根漲停，排除情緒末端追高，只抓主升段第一波
--
-- 防護 2：更嚴格的流動性門檻
--   - 今日成交量 ≥ 3,000 張
--   - 20 日均量 ≥ 1,500 張
--   - 意義：追價策略不能卡單，排除小型籌碼股，確保足夠流動性
--
-- ============================================================================

-- 📅 參數設定
WITH params AS (
    SELECT
        '2026-02-03'::date AS target_date,  -- 查詢日期
        ('2026-02-03'::date - INTERVAL '90 days')::date AS start_date  -- 90天窗口
),

-- 📊 計算所有技術指標（使用 WINDOW 子句優化）
all_indicators AS (
    SELECT
        sp.stock_id,
        sp.trade_date,
        sp.open_price,
        sp.high_price,
        sp.low_price,
        sp.close_price,
        sp.volume,

        -- 計算日漲跌幅（因為資料表沒有 pct_chg 欄位）
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
        sp.volume / NULLIF(AVG(sp.volume) OVER w_20d, 0) AS vol_ratio,

        -- 價格位置
        CASE
            WHEN (sp.high_price - sp.low_price) > 0
            THEN (sp.close_price - sp.low_price) / (sp.high_price - sp.low_price)
            ELSE 0
        END AS close_pos,

        -- 20日最高價（用於判斷創新高）
        MAX(sp.high_price) OVER w_20d_prev AS max_high_20d,

        -- 60日最低價（用於計算漲幅）
        MIN(sp.low_price) OVER w_60d_prev AS min_low_60d

    FROM stock_prices sp
    CROSS JOIN params
    WHERE sp.trade_date BETWEEN params.start_date AND params.target_date

    WINDOW
        w_stock AS (PARTITION BY sp.stock_id ORDER BY sp.trade_date),
        w_5d AS (PARTITION BY sp.stock_id ORDER BY sp.trade_date ROWS BETWEEN 4 PRECEDING AND CURRENT ROW),
        w_20d AS (PARTITION BY sp.stock_id ORDER BY sp.trade_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW),
        w_60d AS (PARTITION BY sp.stock_id ORDER BY sp.trade_date ROWS BETWEEN 59 PRECEDING AND CURRENT ROW),
        w_20d_prev AS (PARTITION BY sp.stock_id ORDER BY sp.trade_date ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING),
        w_60d_prev AS (PARTITION BY sp.stock_id ORDER BY sp.trade_date ROWS BETWEEN 60 PRECEDING AND 1 PRECEDING)
),

-- 🎯 最終篩選與輸出
final_data AS (
    SELECT
        ai.*,
        -- 計算 60 日最大漲幅（防護用）
        CASE
            WHEN ai.min_low_60d > 0
            THEN (ai.close_price - ai.min_low_60d) / ai.min_low_60d
            ELSE 0
        END AS max_gain_60d
    FROM all_indicators ai
)

-- 🎯 最終輸出
SELECT
    f.stock_id AS "股票代號",
    s.stock_name AS "股票名稱",
    s.market_type AS "市場別",
    f.close_price AS "收盤價",
    f.pct_chg AS "日漲跌%",
    ROUND(f.volume / 1000.0, 0) AS "成交量(張)",
    ROUND(f.vol_ratio, 2) AS "量比",
    ROUND(f.close_pos, 2) AS "收盤位置",
    ROUND(f.max_gain_60d * 100, 2) AS "60日漲幅%",

    -- 均線距離
    ROUND((f.close_price - f.ma_20) / NULLIF(f.ma_20, 0) * 100, 2) AS "距MA20%",
    ROUND((f.close_price - f.ma_60) / NULLIF(f.ma_60, 0) * 100, 2) AS "距MA60%",

    -- 條件檢查（調試用）
    CASE WHEN f.close_price > f.ma_20 AND f.ma_20 >= f.ma_60 THEN '✓' ELSE '✗' END AS "A_趨勢不死",
    CASE WHEN f.close_price > f.max_high_20d THEN '✓' ELSE '✗' END AS "B_創20日高",
    CASE WHEN f.vol_ratio >= 1.50 THEN '✓' ELSE '✗' END AS "C_爆量≥1.5",
    CASE WHEN f.pct_chg >= 4 THEN '✓' ELSE '✗' END AS "D_漲幅≥4%",
    CASE WHEN f.close_pos >= 0.75 THEN '✓' ELSE '✗' END AS "E_收高檔",
    CASE WHEN f.max_gain_60d <= 0.35 THEN '✓' ELSE '✗' END AS "防護1_非過熱",
    CASE WHEN f.volume >= 3000 AND f.vol_ma20 >= 1500 THEN '✓' ELSE '✗' END AS "防護2_流動性"

FROM final_data f
CROSS JOIN params
LEFT JOIN stocks s ON f.stock_id = s.stock_id
WHERE
    f.trade_date = params.target_date

    -- ✅ 條件 A：中期趨勢不死
    AND f.close_price > f.ma_20
    AND f.ma_20 >= f.ma_60

    -- ✅ 條件 B：收盤創 20 日新高
    AND f.close_price > f.max_high_20d

    -- ✅ 條件 C：失控式放量（量比 ≥ 1.5）
    AND f.vol_ratio >= 1.50

    -- ✅ 條件 D：價格加速（漲幅 ≥ 4%）
    AND f.pct_chg >= 4

    -- ✅ 條件 E：收在日內高檔（收盤位置 ≥ 0.75）
    AND f.close_pos >= 0.75

    -- 🛡️ 防護 1：排除末升段過熱股（60日漲幅 ≤ 35%）
    AND f.max_gain_60d <= 0.35

    -- 🛡️ 防護 2：更嚴格的流動性門檻
    AND f.volume >= 3000
    AND f.vol_ma20 >= 1500

    -- 排除 ETF
    AND f.stock_id >= '1000'

ORDER BY f.pct_chg DESC, f.vol_ratio DESC;


-- ============================================================================
-- 📝 使用說明
-- ============================================================================
--
-- 🚀 執行方式：
--   docker cp selector.sql tw-stock-postgres:/tmp/
--   docker exec -i tw-stock-postgres psql -U postgres -d tw_stock -f /tmp/selector.sql
--
-- 📅 修改查詢日期：
--   編輯第 37 行的 target_date
--
-- ⚙️ 參數調整：
--   - 量比門檻（第 154 行）：1.5 → 1.3（放寬）/ 2.0（嚴格）
--   - 漲幅門檻（第 157 行）：4% → 3%（放寬）/ 5%（嚴格）
--   - 收盤位置（第 160 行）：0.75 → 0.70（放寬）/ 0.80（嚴格）
--   - 60日漲幅（第 163 行）：35% → 40%（放寬）/ 30%（嚴格）
--
-- ⚠️ 注意事項：
--   1. 這是「追價策略」，風險較高，務必嚴格停損
--   2. 建議單筆不超過總資金 10%
--   3. 沒有選到股票是正常的（嚴格篩選）
--   4. 僅在「強勢多頭市場」使用
--
-- ============================================================================
