# 本地開發與測試指南

本文檔說明如何在本地環境進行開發與測試。

## 📋 目錄

- [環境需求](#環境需求)
- [本地開發設定](#本地開發設定)
- [Docker 建置與測試](#docker-建置與測試)
- [分階段測試流程](#分階段測試流程)
- [常見問題](#常見問題)

## 🔧 環境需求

### 必要工具

- **Docker**: 20.10+ (建議使用 Docker Desktop)
- **Docker Compose**: 2.0+
- **Git**: 2.30+
- **Python**: 3.11+ (選用,用於本地測試)
- **Make**: (選用,用於快捷命令)

### 檢查環境

```bash
# 檢查 Docker
docker --version
docker-compose --version

# 檢查 Python (選用)
python --version
pip --version

# 檢查 Git
git --version
```

## 🚀 本地開發設定

### 1. Clone 專案

```bash
# Clone 專案
git clone https://github.com/yourusername/tw-stock-collector.git
cd tw-stock-collector

# 檢查分支
git branch -a
```

### 2. 配置環境變數

```bash
# 複製環境變數範本
cp deployment/.env.example deployment/.env

# 編輯環境變數
vim deployment/.env  # 或使用其他編輯器

# 必須修改的項目:
# - DB_PASSWORD: 資料庫密碼 (不要使用預設值!)
# - FINMIND_API_TOKEN: (選用) FinMind API Token
```

### 3. 目錄結構檢查

```bash
# 確認關鍵目錄存在
tree -L 2 -d

# 應該看到:
# ├── build/          # Docker 建置檔案
# ├── deployment/     # Docker Compose 配置
# ├── database/       # 資料庫 SQL 腳本
# ├── docs/           # 文檔
# ├── config/         # 應用程式配置
# ├── data/           # 資料儲存 (會自動建立)
# ├── logs/           # 日誌 (會自動建立)
# └── scripts/        # Python 腳本 (待開發)
```

## 🐳 Docker 建置與測試

### 建置映像檔

#### 方式一: 使用 Docker Compose (推薦)

```bash
# 建置所有映像檔
docker-compose -f deployment/docker-compose.yml build

# 僅建置 collector
docker-compose -f deployment/docker-compose.yml build collector

# 僅建置 dashboard
docker-compose -f deployment/docker-compose.yml build dashboard

# 無快取重新建置
docker-compose -f deployment/docker-compose.yml build --no-cache
```

#### 方式二: 使用 docker build

```bash
# 建置 collector 映像檔
docker build \
  -f build/Dockerfile \
  -t tw-stock-collector:local \
  .

# 建置 dashboard 映像檔
docker build \
  -f build/Dockerfile.dashboard \
  -t tw-stock-dashboard:local \
  .
```

### 驗證映像檔

```bash
# 列出建置的映像檔
docker images | grep tw-stock

# 預期輸出:
# tw-stock-collector    latest    ...    400MB
# tw-stock-dashboard    latest    ...    600MB

# 檢查映像檔內容
docker run --rm tw-stock-collector:latest python --version
docker run --rm tw-stock-collector:latest pip list

docker run --rm tw-stock-dashboard:latest streamlit --version
```

### 測試映像檔

```bash
# 測試 Python 環境
docker run --rm tw-stock-collector:latest python -c "import pandas; print(pandas.__version__)"

# 測試 FinMind 套件
docker run --rm tw-stock-collector:latest python -c "import FinMind; print('FinMind OK')"

# 測試 Streamlit
docker run --rm -p 8501:8501 tw-stock-dashboard:latest \
  streamlit hello
# 訪問 http://localhost:8501 應該看到 Streamlit 歡迎頁面
```

## 🧪 分階段測試流程

### Phase 1: 資料收集測試

```bash
# 1. 使用 Phase 1 compose
cd /path/to/tw-stock-collector

# 2. 執行資料收集 (模擬)
docker-compose -f deployment/docker-compose.phase1.yml up

# 3. 檢查收集的資料
ls -lh data/raw/
tree data/raw/ -L 3

# 4. 查看日誌
cat logs/collector.log

# 5. 清理
docker-compose -f deployment/docker-compose.phase1.yml down
```

**預期結果**:
- `data/raw/` 目錄下應該有收集的 JSON/CSV 檔案
- 日誌檔案顯示收集過程無錯誤

### Phase 2: 資料庫與匯入測試

```bash
# 1. 啟動資料庫
docker-compose -f deployment/docker-compose.phase2.yml up -d postgres

# 2. 等待資料庫就緒 (查看日誌)
docker-compose -f deployment/docker-compose.phase2.yml logs -f postgres
# 看到 "database system is ready to accept connections" 即可繼續

# 3. 驗證資料庫初始化
docker-compose -f deployment/docker-compose.phase2.yml exec postgres \
  psql -U stock_user -d tw_stock -c "\dt"

# 應該看到 10 個資料表:
#  stocks
#  trading_calendar
#  daily_prices
#  institutional_trading
#  margin_trading
#  securities_lending
#  foreign_holding
#  shareholding_distribution
#  director_holding
#  import_logs

# 4. 檢查初始資料
docker-compose -f deployment/docker-compose.phase2.yml exec postgres \
  psql -U stock_user -d tw_stock -c "SELECT * FROM stocks LIMIT 5;"

docker-compose -f deployment/docker-compose.phase2.yml exec postgres \
  psql -U stock_user -d tw_stock -c "SELECT COUNT(*) FROM trading_calendar;"

# 5. (待 Phase 1 有資料後) 執行資料匯入
docker-compose -f deployment/docker-compose.phase2.yml run --rm importer

# 6. 驗證匯入的資料
docker-compose -f deployment/docker-compose.phase2.yml exec postgres \
  psql -U stock_user -d tw_stock -c "SELECT COUNT(*) FROM daily_prices;"

# 7. 查看匯入日誌
docker-compose -f deployment/docker-compose.phase2.yml exec postgres \
  psql -U stock_user -d tw_stock -c "SELECT * FROM import_logs ORDER BY created_at DESC LIMIT 5;"

# 8. 啟動 pgAdmin (選用)
docker-compose -f deployment/docker-compose.phase2.yml --profile tools up -d pgadmin
# 訪問 http://localhost:5050
# 登入: admin@localhost / admin

# 9. 清理
docker-compose -f deployment/docker-compose.phase2.yml down
# 如果要保留資料,不要使用 -v
```

**預期結果**:
- 資料庫成功啟動並初始化
- 10 個資料表都已建立
- 初始資料 (16 檔股票, 2020-2030 日曆) 已載入
- 匯入腳本能正確執行

### Phase 3: 儀表板測試

```bash
# 1. 確保 Phase 2 資料庫正在運行
docker-compose -f deployment/docker-compose.phase2.yml up -d postgres

# 2. 啟動儀表板
docker-compose -f deployment/docker-compose.phase3.yml up -d dashboard

# 3. 查看日誌
docker-compose -f deployment/docker-compose.phase3.yml logs -f dashboard

# 4. 訪問儀表板
open http://localhost:8501

# 5. (選用) 啟動 Jupyter
docker-compose -f deployment/docker-compose.phase3.yml --profile tools up -d jupyter
open http://localhost:8888

# 6. 清理
docker-compose -f deployment/docker-compose.phase3.yml down
```

**預期結果**:
- 儀表板成功啟動,可在瀏覽器訪問
- 能夠連接到資料庫
- 能夠顯示資料 (如果資料庫有資料)

### 完整三階段整合測試

```bash
# 使用完整版 docker-compose
cd /path/to/tw-stock-collector

# 1. 啟動資料庫
docker-compose -f deployment/docker-compose.yml up -d postgres

# 2. 等待資料庫就緒
sleep 30

# 3. 執行資料收集 (Phase 1)
docker-compose -f deployment/docker-compose.yml --profile phase1 run --rm collector

# 4. 執行資料匯入 (Phase 2)
docker-compose -f deployment/docker-compose.yml --profile phase2 run --rm importer

# 5. 啟動儀表板 (Phase 3)
docker-compose -f deployment/docker-compose.yml --profile phase3 up -d dashboard

# 6. 訪問儀表板
open http://localhost:8501

# 7. 查看所有服務狀態
docker-compose -f deployment/docker-compose.yml ps

# 8. 清理
docker-compose -f deployment/docker-compose.yml down
```

## 📊 驗證檢查清單

### 建置階段

- [ ] Collector 映像檔建置成功
- [ ] Dashboard 映像檔建置成功
- [ ] 映像檔大小合理 (Collector ~400-500MB, Dashboard ~600-700MB)
- [ ] Python 版本正確 (3.11+)
- [ ] 必要套件都已安裝 (pandas, FinMind, streamlit 等)

### 資料庫階段

- [ ] PostgreSQL 容器啟動成功
- [ ] 資料庫初始化完成 (10 個資料表)
- [ ] 索引建立完成 (41 個索引)
- [ ] 初始資料載入 (16 檔股票, 日曆資料)
- [ ] 可以透過 psql 連線
- [ ] 健康檢查通過

### 應用程式階段

- [ ] Collector 可以執行 (即使沒有真實資料)
- [ ] Importer 可以執行
- [ ] Dashboard 可以啟動
- [ ] Dashboard 可以連接資料庫
- [ ] Dashboard 網頁可以訪問

### CI/CD 階段

- [ ] GitHub Actions workflow 語法正確
- [ ] 可以在本地模擬 Actions 環境 (使用 act)
- [ ] Docker 建置在 GitHub Actions 中成功

## 🐛 常見問題

### Q1: Docker 建置失敗 - "COPY ../requirements.txt: no such file"

**原因**: Dockerfile 中的路徑錯誤
**解決**:
```bash
# 確保從專案根目錄執行
cd /path/to/tw-stock-collector

# 使用 docker-compose (它會自動處理 context)
docker-compose -f deployment/docker-compose.yml build
```

### Q2: 資料庫初始化腳本沒有執行

**原因**: PostgreSQL 資料卷已存在,init 腳本只在首次啟動時執行
**解決**:
```bash
# 刪除資料卷重新初始化
docker-compose -f deployment/docker-compose.phase2.yml down -v
docker-compose -f deployment/docker-compose.phase2.yml up -d postgres
```

### Q3: Streamlit 啟動失敗 - "ModuleNotFoundError"

**原因**: Dashboard 映像檔缺少必要套件
**解決**:
```bash
# 檢查 Dockerfile.dashboard 是否正確安裝 streamlit
# 重新建置
docker-compose -f deployment/docker-compose.yml build --no-cache dashboard
```

### Q4: 無法連接資料庫 - "Connection refused"

**原因**:
1. 資料庫未啟動
2. 健康檢查未通過
3. 環境變數配置錯誤

**解決**:
```bash
# 1. 檢查資料庫狀態
docker-compose -f deployment/docker-compose.phase2.yml ps postgres

# 2. 查看資料庫日誌
docker-compose -f deployment/docker-compose.phase2.yml logs postgres

# 3. 檢查健康狀態
docker-compose -f deployment/docker-compose.phase2.yml exec postgres pg_isready

# 4. 驗證環境變數
cat deployment/.env | grep DB_
```

### Q5: 端口衝突 - "port is already allocated"

**原因**: 端口已被其他服務占用
**解決**:
```bash
# 方式一: 修改 .env 檔案中的端口
vim deployment/.env
# DB_PORT=5433
# STREAMLIT_PORT=8502

# 方式二: 停止衝突的服務
lsof -i :5432  # 查看占用 5432 端口的程序
kill -9 <PID>  # 終止該程序
```

### Q6: 權限錯誤 - "Permission denied"

**原因**: Docker 容器無法寫入主機目錄
**解決**:
```bash
# Linux: 修改目錄權限
chmod 755 data/ logs/ output/

# macOS: 通常不需要,Docker Desktop 已處理
# 如果仍有問題,檢查 Docker Desktop 設定中的檔案共享
```

## 📚 進階開發

### 使用 VS Code DevContainer (選用)

```bash
# 1. 安裝 VS Code 和 Remote-Containers 擴展

# 2. 建立 .devcontainer/devcontainer.json
# (待新增)

# 3. 在 VS Code 中開啟專案
# Command Palette (Cmd+Shift+P) > "Reopen in Container"
```

### 本地 Python 開發 (不使用 Docker)

```bash
# 1. 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 安裝依賴
pip install -r requirements.txt

# 3. 設定環境變數
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=tw_stock
export DB_USER=stock_user
export DB_PASSWORD=your_password

# 4. 執行腳本
python -m scripts.run_collection
python -m scripts.run_import
streamlit run scripts/dashboard/app.py
```

### GitHub Actions 本地測試

```bash
# 使用 act 工具 (https://github.com/nektos/act)
brew install act

# 測試 workflow
act -l  # 列出所有 workflows
act push  # 模擬 push 事件
act -j build-collector  # 執行特定 job
```

## 🔗 相關文檔

- [README.md](../README.md) - 專案概覽
- [Build README](../build/README.md) - Docker 建置說明
- [Deployment README](../deployment/README.md) - 部署指南
- [Database README](../database/README.md) - 資料庫說明
- [Phase 1 規格書](specifications/PHASE1_DATA_COLLECTION.md)
- [Phase 2 規格書](specifications/PHASE2_DATABASE_IMPORT.md)
- [Phase 3 規格書](specifications/PHASE3_DATA_ANALYSIS.md)

---

**維護者**: Jason Huang
**最後更新**: 2025-12-28
