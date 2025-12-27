-- ====================================
-- 台股資料收集系統 - 索引建立
-- Phase 2: 資料庫設計與匯入
-- ====================================
--
-- 檔案: 03_create_indexes.sql
-- 用途: 建立索引以優化查詢效能
-- 執行順序: 第三個執行

SET client_encoding = 'UTF8';
SET timezone = 'Asia/Taipei';

-- ====================================
-- 1. 基礎資料表索引
-- ====================================

-- stocks 表
CREATE INDEX IF NOT EXISTS idx_stocks_market ON stocks(market);
CREATE INDEX IF NOT EXISTS idx_stocks_industry ON stocks(industry);
CREATE INDEX IF NOT EXISTS idx_stocks_is_active ON stocks(is_active);
CREATE INDEX IF NOT EXISTS idx_stocks_name_trgm ON stocks USING gin (stock_name gin_trgm_ops);  -- 模糊搜尋

-- trading_calendar 表
CREATE INDEX IF NOT EXISTS idx_trading_calendar_is_trading ON trading_calendar(is_trading_day);
CREATE INDEX IF NOT EXISTS idx_trading_calendar_year_month ON trading_calendar(year, month);
CREATE INDEX IF NOT EXISTS idx_trading_calendar_quarter ON trading_calendar(year, quarter);

-- ====================================
-- 2. 價量資料表索引
-- ====================================

