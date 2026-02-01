-- ====================================
-- 台股資料收集系統 - 約束條件與觸發器
-- 版本: 1.0.0
-- 支援: PostgreSQL 12+ / SQLite 3.35+
-- ====================================
--
-- 說明:
-- 1. 資料完整性約束
-- 2. 業務邏輯驗證
-- 3. 自動更新 updated_at 欄位
-- ====================================

-- ==========================================
-- 1. 檢查約束 (Check Constraints)
-- ==========================================
-- 注意: 這些約束已在 01-tables.sql 中定義
-- 這裡列出供參考，不需重複執行

-- stocks 表約束
-- CONSTRAINT chk_market_type CHECK (market_type IN ('twse', 'tpex'))

-- top20_volume 表約束
-- CONSTRAINT chk_rank CHECK (rank BETWEEN 1 AND 20)

-- import_logs 表約束
-- CONSTRAINT chk_status CHECK (status IN ('running', 'completed', 'failed'))

-- ==========================================
-- 2. 業務邏輯約束 (Business Logic)
-- ==========================================

-- 價格合理性檢查 (stock_prices)
-- 說明: 確保價格資料的邏輯一致性
-- ALTER TABLE stock_prices ADD CONSTRAINT chk_prices_logic
-- CHECK (
--     high_price >= low_price AND
--     high_price >= open_price AND
--     high_price >= close_price AND
--     low_price <= open_price AND
--     low_price <= close_price AND
--     volume >= 0 AND
--     amount >= 0
-- );

-- 注意: 上述約束在某些情況下可能過於嚴格（例如：開盤即漲停/跌停）
-- 建議在應用層進行資料驗證，而非資料庫層

-- ==========================================
-- 3. 觸發器 - 自動更新 updated_at
-- ==========================================
-- 說明: 當記錄更新時，自動更新 updated_at 欄位

-- PostgreSQL 版本
-- 注意: PostgreSQL 需要先建立函式，再建立觸發器
-- 如果使用 SQLite，請參考 sqlite/ 目錄的版本

-- 建立更新時間戳記的函式 (PostgreSQL only)
-- CREATE OR REPLACE FUNCTION update_updated_at_column()
-- RETURNS TRIGGER AS $$
-- BEGIN
--     NEW.updated_at = CURRENT_TIMESTAMP;
--     RETURN NEW;
-- END;
-- $$ LANGUAGE plpgsql;

-- 為 stocks 表建立觸發器 (PostgreSQL only)
-- CREATE TRIGGER trigger_stocks_updated_at
-- BEFORE UPDATE ON stocks
-- FOR EACH ROW
-- EXECUTE FUNCTION update_updated_at_column();

-- ==========================================
-- 4. 資料驗證建議
-- ==========================================
--
-- 以下驗證建議在應用層實作，而非資料庫層：
--
-- 1. 價格合理性:
--    - high >= max(open, close, low)
--    - low <= min(open, close, high)
--    - 價格不為負數
--    - 價格變化幅度在合理範圍內 (例: ±10%)
--
-- 2. 成交量合理性:
--    - volume >= 0
--    - volume 與 amount 的關係合理
--
-- 3. 法人買賣超:
--    - buy >= 0, sell >= 0
--    - net = buy - sell
--    - total_net = foreign_net + trust_net + dealer_net
--
-- 4. 融資融券:
--    - balance >= 0
--    - change = 當日餘額 - 前日餘額
--
-- 5. 日期驗證:
--    - trade_date 必須是交易日
--    - 不可有未來日期
--
-- ==========================================
-- 5. 唯一性約束 (Unique Constraints)
-- ==========================================
-- 注意: 這些約束已在 01-tables.sql 中定義

-- stock_prices: UNIQUE (stock_id, trade_date)
-- institutional_investors: UNIQUE (stock_id, trade_date)
-- margin_trading: UNIQUE (stock_id, trade_date)
-- securities_lending: UNIQUE (stock_id, trade_date)
-- top20_volume: UNIQUE (trade_date, rank)
-- stock_analysis_daily: PRIMARY KEY (trade_date, stock_id)

-- ==========================================
-- 6. 參照完整性 (Referential Integrity)
-- ==========================================
-- 說明: 確保所有外鍵關聯的資料一致性

-- 所有表都有 FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE
-- 這表示當 stocks 表中的記錄被刪除時，相關的所有資料都會自動刪除

-- 注意事項:
-- 1. ON DELETE CASCADE 會遞迴刪除所有相關資料，請謹慎使用
-- 2. 刪除股票前，建議先備份相關資料
-- 3. 生產環境建議使用 ON DELETE RESTRICT，防止誤刪

-- ==========================================
-- 7. 索引維護建議
-- ==========================================
--
-- PostgreSQL:
-- - 定期執行 ANALYZE 更新統計資訊
-- - 使用 pg_stat_user_tables 監控表的使用情況
-- - 使用 pg_stat_user_indexes 監控索引的使用情況
--
-- SQLite:
-- - 定期執行 ANALYZE 更新統計資訊
-- - 定期執行 VACUUM 回收空間並優化資料庫
--
-- ==========================================
