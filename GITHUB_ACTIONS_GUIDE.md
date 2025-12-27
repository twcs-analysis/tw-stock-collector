# GitHub Actions 使用指南

Phase 1 台股資料收集系統的 GitHub Actions 自動化部署指南。

## 目錄

- [快速開始](#快速開始)
- [工作流程說明](#工作流程說明)
- [環境變數設定](#環境變數設定)
- [使用方式](#使用方式)
- [故障排除](#故障排除)
- [最佳實踐](#最佳實踐)

---

## 快速開始

### 1. Fork 專案並設定 Secrets

1. **Fork 此專案**到你的 GitHub 帳號

2. **設定 Repository Secrets**（Settings → Secrets and variables → Actions）

   ```
   FINMIND_API_TOKEN=你的FinMind_API_Token
   ```

   > 💡 沒有 Token 也可以使用，但會受到 API 頻率限制

3. **啟用 GitHub Actions**
   - 進入 Actions 頁面
   - 點擊 "I understand my workflows, go ahead and enable them"

4. **啟用 GitHub Packages**
   - 確保 Settings → Actions → General → Workflow permissions 設為 "Read and write permissions"

### 2. 驗證設定

手動觸發 CI 工作流程：

1. 進入 Actions → CI - Test and Build
2. 點擊 "Run workflow"
3. 等待執行完成（約 3-5 分鐘）

成功後會看到：
- ✅ Run Tests (測試通過)
- ✅ Build Docker Image (映像檔建置成功)
- ✅ CI Summary (總結通過)

---

## 工作流程說明

本專案包含 4 個 GitHub Actions 工作流程：

### 1. CI - Test and Build
**檔案**: `.github/workflows/ci.yml`

**觸發條件**:
- Push 到 `main` 或 `develop` 分支
- Pull Request 到 `main` 或 `develop`
- 手動觸發

**功能**:
1. ✅ 執行 Phase 1 測試
2. 🐳 建置並推送 Docker 映像檔到 GHCR
3. 📊 產生測試報告

**Docker 映像標籤**:
- `ghcr.io/<你的帳號>/tw-stock-collector:phase1-latest` (預設分支)
- `ghcr.io/<你的帳號>/tw-stock-collector:main` (main 分支)
- `ghcr.io/<你的帳號>/tw-stock-collector:develop` (develop 分支)
- `ghcr.io/<你的帳號>/tw-stock-collector:pr-123` (Pull Request)
- `ghcr.io/<你的帳号>/tw-stock-collector:main-abc1234` (commit SHA)

**支援平台**:
- `linux/amd64`
- `linux/arm64`

---

### 2. Daily Data Collection
**檔案**: `.github/workflows/daily-collection.yml`

**自動執行時間**:
- 每個交易日（週一至週五）台北時間 18:00

**收集資料**:
- 📈 價量資料 (price)
- 🏦 法人籌碼 (institutional)
- 💰 融資融券 (margin)
- 📊 借券賣出 (lending)

**執行流程**:
1. 從 GHCR 拉取最新 Docker 映像
2. 執行資料收集
3. 將收集的資料提交到 Git
4. 上傳收集日誌（保留 30 天）
5. 失敗時自動建立 Issue

---

### 3. Weekly Data Collection
**檔案**: `.github/workflows/weekly-collection.yml`

**自動執行時間**:
- 每週六台北時間 10:00

**收集資料**:
- 👥 股權分散表 (ownership)
- 📊 月營收 (revenue，每月 1-10 日)

**特點**:
- 股權分散表每週更新一次
- 月營收僅在每月 1-10 日執行

---

### 4. Historical Data Backfill
**檔案**: `.github/workflows/backfill.yml`

**觸發條件**:
- 僅手動觸發

**功能**:
- 批次回補歷史資料
- 可指定日期範圍或天數
- 可自訂批次大小
- 支援多種資料類型

---

## 環境變數設定

### Repository Secrets

在 Settings → Secrets and variables → Actions 中設定：

| Secret 名稱 | 必要性 | 說明 |
|------------|--------|------|
| `FINMIND_API_TOKEN` | 選用 | FinMind API Token，可提高頻率限制 |
| `GITHUB_TOKEN` | 自動 | GitHub 自動提供，用於推送 Docker 映像和提交資料 |

### 工作流程環境變數

各工作流程可用的環境變數：

#### Daily Collection
- `COLLECTION_DATE`: 收集日期（預設：yesterday）
- `COLLECTION_TYPES`: 資料類型（預設：price institutional margin lending）

#### Weekly Collection
- `COLLECTION_DATE`: 收集日期（預設：yesterday）

#### Backfill
- `START_DATE`: 開始日期（必填）
- `END_DATE`: 結束日期（選填）
- `BACKFILL_DAYS`: 回補天數（選填）
- `BACKFILL_TYPES`: 資料類型（預設：price institutional margin lending）
- `BATCH_SIZE`: 批次大小（預設：7）

---

## 使用方式

### 手動觸發每日收集

1. 進入 **Actions** → **Daily Data Collection**
2. 點擊 **Run workflow**
3. 設定參數（可選）：
   ```
   date: 2025-01-28
   types: price institutional
   ```
4. 點擊 **Run workflow** 執行

### 手動觸發週資料收集

```
Actions → Weekly Data Collection → Run workflow
```

### 回補歷史資料

**範例 1: 回補最近 30 天**
```
Actions → Historical Data Backfill → Run workflow

start_date: 2025-01-01
days: 30
types: price institutional margin lending
batch_size: 7
```

**範例 2: 回補指定日期範圍**
```
start_date: 2025-01-01
end_date: 2025-01-31
types: price
batch_size: 10
```

**範例 3: 僅回補價格資料**
```
start_date: 2024-01-01
days: 365
types: price
batch_size: 30
```

### 查看執行結果

1. **查看日誌**
   - Actions → 選擇工作流程 → 點擊執行記錄
   - 展開各步驟查看詳細日誌

2. **下載日誌檔案**
   - 在執行記錄頁面底部找到 "Artifacts"
   - 下載 `collection-logs-*` 或 `backfill-logs-*`

3. **檢查提交的資料**
   ```bash
   # Clone 專案後查看
   ls -R data/raw/
   ```

---

## Docker 映像使用

### 從 GHCR 拉取映像

```bash
# 登入 GHCR (需要 Personal Access Token)
echo $GITHUB_TOKEN | docker login ghcr.io -u <你的帳號> --password-stdin

# 拉取最新映像
docker pull ghcr.io/<你的帳號>/tw-stock-collector:phase1-latest

# 執行測試
docker run --rm ghcr.io/<你的帳號>/tw-stock-collector:phase1-latest

# 執行收集
docker run --rm \
  -e FINMIND_API_TOKEN="your_token" \
  -v $(pwd)/data:/app/data \
  ghcr.io/<你的帳號>/tw-stock-collector:phase1-latest \
  python scripts/run_collection.py --date 2025-01-28
```

### 設定映像為公開

預設情況下，GHCR 映像是私有的。若要公開：

1. 進入 https://github.com/users/<你的帳號>/packages
2. 找到 `tw-stock-collector`
3. Package settings → Change visibility → Public

---

## 故障排除

### 常見問題

#### 1. Docker 映像推送失敗

**錯誤**: `denied: permission_denied`

**解決方法**:
- 確認 Settings → Actions → General → Workflow permissions 設為 "Read and write permissions"
- 重新執行工作流程

#### 2. 資料收集失敗

**錯誤**: `API rate limit exceeded`

**解決方法**:
- 設定 `FINMIND_API_TOKEN` Secret
- 減少 `batch_size` 參數
- 增加重試間隔（修改 `config/config.yaml`）

#### 3. Git 推送失敗

**錯誤**: `refusing to allow a GitHub App to create or update workflow`

**原因**: GitHub Actions 預設無法修改 workflow 檔案

**解決方法**:
- 不要將 `.github/workflows/` 目錄加入 `git add`
- 或使用 Personal Access Token 代替 `GITHUB_TOKEN`

#### 4. 測試失敗

**查看詳細錯誤**:
```bash
# 下載測試日誌 artifact
# 或在 Actions 頁面查看詳細輸出
```

#### 5. FinMind API 無回應

**解決方法**:
- 檢查網路連線
- 確認 API Token 有效
- 查看 FinMind 服務狀態

### 查看日誌

**GitHub Actions 日誌**:
1. Actions → 選擇執行記錄
2. 展開步驟查看詳細輸出

**下載收集日誌**:
1. 執行記錄底部 → Artifacts
2. 下載 `collection-logs-*`
3. 解壓縮查看 `logs/` 目錄

---

## 最佳實踐

### 1. 定期檢查執行狀態

- 每週檢查 Actions 頁面
- 訂閱失敗通知（Settings → Notifications）
- 定期清理舊的 Artifacts

### 2. 資料備份策略

```bash
# 定期備份到本地
git clone https://github.com/<你的帳號>/tw-stock-collector.git
cd tw-stock-collector

# 檢查資料完整性
find data/raw -type f -name "*.json" | wc -l

# 打包備份
tar -czf backup-$(date +%Y%m%d).tar.gz data/
```

### 3. 優化 API 使用

**FinMind 免費版限制**:
- 每分鐘 10 次請求
- 每天 600 次請求

**建議**:
- 設定合理的 `batch_size`（建議 7-10）
- 使用 cache 避免重複請求
- 非交易日跳過收集

### 4. 監控儲存空間

**GitHub 免費版限制**:
- Repository 大小: 建議 < 1GB
- Packages (GHCR): 500MB 免費
- Artifacts: 500MB 免費（90 天自動刪除）

**監控方式**:
```bash
# 查看 repository 大小
du -sh .git

# 查看資料大小
du -sh data/

# 清理舊資料（如需要）
find data/raw -type f -mtime +365 -delete
```

### 5. 版本管理

**建議的分支策略**:
```
main        (穩定版，自動收集)
  ↑
develop     (開發版，測試新功能)
  ↑
feature/*   (功能分支)
```

**發布流程**:
1. 在 `feature/*` 開發新功能
2. PR 到 `develop` 測試
3. 測試通過後 PR 到 `main`
4. `main` 自動建置並收集資料

### 6. 安全建議

- ✅ 不要在程式碼中硬編碼 Token
- ✅ 使用 GitHub Secrets 儲存敏感資訊
- ✅ 定期更換 API Token
- ✅ 限制 Workflow permissions
- ✅ 檢查 commit 歷史，避免提交敏感資料

---

## 進階配置

### 自訂執行時間

修改 `.github/workflows/daily-collection.yml`:

```yaml
on:
  schedule:
    # 改為台北時間 19:00 執行 (UTC 11:00)
    - cron: '0 11 * * 1-5'
```

### 增加通知功能

**Slack 通知範例**:

```yaml
- name: Notify Slack
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "Data collection failed!"
      }
```

### 並行執行

修改 backfill workflow 以支援並行：

```yaml
strategy:
  matrix:
    date_range:
      - start: 2024-01-01
        end: 2024-03-31
      - start: 2024-04-01
        end: 2024-06-30
```

---

## 成本估算

### GitHub Actions 用量

**免費額度**（Public Repository）:
- ✅ 無限制

**免費額度**（Private Repository）:
- 2,000 分鐘/月

**預估用量**（本專案）:
- 每日收集: ~5 分鐘
- 每週收集: ~3 分鐘
- CI 測試: ~3 分鐘/次
- 每月總計: ~200 分鐘（免費額度內）

### GitHub Packages (GHCR)

**免費額度**:
- 500 MB 儲存空間
- 1 GB 傳輸量/月

**預估用量**:
- Docker 映像: ~450 MB
- 每月拉取: ~10 次 = ~4.5 GB（可能超出）

**建議**:
- 設定映像為 Public（無傳輸量限制）
- 或使用其他 Registry（Docker Hub, AWS ECR）

---

## 相關文件

- [Docker 使用指南](DOCKER_GUIDE.md)
- [Phase 1 完整指南](PHASE1_GUIDE.md)
- [專案主文檔](README.md)

---

## 故障回報

如遇到問題，請提供：

1. 工作流程執行記錄連結
2. 錯誤訊息截圖
3. 相關日誌檔案

開 Issue: https://github.com/<你的帳號>/tw-stock-collector/issues

---

**最後更新**: 2025-12-28
**版本**: 1.0

