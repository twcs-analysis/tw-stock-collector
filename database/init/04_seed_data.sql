-- ====================================
-- 台股資料收集系統 - 初始資料
-- Phase 2: 資料庫設計與匯入
-- ====================================
--
-- 檔案: 04_seed_data.sql
-- 用途: 插入初始資料 (種子資料)
-- 執行順序: 第四個執行

SET client_encoding = 'UTF8';
SET timezone = 'Asia/Taipei';

-- ====================================
-- 1. 插入基本股票資料 (範例)
-- ====================================
-- 注意: 完整股票清單會透過 Phase 1 資料收集取得
-- 這裡僅插入幾檔常見股票作為測試用途

INSERT INTO stocks (stock_id, stock_name, industry, market, listing_date, is_active)
VALUES
    ('2330', '台積電', '半導體業', 'TWSE', '1994-09-05', TRUE),
    ('2317', '鴻海', '電腦及週邊設備業', 'TWSE', '1991-06-15', TRUE),
    ('2454', '聯發科', '半導體業', 'TWSE', '2001-07-23', TRUE),
    ('2412', '中華電', '通信網路業', 'TWSE', '2000-11-09', TRUE),
    ('2882', '國泰金', '金融保險業', 'TWSE', '2001-07-11', TRUE),
    ('2881', '富邦金', '金融保險業', 'TWSE', '2001-12-19', TRUE),
    ('2886', '兆豐金', '金融保險業', 'TWSE', '2002-02-04', TRUE),
    ('2891', '中信金', '金融保險業', 'TWSE', '2002-05-09', TRUE),
    ('2303', '聯電', '半導體業', 'TWSE', '1985-07-09', TRUE),
    ('2308', '台達電', '電子零組件業', 'TWSE', '1988-11-28', TRUE),
    ('2379', '瑞昱', '半導體業', 'TWSE', '1998-03-03', TRUE),
    ('1301', '台塑', '塑膠工業', 'TWSE', '1962-02-09', TRUE),
    ('1303', '南亞', '塑膠工業', 'TWSE', '1966-01-11', TRUE),
    ('2002', '中鋼', '鋼鐵工業', 'TWSE', '1962-08-28', TRUE),
    ('0050', '元大台灣50', 'ETF', 'TWSE', '2003-06-25', TRUE),
    ('0056', '元大高股息', 'ETF', 'TWSE', '2007-12-13', TRUE)
ON CONFLICT (stock_id) DO NOTHING;

-- ====================================
-- 2. 產生交易日曆 (2020-2030)
-- ====================================
-- 使用 generate_series 產生日期範圍,並標記週末為非交易日
-- 真實的假日資料需要額外匯入

DO $$
DECLARE
    start_date DATE := '2020-01-01';
    end_date DATE := '2030-12-31';
    curr_date DATE;
    day_of_week_val INTEGER;
BEGIN
    curr_date := start_date;

    WHILE curr_date <= end_date LOOP
        day_of_week_val := EXTRACT(DOW FROM curr_date);  -- 0=Sunday, 6=Saturday

        INSERT INTO trading_calendar (
            date,
            is_trading_day,
            year,
            month,
            quarter,
            week_of_year,
            day_of_week,
            is_month_end,
            is_quarter_end,
            is_year_end
        )
        VALUES (
            curr_date,
            -- 週一到週五視為交易日 (實際假日需另外更新)
            (day_of_week_val >= 1 AND day_of_week_val <= 5),
            EXTRACT(YEAR FROM curr_date),
            EXTRACT(MONTH FROM curr_date),
            EXTRACT(QUARTER FROM curr_date),
            EXTRACT(WEEK FROM curr_date),
            CASE WHEN day_of_week_val = 0 THEN 7 ELSE day_of_week_val END,  -- 1=週一, 7=週日
            curr_date = (DATE_TRUNC('MONTH', curr_date) + INTERVAL '1 MONTH - 1 DAY')::DATE,
            EXTRACT(MONTH FROM curr_date) IN (3, 6, 9, 12) AND
                curr_date = (DATE_TRUNC('MONTH', curr_date) + INTERVAL '1 MONTH - 1 DAY')::DATE,
            EXTRACT(MONTH FROM curr_date) = 12 AND
                curr_date = (DATE_TRUNC('MONTH', curr_date) + INTERVAL '1 MONTH - 1 DAY')::DATE
        )
        ON CONFLICT (date) DO NOTHING;

        curr_date := curr_date + 1;
    END LOOP;

    RAISE NOTICE '交易日曆已產生: % 至 %', start_date, end_date;
