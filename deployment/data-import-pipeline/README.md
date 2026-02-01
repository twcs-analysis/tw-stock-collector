# 資料匯入管道 (Data Import Pipeline)

完整的台股資料收集、匯入與儲存管道。

---

## 🎯 功能概述

此部署配置包含三個核心服務：

1. **PostgreSQL** - 資料庫服務
2. **Data Collector** - 從 TWSE/TPEx API 收集資料
3. **Data Importer** - 將 JSON 資料匯入資料庫

服務啟動順序：
```
PostgreSQL → Collector → Importer
```

---

## 🚀 快速開始

### 1. 準備環境

```bash
cd deployment/data-import-pipeline

# 複製環境變數範本
cp .env.example .env

# 編輯 .env 並設定 POSTGRES_PASSWORD
nano .env
```

### 2. 收集並匯入今日資料

```bash
# 啟動管道（預設收集最近交易日）
docker-compose up

# 背景執行
docker-compose up -d

# 查看日誌
docker-compose logs -f
```

### 3. 收集並匯入指定日期

```bash
# 編輯 .env，設定參數
COLLECTOR_ARGS=--date 2024-12-27
IMPORTER_ARGS=--date 2024-12-27

# 啟動
docker-compose up
```

### 4. 回補歷史資料

```bash
# 編輯 .env
COLLECTOR_ARGS=--start 2024-12-01 --end 2024-12-31
IMPORTER_ARGS=--start 2024-12-01 --end 2024-12-31

# 啟動
docker-compose up
```

---

## 📋 管理操作

### 查看服務狀態

```bash
# 查看所有服務
docker-compose ps

# 查看特定服務日誌
docker-compose logs postgres
docker-compose logs collector
docker-compose logs importer

# 即時追蹤日誌
docker-compose logs -f importer
```

### 重新執行匯入

```bash
# 停止並移除容器
docker-compose down

# 修改 .env 參數後重新執行
docker-compose up
```

### 連線到資料庫

```bash
# 使用 psql
docker-compose exec postgres psql -U postgres -d tw_stock

# 查看已匯入的資料
SELECT trade_date, COUNT(*) FROM stock_prices GROUP BY trade_date ORDER BY trade_date DESC LIMIT 10;
```

### 停止服務

```bash
# 停止所有服務
docker-compose down

# 停止並刪除資料庫資料
docker-compose down -v
```

---

## 🔧 設定說明

### Collector 參數

| 參數 | 說明 | 範例 |
|------|------|------|
| `--date` | 指定收集日期 | `--date 2024-12-27` |
| `--types` | 指定收集類型 | `--types price margin` |
| `--start / --end` | 回補日期範圍 | `--start 2024-12-01 --end 2024-12-31` |
| `--skip-trading-day-check` | 跳過交易日檢查 | `--skip-trading-day-check` |

### Importer 參數

| 參數 | 說明 | 範例 |
|------|------|------|
| `--date` | 指定匯入日期 | `--date 2024-12-27` |
| `--types` | 指定匯入類型 | `--types price institutional` |
| `--start / --end` | 回補日期範圍 | `--start 2024-12-01 --end 2024-12-31` |
| `--batch-size` | 批次大小 | `--batch-size 1000` |

### 可用的資料類型

- `price` - 價格資料
- `institutional` - 三大法人
- `margin` - 融資融券
- `lending` - 借券賣出
- `top20_volume` - 成交量前20名

---

## 📊 資料流程

```
┌─────────────┐
│  TWSE API   │
│  TPEx API   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Collector  │  收集原始資料
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ data/raw/   │  JSON 檔案
│  ├─ price/  │
│  ├─ margin/ │
│  └─ ...     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Importer   │  匯入資料庫
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ PostgreSQL  │  結構化儲存
└─────────────┘
```

---

## 🛠️ 疑難排解

### Collector 失敗

```bash
# 查看 collector 日誌
docker-compose logs collector

# 常見原因:
# 1. 非交易日 → 使用 --skip-trading-day-check
# 2. API 無回應 → 檢查網路連線
# 3. 日期格式錯誤 → 確認格式為 YYYY-MM-DD
```

### Importer 失敗

```bash
# 查看 importer 日誌
docker-compose logs importer

# 常見原因:
# 1. 資料庫連線失敗 → 檢查 POSTGRES_PASSWORD
# 2. JSON 檔案不存在 → 先執行 collector
# 3. 資料格式錯誤 → 檢查 JSON 檔案內容
```

### 資料庫連線問題

```bash
# 檢查資料庫健康狀態
docker-compose exec postgres pg_isready -U postgres

# 檢查網路
docker network ls | grep stock

# 重建網路
docker-compose down
docker network prune
docker-compose up
```

---

## 📈 效能優化

### 批次匯入

```bash
# 增加批次大小（預設 1000）
IMPORTER_ARGS=--date 2024-12-27 --batch-size 5000
```

### 平行處理

```bash
# 分別收集不同類型的資料
docker-compose run collector --date 2024-12-27 --types price &
docker-compose run collector --date 2024-12-27 --types margin &
wait

# 然後匯入
docker-compose run importer --date 2024-12-27
```

---

## 🔗 相關文件

- [資料庫 Schema](../../database/README.md)
- [PostgreSQL 部署](../database/postgresql/README.md)
- [資料收集器文檔](../../docs/specifications/PHASE1_DATA_COLLECTION.md)

---

**最後更新**: 2026-02-01
