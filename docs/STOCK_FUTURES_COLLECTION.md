# 個股期貨資料收集指南

## 📊 概述

本系統提供完整的**個股期貨（Stock Futures）**每日交易資料收集功能，使用台灣期貨交易所（TAIFEX）的免費 OpenAPI。

---

## 🎯 資料內容

### 資料來源
- **來源**: 台灣期貨交易所 (TAIFEX)
- **API**: https://openapi.taifex.com.tw/v1/DailyMarketReportFut
- **認證**: ❌ 無需 API Key（完全免費）
- **格式**: JSON

### 資料涵蓋範圍
- **個股期貨契約**: 154 筆（2026-03-13 實測）
- **標的股票**: 314 檔（包含上市股票和 ETF）
- **契約月份**: 近月、次月、季月等多個月份
- **交易時段**: 一般交易時段 + 盤後交易

### 資料欄位

```json
{
  "date": "2026-03-13",           // 交易日期
  "contract": "CDF",               // 期貨代碼（CDF=台積電）
  "stock_id": "2330",              // 股票代碼
  "stock_name": "台積電",          // 股票名稱
  "contract_month": "202603",      // 契約月份
  "open": 1050.0,                  // 開盤價
  "high": 1065.0,                  // 最高價
  "low": 1048.0,                   // 最低價
  "close": 1060.0,                 // 收盤價
  "change": "+5",                  // 漲跌
  "change_percent": "+0.47%",      // 漲跌幅
  "volume": 15000,                 // 成交量（口）
  "settlement_price": 1058.0,      // 結算價
  "open_interest": 25000,          // 未平倉量
  "best_bid": 1059.0,              // 最佳買價
  "best_ask": 1061.0,              // 最佳賣價
  "trading_session": "一般",       // 交易時段
  "type": "taifex"                 // 資料類型
}
```

---

## 🚀 使用方式

### 方法 1: 使用 Shell 腳本（推薦）

```bash
# 收集今天的資料
./scripts/data-collector/collect_stock_futures.sh

# 收集指定日期的資料
./scripts/data-collector/collect_stock_futures.sh 2026-03-13

# 收集資料但不執行驗證
./scripts/data-collector/collect_stock_futures.sh 2026-03-13 --no-validation
```

### 方法 2: 使用 Python 腳本

```bash
# 收集今天的資料
python3.11 scripts/data-collector/collect_stock_futures.py

# 收集指定日期的資料
python3.11 scripts/data-collector/collect_stock_futures.py --date 2026-03-13

# 不執行驗證
python3.11 scripts/data-collector/collect_stock_futures.py --date 2026-03-13 --no-validation
```

### 方法 3: 在程式中使用

```python
from services.common.collectors import StockFuturesCollector

# 建立收集器
collector = StockFuturesCollector(date='2026-03-13')

# 執行收集
result = collector.run(enable_validation=True)

if result['status'] == 'success':
    print(f"✅ 成功收集 {result['records']} 筆資料")
    print(f"檔案: {result['file']}")
```

---

## 📁 資料儲存位置

### 目錄結構

```
data/raw/stock_futures/
├── 2026/
│   ├── 03/
│   │   ├── 2026-03-13.json
│   │   ├── 2026-03-14.json
│   │   └── ...
│   └── ...
└── ...
```

### 檔案格式

```json
{
  "metadata": {
    "date": "2026-03-13",
    "total_count": 154,
    "unique_stocks": 21,
    "total_contracts": 314,
    "source": "TAIFEX OpenAPI",
    "api": "DailyMarketReportFut"
  },
  "data": [
    {
      "date": "2026-03-13",
      "contract": "CDF",
      "stock_id": "2330",
      "stock_name": "台積電",
      ...
    }
  ]
}
```

---

## 🔍 期貨代碼對應表

### 常見個股期貨

| 期貨代碼 | 股票代碼 | 股票名稱 | 類型 |
|---------|---------|---------|------|
| CDF | 2330 | 台積電 | 上市 |
| CAF | 1303 | 南亞 | 上市 |
| CBF | 2002 | 中鋼 | 上市 |
| CCF | 2303 | 聯電 | 上市 |
| CEF | 2881 | 富邦金 | 上市 |
| CFF | 1301 | 台塑 | 上市 |
| CKF | 2882 | 國泰金 | 上市 |
| CLF | 2886 | 兆豐金 | 上市 |

