# Phase 1 測試指南

此文檔說明如何測試 Phase 1 的三個關鍵功能。

---

## 測試 1: 確認 GitHub Action 正常建置 Docker Image

### 步驟：

1. **查看 CI 工作流程狀態**
   ```bash
   gh run list --workflow=ci.yml --limit 5
   ```

2. **等待最新的 CI 完成**

   推送後，GitHub Actions 會自動觸發 CI workflow。查看執行狀態：
   ```bash
   gh run watch
   ```

3. **確認建置成功**

   成功的 CI run 應該顯示：
   - ✅ Run Tests
   - ✅ Build Docker Image
   - ✅ CI Summary

4. **確認 Docker Image 已推送到 GHCR**

   檢查 GitHub Container Registry：
   ```bash
   gh api /user/packages/container/tw-stock-collector/versions
   ```

   或訪問：
   ```
   https://github.com/twcs-analysis/tw-stock-collector/pkgs/container/tw-stock-collector
   ```

5. **驗證 Image 標籤**

   應該能看到以下標籤：
   - `main` - main 分支最新版本
   - `phase1-latest` - Phase 1 的最新穩定版本
   - `<sha>` - 特定 commit 的版本

---

## 測試 2: 本地部署使用 GitHub Actions 的 Docker Image

### 前置需求：

- Docker 已安裝
- 已登入 GitHub Container Registry

### 步驟：

1. **登入 GHCR**
   ```bash
   echo $GHCR_TOKEN_JASONHUANG | docker login ghcr.io -u jasonhuang --password-stdin
   ```

   或使用 GitHub Token：
   ```bash
   echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin
   ```

2. **拉取最新的 Docker Image**
   ```bash
   docker pull ghcr.io/twcs-analysis/tw-stock-collector:phase1-latest
   ```

3. **測試 Docker Image - 顯示說明**
   ```bash
   docker run --rm ghcr.io/twcs-analysis/tw-stock-collector:phase1-latest --help
   ```

   預期輸出：
   ```
   usage: run_collection.py [-h] [--date DATE] [--types {price,margin,institutional,lending} ...]
   ...
   ```

4. **測試 Docker Image - 收集單日資料**
   ```bash
   # 建立本地資料目錄
   mkdir -p data/raw

   # 收集 2024-12-27 的所有資料
   docker run --rm \
     -v $(pwd)/data:/app/data \
     ghcr.io/twcs-analysis/tw-stock-collector:phase1-latest \
     --date 2024-12-27 \
     --skip-trading-day-check
   ```

5. **檢查收集結果**
   ```bash
   ls -lh data/raw/*/2024/12/
   ```

   應該看到：
   ```
   data/raw/price/2024/12/2024-12-27.json
   data/raw/margin/2024/12/2024-12-27.json
   data/raw/institutional/2024/12/2024-12-27.json
   data/raw/lending/2024/12/2024-12-27.json
   ```

6. **查看資料內容**
   ```bash
   cat data/raw/price/2024/12/2024-12-27.json | jq '.metadata'
   ```

   預期輸出：
   ```json
   {
     "date": "2024-12-27",
     "collected_at": "2025-12-28T...",
     "total_count": 1946,
     "source": "TWSE + TPEx Official API"
   }
   ```

---

## 測試 3: 回補歷史資料 (2025-01-01 ~ 2025-01-31)

### 方法 A: 使用本地 Python 腳本

1. **確保已安裝依賴**
   ```bash
   pip install -r requirements.txt
   ```

2. **執行回補腳本**
   ```bash
   python scripts/backfill.py \
     --start 2025-01-01 \
     --end 2025-01-31 \
     --types price margin institutional lending
   ```

3. **監控進度**

   腳本會顯示每日的收集進度：
   ```
   [1/31] 處理日期: 2025-01-01
   ----------------------------------------------------------------------
     [PRICE] 開始收集...
     ✅ price: 1946 筆
     [MARGIN] 開始收集...
     ✅ margin: 1815 筆
   ...
   ```

4. **查看最終統計**
   ```
   ======================================================================
   回補完成
   ======================================================================
   總天數: 31
     處理: 22
     成功: 22
     跳過: 9
     失敗: 0
   總筆數: 128,348
   ======================================================================
   ```

### 方法 B: 使用 Docker Image

1. **使用 Docker 執行回補**
   ```bash
   docker run --rm \
     -v $(pwd)/data:/app/data \
     ghcr.io/twcs-analysis/tw-stock-collector:phase1-latest \
     python scripts/backfill.py \
     --start 2025-01-01 \
     --end 2025-01-31 \
     --types price margin institutional lending
   ```

