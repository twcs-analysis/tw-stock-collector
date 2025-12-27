-- ====================================
-- 台股資料收集系統 - 資料庫初始化
-- Phase 2: 資料庫設計與匯入
-- ====================================
--
-- 檔案: 01_create_schema.sql
-- 用途: 建立資料庫 schema 與基本設定
-- 執行順序: 第一個執行
--
-- 注意: PostgreSQL docker-entrypoint-initdb.d 會按檔名順序執行

-- 設定用戶端編碼
SET client_encoding = 'UTF8';

-- 設定時區
SET timezone = 'Asia/Taipei';

-- 建立 Extension (如需要)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";  -- UUID 支援
CREATE EXTENSION IF NOT EXISTS "pg_trgm";    -- 文字搜尋加速

-- ====================================
-- Schema 資訊表
-- ====================================

CREATE TABLE IF NOT EXISTS schema_version (
    version VARCHAR(20) PRIMARY KEY,
    description TEXT,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    applied_by VARCHAR(100) DEFAULT CURRENT_USER
);

-- 記錄初始版本
INSERT INTO schema_version (version, description)
VALUES ('1.0.0', '初始資料庫結構 - Phase 2 規格書 v1.0')
ON CONFLICT (version) DO NOTHING;

-- ====================================
-- 註解
-- ====================================

COMMENT ON DATABASE tw_stock IS '台股資料收集與分析系統';
COMMENT ON TABLE schema_version IS '資料庫 schema 版本追蹤';
