-- ====================================
-- 台股資料收集系統 - 資料表建立
-- Phase 2: 資料庫設計與匯入
-- ====================================
--
-- 檔案: 02_create_tables.sql
-- 用途: 建立所有資料表
-- 執行順序: 第二個執行

SET client_encoding = 'UTF8';
SET timezone = 'Asia/Taipei';

-- ====================================
-- 1. 基礎資料表
-- ====================================

-- 1.1 股票基本資料表
CREATE TABLE IF NOT EXISTS stocks (
    stock_id VARCHAR(10) PRIMARY KEY,          -- 股票代碼 (e.g., "2330")
    stock_name VARCHAR(100) NOT NULL,          -- 股票名稱 (e.g., "台積電")
    industry VARCHAR(100),                     -- 產業別
    market VARCHAR(10),                        -- 市場別 (上市/上櫃)
    listing_date DATE,                         -- 上市日期
    is_active BOOLEAN DEFAULT TRUE,            -- 是否持續交易
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE stocks IS '股票基本資料';
COMMENT ON COLUMN stocks.stock_id IS '股票代碼';
COMMENT ON COLUMN stocks.stock_name IS '股票名稱';
COMMENT ON COLUMN stocks.industry IS '產業別';
COMMENT ON COLUMN stocks.market IS '市場別 (TWSE/TPEx)';
COMMENT ON COLUMN stocks.is_active IS '是否仍在交易';

-- 1.2 交易日曆表
CREATE TABLE IF NOT EXISTS trading_calendar (
    date DATE PRIMARY KEY,                     -- 日期
    is_trading_day BOOLEAN NOT NULL,           -- 是否為交易日
    year INTEGER NOT NULL,                     -- 年份
    month INTEGER NOT NULL,                    -- 月份
    quarter INTEGER NOT NULL,                  -- 季度
    week_of_year INTEGER NOT NULL,             -- 年度第幾週
    day_of_week INTEGER NOT NULL,              -- 星期幾 (1=週一)
    is_month_end BOOLEAN DEFAULT FALSE,        -- 是否為月底
    is_quarter_end BOOLEAN DEFAULT FALSE,      -- 是否為季底
    is_year_end BOOLEAN DEFAULT FALSE,         -- 是否為年底
    holiday_name VARCHAR(100),                 -- 假日名稱 (如果是假日)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE trading_calendar IS '交易日曆';
COMMENT ON COLUMN trading_calendar.is_trading_day IS '是否為交易日';
COMMENT ON COLUMN trading_calendar.holiday_name IS '假日名稱';

-- ====================================
-- 2. 價量資料表 (Technical Data)
-- ====================================

-- 2.1 每日價量資料
CREATE TABLE IF NOT EXISTS daily_prices (
    id BIGSERIAL PRIMARY KEY,
    stock_id VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(10, 2),                       -- 開盤價
    high DECIMAL(10, 2),                       -- 最高價
    low DECIMAL(10, 2),                        -- 最低價
    close DECIMAL(10, 2) NOT NULL,             -- 收盤價
    volume BIGINT,                             -- 成交股數
    amount DECIMAL(15, 2),                     -- 成交金額
    transaction_count INTEGER,                  -- 成交筆數
    change_price DECIMAL(10, 2),               -- 漲跌價差
    change_rate DECIMAL(10, 4),                -- 漲跌幅 (%)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_id, date),
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    FOREIGN KEY (date) REFERENCES trading_calendar(date)
);

COMMENT ON TABLE daily_prices IS '每日價量資料';
COMMENT ON COLUMN daily_prices.volume IS '成交股數';
COMMENT ON COLUMN daily_prices.amount IS '成交金額 (新台幣)';
COMMENT ON COLUMN daily_prices.transaction_count IS '成交筆數';

-- ====================================
-- 3. 籌碼資料表 (Chip Data)
-- ====================================

-- 3.1 三大法人買賣超
CREATE TABLE IF NOT EXISTS institutional_trading (
    id BIGSERIAL PRIMARY KEY,
    stock_id VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    foreign_buy BIGINT,                        -- 外資買進股數
    foreign_sell BIGINT,                       -- 外資賣出股數
    foreign_net BIGINT,                        -- 外資買賣超
    investment_trust_buy BIGINT,               -- 投信買進
    investment_trust_sell BIGINT,              -- 投信賣出
    investment_trust_net BIGINT,               -- 投信買賣超
    dealer_buy BIGINT,                         -- 自營商買進
    dealer_sell BIGINT,                        -- 自營商賣出
    dealer_net BIGINT,                         -- 自營商買賣超
    dealer_hedging_buy BIGINT,                 -- 自營商避險買進
    dealer_hedging_sell BIGINT,                -- 自營商避險賣出
    dealer_hedging_net BIGINT,                 -- 自營商避險買賣超
    total_net BIGINT,                          -- 三大法人合計買賣超
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_id, date),
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    FOREIGN KEY (date) REFERENCES trading_calendar(date)
);

