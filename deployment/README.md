# Deployment 目錄

此目錄包含台股資料收集系統的 Docker 部署配置。

## 📁 檔案說明

### docker-compose.yml
資料收集服務的 Docker Compose 配置檔。

**功能:**
- 運行資料收集器
- 將資料儲存到本地 `data/` 目錄
- 供 Git 版本控制使用

**使用方式:**

```bash
# 從專案根目錄執行
cd /path/to/tw-stock-collector

# 收集指定日期的資料
COLLECTION_DATE=2025-01-28 docker-compose -f deployment/docker-compose.yml up

# 使用特定 profile 執行收集
docker-compose --profile collection up

# 背景執行
docker-compose -f deployment/docker-compose.yml up -d
```

**環境變數:**
- `COLLECTION_DATE`: 收集日期（預設：today）
- `COLLECTION_TYPES`: 資料類型（預設：price institutional margin lending）
- `LOG_LEVEL`: 日誌等級（預設：INFO）

### .env.example
環境變數範例檔案。

**設定步驟:**
```bash
# 複製範例檔案
cp .env.example .env

# 編輯環境變數（選用）
vim .env
```

### .dockerignore
Docker build 時忽略的檔案清單。

## 🚀 快速開始

### 1. 建置 Docker 映像檔

```bash
# 從專案根目錄執行
docker build -f build/Dockerfile -t tw-stock-collector:latest .
```

### 2. 執行資料收集

```bash
# 收集今天的資料
docker-compose -f deployment/docker-compose.yml up

# 收集指定日期
COLLECTION_DATE=2024-12-27 docker-compose -f deployment/docker-compose.yml up

# 只收集特定類型
COLLECTION_DATE=2024-12-27 COLLECTION_TYPES="price margin" \
  docker-compose -f deployment/docker-compose.yml up
```

### 3. 檢查結果

```bash
# 查看收集的資料
ls -lh ../data/raw/price/2024/12/

# 查看日誌
docker-compose -f deployment/docker-compose.yml logs
```

## 📝 注意事項

**主要部署方式:**
- Phase 1 資料收集主要透過 **GitHub Actions** 自動執行
- 每交易日 21:30 自動收集並提交資料
- 此 Docker Compose 配置主要用於**本地開發測試**

**適用場景:**
- 本地測試資料收集功能
- 回補歷史資料
- 驗證資料來源連線
- 開發新功能時的測試環境

## 🔧 進階設定

### 自訂網路名稱

編輯 `.env` 檔案:
```bash
NETWORK_NAME=my-custom-network
```

### 掛載自訂配置

修改 `docker-compose.yml` 中的 volumes:
```yaml
volumes:
  - ../data:/app/data
  - ../logs:/app/logs
  - /path/to/custom/config:/app/config:ro
```

## 🐛 故障排除

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
mkdir -p data logs
chmod 755 data logs
```

## 📖 相關文件

- **[主要 README](../README.md)** - 專案整體說明
- **[Dockerfile](../build/Dockerfile)** - Docker 映像檔建置腳本
- **[GitHub Actions](../.github/workflows/)** - 自動化收集設定

---

**最後更新**: 2026-02-01
