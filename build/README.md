# Build 目錄

此目錄包含 Docker 映像檔建置相關的檔案。

## 📁 檔案說明

### Dockerfile
**Phase 1: 台股資料收集器 Docker Image**

這個 Dockerfile 用於建置 Phase 1 資料收集程式的 Docker 映像檔，可在以下環境執行：
- GitHub Actions (自動化收集)
- 本地開發測試
- 生產環境部署

**基礎映像**: Python 3.11-slim

**包含內容**:
- Python 3.11 執行環境
- Git（用於版本控制）
- 所有 Python 依賴套件（requirements.txt）
- 資料收集程式碼（src/ 和 scripts/）

**環境變數**:
- `PYTHONUNBUFFERED=1`: 確保 Python 輸出不緩衝
- `PYTHONPATH=/app`: 設定 Python 模組搜尋路徑

**入口點**: `python /app/scripts/run_collection.py`

---

## 🚀 使用方式

### 本地建置

```bash
# 從專案根目錄執行
cd /path/to/tw-stock-collector

# 建置 Docker 映像檔
docker build -f build/Dockerfile -t tw-stock-collector:local .

# 測試映像檔
docker run --rm tw-stock-collector:local --help
```

### 執行資料收集

```bash
# 收集今天的所有資料
docker run --rm \
  -v $(pwd)/data:/app/data \
  tw-stock-collector:local

# 收集指定日期的資料
docker run --rm \
  -v $(pwd)/data:/app/data \
  tw-stock-collector:local --date 2024-12-27

# 只收集特定類型
docker run --rm \
  -v $(pwd)/data:/app/data \
  tw-stock-collector:local --date 2024-12-27 --types price margin

# 跳過交易日檢查
docker run --rm \
  -v $(pwd)/data:/app/data \
  tw-stock-collector:local --date 2024-12-27 --skip-trading-day-check
```

### 使用環境變數

```bash
# 透過環境變數設定參數
docker run --rm \
  -e COLLECTION_DATE=2024-12-27 \
  -e COLLECTION_TYPES="price margin institutional lending" \
  -e TZ=Asia/Taipei \
  -v $(pwd)/data:/app/data \
  tw-stock-collector:local
```

---

## 🏗️ CI/CD 建置流程

### GitHub Actions 自動建置

本專案使用 GitHub Actions 自動建置並推送 Docker 映像檔到 GitHub Container Registry (GHCR)。

**工作流程**: `.github/workflows/ci.yml`

**觸發條件**:
- 推送到 `main` 或 `develop` 分支
- Pull Request 到 `main` 或 `develop`
- 手動觸發 (workflow_dispatch)

**映像檔標籤**:
- `ghcr.io/<owner>/<repo>:main` - main 分支最新版本
- `ghcr.io/<owner>/<repo>:phase1-latest` - Phase 1 的最新穩定版本
- `ghcr.io/<owner>/<repo>:<sha>` - 特定 commit 的版本

### 從 GHCR 拉取映像檔

```bash
# 登入 GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# 拉取最新版本
docker pull ghcr.io/<owner>/<repo>:phase1-latest

# 執行
docker run --rm \
  -v $(pwd)/data:/app/data \
  ghcr.io/<owner>/<repo>:phase1-latest --date 2024-12-27
```

---

## 📦 映像檔結構

```
/app/                           # 工作目錄
├── src/                        # 程式碼
│   ├── collectors/            # 收集器
│   ├── datasources/           # 資料源 API
│   └── utils/                 # 工具函式
├── scripts/                   # 執行腳本
│   ├── run_collection.py      # 主要收集腳本
│   └── backfill.py            # 回補腳本
├── data/                      # 資料目錄（通過 volume 掛載）
│   └── raw/                   # 原始資料
└── requirements.txt           # Python 依賴
```

**Volume 掛載建議**:
- `/app/data`: 資料儲存（必須）
- `/app/logs`: 日誌輸出（選用）
- `/app/cache`: 快取資料（選用）

---

## 🔧 進階用法

### 多平台建置

```bash
# 建置支援多平台的映像檔
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -f build/Dockerfile \
  -t tw-stock-collector:multi-arch \
  --push \
  .
```

### 開發模式

```bash
# 掛載原始碼進行開發測試
docker run --rm -it \
  -v $(pwd)/src:/app/src \
  -v $(pwd)/scripts:/app/scripts \
  -v $(pwd)/data:/app/data \
  tw-stock-collector:local \
  bash
```

### 自訂 Python 版本

如需使用不同的 Python 版本，修改 Dockerfile 第一行：

```dockerfile
# 例如使用 Python 3.12
FROM python:3.12-slim
```

---

## 🐛 故障排除

### 映像檔建置失敗

```bash
# 清除 Docker 快取
docker system prune -a

# 重新建置（不使用快取）
docker build --no-cache -f build/Dockerfile -t tw-stock-collector:local .
```

### 容器內找不到模組

確認 `PYTHONPATH` 環境變數已正確設定：

```bash
docker run --rm tw-stock-collector:local python -c "import sys; print(sys.path)"
```

### 資料卷權限問題

```bash
# macOS/Linux: 確保 data 目錄存在且有寫入權限
mkdir -p data/raw
chmod 755 data

# 檢查容器內的權限
docker run --rm -it \
  -v $(pwd)/data:/app/data \
  tw-stock-collector:local \
  ls -la /app/data
```

### SSL 憑證錯誤

某些環境可能會遇到 SSL 憑證驗證問題，可透過以下方式解決：

```bash
# 方法 1: 更新系統 CA 憑證
docker build --build-arg INSTALL_CA=true -f build/Dockerfile .

# 方法 2: 在收集器中已經處理（verify=False）
# 參考: src/collectors/institutional_collector.py
```

---

## 📊 映像檔大小優化

目前的 Dockerfile 已包含以下優化：

1. ✅ 使用 `python:3.11-slim` 而非完整版本
2. ✅ 清理 apt 快取 (`rm -rf /var/lib/apt/lists/*`)
3. ✅ 使用 `--no-cache-dir` 安裝 pip 套件
4. ✅ 只複製必要的檔案

**映像檔大小**: 約 200-300 MB

**進一步優化建議**:
- 使用多階段建置 (Multi-stage build)
- 使用 Alpine Linux 基礎映像檔（注意 glibc 相容性）
- 移除不必要的依賴套件

---

## 🔐 安全建議

1. **不要在映像檔中包含敏感資訊**
   - 不要 COPY .env 檔案
   - 使用環境變數或 Docker secrets 傳遞機敏資料

2. **定期更新基礎映像檔**
   ```bash
   docker pull python:3.11-slim
   docker build --no-cache -f build/Dockerfile .
   ```

3. **掃描映像檔漏洞**
   ```bash
   # 使用 Docker Scout
   docker scout cves tw-stock-collector:local

   # 使用 Trivy
   trivy image tw-stock-collector:local
   ```

4. **使用非 root 使用者執行**
   未來可考慮在 Dockerfile 中加入：
   ```dockerfile
   RUN useradd -m -u 1000 appuser
   USER appuser
   ```

---

## 📚 相關文檔

- [Docker 官方文檔](https://docs.docker.com/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [專案部署文檔](../deployment/README.md)
- [專案主要 README](../README.md)
- [Phase 1 規格書](../docs/specifications/PHASE1_DATA_COLLECTION.md)

---

**維護者**: Jason Huang
**最後更新**: 2025-12-28
