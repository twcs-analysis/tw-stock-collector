-- 月營收選股：策略 A - 嚴格成長股（最嚴格）
--
-- 篩選邏輯：
--   ✅ 成長性：YoY > 20% 且 MoM > 0%
--   ✅ 歷史位階：創下 12 個月新高
--   ✅ 趨勢強度：連續 3 個月 YoY 遞增
--   ✅ 量價關係：營收公布後股價帶量突破
--
-- 注意：此查詢需要整合 stock_prices 資料表

-- 設定參數
\set target_month '''2026-01'''
\set min_yoy 20
\set min_mom 0
\set lookback_months 12
\set trend_months 3
\set volume_ratio_threshold 1.2  -- 成交量比（當日/20日均量）

-- ==========================================
-- 步驟 1：計算歷史位階（12 個月新高）
-- ==========================================
WITH revenue_history AS (
    SELECT
        stock_id,
        year_month,
        revenue,
        MAX(revenue) OVER (
            PARTITION BY stock_id
            ORDER BY year_month
            ROWS BETWEEN :lookback_months PRECEDING AND 1 PRECEDING
        ) AS max_revenue_12m,
        MAX(revenue) OVER (
            PARTITION BY stock_id
            ORDER BY year_month
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS max_revenue_all_time
    FROM stock_revenues
    WHERE revenue IS NOT NULL
),

-- ==========================================
-- 步驟 2：判斷趨勢強度（連續 3 個月 YoY 遞增）
-- ==========================================
trend_check AS (
    SELECT
        stock_id,
        year_month,
        yoy_growth,
        LAG(yoy_growth, 1) OVER (
            PARTITION BY stock_id ORDER BY year_month
        ) AS yoy_1m_ago,
        LAG(yoy_growth, 2) OVER (
            PARTITION BY stock_id ORDER BY year_month
        ) AS yoy_2m_ago
    FROM stock_revenues
    WHERE yoy_growth IS NOT NULL
),

-- ==========================================
-- 步驟 3：量價關係分析
-- 營收公布日期通常在次月 1-10 日
-- 例如：2026-01 營收在 2026-02-01 至 2026-02-10 公布
-- ==========================================
price_reaction AS (
    SELECT
        sp.stock_id,
        -- 營收公布期間的最大漲幅
        MAX(sp.close_price) OVER (
            PARTITION BY sp.stock_id
            ORDER BY sp.trade_date
            ROWS BETWEEN CURRENT ROW AND 10 FOLLOWING
        ) / sp.close_price - 1 AS max_gain_10d,
        -- 成交量比（當日量/20日均量）
        sp.volume / NULLIF(sp.volume_ma20, 0) AS volume_ratio,
        -- 是否帶量突破（量比 > 1.2 且漲幅 > 3%）
        CASE
            WHEN sp.volume / NULLIF(sp.volume_ma20, 0) > :volume_ratio_threshold
                 AND sp.close_price > sp.open_price
                 AND (sp.close_price - sp.open_price) / sp.open_price > 0.03
            THEN TRUE
            ELSE FALSE
        END AS is_breakout,
        ROW_NUMBER() OVER (
            PARTITION BY sp.stock_id
            ORDER BY sp.trade_date DESC
        ) AS rn
    FROM stock_prices sp
    WHERE sp.trade_date >= (
        -- 營收公布月份的第一天
        (SELECT TO_DATE(:target_month || '-01', 'YYYY-MM-DD') + INTERVAL '1 month')
    )
    AND sp.trade_date <= (
        -- 營收公布月份的第 10 天
        (SELECT TO_DATE(:target_month || '-01', 'YYYY-MM-DD') + INTERVAL '1 month 10 days')
    )
),

-- ==========================================
-- 步驟 4：整合條件篩選
-- ==========================================
filtered_stocks AS (
    SELECT
        sr.year_month,
        sr.stock_id,
        sr.stock_name,

        -- 營收資料（億元）
        ROUND(sr.revenue / 100000.0, 2) AS revenue_billions,

        -- 增率資料
        ROUND(sr.mom_growth, 2) AS mom_pct,
        ROUND(sr.yoy_growth, 2) AS yoy_pct,

        -- 歷史位階判斷
        CASE
            WHEN sr.revenue >= rh.max_revenue_all_time THEN '✨ 歷史新高'
            WHEN sr.revenue >= rh.max_revenue_12m THEN '📈 12月新高'
            ELSE '普通'
        END AS revenue_position,

        -- 趨勢強度判斷
        CASE
            WHEN sr.yoy_growth > tc.yoy_1m_ago
                 AND tc.yoy_1m_ago > tc.yoy_2m_ago THEN '✅ 連續遞增'
            ELSE '❌ 未連續'
        END AS trend_strength,

        -- 量價關係
        CASE
            WHEN pr.is_breakout THEN '🚀 帶量突破'
            WHEN pr.volume_ratio > :volume_ratio_threshold THEN '📊 量增'
            WHEN pr.max_gain_10d > 0.05 THEN '📈 價漲'
            ELSE '⚪ 未突破'
        END AS price_reaction,

        ROUND(COALESCE(pr.volume_ratio, 0), 2) AS volume_ratio,
        ROUND(COALESCE(pr.max_gain_10d * 100, 0), 2) AS max_gain_pct,

        -- 累計資料（億元）
        ROUND(sr.cumulative_revenue / 100000.0, 2) AS cumulative_billions,
        ROUND(sr.cumulative_yoy_growth, 2) AS cumulative_yoy_pct

    FROM stock_revenues sr
    INNER JOIN revenue_history rh
        ON sr.stock_id = rh.stock_id
        AND sr.year_month = rh.year_month
    INNER JOIN trend_check tc
        ON sr.stock_id = tc.stock_id
        AND sr.year_month = tc.year_month
    LEFT JOIN (
        SELECT * FROM price_reaction WHERE rn = 1
    ) pr ON sr.stock_id = pr.stock_id

    WHERE
        -- 目標月份
        sr.year_month = :target_month

        -- 條件 1：成長性（必要）
        AND sr.yoy_growth > :min_yoy
        AND sr.mom_growth > :min_mom

        -- 條件 2：歷史位階（必要）
        AND sr.revenue >= rh.max_revenue_12m

        -- 條件 3：趨勢強度（必要）
        AND sr.yoy_growth > tc.yoy_1m_ago
        AND tc.yoy_1m_ago > tc.yoy_2m_ago

        -- 條件 4：量價關係（必要）
        AND (
            pr.is_breakout = TRUE
            OR (pr.volume_ratio > :volume_ratio_threshold AND pr.max_gain_10d > 0.03)
        )

        -- 排除空值
        AND sr.revenue IS NOT NULL
        AND sr.yoy_growth IS NOT NULL
)

-- ==========================================
-- 最終輸出：依年增率排序
-- ==========================================
SELECT
    year_month AS "月份",
    stock_id AS "代碼",
    stock_name AS "名稱",
    revenue_billions AS "營收(億)",
    mom_pct AS "月增率%",
    yoy_pct AS "年增率%",
    revenue_position AS "歷史位階",
    trend_strength AS "趨勢強度",
    price_reaction AS "量價反應",
    volume_ratio AS "量比",
    max_gain_pct AS "10日最大漲幅%",
    RANK() OVER (ORDER BY yoy_pct DESC) AS "排名"
FROM filtered_stocks
ORDER BY yoy_pct DESC;

-- ==========================================
-- 摘要統計
-- ==========================================
\echo '\n=== 策略 A：嚴格成長股 - 摘要統計 ==='
SELECT
    COUNT(*) AS "符合股票數",
    ROUND(AVG(yoy_pct), 2) AS "平均年增率%",
    ROUND(AVG(mom_pct), 2) AS "平均月增率%",
    ROUND(AVG(revenue_billions), 2) AS "平均營收(億)",
    ROUND(AVG(volume_ratio), 2) AS "平均量比",
    ROUND(AVG(max_gain_pct), 2) AS "平均漲幅%",
    COUNT(CASE WHEN revenue_position = '✨ 歷史新高' THEN 1 END) AS "歷史新高數",
    COUNT(CASE WHEN price_reaction = '🚀 帶量突破' THEN 1 END) AS "帶量突破數"
FROM filtered_stocks;

-- 使用範例：
-- psql-17 -U postgres -d tw_stock -f analysis/月營收選股/queries/strategy_a_strict.sql
-- psql-17 -U postgres -d tw_stock -v target_month='2026-01' -f analysis/月營收選股/queries/strategy_a_strict.sql