-- daily_prices 表 (最常查詢的表,需要完善的索引)
CREATE INDEX IF NOT EXISTS idx_daily_prices_stock_date ON daily_prices(stock_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_daily_prices_date ON daily_prices(date DESC);
CREATE INDEX IF NOT EXISTS idx_daily_prices_stock_id ON daily_prices(stock_id);
CREATE INDEX IF NOT EXISTS idx_daily_prices_volume ON daily_prices(volume DESC);
CREATE INDEX IF NOT EXISTS idx_daily_prices_amount ON daily_prices(amount DESC);
CREATE INDEX IF NOT EXISTS idx_daily_prices_change_rate ON daily_prices(change_rate DESC);

-- 複合索引 - 常用查詢組合
CREATE INDEX IF NOT EXISTS idx_daily_prices_date_volume ON daily_prices(date DESC, volume DESC);
CREATE INDEX IF NOT EXISTS idx_daily_prices_stock_date_close ON daily_prices(stock_id, date DESC, close);

-- ====================================
-- 3. 籌碼資料表索引
-- ====================================

-- institutional_trading 表
CREATE INDEX IF NOT EXISTS idx_inst_trading_stock_date ON institutional_trading(stock_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_inst_trading_date ON institutional_trading(date DESC);
CREATE INDEX IF NOT EXISTS idx_inst_trading_foreign_net ON institutional_trading(foreign_net DESC);
CREATE INDEX IF NOT EXISTS idx_inst_trading_total_net ON institutional_trading(total_net DESC);

-- 複合索引 - 外資買超排行
CREATE INDEX IF NOT EXISTS idx_inst_trading_date_foreign ON institutional_trading(date DESC, foreign_net DESC);

-- margin_trading 表
CREATE INDEX IF NOT EXISTS idx_margin_trading_stock_date ON margin_trading(stock_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_margin_trading_date ON margin_trading(date DESC);
CREATE INDEX IF NOT EXISTS idx_margin_trading_margin_balance ON margin_trading(margin_purchase_balance DESC);
CREATE INDEX IF NOT EXISTS idx_margin_trading_short_balance ON margin_trading(short_sale_balance DESC);

-- securities_lending 表
CREATE INDEX IF NOT EXISTS idx_sec_lending_stock_date ON securities_lending(stock_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_sec_lending_date ON securities_lending(date DESC);
CREATE INDEX IF NOT EXISTS idx_sec_lending_balance ON securities_lending(lending_balance DESC);

-- foreign_holding 表
CREATE INDEX IF NOT EXISTS idx_foreign_holding_stock_date ON foreign_holding(stock_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_foreign_holding_date ON foreign_holding(date DESC);
CREATE INDEX IF NOT EXISTS idx_foreign_holding_rate ON foreign_holding(holding_rate DESC);

-- 複合索引 - 外資持股比例排行
CREATE INDEX IF NOT EXISTS idx_foreign_holding_date_rate ON foreign_holding(date DESC, holding_rate DESC);

-- shareholding_distribution 表
CREATE INDEX IF NOT EXISTS idx_shareholding_stock_date ON shareholding_distribution(stock_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_shareholding_date ON shareholding_distribution(date DESC);

-- director_holding 表
CREATE INDEX IF NOT EXISTS idx_director_holding_stock_date ON director_holding(stock_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_director_holding_date ON director_holding(date DESC);
CREATE INDEX IF NOT EXISTS idx_director_pledged_rate ON director_holding(director_pledged_rate DESC);

-- ====================================
-- 4. 系統管理表索引
-- ====================================

-- import_logs 表
CREATE INDEX IF NOT EXISTS idx_import_logs_data_type ON import_logs(data_type);
CREATE INDEX IF NOT EXISTS idx_import_logs_import_date ON import_logs(import_date DESC);
CREATE INDEX IF NOT EXISTS idx_import_logs_status ON import_logs(status);
CREATE INDEX IF NOT EXISTS idx_import_logs_created_at ON import_logs(created_at DESC);

-- 複合索引 - 查詢特定資料類型的最近匯入記錄
CREATE INDEX IF NOT EXISTS idx_import_logs_type_date ON import_logs(data_type, import_date DESC);

-- ====================================
-- 5. 部分索引 (Partial Indexes)
-- ====================================
-- 針對特定條件的查詢優化

-- 只索引交易日
CREATE INDEX IF NOT EXISTS idx_trading_days_only
ON trading_calendar(date DESC)
WHERE is_trading_day = TRUE;

-- 只索引活躍股票
CREATE INDEX IF NOT EXISTS idx_active_stocks_only
ON stocks(stock_id)
WHERE is_active = TRUE;

-- 只索引成功的匯入記錄
CREATE INDEX IF NOT EXISTS idx_import_success_only
ON import_logs(data_type, import_date DESC)
WHERE status = 'success';

-- ====================================
-- 6. 索引維護提示
-- ====================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE '索引建立完成!';
    RAISE NOTICE '';
    RAISE NOTICE '索引統計:';
    RAISE NOTICE '  - 基礎資料表: 7 個索引';
    RAISE NOTICE '  - 價量資料表: 8 個索引';
    RAISE NOTICE '  - 籌碼資料表: 18 個索引';
    RAISE NOTICE '  - 系統管理表: 5 個索引';
    RAISE NOTICE '  - 部分索引: 3 個索引';
    RAISE NOTICE '  總計: 41 個索引';
    RAISE NOTICE '';
    RAISE NOTICE '建議定期執行:';
    RAISE NOTICE '  VACUUM ANALYZE; -- 更新統計資訊';
    RAISE NOTICE '  REINDEX DATABASE tw_stock; -- 重建索引';
    RAISE NOTICE '========================================';
END $$;

-- ====================================
-- 7. 自動更新 updated_at 欄位的觸發器
-- ====================================

-- 建立更新時間戳記函數
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 為所有需要的表建立觸發器
CREATE TRIGGER update_stocks_updated_at
    BEFORE UPDATE ON stocks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_daily_prices_updated_at
    BEFORE UPDATE ON daily_prices
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_institutional_trading_updated_at
    BEFORE UPDATE ON institutional_trading
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_margin_trading_updated_at
    BEFORE UPDATE ON margin_trading
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_securities_lending_updated_at
    BEFORE UPDATE ON securities_lending
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_foreign_holding_updated_at
    BEFORE UPDATE ON foreign_holding
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_shareholding_distribution_updated_at
    BEFORE UPDATE ON shareholding_distribution
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_director_holding_updated_at
    BEFORE UPDATE ON director_holding
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
