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

1. **收集今日資料（自動偵測最近交易日）**
   ```bash
   python scripts/run_collection.py
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

4. **使用 Docker 收集**
   ```bash
   # 收集指定日期所有類型
   COLLECTION_DATE=2024-12-27 docker-compose up

   # 收集特定類型
   COLLECTION_DATE=2024-12-27 COLLECTION_TYPES="price margin" docker-compose up
   ```

### 設定 GitHub Actions 自動化

1. **Fork 此專案到你的 GitHub**
2. **在專案的 Actions 頁面啟用工作流程**
3. **無需任何設定** - 每交易日 18:00 自動收集並提交資料

**自動化時程**:
- **每日收集**: 每交易日 18:00 自動執行
- **回補資料**: 可透過 GitHub Actions 手動觸發

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
│       └── lending/             # 借券賣出資料
│
├── docs/                        # 文檔目錄
│   ├── DATA_VALIDATION_SPEC.md  # 資料驗證規範
│   └── specifications/          # 詳細規格書
│
└── build/                       # Docker 建置檔案
    └── Dockerfile               # Phase 1 Docker 映像檔
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
- **收集時間**: 約 2-3 分鐘（四種資料類型）
- **單日資料量**: 約 2.9 MB（5,834 筆記錄）
  - 價格資料: 600 KB（1,946 檔股票）
  - 融資融券: 877 KB（1,815 檔股票）
  - 三大法人: 987 KB（1,027 檔股票）
  - 借券賣出: 463 KB（1,046 檔股票）

### 儲存空間
- **每月**: 約 60-70 MB（20 個交易日）
- **每年**: 約 700-800 MB（240 個交易日）
- **檔案數量**: ~960 個檔案/年（每交易日 4 個檔案）

### 成本
- **GitHub Actions**: 完全在免費額度內運行
- **API 使用**: 官方免費 API，無需 Token
- **儲存空間**: GitHub 免費方案足夠使用

**實測環境**: Python 3.11, 一般家用寬頻, 測試日期 2025-12-26

---

## 📖 完整文檔

### 核心文件
- **[資料目錄說明](data/README.md)** - 資料結構與格式詳細說明
- **[資料驗證規範](docs/DATA_VALIDATION_SPEC.md)** - 完整驗證標準與抽樣機制

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

**最後更新**: 2025-12-28
**版本**: Phase 1 資料收集完成
