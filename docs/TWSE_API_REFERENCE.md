# 台灣證交所 OpenAPI v1 參考文件

## 📚 官方文件

- **官方 Swagger JSON**: https://openapi.twse.com.tw/v1/swagger.json
- **Base URL**: `https://openapi.twse.com.tw/v1`
- **API 版本**: 1.0
- **使用條款**: https://www.twse.com.tw/zh/page/terms/use.html

---

## 🎯 本專案使用的 API

### 1. 價格資料 (Price Data)

#### `/exchangeReport/STOCK_DAY_ALL`
- **說明**: 上市個股日成交資訊
- **完整 URL**: https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL
- **方法**: GET
- **回傳格式**: JSON
- **更新時間**: 每日盤後
- **本專案使用**: ✅ 已在 `PriceCollector` 中使用

**回傳欄位**:
- `Code`: 股票代號
- `Name`: 股票名稱
- `OpeningPrice`: 開盤價
- `HighestPrice`: 最高價
- `LowestPrice`: 最低價
- `ClosingPrice`: 收盤價
- `TradeVolume`: 成交量
- `TradeValue`: 成交金額
- `Transaction`: 成交筆數
- `Change`: 漲跌價差

**範例**:
```bash
curl "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
```

---

### 2. 融資融券 (Margin Trading)

#### `/exchangeReport/MI_MARGN`
- **說明**: 信用交易統計
- **完整 URL**: https://openapi.twse.com.tw/v1/exchangeReport/MI_MARGN
- **方法**: GET
- **回傳格式**: JSON
- **本專案使用**: ⏳ 規劃中（目前使用舊版 API）

---

### 3. 借券賣出 (Securities Lending)

#### `/exchangeReport/TWT93U`
- **說明**: 借券賣出餘額
- **完整 URL**: https://openapi.twse.com.tw/v1/exchangeReport/TWT93U
- **方法**: GET
- **回傳格式**: JSON
- **本專案使用**: ✅ 可用（目前使用舊版 `/TWT93U?response=json&date=YYYYMMDD`）

---

## 📊 其他常用 API 端點

### 市場統計

| 端點 | 說明 | 完整 URL |
|------|------|----------|
| `/exchangeReport/MI_INDEX` | 每日收盤行情-大盤統計 | https://openapi.twse.com.tw/v1/exchangeReport/MI_INDEX |
| `/exchangeReport/FMTQIK` | 每日市場成交資訊 | https://openapi.twse.com.tw/v1/exchangeReport/FMTQIK |
| `/exchangeReport/MI_INDEX20` | 成交量前20名 | https://openapi.twse.com.tw/v1/exchangeReport/MI_INDEX20 |

### 技術分析

| 端點 | 說明 | 完整 URL |
|------|------|----------|
| `/exchangeReport/BWIBBU_ALL` | 本益比、殖利率、股價淨值比 | https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL |
| `/exchangeReport/STOCK_DAY_AVG_ALL` | 日收盤價及月平均價 | https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_AVG_ALL |

### 月/年資料

| 端點 | 說明 | 完整 URL |
|------|------|----------|
| `/exchangeReport/FMSRFK_ALL` | 個股月成交資訊 | https://openapi.twse.com.tw/v1/exchangeReport/FMSRFK_ALL |
| `/exchangeReport/FMNPTK_ALL` | 個股年成交資訊 | https://openapi.twse.com.tw/v1/exchangeReport/FMNPTK_ALL |

### 當沖資料

| 端點 | 說明 | 完整 URL |
|------|------|----------|
| `/exchangeReport/TWTB4U` | 每日當沖交易標的及統計 | https://openapi.twse.com.tw/v1/exchangeReport/TWTB4U |

---

## 📋 完整 API 分類

根據官方 Swagger 文件，TWSE OpenAPI 提供以下分類：

- **公司治理**: 56 個 API
  - ESG 資訊揭露
  - 股利分派
  - 董監持股
  - 內部人交易

- **證券交易**: 36 個 API
  - 每日價量資料
  - 市場統計
  - 當沖資訊
  - 融資融券

- **財務報表**: 30 個 API
  - 月營收
  - 季報、年報
  - 財務比率

- **指數**: 5 個 API
  - 加權指數
  - 類股指數

- **權證**: 3 個 API

- **其他**: 4 個 API

- **券商資料**: 9 個 API

**總計**: **143 個 API 端點**

---

## 🔧 使用方式

### Python 範例

```python
import requests

# 1. 取得每日價量資料
url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
response = requests.get(url, verify=False)
data = response.json()

# 2. 取得大盤統計
url = "https://openapi.twse.com.tw/v1/exchangeReport/MI_INDEX"
response = requests.get(url, verify=False)
market_data = response.json()
```

### curl 範例

```bash
# 取得每日價量資料
curl "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"

# 取得融資融券資料
curl "https://openapi.twse.com.tw/v1/exchangeReport/MI_MARGN"
```

---

## ⚠️ 注意事項

1. **無需認證**: TWSE OpenAPI 不需要 API Token，可直接使用
2. **SSL 憑證**: 某些環境可能需要 `verify=False` 繞過憑證驗證
3. **更新時間**: 大部分資料在**每日盤後 15:00-17:00** 更新
4. **回傳格式**: 統一為 JSON 格式
5. **速率限制**: 官方未明確說明，建議合理使用
6. **日期格式**: 不需要傳入日期參數，API 自動回傳最新資料

---

## 🔄 舊版 API vs 新版 OpenAPI

### 舊版 API (仍在使用)

**Base URL**: `https://www.twse.com.tw`

需要加上 `response=csv` 或 `response=json` 參數：

```python
# 三大法人 (舊版 - 本專案目前使用)
url = f"https://www.twse.com.tw/fund/T86?response=csv&date={date}&selectType=ALLBUT0999"

# 借券賣出 (舊版)
url = f"https://www.twse.com.tw/exchangeReport/TWT93U?response=json&date={date}"
```

### 新版 OpenAPI (推薦)

**Base URL**: `https://openapi.twse.com.tw/v1`

直接 GET 即可，自動回傳 JSON：

```python
# 價量資料 (新版 - 本專案已使用)
url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"

# 融資融券 (新版 - 可遷移)
url = "https://openapi.twse.com.tw/v1/exchangeReport/MI_MARGN"
```

**優點**:
- ✅ RESTful 設計
- ✅ 統一 JSON 格式
- ✅ 不需要日期參數
- ✅ 更穩定可靠

---

## 📖 相關文件

- [TWSE 官方 OpenAPI](https://openapi.twse.com.tw/)
- [本專案 API 研究結果](API_RESEARCH_RESULTS.md)
- [資料收集規格](specifications/TWSE_DATA_COLLECTION_SPEC.md)

---

**最後更新**: 2026-01-27
**維護者**: tw-stock-collector 專案團隊
