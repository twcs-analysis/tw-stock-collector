-- ============================================================================
-- 📊 月營收成長股 + ETF 持股篩選（Markdown 報告版 v2）
-- ============================================================================
--
-- 改進：從資料庫讀取 ETF 持股資料，不再寫死
-- 輸出格式：Markdown 表格，包含最新收盤價
--
-- ============================================================================

-- 📅 參數設定
\set target_month '''2025-11'''
\set min_yoy 15              -- 最低年增率 (%)
\set min_mom 0               -- 最低月增率 (%)
\set min_etf_count 1         -- 最少被幾個 ETF 持有
\set verify_latest_month '''2026-01'''  -- 驗證最新月份（確保近期仍成長）

-- ==========================================
-- 完整查詢（從資料庫讀取 ETF 持股）
-- ==========================================
WITH etf_holdings_agg AS (
    -- 從資料庫讀取最新的 ETF 持股資料
    SELECT
        stock_id,
        COUNT(DISTINCT etf_id) AS etf_count,
        STRING_AGG(etf_id, ', ' ORDER BY etf_id) AS etf_list,
        STRING_AGG(etf_detail, ', ' ORDER BY etf_id) AS etf_detail,
        ROUND(AVG(weight), 2) AS avg_weight,
        ROUND(MAX(weight), 2) AS max_weight
    FROM (
        SELECT DISTINCT
            eh.stock_id,
            eh.etf_id,
            eh.etf_id || ':' || e.etf_name AS etf_detail,
            eh.weight
        FROM etf_holdings eh
        INNER JOIN etfs e ON eh.etf_id = e.etf_id
        WHERE eh.snapshot_date = (
            SELECT MAX(snapshot_date) FROM etf_holdings
        )
    ) AS distinct_holdings
    GROUP BY stock_id
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
        COALESCE(eh.etf_count, 0) AS etf_count,
        COALESCE(eh.etf_list, '-') AS etf_list,
        CASE
            WHEN COALESCE(eh.etf_count, 0) >= 5 THEN 10
            WHEN COALESCE(eh.etf_count, 0) >= 4 THEN 8
            WHEN COALESCE(eh.etf_count, 0) >= 3 THEN 7
            WHEN COALESCE(eh.etf_count, 0) >= 2 THEN 5
            WHEN COALESCE(eh.etf_count, 0) >= 1 THEN 3
            ELSE 0
        END AS recognition_score,
        CASE
            WHEN COALESCE(eh.etf_count, 0) >= 4 THEN '低風險'
            WHEN COALESCE(eh.etf_count, 0) >= 2 THEN '中風險'
            WHEN COALESCE(eh.etf_count, 0) >= 1 THEN '中高風險'
            ELSE '高風險'
        END AS risk_level,
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
    LEFT JOIN etf_holdings_agg eh ON sr.stock_id = eh.stock_id
    LEFT JOIN latest_prices lp ON sr.stock_id = lp.stock_id

    WHERE sr.year_month = :target_month
        AND sr.yoy_change_pct >= :min_yoy
        AND sr.mom_change_pct >= :min_mom
        AND tc.yoy_change_pct > tc.yoy_1m_ago
        AND tc.yoy_1m_ago > tc.yoy_2m_ago
        AND COALESCE(eh.etf_count, 0) >= :min_etf_count
        -- 驗證最新月份仍維持成長動能
        AND EXISTS (
            SELECT 1 FROM stock_revenues sr_latest
            WHERE sr_latest.stock_id = sr.stock_id
              AND sr_latest.year_month = :verify_latest_month
              AND sr_latest.yoy_change_pct > 0  -- 最新月份 YoY 仍為正
        )
),

report_stats AS (
    SELECT
        COUNT(*) AS total_count,
        COUNT(CASE WHEN revenue_position IN ('歷史新高', '12月新高') THEN 1 END) AS new_high_count,
        ROUND(AVG(yoy_pct), 2) AS avg_yoy,
        ROUND(AVG(mom_pct), 2) AS avg_mom,
        ROUND(AVG(etf_count), 1) AS avg_etf_count
    FROM filtered_stocks
),

etf_data_info AS (
    SELECT
        MAX(snapshot_date) AS latest_snapshot,
        COUNT(DISTINCT etf_id) AS total_etfs,
        COUNT(DISTINCT stock_id) AS total_stocks
    FROM etf_holdings
    WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM etf_holdings)
)

