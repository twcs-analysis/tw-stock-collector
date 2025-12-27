# Phase 1: 資料擷取與儲存

## 📋 階段概述

本階段專注於**自動化資料收集**，透過 GitHub Actions 定時執行資料擷取任務，將台股相關數據以檔案形式儲存至 Git 倉庫中。

**核心目標**:
- 建立穩定的自動化資料收集流程
- 使用 Git 作為資料版本控制與儲存媒介
- 確保資料完整性與可追溯性

---

## 🎯 設計理念

### 為什麼使用 Git 儲存資料？

1. **版本控制**: 每次資料更新都有完整歷史記錄
2. **可追溯性**: 可以回溯任何時間點的資料狀態
3. **免費儲存**: GitHub 提供免費的 Git LFS 和倉庫空間
4. **自動化**: GitHub Actions 提供免費的 CI/CD 運行時間
5. **分散式**: 資料可以被多個專案或服務使用
6. **備份**: Git 本身就是分散式備份系統

### 與資料庫方案的對比

| 特性 | Git 檔案儲存 | 資料庫儲存 |
|------|-------------|-----------|
| 成本 | 免費 | 需要主機成本 |
| 版本控制 | 原生支援 | 需額外實作 |
| 查詢效能 | 較低 | 高 |
| 適用場景 | 歷史資料收集 | 即時查詢分析 |
| 維護成本 | 低 | 較高 |

**結論**: 上半段使用 Git 儲存，中段再匯入資料庫進行分析。

---

## 📊 資料來源與收集策略

### 資料來源選擇

#### FinMind API (主要來源)
- **優點**:
  - 免費且穩定
  - API 介面完整
  - 資料品質良好
  - 涵蓋大部分需求
- **限制**:
  - 免費版有請求頻率限制
  - 部分進階資料需付費

#### 其他資料來源 (備用/補充)
- **台灣證券交易所 (TWSE)**: 官方資料，最準確
- **證券櫃買中心 (TPEx)**: 上櫃股票資料
- **公開資訊觀測站 (MOPS)**: 財報、董監持股等

### 收集頻率規劃

| 資料類型 | 更新頻率 | GitHub Actions 排程 |
|---------|---------|-------------------|
| 每日價量資料 | 每交易日 | `0 18 * * 1-5` (18:00, 週一至週五) |
| 三大法人買賣超 | 每交易日 | `0 18 * * 1-5` |
| 融資融券 | 每交易日 | `0 18 * * 1-5` |
| 借券資料 | 每交易日 | `0 18 * * 1-5` |
| 外資持股 | 每交易日 | `0 18 * * 1-5` |
| 股權分散表 | 每週 | `0 10 * * 6` (週六 10:00) |
| 董監持股 | 每週 | `0 10 * * 6` |
| 股票清單 | 每月 | `0 2 1 * *` (每月 1 日) |

---

## 🗂️ 資料儲存結構

### 目錄架構設計

```
data/
├── raw/                          # 原始資料 (JSON/CSV)
│   ├── price/                    # 價量資料
│   │   ├── daily/               # 每日價量
│   │   │   ├── 2025/
│   │   │   │   ├── 01/
│   │   │   │   │   ├── 20250102.json
│   │   │   │   │   ├── 20250103.json
│   │   │   │   │   └── ...
│   │   │   │   └── 02/
│   │   │   └── 2024/
│   │   └── adjusted/            # 還原股價
│   │       └── YYYY/MM/
│   ├── institutional/           # 法人籌碼
│   │   ├── investors/          # 三大法人買賣超
│   │   │   └── YYYY/MM/
│   │   ├── foreign_holding/    # 外資持股
│   │   │   └── YYYY/MM/
│   │   └── major_trades/       # 八大行庫 (若有)
│   │       └── YYYY/MM/
│   ├── margin/                  # 信用交易
│   │   ├── margin_trading/     # 融資融券
│   │   │   └── YYYY/MM/
│   │   └── securities_lending/ # 借券
│   │       └── YYYY/MM/
│   ├── ownership/               # 持股結構
│   │   ├── shareholding/       # 股權分散表
│   │   │   └── YYYY/MM/
│   │   └── directors/          # 董監持股
│   │       └── YYYY/MM/
│   └── metadata/                # 基礎資料
│       ├── stock_list/         # 股票清單
│       │   └── YYYY/MM/
│       └── trading_calendar/   # 交易日曆
│           └── YYYY/
└── logs/                        # 執行日誌
    └── collection/
        └── YYYY/MM/
```

### 檔案命名規範

#### 每日資料
- 格式: `YYYYMMDD.json` 或 `YYYYMMDD.csv`
- 範例: `20250128.json`

#### 每週資料
- 格式: `YYYY-Www.json` (ISO 週次)
- 範例: `2025-W05.json`

#### 每月資料
- 格式: `YYYY-MM.json`
- 範例: `2025-01.json`

### 資料格式選擇

#### JSON vs CSV 對比

