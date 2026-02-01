# PostgreSQL 資料庫部署

台股資料收集系統的 PostgreSQL 資料庫服務配置。

---

## 🚀 快速開始

### 1. 準備環境

```bash
cd deployment/database/postgresql

# 複製環境變數範本
cp .env.example .env

# 編輯 .env 並設定 POSTGRES_PASSWORD
nano .env
```

### 2. 啟動服務

```bash
# 啟動資料庫
docker-compose up -d

# 查看日誌
docker-compose logs -f

# 檢查狀態
docker-compose ps
```

### 3. 驗證安裝

```bash
# 連線到資料庫
docker-compose exec postgres psql -U postgres -d tw_stock

# 查看資料表
\dt

# 查看索引
\di

# 離開
\q
```

---

## 📋 管理操作

### 資料庫連線

```bash
# 使用 psql 連線
docker-compose exec postgres psql -U postgres -d tw_stock

# 使用外部工具連線
# Host: localhost
# Port: 5432 (或 .env 中設定的 POSTGRES_PORT)
# Database: tw_stock
# Username: postgres
# Password: (見 .env 的 POSTGRES_PASSWORD)
```

### 備份與還原

```bash
# 備份資料庫
docker-compose exec postgres pg_dump -U postgres -d tw_stock -F c -f /backups/tw_stock_$(date +%Y%m%d).dump

# 還原資料庫
docker-compose exec postgres pg_restore -U postgres -d tw_stock -c /backups/tw_stock_20241227.dump

# 備份到本地
docker-compose exec postgres pg_dump -U postgres -d tw_stock > ../../../database/backups/tw_stock_$(date +%Y%m%d).sql
```

### 維護操作

```bash
# 更新統計資訊
docker-compose exec postgres psql -U postgres -d tw_stock -c "ANALYZE;"

# 回收空間
docker-compose exec postgres psql -U postgres -d tw_stock -c "VACUUM;"

# 完整優化
docker-compose exec postgres psql -U postgres -d tw_stock -c "VACUUM ANALYZE;"
```

---

## 🔧 設定說明

### 環境變數

| 變數名稱 | 說明 | 預設值 | 必填 |
|---------|------|-------|------|
| POSTGRES_DB | 資料庫名稱 | tw_stock | ❌ |
| POSTGRES_USER | 資料庫使用者 | postgres | ❌ |
| POSTGRES_PASSWORD | 資料庫密碼 | - | ✅ |
| POSTGRES_PORT | 連接埠 | 5432 | ❌ |
| NETWORK_NAME | Docker 網路名稱 | tw-stock-network | ❌ |

### 資料持久化

資料儲存在 Docker Volume `tw-stock-postgres-data` 中：

```bash
# 查看 Volume
docker volume ls | grep postgres

# 查看 Volume 詳細資訊
docker volume inspect tw-stock-postgres-data

# 刪除 Volume（⚠️ 會刪除所有資料）
docker volume rm tw-stock-postgres-data
```

---

## 🔗 與其他服務整合

### 與資料匯入器整合

```bash
# 先啟動資料庫
cd deployment/database/postgresql
docker-compose up -d

# 等待資料庫就緒
sleep 10

# 啟動資料匯入管道
cd ../data-import-pipeline
docker-compose up -d
```

---

## 🛠️ 疑難排解

### 資料庫無法啟動

```bash
# 查看日誌
docker-compose logs postgres

# 檢查設定
docker-compose config

# 重新建立容器
docker-compose down
docker-compose up -d
```

### 連線被拒絕

```bash
# 檢查服務狀態
docker-compose ps

# 檢查健康狀態
docker-compose exec postgres pg_isready -U postgres

# 檢查連接埠
netstat -an | grep 5432
```

### 效能問題

```bash
# 查看連線數
docker-compose exec postgres psql -U postgres -d tw_stock -c "SELECT count(*) FROM pg_stat_activity;"

# 查看慢查詢
docker-compose exec postgres psql -U postgres -d tw_stock -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

---

**最後更新**: 2026-02-01
