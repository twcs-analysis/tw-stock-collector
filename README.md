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
- 使用 **GitHub Actions** 自動化執行資料收集
- 將原始資料以 **JSON/CSV** 格式儲存至 Git 倉庫
- 利用 Git 進行版本控制與歷史追蹤
- 優點: 免費、可追溯、分散式備份

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

### 參考文檔
- **[台股數據收集規格書](docs/specifications/TWSE_DATA_COLLECTION_SPEC.md)** - 完整資料收集系統設計
- **[FinMind 實作指南](docs/specifications/FINMIND_IMPLEMENTATION_GUIDE.md)** - FinMind 免費版使用指南
- **[文檔中心](docs/README.md)** - 所有文檔的導覽頁面
- **[專案路線圖](docs/project-management/PROJECT_ROADMAP.md)** - 專案開發規劃

---

## 🗂️ 專案結構

```
tw-stock-collector/
├── README.md                    # 本文件
├── requirements.txt             # Python 套件依賴
├── .env.example                 # 環境變數範例
│
├── .github/                     # GitHub Actions
│   └── workflows/
│       ├── daily-collection.yml     # 每日資料收集
│       ├── weekly-collection.yml    # 每週資料收集
│       └── backfill.yml             # 歷史資料回補
│
├── data/                        # Phase 1: 原始資料儲存
│   ├── raw/                     # 原始資料 (JSON/CSV)
│   │   ├── price/              # 價量資料
│   │   │   └── YYYY/MM/YYYY-MM-DD.json  # 每日一檔，包含所有股票
│   │   ├── institutional/      # 法人籌碼
│   │   │   └── YYYY/MM/YYYY-MM-DD.json
│   │   ├── margin/             # 信用交易
│   │   │   └── YYYY/MM/YYYY-MM-DD.json
│   │   └── lending/            # 借券賣出
│   │       └── YYYY/MM/YYYY-MM-DD.json
│   └── logs/                    # 收集日誌
│
├── scripts/                     # 執行腳本
│   ├── collectors/              # Phase 1: 資料收集器
│   │   ├── price.py
│   │   ├── institutional.py
│   │   └── ...
│   ├── database/                # Phase 2: 資料庫相關
│   │   ├── init_db.py          # 初始化資料庫
│   │   └── schema.py           # 資料表結構
│   ├── importers/               # Phase 2: 資料匯入器
│   │   ├── price_importer.py
│   │   └── ...
│   ├── analysis/                # Phase 3: 數據分析
│   │   ├── technical/          # 技術分析
│   │   ├── chip/               # 籌碼分析
│   │   └── composite/          # 綜合分析
│   └── run_*.py                 # 主執行腳本
│
├── docs/                        # 文檔目錄
│   ├── specifications/          # 規格書
│   │   ├── PHASE1_DATA_COLLECTION.md
│   │   ├── PHASE2_DATABASE_IMPORT.md
│   │   └── PHASE3_DATA_ANALYSIS.md
│   └── project-management/      # 專案管理
│       ├── PROJECT_ROADMAP.md
│       └── DEVELOPMENT_SCHEDULE.md
│
├── config/                      # 配置檔案
│   ├── config.yaml
│   └── database.yaml
│
└── notebooks/                   # Jupyter 筆記本 (Phase 3)
    └── analysis/
```

---

## 🚀 快速開始

### 前置需求

- Python 3.11+
- Git
- PostgreSQL (Phase 2) 或 SQLite
- GitHub Account (Phase 1)

### Phase 1: 資料收集設定

1. **Fork 此專案** 到你的 GitHub

2. **設定 GitHub Actions Secrets** (如需要)
   ```
   FINMIND_API_TOKEN=你的FinMind Token
   ```

3. **啟用 GitHub Actions**
   - 在專案的 Actions 頁面啟用工作流程
   - 手動觸發一次測試

4. **檢查資料收集**
   ```bash
   # 查看 data/raw/ 目錄
   ls -R data/raw/
   ```

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
- ✅ 每日價量資料 (開高低收、成交量)
- ✅ 還原股價 (除權息調整)
- ✅ 技術指標 (MA, MACD, RSI, KD, 布林通道, OBV)

### 籌碼面資料
- ✅ 三大法人買賣超 (外資、投信、自營商)
- ✅ 融資融券餘額與變化
- ✅ 借券賣出資料
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

### 資料來源官方文檔
- [FinMind 官網](https://finmindtrade.com/)
- [FinMind API 文檔](https://finmind.github.io/)
- [台灣證券交易所](https://www.twse.com.tw)
- [證券櫃買中心](https://www.tpex.org.tw)

### 技術分析參考
- [TA-Lib 技術指標庫](https://ta-lib.org/)
- [Pandas-TA](https://github.com/twopirllc/pandas-ta)

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
- 每日收集時間: < 5 分鐘
- 儲存空間: ~60MB/月
- 檔案數量: ~1,000 個檔案/年（每日 4 個檔案）
- GitHub Actions 免費額度內

### Phase 2 (資料匯入)
- 每日匯入時間: < 3 分鐘
- 資料庫大小: ~200MB/年

### Phase 3 (數據分析)
- 技術指標計算: < 5 分鐘
- 選股策略執行: < 2 分鐘

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
**版本**: 2.0 (三階段架構)