| 格式 | 優點 | 缺點 | 使用場景 |
|------|------|------|---------|
| JSON | 結構化、易解析、支援巢狀 | 檔案較大 | 複雜結構資料 |
| CSV | 檔案小、Excel 可讀 | 結構扁平、需額外處理 | 簡單表格資料 |

**建議**:
- 每日價量資料: CSV (檔案小、結構簡單)
- 法人籌碼資料: JSON (包含多層資訊)
- 持股結構: JSON (巢狀結構)

---

## ⚙️ GitHub Actions 自動化

### 工作流程設計

#### 1. 每日資料收集 (`daily-collection.yml`)

**觸發條件**:
- Cron 排程: `0 18 * * 1-5` (平日 18:00)
- 手動觸發: workflow_dispatch

**執行步驟**:
1. 檢查是否為交易日
2. 執行資料收集腳本
3. 驗證資料完整性
4. 提交至 Git
5. 推送至遠端

#### 2. 每週資料收集 (`weekly-collection.yml`)

**觸發條件**:
- Cron 排程: `0 10 * * 6` (週六 10:00)
- 手動觸發: workflow_dispatch

**收集項目**:
- 股權分散表
- 董監持股變動

#### 3. 歷史資料回補 (`backfill.yml`)

**觸發條件**:
- 手動觸發: workflow_dispatch
  - 輸入參數: start_date, end_date, data_type

**用途**:
- 補充缺失的歷史資料
- 首次初始化資料

---

## 🔄 資料收集流程

### 收集腳本架構

#### 目錄結構
```
scripts/
├── collectors/
│   ├── __init__.py
│   ├── base.py              # 基礎收集器類別
│   ├── price.py             # 價量資料收集器
│   ├── institutional.py     # 法人資料收集器
│   ├── margin.py            # 信用交易收集器
│   └── ownership.py         # 持股結構收集器
├── utils/
│   ├── __init__.py
│   ├── date_helper.py       # 日期工具
│   ├── validator.py         # 資料驗證
│   └── file_helper.py       # 檔案操作
└── run_collection.py        # 主執行腳本
```

### 執行流程

1. **前置檢查**
   - 檢查是否為交易日
   - 檢查資料是否已存在
   - 驗證 API 可用性

2. **資料收集**
   - 依序執行各收集器
   - 實作重試機制 (最多 3 次)
   - 記錄執行日誌

3. **資料驗證**
   - 檢查資料完整性
   - 驗證欄位格式
   - 比對資料筆數

4. **資料儲存**
   - 按規範儲存至對應目錄
   - 產生 metadata (收集時間、資料筆數等)
   - 更新索引檔案

5. **Git 提交**
   - Git add 新增檔案
   - Git commit (包含收集日期、資料類型)
   - Git push 至遠端

---

## 📝 資料清單

### 技術面資料

#### 1. 每日價量資料
- **資料項目**:
  - 日期、股票代號
  - 開盤價、最高價、最低價、收盤價
  - 成交量、成交金額
  - 成交筆數

- **儲存路徑**: `data/raw/price/daily/YYYY/MM/YYYYMMDD.csv`

#### 2. 還原股價資料
- **資料項目**:
  - 除權息調整後價格
  - 還原權值

- **儲存路徑**: `data/raw/price/adjusted/YYYY/MM/YYYYMMDD.json`

### 籌碼面資料

#### 3. 三大法人買賣超
- **資料項目**:
  - 外資買賣超金額與張數
  - 投信買賣超金額與張數
  - 自營商買賣超金額與張數

- **儲存路徑**: `data/raw/institutional/investors/YYYY/MM/YYYYMMDD.json`

#### 4. 融資融券
- **資料項目**:
  - 融資餘額、融資增減
  - 融券餘額、融券增減
  - 資券相抵張數

- **儲存路徑**: `data/raw/margin/margin_trading/YYYY/MM/YYYYMMDD.json`

#### 5. 借券資料
- **資料項目**:
  - 借券賣出餘額
  - 借券賣出增減

- **儲存路徑**: `data/raw/margin/securities_lending/YYYY/MM/YYYYMMDD.json`

#### 6. 外資持股比例
- **資料項目**:
  - 外資持股張數
  - 外資持股比例
  - 外資可投資比例

- **儲存路徑**: `data/raw/institutional/foreign_holding/YYYY/MM/YYYYMMDD.json`

#### 7. 股權分散表 (每週)
- **資料項目**:
  - 各級距持股人數與張數分布
  - 董監持股、外資持股統計

- **儲存路徑**: `data/raw/ownership/shareholding/YYYY/MM/YYYY-Www.json`

#### 8. 董監持股 (每週)
- **資料項目**:
  - 董監事持股張數
  - 質押張數與比例

- **儲存路徑**: `data/raw/ownership/directors/YYYY/MM/YYYY-Www.json`

### 基礎資料

#### 9. 股票清單 (每月更新)
- **資料項目**:
  - 股票代號、名稱
  - 產業別、市場別 (上市/上櫃)
  - 上市日期

- **儲存路徑**: `data/raw/metadata/stock_list/YYYY/MM/YYYY-MM.json`

