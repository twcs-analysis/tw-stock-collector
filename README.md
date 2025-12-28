# 台股資料收集與分析系統 (Taiwan Stock Data Collection & Analysis)

建立一個完整的台股資料收集與分析系統,從資料擷取、儲存、匯入資料庫,到最終的數據分析與視覺化。

---

## 🎯 專案架構

本專案採用**三階段架構**,將複雜的數據處理流程拆分為獨立的模組:

```
Phase 1: 資料擷取與儲存 (Data Collection)
    ↓ Git Repository
Phase 2: 資料庫設計與匯入 (Database Import)
    ↓ PostgreSQL/SQLite
Phase 3: 數據整理與分析 (Data Analysis)
    ↓ 投資決策支援
```

### 階段說明

#### **Phase 1: 資料擷取與儲存**
- 使用 **台灣證交所與櫃買中心官方 API** 收集資料
- 使用 **GitHub Actions** 自動化執行資料收集
- 將原始資料以 **JSON** 格式儲存至 Git 倉庫
- 利用 Git 進行版本控制與歷史追蹤
- 優點: 免費、即時、可追溯、分散式備份

📖 詳細規格: [Phase 1 規格書](docs/specifications/PHASE1_DATA_COLLECTION.md)

#### **Phase 2: 資料庫設計與匯入**
- 設計符合分析需求的**關聯式資料庫結構**
- 從 Git 倉庫讀取原始資料並匯入資料庫
- 實作資料驗證與完整性檢查
- 建立定時自動匯入機制

📖 詳細規格: [Phase 2 規格書](docs/specifications/PHASE2_DATABASE_IMPORT.md)

#### **Phase 3: 數據整理與分析**
- 計算技術指標 (MA, MACD, RSI, KD等)
- 籌碼分析 (法人動向、融資融券、主力追蹤)
- 多維度數據聚合與選股策略
- 視覺化儀表板與報表產出

📖 詳細規格: [Phase 3 規格書](docs/specifications/PHASE3_DATA_ANALYSIS.md)

---

## 📖 完整文檔

### 核心規格書
- **[Phase 1: 資料擷取與儲存](docs/specifications/PHASE1_DATA_COLLECTION.md)** - GitHub Actions 自動化收集
- **[Phase 2: 資料庫設計與匯入](docs/specifications/PHASE2_DATABASE_IMPORT.md)** - 資料庫結構與匯入流程
- **[Phase 3: 數據整理與分析](docs/specifications/PHASE3_DATA_ANALYSIS.md)** - 技術分析與籌碼分析

### 實作文檔
- **[整合計畫書](docs/INTEGRATION_PLAN.md)** - Phase 1 收集器整合架構設計
- **[官方 API 重構計畫](docs/REFACTOR_PLAN_TWSE_API.md)** - 從 FinMind 遷移至官方 API

### 參考文檔
- **[台股數據收集規格書](docs/specifications/TWSE_DATA_COLLECTION_SPEC.md)** - 完整資料收集系統設計
- **[文檔中心](docs/README.md)** - 所有文檔的導覽頁面
- **[專案路線圖](docs/project-management/PROJECT_ROADMAP.md)** - 專案開發規劃

---

## 🗂️ 專案結構

