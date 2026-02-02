# Git LFS 使用指南

本專案使用 Git LFS (Large File Storage) 來管理大型資料檔案。

## 📋 什麼是 Git LFS？

Git LFS 是 Git 的擴充功能，專門用於處理大型檔案。它將大檔案的實際內容儲存在遠端 LFS 伺服器，而在 Git 倉庫中只保留輕量級的「指標檔案」(pointer)。

## 🎯 為什麼使用 LFS？

- **倉庫大小**: 原本 `.git` 目錄有 15GB，導致 clone 和操作緩慢
- **檔案數量**: 12,000+ 個資料檔案，每個 0.5-5 MB
- **版本歷史**: 每次資料更新都會增加倉庫大小

使用 LFS 後：
- Clone 時間大幅減少
- 本地操作更快速
- 只下載需要的檔案版本

## 📦 追蹤的檔案類型

根據 `.gitattributes` 設定，以下檔案類型由 LFS 管理：

```
data/**/*.json    # 所有資料目錄下的 JSON 檔案
data/**/*.csv     # 所有資料目錄下的 CSV 檔案
```

## 🚀 本地設定

### 首次設定

如果你是**首次** clone 此專案（在啟用 LFS 之後）：

```bash
# 安裝 Git LFS (macOS)
brew install git-lfs

# 安裝 Git LFS (Ubuntu/Debian)
sudo apt-get install git-lfs

# 初始化 Git LFS
git lfs install

# Clone 專案（會自動下載 LFS 檔案）
git clone https://github.com/twcs-analysis/tw-stock-collector.git
```

### 已有本地倉庫的用戶

如果你**之前已經** clone 了專案（在啟用 LFS 之前）：

```bash
# 1. 安裝 Git LFS
brew install git-lfs  # macOS
# 或
sudo apt-get install git-lfs  # Ubuntu

# 2. 初始化 Git LFS
git lfs install

# 3. 重新 fetch 並切換到新的歷史
git fetch origin
git reset --hard origin/main

# 4. 下載 LFS 物件
git lfs pull
```

**⚠️ 警告**: `git reset --hard` 會覆蓋本地變更，請先備份重要的修改！

## 💻 日常使用

### 一般 Git 操作

使用 Git LFS 後，日常操作與普通 Git 完全相同：

```bash
# 查看狀態
git status

# 新增檔案
git add data/raw/price/2024/12/2024-12-27.json

# 提交
git commit -m "data: 新增 2024-12-27 資料"

# 推送（LFS 會自動上傳）
git push
```

### 查看 LFS 狀態

```bash
# 列出所有 LFS 追蹤的檔案
git lfs ls-files

# 查看 LFS 儲存空間使用
git lfs status

# 檢查特定檔案是否為 LFS
git lfs ls-files | grep "2024-12-27.json"
```

### 只下載最新版本

如果你只需要最新的資料，不需要歷史版本：

```bash
# Clone 時使用 --depth 1 (淺層 clone)
git clone --depth 1 https://github.com/twcs-analysis/tw-stock-collector.git

# 只下載當前 checkout 的 LFS 檔案
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/twcs-analysis/tw-stock-collector.git
cd tw-stock-collector
git lfs pull --include="data/raw/price/2024/**"  # 只下載 2024 年價格資料
```

## 🤖 GitHub Actions

GitHub Actions 已設定為自動支援 LFS：

```yaml
- name: Checkout code
  uses: actions/checkout@v4
  with:
    lfs: true  # 啟用 LFS 支援
```

自動化收集的資料會自動：
1. 寫入 LFS 追蹤的檔案
2. Commit
3. Push（包含 LFS 物件）

## 📊 儲存空間配額

### GitHub 免費配額

- **儲存空間**: 1 GB
- **頻寬**: 每月 1 GB

### 檢查使用量

```bash
# 查看本地 LFS 物件大小
du -sh .git/lfs/objects

# 在 GitHub 上查看
# Settings → Billing → Git LFS data
```

### 超過配額怎麼辦？

1. **購買額外配額**: GitHub 提供付費方案
2. **清理舊資料**: 刪除不需要的歷史資料
3. **使用外部儲存**: 考慮將資料移至 S3 或其他儲存服務

## 🔧 進階操作

### 遷移特定檔案到 LFS

```bash
# 將現有檔案遷移到 LFS
git lfs migrate import --include="*.json" --everything
```

### 從 LFS 移除檔案

```bash
# 從 LFS 移除追蹤（保留檔案）
git lfs untrack "data/**/*.json"

# 從 LFS 匯出回普通 Git
git lfs migrate export --include="*.json" --everything
```

### 清理 LFS 快取

```bash
# 清理本地 LFS 快取
git lfs prune

# 強制清理所有未追蹤的 LFS 物件
git lfs prune --verify-remote
```

## 🐛 常見問題

### Q: Clone 時出現 LFS 錯誤

```bash
Error: Failed to fetch some objects from 'https://github.com/...'
```

**解決方法**:
```bash
# 跳過 LFS 下載，稍後手動拉取
GIT_LFS_SKIP_SMUDGE=1 git clone <repo-url>
cd <repo>
git lfs pull
```

### Q: 為什麼 data 檔案顯示為 pointer？

如果你看到類似這樣的內容：

```
version https://git-lfs.github.com/spec/v1
oid sha256:6eedbf86c545d94c67103e1419568e14...
size 618946
```

這表示 LFS 檔案尚未下載，執行：

```bash
git lfs pull
```

### Q: Push 時很慢

LFS 檔案需要上傳到 LFS 伺服器，這比普通 Git push 慢。可以：

1. 使用更快的網路連線
2. 檢查是否有不必要的大檔案被追蹤
3. 考慮分批提交

### Q: 如何只下載部分資料？

```bash
# 只下載特定路徑的 LFS 檔案
git lfs fetch --include="data/raw/price/**"
git lfs checkout
```

## 📚 參考資源

- [Git LFS 官方文檔](https://git-lfs.github.com/)
- [GitHub LFS 使用指南](https://docs.github.com/en/repositories/working-with-files/managing-large-files)
- [Git LFS 教學](https://github.com/git-lfs/git-lfs/wiki/Tutorial)

## 📝 更新日誌

- **2026-02-02**: 啟用 Git LFS，遷移所有 data 目錄下的 JSON 和 CSV 檔案
  - 遷移了 12,770 個檔案 (15GB)
  - 重寫了完整的 Git 歷史
  - 更新了 GitHub Actions workflows

---

如有任何問題或建議，請開 Issue 討論。