-- ==========================================
-- 生成完整 Markdown 報告
-- ==========================================
SELECT
    '# 📊 月營收成長股 + ETF 持股篩選報告' || E'\n' ||
    E'\n' ||
    '**生成時間**: ' || TO_CHAR(NOW(), 'YYYY-MM-DD HH24:MI:SS') || E'\n' ||
    E'\n' ||
    '**篩選條件**:' || E'\n' ||
    '- 目標月份: 2025-11' || E'\n' ||
    '- 最低年增率: 15%' || E'\n' ||
    '- 最低月增率: 0%' || E'\n' ||
    '- 最少 ETF 持有數: 1 個' || E'\n' ||
    '- 趨勢條件: 連續 3 個月 YoY 遞增' || E'\n' ||
    '- 最新驗證: 2026-01 月仍維持正成長' || E'\n' ||
    E'\n' ||
    '**ETF 資料來源**:' || E'\n' ||
    '- 資料日期: ' || TO_CHAR(edi.latest_snapshot, 'YYYY-MM-DD') || E'\n' ||
    '- 涵蓋 ETF 數: ' || edi.total_etfs || ' 個' || E'\n' ||
    '- 涵蓋股票數: ' || edi.total_stocks || ' 檔' || E'\n' ||
    E'\n' ||
    '---' || E'\n' ||
    E'\n' ||
    '## 📈 篩選結果統計' || E'\n' ||
    E'\n' ||
    '- **符合條件股票數**: ' || rs.total_count || ' 檔' || E'\n' ||
    '- **創新高數量**: ' || rs.new_high_count || ' 檔' || E'\n' ||
    '- **平均年增率**: ' || rs.avg_yoy || '%' || E'\n' ||
    '- **平均月增率**: ' || rs.avg_mom || '%' || E'\n' ||
    '- **平均持有 ETF 數**: ' || rs.avg_etf_count || ' 個' || E'\n' ||
    E'\n' ||
    '---' || E'\n' ||
    E'\n' ||
    '## 🎯 篩選結果明細' || E'\n' ||
    E'\n' ||
    '| 代號 | 股票名稱 | 收盤價 | 營收(億) | 月增(%) | 年增(%) | 位階 | 趨勢 | ETF數 | 認可度 | 風險 | ETF清單 |' || E'\n' ||
    '|------|---------|--------|------------|--------|--------|------|-----|------|-------|------|---------|' || E'\n' ||
    COALESCE(
        STRING_AGG(
            '| ' || fs.stock_id ||
            ' | ' || fs.stock_name ||
            ' | ' || fs.latest_close ||
            ' | ' || fs.revenue_billions ||
            ' | ' || fs.mom_pct ||
            ' | ' || fs.yoy_pct ||
            ' | ' || fs.revenue_position ||
            ' | ' || fs.trend_strong ||
            ' | ' || fs.etf_count ||
            ' | ' || fs.recognition_score ||
            ' | ' || fs.risk_level ||
            ' | ' || fs.etf_list || ' |',
            E'\n'
            ORDER BY fs.position_score DESC, fs.etf_count DESC, fs.yoy_pct DESC
        ),
        '| - | 無符合條件的股票 | - | - | - | - | - | - | - | - | - | - |'
    ) || E'\n' ||
    E'\n' ||
    '---' || E'\n' ||
    E'\n' ||
    '## 📝 風險等級說明' || E'\n' ||
    E'\n' ||
    '| 風險等級 | ETF 持有數 | 特性 | 建議投資比例 |' || E'\n' ||
    '|---------|-----------|------|-------------|' || E'\n' ||
    '| 低風險 | ≥ 4 個 | 多家機構認可，財務穩健 | 50-70% |' || E'\n' ||
    '| 中風險 | 2-3 個 | 有一定認可度 | 20-30% |' || E'\n' ||
    '| 中高風險 | 1 個 | 基本認可 | 10-20% |' || E'\n' ||
    '| 高風險 | 0 個 | 未被 ETF 持有 | < 5% 或避免 |' || E'\n' ||
    E'\n' ||
    '---' || E'\n' ||
    E'\n' ||
    '**資料來源**:' || E'\n' ||
    '- 月營收資料: 公開資訊觀測站' || E'\n' ||
    '- 股價資料: 台灣證券交易所 / 櫃買中心 (截至 ' || COALESCE(TO_CHAR(MAX(fs.price_date), 'YYYY-MM-DD'), 'N/A') || ')' || E'\n' ||
    '- ETF 持股: 資料庫 etf_holdings 表 (截至 ' || TO_CHAR(edi.latest_snapshot, 'YYYY-MM-DD') || ')' || E'\n' ||
    E'\n' ||
    '**免責聲明**: 本報告僅供參考，不構成投資建議。投資有風險，請謹慎評估。' || E'\n'
    AS markdown_report
FROM filtered_stocks fs
CROSS JOIN report_stats rs
CROSS JOIN etf_data_info edi
GROUP BY rs.total_count, rs.new_high_count, rs.avg_yoy, rs.avg_mom, rs.avg_etf_count,
         edi.latest_snapshot, edi.total_etfs, edi.total_stocks;
