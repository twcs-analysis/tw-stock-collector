-- ====================================
-- PostgreSQL 專用 - 序列 (Sequences)
-- ====================================
--
-- 說明: PostgreSQL 使用 SERIAL/BIGSERIAL 時會自動建立序列
-- 這裡列出明確的序列定義供參考
-- ====================================

-- stock_prices 主鍵序列
CREATE SEQUENCE IF NOT EXISTS stock_prices_id_seq;
ALTER TABLE stock_prices ALTER COLUMN id SET DEFAULT nextval('stock_prices_id_seq');

-- institutional_investors 主鍵序列
CREATE SEQUENCE IF NOT EXISTS institutional_investors_id_seq;
ALTER TABLE institutional_investors ALTER COLUMN id SET DEFAULT nextval('institutional_investors_id_seq');

-- margin_trading 主鍵序列
CREATE SEQUENCE IF NOT EXISTS margin_trading_id_seq;
ALTER TABLE margin_trading ALTER COLUMN id SET DEFAULT nextval('margin_trading_id_seq');

-- securities_lending 主鍵序列
CREATE SEQUENCE IF NOT EXISTS securities_lending_id_seq;
ALTER TABLE securities_lending ALTER COLUMN id SET DEFAULT nextval('securities_lending_id_seq');

-- top20_volume 主鍵序列
CREATE SEQUENCE IF NOT EXISTS top20_volume_id_seq;
ALTER TABLE top20_volume ALTER COLUMN id SET DEFAULT nextval('top20_volume_id_seq');

-- import_logs 主鍵序列
CREATE SEQUENCE IF NOT EXISTS import_logs_id_seq;
ALTER TABLE import_logs ALTER COLUMN id SET DEFAULT nextval('import_logs_id_seq');

-- etf_holdings 主鍵序列
CREATE SEQUENCE IF NOT EXISTS etf_holdings_id_seq;
ALTER TABLE etf_holdings ALTER COLUMN id SET DEFAULT nextval('etf_holdings_id_seq');

-- stock_revenues 主鍵序列
CREATE SEQUENCE IF NOT EXISTS stock_revenues_id_seq;
ALTER TABLE stock_revenues ALTER COLUMN id SET DEFAULT nextval('stock_revenues_id_seq');
