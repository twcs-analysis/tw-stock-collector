# 台股資料收集系統 - AI 助手指南

本文件提供給 AI 助手參考，協助理解專案架構與開發規範。

---

## 🌏 語言偏好

**重要**: 本專案使用**繁體中文**（Traditional Chinese），請確保：
- 所有回應、文檔、註解使用**繁體中文**
- 避免使用簡體中文
- Git commit 訊息使用繁體中文
- 程式碼註解使用繁體中文

---

## 📋 專案概述

**專案名稱**: 台股資料收集與分析系統
**主要目標**: 自動化收集台股資料，包含價格、法人、融資融券等數據
**技術棧**: Python 3.11+, PostgreSQL, GitHub Actions, Docker, JSON
**資料來源**: 台灣證交所 (TWSE) 與櫃買中心 (TPEx) 官方 API

### 核心特色

- GitHub Actions 自動化收集（每交易日 21:30）
- 無需 API Token，完全使用免費公開 API
- Git 版本控制追蹤所有資料變更
- 統一的 JSON 資料結構
- 三層資料驗證機制

### 🔴 重要環境資訊

**Python 環境**（2026-02-04 更新）：
- **Python 版本**: Python 3.11+（必須使用 `python3.11`，不可使用系統預設的 `python3` 3.7）
- **套件管理器**: 優先使用 `uv`（已安裝），次選 `pip`
- **虛擬環境**: `venv/`（使用 uv 管理）
- **套件安裝方式**：
  1. **推薦**: `uv pip install -r requirements.txt`（快速）
  2. **替代**: `python3.11 -m pip install --user -r requirements.txt`（全域安裝）
- **重要**: 所有腳本執行都必須使用 `python3.11`，已更新：
  - `scripts/data-importer/import.sh`（已改為 python3.11）
  - 其他 shell 腳本如需 Python 也應使用 python3.11

**資料庫設定**（本地 PostgreSQL）：
- **類型**: PostgreSQL 17（本地安裝，非 Docker）
- **主機**: localhost
- **埠號**: 5432
- **資料庫名稱**: tw_stock
- **使用者**: postgres
- **密碼**: tw_stock_dev_password_2024
- **CLI 工具**: `psql-17`（請使用 `psql-17` 而非 `psql`）

**目前資料庫狀態**（2026-02-04 更新）：
- ✅ **Schema 重建完成**: 使用 `services/common/database/` 統一模型
- ✅ **資料匯入完成**: 所有 price 資料已匯入
- **主表格**: `stock_prices`（統一使用此名稱，欄位名稱: `trade_date`, `stock_id`, `open_price`, `close_price` 等）
- **股票總數**: 2,019 檔
- **資料範圍**: 2024-01-02 至 2026-02-04
- **交易日數**: 514 天
- **總記錄數**: 960,750 筆

**資料收集架構**（2026-02-03 修正）：
- ✅ **雙模式 API 架構**: 自動判斷日期選擇適當的 API
  - 即時模式：當日資料使用 OpenAPI（快速，僅當日）
  - 回補模式：歷史資料使用 MI_INDEX API（TWSE）/ 傳統 API（TPEx）
- ✅ **自動切換**: `PriceCollector` 根據日期自動選擇模式
- ⚠️ **重要**: 歷史資料收集必須使用回補模式，否則會取得重複或錯誤的資料

**技術分析轉換器**：
- ✅ 已整合資料庫載入模式
- ✅ 計算 30 個技術指標（MA、RSI、MACD、DMI/ADX、布林通道、成交量分析）
- ✅ VWAP 修正: amount ÷ volume
- ✅ ADX 修正: Wilder's Smoothing (EWM)
- ⚡ 效能: ~20 秒處理 1,900 檔股票
- 📂 輸出路徑: `data/transformed/technical/`

**月營收資料處理**（2026-02-07 新增）：
- ✅ **雙模式收集**:
  - Daily 模式（1-10 號）：增量更新，逐一查詢已公告股票
  - Monthly 模式（10 號後）：一次取得完整資料（~1,940 檔）
- ✅ **資料表**: `stock_revenues`（year_month, stock_id 為 unique key）
- ✅ **自動化執行**: `cron-automation/revenue-pipeline/run.sh`
- 🔴 **重要單位轉換規則**：
  - **資料庫儲存**: 千元（例如：730,039,420）
  - **顯示轉換**: 億元 = 千元 ÷ 100,000
  - **正確公式**: `revenue_in_billions = revenue_in_thousands / 100000`
  - **範例**: 730,039,420 千元 ÷ 100,000 = 7,300.39 億元
  - ⚠️ **常見錯誤**: 不要多除或少除任何單位

