-- ============================================================================
-- 📊 月營收成長股篩選（純營收版，不限 ETF）
-- ============================================================================
--
-- 策略說明：
-- 1. 僅使用月營收成長條件篩選
-- 2. 不限定 ETF 持股，擴大選股範圍
-- 3. 包含最新收盤價資訊
--
-- 篩選維度：
--   ✅ 成長性：YoY > 15% 且 MoM > 0%
--   ✅ 趨勢強度：連續 3 個月 YoY 遞增
--   ✅ 歷史位階：創 12 個月新高（加分項）
--
-- ============================================================================

-- 📅 參數設定
\set target_month '''2025-11'''
\set min_yoy 15              -- 最低年增率 (%)
\set min_mom 0               -- 最低月增率 (%)

-- ==========================================
-- 完整查詢
-- ==========================================
WITH trend_check AS (
    SELECT
        stock_id,
        year_month,
        yoy_change_pct,
        LAG(yoy_change_pct, 1) OVER (PARTITION BY stock_id ORDER BY year_month) AS yoy_1m_ago,
        LAG(yoy_change_pct, 2) OVER (PARTITION BY stock_id ORDER BY year_month) AS yoy_2m_ago
    FROM stock_revenues
    WHERE yoy_change_pct IS NOT NULL
),

revenue_history AS (
    SELECT
        stock_id,
        year_month,
        current_month_revenue,
        MAX(current_month_revenue) OVER (
            PARTITION BY stock_id
            ORDER BY year_month
            ROWS BETWEEN 12 PRECEDING AND 1 PRECEDING
        ) AS max_revenue_12m,
        MAX(current_month_revenue) OVER (
            PARTITION BY stock_id
            ORDER BY year_month
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS max_revenue_all_time
    FROM stock_revenues
    WHERE current_month_revenue IS NOT NULL
),

latest_prices AS (
    SELECT DISTINCT ON (stock_id)
        stock_id,
        close_price,
        trade_date
    FROM stock_prices
    WHERE trade_date >= CURRENT_DATE - INTERVAL '7 days'
    ORDER BY stock_id, trade_date DESC
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
            ELSE '普通'
        END AS revenue_position,
        CASE
            WHEN tc.yoy_change_pct > tc.yoy_1m_ago AND tc.yoy_1m_ago > tc.yoy_2m_ago THEN '✓ 強勢'
            WHEN tc.yoy_change_pct > tc.yoy_1m_ago THEN '△ 改善'
            ELSE '▽ 減緩'
        END AS trend_strong,
        ROUND(COALESCE(lp.close_price, 0), 2) AS latest_close,
        lp.trade_date AS price_date,
        CASE
            WHEN sr.current_month_revenue >= rh.max_revenue_all_time THEN 3
            WHEN sr.current_month_revenue >= rh.max_revenue_12m THEN 2
            ELSE 1
        END AS position_score

    FROM stock_revenues sr
    INNER JOIN stocks s ON sr.stock_id = s.stock_id
    LEFT JOIN revenue_history rh ON sr.stock_id = rh.stock_id AND sr.year_month = rh.year_month
    LEFT JOIN trend_check tc ON sr.stock_id = tc.stock_id AND sr.year_month = tc.year_month
    LEFT JOIN latest_prices lp ON sr.stock_id = lp.stock_id

    WHERE sr.year_month = :target_month
        AND sr.yoy_change_pct >= :min_yoy
        AND sr.mom_change_pct >= :min_mom
        AND tc.yoy_change_pct > tc.yoy_1m_ago
        AND tc.yoy_1m_ago > tc.yoy_2m_ago
),

report_stats AS (
    SELECT
        COUNT(*) AS total_count,
        COUNT(CASE WHEN revenue_position IN ('歷史新高', '12月新高') THEN 1 END) AS new_high_count,
        ROUND(AVG(yoy_pct), 2) AS avg_yoy,
        ROUND(AVG(mom_pct), 2) AS avg_mom
    FROM filtered_stocks
)

-- ==========================================
-- 生成完整 Markdown 報告
-- ==========================================
SELECT
    '# 📊 月營收成長股篩選報告' || E'\n' ||
    E'\n' ||
    '**生成時間**: ' || TO_CHAR(NOW(), 'YYYY-MM-DD HH24:MI:SS') || E'\n' ||
    E'\n' ||
    '**篩選條件**:' || E'\n' ||
    '- 目標月份: 2025-11' || E'\n' ||
    '- 最低年增率: 15%' || E'\n' ||
    '- 最低月增率: 0%' || E'\n' ||
    '- 趨勢條件: 連續 3 個月 YoY 遞增' || E'\n' ||
    E'\n' ||
    '---' || E'\n' ||
    E'\n' ||
    '## 📈 篩選結果統計' || E'\n' ||
    E'\n' ||
    '- **符合條件股票數**: ' || rs.total_count || ' 檔' || E'\n' ||
    '- **創新高數量**: ' || rs.new_high_count || ' 檔' || E'\n' ||
    '- **平均年增率**: ' || rs.avg_yoy || '%' || E'\n' ||
    '- **平均月增率**: ' || rs.avg_mom || '%' || E'\n' ||
    E'\n' ||
    '---' || E'\n' ||
    E'\n' ||
    '## 🎯 篩選結果明細（前 30 名）' || E'\n' ||
    E'\n' ||
    '| 代號 | 股票名稱 | 收盤價 | 當月營收(億) | 月增(%) | 年增(%) | 位階 | 趨勢 |' || E'\n' ||
    '|------|---------|--------|------------|--------|--------|------|-----|' || E'\n' ||
    STRING_AGG(
        '| ' || fs.stock_id ||
        ' | ' || fs.stock_name ||
        ' | ' || fs.latest_close ||
        ' | ' || fs.revenue_billions ||
        ' | ' || fs.mom_pct ||
        ' | ' || fs.yoy_pct ||
        ' | ' || fs.revenue_position ||
        ' | ' || fs.trend_strong || ' |',
        E'\n'
        ORDER BY fs.position_score DESC, fs.yoy_pct DESC
    ) || E'\n' ||
    E'\n' ||
    '---' || E'\n' ||
    E'\n' ||
    '**資料來源**:' || E'\n' ||
    '- 月營收資料: 公開資訊觀測站' || E'\n' ||
    '- 股價資料: 台灣證券交易所 / 櫃買中心 (截至 ' || TO_CHAR(MAX(fs.price_date), 'YYYY-MM-DD') || ')' || E'\n' ||
    E'\n' ||
    '**免責聲明**: 本報告僅供參考，不構成投資建議。投資有風險，請謹慎評估。' || E'\n'
    AS markdown_report
FROM (
    SELECT * FROM filtered_stocks
    ORDER BY position_score DESC, yoy_pct DESC
    LIMIT 30
) fs
CROSS JOIN report_stats rs
GROUP BY rs.total_count, rs.new_high_count, rs.avg_yoy, rs.avg_mom;