COMMENT ON TABLE institutional_trading IS '三大法人買賣超';
COMMENT ON COLUMN institutional_trading.foreign_net IS '外資買賣超股數';
COMMENT ON COLUMN institutional_trading.investment_trust_net IS '投信買賣超股數';
COMMENT ON COLUMN institutional_trading.dealer_net IS '自營商買賣超股數 (含避險)';

-- 3.2 融資融券
CREATE TABLE IF NOT EXISTS margin_trading (
    id BIGSERIAL PRIMARY KEY,
    stock_id VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    margin_purchase_buy BIGINT,                -- 融資買進
    margin_purchase_sell BIGINT,               -- 融資賣出
    margin_purchase_cash_repay BIGINT,         -- 融資現金償還
    margin_purchase_balance BIGINT,            -- 融資餘額
    margin_purchase_limit BIGINT,              -- 融資限額
    short_sale_buy BIGINT,                     -- 融券買進
    short_sale_sell BIGINT,                    -- 融券賣出
    short_sale_cash_repay BIGINT,              -- 融券現金償還
    short_sale_balance BIGINT,                 -- 融券餘額
    short_sale_limit BIGINT,                   -- 融券限額
    offset BIGINT,                             -- 資券互抵
    note VARCHAR(200),                         -- 備註
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_id, date),
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    FOREIGN KEY (date) REFERENCES trading_calendar(date)
);

COMMENT ON TABLE margin_trading IS '融資融券資料';
COMMENT ON COLUMN margin_trading.margin_purchase_balance IS '融資餘額 (股)';
COMMENT ON COLUMN margin_trading.short_sale_balance IS '融券餘額 (股)';

-- 3.3 借券資料
CREATE TABLE IF NOT EXISTS securities_lending (
    id BIGSERIAL PRIMARY KEY,
    stock_id VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    lending_balance BIGINT,                    -- 借券餘額
    lending_limit BIGINT,                      -- 借券限額
    lending_rate DECIMAL(6, 4),                -- 借券利率 (%)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_id, date),
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    FOREIGN KEY (date) REFERENCES trading_calendar(date)
);

COMMENT ON TABLE securities_lending IS '借券賣出資料';
COMMENT ON COLUMN securities_lending.lending_balance IS '借券餘額 (股)';
COMMENT ON COLUMN securities_lending.lending_rate IS '借券利率';

-- 3.4 外資持股比例
CREATE TABLE IF NOT EXISTS foreign_holding (
    id BIGSERIAL PRIMARY KEY,
    stock_id VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    shares_held BIGINT,                        -- 外資持有股數
    holding_rate DECIMAL(6, 4),                -- 持股比例 (%)
    upper_limit_rate DECIMAL(6, 4),            -- 持股上限 (%)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_id, date),
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    FOREIGN KEY (date) REFERENCES trading_calendar(date)
);

COMMENT ON TABLE foreign_holding IS '外資持股比例';
COMMENT ON COLUMN foreign_holding.holding_rate IS '外資持股比例 (%)';
COMMENT ON COLUMN foreign_holding.upper_limit_rate IS '外資持股上限 (%)';

