# 台股資料收集與分析系統 (Taiwan Stock Data Collection & Analysis)

建立一個完整的台股資料收集與分析系統,從資料擷取、儲存、匯入資料庫,到最終的數據分析與視覺化。

---

## 🎯 專案特色

- ✅ **自動化收集**: GitHub Actions 每交易日 18:00 自動執行
- ✅ **官方資料源**: 使用台灣證交所與櫃買中心官方 API
- ✅ **無需 API Token**: 完全使用免費公開 API
- ✅ **版本控制**: Git 追蹤所有資料歷史變更
- ✅ **標準化格式**: 統一的 JSON 資料結構
- ✅ **完整驗證**: 三層資料驗證機制

---

## 📊 資料涵蓋範圍

### 技術面資料
- ✅ **[每日價量資料](data/raw/price/)** - 開高低收、成交量
- ✅ 還原股價 (除權息調整)
- ✅ 技術指標 (MA, MACD, RSI, KD, 布林通道, OBV)

### 基本面資料
- ✅ **[月營收資料](data/raw/revenue-daily/)** - 每月營業收入、年增率、月增率（2025 年完整資料）
- 📅 財報資料（規劃中）
- 📅 股利政策（規劃中）

### 籌碼面資料
- ✅ **[三大法人買賣超](data/raw/institutional/)** - 外資、投信、自營商
- ✅ **[融資融券餘額](data/raw/margin/)** - 融資融券餘額與變化
- ✅ **[借券賣出資料](data/raw/lending/)** - 借券賣出餘額
- ✅ 外資持股比例
- ✅ 股權分散表
- ✅ 董監持股與質押比例

### 衍生性商品
- ✅ **[個股期貨](data/raw/stock_futures/)** - 每日期貨交易資料（開高低收、成交量、未平倉）

### 市場統計
- ✅ **[成交量前 20 名](data/raw/top20_volume/)** - 每日成交量排行
- ✅ 每日市場總覽 (漲跌家數、成交量)
- ✅ 產業統計
- ✅ 強弱勢排行

---

## 🚀 快速開始

### 前置需求

- Python 3.11+
- Git
- **Git LFS** (用於大型資料檔案)
- GitHub Account (用於自動化收集)

### 安裝步驟

1. **安裝 Git LFS**
   ```bash
   # macOS
   brew install git-lfs

   # Ubuntu/Debian
   sudo apt-get install git-lfs

   # 初始化 Git LFS
   git lfs install
   ```

2. **Clone 專案**
   ```bash
   git clone https://github.com/twcs-analysis/tw-stock-collector.git
   cd tw-stock-collector
   ```

3. **安裝 Python 套件**
   ```bash
   pip install -r requirements.txt
   ```

> 💡 **關於 Git LFS**: 本專案使用 Git LFS 管理大型資料檔案（`data/` 目錄）。詳細說明請參考 [Git LFS 使用指南](docs/GIT_LFS_GUIDE.md)。

### 本地收集資料

#### 使用 Shell 腳本（推薦）

```bash
# 收集每日資料（價格、籌碼面）
./scripts/data-collector/collect.sh

# 收集指定日期的所有資料
./scripts/data-collector/collect.sh 2026-02-02

# 收集特定類型的資料
./scripts/data-collector/collect.sh 2026-02-02 price margin
# 可用類型: price, institutional, margin, lending, top20_volume

# 回補歷史資料（自動完成：收集 → 匯入 → 轉換）
./scripts/data-collector/backfill.sh 2026-01-01 2026-01-31

# 收集月營收資料
# Daily 模式（1-10 日使用，增量更新）
python3.11 scripts/data-collector/collect_revenue.py --mode daily --year-month 2026-01

# Monthly 模式（10 日後使用，完整資料）
python3.11 scripts/data-collector/collect_revenue.py --mode monthly --year-month 2026-01

# 收集個股期貨資料
./scripts/data-collector/collect_stock_futures.sh                    # 收集當天資料
./scripts/data-collector/collect_stock_futures.sh 2026-03-13         # 收集指定日期
./scripts/data-collector/backfill_stock_futures.sh 2026              # 回補整年資料
./scripts/data-collector/backfill_stock_futures.sh 2026-01-01 2026-03-31  # 回補指定範圍
```

#### 使用 Python 腳本

```bash
# 或使用 Python 直接調用
python scripts/run_collection.py --date 2026-02-02
python scripts/backfill.py --start 2026-01-01 --end 2026-01-31
```

#### 使用 Docker

```bash
# 進入 deployment 目錄
cd deployment/stock-data-collector

# 1. 準備環境
cp .env.example .env

# 2. 修改收集日期
# 編輯 docker-compose.yml 中的 command 參數
# command: ["--date", "2024-12-27", "--skip-trading-day-check"]

# 3. 執行收集
docker-compose up

# 4. 查看結果
ls -lh ../../data/raw/price/2024/12/
```

