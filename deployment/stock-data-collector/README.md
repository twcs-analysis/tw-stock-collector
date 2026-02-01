# Stock Data Collector 部署

台股資料收集服務的 Docker 部署配置。

## 📋 功能說明

此服務負責從官方 API 收集台股資料:
- **價量資料**: 開高低收、成交量
- **三大法人**: 外資、投信、自營商買賣超
- **融資融券**: 融資融券餘額與變化
- **借券賣出**: 借券賣出餘額
- **成交量前 20 名**: 當日成交量最大的 20 檔股票

## 🚀 快速開始

### 1. 環境準備

```bash
# 複製環境變數範例
cp .env.example .env

# 編輯環境變數（選用）
vim .env
```

### 2. 修改收集日期

編輯 `docker-compose.yml` 的 command 參數:

```yaml
command: ["--date", "2024-12-27", "--skip-trading-day-check"]
# 將日期改為您要收集的日期
```

### 3. 執行資料收集

```bash
# 執行收集
docker-compose up

# 背景執行
docker-compose up -d

# 查看日誌
docker-compose logs -f
```

### 4. 檢查結果

```bash
# 查看收集的資料
ls -lh ../../data/raw/price/2024/12/

# 查看資料內容
cat ../../data/raw/price/2024/12/2024-12-27.json | jq '.metadata'
```

## ⚙️ 環境變數

在 `.env` 檔案中可設定:

| 變數 | 說明 | 預設值 |
|-----|------|--------|
| `LOG_LEVEL` | 日誌等級 | INFO |
| `TZ` | 時區 | Asia/Taipei |
| `NETWORK_NAME` | Docker 網路名稱 | tw-stock-network |

## 🔧 進階用法

### 修改收集參數

編輯 `docker-compose.yml` 的 command:

```yaml
# 收集特定日期
command: ["--date", "2025-01-15", "--skip-trading-day-check"]

# 只收集特定類型
command: ["--date", "2025-01-15", "--types", "price", "margin", "--skip-trading-day-check"]

# 不跳過交易日檢查
command: ["--date", "2025-01-15"]
```

### 回補歷史資料

```bash
# 方法 1: 手動修改日期並執行
# 編輯 docker-compose.yml 中的日期
vim docker-compose.yml
docker-compose up

# 方法 2: 使用 Python 腳本（推薦）
cd ../..
python scripts/backfill.py --start 2025-01-01 --end 2025-01-31
```

### 自訂資料目錄

修改 `docker-compose.yml` 中的 volumes:

```yaml
volumes:
  - /custom/path/data:/app/data
  - ../../config:/app/config:ro
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

### 容器執行失敗

```bash
# 查看完整日誌
docker-compose logs

# 進入容器除錯
docker run -it --rm \
  -v $(pwd)/../../data:/app/data \
  tw-stock-collector:latest bash
```

## 📝 使用說明

### 收集資料類型

可收集的資料類型 (`--types` 參數):
- `price`: 價量資料
- `institutional`: 三大法人買賣超
- `margin`: 融資融券
- `lending`: 借券賣出
- `top20_volume`: 成交量前 20 名

### 日期格式

- 日期格式: `YYYY-MM-DD` (例如: `2024-12-27`)
- 特殊值: `today`, `yesterday`
- 建議加上 `--skip-trading-day-check` 避免非交易日檢查

### 輸出位置

資料會儲存在:
```
../../data/raw/
├── price/2024/12/2024-12-27.json
├── institutional/2024/12/2024-12-27.json
├── margin/2024/12/2024-12-27.json
├── lending/2024/12/2024-12-27.json
└── top20_volume/2024/12/2024-12-27.json
```

## 📊 測試結果

成功測試收集 2024-12-27 資料:
- **price**: 1,954 筆 (604 KB)
- **margin**: 1,819 筆 (980 KB)
- **institutional**: 1,721 筆 (4.1 MB)
- **lending**: 1,014 筆 (551 KB)
- **top20_volume**: 20 筆 (6.6 KB)

## 📝 注意事項

**主要部署方式:**
- 本專案主要透過 **GitHub Actions** 自動化執行
- 每交易日 21:30 (台北時間) 自動收集並提交資料
- 此 Docker Compose 配置主要用於**本地開發測試**

**適用場景:**
- 本地測試資料收集功能
- 回補歷史資料
- 驗證資料源連線
- 開發新功能時的測試環境

**不建議用途:**
- 不建議用於生產環境長期運行
- 建議使用 GitHub Actions 進行自動化收集

## 📖 相關文件

- **[部署總覽](../README.md)** - 整體部署架構
- **[專案 README](../../README.md)** - 專案說明
- **[Dockerfile](../../build/Dockerfile)** - 映像檔建置腳本

---

**最後更新**: 2026-02-01
**測試狀態**: ✅ 已驗證可正常運作
