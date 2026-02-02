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

### 籌碼面資料
- ✅ **[三大法人買賣超](data/raw/institutional/)** - 外資、投信、自營商
- ✅ **[融資融券餘額](data/raw/margin/)** - 融資融券餘額與變化
- ✅ **[借券賣出資料](data/raw/lending/)** - 借券賣出餘額
- ✅ 外資持股比例
- ✅ 股權分散表
- ✅ 董監持股與質押比例

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
- GitHub Account (用於自動化收集)

### 安裝步驟

1. **Clone 專案**
   ```bash
   git clone https://github.com/twcs-analysis/tw-stock-collector.git
   cd tw-stock-collector
   ```

2. **安裝 Python 套件**
   ```bash
   pip install -r requirements.txt
   ```

### 本地收集資料

#### 使用 Python 腳本

```bash
# 收集當天資料（預設使用當天日期）
python scripts/run_collection.py

# 收集指定日期的所有資料
python scripts/run_collection.py --date 2024-12-27

# 收集特定類型的資料
python scripts/run_collection.py --date 2024-12-27 --types price margin
# 可用類型: price, institutional, margin, lending, top20_volume

# 回補歷史資料
python scripts/backfill.py --start 2025-01-01 --end 2025-01-31
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
- **每日收集**: 週一至週六 21:30 (台北時間) 自動執行
- **收集日期**: 預設收集當天日期的資料
- **自動判斷**: 跳過非交易日，只在交易日收集資料
- **自動提交**: 收集完成後自動 commit 並 push 到 Git

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
│   └── YYYY/MM/YYYY-MM-DD.json  # 單日檔案，包含所有股票
│
├── institutional/               # 三大法人買賣超資料
│   └── YYYY/MM/YYYY-MM-DD.json
│
├── margin/                      # 融資融券資料
│   └── YYYY/MM/YYYY-MM-DD.json
│
└── lending/                     # 借券賣出資料
    └── YYYY/MM/YYYY-MM-DD.json
```

**已收集資料快速連結**：
- [價格資料](data/raw/price/) - 每日股票開高低收與成交量
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

```
tw-stock-collector/
├── README.md                    # 本文件（專案說明）
├── requirements.txt             # Python 套件依賴
│
├── .github/workflows/           # GitHub Actions 自動化
│   ├── daily-collection.yml     # 每日資料收集
│   ├── backfill.yml             # 歷史資料回補
│   └── ci.yml                   # CI/CD 流程
│
├── src/                         # 核心程式碼
│   ├── collectors/              # 資料收集器
│   │   ├── base.py              # BaseCollector 基礎類別
│   │   ├── price_collector.py   # 價格資料收集器
│   │   ├── margin_collector.py  # 融資融券收集器
│   │   ├── institutional_collector.py  # 三大法人收集器
│   │   └── lending_collector.py # 借券賣出收集器
│   │
│   ├── datasources/             # 資料源 API 封裝
│   │   ├── twse_datasource.py   # 證交所 API（上市）
│   │   └── tpex_datasource.py   # 櫃買中心 API（上櫃）
│   │
│   └── utils/                   # 工具函式庫
│       ├── date_helper.py       # 交易日判斷、日期轉換
│       ├── file_handler.py      # 檔案操作、路徑管理
│       └── logger.py            # 統一日誌記錄
│
├── scripts/                     # 執行腳本
│   ├── run_collection.py        # 資料收集主腳本
│   └── backfill.py              # 歷史資料回補腳本
│
├── data/                        # 資料儲存目錄
│   └── raw/                     # 原始資料（JSON 格式）
│       ├── price/               # 每日價格資料
│       ├── margin/              # 融資融券資料
│       ├── institutional/       # 三大法人資料
│       ├── lending/             # 借券賣出資料
│       └── top20_volume/        # 成交量前 20 名
│
├── database/                    # 資料庫相關
│   ├── schemas/                 # 資料庫 Schema 定義
│   │   ├── common/              # PostgreSQL + SQLite 共用
│   │   ├── postgresql/          # PostgreSQL 專用
│   │   └── sqlite/              # SQLite 專用
│   ├── backups/                 # 資料庫備份
│   ├── seeds/                   # 測試資料
│   └── sqlite/                  # SQLite 檔案儲存
│
├── deployment/                  # 部署配置
│   ├── deploy.sh                # 部署腳本
│   ├── stock-data-collector/    # 資料收集服務
│   ├── database/                # 資料庫服務
│   │   ├── postgresql/          # PostgreSQL 部署
│   │   └── sqlite/              # SQLite 部署
│   └── data-import-pipeline/    # 資料匯入管道
│
├── docs/                        # 文檔目錄
│   ├── DATA_VALIDATION_SPEC.md  # 資料驗證規範
│   ├── database/                # 資料庫文檔
│   │   ├── QUERY_EXAMPLES.md    # SQL 查詢範例
│   │   └── QUICK_REFERENCE.md   # 快速參考手冊
│   └── specifications/          # 詳細規格書
│
├── transcripts/                 # 教學影片逐字稿
│   ├── raw/                     # 原始逐字稿
│   └── notes/                   # 重點整理
│
└── build/                       # Docker 建置檔案
    ├── stock-data-collector/    # 資料收集器映像檔
    └── data-importer/           # 資料匯入器映像檔
```

