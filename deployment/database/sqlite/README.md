# SQLite 資料庫部署

台股資料收集系統的 SQLite 資料庫服務配置（開發/測試環境）。

---

## 🚀 快速開始

### 方法一: 使用 Docker（推薦新手）

```bash
cd deployment/database/sqlite

# 啟動初始化容器
docker-compose up -d

# 查看初始化結果
docker-compose logs

# 驗證資料庫
ls -lh ../../../database/sqlite/dev.db
```

### 方法二: 直接使用 SQLite CLI（推薦）

```bash
# 建立資料庫
cd database/sqlite
sqlite3 dev.db

# 執行 schema
.read ../schemas/common/01-tables.sql
.read ../schemas/common/02-indexes.sql
.read ../schemas/sqlite/01-pragmas.sql

# 驗證
.tables
.quit
```

### 方法三: 使用 Python 腳本

```bash
# 從專案根目錄執行
python scripts/db/init_db.py --db-type sqlite --env development
```

---

## 📋 管理操作

### 資料庫連線

```bash
# 使用 sqlite3 CLI
sqlite3 database/sqlite/dev.db

# 常用指令
.tables          # 列出所有表格
.schema stocks   # 查看表格結構
.indexes         # 列出所有索引
.quit            # 離開
```

### 資料查詢

```sql
-- 查詢股票列表
SELECT * FROM stocks LIMIT 10;

-- 查詢最新價格資料
SELECT * FROM stock_prices ORDER BY trade_date DESC LIMIT 10;

-- 查看資料庫資訊
PRAGMA database_list;
PRAGMA table_info(stocks);
```

### 備份與還原

```bash
# 備份（複製檔案）
cp database/sqlite/dev.db database/backups/dev_$(date +%Y%m%d).db

# 還原
cp database/backups/dev_20241227.db database/sqlite/dev.db

# 匯出為 SQL
sqlite3 database/sqlite/dev.db .dump > database/backups/dev_$(date +%Y%m%d).sql

# 從 SQL 匯入
sqlite3 database/sqlite/new.db < database/backups/dev_20241227.sql
```

### 維護操作

```bash
# 連線到資料庫
sqlite3 database/sqlite/dev.db

# 更新統計資訊
ANALYZE;

# 回收空間並優化
VACUUM;

# 檢查資料庫完整性
PRAGMA integrity_check;

# 查看資料庫大小
.databases
```

---

## 🔧 效能優化

### PRAGMA 設定

在連線時執行（已包含在 01-pragmas.sql）：

```sql
-- 啟用外鍵約束
PRAGMA foreign_keys = ON;

-- WAL 模式（提升並發效能）
PRAGMA journal_mode = WAL;

-- 設定快取大小（40 MB）
PRAGMA cache_size = -40000;

-- 記憶體映射（256 MB）
PRAGMA mmap_size = 268435456;
```

### 批次寫入優化

```python
import sqlite3

conn = sqlite3.connect('database/sqlite/dev.db')
cursor = conn.cursor()

# 開始交易
cursor.execute('BEGIN TRANSACTION')

# 批次插入
for data in batch_data:
    cursor.execute('INSERT INTO stocks VALUES (?, ?, ?)', data)

# 提交交易
conn.commit()
```

---

## 📊 與 PostgreSQL 的差異

| 功能 | SQLite | PostgreSQL |
|------|--------|-----------|
| 部署方式 | 單一檔案 | 服務程序 |
| 並發寫入 | 不支援 | 支援 |
| 資料型態 | 動態 | 嚴格 |
| 最大資料庫大小 | ~140 TB | ~32 TB |
| 適用場景 | 開發/測試 | 生產環境 |
| 效能（讀取） | 快 | 快 |
| 效能（寫入） | 中 | 快 |

---

## 🛠️ 疑難排解

### 資料庫鎖定

```bash
# 錯誤: database is locked
# 原因: 有其他程序正在寫入

# 解決方法:
# 1. 關閉所有使用該資料庫的程序
# 2. 刪除 .db-shm 和 .db-wal 檔案
rm database/sqlite/dev.db-shm database/sqlite/dev.db-wal
```

### 效能問題

```sql
-- 查看索引使用情況
EXPLAIN QUERY PLAN SELECT * FROM stocks WHERE stock_id = '2330';

-- 重建索引
REINDEX;

-- 優化資料庫
VACUUM;
ANALYZE;
```

### 檔案損壞

```bash
# 檢查完整性
sqlite3 database/sqlite/dev.db "PRAGMA integrity_check;"

# 如果損壞，嘗試匯出再匯入
sqlite3 database/sqlite/dev.db .dump | sqlite3 database/sqlite/dev_new.db
```

---

## ⚠️ 注意事項

1. **不建議用於生產環境**
   - SQLite 不支援並發寫入
   - 適合單使用者、開發測試環境

2. **資料庫檔案管理**
   - `.db` 檔案不應納入 Git
   - 定期備份資料庫檔案
   - 注意 `.db-shm` 和 `.db-wal` 暫存檔案

3. **效能限制**
   - 大量並發請求時效能下降
   - 超過 1GB 資料時考慮改用 PostgreSQL

4. **遷移至 PostgreSQL**
   - 開發完成後，建議遷移至 PostgreSQL
   - 使用工具: pgloader, sqlalchemy

---

**最後更新**: 2026-02-01
