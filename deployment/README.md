# Deployment 目錄

此目錄包含 Docker Compose 相關的部署配置檔案,按照專案三階段架構組織。

## 📁 檔案說明

### docker-compose.yml
**完整版本** - 包含三個階段的所有服務

適用場景:
- 開發環境的完整測試
- 需要同時運行多個階段
- 了解整體系統架構

```bash
# 從專案根目錄執行
cd /path/to/tw-stock-collector

# 啟動資料庫
docker-compose -f deployment/docker-compose.yml up -d postgres

# 執行資料收集 (Phase 1)
docker-compose -f deployment/docker-compose.yml --profile phase1 run --rm collector

# 執行資料匯入 (Phase 2)
docker-compose -f deployment/docker-compose.yml --profile phase2 run --rm importer

# 啟動儀表板 (Phase 3)
docker-compose -f deployment/docker-compose.yml --profile phase3 up -d dashboard
```

### docker-compose.phase1.yml
**Phase 1: 資料擷取與儲存**

功能:
- 運行資料收集器
- 將資料儲存到本地 `data/` 目錄
- 供 Git 版本控制使用

適用場景:
- 本地測試資料收集功能
- 回補歷史資料
- 驗證資料來源連線

```bash
# 執行今天的資料收集
docker-compose -f deployment/docker-compose.phase1.yml up

# 收集指定日期
COLLECTION_DATE=2025-01-28 docker-compose -f deployment/docker-compose.phase1.yml up

# 背景執行
docker-compose -f deployment/docker-compose.phase1.yml up -d
```

**注意**: Phase 1 主要透過 GitHub Actions 自動執行,此 compose 檔案僅用於本地開發測試。

### docker-compose.phase2.yml
**Phase 2: 資料庫設計與匯入**

功能:
- 啟動 PostgreSQL 資料庫
- 執行資料庫初始化 (建表)
- 從 `data/` 目錄匯入資料到資料庫
- 選用: pgAdmin 管理介面

適用場景:
- 建立本地資料庫環境
- 測試資料匯入流程
- 資料查詢與驗證

```bash
# 啟動資料庫
docker-compose -f deployment/docker-compose.phase2.yml up -d postgres

# 等待資料庫就緒
docker-compose -f deployment/docker-compose.phase2.yml logs -f postgres

# 執行資料匯入
docker-compose -f deployment/docker-compose.phase2.yml run --rm importer

# 啟動 pgAdmin (選用)
docker-compose -f deployment/docker-compose.phase2.yml --profile tools up -d pgadmin
# 訪問: http://localhost:5050
```

### docker-compose.phase3.yml
**Phase 3: 數據整理與分析**

功能:
- 運行分析引擎 (計算技術指標、籌碼分析)
- 啟動 Streamlit 儀表板
- 選用: Jupyter Notebook 互動式分析

適用場景:
- 查看視覺化儀表板
- 執行選股策略
- 互動式資料探索

```bash
# 啟動儀表板 (假設 Phase 2 資料庫已運行)
docker-compose -f deployment/docker-compose.phase3.yml up -d dashboard
# 訪問: http://localhost:8501

# 執行分析任務
docker-compose -f deployment/docker-compose.phase3.yml --profile analysis up analyzer

# 啟動 Jupyter (選用)
docker-compose -f deployment/docker-compose.phase3.yml --profile tools up -d jupyter
# 訪問: http://localhost:8888
```

### .env.example
環境變數範本檔案

使用方式:
```bash
# 複製範本
cp deployment/.env.example deployment/.env

# 編輯配置
vim deployment/.env

# 重要: 修改預設密碼!
# DB_PASSWORD=your_secure_password
```

## 🚀 快速開始

### 1. 環境準備

```bash
# 1. 確保已安裝 Docker 和 Docker Compose
docker --version
docker-compose --version

# 2. 複製環境變數範本
cp deployment/.env.example deployment/.env

# 3. 編輯 .env 檔案,至少修改資料庫密碼
vim deployment/.env
```

### 2. Phase 1 - 資料收集 (本地測試)

```bash
# 執行資料收集
docker-compose -f deployment/docker-compose.phase1.yml up

# 檢查收集的資料
ls -lh data/raw/
```

### 3. Phase 2 - 建立資料庫並匯入

```bash
# 啟動資料庫
docker-compose -f deployment/docker-compose.phase2.yml up -d postgres

# 等待資料庫就緒 (約 10-30 秒)
docker-compose -f deployment/docker-compose.phase2.yml logs -f postgres

# 執行資料匯入
docker-compose -f deployment/docker-compose.phase2.yml run --rm importer

# 驗證資料
docker-compose -f deployment/docker-compose.phase2.yml exec postgres \
  psql -U stock_user -d tw_stock -c "SELECT COUNT(*) FROM daily_prices;"
```

### 4. Phase 3 - 啟動儀表板

```bash
# 方式一: 使用 Phase 3 compose (假設資料庫已運行)
docker-compose -f deployment/docker-compose.phase3.yml up -d dashboard

# 方式二: 組合 Phase 2 + Phase 3
docker-compose \
  -f deployment/docker-compose.phase2.yml \
  -f deployment/docker-compose.phase3.yml \
  up -d postgres dashboard

# 訪問儀表板
open http://localhost:8501
```

