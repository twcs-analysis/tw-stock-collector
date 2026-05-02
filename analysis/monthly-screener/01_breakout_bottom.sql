-- 月線級別「大底突破」量化選股
-- 公式: Score = A*0.4 + B*0.3 + C*0.3
--   A: 均線多頭排列 (MA5 > MA10 > MA20 > MA24 且 MA20 斜率為正)
--   B: 底型壓縮度 (近 24 個月 (Max-Min)/Min < 50%)
--   C: 量能激發比 (當月成交量 > 近 12 個月均量 * 2.5)
-- 註: 公式原本指定 MA60/MA120 (5 年/10 年月線)，但資料庫只有 28 個月，
--     改用月線常用均線 MA5(季)、MA10(半年)、MA20(年又8月)、MA24(2 年)

WITH monthly AS (
    -- Step 1: 將日線聚合為月線
    SELECT
        stock_id,
        DATE_TRUNC('month', trade_date)::date AS year_month,
        (ARRAY_AGG(close_price ORDER BY trade_date DESC))[1] AS close_m,
        SUM(volume) AS volume_m
    FROM stock_prices
    GROUP BY stock_id, DATE_TRUNC('month', trade_date)
),
monthly_ma AS (
    -- Step 2: 計算月線均線與滾動統計
    SELECT
        stock_id,
        year_month,
        close_m,
        volume_m,
        AVG(close_m) OVER w5  AS ma5_m,
        AVG(close_m) OVER w10 AS ma10_m,
        AVG(close_m) OVER w20 AS ma20_m,
        AVG(close_m) OVER w24 AS ma24_m,
        MAX(close_m) OVER w24 AS max_24m,
        MIN(close_m) OVER w24 AS min_24m,
        AVG(volume_m) OVER w12prev AS vol_avg_12m,
        ROW_NUMBER() OVER (PARTITION BY stock_id ORDER BY year_month) AS month_idx
    FROM monthly
    WINDOW
        w5  AS (PARTITION BY stock_id ORDER BY year_month ROWS BETWEEN  4 PRECEDING AND CURRENT ROW),
        w10 AS (PARTITION BY stock_id ORDER BY year_month ROWS BETWEEN  9 PRECEDING AND CURRENT ROW),
        w20 AS (PARTITION BY stock_id ORDER BY year_month ROWS BETWEEN 19 PRECEDING AND CURRENT ROW),
        w24 AS (PARTITION BY stock_id ORDER BY year_month ROWS BETWEEN 23 PRECEDING AND CURRENT ROW),
        w12prev AS (PARTITION BY stock_id ORDER BY year_month ROWS BETWEEN 12 PRECEDING AND 1 PRECEDING)
),
monthly_with_lag AS (
    -- Step 3: 計算 MA20 斜率（與 3 個月前比較）
    SELECT
        m.*,
        LAG(ma20_m, 3) OVER (PARTITION BY stock_id ORDER BY year_month) AS ma20_3m_ago
    FROM monthly_ma m
),
scored AS (
    SELECT
        stock_id,
        year_month,
        close_m,
        volume_m,
        ma5_m, ma10_m, ma20_m, ma24_m,
        max_24m, min_24m, vol_avg_12m,
        ma20_3m_ago,
        month_idx,
        -- 指標 A: 均線多頭排列 + MA20 斜率為正
        CASE WHEN ma5_m > ma10_m AND ma10_m > ma20_m AND ma20_m > ma24_m
                  AND ma20_m > ma20_3m_ago
             THEN 1 ELSE 0 END AS a_aligned,
        -- 指標 B: 24 個月波動壓縮 (Max-Min)/Min < 50%
        CASE WHEN min_24m > 0 AND (max_24m - min_24m) / min_24m < 0.5
             THEN 1 ELSE 0 END AS b_compressed,
        -- 指標 C: 當月成交量 > 12 月均量 * 2.5
        CASE WHEN vol_avg_12m > 0 AND volume_m > vol_avg_12m * 2.5
             THEN 1 ELSE 0 END AS c_volume_surge,
        (max_24m - min_24m) / NULLIF(min_24m, 0) * 100 AS range_24m_pct,
        volume_m::numeric / NULLIF(vol_avg_12m, 0) AS vol_ratio_12m
    FROM monthly_with_lag
    WHERE month_idx >= 24
)
SELECT
    s.stock_id,
    st.stock_name,
    s.close_m AS close_price,
    s.a_aligned AS "A",
    s.b_compressed AS "B",
    s.c_volume_surge AS "C",
    ROUND(s.range_24m_pct, 1) AS "24M漲幅%",
    ROUND(s.vol_ratio_12m, 2) AS "量能倍數",
    ROUND((s.a_aligned * 0.4 + s.b_compressed * 0.3 + s.c_volume_surge * 0.3)::numeric, 2) AS score
FROM scored s
JOIN stocks st ON st.stock_id = s.stock_id
WHERE s.year_month = '2026-04-01'
  AND (s.a_aligned + s.b_compressed + s.c_volume_surge) >= 2
ORDER BY score DESC, s.vol_ratio_12m DESC
LIMIT 50;
