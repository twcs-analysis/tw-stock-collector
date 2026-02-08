-- 月營收選股：策略 D - 爆發突破股（短線）
--
-- 篩選邏輯：
--   ✅ 成長性：MoM > 30% 或 YoY > 50%（營收暴增）
--   ✅ 歷史位階：創歷史新高
--   ⚪ 趨勢強度：選填（可能是新突破，無歷史趨勢）

-- 設定參數
\set target_month '''2026-01'''
\set min_mom_explosion 30
\set min_yoy_explosion 50

-- ==========================================
-- 步驟 1：計算歷史位階（歷史新高）
-- ==========================================
WITH revenue_history AS (
    SELECT
        stock_id,
        year_month,
        revenue,
        -- 計算歷史最高營收
        MAX(revenue) OVER (
            PARTITION BY stock_id
            ORDER BY year_month
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS max_revenue_all_time
    FROM stock_revenues
    WHERE revenue IS NOT NULL
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

        -- 爆發類型
        CASE
            WHEN sr.mom_growth > :min_mom_explosion AND sr.yoy_growth > :min_yoy_explosion
                THEN '🔥 月年雙爆'
            WHEN sr.mom_growth > :min_mom_explosion
                THEN '📈 月增爆發'
            WHEN sr.yoy_growth > :min_yoy_explosion
                THEN '⭐ 年增爆發'
            ELSE '普通'
        END AS explosion_type,

        -- 歷史位階
        CASE
            WHEN sr.revenue >= rh.max_revenue_all_time THEN '✨ 歷史新高'
            ELSE '非新高'
        END AS revenue_position,

        -- 突破幅度（%）
        ROUND((sr.revenue - rh.max_revenue_all_time) / NULLIF(rh.max_revenue_all_time, 0) * 100, 2) AS breakthrough_pct,

        -- 累計資料（億元）
        ROUND(sr.cumulative_revenue / 100000.0, 2) AS cumulative_billions,
        ROUND(sr.cumulative_yoy_growth, 2) AS cumulative_yoy_pct

    FROM stock_revenues sr
    INNER JOIN revenue_history rh
        ON sr.stock_id = rh.stock_id
        AND sr.year_month = rh.year_month

    WHERE
        -- 目標月份
        sr.year_month = :target_month

        -- 條件 1：營收爆發（必要）
        AND (
            sr.mom_growth > :min_mom_explosion
            OR sr.yoy_growth > :min_yoy_explosion
        )

        -- 條件 2：歷史新高（必要）
        AND sr.revenue >= rh.max_revenue_all_time

        -- 排除空值
        AND sr.revenue IS NOT NULL
        AND sr.mom_growth IS NOT NULL
        AND sr.yoy_growth IS NOT NULL
)

-- ==========================================
-- 最終輸出：依突破幅度排序
-- ==========================================
SELECT
    year_month AS "月份",
    stock_id AS "代碼",
    stock_name AS "名稱",
    revenue_billions AS "營收(億)",
    mom_pct AS "月增率%",
    yoy_pct AS "年增率%",
    explosion_type AS "爆發類型",
    revenue_position AS "歷史位階",
    breakthrough_pct AS "突破幅度%",
    cumulative_billions AS "累計營收(億)",
    cumulative_yoy_pct AS "累計年增%",
    RANK() OVER (ORDER BY breakthrough_pct DESC) AS "排名"
FROM filtered_stocks
ORDER BY breakthrough_pct DESC;

-- ==========================================
-- 摘要統計
-- ==========================================
\echo '\n=== 策略 D：爆發突破股 - 摘要統計 ==='
SELECT
    COUNT(*) AS "符合股票數",
    ROUND(AVG(mom_pct), 2) AS "平均月增率%",
    ROUND(AVG(yoy_pct), 2) AS "平均年增率%",
    ROUND(AVG(revenue_billions), 2) AS "平均營收(億)",
    ROUND(AVG(breakthrough_pct), 2) AS "平均突破幅度%",
    ROUND(MAX(breakthrough_pct), 2) AS "最大突破幅度%",
    COUNT(CASE WHEN explosion_type = '🔥 月年雙爆' THEN 1 END) AS "月年雙爆數",
    COUNT(CASE WHEN explosion_type = '📈 月增爆發' THEN 1 END) AS "月增爆發數",
    COUNT(CASE WHEN explosion_type = '⭐ 年增爆發' THEN 1 END) AS "年增爆發數"
FROM filtered_stocks;

-- 使用範例：
-- psql-17 -U postgres -d tw_stock -f analysis/月營收選股/queries/strategy_d_breakout.sql
-- psql-17 -U postgres -d tw_stock -v target_month='2026-01' -v min_mom_explosion=40 -f analysis/月營收選股/queries/strategy_d_breakout.sql
