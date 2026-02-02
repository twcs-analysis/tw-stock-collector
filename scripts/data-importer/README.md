# 資料匯入腳本

將 JSON 格式的原始資料匯入到資料庫（PostgreSQL）。

## 前置條件

1. **啟動 PostgreSQL 資料庫**

```bash
# 方法 1: 使用獨立的 PostgreSQL
cd deployment/database/postgresql
docker-compose up -d

# 方法 2: 使用完整的資料管道（包含 collector + importer）
cd deployment/data-import-pipeline
docker-compose up -d
```

2. **設定環境變數**

```bash
export DB_PASSWORD=tw_stock_dev_password_2024
# 或使用 .env 檔案
```

## 使用方式

### 1. 匯入單一日期的資料

```bash
# 匯入所有類型（price, institutional, margin, lending, top20_volume）
DB_PASSWORD=tw_stock_dev_password_2024 \
python scripts/data-importer/import_data.py --date 2026-01-02

# 只匯入 price 資料
DB_PASSWORD=tw_stock_dev_password_2024 \
python scripts/data-importer/import_data.py --date 2026-01-02 --types price
```

### 2. 匯入指定類型

```bash
# 匯入 price 和 institutional
DB_PASSWORD=tw_stock_dev_password_2024 \
python scripts/data-importer/import_data.py \
  --date 2026-01-02 \
  --types price institutional
```

### 3. 匯入日期區間

```bash
# 匯入 2026 年 1 月的所有資料
DB_PASSWORD=tw_stock_dev_password_2024 \
python scripts/data-importer/import_data.py \
  --start 2026-01-01 \
  --end 2026-01-31

# 只匯入特定類型
DB_PASSWORD=tw_stock_dev_password_2024 \
python scripts/data-importer/import_data.py \
  --start 2026-01-01 \
  --end 2026-01-31 \
  --types price margin
```

### 4. 自訂資料庫設定

```bash
# 使用自訂資料庫配置
DB_HOST=localhost \
DB_PORT=5432 \
DB_NAME=tw_stock \
DB_USER=postgres \
DB_PASSWORD=your_password \
python scripts/data-importer/import_data.py --date 2026-01-02
```

## 支援的資料類型

| 類型 | 說明 | 資料表 |
|------|------|--------|
| `price` | 每日價格資料 | `stock_prices` |
| `institutional` | 三大法人買賣超 | `institutional_investors` |
| `margin` | 融資融券 | `margin_trading` |
| `lending` | 借券賣出 | `securities_lending` |
| `top20_volume` | 成交量前20名 | `top20_volume` |

## 驗證資料

```bash
# 查看匯入的記錄數
docker exec tw-stock-postgres psql -U postgres -d tw_stock -c \
  "SELECT COUNT(*) FROM stock_prices WHERE trade_date = '2026-01-02';"

# 查看成交量前 5 名
docker exec tw-stock-postgres psql -U postgres -d tw_stock -c \
  "SELECT stock_id, close_price, volume
   FROM stock_prices
   WHERE trade_date = '2026-01-02'
   ORDER BY volume DESC LIMIT 5;"

# 查看特定股票
docker exec tw-stock-postgres psql -U postgres -d tw_stock -c \
  "SELECT * FROM stock_prices
   WHERE trade_date = '2026-01-02' AND stock_id = '2330';"
```

## 常見問題

### Q: 連線失敗 "no password supplied"

A: 請設定 `DB_PASSWORD` 環境變數：
```bash
export DB_PASSWORD=tw_stock_dev_password_2024
```

### Q: 檔案找不到

A: 確認 JSON 檔案路徑正確：
```bash
# 檢查檔案是否存在
ls -lh data/raw/price/2026/01/2026-01-02.json
```

### Q: 重複匯入會發生什麼？

A: 資料表有 UNIQUE 約束 (trade_date, stock_id)，重複匯入會報錯。如需更新資料，請先刪除舊資料：
```sql
DELETE FROM stock_prices WHERE trade_date = '2026-01-02';
```

### Q: 如何批次匯入整個月或整年的資料？

A: 使用 `--start` 和 `--end` 參數：
```bash
# 匯入 2026 年 1 月
DB_PASSWORD=tw_stock_dev_password_2024 \
python scripts/data-importer/import_data.py \
  --start 2026-01-01 --end 2026-01-31
```

## 環境變數

| 變數 | 說明 | 預設值 |
|------|------|--------|
| `DB_TYPE` | 資料庫類型 | `postgresql` |
| `DB_HOST` | 資料庫主機 | `localhost` |
| `DB_PORT` | 資料庫埠號 | `5432` |
| `DB_NAME` | 資料庫名稱 | `tw_stock` |
| `DB_USER` | 資料庫使用者 | `postgres` |
| `DB_PASSWORD` | 資料庫密碼 | （必填） |

## 相關文件

- [Data Importer Service](../../services/data-importer/README.md) - 匯入服務完整文檔
- [Database Schema](../../database/schemas/README.md) - 資料庫結構說明
- [資料收集腳本](../run_collection.py) - 資料收集工具
