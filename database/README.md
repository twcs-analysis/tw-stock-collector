# Database 目錄

此目錄包含資料庫相關的 SQL 腳本與遷移檔案。

## 📁 目錄結構

```
database/
├── README.md              # 本文件
├── init/                  # 資料庫初始化腳本 (Docker 自動執行)
│   ├── 01_create_schema.sql
│   ├── 02_create_tables.sql
│   ├── 03_create_indexes.sql
│   └── 04_seed_data.sql
└── migrations/            # 資料庫遷移腳本 (版本升級用)
    └── (待新增)
```

## 🗄️ 資料庫設計

基於 [Phase 2 規格書](../docs/specifications/PHASE2_DATABASE_IMPORT.md) 的完整設計。

### 資料表結構

總共 10 個資料表,分為四大類:

#### 1. 基礎資料表 (2 tables)
- `stocks` - 股票基本資料
- `trading_calendar` - 交易日曆 (2020-2030)

#### 2. 價量資料表 (1 table)
- `daily_prices` - 每日價量資料 (OHLCV)

#### 3. 籌碼資料表 (6 tables)
- `institutional_trading` - 三大法人買賣超
- `margin_trading` - 融資融券
- `securities_lending` - 借券賣出
- `foreign_holding` - 外資持股比例
- `shareholding_distribution` - 股權分散表
- `director_holding` - 董監持股與質押

#### 4. 系統管理表 (1 table)
- `import_logs` - 資料匯入日誌
- `schema_version` - Schema 版本追蹤

### ER 圖

```
stocks (股票基本資料)
  ├── daily_prices (每日價量)
  ├── institutional_trading (法人買賣)
  ├── margin_trading (融資融券)
  ├── securities_lending (借券)
  ├── foreign_holding (外資持股)
  ├── shareholding_distribution (股權分散)
  └── director_holding (董監持股)

trading_calendar (交易日曆)
  ├── daily_prices
  ├── institutional_trading
  ├── margin_trading
  ├── securities_lending
  ├── foreign_holding
  ├── shareholding_distribution
  └── director_holding
```

## 📄 init/ 腳本說明

### 執行順序

Docker PostgreSQL 會按檔名順序自動執行 `init/` 目錄下的 `.sql` 檔案:

1. **01_create_schema.sql** - 建立 Schema 與基本設定
   - 設定 UTF-8 編碼
   - 設定時區為 Asia/Taipei
   - 啟用必要的 PostgreSQL extensions
   - 建立 schema_version 追蹤表

2. **02_create_tables.sql** - 建立所有資料表
   - 10 個業務資料表
   - 完整的欄位註解
   - 外鍵約束

3. **03_create_indexes.sql** - 建立索引與觸發器
   - 41 個索引 (優化查詢效能)
   - 部分索引 (針對常用條件)
   - `updated_at` 自動更新觸發器

4. **04_seed_data.sql** - 插入初始資料
   - 16 檔常見股票 (測試用途)
   - 交易日曆 (2020-2030)
   - 常見固定假日標記

### 腳本特性

✅ **冪等性 (Idempotent)**: 可以重複執行,使用 `IF NOT EXISTS` 和 `ON CONFLICT DO NOTHING`
✅ **註解完整**: 所有表和重要欄位都有 COMMENT
✅ **自動化**: Docker 容器啟動時自動執行
✅ **日誌輸出**: 使用 `RAISE NOTICE` 輸出執行進度

## 🚀 使用方式

### 方式一: 使用 Docker Compose (推薦)

```bash
# 啟動資料庫 (會自動執行 init 腳本)
docker-compose -f deployment/docker-compose.phase2.yml up -d postgres

# 查看初始化日誌
docker-compose -f deployment/docker-compose.phase2.yml logs postgres

# 驗證資料表是否建立
docker-compose -f deployment/docker-compose.phase2.yml exec postgres \
  psql -U stock_user -d tw_stock -c "\dt"

# 查看初始資料
docker-compose -f deployment/docker-compose.phase2.yml exec postgres \
  psql -U stock_user -d tw_stock -c "SELECT * FROM stocks LIMIT 5;"
```

### 方式二: 手動執行 (本地 PostgreSQL)

```bash
# 1. 建立資料庫
createdb tw_stock

# 2. 依序執行腳本
psql -d tw_stock -f database/init/01_create_schema.sql
psql -d tw_stock -f database/init/02_create_tables.sql
psql -d tw_stock -f database/init/03_create_indexes.sql
psql -d tw_stock -f database/init/04_seed_data.sql

# 3. 驗證
psql -d tw_stock -c "\dt"  # 列出所有表
psql -d tw_stock -c "SELECT * FROM schema_version;"  # 查看版本
```

## 🔍 常用查詢

### 查看資料庫統計

```sql
-- 查看所有表的筆數
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    n_live_tup AS rows
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 查看索引使用情況
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan AS index_scans
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- 查看最近匯入記錄
SELECT
    data_type,
    import_date,
    records_total,
    records_inserted,
    status,
    duration_seconds
FROM import_logs
ORDER BY created_at DESC
LIMIT 10;
```

### 業務查詢範例

```sql
-- 查詢台積電最近 10 天價量
SELECT date, open, high, low, close, volume
FROM daily_prices
WHERE stock_id = '2330'
ORDER BY date DESC
LIMIT 10;

-- 查詢今天外資買超前 10 名
SELECT
    s.stock_id,
    s.stock_name,
    it.foreign_net,
    it.date
FROM institutional_trading it
JOIN stocks s ON it.stock_id = s.stock_id
WHERE it.date = CURRENT_DATE
ORDER BY it.foreign_net DESC
LIMIT 10;

-- 查詢本週交易日
SELECT date, day_of_week
FROM trading_calendar
WHERE is_trading_day = TRUE
  AND date >= DATE_TRUNC('week', CURRENT_DATE)
  AND date < DATE_TRUNC('week', CURRENT_DATE) + INTERVAL '7 days'
ORDER BY date;
```