```
tw-stock-collector/
├── README.md                    # 本文件（專案說明）
├── requirements.txt             # Python 套件依賴
├── .env.example                 # 環境變數範例
│
├── .github/                     # GitHub Actions 自動化
│   └── workflows/
│       ├── daily-collection.yml     # 每日資料收集
│       ├── weekly-collection.yml    # 每週資料收集
│       └── backfill.yml             # 歷史資料回補
│
├── src/                         # 核心程式碼
│   ├── utils/                   # 工具函式庫
│   │   ├── __init__.py
│   │   ├── date_helper.py       # 交易日判斷、民國曆轉換
│   │   ├── file_helper.py       # 檔案操作、路徑管理
│   │   ├── logger.py            # 統一日誌記錄
│   │   └── data_merger.py       # 資料合併工具
│   │
│   ├── datasources/             # 資料源 API 封裝
│   │   ├── __init__.py
│   │   ├── base_datasource.py   # 資料源基礎類別
│   │   ├── twse_datasource.py   # 證交所 API（上市）
│   │   └── tpex_datasource.py   # 櫃買中心 API（上櫃）
│   │
│   └── collectors/              # 資料收集器
│       ├── __init__.py
│       ├── base.py              # BaseCollector 基礎類別
│       ├── price_collector.py   # 價格資料收集器
│       ├── margin_collector.py  # 融資融券收集器
│       ├── institutional_collector.py  # 三大法人收集器
│       └── lending_collector.py # 借券賣出收集器
│
├── scripts/                     # 執行腳本
│   ├── run_collection.py        # 統一資料收集入口（主腳本）
│   ├── database/                # Phase 2: 資料庫相關
│   │   ├── init_db.py          # 初始化資料庫
│   │   └── schema.py           # 資料表結構
│   └── analysis/                # Phase 3: 數據分析
│       ├── technical/          # 技術分析
│       ├── chip/               # 籌碼分析
│       └── composite/          # 綜合分析
│
├── data/                        # 資料儲存目錄（詳見下方說明）
│   ├── raw/                     # 原始資料（JSON 格式）
│   │   ├── price/              # 每日價格資料
│   │   ├── margin/             # 融資融券資料
│   │   ├── institutional/      # 三大法人資料
│   │   └── lending/            # 借券賣出資料
│   └── logs/                    # 收集日誌
│
├── docs/                        # 文檔目錄
│   ├── specifications/          # 規格書
│   │   ├── PHASE1_DATA_COLLECTION.md
│   │   ├── PHASE2_DATABASE_IMPORT.md
│   │   └── PHASE3_DATA_ANALYSIS.md
│   ├── project-management/      # 專案管理
│   │   ├── PROJECT_ROADMAP.md
│   │   └── DEVELOPMENT_SCHEDULE.md
│   └── INTEGRATION_PLAN.md      # 整合計畫書
│
├── config/                      # 配置檔案（未來使用）
│   ├── config.yaml
│   └── database.yaml
│
└── notebooks/                   # Jupyter 筆記本 (Phase 3)
    └── analysis/
```

### 📂 資料目錄結構說明

`data/raw/` 目錄下的資料採用**按日期聚合**的結構，每個檔案包含當日所有股票的資料：

```
data/raw/
├── price/                       # 價格資料（開高低收、成交量）
│   └── YYYY/                    # 年份目錄
│       └── MM/                  # 月份目錄
│           └── YYYY-MM-DD.json  # 單日檔案，包含所有股票的價格資料
│
├── margin/                      # 融資融券資料
│   └── YYYY/MM/YYYY-MM-DD.json  # 單日檔案，包含所有股票的融資融券資料
│
├── institutional/               # 三大法人買賣超資料
│   └── YYYY/MM/YYYY-MM-DD.json  # 單日檔案，包含所有股票的法人資料
│
└── lending/                     # 借券賣出資料
    └── YYYY/MM/YYYY-MM-DD.json  # 單日檔案，包含所有股票的借券資料
```

**已收集資料快速連結**：
- [價格資料](data/raw/price/) - 每日股票開高低收與成交量
- [三大法人](data/raw/institutional/) - 外資、投信、自營商買賣超
- [融資融券](data/raw/margin/) - 融資融券餘額與變化
- [借券賣出](data/raw/lending/) - 借券賣出餘額資料

