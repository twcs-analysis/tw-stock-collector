-- ====================================
-- PostgreSQL 專用 - 擴充功能
-- ====================================

-- 啟用 UUID 支援（未來可能用於分散式系統）
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 啟用全文檢索支援（用於股票名稱搜尋）
-- CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 啟用時間序列資料優化（選用）
-- CREATE EXTENSION IF NOT EXISTS "timescaledb";

-- 注意: 擴充功能需要 superuser 權限
-- 如無需要可跳過此檔案
