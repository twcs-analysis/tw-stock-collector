# TAIFEX 個股期貨 API 研究報告

**研究日期**: 2026-03-15
**研究目標**: 找出台灣期貨交易所（TAIFEX）個股期貨每日交易資料的取得方式

---

## 一、主要發現

### ✅ TAIFEX 提供完整的免費 OpenAPI

- **OpenAPI 平台**: https://openapi.taifex.com.tw/
- **Swagger 文件**: https://openapi.taifex.com.tw/swagger.json
- **基礎 URL**: https://openapi.taifex.com.tw/v1
- **認證需求**: ❌ 無需認證或 API Key（完全免費公開）
- **資料格式**: JSON（預設）、CSV（透過 Accept header）

---

## 二、核心 API 端點

### 1. 每日期貨交易行情（包含個股期貨）

**端點**: `/DailyMarketReportFut`
**完整 URL**: https://openapi.taifex.com.tw/v1/DailyMarketReportFut
**用途**: 取得所有期貨商品的每日交易資料，包含個股期貨

**資料特性**:
- 預設回傳最新交易日資料
- 支援日期參數（格式：`?date=YYYY-MM-DD`）
- 回傳 JSON 陣列，包含所有期貨商品
- 個股期貨的 Contract 代碼開頭為 `C`（例如：CDF=台積電、CAF=南亞）

**資料欄位**:
```json
{
  "Date": "20260313",              // 交易日期（YYYYMMDD）
  "Contract": "CDF",                // 期貨代碼
  "ContractMonth(Week)": "202603",  // 契約月份
  "Open": "1050",                   // 開盤價
  "High": "1065",                   // 最高價
  "Low": "1048",                    // 最低價
  "Last": "1060",                   // 收盤價
  "Change": "+5",                   // 漲跌
  "%": "+0.47%",                    // 漲跌幅
  "Volume": "15000",                // 成交量
  "SettlementPrice": "1058",        // 結算價
  "OpenInterest": "25000",          // 未平倉量
  "BestBid": "1059",                // 最佳買價
  "BestAsk": "1061",                // 最佳賣價
  "HistoricalHigh": "1200",         // 歷史最高價
  "HistoricalLow": "900",           // 歷史最低價
  "TradingHalt": "",                // 是否暫停交易
  "TradingSession": "一般",         // 交易時段（一般/盤後）
  "Volume(ExecutionsAmongSpreadOrderAndSingleOrderOnly)": ""
}
```

**實測結果**（2026-03-13）:
- 總筆數: 2,253 筆（包含所有期貨商品）
- 個股期貨: 154 筆
- 包含一般交易時段和盤後交易時段資料

### 2. 個股期貨交易標的清單

**端點**: `/SSFLists`
**完整 URL**: https://openapi.taifex.com.tw/v1/SSFLists
**用途**: 取得所有個股期貨標的資訊（股票代碼對應關係）

**資料欄位**:
```json
{
  "Contract": "CDF",                              // 期貨代碼
  "UnderlyingStock": "台灣積體電路製造股份有限公司", // 標的股票全名
  "StockCode": "2330",                            // 股票代碼
  "StockName": "台積電",                          // 股票簡稱
  "Type": "上市普通股標的證券"                     // 標的類型
}
```

**實測結果**:
- 總標的數: 314 檔個股期貨
- 包含上市普通股和 ETF 標的

### 3. 每日個股期貨交易量統計

**端點**: `/va12`
**完整 URL**: https://openapi.taifex.com.tw/v1/va12
**用途**: 每日個股期貨交易量統計（區分股票與 ETF）

**資料欄位**:
```json
{
  "Date": "20260313",         // 日期
  "ContractType": "STF",      // 類型（STF=股票期貨, ETF=ETF期貨）
  "Volume": "725861"          // 總成交量
}
```

**實測結果**（2026-03-13）:
- 股票期貨 (STF): 725,861 口
- ETF 期貨 (ETF): 26,242 口

---

## 三、其他相關 API 端點