**檔案格式範例** (`price/2025/12/2025-12-26.json`)：
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
    },
    // ... 更多股票資料
  ]
}
```

**資料特性**：
- ✅ **聚合檔案**：一個日期一個檔案，包含所有股票（約 1,000～2,000 檔）
- ✅ **自動分層**：依年份（YYYY）和月份（MM）分目錄，易於管理
- ✅ **標準格式**：統一的 JSON 結構，包含 metadata 和 data
- ✅ **資料來源**：使用台灣證交所（TWSE）和櫃買中心（TPEx）官方 API
- ✅ **版本控制**：存放於 Git，可追蹤歷史變更

---

## 🏗️ 核心架構設計

本專案採用**三層架構**設計，確保程式碼可維護性與擴展性：

```
┌─────────────────────────────────────────────┐
│         執行層 (Execution Layer)             │
│   scripts/run_collection.py                 │
│   - 統一入口                                 │
│   - 參數解析                                 │
│   - 執行協調                                 │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│        收集器層 (Collectors Layer)           │
│   src/collectors/                           │
│   - BaseCollector (抽象基礎類別)             │
│   - PriceCollector (價格收集器)              │
│   - MarginCollector (融資融券收集器)         │
│   - InstitutionalCollector (三大法人收集器)  │
│   - LendingCollector (借券收集器)            │
│                                             │
│   統一介面: collect() → save() → run()      │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│         工具層 (Utils Layer)                 │
│   src/utils/                                │
│   - date_helper: 交易日判斷、日期轉換        │
│   - file_helper: 檔案操作、路徑管理          │
│   - logger: 統一日誌記錄                     │
│   - data_merger: 資料合併工具                │
│                                             │
│   src/datasources/                          │
│   - TWSEDataSource: 證交所 API 封裝          │
│   - TPExDataSource: 櫃買中心 API 封裝        │
└─────────────────────────────────────────────┘
```

### 設計優勢

✅ **統一介面**: 所有收集器繼承 `BaseCollector`，提供一致的 `run()` 方法
✅ **易於擴展**: 新增資料類型只需繼承 `BaseCollector` 並實作 `collect()` 方法
✅ **錯誤處理**: 統一的異常處理與日誌記錄機制
✅ **交易日檢測**: 自動判斷週末與國定假日，避免無效查詢
✅ **標準化儲存**: 統一的檔案路徑規則 `data/raw/{type}/{YYYY}/{MM}/{date}.json`

詳細設計請參考 [整合計畫書](docs/INTEGRATION_PLAN.md)

---

## 🚀 快速開始

### 前置需求

- Python 3.11+
- Git
- PostgreSQL (Phase 2) 或 SQLite
- GitHub Account (Phase 1)

### Phase 1: 資料收集設定

1. **安裝 Python 套件**
   ```bash
   pip install -r requirements.txt
   ```

2. **收集指定日期的所有資料**
   ```bash
   python scripts/run_collection.py --date 2024-12-27
   ```

3. **收集特定類型的資料**
   ```bash
   # 只收集價格和融資融券資料
   python scripts/run_collection.py --date 2024-12-27 --types price margin

   # 可用類型: price, margin, institutional, lending
   ```

4. **使用最近交易日（自動偵測）**
   ```bash
   python scripts/run_collection.py
   ```

5. **檢查收集結果**
   ```bash
   # 查看 data/raw/ 目錄
   ls -R data/raw/

   # 範例輸出：
   # data/raw/price/2024/12/2024-12-27.json
   # data/raw/margin/2024/12/2024-12-27.json
   # data/raw/institutional/2024/12/2024-12-27.json
   # data/raw/lending/2024/12/2024-12-27.json
   ```

6. **使用 Docker 自動化收集**
   ```bash
   # 設定收集日期和類型
   COLLECTION_DATE=2024-12-27 COLLECTION_TYPES="price margin" docker-compose up

   # 收集所有類型
   COLLECTION_DATE=2024-12-27 docker-compose up
   ```

7. **設定 GitHub Actions 自動化**
   - Fork 此專案到你的 GitHub
   - 在專案的 Actions 頁面啟用工作流程
   - **無需設定 API Token**（使用官方免費 API）
   - 每交易日 18:00 自動收集並提交資料

**說明**：
- 📖 詳細使用方式請參考 [Phase 1 規格書](docs/specifications/PHASE1_DATA_COLLECTION.md)
- 📖 整合架構設計請參考 [整合計畫書](docs/INTEGRATION_PLAN.md)

### Phase 2: 資料庫建置

1. **安裝 Python 套件**
   ```bash
   pip install -r requirements.txt
   ```

2. **配置環境變數**
   ```bash
   cp .env.example .env
   # 編輯 .env 填入資料庫連線資訊
   ```

3. **初始化資料庫**
   ```bash
   python scripts/database/init_db.py
   ```

4. **執行資料匯入**
   ```bash
   # 匯入指定日期
   python scripts/run_import.py --date 2025-01-28

   # 批次匯入
   python scripts/run_import.py --start-date 2024-01-01 --end-date 2024-12-31
   ```

### Phase 3: 數據分析

1. **計算技術指標**
   ```bash
   python scripts/run_analysis.py --type technical
   ```

2. **執行選股策略**
   ```bash
   python scripts/run_analysis.py --type screening
   ```

3. **啟動視覺化儀表板**
   ```bash
   streamlit run scripts/dashboard/app.py
   ```

---

## 📊 資料涵蓋範圍

### 技術面資料
- ✅ **[每日價量資料](data/raw/price/)** - 開高低收、成交量
- ✅ 還原股價 (除權息調整)
- ✅ 技術指標 (MA, MACD, RSI, KD, 布林通道, OBV)

### 籌碼面資料
- ✅ **[三大法人買賣超](data/raw/institutional/)** - 外資、投信、自營商
- ✅ **[融資融券餘額](data/raw/margin/)** - 融資融券餘額與變化
- ✅ **[借券賣出資料](data/raw/lending/)** - 借券賣出餘額
- ✅ 外資持股比例
- ✅ 股權分散表
- ✅ 董監持股與質押比例

### 市場統計
- ✅ 每日市場總覽 (漲跌家數、成交量)
- ✅ 產業統計
- ✅ 強弱勢排行

---

## ⏰ 自動化時程

| 任務 | 頻率 | 執行時間 | 階段 |
|------|------|---------|------|
| 價量資料收集 | 每交易日 | 18:00 | Phase 1 |
| 法人籌碼收集 | 每交易日 | 18:00 | Phase 1 |
| 股權分散表 | 每週六 | 10:00 | Phase 1 |
| 資料匯入資料庫 | 每交易日 | 19:00 | Phase 2 |
| 技術指標計算 | 每交易日 | 19:30 | Phase 3 |
| 選股策略執行 | 每交易日 | 20:00 | Phase 3 |
| 每日報表產出 | 每交易日 | 20:30 | Phase 3 |

---

## 🎓 學習資源

### 官方資料來源
- [台灣證券交易所 (TWSE)](https://www.twse.com.tw) - 上市股票資料
- [證券櫃買中心 (TPEx)](https://www.tpex.org.tw) - 上櫃股票資料
- [TWSE OpenAPI](https://openapi.twse.com.tw) - 證交所開放 API
- [TPEx OpenAPI](https://www.tpex.org.tw/openapi/v1) - 櫃買中心開放 API

### 技術分析參考
- [TA-Lib 技術指標庫](https://ta-lib.org/)
- [Pandas-TA](https://github.com/twopirllc/pandas-ta)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

### 專案相關文檔
- [整合架構設計](docs/INTEGRATION_PLAN.md) - BaseCollector 模式與三層架構
- [Phase 1 規格書](docs/specifications/PHASE1_DATA_COLLECTION.md) - 資料收集詳細說明

---

## 🛡️ 資料品質保證

### 驗證機制
- ✅ 格式驗證 (欄位、型別、範圍)
- ✅ 完整性檢查 (筆數、股票清單)
- ✅ 一致性驗證 (交叉比對)
- ✅ 異常值檢測 (統計分析)

### 錯誤處理
- 🔄 自動重試 (失敗時最多3次)
- 📝 詳細日誌記錄
- 🚨 錯誤通知 (可選)

---

## 📈 效能指標

### Phase 1 (資料收集)
- **收集時間**: 約 2-3 分鐘（四種資料類型）
- **單日資料量**: 約 2.9 MB（5,834 筆記錄）
  - 價格資料：600 KB（1,946 檔股票）
  - 融資融券：877 KB（1,815 檔股票）
  - 三大法人：987 KB（1,027 檔股票）
  - 借券賣出：463 KB（1,046 檔股票）
- **儲存空間估算**:
  - 每月約 60-70 MB（20 個交易日）
  - 每年約 700-800 MB（240 個交易日）
- **檔案數量**: ~960 個檔案/年（每交易日 4 個檔案）
- **GitHub Actions**: 完全在免費額度內運行
- **資料來源**: 使用官方免費 API，無需 Token

### Phase 2 (資料匯入)
- 每日匯入時間: < 3 分鐘
- 資料庫大小: ~200MB/年

### Phase 3 (數據分析)
- 技術指標計算: < 5 分鐘
- 選股策略執行: < 2 分鐘

**實測環境**:
- Python 3.11
- 網路環境: 一般家用寬頻
- 測試日期: 2025-12-26

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

## ⚡ 快速命令參考

```bash
# 收集今日所有資料（自動偵測最近交易日）
python scripts/run_collection.py

# 收集指定日期的所有資料
python scripts/run_collection.py --date 2024-12-27

# 只收集特定類型資料
python scripts/run_collection.py --date 2024-12-27 --types price margin

# 跳過交易日檢查（測試或補資料用）
python scripts/run_collection.py --date 2024-12-27 --skip-trading-day-check

# 使用 Docker 收集
COLLECTION_DATE=2024-12-27 COLLECTION_TYPES="price margin institutional lending" docker-compose up

# 查看收集結果
ls -lh data/raw/price/2024/12/2024-12-27.json
cat data/raw/price/2024/12/2024-12-27.json | jq '.metadata'
```

---

**最後更新**: 2025-12-28
**版本**: 2.1 (整合架構完成)
