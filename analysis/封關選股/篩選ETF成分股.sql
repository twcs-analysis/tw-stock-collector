-- ============================================================================
-- 篩選年線附近選股中的 ETF 成分股
-- ============================================================================
--
-- 說明：從 101 檔年線附近股票中，篩選出被高股息 ETF 持有的股票
-- 用途：找出「年線支撐 + ETF 買盤」的雙重保護標的
--
-- ============================================================================

-- 101 檔年線附近股票清單
WITH target_stocks AS (
    SELECT stock_id FROM (VALUES
        ('3685'),('6425'),('3363'),('3580'),('4303'),('6261'),('4123'),('5508'),
        ('5315'),('4768'),('6290'),('3289'),('4416'),('6179'),('7777'),('4105'),
        ('6462'),('6643'),('6156'),('5009'),('8936'),('6284'),('8927'),('6207'),
        ('6603'),('4909'),('6245'),('6190'),('8048'),('5309'),('4130'),('3372'),
        ('3526'),('4908'),('5291'),('8069'),('8054'),('4966'),('3455'),('6187'),
        ('6651'),('4979'),('8044'),('6143'),('3498'),('6547'),('3430'),('6683'),
        ('6127'),('5483'),('5864'),('5425'),('3466'),('4114'),('8155'),('6488'),
        ('8034'),('3317'),('5512'),('1569'),('8390'),('6546'),('3260'),('3491'),
        ('5340'),('6121'),('6510'),('3663'),('6026'),('2736'),('8111'),('3294'),
        ('3689'),('4903'),('3693'),('3078'),('8431'),('6111'),('3221'),('5905'),
        ('6126'),('3066'),('6130'),('4714'),('4953'),('3324'),('3290'),('6147'),
        ('3265'),('8076'),('3227'),('3587'),('5302'),('3511'),('6231'),('5530'),
        ('6274'),('2641'),('4510'),('4167'),('1785')
    ) AS t(stock_id)
),

-- 高股息 ETF 清單（可根據需求調整）
target_etfs AS (
    SELECT etf_id FROM (VALUES
        ('0056'),  -- 元大高股息
        ('00878'), -- 國泰永續高股息
        ('00919'), -- 群益台灣精選高息
        ('00929'), -- 復華台灣科技優息
        ('00940'), -- 元大台灣價值高息
        ('00713')  -- 元大台灣高息低波
    ) AS t(etf_id)
),

-- 查詢 ETF 持股
etf_holdings_filtered AS (
    SELECT
        eh.stock_id,
        s.stock_name,
        eh.etf_id,
        e.etf_name,
        eh.weight,
        eh.shares,
        eh.snapshot_date
    FROM etf_holdings eh
    INNER JOIN target_stocks ts ON eh.stock_id = ts.stock_id
    INNER JOIN target_etfs te ON eh.etf_id = te.etf_id
    LEFT JOIN stocks s ON eh.stock_id = s.stock_id
    LEFT JOIN etfs e ON eh.etf_id = e.etf_id
    WHERE eh.snapshot_date = (
        SELECT MAX(snapshot_date)
        FROM etf_holdings
        WHERE etf_id = eh.etf_id
    )
)

-- 最終結果：依持有 ETF 數量排序
SELECT
    stock_id AS "股票代號",
    stock_name AS "股票名稱",
    COUNT(DISTINCT etf_id) AS "被持有ETF數",
    STRING_AGG(etf_name, ', ' ORDER BY weight DESC) AS "持有ETF",
    ROUND(AVG(weight), 2) AS "平均權重(%)",
    MAX(weight) AS "最高權重(%)"
FROM etf_holdings_filtered
GROUP BY stock_id, stock_name
ORDER BY COUNT(DISTINCT etf_id) DESC, AVG(weight) DESC;


-- ============================================================================
-- 替代查詢：顯示詳細持股資訊
-- ============================================================================

/*
SELECT
    eh.stock_id AS "股票代號",
    s.stock_name AS "股票名稱",
    eh.etf_id AS "ETF代號",
    e.etf_name AS "ETF名稱",
    eh.weight AS "權重(%)",
    eh.shares AS "持股數",
    eh.snapshot_date AS "資料日期"
FROM etf_holdings eh
INNER JOIN target_stocks ts ON eh.stock_id = ts.stock_id
INNER JOIN target_etfs te ON eh.etf_id = te.etf_id
LEFT JOIN stocks s ON eh.stock_id = s.stock_id
LEFT JOIN etfs e ON eh.etf_id = e.etf_id
WHERE eh.snapshot_date = (
    SELECT MAX(snapshot_date)
    FROM etf_holdings
    WHERE etf_id = eh.etf_id
)
ORDER BY eh.weight DESC;
*/


-- ============================================================================
-- 使用說明
-- ============================================================================
--
-- 1. 執行查詢（需要有 etf_holdings 資料）：
--    psql-17 -U postgres -d tw_stock -f "analysis/封關選股/篩選ETF成分股.sql"
--
-- 2. 修改目標 ETF：
--    在 target_etfs CTE 中新增或刪除 ETF 代號
--
-- 3. 查詢結果說明：
--    - 被持有ETF數：越多代表被多個 ETF 看好
--    - 平均權重：在所有持有 ETF 中的平均持股比例
--    - 最高權重：在某個 ETF 中的最高持股比例
--
-- 4. 投資建議：
--    - 被 2 個以上 ETF 持有：代表多個 ETF 看好
--    - 權重 > 1%：代表是該 ETF 的重要成分股
--    - 年線附近 + ETF 持有 = 雙重買盤支撐
--
-- ============================================================================