### 方法 C: 使用 GitHub Actions (手動觸發)

1. **前往 GitHub Actions 頁面**
   ```
   https://github.com/twcs-analysis/tw-stock-collector/actions/workflows/backfill.yml
   ```

2. **點擊 "Run workflow"**

3. **填寫參數**:
   - **開始日期**: `2025-01-01`
   - **結束日期**: `2025-01-31`
   - **資料類型**: `price margin institutional lending`
   - **批次大小**: `10` (預設)

4. **點擊 "Run workflow" 按鈕**

5. **監控執行狀態**
   ```bash
   gh run watch
   ```

6. **查看日誌**
   ```bash
   # 查看最新的 backfill run
   gh run list --workflow=backfill.yml --limit 1

   # 查看詳細日誌 (取代 <run-id>)
   gh run view <run-id> --log
   ```

7. **確認資料已提交到 Git**

   回補完成後，GitHub Actions 會自動 commit 並 push 資料：
   ```bash
   git pull origin main
   ls -R data/raw/
   ```

---

## 驗證資料完整性

### 檢查檔案數量

```bash
# 統計各類型資料檔案數
echo "價格資料:"
find data/raw/price/2025/01/ -name "*.json" | wc -l

echo "融資融券:"
find data/raw/margin/2025/01/ -name "*.json" | wc -l

echo "三大法人:"
find data/raw/institutional/2025/01/ -name "*.json" | wc -l

echo "借券賣出:"
find data/raw/lending/2025/01/ -name "*.json" | wc -l
```

### 檢查資料大小

```bash
du -sh data/raw/*/2025/01/
```

預期大小（每個交易日約 2.9 MB）：
- 22 個交易日 ≈ 64 MB

### 驗證資料格式

```bash
# 檢查第一個檔案的結構
cat data/raw/price/2025/01/2025-01-02.json | jq '.metadata'
cat data/raw/price/2025/01/2025-01-02.json | jq '.data | length'
```

---

## 常見問題排除

### 問題 1: Docker pull 失敗

**錯誤訊息**:
```
Error response from daemon: pull access denied
```

**解決方式**:
```bash
# 確認登入狀態
docker login ghcr.io

# 使用正確的 token
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

### 問題 2: 回補時出現 SSL 錯誤

**錯誤訊息**:
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**解決方式**:

已在程式碼中處理（`verify=False`），但若仍有問題：
```bash
# macOS
/Applications/Python\ 3.11/Install\ Certificates.command

# Linux
apt-get install ca-certificates
```

### 問題 3: 某些日期沒有資料

**原因**: 該日期可能是：
- 週末
- 國定假日
- 非交易日

**驗證**:
```bash
python -c "from src.utils import is_trading_day; print(is_trading_day('2025-01-01'))"
```

### 問題 4: GitHub Actions 失敗

**查看失敗原因**:
```bash
gh run view <run-id> --log-failed
```

**重新觸發**:
```bash
gh run rerun <run-id>
```

---

## 測試檢查清單

使用此檢查清單確保所有功能正常：

- [ ] **CI 建置**
  - [ ] GitHub Actions CI workflow 成功完成
  - [ ] Docker image 已推送到 GHCR
  - [ ] Image 有正確的標籤 (main, phase1-latest)

- [ ] **本地部署**
  - [ ] 成功拉取 Docker image
  - [ ] `--help` 顯示正確
  - [ ] 單日資料收集成功
  - [ ] 產生的檔案格式正確

- [ ] **歷史回補**
  - [ ] 回補腳本可正常執行
  - [ ] 自動跳過非交易日
  - [ ] 產生正確數量的檔案
  - [ ] 資料格式驗證通過
  - [ ] (選用) GitHub Actions 回補成功

---

## 測試完成後

### 清理測試資料 (選用)

```bash
# 刪除測試產生的資料
rm -rf data/raw/2025/

# 或保留資料並提交到 Git
git add data/raw/
git commit -m "data: Add backfilled data for Jan 2025"
git push
```

### 驗證 CI/CD 流程

確認以下流程都正常：

1. ✅ 程式碼變更 → CI 測試 → Docker 建置 → GHCR 推送
2. ✅ 每日 cronjob → 資料收集 → Git commit → Push
3. ✅ 手動回補 → 範圍收集 → Git commit → Push

---

**測試日期**: 2025-12-28
**測試者**: Jason Huang
