# 台灣證交所 OpenAPI v1 參考文件

## 📚 官方文件

### 主要入口

- **🌐 官方 Swagger UI**: https://openapi.twse.com.tw/
  - 互動式 API 文檔
  - 可直接測試 API 請求
  - 包含完整的 endpoints 說明與範例
  - 145 個可用 API endpoints

- **📄 Swagger JSON 規格**: https://openapi.twse.com.tw/v1/swagger.json
  - 機器可讀的 API 規格
  - 包含所有 endpoints 定義
  - 可用於自動生成客戶端程式碼

- **🔗 Base URL**: `https://openapi.twse.com.tw/v1`
- **📋 API 版本**: 1.0
- **⚖️ 使用條款**: https://www.twse.com.tw/zh/page/terms/use.html

### API 分類概覽

根據官方文檔，OpenAPI 提供以下類別：

| 分類 | 說明 | 範例 endpoints |
|------|------|---------------|
| **證券交易** | 每日價量、市場統計 | STOCK_DAY_ALL, MI_INDEX, MI_MARGN |
| **公司治理** | ESG 資訊、股利分派、董監持股 | ~56 個 endpoints |
| **財務報表** | 月營收、季報、年報 | t187ap05_L (月營收彙總) |
| **指數資訊** | 加權指數、類股指數 | FRMSA, TAI50I |
| **法人資訊** | 外資持股、三大法人 | MI_QFIIS_cat, MI_QFIIS_sort_20 |
| **其他資訊** | 公告事項、新聞、休市日曆 | eventList, newsList, holidaySchedule |

**總計**: 145 個 API endpoints

---

## 🎯 本專案使用的 API

### 0. 月營收資料 (Monthly Revenue) 🆕

#### `/opendata/t187ap05_L`
- **說明**: 上市公司每月營業收入彙總表
- **完整 URL**: https://openapi.twse.com.tw/v1/opendata/t187ap05_L
- **方法**: GET
- **回傳格式**: JSON / CSV
- **分類**: 財務報表
- **本專案使用**: ⏳ 規劃中（搭配 MOPS API 使用）

**回傳欄位**:
- `出表日期`: 資料公告日期（民國年格式，如 1150117）
- `資料年月`: 營收年月（民國年格式，如 11412）
- `公司代號`: 股票代號
- `公司名稱`: 公司名稱
- `產業別`: 產業分類
- `營業收入-當月營收`: 當月營業收入（千元）
- `營業收入-上月營收`: 上月營業收入（千元）
- `營業收入-去年當月營收`: 去年同月營業收入（千元）
- `營業收入-上月比較增減(%)`: 月增率
- `營業收入-去年同月增減(%)`: 年增率
- `累計營業收入-當月累計營收`: 年初至今累計營收（千元）
- `累計營業收入-去年累計營收`: 去年同期累計營收（千元）
- `累計營業收入-前期比較增減(%)`: 累計年增率
- `備註`: 營收變動說明

**範例**:
```bash
# 取得所有上市公司最新月營收
curl "https://openapi.twse.com.tw/v1/opendata/t187ap05_L"
```

**重要說明**:
- ⚠️ 此 API **僅提供最新一期**月營收資料
- ⚠️ 無法指定歷史年月查詢
- ⚠️ 資料更新有 1-2 天延遲（每月 10 號公司公告，11 號後 API 更新）
- ✅ 一次請求即可取得所有上市公司資料（~1,000 檔）
- 💡 搭配使用 MOPS API 可查詢歷史資料與即時資料

#### `/opendata/t187ap05_P`
- **說明**: 公開發行公司每月營業收入彙總表（包含上市上櫃）
- **完整 URL**: https://openapi.twse.com.tw/v1/opendata/t187ap05_P
- **方法**: GET
- **回傳格式**: JSON / CSV
- **分類**: 公司治理
- **本專案使用**: ⏳ 規劃中

**說明**:
- 包含所有公開發行公司（上市 + 上櫃 + 興櫃）
- 資料欄位與 `t187ap05_L` 相同
- 筆數更多（~2,000 檔）

---

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