## 📊 常用命令

### 查看服務狀態

```bash
# 查看所有運行中的容器
docker-compose -f deployment/docker-compose.yml ps

# 查看特定階段
docker-compose -f deployment/docker-compose.phase2.yml ps
```

### 查看日誌

```bash
# 查看所有日誌
docker-compose -f deployment/docker-compose.yml logs

# 跟蹤特定服務
docker-compose -f deployment/docker-compose.yml logs -f postgres
docker-compose -f deployment/docker-compose.yml logs -f dashboard

# 查看最近 100 行
docker-compose -f deployment/docker-compose.yml logs --tail=100 importer
```

### 停止服務

```bash
# 停止所有服務
docker-compose -f deployment/docker-compose.yml down

# 停止並刪除資料卷 (⚠️ 會刪除資料庫資料)
docker-compose -f deployment/docker-compose.yml down -v

# 停止特定階段
docker-compose -f deployment/docker-compose.phase3.yml down
```

### 重建映像檔

```bash
# 重新建置所有映像檔
docker-compose -f deployment/docker-compose.yml build --no-cache

# 重建特定服務
docker-compose -f deployment/docker-compose.yml build --no-cache collector
docker-compose -f deployment/docker-compose.yml build --no-cache dashboard
```

## 🔧 進階用法

### 組合多個 Compose 檔案

```bash
# Phase 2 + Phase 3 一起啟動
docker-compose \
  -f deployment/docker-compose.phase2.yml \
  -f deployment/docker-compose.phase3.yml \
  up -d

# 使用完整版 + 特定 profile
docker-compose \
  -f deployment/docker-compose.yml \
  --profile phase2 \
  --profile phase3 \
  up -d
```

### 覆寫環境變數

```bash
# 臨時覆寫資料庫配置
DB_PASSWORD=new_password \
DB_USER=admin \
docker-compose -f deployment/docker-compose.phase2.yml up -d postgres

# 使用不同的 .env 檔案
docker-compose -f deployment/docker-compose.yml --env-file .env.production up -d
```

### 擴展服務 (Scaling)

```bash
# 不適用 - 本專案服務為單例設計
# 如需擴展,請考慮使用 Kubernetes
```

## 🐛 故障排除

### 資料庫連線失敗

```bash
# 檢查資料庫是否就緒
docker-compose -f deployment/docker-compose.phase2.yml exec postgres pg_isready

# 檢查資料庫日誌
docker-compose -f deployment/docker-compose.phase2.yml logs postgres

# 重啟資料庫
docker-compose -f deployment/docker-compose.phase2.yml restart postgres
```

### 端口被占用

```bash
# 修改 .env 檔案中的端口
STREAMLIT_PORT=8502
DB_PORT=5433

# 或臨時覆寫
STREAMLIT_PORT=8502 docker-compose -f deployment/docker-compose.phase3.yml up -d dashboard
```

### 映像檔建置失敗

```bash
# 清除 Docker 快取
docker system prune -a

# 重新建置
docker-compose -f deployment/docker-compose.yml build --no-cache --pull
```

### 資料卷權限問題

```bash
# macOS/Linux: 確保目錄存在且有寫入權限
mkdir -p data logs output
chmod 755 data logs output

# 如果使用命名卷,檢查卷
docker volume ls
docker volume inspect tw_stock_postgres_data
```

## 📝 最佳實踐

### 1. 環境隔離
- 開發: 使用 `.env`
- 測試: 使用 `.env.test`
- 生產: 使用 `.env.production` (不要 commit!)

### 2. 資料備份
```bash
# 備份資料庫
docker-compose -f deployment/docker-compose.phase2.yml exec postgres \
  pg_dump -U stock_user tw_stock > backup_$(date +%Y%m%d).sql

# 備份資料卷
docker run --rm -v tw_stock_postgres_data:/data \
  -v $(pwd):/backup alpine tar czf /backup/postgres_data_$(date +%Y%m%d).tar.gz /data
```

### 3. 資源限制
在 compose 檔案中添加資源限制:
```yaml
services:
  postgres:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          memory: 512M
```

### 4. 健康檢查
所有關鍵服務都配置了 healthcheck,確保依賴服務就緒後再啟動。

## 🔐 安全建議

1. **修改預設密碼**: 絕不使用 `.env.example` 中的預設密碼
2. **環境變數保護**: 不要 commit `.env` 到 Git
3. **網路隔離**: 使用 Docker 內部網路,只暴露必要端口
4. **最小權限**: 資料卷使用 `:ro` (readonly) 掛載配置檔
5. **定期更新**: 定期更新基礎映像檔 (postgres, python)

## 📚 相關文檔

- [Docker 官方文檔](https://docs.docker.com/)
- [Docker Compose 文檔](https://docs.docker.com/compose/)
- [PostgreSQL Docker 映像檔](https://hub.docker.com/_/postgres)
- [專案 Build 說明](../build/README.md)
- [專案主要 README](../README.md)

---

**維護者**: Jason Huang
**最後更新**: 2025-12-28
