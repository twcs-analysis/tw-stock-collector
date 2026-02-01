# PostgreSQL 快速參考指南

## 🚀 快速連線

```bash
# 方法 1: 使用 Docker（推薦）
docker exec -i tw-stock-postgres psql -U postgres -d tw_stock

# 方法 2: 使用本地 psql
psql -h localhost -p 5432 -U postgres -d tw_stock
# 密碼: tw_stock_dev_password_2024
```

---

## 🔍 基本查詢指令

### 查看所有表格
```sql
\dt
```

### 查看表格結構
```sql
\d stocks
\d stock_analysis_daily
```

### 查看所有索引
```sql
\di
```

### 離開
```sql
\q
```

---

## 📊 常用 SQL 查詢

### 1. 查詢股票列表
```sql
SELECT * FROM stocks ORDER BY stock_id;
```

### 2. 查詢技術分析資料
```sql
SELECT
    trade_date,
    stock_id,
    close_price,
    ma_5, ma_20,
    rsi_14,
    vol_ratio
FROM stock_analysis_daily
WHERE stock_id = '2330'
ORDER BY trade_date DESC
LIMIT 10;
```

### 3. 均線多頭排列選股
```sql
SELECT
    stock_id,
    close_price,
    ma_5, ma_20, ma_60,
    vol_ratio
FROM stock_analysis_daily
WHERE trade_date = '2024-12-27'
  AND close_price > ma_5
  AND ma_5 > ma_20
  AND ma_20 > ma_60
ORDER BY vol_ratio DESC;
```

### 4. RSI 超賣選股
```sql
SELECT
    stock_id,
    close_price,
    rsi_14,
    macd_hist
FROM stock_analysis_daily
WHERE trade_date = '2024-12-27'
  AND rsi_14 < 30
ORDER BY rsi_14 ASC;
```

### 5. 外資買超排行
```sql
SELECT
    ii.stock_id,
    s.stock_name,
    ii.foreign_net,
    ii.total_net
FROM institutional_investors ii
JOIN stocks s ON ii.stock_id = s.stock_id
WHERE ii.trade_date = '2024-12-27'
ORDER BY ii.foreign_net DESC
LIMIT 20;
```

---

## 🔧 管理指令

### 驗證資料庫
```bash
./deployment/database/postgresql/verify_db.sh
```

### 查看日誌
```bash
docker-compose -f deployment/database/postgresql/docker-compose.yml logs -f
```

### 停止資料庫
```bash
docker-compose -f deployment/database/postgresql/docker-compose.yml down
```

### 備份資料庫
```bash
docker exec tw-stock-postgres pg_dump -U postgres -d tw_stock > backup_$(date +%Y%m%d).sql
```

---

## 📖 詳細文檔

- [完整查詢範例](../../docs/database/QUERY_EXAMPLES.md)
- [Schema 設計](../../database/README.md)
- [部署說明](README.md)

---

**連線資訊**:
- Host: localhost
- Port: 5432
- Database: tw_stock
- Username: postgres
- Password: tw_stock_dev_password_2024