### 取得完整對應表

使用 TAIFEXDataSource 取得所有標的：

```python
from services.common.datasources import TAIFEXDataSource

datasource = TAIFEXDataSource()
contracts = datasource.get_all_contracts()

for contract in contracts[:10]:
    print(f"{contract['contract']}: {contract['stock_code']} {contract['stock_name']}")
```

---

## 📊 與現貨市場的差異

### 重要差異

1. **契約月份**: 每檔股票有多個契約月份（近月、次月、季月等）
2. **成交量單位**: 期貨為「口」，現貨為「股」
3. **價格差異**: 期貨價格與現貨可能有價差（基差）
4. **到期日**: 期貨有到期日，需注意轉倉
5. **交易時段**: 包含一般交易和盤後交易

### 資料處理建議

- 使用 `contract_month` 欄位區分不同契約月份
- 使用 `trading_session` 欄位區分一般交易與盤後交易
- 注意處理 `NaN` 值（無成交量的契約）
- 結合現貨價格分析基差

---

## 🔧 進階使用

### 篩選特定股票的期貨

```python
from services.common.datasources import TAIFEXDataSource

datasource = TAIFEXDataSource()

# 只取得台積電和聯電的期貨
df = datasource.get_daily_prices(
    date='2026-03-13',
    stock_ids=['2330', '2303']
)

print(f"共 {len(df)} 筆契約")
```

### 查詢期貨代碼資訊

```python
from services.common.datasources import TAIFEXDataSource

datasource = TAIFEXDataSource()

# 查詢 CDF 對應的股票資訊
info = datasource.get_contract_info('CDF')
print(info)
# 輸出: {'stock_code': '2330', 'stock_name': '台積電'}
```

### 分析近月契約

```python
import pandas as pd

# 讀取資料
with open('data/raw/stock_futures/2026/03/2026-03-13.json') as f:
    data = json.load(f)

df = pd.DataFrame(data['data'])

# 篩選近月契約（202603）
near_month = df[df['contract_month'] == '202603']
print(f"近月契約共 {len(near_month)} 筆")

# 篩選一般交易時段
regular_trading = df[df['trading_session'] == '一般']
print(f"一般交易時段共 {len(regular_trading)} 筆")
```

---

## 📈 自動化收集

### GitHub Actions

如需自動化收集，可參考現有的 `daily-collection.yml` 工作流程，新增個股期貨收集步驟：

```yaml
- name: Collect Stock Futures
  run: |
    python3 scripts/data-collector/collect_stock_futures.py --no-validation
```

### Cron 排程

```bash
# 每個交易日 21:30 執行
30 21 * * 1-5 cd /path/to/project && ./scripts/data-collector/collect_stock_futures.sh
```

---

## ⚠️ 注意事項

### 資料特性
1. **非交易日**: 假日或非交易日將回傳空資料
2. **資料延遲**: TAIFEX API 在盤後才會更新
3. **契約到期**: 每月第三個星期三為結算日

### 已知限制
1. 某些契約可能無成交量（顯示為 `NaN`）
2. 盤後交易資料包含在同一個檔案中
3. 歷史資料查詢受 API 限制

---

## 🔗 相關資源

### 官方文件
- [TAIFEX 官網](https://www.taifex.com.tw)
- [TAIFEX OpenAPI](https://openapi.taifex.com.tw/)
- [個股期貨交易規則](https://www.taifex.com.tw/cht/2/stockLists)

### 系統文件
- [TAIFEX API 研究報告](research/TAIFEX_API_RESEARCH.md)
- [資料收集架構](../CLAUDE.md)
- [現貨資料收集](../README.md)

---

## 📞 問題回報

如有問題或建議，請在 GitHub Issues 中回報。

---

**建立日期**: 2026-03-15
**維護者**: Claude Sonnet 4.5
**版本**: 1.0.0
