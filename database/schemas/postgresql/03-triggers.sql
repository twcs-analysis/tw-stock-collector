-- ====================================
-- PostgreSQL 專用 - 觸發器
-- ====================================

-- ==========================================
-- 1. 自動更新 updated_at 欄位
-- ==========================================

-- 建立觸發器函式
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 為 stocks 表建立觸發器
DROP TRIGGER IF EXISTS trigger_stocks_updated_at ON stocks;
CREATE TRIGGER trigger_stocks_updated_at
    BEFORE UPDATE ON stocks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ==========================================
-- 2. 資料驗證觸發器（選用）
-- ==========================================

-- 驗證價格資料的合理性
CREATE OR REPLACE FUNCTION validate_price_data()
RETURNS TRIGGER AS $$
BEGIN
    -- 檢查價格邏輯
    IF NEW.high_price < NEW.low_price THEN
        RAISE EXCEPTION '最高價不能低於最低價: stock_id=%, date=%', NEW.stock_id, NEW.trade_date;
    END IF;

    IF NEW.volume < 0 THEN
        RAISE EXCEPTION '成交量不能為負數: stock_id=%, date=%', NEW.stock_id, NEW.trade_date;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 為 stock_prices 表建立驗證觸發器（選用，可能影響效能）
-- DROP TRIGGER IF EXISTS trigger_validate_price ON stock_prices;
-- CREATE TRIGGER trigger_validate_price
--     BEFORE INSERT OR UPDATE ON stock_prices
--     FOR EACH ROW
--     EXECUTE FUNCTION validate_price_data();

-- ==========================================
-- 3. 審計日誌觸發器（選用）
-- ==========================================

-- 建立審計日誌表
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    operation VARCHAR(10) NOT NULL,  -- INSERT, UPDATE, DELETE
    old_data JSONB,
    new_data JSONB,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 通用審計日誌函式
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_logs (table_name, operation, new_data, changed_by)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(NEW), current_user);
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_logs (table_name, operation, old_data, new_data, changed_by)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(OLD), row_to_json(NEW), current_user);
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_logs (table_name, operation, old_data, changed_by)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(OLD), current_user);
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 為重要表建立審計觸發器（選用）
-- DROP TRIGGER IF EXISTS trigger_audit_stocks ON stocks;
-- CREATE TRIGGER trigger_audit_stocks
--     AFTER INSERT OR UPDATE OR DELETE ON stocks
--     FOR EACH ROW
--     EXECUTE FUNCTION audit_trigger_function();