## 🔧 資料庫維護

### 定期維護任務

```sql
-- 更新統計資訊 (建議每日執行)
VACUUM ANALYZE;

-- 重建索引 (建議每週執行)
REINDEX DATABASE tw_stock;

-- 清理舊日誌 (保留 90 天)
DELETE FROM import_logs
WHERE created_at < CURRENT_DATE - INTERVAL '90 days';
```

### 備份與還原

```bash
# 備份整個資料庫
docker-compose -f deployment/docker-compose.phase2.yml exec postgres \
  pg_dump -U stock_user -F c tw_stock > backup_$(date +%Y%m%d).dump

# 備份特定表
docker-compose -f deployment/docker-compose.phase2.yml exec postgres \
  pg_dump -U stock_user -t daily_prices tw_stock > daily_prices_$(date +%Y%m%d).sql

# 還原
docker-compose -f deployment/docker-compose.phase2.yml exec -T postgres \
  pg_restore -U stock_user -d tw_stock -c < backup_20250128.dump
```

### 重置資料庫

```bash
# ⚠️ 警告: 會刪除所有資料!

# 方式一: 刪除並重建容器
docker-compose -f deployment/docker-compose.phase2.yml down -v
docker-compose -f deployment/docker-compose.phase2.yml up -d postgres

# 方式二: 手動刪除所有表
docker-compose -f deployment/docker-compose.phase2.yml exec postgres \
  psql -U stock_user -d tw_stock -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
```

## 📊 效能優化

### 索引策略

已建立 41 個索引,涵蓋:
- **單欄位索引**: 常用查詢欄位 (date, stock_id, volume等)
- **複合索引**: 多欄位組合查詢 (stock_id + date)
- **部分索引**: 針對特定條件 (is_trading_day = TRUE)
- **GIN 索引**: 文字模糊搜尋 (stock_name)

### 查詢優化建議

1. **總是在 WHERE 子句中包含日期範圍**
   ```sql
   -- ✅ 好
   WHERE date BETWEEN '2025-01-01' AND '2025-01-31'

   -- ❌ 不好
   WHERE EXTRACT(MONTH FROM date) = 1
   ```

2. **JOIN 時使用索引欄位**
   ```sql
   -- ✅ 好 (使用 stock_id JOIN)
   JOIN stocks s ON dp.stock_id = s.stock_id

   -- ❌ 不好 (使用非索引欄位)
   JOIN stocks s ON dp.stock_name = s.stock_name
   ```

3. **使用 EXPLAIN ANALYZE 分析慢查詢**
   ```sql
   EXPLAIN ANALYZE
   SELECT * FROM daily_prices
   WHERE stock_id = '2330' AND date > '2025-01-01';
   ```

## 🗂️ migrations/ 目錄

用於資料庫結構變更 (Schema Migration):

### 命名規範

```
YYYYMMDD_HHmmss_description.sql

範例:
20250128_143000_add_dividend_table.sql
20250129_100000_add_index_to_daily_prices.sql
```

### 遷移腳本範本

```sql
-- Migration: 添加股利資料表
-- Date: 2025-01-28
-- Author: Jason Huang

BEGIN;

-- 建立新表
CREATE TABLE IF NOT EXISTS dividends (
    id BIGSERIAL PRIMARY KEY,
    stock_id VARCHAR(10) NOT NULL,
    ex_dividend_date DATE NOT NULL,
    cash_dividend DECIMAL(10, 4),
    stock_dividend DECIMAL(10, 4),
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id)
);

-- 建立索引
CREATE INDEX idx_dividends_stock_date ON dividends(stock_id, ex_dividend_date DESC);

-- 更新版本
INSERT INTO schema_version (version, description)
VALUES ('1.1.0', '新增股利資料表');

COMMIT;
```

## 🐛 故障排除

### 資料庫無法啟動

```bash
# 查看詳細日誌
docker-compose -f deployment/docker-compose.phase2.yml logs postgres

# 檢查資料卷
docker volume inspect tw_stock_postgres_data

# 刪除損壞的資料卷並重建
docker-compose -f deployment/docker-compose.phase2.yml down -v
docker-compose -f deployment/docker-compose.phase2.yml up -d postgres
```

### init 腳本執行失敗

```bash
# init 腳本只在首次啟動時執行
# 如果需要重新執行:
# 1. 刪除資料卷
docker volume rm tw_stock_postgres_data

# 2. 重新啟動
docker-compose -f deployment/docker-compose.phase2.yml up -d postgres
```

### 連線被拒絕

```bash
# 檢查容器狀態
docker-compose -f deployment/docker-compose.phase2.yml ps

# 檢查健康狀態
docker-compose -f deployment/docker-compose.phase2.yml exec postgres pg_isready

# 檢查連線參數
# 確認 .env 中的 DB_USER, DB_PASSWORD, DB_NAME 正確
```

## 📚 相關文檔

- [Phase 2 規格書](../docs/specifications/PHASE2_DATABASE_IMPORT.md) - 完整資料庫設計
- [PostgreSQL 官方文檔](https://www.postgresql.org/docs/)
- [Docker PostgreSQL](https://hub.docker.com/_/postgres)
- [Deployment README](../deployment/README.md) - Docker Compose 使用說明

---

**維護者**: Jason Huang
**最後更新**: 2025-12-28
**Schema 版本**: 1.0.0
