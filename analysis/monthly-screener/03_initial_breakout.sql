-- 月線「初升段爆發」篩選器（公式 3）
-- 邏輯: 找剛起漲第一/第二棒的爆發股，捕捉趨勢確立前的最早入場點
--
-- Score = D * 0.4 + E * 0.3 + F * 0.3
--   D: 近 2 個月累積爆發 (近 2 月漲幅 >= 25%)
--   E: 站上 12 月新高 (close >= max_close_12m * 0.95)
--   F: 量能爆發 (當月量 > 12M 均量 * 3.0，要求比公式 2 更嚴格)
--
-- 不要求均線多頭排列（A 條件）— 因為剛起漲時均線還沒翻多
-- 補充過濾: 排除「漲完整波段又拉回」的標的（要求離 24M 底部還近）
--
-- 適合對象: 像均豪 (5443) 這類「連 2 個月暴漲、均線還沒翻多」的爆發初期標的
-- 對應公式 2 (強勢趨勢) 撈不到的初升段股票

WITH monthly AS (
    SELECT
        stock_id,
        DATE_TRUNC('month', trade_date)::date AS year_month,
        (ARRAY_AGG(close_price ORDER BY trade_date DESC))[1] AS close_m,
        SUM(volume) AS volume_m
    FROM stock_prices
    GROUP BY stock_id, DATE_TRUNC('month', trade_date)
),
monthly_calc AS (
    SELECT
        stock_id,
        year_month,
        close_m,
        volume_m,
        LAG(close_m, 1) OVER (PARTITION BY stock_id ORDER BY year_month) AS close_prev,
        LAG(close_m, 2) OVER (PARTITION BY stock_id ORDER BY year_month) AS close_2m_ago,
        MAX(close_m) OVER w12 AS max_close_12m,
        MIN(close_m) OVER w24 AS min_close_24m,
        AVG(volume_m) OVER w12prev AS vol_avg_12m,
        ROW_NUMBER() OVER (PARTITION BY stock_id ORDER BY year_month) AS month_idx
    FROM monthly
    WINDOW
        w12 AS (PARTITION BY stock_id ORDER BY year_month ROWS BETWEEN 11 PRECEDING AND CURRENT ROW),
        w24 AS (PARTITION BY stock_id ORDER BY year_month ROWS BETWEEN 23 PRECEDING AND CURRENT ROW),
        w12prev AS (PARTITION BY stock_id ORDER BY year_month ROWS BETWEEN 12 PRECEDING AND 1 PRECEDING)
),
scored AS (
    SELECT
        stock_id,
        year_month,
        close_m,
        volume_m,
        close_prev,
        close_2m_ago,
        max_close_12m,
        min_close_24m,
        vol_avg_12m,
        month_idx,
        -- 月漲幅
        (close_m - close_prev) / NULLIF(close_prev, 0) * 100 AS month_change_pct,
        -- 近 2 月累積漲幅
        (close_m - close_2m_ago) / NULLIF(close_2m_ago, 0) * 100 AS two_month_change_pct,
        -- 距離 24M 低點漲幅（用來判斷是否還在「初期」）
        (close_m - min_close_24m) / NULLIF(min_close_24m, 0) * 100 AS from_bottom_pct,
        -- D: 近 2 月累積漲幅 >= 25%
        CASE WHEN close_2m_ago > 0 AND (close_m - close_2m_ago) / close_2m_ago >= 0.25
             THEN 1 ELSE 0 END AS d_surge,
        -- E: 站上 12 月新高
        CASE WHEN max_close_12m > 0 AND close_m >= max_close_12m * 0.95
             THEN 1 ELSE 0 END AS e_near_high,
        -- F: 量能爆發 > 3.0×（比公式 2 嚴格）
        CASE WHEN vol_avg_12m > 0 AND volume_m > vol_avg_12m * 3.0
             THEN 1 ELSE 0 END AS f_volume_surge,
        volume_m::numeric / NULLIF(vol_avg_12m, 0) AS vol_ratio_12m
    FROM monthly_calc
    WHERE month_idx >= 24
)
SELECT
    s.stock_id,
    st.stock_name,
    s.close_m AS close_price,
    ROUND(s.month_change_pct, 1) AS "月漲%",
    ROUND(s.two_month_change_pct, 1) AS "近2月漲%",
    s.d_surge AS "D",
    s.e_near_high AS "E",
    s.f_volume_surge AS "F",
    ROUND(s.vol_ratio_12m, 2) AS "量倍",
    ROUND(s.from_bottom_pct, 0) AS "距底%",
    ROUND((s.d_surge * 0.4 + s.e_near_high * 0.3 + s.f_volume_surge * 0.3)::numeric, 2) AS score
FROM scored s
JOIN stocks st ON st.stock_id = s.stock_id
WHERE s.year_month = '2026-04-01'
  AND (s.d_surge + s.e_near_high + s.f_volume_surge) >= 2
ORDER BY score DESC, s.vol_ratio_12m DESC
LIMIT 80;