END $$;

-- ====================================
-- 3. 更新常見假日為非交易日
-- ====================================
-- 台灣固定假日 (每年相同日期)

DO $$
DECLARE
    yr INTEGER;
BEGIN
    FOR yr IN 2020..2030 LOOP
        -- 元旦 (1/1)
        UPDATE trading_calendar
        SET is_trading_day = FALSE, holiday_name = '元旦'
        WHERE date = make_date(yr, 1, 1);

        -- 和平紀念日 (2/28)
        UPDATE trading_calendar
        SET is_trading_day = FALSE, holiday_name = '和平紀念日'
        WHERE date = make_date(yr, 2, 28);

        -- 兒童節 (4/4)
        UPDATE trading_calendar
        SET is_trading_day = FALSE, holiday_name = '兒童節'
        WHERE date = make_date(yr, 4, 4);

        -- 清明節 (通常 4/5,但實際需依當年公告)
        UPDATE trading_calendar
        SET is_trading_day = FALSE, holiday_name = '清明節'
        WHERE date = make_date(yr, 4, 5);

        -- 勞動節 (5/1)
        UPDATE trading_calendar
        SET is_trading_day = FALSE, holiday_name = '勞動節'
        WHERE date = make_date(yr, 5, 1);

        -- 國慶日 (10/10)
        UPDATE trading_calendar
        SET is_trading_day = FALSE, holiday_name = '國慶日'
        WHERE date = make_date(yr, 10, 10);
    END LOOP;

    RAISE NOTICE '常見假日已標記為非交易日';
    RAISE NOTICE '注意: 農曆假日(春節/端午/中秋)需要另外更新';
END $$;

-- ====================================
-- 4. 插入初始匯入日誌 (用於測試)
-- ====================================

INSERT INTO import_logs (
    data_type,
    import_date,
    source_file,
    records_total,
    records_inserted,
    records_updated,
    records_failed,
    status,
    started_at,
    completed_at,
    duration_seconds
)
VALUES
    ('schema_init', CURRENT_DATE, '01_create_schema.sql', 1, 1, 0, 0, 'success',
     CURRENT_TIMESTAMP - INTERVAL '5 minutes', CURRENT_TIMESTAMP - INTERVAL '4 minutes 55 seconds', 5),
    ('table_init', CURRENT_DATE, '02_create_tables.sql', 10, 10, 0, 0, 'success',
     CURRENT_TIMESTAMP - INTERVAL '4 minutes 50 seconds', CURRENT_TIMESTAMP - INTERVAL '4 minutes 30 seconds', 20),
    ('index_init', CURRENT_DATE, '03_create_indexes.sql', 41, 41, 0, 0, 'success',
     CURRENT_TIMESTAMP - INTERVAL '4 minutes 25 seconds', CURRENT_TIMESTAMP - INTERVAL '3 minutes 50 seconds', 35),
    ('seed_data', CURRENT_DATE, '04_seed_data.sql', 16, 16, 0, 0, 'success',
     CURRENT_TIMESTAMP - INTERVAL '1 minute', CURRENT_TIMESTAMP, 60);

-- ====================================
-- 完成訊息
-- ====================================

DO $$
DECLARE
    stock_count INTEGER;
    calendar_count INTEGER;
    trading_days_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO stock_count FROM stocks;
    SELECT COUNT(*) INTO calendar_count FROM trading_calendar;
    SELECT COUNT(*) INTO trading_days_count FROM trading_calendar WHERE is_trading_day = TRUE;

    RAISE NOTICE '========================================';
    RAISE NOTICE '初始資料載入完成!';
    RAISE NOTICE '';
    RAISE NOTICE '資料統計:';
    RAISE NOTICE '  - 股票數量: %', stock_count;
    RAISE NOTICE '  - 日曆天數: %', calendar_count;
    RAISE NOTICE '  - 交易日數: % (約 %%)', trading_days_count,
                 ROUND(trading_days_count::NUMERIC / calendar_count * 100, 1);
    RAISE NOTICE '';
    RAISE NOTICE '後續步驟:';
    RAISE NOTICE '  1. 執行 Phase 1 資料收集';
    RAISE NOTICE '  2. 使用 importer 匯入實際交易資料';
    RAISE NOTICE '  3. 更新農曆假日標記';
    RAISE NOTICE '========================================';
END $$;
