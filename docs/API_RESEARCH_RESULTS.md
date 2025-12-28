# TWSE/TPEx 官方 API 研究結果

**日期**: 2025-12-28
**研究者**: Jason Huang
**目的**: 尋找可用的官方 API 替代 FinMind，以獲取即時資料

---

## 📊 研究總結

### ✅ 成功找到的 API

| 資料類型 | 交易所 | 端點 | 狀態 | 筆數 | 備註 |
|---------|-------|------|------|------|------|
| **價格資料** | TWSE | `/exchangeReport/STOCK_DAY_ALL` | ✅ | 1,075 | 即時資料 |
| **價格資料** | TPEx | `/openapi/v1/tpex_mainboard_quotes` | ✅ | 871 | 即時資料 |
| **融資融券** | TWSE | `/exchangeReport/MI_MARGN` | ✅ | 1,044 | 即時資料 |
| **融資融券** | TPEx | `/web/stock/margin_trading/margin_balance/margin_bal_result.php` | ✅ | 771 | 即時資料 |
| **三大法人** | TWSE | `/fund/T86?response=csv` | ✅ | 1,027 | 即時資料，使用 voidful 方法 |
| **三大法人** | TPEx | `/web/stock/3insti/daily_trade/3itrade_hedge_result.php` | ✅ | 836 | 即時資料 |
| **借券賣出** | TWSE | `/exchangeReport/TWT93U?response=json` | ✅ | 1,185 | 即時資料，**包含上市+上櫃** |

---

## 🔬 詳細研究過程

### 1. 價格資料（Price） - ✅ 成功

#### TWSE 價格 API
- **端點**: `https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL`
- **方法**: GET
- **回傳格式**: JSON Array
- **筆數**: 1,075 檔上市股票
- **欄位**:
  ```json
  {
    "Code": "0050",
    "Name": "元大台灣50",
    "TradeVolume": "9234567",
    "TradeValue": "1234567890",
    "OpeningPrice": "150.50",
    "HighestPrice": "152.00",
    "LowestPrice": "150.00",
    "ClosingPrice": "151.50",
    "Change": "+1.00",
    ...
  }
  ```

#### TPEx 價格 API
- **端點**: `https://www.tpex.org.tw/openapi/v1/tpex_mainboard_quotes`
- **方法**: GET
- **回傳格式**: JSON Array
- **筆數**: 871 檔上櫃股票
- **特點**: RESTful API 風格

**效能提升**: **973 倍**（1,946 請求 → 2 請求）

---

### 2. 融資融券（Margin） - ✅ 成功

#### TWSE 融資融券 API
- **端點**: `https://openapi.twse.com.tw/v1/exchangeReport/MI_MARGN`
- **方法**: GET
- **回傳格式**: JSON Array
- **筆數**: 1,044 檔
- **欄位對照**:
  ```python
  {
      '股票代號': 'stock_id',
      '股票名稱': 'stock_name',
      '融資買進': 'margin_buy',
      '融資賣出': 'margin_sell',
      '融資今日餘額': 'margin_balance',
      '融券買進': 'short_covering',
      '融券賣出': 'short_sell',
      '融券今日餘額': 'short_balance',
      ...
  }
  ```

#### TPEx 融資融券 API - 🎉 重大突破
- **端點**: `https://www.tpex.org.tw/web/stock/margin_trading/margin_balance/margin_bal_result.php`
- **方法**: GET
- **回傳格式**: JSON Object `{tables: [{fields: [], data: []}]}`
- **筆數**: 771 檔

**關鍵發現**:
1. TPEx 使用 `/web/stock/` PHP 端點，而非 `/openapi/v1/` RESTful API
2. 回傳格式為 `{tables: [{fields: [], data: []}]}`，與 TWSE 的 JSON Array 不同
3. 此模式適用於所有 TPEx 交易統計資料（非即時行情）

**效能提升**: **907.5 倍**（1,815 請求 → 2 請求）

---

### 3. 三大法人（Institutional） - ✅ 成功（感謝 voidful 專案）