### 個股期貨相關
- `/SSFAdjustedInfo` - 股票期貨調整型契約資訊
- `/SSFRefferedOpeningPrice` - 股票期貨調整開盤參考價
- `/FinalSettlementPriceSSF` - 最後結算價（股票期貨）
- `/SettledPositionsSSF` - 到期契約履約交割
- `/SingleStockFuturesMargining` - 保證金一覽表
- `/STFTop10` - 每日股票期貨交易量前十大統計表

### 月度/年度統計
- `/va13` - 每月個股期貨交易量統計表
- `/va14` - 每年個股期貨交易量統計表

---

## 四、資料格式與參數

### 支援的資料格式

1. **JSON**（預設）:
   ```bash
   curl "https://openapi.taifex.com.tw/v1/DailyMarketReportFut"
   ```

2. **CSV**（透過 Accept header）:
   ```bash
   curl -H "Accept: text/csv" "https://openapi.taifex.com.tw/v1/DailyMarketReportFut"
   ```

### 日期參數

- **格式**: `?date=YYYY-MM-DD`
- **範例**: `https://openapi.taifex.com.tw/v1/DailyMarketReportFut?date=2026-03-13`
- **注意**: 不加日期參數會回傳最新交易日資料

---

## 五、使用範例

### 範例 1: 取得今日所有個股期貨資料

```python
import requests

url = "https://openapi.taifex.com.tw/v1/DailyMarketReportFut"
response = requests.get(url)
data = response.json()

# 過濾出個股期貨（Contract 開頭為 C）
stock_futures = [item for item in data if item['Contract'].startswith('C')]

print(f"今日個股期貨筆數: {len(stock_futures)}")
```

### 範例 2: 取得指定日期的台積電期貨資料

```python
import requests

url = "https://openapi.taifex.com.tw/v1/DailyMarketReportFut?date=2026-03-13"
response = requests.get(url)
data = response.json()

# 找出台積電期貨（CDF）的所有契約月份
tsmc_futures = [item for item in data if item['Contract'] == 'CDF']

for contract in tsmc_futures:
    print(f"契約月份: {contract['ContractMonth(Week)']}, 收盤價: {contract['Last']}")
```

### 範例 3: 取得個股期貨標的對應表

```python
import requests

url = "https://openapi.taifex.com.tw/v1/SSFLists"
response = requests.get(url)
stock_list = response.json()

# 建立期貨代碼 -> 股票代碼的對應字典
contract_to_stock = {
    item['Contract']: {
        'stock_code': item['StockCode'],
        'stock_name': item['StockName']
    }
    for item in stock_list
}

print(f"CDF 對應股票: {contract_to_stock['CDF']}")
# 輸出: {'stock_code': '2330', 'stock_name': '台積電'}
```

---

## 六、與證交所 API 的比較

| 項目 | TWSE (證交所) | TAIFEX (期交所) |
|------|---------------|-----------------|
| **API 類型** | OpenAPI | OpenAPI |
| **認證需求** | ❌ 無需 | ❌ 無需 |
| **資料格式** | JSON, CSV | JSON, CSV |
| **更新頻率** | 每日（交易日結束後） | 每日（交易日結束後） |
| **歷史資料** | 支援日期參數 | 支援日期參數 |
| **一次取得所有股票** | ✅ STOCK_DAY_ALL | ✅ DailyMarketReportFut |
| **資料完整度** | 上市+上櫃 | 期貨（多個契約月份） |

---

## 七、個股期貨代碼對應表（範例）

| 期貨代碼 | 股票代碼 | 股票名稱 |
|---------|---------|---------|
| CAF | 1303 | 南亞 |
| CBF | 2002 | 中鋼 |
| CCF | 2303 | 聯電 |
| CDF | 2330 | 台積電 |
| CEF | 2881 | 富邦金 |
| CFF | 1301 | 台塑 |
| CGF | 2324 | 仁寶 |
| CHF | 2409 | 友達 |
| CJF | 2880 | 華南金 |
| CKF | 2882 | 國泰金 |
| CLF | 2886 | 兆豐金 |