-- 3.5 股權分散表
CREATE TABLE IF NOT EXISTS shareholding_distribution (
    id BIGSERIAL PRIMARY KEY,
    stock_id VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    level_1_15 BIGINT,                         -- 1-999張持股人數
    level_1000_5000 BIGINT,                    -- 1,000-5,000張
    level_5000_10000 BIGINT,                   -- 5,000-10,000張
    level_10000_15000 BIGINT,                  -- 10,000-15,000張
    level_15000_20000 BIGINT,                  -- 15,000-20,000張
    level_20000_30000 BIGINT,                  -- 20,000-30,000張
    level_30000_40000 BIGINT,                  -- 30,000-40,000張
    level_40000_50000 BIGINT,                  -- 40,000-50,000張
    level_50000_100000 BIGINT,                 -- 50,000-100,000張
    level_100000_200000 BIGINT,                -- 100,000-200,000張
    level_200000_400000 BIGINT,                -- 200,000-400,000張
    level_400000_600000 BIGINT,                -- 400,000-600,000張
    level_600000_800000 BIGINT,                -- 600,000-800,000張
    level_800000_1000000 BIGINT,               -- 800,000-1,000,000張
    level_over_1000000 BIGINT,                 -- 1,000,000張以上
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_id, date),
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    FOREIGN KEY (date) REFERENCES trading_calendar(date)
);

COMMENT ON TABLE shareholding_distribution IS '股權分散表 (每週更新)';
COMMENT ON COLUMN shareholding_distribution.level_1_15 IS '1-999張持股人數';
COMMENT ON COLUMN shareholding_distribution.level_over_1000000 IS '100萬張以上持股人數';

-- 3.6 董監持股
CREATE TABLE IF NOT EXISTS director_holding (
    id BIGSERIAL PRIMARY KEY,
    stock_id VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    director_shares BIGINT,                    -- 董監持有股數
    director_pledged_shares BIGINT,            -- 董監質押股數
    director_pledged_rate DECIMAL(6, 4),       -- 董監質押比例 (%)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_id, date),
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE,
    FOREIGN KEY (date) REFERENCES trading_calendar(date)
);

COMMENT ON TABLE director_holding IS '董監持股與質押';
COMMENT ON COLUMN director_holding.director_shares IS '董監持有股數';
COMMENT ON COLUMN director_holding.director_pledged_rate IS '董監質押比例 (%)';

-- ====================================
-- 4. 系統管理表
-- ====================================

-- 4.1 資料匯入日誌
CREATE TABLE IF NOT EXISTS import_logs (
    id BIGSERIAL PRIMARY KEY,
    data_type VARCHAR(50) NOT NULL,            -- 資料類型 (price, institutional, etc.)
    import_date DATE NOT NULL,                 -- 匯入的資料日期
    source_file VARCHAR(500),                  -- 來源檔案路徑
    records_total INTEGER,                     -- 總筆數
    records_inserted INTEGER,                  -- 新增筆數
    records_updated INTEGER,                   -- 更新筆數
    records_failed INTEGER,                    -- 失敗筆數
    status VARCHAR(20) NOT NULL,               -- 狀態 (success, failed, partial)
    error_message TEXT,                        -- 錯誤訊息
    started_at TIMESTAMP WITH TIME ZONE,       -- 開始時間
    completed_at TIMESTAMP WITH TIME ZONE,     -- 完成時間
    duration_seconds INTEGER,                  -- 執行時長 (秒)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE import_logs IS '資料匯入日誌';
COMMENT ON COLUMN import_logs.data_type IS '資料類型';
COMMENT ON COLUMN import_logs.status IS '匯入狀態 (success/failed/partial)';

-- ====================================
-- 建立完成訊息
-- ====================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE '資料表建立完成!';
    RAISE NOTICE '總共建立 10 個資料表:';
    RAISE NOTICE '  - 基礎: stocks, trading_calendar';
    RAISE NOTICE '  - 價量: daily_prices';
    RAISE NOTICE '  - 籌碼: institutional_trading, margin_trading,';
    RAISE NOTICE '          securities_lending, foreign_holding,';
    RAISE NOTICE '          shareholding_distribution, director_holding';
    RAISE NOTICE '  - 系統: import_logs';
    RAISE NOTICE '========================================';
END $$;