**注意事項:**
- Docker 方式需要手動修改 `docker-compose.yml` 中的日期
- 主要用於本地開發測試,不支援環境變數動態設定
- 建議使用 Python 腳本或 GitHub Actions 進行自動化收集

詳細說明: [deployment/stock-data-collector/README.md](deployment/stock-data-collector/README.md)

### 設定 GitHub Actions 自動化

1. **Fork 此專案到你的 GitHub**
2. **在專案的 Actions 頁面啟用工作流程**
3. **無需任何設定** - 系統會自動運作

**自動化時程**:
- **每日收集**: 週一至週五 21:30 (台北時間) 自動執行
- **收集日期**: 預設收集當天日期的資料
- **自動判斷**: 跳過非交易日，只在交易日收集資料
- **自動提交**: 收集完成後自動 commit 並 push 到 Git
- **Git LFS**: 資料檔案使用 LFS 儲存，節省倉庫空間

**手動觸發**:
```bash
# 手動觸發每日收集
gh workflow run daily-collection.yml

# 手動觸發回補資料
gh workflow run backfill.yml
```

---

## 📁 資料結構

### 目錄架構

```
data/raw/
├── price/                       # 價格資料（開高低收、成交量）
├── institutional/               # 三大法人買賣超資料
├── margin/                      # 融資融券資料
├── lending/                     # 借券賣出資料
├── revenue-daily/               # 月營收資料（Daily 模式）
└── revenue-monthly/             # 月營收資料（Monthly 模式）
```

**已收集資料快速連結**：
- [價格資料](data/raw/price/) - 每日股票開高低收與成交量
- [月營收資料](data/raw/revenue-daily/) - 每月營業收入、年增率、月增率（2025 年完整資料）
- [三大法人](data/raw/institutional/) - 外資、投信、自營商買賣超
- [融資融券](data/raw/margin/) - 融資融券餘額與變化
- [借券賣出](data/raw/lending/) - 借券賣出餘額資料
- [成交量前 20 名](data/raw/top20_volume/) - 每日成交量排行

### 檔案格式

**範例檔案** (`price/2025/12/2025-12-26.json`)：
```json
{
  "metadata": {
    "date": "2025-12-26",
    "collected_at": "2025-12-26T18:30:45",
    "total_count": 1946,
    "source": "TWSE + TPEx Official API"
  },
  "data": [
    {
      "date": "2025-12-26",
      "stock_id": "2330",
      "stock_name": "台積電",
      "open": 1080.0,
      "high": 1095.0,
      "low": 1075.0,
      "close": 1090.0,
      "volume": 45678912,
      "type": "twse"
    }
    // ... 更多股票資料
  ]
}
```

**資料特性**：
- ✅ **聚合檔案**: 一個日期一個檔案，包含所有股票（約 1,000～2,000 檔）
- ✅ **自動分層**: 依年份（YYYY）和月份（MM）分目錄
- ✅ **標準格式**: 統一的 JSON 結構，包含 metadata 和 data
- ✅ **官方來源**: 台灣證交所（TWSE）和櫃買中心（TPEx）官方 API
- ✅ **版本控制**: 存放於 Git，可追蹤歷史變更

詳細說明請參考: [資料目錄說明文件](data/README.md)

---

## 🗂️ 專案結構

### 核心目錄

```
tw-stock-collector/
├── services/common/             # 共用核心模組（collectors, datasources, utils）
├── scripts/                     # 執行腳本（收集、匯入、轉換）
├── data/                        # 資料儲存目錄
│   ├── raw/                     # 原始資料（JSON 格式）
│   └── transformed/             # 轉換後資料（技術指標）
├── database/                    # 資料庫相關（schemas, backups）
├── analysis/                    # 技術分析工具
├── .github/workflows/           # GitHub Actions 自動化
└── deployment/                  # 部署配置
```

完整結構請參考 [CLAUDE.md](CLAUDE.md)

---

## 🛡️ 資料品質保證

### 驗證機制
- ✅ **結構驗證**: 檔案格式、JSON 有效性
- ✅ **完整性檢查**: 欄位完整、筆數範圍
- ✅ **合理性驗證**: 數值範圍、邏輯一致性

詳細規範請參考: [資料驗證規範](docs/DATA_VALIDATION_SPEC.md)

### 錯誤處理
- 🔄 自動重試機制（失敗時最多 3 次）
- 📝 完整日誌記錄
- 🚨 錯誤通知與追蹤

---

## 📈 效能指標

### 資料收集

**每日資料**（五種類型）：
- **收集時間**: 約 2-3 分鐘
- **單日資料量**: 約 6.1 MB（6,528 筆記錄）
- **儲存空間**: 約 120 MB/月（20 個交易日）