完整清單請使用 `/SSFLists` API 查詢（共 314 檔）。

---

## 八、注意事項與限制

### 資料特性
1. **多個契約月份**: 每檔個股期貨會有多個契約月份（近月、次月、季月等）
2. **盤後交易**: 資料包含一般交易時段和盤後交易時段
3. **成交量為 0**: 某些契約月份可能無交易量（Open/High/Low/Last 顯示為 "-"）

### 資料處理建議
1. 根據 `TradingSession` 欄位區分一般交易與盤後交易
2. 根據 `ContractMonth(Week)` 欄位識別契約月份
3. 注意處理 "-" 和 "NULL" 值

### 與現貨市場的差異
- 期貨價格可能與現貨有價差（基差）
- 期貨有到期日，需注意轉倉
- 期貨交易量單位為「口」，現貨為「股」

---

## 九、建議的資料收集策略

### 方案 A: 收集所有期貨資料（推薦）

**優點**:
- 一次 API 呼叫取得所有資料
- 包含指數期貨、商品期貨等完整資料
- 與現有架構一致（類似 STOCK_DAY_ALL）

**流程**:
1. 呼叫 `/DailyMarketReportFut` 取得所有期貨資料
2. 過濾出個股期貨（Contract 開頭為 C）
3. 儲存為 `data/raw/stock_futures/YYYY/MM/YYYY-MM-DD.json`

### 方案 B: 僅收集個股期貨

**優點**:
- 資料量較小
- 專注於個股期貨

**缺點**:
- 需要額外過濾邏輯
- 未來若需要其他期貨資料需重新收集

### 建議採用方案 A

---

## 十、整合到現有系統

### 新增的資料類型
```python
# 在 src/collectors/ 新增
class StockFuturesCollector(BaseCollector):
    """個股期貨資料收集器"""

    def collect(self, date: str) -> Dict:
        # 呼叫 TAIFEX DailyMarketReportFut API
        pass
```

### 資料結構範例
```json
{
  "metadata": {
    "date": "2026-03-13",
    "type": "stock_futures",
    "source": "TAIFEX",
    "api": "DailyMarketReportFut",
    "collected_at": "2026-03-13T22:00:00+08:00",
    "total_contracts": 154,
    "total_underlyings": 314
  },
  "data": [
    {
      "date": "20260313",
      "contract": "CDF",
      "stock_code": "2330",
      "stock_name": "台積電",
      "contract_month": "202603",
      "open": "1050",
      "high": "1065",
      "low": "1048",
      "close": "1060",
      "change": "+5",
      "change_percent": "+0.47%",
      "volume": "15000",
      "settlement_price": "1058",
      "open_interest": "25000",
      "best_bid": "1059",
      "best_ask": "1061",
      "trading_session": "一般"
    }
  ]
}
```

---

## 十一、參考資源

### 官方文件
- [TAIFEX 官網](https://www.taifex.com.tw)
- [TAIFEX OpenAPI](https://openapi.taifex.com.tw/)
- [資料下載專區](https://www.taifex.com.tw/cht/3/dlFutDailyMarketView)

### 相關連結
- [行情資訊網站](https://mis.taifex.com.tw/futures/)
- [期交所統計資料](https://www.taifex.com.tw/cht/7/annualTrading)

---

## 十二、結論

✅ **TAIFEX 提供完整且免費的 OpenAPI**，可滿足個股期貨每日交易資料收集需求：

1. **API 端點**: `/DailyMarketReportFut` 提供所有期貨商品的每日行情
2. **資料格式**: JSON/CSV 雙格式支援
3. **認證需求**: 無需認證或 API Key
4. **資料完整性**: 包含開高低收、成交量、未平倉等完整資訊
5. **契約對應**: `/SSFLists` 提供期貨代碼與股票代碼的對應關係

**與證交所 API 類似**，TAIFEX OpenAPI 的設計理念一致，可直接整合到現有的資料收集系統中。

---

**研究者**: Claude Sonnet 4.5
**最後更新**: 2026-03-15