---

## ⚡ 快速命令參考

### 本地收集資料

```bash
# 收集今日所有資料（自動偵測最近交易日）
python scripts/run_collection.py

# 收集指定日期的所有資料
python scripts/run_collection.py --date 2024-12-27

# 只收集特定類型資料
python scripts/run_collection.py --date 2024-12-27 --types price margin

# 跳過交易日檢查（測試或補資料用）
python scripts/run_collection.py --date 2024-12-27 --skip-trading-day-check
```

### Docker 部署

```bash
# 使用 Docker 收集資料
COLLECTION_DATE=2024-12-27 docker-compose up

# 使用 GitHub Container Registry 映像檔
docker run --rm \
  -v $(pwd)/data:/app/data \
  ghcr.io/twcs-analysis/tw-stock-collector:phase1-latest \
  --date 2024-12-27
```

### 檢視資料

```bash
# 查看收集結果
ls -lh data/raw/price/2024/12/2024-12-27.json

# 使用 jq 查看 metadata
cat data/raw/price/2024/12/2024-12-27.json | jq '.metadata'

# 統計資料筆數
cat data/raw/price/2024/12/2024-12-27.json | jq '.data | length'
```

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
- **收集時間**: 約 2-3 分鐘（五種資料類型）
- **單日資料量**: 約 6.1 MB（6,528 筆記錄）
  - 價格資料: 604 KB（1,954 檔股票）
  - 三大法人: 4.1 MB（1,721 檔股票）
  - 融資融券: 980 KB（1,819 檔股票）
  - 借券賣出: 551 KB（1,014 檔股票）
  - 成交量前 20 名: 6.6 KB（20 檔股票）

### 儲存空間
- **每月**: 約 120 MB（20 個交易日）
- **每年**: 約 1.4 GB（240 個交易日）
- **檔案數量**: ~1,200 個檔案/年（每交易日 5 個檔案）

### 成本
- **GitHub Actions**: 完全在免費額度內運行
- **API 使用**: 官方免費 API，無需 Token
- **儲存空間**: GitHub 免費方案足夠使用

**實測環境**: Python 3.11, 一般家用寬頻, 測試日期 2024-12-27

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

- **移動平均線**: MA5, MA10, MA20, MA60, MA120, MA240
- **RSI 指標**: RSI6, RSI14
- **MACD 指標**: DIF, DEA, Histogram
- **DMI 指標**: PDI, MDI, ADX, ADXR
- **布林通道**: Upper, Mid, Lower
- **成交量分析**: Vol MA5, Vol MA20, Vol Ratio, VWAP

### 快速部署資料庫

```bash
# PostgreSQL
cd deployment/database/postgresql
cp .env.example .env
# 編輯 .env 設定密碼
docker-compose up -d

# SQLite
cd deployment/database/sqlite
cp .env.example .env
docker-compose up -d
```

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

**最後更新**: 2026-02-01
**版本**: Phase 1 資料收集完成 + 資料庫架構建置完成