#### TWSE 三大法人 API - 🎉 突破性發現
- **端點**: `https://www.twse.com.tw/fund/T86?response=csv&date={YYYYMMDD}&selectType=ALLBUT0999`
- **方法**: GET
- **回傳格式**: CSV（需解析）
- **編碼**: Big5 (cp950)
- **筆數**: 1,027 檔上市股票
- **參考來源**: [voidful/tw-institutional-stocker](https://github.com/voidful/tw-institutional-stocker)

**關鍵發現**:
1. 必須使用 `response=csv` 參數（而非 JSON）
2. 必須指定 `selectType=ALLBUT0999`（排除 0999 彙總資料）
3. CSV 包含前導說明行，需找到「證券代號」標題行後才開始解析
4. 使用 Big5 編碼

**解析方式**:
```python
response.encoding = 'cp950'  # Big5 編碼
lines = response.text.split('\n')

# 找到標題行
for i, line in enumerate(lines):
    if '證券代號' in line:
        start_idx = i
        break

# 從標題行開始解析 CSV
data_content = '\n'.join(lines[start_idx:])
df = pd.read_csv(StringIO(data_content))
```

#### TPEx 三大法人 API
- **端點**: `https://www.tpex.org.tw/web/stock/3insti/daily_trade/3itrade_hedge_result.php?d={YYY/MM/DD}&l=zh-tw&o=htm`
- **方法**: GET
- **回傳格式**: HTML Table（使用 pandas.read_html 解析）
- **筆數**: 836 檔上櫃股票
- **日期格式**: 民國曆 YYY/MM/DD

**解析注意事項**:
1. TPEx 使用 MultiIndex 欄位，需扁平化
2. 回應為 HTML 而非 JSON
3. 使用 `pd.read_html()` 解析表格

**效能提升**: **~930 倍**（假設原本需要逐檔查詢 1,863 檔 → 現在只需 2 次請求）

---

### 4. 借券賣出（Securities Lending） - ✅ 成功

#### TWSE 借券賣出 API - 🎉 重大發現
- **端點**: `https://www.twse.com.tw/exchangeReport/TWT93U?response=json&date={YYYYMMDD}`
- **方法**: GET
- **回傳格式**: JSON Object `{fields: [], data: []}`
- **筆數**: 1,185 檔
- **重要特性**: **包含上市+上櫃所有股票**

**欄位對照**:
```python
fields = [
    '代號',           # 股票代號
    '名稱',           # 股票名稱
    '前日餘額',       # 融券前日餘額
    '賣出',           # 融券賣出
    '買進',           # 融券買進
    '現券',           # 現券償還
    '今日餘額',       # 融券今日餘額
    '次一營業日限額', # 次一營業日融券限額
    '前日餘額',       # 借券前日餘額
    '當日賣出',       # 借券賣出
    '當日還券',       # 借券還券
    '當日調整',       # 借券調整
    '當日餘額',       # 借券當日餘額
    '次一營業日可限額', # 次一營業日可借券限額
    '備註'
]
```

**關鍵發現**:
1. 此 API **同時包含上市和上櫃股票**（透過股票代碼分析確認）
2. 包含 4xxx, 5xxx, 6xxx, 8xxx 開頭的上櫃股票
3. 一次 API 呼叫即可取得所有市場資料

#### TPEx 借券賣出 API - ✅ 可用但非必需
- **端點**: `https://www.tpex.org.tw/web/stock/margin_trading/margin_sbl/margin_sbl_result.php?l=zh-tw&d={YYY/MM/DD}`
- **方法**: GET
- **回傳格式**: JSON Object `{tables: [{fields: [], data: []}]}`
- **筆數**: 835 檔上櫃股票
- **日期格式**: 民國曆 YYY/MM/DD

**結論**:
- ✅ **建議使用 TWSE TWT93U**，因為已包含所有股票（上市+上櫃）
- TPEx API 僅提供上櫃股票，資料重複
- 單一 API 即可滿足需求，無需分別呼叫

**效能提升**: **~1,200 倍**（假設原本需要逐檔查詢 1,185 檔 → 現在只需 1 次請求）

---

## 💡 發現的 API 模式

### TWSE API 架構
- **基礎 URL**: `https://openapi.twse.com.tw/v1`
- **風格**: RESTful API
- **回傳格式**: JSON Array
- **特點**:
  - 簡潔的端點命名
  - 統一的資料格式
  - 完整的欄位名稱（中文）

### TPEx API 雙重架構

#### 1. 即時行情 API
- **路徑**: `/openapi/v1/*`
- **風格**: RESTful API
- **用途**: 價格行情資料
- **範例**: `/openapi/v1/tpex_mainboard_quotes`

#### 2. 交易統計 API
- **路徑**: `/web/stock/*`
- **風格**: 傳統 PHP 端點
- **回傳格式**: `{tables: [{fields: [], data: []}]}`
- **用途**: 融資融券、可能的其他統計資料
- **範例**: `/web/stock/margin_trading/margin_balance/margin_bal_result.php`

**重要**: 這個發現對未來尋找其他 TPEx API 非常有幫助！

---

## 📈 效能提升統計

### ✅ 全部完成！所有資料類型皆使用官方 API

| 資料類型 | FinMind 請求數 | 官方 API 請求數 | 效能提升 | 資料延遲 |
|---------|---------------|----------------|----------|----------|
| **價格資料** | 1,946 | 2 | **973x** | 即時 vs 30天 |
| **融資融券** | 1,815 | 2 | **907.5x** | 即時 vs 30天 |
| **三大法人** | ~1,863 | 2 | **~930x** | 即時 vs 30天 |
| **借券賣出** | ~1,185 | 1 | **~1,185x** | 即時 vs 30天 |

**總計效能提升**:
- 原本需要 ~6,809 次 API 請求
- 現在只需要 **7 次請求**
- **整體效能提升約 973 倍**
- **所有資料即時更新（0 延遲）**

---

## 🎯 實作策略 - 全部達成 ✅

### ✅ 所有資料類型皆使用官方 API
- [x] 價格資料 → 官方 API（TWSE + TPEx，973x 效能提升）
- [x] 融資融券 → 官方 API（TWSE + TPEx，907.5x 效能提升）
- [x] 三大法人 → 官方 API（TWSE T86 + TPEx，930x 效能提升）
- [x] 借券賣出 → 官方 API（TWSE TWT93U，1,185x 效能提升）

### 優勢
1. **即時資料**: 所有資料都是當日最新，無延遲
2. **巨大效能提升**: 整體提升約 973 倍
3. **官方來源**: 資料權威可靠
4. **無需 API Token**: 所有端點皆為公開 API
5. **完全擺脫 FinMind**: 不再受 30 天資料延遲限制

---

## 📚 參考資源

- [TWSE OpenAPI](https://openapi.twse.com.tw/)
- [TPEx OpenAPI](https://www.tpex.org.tw/openapi/)
- [證交所 API (GitHub Gist)](https://gist.github.com/ktlast/148daf9045d491ac98a1ce90da8c1715)
- [使用證券交易所API爬取股票資訊 (HackMD)](https://hackmd.io/@aaronlife/python-ex-stock-by-api)
- [voidful/tw-institutional-stocker](https://github.com/voidful/tw-institutional-stocker) - 三大法人 API 參考來源

---

## 📝 測試與收集腳本

研究過程中建立的腳本：

### 測試腳本
- [scripts/test_institutional_voidful_method.py](../scripts/test_institutional_voidful_method.py) - 三大法人 API 測試
- [scripts/test_lending_api.py](../scripts/test_lending_api.py) - 借券賣出 API 測試

### 收集腳本
- [scripts/collect_institutional_data.py](../scripts/collect_institutional_data.py) - 三大法人資料收集
- [scripts/collect_lending_data.py](../scripts/collect_lending_data.py) - 借券賣出資料收集

---

## 🎉 總結

成功找到所有四種資料類型的官方 API！

| 資料類型 | API 數量 | 狀態 |
|---------|---------|------|
| 價格資料 | 2 (TWSE + TPEx) | ✅ |
| 融資融券 | 2 (TWSE + TPEx) | ✅ |
| 三大法人 | 2 (TWSE + TPEx) | ✅ |
| 借券賣出 | 1 (TWSE，含上市+上櫃) | ✅ |

**專案目標達成**: 完全擺脫 FinMind 30 天資料延遲限制，實現即時資料收集，效能提升 973 倍！
