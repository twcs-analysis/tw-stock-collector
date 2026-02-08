-- 月營收選股：策略 B - 強勢成長股（推薦）
--
-- 篩選邏輯：
--   ✅ 成長性：YoY > 20% 且 MoM > 0%
--   ✅ 歷史位階：創下 12 個月新高
--   ✅ 趨勢強度：連續 3 個月 YoY 遞增
--   ⚪ 量價關係：選填（需整合股價資料）

-- 設定參數
\set target_month '''2026-01'''
\set min_yoy 20
\set min_mom 0
\set lookback_months 12
\set trend_months 3

-- ==========================================
-- 步驟 1：計算歷史位階（12 個月新高）
-- ==========================================
WITH revenue_history AS (
    SELECT
        stock_id,
        year_month,
        current_month_revenue,
        -- 計算過去 12 個月最高營收
        MAX(current_month_revenue) OVER (
            PARTITION BY stock_id
            ORDER BY year_month
            ROWS BETWEEN :lookback_months PRECEDING AND 1 PRECEDING
        ) AS max_revenue_12m,
        -- 計算歷史最高營收
        MAX(current_month_revenue) OVER (
            PARTITION BY stock_id
            ORDER BY year_month
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS max_revenue_all_time
    FROM stock_revenues
    WHERE current_month_revenue IS NOT NULL
),

-- ==========================================
-- 步驟 2：判斷趨勢強度（連續 3 個月 YoY 遞增）
-- ==========================================
trend_check AS (
    SELECT
        stock_id,
        year_month,
        yoy_change_pct,
        -- 前 1 個月的 YoY
        LAG(yoy_change_pct, 1) OVER (
            PARTITION BY stock_id ORDER BY year_month
        ) AS yoy_1m_ago,
        -- 前 2 個月的 YoY
        LAG(yoy_change_pct, 2) OVER (
            PARTITION BY stock_id ORDER BY year_month
        ) AS yoy_2m_ago
    FROM stock_revenues
    WHERE yoy_change_pct IS NOT NULL
),

-- ==========================================
-- 步驟 3：整合條件篩選
-- ==========================================
filtered_stocks AS (
    SELECT
        sr.year_month,
        sr.stock_id,
        s.stock_name,

        -- 營收資料（億元）
        ROUND(sr.current_month_revenue / 100000.0, 2) AS revenue_billions,

        -- 增率資料
        ROUND(sr.mom_change_pct, 2) AS mom_pct,
        ROUND(sr.yoy_change_pct, 2) AS yoy_pct,

        -- 歷史位階判斷
        CASE
            WHEN sr.current_month_revenue >= rh.max_revenue_all_time THEN '歷史新高'
            WHEN sr.current_month_revenue >= rh.max_revenue_12m THEN '12月新高'
            ELSE '非新高'
        END AS revenue_position,

        -- 趨勢強度判斷
        CASE
            WHEN sr.yoy_change_pct > tc.yoy_1m_ago
                 AND tc.yoy_1m_ago > tc.yoy_2m_ago THEN '✅ 連續遞增'
            WHEN sr.yoy_change_pct > tc.yoy_1m_ago THEN '⚠️  近期遞增'
            ELSE '❌ 未遞增'
        END AS trend_strength,

        -- 累計資料（億元）
        ROUND(sr.ytd_revenue / 100000.0, 2) AS ytd_billions,
        ROUND(sr.ytd_yoy_change_pct, 2) AS ytd_yoy_pct

    FROM stock_revenues sr
    INNER JOIN stocks s ON sr.stock_id = s.stock_id
    INNER JOIN revenue_history rh
        ON sr.stock_id = rh.stock_id
        AND sr.year_month = rh.year_month
    INNER JOIN trend_check tc
        ON sr.stock_id = tc.stock_id
        AND sr.year_month = tc.year_month

    WHERE
        -- 目標月份
        sr.year_month = :target_month

        -- 條件 1：成長性（必要）
        AND sr.yoy_change_pct > :min_yoy
        AND sr.mom_change_pct > :min_mom

        -- 條件 2：歷史位階（必要）
        AND sr.current_month_revenue >= rh.max_revenue_12m

        -- 條件 3：趨勢強度（必要）
        AND sr.yoy_change_pct > tc.yoy_1m_ago
        AND tc.yoy_1m_ago > tc.yoy_2m_ago

        -- 排除空值
        AND sr.current_month_revenue IS NOT NULL
        AND sr.yoy_change_pct IS NOT NULL
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
    ytd_billions AS "累計營收(億)",
    ytd_yoy_pct AS "累計年增%",
    RANK() OVER (ORDER BY yoy_pct DESC) AS "排名"
FROM filtered_stocks
ORDER BY yoy_pct DESC;

-- ==========================================
-- 摘要統計（使用子查詢）
-- ==========================================
\echo '\n=== 策略 B：強勢成長股 - 摘要統計 ==='
WITH revenue_history AS (
    SELECT
        stock_id,
        year_month,
        current_month_revenue,
        MAX(current_month_revenue) OVER (
            PARTITION BY stock_id
            ORDER BY year_month
            ROWS BETWEEN :lookback_months PRECEDING AND 1 PRECEDING
        ) AS max_revenue_12m,
        MAX(current_month_revenue) OVER (
            PARTITION BY stock_id
            ORDER BY year_month
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS max_revenue_all_time
    FROM stock_revenues
    WHERE current_month_revenue IS NOT NULL
),
trend_check AS (
    SELECT
        stock_id,
        year_month,
        yoy_change_pct,
        LAG(yoy_change_pct, 1) OVER (PARTITION BY stock_id ORDER BY year_month) AS yoy_1m_ago,
        LAG(yoy_change_pct, 2) OVER (PARTITION BY stock_id ORDER BY year_month) AS yoy_2m_ago
    FROM stock_revenues
    WHERE yoy_change_pct IS NOT NULL
),
filtered_stocks AS (
    SELECT
        sr.year_month,
        sr.stock_id,
        s.stock_name,
        ROUND(sr.current_month_revenue / 100000.0, 2) AS revenue_billions,
        ROUND(sr.mom_change_pct, 2) AS mom_pct,
        ROUND(sr.yoy_change_pct, 2) AS yoy_pct,
        CASE
            WHEN sr.current_month_revenue >= rh.max_revenue_all_time THEN '歷史新高'
            WHEN sr.current_month_revenue >= rh.max_revenue_12m THEN '12月新高'
            ELSE '非新高'
        END AS revenue_position,
        CASE
            WHEN sr.yoy_change_pct > tc.yoy_1m_ago
                 AND tc.yoy_1m_ago > tc.yoy_2m_ago THEN '✅ 連續遞增'
            WHEN sr.yoy_change_pct > tc.yoy_1m_ago THEN '⚠️  近期遞增'
            ELSE '❌ 未遞增'
        END AS trend_strength,
        ROUND(sr.ytd_revenue / 100000.0, 2) AS ytd_billions,
        ROUND(sr.ytd_yoy_change_pct, 2) AS ytd_yoy_pct
    FROM stock_revenues sr
    INNER JOIN stocks s ON sr.stock_id = s.stock_id
    INNER JOIN revenue_history rh ON sr.stock_id = rh.stock_id AND sr.year_month = rh.year_month
    INNER JOIN trend_check tc ON sr.stock_id = tc.stock_id AND sr.year_month = tc.year_month
    WHERE sr.year_month = :target_month
        AND sr.yoy_change_pct > :min_yoy
        AND sr.mom_change_pct > :min_mom
        AND sr.current_month_revenue >= rh.max_revenue_12m
        AND sr.yoy_change_pct > tc.yoy_1m_ago
        AND tc.yoy_1m_ago > tc.yoy_2m_ago
        AND sr.current_month_revenue IS NOT NULL
        AND sr.yoy_change_pct IS NOT NULL
)
SELECT
    COUNT(*) AS "符合股票數",
    ROUND(AVG(yoy_pct), 2) AS "平均年增率%",
    ROUND(AVG(mom_pct), 2) AS "平均月增率%",
    ROUND(AVG(revenue_billions), 2) AS "平均營收(億)",
    ROUND(MAX(yoy_pct), 2) AS "最高年增率%",
    ROUND(MIN(yoy_pct), 2) AS "最低年增率%",
    COUNT(CASE WHEN revenue_position = '歷史新高' THEN 1 END) AS "歷史新高數"
FROM filtered_stocks;

-- 使用範例：
-- psql-17 -U postgres -d tw_stock -f analysis/月營收選股/queries/strategy_b_balanced.sql
-- psql-17 -U postgres -d tw_stock -v target_month='2026-01' -v min_yoy=25 -f analysis/月營收選股/queries/strategy_b_balanced.sql