**月營收資料**：
- **收集時間**: 約 10-15 分鐘/月份
- **單月資料量**: 約 945 KB（1,940 檔股票）
- **2025 年完整資料**: 11 個月，約 10.3 MB

### 成本
- **GitHub Actions**: 完全在免費額度內運行
- **API 使用**: 官方免費 API，無需 Token
- **儲存空間**: GitHub 免費方案足夠使用

---

## 🗄️ 資料庫架構

### 支援的資料庫

- **PostgreSQL 16+** - 生產環境推薦
- **SQLite 3.35+** - 開發/測試環境

### 資料表設計

系統包含 9 個主要資料表：

1. **stocks** - 股票基本資訊
2. **stock_price_daily** - 每日價格資料
3. **stock_institutional_daily** - 三大法人買賣超
4. **stock_margin_daily** - 融資融券資料
5. **stock_lending_daily** - 借券賣出資料
6. **stock_top20_volume_daily** - 成交量前 20 名
7. **stock_analysis_daily** - 技術分析寬表（30+ 技術指標）
8. **data_collection_log** - 資料收集記錄
9. **data_import_log** - 資料匯入記錄

### 技術分析寬表

`stock_analysis_daily` 表包含完整的技術指標：
- 移動平均線（MA5～MA240）
- RSI、MACD、DMI/ADX
- 布林通道、成交量分析

### 查詢範例文檔

完整的 SQL 查詢範例請參考：
- **[SQL 查詢範例](docs/database/QUERY_EXAMPLES.md)** - 60+ 實用 SQL 查詢
- **[快速參考手冊](docs/database/QUICK_REFERENCE.md)** - 常用查詢速查表

---

## 📖 完整文檔

### 核心文件
- **[資料目錄說明](data/README.md)** - 資料結構與格式詳細說明
- **[資料庫說明](database/README.md)** - 資料庫架構與 Schema 說明
- **[資料驗證規範](docs/DATA_VALIDATION_SPEC.md)** - 完整驗證標準與抽樣機制
- **[TWSE API 參考文件](docs/TWSE_API_REFERENCE.md)** - 證交所 OpenAPI 完整端點說明
- **[交易日曆服務](services/common/calendar/README.md)** - 證交所交易日曆查詢與驗證服務

### 資料庫文檔
- **[SQL 查詢範例](docs/database/QUERY_EXAMPLES.md)** - 涵蓋選股策略、效能優化等 60+ 查詢範例
- **[快速參考手冊](docs/database/QUICK_REFERENCE.md)** - 常用 SQL 查詢速查表

### 部署文檔
- **[部署說明](deployment/README.md)** - 整體部署架構與快速開始
- **[PostgreSQL 部署](deployment/database/postgresql/README.md)** - PostgreSQL 部署詳細說明
- **[SQLite 部署](deployment/database/sqlite/README.md)** - SQLite 部署詳細說明

### 規格書
- **[Phase 1: 資料擷取與儲存](docs/specifications/PHASE1_DATA_COLLECTION.md)** - GitHub Actions 自動化收集
- **[Phase 2: 資料庫設計與匯入](docs/specifications/PHASE2_DATABASE_IMPORT.md)** - 資料庫結構與匯入流程
- **[Phase 3: 數據整理與分析](docs/specifications/PHASE3_DATA_ANALYSIS.md)** - 技術分析與籌碼分析

---

## 🎓 資料來源

### 官方 API
- [台灣證券交易所 (TWSE)](https://www.twse.com.tw) - 上市股票資料
- [證券櫃買中心 (TPEx)](https://www.tpex.org.tw) - 上櫃股票資料
- [TWSE OpenAPI](https://openapi.twse.com.tw) - 證交所開放 API
- [TPEx OpenAPI](https://www.tpex.org.tw/openapi/v1) - 櫃買中心開放 API

### 技術參考
- [TA-Lib 技術指標庫](https://ta-lib.org/)
- [Pandas-TA](https://github.com/twopirllc/pandas-ta)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

---

## 🤝 貢獻指南

歡迎提交 Issue 或 Pull Request！

### 開發流程
1. Fork 此專案
2. 建立 feature 分支
3. 提交變更
4. 發送 Pull Request

---

## 📄 授權

MIT License

---

## 👤 維護者

**Jason Huang**

如有問題或建議,歡迎開 Issue 討論！

---

## 🎉 最新進展

### 2026-02-08: 月營收資料收集完成
- ✅ 完成 2025 年全年月營收資料收集（2025-01 至 2025-11）
- ✅ 總計 11 個月份，約 21,340 筆資料
- ✅ 資料儲存於 `data/raw/revenue-daily/2025/`
- 📊 詳細收集狀態請參考：[revenue_collection_status.md](revenue_collection_status.md)

---

**最後更新**: 2026-02-08
**版本**: 新增月營收資料收集功能 - 2025 年完整資料
