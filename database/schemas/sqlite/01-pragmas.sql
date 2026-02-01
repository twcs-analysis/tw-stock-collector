-- ====================================
-- SQLite 專用 - PRAGMA 設定
-- ====================================
--
-- 說明: 這些設定優化 SQLite 的效能與資料完整性
-- 建議在每次連線時執行
-- ====================================

-- 啟用外鍵約束（SQLite 預設關閉）
PRAGMA foreign_keys = ON;

-- 設定日誌模式為 WAL (Write-Ahead Logging)
-- 優點: 提升並發讀寫效能
PRAGMA journal_mode = WAL;

-- 設定同步模式為 NORMAL（平衡效能與安全性）
-- FULL: 最安全但最慢
-- NORMAL: 平衡（推薦）
-- OFF: 最快但可能資料遺失
PRAGMA synchronous = NORMAL;

-- 設定暫存記憶體大小 (64 MB)
PRAGMA temp_store = MEMORY;
PRAGMA temp_store_directory = '';

-- 設定快取大小 (10000 pages ≈ 40 MB, 假設 page_size = 4096)
PRAGMA cache_size = -40000;  -- 負數表示 KB

-- 設定記憶體映射大小 (256 MB)
-- 可加速讀取效能
PRAGMA mmap_size = 268435456;

-- 啟用自動索引
PRAGMA automatic_index = ON;

-- 設定分析限制
PRAGMA analysis_limit = 1000;

-- 顯示目前設定（除錯用）
-- PRAGMA foreign_keys;
-- PRAGMA journal_mode;
-- PRAGMA synchronous;
-- PRAGMA cache_size;

-- ==========================================
-- 自動序列設定 (AUTOINCREMENT)
-- ==========================================
-- 注意: SQLite 的 AUTOINCREMENT 已在建表時定義
-- 這裡不需要額外設定

-- ==========================================
-- 觸發器 - 自動更新 updated_at
-- ==========================================

-- 為 stocks 表建立觸發器
DROP TRIGGER IF EXISTS trigger_stocks_updated_at;
CREATE TRIGGER trigger_stocks_updated_at
AFTER UPDATE ON stocks
FOR EACH ROW
BEGIN
    UPDATE stocks
    SET updated_at = CURRENT_TIMESTAMP
    WHERE stock_id = NEW.stock_id;
END;