**資料儲存架構**：
1. **原始資料**: `data/raw/` - JSON 檔案（版本控制，2020-2026）
2. **資料庫**: PostgreSQL - 結構化資料（目前僅 2024-2026）
3. **轉換後資料**: `data/transformed/` - 技術指標等衍生資料

---

## 📊 資料結構

### 資料類型

系統收集六種資料類型：

1. **price** - 每日價量資料（開高低收、成交量）
2. **institutional** - 三大法人買賣超（外資、投信、自營商）
3. **margin** - 融資融券餘額與變化
4. **lending** - 借券賣出餘額
5. **top20_volume** - 成交量前 20 名個股
6. **revenue** - 月營收資料（支援 daily 和 monthly 兩種模式）

### 檔案組織

**每日資料**（price, institutional, margin, lending, top20_volume）:
```
data/raw/{type}/YYYY/MM/YYYY-MM-DD.json
```

**月營收資料**（revenue）:
```
data/raw/revenue-daily/YYYY/YYYY-MM.json    # 每日模式（1-10 日，增量更新）
data/raw/revenue-monthly/YYYY/YYYY-MM.json  # 月度模式（10 日後，完整資料）
```

**資料特性**：
- 每日資料：一個日期一個檔案，包含所有股票資料
- 月營收資料：同一個月同一個檔案（daily 模式增量更新）
- 依年份（YYYY）和月份（MM）分目錄
- 統一的 JSON 格式，包含 metadata 和 data

**詳細 JSON 格式範例請參考**: [README.md](README.md)

---

## 🔧 核心功能

### 資料收集器架構

所有收集器繼承 `BaseCollector`，實作統一介面：

```python
class BaseCollector:
    def collect(self, date: str) -> Dict
    def validate(self, data: Dict) -> bool
    def save(self, data: Dict, date: str) -> None
```

### 資料源整合

**TWSEDataSource** - 證交所 API（上市股票），雙模式架構：
1. **即時模式** - 使用 STOCK_DAY_ALL OpenAPI
   - API: `https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL`
   - 速度：約 2-3 秒
   - 用途：每日自動收集（僅限當日最新資料）

2. **回補模式** - 使用 MI_INDEX API
   - API: `https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX`
   - 速度：約 2-3 秒（一次取得所有股票）
   - 用途：歷史資料回補（支援任意歷史日期）
   - 重要：此 API 從 `tables[8]` 取得股票資料

**TPExDataSource** - 櫃買中心 API（上櫃股票）

**RevenueCollector** - 月營收資料收集器（雙模式）：
1. **Daily 模式**（1-10 日，增量更新）
   - 當月資料：MOPS API（逐一查詢）`https://mops.twse.com.tw/mops/api/t05st10_ifrs`
   - 上月資料：OpenAPI（用於計算 MoM）
   - 速度：5-10 分鐘（增量，跳過已公告股票）
   - 特性：增量更新同一檔案，支援中斷續傳

2. **Monthly 模式**（10 日後，完整資料）
   - API: TWSE/TPEx OpenAPI `t187ap05_L` / `mopsfin_t187ap05_O`
   - 速度：2-3 秒
   - 特性：一次取得所有公司完整資料（~1,940 檔）

每個收集器會整合兩個資料源的資料。

### 驗證機制

三層驗證：
1. **結構驗證** - JSON 格式、必要欄位
2. **完整性檢查** - 筆數範圍、欄位完整
3. **合理性驗證** - 數值範圍、邏輯一致性

---

## 🚀 常用指令

**⚠️ 重要：所有資料處理任務都應使用 `scripts/` 目錄下的 shell 腳本，而非直接執行 Python 檔案**

### 資料收集（data-collect）
```bash
# 收集當天資料
python3 scripts/run_collection.py

# 收集指定日期資料
python3 scripts/run_collection.py --date 2024-12-27 --types price margin

# 回補歷史資料
python3 scripts/backfill.py --start 2025-01-01 --end 2025-01-31
```

### 資料匯入（data-import）
```bash
# 匯入所有資料類型
export DB_PASSWORD=<your_password>
scripts/data-importer/import.sh all --date 2026-02-06
```

### 技術分析轉換（data-transform）
```bash
# 轉換今天的資料
export DB_PASSWORD=<your_password>
scripts/data-transformer/transform.sh today

# 轉換日期區間
scripts/data-transformer/transform.sh range 2026-01-01 2026-01-31
```

### Cron 自動化執行
```bash
# Revenue Pipeline（月營收自動處理）
./cron-automation/revenue-pipeline/run.sh

# YT Finance Show（理財達人秀影片處理）
./cron-automation/yt-finance-show/run.sh
```

