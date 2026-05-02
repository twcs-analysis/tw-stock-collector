-- 月線「強勢趨勢」篩選器
-- 邏輯: 找已經會漲的強勢股（不是找剛從底部起飛）
--
-- Score = A * 0.4 + B' * 0.3 + C' * 0.3
--   A   均線多頭排列 (MA5 > MA10 > MA20 > MA24 且 MA20 斜率為正)
--   B'  站上 12 月新高 95% (取代原 VCP 壓縮條件)
--   C'  量能溫和放大 (當月 vol > 12 月均量 * 1.5)
--
-- 適合對象: 已經漲過一波、回檔後再起或持續創新高的「強勢趨勢股」
-- 對應公式 1 (大底突破) 撈不到的飆股，例如均豪 (5443)、愛普 (6531)

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
    -- Step 2: 計算月線均線、12 月最高收盤、12 月均量
    SELECT
        stock_id,
        year_month,
        close_m,
        volume_m,
        AVG(close_m) OVER w5  AS ma5_m,
        AVG(close_m) OVER w10 AS ma10_m,
        AVG(close_m) OVER w20 AS ma20_m,
        AVG(close_m) OVER w24 AS ma24_m,
        MAX(close_m) OVER w12 AS max_close_12m,         -- B': 12 月最高收盤
        AVG(volume_m) OVER w12prev AS vol_avg_12m,      -- C': 12 月均量
        ROW_NUMBER() OVER (PARTITION BY stock_id ORDER BY year_month) AS month_idx
    FROM monthly
    WINDOW
        w5  AS (PARTITION BY stock_id ORDER BY year_month ROWS BETWEEN  4 PRECEDING AND CURRENT ROW),
        w10 AS (PARTITION BY stock_id ORDER BY year_month ROWS BETWEEN  9 PRECEDING AND CURRENT ROW),
        w20 AS (PARTITION BY stock_id ORDER BY year_month ROWS BETWEEN 19 PRECEDING AND CURRENT ROW),
        w24 AS (PARTITION BY stock_id ORDER BY year_month ROWS BETWEEN 23 PRECEDING AND CURRENT ROW),
        w12 AS (PARTITION BY stock_id ORDER BY year_month ROWS BETWEEN 11 PRECEDING AND CURRENT ROW),
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
        max_close_12m, vol_avg_12m,
        ma20_3m_ago,
        month_idx,
        -- A: 均線多頭排列 + MA20 斜率為正
        CASE WHEN ma5_m > ma10_m AND ma10_m > ma20_m AND ma20_m > ma24_m
                  AND ma20_m > ma20_3m_ago
             THEN 1 ELSE 0 END AS a_aligned,
        -- B': 當月收盤站上 12 月最高收盤 × 95%
        CASE WHEN max_close_12m > 0 AND close_m >= max_close_12m * 0.95
             THEN 1 ELSE 0 END AS b_near_high,
        -- C': 當月量 > 12 月均量 × 1.5
        CASE WHEN vol_avg_12m > 0 AND volume_m > vol_avg_12m * 1.5
             THEN 1 ELSE 0 END AS c_volume_up,
        -- 額外資訊
        close_m / NULLIF(max_close_12m, 0) * 100 AS pct_of_12m_high,
        volume_m::numeric / NULLIF(vol_avg_12m, 0) AS vol_ratio_12m
    FROM monthly_with_lag
    WHERE month_idx >= 24
)
SELECT
    s.stock_id,
    st.stock_name,
    s.close_m AS close_price,
    s.a_aligned AS "A",
    s.b_near_high AS "B'",
    s.c_volume_up AS "C'",
    ROUND(s.pct_of_12m_high, 1) AS "佔12M高%",
    ROUND(s.vol_ratio_12m, 2) AS "量能倍數",
    ROUND((s.a_aligned * 0.4 + s.b_near_high * 0.3 + s.c_volume_up * 0.3)::numeric, 2) AS score
FROM scored s
JOIN stocks st ON st.stock_id = s.stock_id
WHERE s.year_month = '2026-04-01'
  AND (s.a_aligned + s.b_near_high + s.c_volume_up) >= 2  -- 至少 2 個指標達標
ORDER BY score DESC, s.vol_ratio_12m DESC
LIMIT 50;
