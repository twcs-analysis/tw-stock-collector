-- 月營收選股：策略 C - 潛力成長股（寬鬆）
--
-- 篩選邏輯：
--   ✅ 成長性：YoY > 20% 且 MoM > 0%
--   ✅ 趨勢強度：連續 3 個月 YoY 遞增
--   ⚪ 歷史位階：選填
--   ⚪ 量價關係：選填

-- 設定參數
\set target_month '''2026-01'''
\set min_yoy 20
\set min_mom 0

-- ==========================================
-- 步驟 1：判斷趨勢強度（連續 3 個月 YoY 遞增）
-- ==========================================
WITH trend_check AS (
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
-- 步驟 2：整合條件篩選
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

        -- 趨勢強度判斷
        CASE
            WHEN sr.yoy_growth > tc.yoy_1m_ago
                 AND tc.yoy_1m_ago > tc.yoy_2m_ago THEN '✅ 連續遞增'
            ELSE '❌ 未連續'
        END AS trend_strength,

        -- 累計資料（億元）
        ROUND(sr.cumulative_revenue / 100000.0, 2) AS cumulative_billions,
        ROUND(sr.cumulative_yoy_growth, 2) AS cumulative_yoy_pct

    FROM stock_revenues sr
    INNER JOIN trend_check tc
        ON sr.stock_id = tc.stock_id
        AND sr.year_month = tc.year_month

    WHERE
        -- 目標月份
        sr.year_month = :target_month

        -- 條件 1：成長性（必要）
        AND sr.yoy_growth > :min_yoy
        AND sr.mom_growth > :min_mom

        -- 條件 2：趨勢強度（必要）
        AND sr.yoy_growth > tc.yoy_1m_ago
        AND tc.yoy_1m_ago > tc.yoy_2m_ago

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
    trend_strength AS "趨勢強度",
    cumulative_billions AS "累計營收(億)",
    cumulative_yoy_pct AS "累計年增%",
    RANK() OVER (ORDER BY yoy_pct DESC) AS "排名"
FROM filtered_stocks
ORDER BY yoy_pct DESC;

-- ==========================================
-- 摘要統計
-- ==========================================
\echo '\n=== 策略 C：潛力成長股 - 摘要統計 ==='
SELECT
    COUNT(*) AS "符合股票數",
    ROUND(AVG(yoy_pct), 2) AS "平均年增率%",
    ROUND(AVG(mom_pct), 2) AS "平均月增率%",
    ROUND(AVG(revenue_billions), 2) AS "平均營收(億)",
    ROUND(MAX(yoy_pct), 2) AS "最高年增率%",
    ROUND(MIN(yoy_pct), 2) AS "最低年增率%"
FROM filtered_stocks;

-- 使用範例：
-- psql-17 -U postgres -d tw_stock -f analysis/月營收選股/queries/strategy_c_potential.sql
-- psql-17 -U postgres -d tw_stock -v target_month='2026-01' -v min_yoy=15 -f analysis/月營收選股/queries/strategy_c_potential.sql