### 完整 Pipeline
```bash
# 使用 data-pipeline skill 自動執行完整流程
# 包含：收集 → 匯入 → 轉換 → Git 提交
# 詳見：.claude/skills/data-pipeline/SKILL.md
```

---

## 💻 Claude Skills 快速參考

本專案提供多個 Claude Skills 自動化常見任務：

### 資料處理類
- **data-pipeline** - 完整資料處理流程（收集→匯入→轉換→Git 提交）
- **data-collect** - 資料收集
- **data-import** - 資料匯入資料庫
- **data-transform** - 技術指標轉換
- **revenue-pipeline** - 月營收資料處理

### 工具類
- **git** - Git 提交流程
- **yt-finance-show** - YouTube 理財影片分析

**使用方式**: 在 Claude CLI 中直接輸入 skill 名稱即可執行
**詳細說明**: 參考各 skill 的 SKILL.md 文件

---

## 📝 開發規範

### 🚨 執行腳本規範（極重要）

**絕對規則**: 執行任何任務時，**必須優先使用** `scripts/` 目錄下的現有腳本，**禁止自行撰寫程式**，除非該腳本不存在。

#### 適用範圍

此規範適用於所有操作類型：

1. **資料收集** (`data-collect`)
   - ✅ 使用: `scripts/run_collection.py` 或 `scripts/data-collector/backfill_historical.py`
   - ❌ 禁止: 自行撰寫收集程式

2. **資料匯入** (`data-import`)
   - ✅ 使用: `scripts/data-importer/` 下的腳本
   - ❌ 禁止: 自行撰寫匯入程式

3. **資料轉換** (`data-transform`)
   - ✅ 使用: `scripts/data-transformer/transform.sh`（shell 腳本）
   - ❌ 禁止: 直接執行 Python 檔案或自行撰寫轉換程式
   - **重要**: 必須使用 `transform.sh`，不可使用 `run_technical_analysis.py`

4. **資料分析** (`analysis`)
   - ✅ 使用: `scripts/analysis/` 或 `analysis/` 下的 SQL 腳本
   - ❌ 禁止: 自行撰寫分析程式

#### 執行前檢查清單

在執行任何任務前，**必須**遵循以下步驟：

1. **檢查現有腳本**
   ```bash
   # 查看 scripts 目錄結構
   ls -R scripts/

   # 搜尋相關腳本
   find scripts/ -name "*.py" | grep <關鍵字>
   ```

2. **閱讀腳本說明**
   - 使用 `--help` 查看腳本用法
   - 閱讀腳本開頭的 docstring

3. **使用現有腳本**
   - 優先使用現有腳本
   - 必要時調整參數

4. **例外情況**（僅在以下情況才可自行撰寫）
   - ✅ `scripts/` 下確實無相關腳本
   - ✅ 現有腳本完全無法滿足需求
   - ✅ 需求屬於一次性特殊操作

#### 違反後果

❌ **不遵守此規範可能導致**：
- 重複造輪子，浪費開發時間
- 與現有架構不一致
- 缺乏統一的錯誤處理
- 資料不一致或損壞
- 無法追蹤執行歷史

#### 範例

**錯誤做法** ❌：
```python
# 使用者要求：「幫我收集 2026-02-01 的股價資料」
# AI 錯誤回應：「好的，我來寫一個程式收集資料...」
import requests
# ... 自行撰寫收集程式 ...
```

**正確做法** ✅：
```bash
# 使用者要求：「幫我收集 2026-02-01 的股價資料」
# AI 正確回應：「我會使用現有的收集腳本...」
python scripts/run_collection.py --date 2026-02-01 --types price
```

---

### Git Commit 格式

使用 Conventional Commits 規範：

```
<type>(<scope>): <subject>

<body>

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Type 類型**：
- `feat` - 新功能
- `fix` - 修復 bug
- `docs` - 文檔更新
- `refactor` - 重構
- `chore` - 雜項（建置、設定）
- `test` - 測試
- `data` - 資料更新

**範例**：
```bash
feat: 新增成交量前 20 名資料收集器

- 新增 Top20VolumeCollector
- 從 TWSE OpenAPI 收集每日成交量前 20 名
- 新增對應的資料驗證器

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

### 程式碼風格

- Python: 遵循 PEP 8
- 使用 type hints
- 完整的 docstrings
- 適當的錯誤處理

### 文檔更新

變更時需更新的文檔：
- **新功能或重大變更** → 更新 `README.md`
- **部署相關變更** → 更新 `deployment/README.md`
- **Docker 配置變更** → 更新 `deployment/stock-data-collector/README.md`
- **所有變更** → 更新 `CHANGELOG.md`

CHANGELOG.md 使用 Keep a Changelog 格式：

