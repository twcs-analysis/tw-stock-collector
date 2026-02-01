# GitHub Actions 工作流程

本專案使用 GitHub Actions 進行自動化資料收集與 CI/CD。

## 📁 工作流程列表

### 1. ci.yml - 持續整合

**觸發條件**:
- Push 到 `main` 或 `develop` 分支
- Pull Request 到 `main` 或 `develop`
- 手動觸發 (workflow_dispatch)

**執行步驟**:
1. **測試** - 執行 Python 測試套件
2. **建置 Docker** - 建置 data-collector 微服務映像檔
3. **推送映像檔** - 推送到 GitHub Container Registry

**映像檔標籤**:
- `ghcr.io/<owner>/<repo>/data-collector:latest` - main 分支最新版
- `ghcr.io/<owner>/<repo>/data-collector:<branch>` - 分支名稱
- `ghcr.io/<owner>/<repo>/data-collector:<sha>` - Commit SHA

### 2. daily-collection.yml - 每日資料收集

**觸發條件**:
- 排程: 每週一至週六 21:30 (台灣時間)
- 手動觸發可指定日期與資料類型

**執行步驟**:
1. Checkout 程式碼
2. 拉取 data-collector 映像檔
3. 執行資料收集
4. 驗證收集結果
5. Commit 並 push 到 Git
6. 上傳日誌檔案
7. 失敗時自動建立 Issue

**手動觸發範例**:
```bash
# 使用 GitHub CLI
gh workflow run daily-collection.yml \
  -f date=2024-12-27 \
  -f types="price institutional margin"
```

### 3. backfill.yml - 歷史資料回補

**觸發條件**:
- 僅手動觸發

**輸入參數**:
- `start_date` - 開始日期 (必填)
- `end_date` - 結束日期 (選填)
- `days` - 回補天數 (與 end_date 擇一)
- `types` - 資料類型
- `batch_size` - 批次大小

**執行步驟**:
1. 計算日期範圍
2. 拉取 data-collector 映像檔
3. 批次執行資料收集
4. 驗證資料完整性
5. Commit 並 push 到 Git

**手動觸發範例**:
```bash
# 回補 30 天資料
gh workflow run backfill.yml \
  -f start_date=2024-12-01 \
  -f days=30 \
  -f types="price institutional margin lending"

# 指定日期區間
gh workflow run backfill.yml \
  -f start_date=2024-12-01 \
  -f end_date=2024-12-31
```

### 4. weekly-collection.yml - 每週資料收集

**觸發條件**:
- 排程: 每週日執行
- 收集過去一週的資料

## 🐳 Docker 映像檔架構

### 舊版 (Phase 1)

```
ghcr.io/<owner>/<repo>:phase1-latest
└── 使用 build/Dockerfile (已棄用)
```

### 新版 (微服務架構)

```
ghcr.io/<owner>/<repo>/data-collector:latest
├── 使用 build/data-collector/Dockerfile
├── 包含 services/common 共用程式庫
├── 包含 services/data-collector/app
└── 向後相容舊版 scripts/
```

## 🔄 遷移說明

### 從舊版遷移到新版

**已完成的變更**:

1. **CI/CD (ci.yml)**
   - ❌ 舊版: 建置 `build/Dockerfile` → `:phase1-latest`
   - ✅ 新版: 建置 `build/data-collector/Dockerfile` → `/data-collector:latest`

2. **每日收集 (daily-collection.yml)**
   - ❌ 舊版: 使用 `:phase1-latest` 映像檔
   - ✅ 新版: 使用 `/data-collector:latest` 映像檔

3. **歷史回補 (backfill.yml)**
   - ❌ 舊版: 使用 `:phase1-latest` + `/app/scripts/backfill.py`
   - ✅ 新版: 使用 `/data-collector:latest` + `/app/app/backfill.py`

### 向後相容性

data-collector 映像檔包含：
- ✅ `services/common/` - 新版共用程式庫
- ✅ `services/data-collector/app/` - 新版服務程式碼
- ✅ `src/` - 舊版原始碼 (保留)
- ✅ `scripts/run_collection.py` - 舊版入口點 (保留)
- ✅ `scripts/backfill.py` - 舊版回補腳本 (保留)

因此，現有的 GitHub Actions 工作流程無需修改即可運作。

## 🚀 本地測試工作流程

### 測試 CI 流程

```bash
# 建置 Docker 映像檔
docker build -f build/data-collector/Dockerfile -t test-collector .

# 測試映像檔
docker run --rm test-collector --help
docker run --rm -v $(pwd)/data:/app/data test-collector --date yesterday
```

### 模擬每日收集

```bash
# 拉取映像檔
docker pull ghcr.io/<owner>/<repo>/data-collector:latest

# 執行收集
docker run --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  ghcr.io/<owner>/<repo>/data-collector:latest \
  --date yesterday

# 檢查結果
find data/raw -name "*.json" | tail -10
```

### 模擬歷史回補

```bash
docker run --rm \
  --entrypoint python \
  -v $(pwd)/data:/app/data \
  ghcr.io/<owner>/<repo>/data-collector:latest \
  /app/app/backfill.py \
  --start 2024-12-01 \
  --end 2024-12-31
```

## 🔐 Secrets 設定

需要在 GitHub Repository 設定以下 Secrets:

- `PERSONAL_ACCESS_TOKEN` - GitHub Personal Access Token
  - 權限: `write:packages`, `contents:write`
  - 用途: 推送 Docker 映像檔到 GHCR、Commit 資料到 Git

## 📊 監控與除錯

### 查看工作流程執行狀態

```bash
# 列出最近的執行
gh run list --workflow=daily-collection.yml --limit 10

# 查看特定執行的日誌
gh run view <run-id> --log

# 下載 artifacts
gh run download <run-id>
```

### 常見問題

**Q: Docker 映像檔拉取失敗?**
```bash
# 檢查映像檔是否存在
docker pull ghcr.io/<owner>/<repo>/data-collector:latest

# 檢查 GHCR 權限
echo $GITHUB_TOKEN | docker login ghcr.io -u <username> --password-stdin
```

**Q: 資料收集失敗?**
- 檢查 workflow logs
- 下載 collection-logs artifact
- 查看 Issues 是否有自動建立的錯誤報告

**Q: Commit 失敗?**
- 檢查 `PERSONAL_ACCESS_TOKEN` 權限
- 確認 token 未過期

## 🔗 相關文件

- [Services README](../../services/README.md) - 微服務架構說明
- [Build README](../../build/README.md) - Docker 建置指南
- [Data Collector README](../../services/data-collector/README.md) - 服務詳細說明

---

**最後更新**: 2026-02-01
**維護者**: Jason Huang