#### 10. 交易日曆 (每年)
- **資料項目**:
  - 交易日列表
  - 休市日資訊

- **儲存路徑**: `data/raw/metadata/trading_calendar/YYYY.json`

---

## 🔒 資料品質控制

### 驗證機制

#### 1. 格式驗證
- 檢查必要欄位是否存在
- 驗證資料型別正確性
- 確認日期格式一致

#### 2. 完整性檢查
- 比對預期資料筆數
- 檢查是否有缺失的股票代號
- 驗證數值範圍合理性

#### 3. 一致性驗證
- 交叉比對不同來源的相同資料
- 檢查時間序列連續性
- 驗證累計值的正確性

### 錯誤處理

#### 失敗重試策略
- 初次失敗: 等待 30 秒後重試
- 二次失敗: 等待 60 秒後重試
- 三次失敗: 記錄錯誤並發送通知

#### 部分失敗處理
- 單一股票資料失敗: 記錄並繼續
- 整批資料失敗: 中止並通知
- API 限流: 延遲後重試

---

## 📊 執行日誌

### 日誌格式

#### 收集日誌結構
```json
{
  "execution_id": "uuid",
  "collection_date": "2025-01-28",
  "execution_time": "2025-01-28T18:00:00+08:00",
  "data_types": ["price", "institutional", "margin"],
  "status": "success",
  "results": {
    "price": {
      "status": "success",
      "records": 1850,
      "duration": "45s"
    },
    "institutional": {
      "status": "success",
      "records": 1850,
      "duration": "32s"
    }
  },
  "errors": [],
  "commit_hash": "abc123..."
}
```

#### 日誌儲存路徑
`data/logs/collection/YYYY/MM/YYYYMMDD-HHMMSS.json`

---

## 🚀 實作檢查清單

### Phase 1.1: 環境建置
- [ ] 設定 GitHub 倉庫
- [ ] 建立目錄結構
- [ ] 設定 Git LFS (如需要)
- [ ] 配置 GitHub Actions Secrets

### Phase 1.2: 基礎收集器
- [ ] 實作交易日判斷函數
- [ ] 實作 FinMind API 基礎類別
- [ ] 實作檔案儲存工具
- [ ] 實作日期處理工具

### Phase 1.3: 資料收集器
- [ ] 實作每日價量收集器
- [ ] 實作三大法人收集器
- [ ] 實作融資融券收集器
- [ ] 實作其他籌碼資料收集器

### Phase 1.4: GitHub Actions
- [ ] 建立每日收集工作流程
- [ ] 建立每週收集工作流程
- [ ] 建立歷史回補工作流程
- [ ] 測試自動化流程

### Phase 1.5: 資料驗證
- [ ] 實作資料格式驗證
- [ ] 實作完整性檢查
- [ ] 實作錯誤處理機制
- [ ] 建立日誌記錄系統

### Phase 1.6: 測試與上線
- [ ] 手動執行測試
- [ ] 回補近期歷史資料
- [ ] 驗證自動化排程
- [ ] 監控運行狀況

---

## 💡 最佳實踐

### Git 提交策略

#### 提交訊息格式
```
data: collect {data_type} for {date}

- Records: {count}
- Source: FinMind
- Duration: {duration}
```

範例:
```
data: collect daily price for 2025-01-28

- Records: 1850
- Source: FinMind
- Duration: 45s
```

### 儲存空間管理

#### 預估空間需求
- 每日價量資料: ~2MB/日
- 法人籌碼資料: ~1MB/日
- 預估月增長: ~60MB
- 預估年增長: ~720MB

#### 優化策略
1. 使用壓縮格式 (JSON.gz, CSV.gz)
2. 定期歸檔舊資料
3. 使用 Git LFS 處理大檔案
4. 考慮設定保留政策 (如保留最近 2 年)

---

## 🔧 技術需求

### Python 套件
- `FinMind`: FinMind API 客戶端
- `pandas`: 資料處理
- `requests`: HTTP 請求
- `python-dotenv`: 環境變數管理

### GitHub Actions
- Ubuntu latest runner
- Python 3.11+
- Git 配置

### 環境變數
- `FINMIND_API_TOKEN`: FinMind API Token (可選)
- `GIT_USER_NAME`: Git 提交者名稱
- `GIT_USER_EMAIL`: Git 提交者 Email

---

## 📅 預計時程

| 任務 | 預估時間 |
|------|---------|
| 環境建置 | 2h |
| 基礎工具開發 | 4h |
| 收集器開發 | 8h |
| GitHub Actions 設定 | 3h |
| 測試與調整 | 4h |
| **總計** | **21h** |

---

## ✅ 完成標準

Phase 1 完成後應達成:

1. **自動化運行**: GitHub Actions 每日自動執行
2. **資料完整**: 涵蓋所有規劃的資料類型
3. **穩定性**: 連續 7 天無失敗記錄
4. **可追溯**: 所有資料變更有 Git 歷史
5. **文檔完善**: 執行日誌與錯誤記錄清晰

---

**維護者**: Jason Huang
**版本**: 1.0
**最後更新**: 2025-12-28
