# Stock Data Collector 部署

台股資料收集服務的 Docker 部署配置。

## 📋 功能說明

此服務負責從官方 API 收集台股資料:
- **價量資料**: 開高低收、成交量
- **三大法人**: 外資、投信、自營商買賣超
- **融資融券**: 融資融券餘額與變化
- **借券賣出**: 借券賣出餘額

## 🚀 快速開始

### 1. 環境準備

```bash
# 複製環境變數範例
cp .env.example .env

# 編輯環境變數（選用）
vim .env
```

### 2. 執行資料收集

```bash
# 收集今天的資料
docker-compose up

# 收集指定日期
COLLECTION_DATE=2024-12-27 docker-compose up

# 只收集特定類型
COLLECTION_DATE=2024-12-27 COLLECTION_TYPES="price margin" docker-compose up

# 背景執行
docker-compose up -d
```

### 3. 檢查結果

```bash
# 查看收集的資料
ls -lh ../../data/raw/price/2024/12/

# 查看日誌
docker-compose logs
```

## ⚙️ 環境變數

| 變數 | 說明 | 預設值 |
|-----|------|--------|
| `COLLECTION_DATE` | 收集日期 | today |
| `COLLECTION_TYPES` | 資料類型（空格分隔） | price institutional margin lending |
| `LOG_LEVEL` | 日誌等級 | INFO |
| `TZ` | 時區 | Asia/Taipei |
| `NETWORK_NAME` | Docker 網路名稱 | tw-stock-network |

## 🔧 進階用法

### 回補歷史資料

```bash
# 使用迴圈回補多日資料
for date in 2025-01-{01..31}; do
  COLLECTION_DATE=$date docker-compose up
  sleep 5
done
```

### 自訂配置

修改 `docker-compose.yml` 中的 volumes:
```yaml
volumes:
  - ../../data:/app/data
  - /path/to/custom/config:/app/config:ro
```

## 🐛 故障排除

### 映像檔建置失敗

```bash
# 從專案根目錄重新建置
cd ../..
docker build -f build/Dockerfile -t tw-stock-collector:latest .
```

### 資料目錄權限問題

```bash
# 確保資料目錄存在且有寫入權限
mkdir -p ../../data
chmod 755 ../../data
```

### 清除 Docker 快取

```bash
docker system prune -a
docker-compose build --no-cache
```

## 📝 注意事項

**主要部署方式:**
- 本專案主要透過 **GitHub Actions** 自動化執行
- 每交易日 21:30 自動收集並提交資料
- 此 Docker Compose 配置主要用於**本地開發測試**

**適用場景:**
- 本地測試資料收集功能
- 回補歷史資料
- 驗證資料源連線
- 開發新功能時的測試環境

## 📖 相關文件

- **[部署總覽](../README.md)** - 整體部署架構
- **[專案 README](../../README.md)** - 專案說明
- **[Dockerfile](../../build/Dockerfile)** - 映像檔建置腳本

---

**最後更新**: 2026-02-01