```markdown
## [Unreleased]

### Added
- 新增功能描述

### Changed
- 變更內容描述

### Fixed
- 修復問題描述

### Removed
- 移除項目描述
```

### 新增收集器

1. 在 `src/collectors/` 建立新的收集器類別
2. 繼承 `BaseCollector`
3. 實作 `collect()`, `validate()`, `save()` 方法
4. 在 `scripts/run_collection.py` 註冊新的收集器類型
5. 更新相關文檔

### 新增資料源

1. 在 `src/datasources/` 建立新的資料源類別
2. 實作統一的 API 介面
3. 加入錯誤處理與重試機制
4. 撰寫單元測試

---

## 🔒 安全注意事項

### 敏感資訊管理

- ✅ `.env` 檔案已在 `.gitignore` 中
- ✅ 日誌檔案 `*.log` 不提交到 Git
- ❌ 不要硬編碼 API keys、密碼或 tokens
- ❌ 不要提交包含敏感資訊的設定檔

### 提交前檢查清單

- [ ] 沒有硬編碼的密碼或 API token
- [ ] `.env` 檔案在 `.gitignore` 中
- [ ] 沒有提交敏感設定檔
- [ ] 日誌檔案已在 `.gitignore` 中
- [ ] 測試資料已清理

---

## 🎯 GitHub Actions 自動化

### 工作流程

1. **daily-collection.yml** - 每日資料收集
   - 排程: 週一至週六 21:30 (台北時間)
   - 自動判斷交易日
   - 收集完成後自動 commit 並 push

2. **backfill.yml** - 歷史資料回補
   - 手動觸發
   - 指定日期範圍回補資料

### 手動觸發

```bash
# 觸發每日收集
gh workflow run daily-collection.yml

# 觸發回補資料
gh workflow run backfill.yml
```

---

## 🛠️ 開發工具

### 必要工具

- Python 3.11+
- Git
- Docker & Docker Compose（選用）
- GitHub CLI（選用）

### Python 套件

主要依賴：
- `requests` - HTTP 請求
- `pandas` - 資料處理
- `python-dotenv` - 環境變數管理

---

## 📖 參考文件

### 核心文件

- [README.md](README.md) - 專案說明
- [data/README.md](data/README.md) - 資料結構說明
- [deployment/README.md](deployment/README.md) - 部署說明
- [.claude/skills/git/SKILL.md](.claude/skills/git/SKILL.md) - Git 提交流程
- [.claude/skills/data-pipeline/SKILL.md](.claude/skills/data-pipeline/SKILL.md) - 資料處理 Pipeline（收集→匯入→轉換）

### 規格書

- [PHASE1_DATA_COLLECTION.md](docs/specifications/PHASE1_DATA_COLLECTION.md) - 資料收集規格
- [DATA_VALIDATION_SPEC.md](docs/DATA_VALIDATION_SPEC.md) - 資料驗證規範

### API 文件

- [TWSE OpenAPI](https://openapi.twse.com.tw) - 證交所開放 API
- [TPEx OpenAPI](https://www.tpex.org.tw/openapi/v1) - 櫃買中心開放 API

---

## ⚠️ 已知問題與修正歷史

### 2026-02-02：資料源 API 限制與雙模式設計

**問題**: TWSE `STOCK_DAY_ALL` API 僅支援最新交易日資料，無法查詢歷史日期

**解決方案：雙模式設計**
- ✅ **即時模式**（推薦）：使用 `STOCK_DAY_ALL` OpenAPI，每日自動收集當天資料
- ⚠️ **回補模式**（緊急用）：使用 `STOCK_DAY` API 逐股查詢，速度慢（1,900 支 = 20-30 分鐘）

**建議**: 優先使用每日自動收集（GitHub Actions），回補模式僅用於緊急補少量資料

---

## 🚨 常見問題

### Docker 相關
- **Q: Docker daemon 未啟動？** A: 啟動 Docker Desktop 或使用 Python 腳本替代
- **Q: 不建議用 Docker 部署？** A: Docker 主要用於本地測試，生產環境建議使用 GitHub Actions

### 資料收集
- **Q: 如何判斷交易日？** A: 使用 `src/utils/date_helper.py` 的 `is_trading_day()` 函式
- **Q: 收集失敗？** A: 系統會自動重試最多 3 次，查看日誌了解錯誤原因
- **Q: 如何回補歷史資料？** A: 使用 `python scripts/data-collector/backfill_historical.py --date YYYY-MM-DD`

---

## 📞 支援

如有問題或建議：
1. 查看相關文檔
2. 搜尋 GitHub Issues
3. 建立新的 Issue 討論

---

**最後更新**: 2026-02-08
**維護者**: Jason Huang
**專案狀態**: Phase 1 完成，持續維護中
