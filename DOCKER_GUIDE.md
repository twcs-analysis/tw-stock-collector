# Docker 使用指南

Phase 1 台股資料收集系統的 Docker 部署與測試指南。

## 目錄

- [快速開始](#快速開始)
- [Docker 架構](#docker-架構)
- [使用方式](#使用方式)
- [環境變數](#環境變數)
- [常見問題](#常見問題)

## 快速開始

### 1. 登入 GitHub Container Registry (GHCR)

```bash
# 使用 GitHub Personal Access Token 登入
echo $GHCR_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin

# 或使用互動式登入
docker login ghcr.io
```

### 2. 拉取映像檔

```bash
# 拉取最新的 Phase 1 映像檔
docker pull ghcr.io/twcs-analysis/tw-stock-collector:phase1-latest
```

### 3. 執行測試

```bash
# 使用 docker-compose 執行測試
docker-compose up phase1-test

# 或直接使用 Docker
docker run --rm ghcr.io/twcs-analysis/tw-stock-collector:phase1-latest
```

> **注意**: 如果你想在本地建置映像檔而不是使用 GHCR,可以執行:
> ```bash
> docker build -t tw-stock-collector:phase1 .
> ```

### 4. 查看結果

測試完成後會顯示：
```
======================================================================
測試總結
======================================================================
總測試數: 6
通過: 6
失敗: 0
成功率: 100.0%
======================================================================
```

## Docker 架構

本專案提供三個 Docker 服務：

### 1. phase1-test（測試服務）

執行 Phase 1 完整測試。

```bash
docker-compose up phase1-test
```

**特點：**
- 預設執行：`python scripts/test_phase1.py --skip-api`
- 自動執行所有基礎測試
- 無需 API Token

### 2. phase1-collector（收集服務）

執行資料收集。

```bash
# 收集昨天的資料
docker-compose --profile collection up phase1-collector

# 收集指定日期
COLLECTION_DATE=2025-01-28 docker-compose --profile collection up phase1-collector

# 只收集特定類型
COLLECTION_TYPES="price institutional" docker-compose --profile collection up phase1-collector
```

**環境變數：**
- `COLLECTION_DATE`: 收集日期（預設：yesterday）
- `COLLECTION_TYPES`: 資料類型（預設：price institutional margin lending）
- `FINMIND_API_TOKEN`: FinMind API Token（選用）

### 3. phase1-backfill（回補服務）

批次回補歷史資料。

```bash
# 回補最近 7 天
docker-compose --profile backfill up phase1-backfill

# 回補指定日期範圍
START_DATE=2025-01-01 END_DATE=2025-01-31 \
docker-compose --profile backfill up phase1-backfill

# 回補指定天數
START_DATE=2025-01-01 BACKFILL_DAYS=30 \
docker-compose --profile backfill up phase1-backfill
```

**環境變數：**
- `START_DATE`: 開始日期（必填）
- `END_DATE`: 結束日期（與 BACKFILL_DAYS 二選一）
- `BACKFILL_DAYS`: 回補天數（與 END_DATE 二選一，預設：7）
- `BACKFILL_TYPES`: 資料類型（預設：price institutional margin lending）
- `FINMIND_API_TOKEN`: FinMind API Token（選用）

## 使用方式

### 基礎測試

```bash
# 建置並執行測試
docker-compose up --build phase1-test

# 查看測試日誌
docker-compose logs phase1-test

# 清理容器
docker-compose down
```

### 資料收集

```bash
# 1. 設定環境變數（可選）
export FINMIND_API_TOKEN="your_token_here"

# 2. 收集昨天的資料
docker-compose --profile collection up phase1-collector

# 3. 查看收集的資料
ls -R data/raw/

# 4. 查看日誌
docker-compose logs phase1-collector
```

### 歷史回補

```bash
# 回補 2025 年 1 月的所有資料
START_DATE=2025-01-01 END_DATE=2025-01-31 \
docker-compose --profile backfill up phase1-backfill

# 只回補價格資料
START_DATE=2025-01-01 BACKFILL_DAYS=7 BACKFILL_TYPES="price" \
docker-compose --profile backfill up phase1-backfill
```

### 互動式使用

進入容器執行自訂命令：

```bash
# 啟動容器並進入 shell
docker run -it --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  tw-stock-collector:phase1 bash

# 在容器內執行命令
python scripts/init_stock_list.py
python scripts/run_collection.py --date 2025-01-28
python scripts/test_phase1.py --verbose
```

## 環境變數

### 全域環境變數

可透過 `.env` 檔案設定：

```bash
# 建立 .env 檔案
cat > .env << EOF
FINMIND_API_TOKEN=your_token_here
TZ=Asia/Taipei
