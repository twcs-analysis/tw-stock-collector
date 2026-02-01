-- ====================================
-- 台股資料收集系統 - 索引定義
-- 版本: 1.0.0
-- 支援: PostgreSQL 12+ / SQLite 3.35+
-- ====================================
--
-- 索引設計原則:
-- 1. 針對常用查詢建立索引
-- 2. 複合索引遵循最左前綴原則
-- 3. 平衡查詢效能與寫入效能
-- 4. 避免過度索引
-- ====================================

-- ==========================================
-- 1. stock_prices 索引
-- ==========================================
-- 用途: 查詢特定股票的歷史價格 (繪圖、K線圖)
CREATE INDEX IF NOT EXISTS idx_prices_stock_date
ON stock_prices (stock_id, trade_date DESC);

-- 用途: 查詢特定日期的所有股票價格 (市場分析)
CREATE INDEX IF NOT EXISTS idx_prices_date
ON stock_prices (trade_date DESC);

-- 用途: 依成交量排序 (篩選活躍股票)
CREATE INDEX IF NOT EXISTS idx_prices_volume
ON stock_prices (trade_date DESC, volume DESC);

-- 用途: 依成交金額排序 (篩選大型股)
CREATE INDEX IF NOT EXISTS idx_prices_amount
ON stock_prices (trade_date DESC, amount DESC);

-- ==========================================
-- 2. institutional_investors 索引
-- ==========================================
-- 用途: 查詢特定股票的法人買賣超歷史
CREATE INDEX IF NOT EXISTS idx_institutional_stock_date
ON institutional_investors (stock_id, trade_date DESC);

-- 用途: 查詢特定日期的所有法人資料
CREATE INDEX IF NOT EXISTS idx_institutional_date
ON institutional_investors (trade_date DESC);

-- 用途: 篩選外資大量買超的股票
CREATE INDEX IF NOT EXISTS idx_institutional_foreign_net
ON institutional_investors (trade_date DESC, foreign_net DESC);

-- 用途: 篩選投信大量買超的股票
CREATE INDEX IF NOT EXISTS idx_institutional_trust_net
ON institutional_investors (trade_date DESC, trust_net DESC);

-- 用途: 篩選三大法人同步買超的股票
CREATE INDEX IF NOT EXISTS idx_institutional_total_net
ON institutional_investors (trade_date DESC, total_net DESC);

-- ==========================================
-- 3. margin_trading 索引
-- ==========================================
-- 用途: 查詢特定股票的融資融券歷史
CREATE INDEX IF NOT EXISTS idx_margin_stock_date
ON margin_trading (stock_id, trade_date DESC);

-- 用途: 查詢特定日期的所有融資融券資料
CREATE INDEX IF NOT EXISTS idx_margin_date
ON margin_trading (trade_date DESC);

-- 用途: 篩選融資大增的股票 (可能有主力介入)
CREATE INDEX IF NOT EXISTS idx_margin_change
ON margin_trading (trade_date DESC, margin_change DESC);

-- ==========================================
-- 4. securities_lending 索引
-- ==========================================
-- 用途: 查詢特定股票的借券歷史
CREATE INDEX IF NOT EXISTS idx_lending_stock_date
ON securities_lending (stock_id, trade_date DESC);

-- 用途: 查詢特定日期的所有借券資料
CREATE INDEX IF NOT EXISTS idx_lending_date
ON securities_lending (trade_date DESC);

-- 用途: 篩選借券大增的股票 (可能有放空壓力)
CREATE INDEX IF NOT EXISTS idx_lending_change
ON securities_lending (trade_date DESC, lending_change DESC);

-- ==========================================
-- 5. top20_volume 索引
-- ==========================================
-- 用途: 查詢特定日期的成交量排名
CREATE INDEX IF NOT EXISTS idx_top20_date_rank
ON top20_volume (trade_date DESC, rank);

-- 用途: 查詢特定股票是否進入前20名
CREATE INDEX IF NOT EXISTS idx_top20_stock_date
ON top20_volume (stock_id, trade_date DESC);

-- ==========================================
-- 6. stock_analysis_daily 索引 (技術分析專用)
-- ==========================================
-- 用途: 查詢特定股票的技術指標歷史 (繪圖、回測)
-- 這是最常用的查詢，優先建立
CREATE INDEX IF NOT EXISTS idx_analysis_stock_date
ON stock_analysis_daily (stock_id, trade_date DESC);

-- 用途: 全市場當日的指標篩選 (選股)
-- 例如: 篩選當天 RSI < 30 的所有股票
CREATE INDEX IF NOT EXISTS idx_analysis_date_stock
ON stock_analysis_daily (trade_date DESC, stock_id);

-- ==========================================
-- 選股專用複合索引 (進階)
-- ==========================================
-- 說明: 這些索引針對常見的選股條件設計
-- 注意: 索引數量與維護成本成正比，請依實際需求啟用

-- 用途: 篩選均線多頭排列 + 量能放大的股票
-- 查詢範例: WHERE trade_date = '2024-12-27' AND close_price > ma_5 AND vol_ratio > 1.5
CREATE INDEX IF NOT EXISTS idx_analysis_trend_vol
ON stock_analysis_daily (trade_date, close_price, ma_5, vol_ratio);

-- 用途: 篩選 RSI 超賣且 MACD 翻多的股票
-- 查詢範例: WHERE trade_date = '2024-12-27' AND rsi_14 < 30 AND macd_hist > 0
CREATE INDEX IF NOT EXISTS idx_analysis_rsi_macd
ON stock_analysis_daily (trade_date, rsi_14, macd_hist);

-- 用途: 篩選 DMI 趨勢啟動的股票
-- 查詢範例: WHERE trade_date = '2024-12-27' AND dmi_pdi > dmi_mdi AND dmi_adx > 25
CREATE INDEX IF NOT EXISTS idx_analysis_dmi
ON stock_analysis_daily (trade_date, dmi_pdi, dmi_mdi, dmi_adx);

-- 用途: 篩選布林帶突破的股票
-- 查詢範例: WHERE trade_date = '2024-12-27' AND close_price > bb_upper
CREATE INDEX IF NOT EXISTS idx_analysis_bb
ON stock_analysis_daily (trade_date, close_price, bb_upper, bb_lower);

-- ==========================================
-- 7. import_logs 索引
-- ==========================================
-- 用途: 查詢特定日期的匯入記錄
CREATE INDEX IF NOT EXISTS idx_import_logs_date_type
ON import_logs (import_date DESC, data_type);

-- 用途: 查詢失敗的匯入記錄 (監控用)
CREATE INDEX IF NOT EXISTS idx_import_logs_status
ON import_logs (status, created_at DESC);

-- ==========================================
-- 效能優化建議
-- ==========================================
--
-- 1. 定期執行 VACUUM (PostgreSQL) 或 VACUUM (SQLite):
--    - PostgreSQL: VACUUM ANALYZE;
--    - SQLite: VACUUM;
--
-- 2. 監控索引使用率 (PostgreSQL):
--    SELECT schemaname, tablename, indexname, idx_scan
--    FROM pg_stat_user_indexes
--    ORDER BY idx_scan;
--
-- 3. 資料分區策略 (PostgreSQL only):
--    - 對於 stock_analysis_daily 表，可考慮按年份分區
--    - 對於 stock_prices 表，可考慮按月份分區
--
-- 4. 索引維護:
--    - 定期檢查並移除未使用的索引
--    - 根據實際查詢模式調整索引
--
-- ==========================================
