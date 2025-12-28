# 台股股票清單參考資料

本目錄包含台灣證券交易所（TWSE）與櫃買中心（TPEx）的完整上市上櫃股票清單。

## 檔案說明

### `stock_list_reference.csv`
完整的台股上市上櫃股票清單（參考用）

- **來源**:
  - 上市股票：證交所 OpenAPI `https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL`
  - 上櫃股票：櫃買中心 OpenAPI `https://www.tpex.org.tw/openapi/v1/tpex_mainboard_quotes`
- **更新日期**: 2025-12-28
- **股票數量**: 1,946 檔
  - 上市（TWSE）: 1,075 檔
  - 上櫃（TPEx）: 871 檔

### 欄位說明

| 欄位 | 說明 | 範例 |
|------|------|------|
| `stock_id` | 股票代碼（4位數字） | 2330 |
| `stock_name` | 股票名稱 | 台積電 |
| `type` | 市場類型 | twse（上市）/ tpex（上櫃） |
| `industry_category` | 產業分類 | 上市 / 上櫃 |
| `date` | 資料日期 | 2025-12-28 |
| `updated_at` | 更新時間 | 2025-12-28 14:35:39 |

## 使用說明

### 更新股票清單

執行以下腳本重新抓取最新的股票清單：

```bash
# 使用 Docker 執行
docker run --rm \
  -v "$(pwd)":/app \
  tw-stock-collector:local \
  python scripts/build_stock_list.py

# 複製到運作目錄
cp data/reference/stock_list_reference.csv data/stock_list.csv
```

### 程式使用

資料收集程式會自動從 `data/stock_list.csv` 讀取股票清單。此檔案是從 `stock_list_reference.csv` 複製過來的，作為實際運作使用的清單。

## 注意事項

1. **股票代碼規則**: 只包含 4 位數字的股票代碼（排除 ETF、權證等）
2. **市場分類**:
   - `twse`: 台灣證券交易所（上市）
   - `tpex`: 證券櫃檯買賣中心（上櫃）
3. **更新頻率**: 建議每月更新一次，以確保包含新上市上櫃的股票
4. **資料用途**: 此清單作為資料收集的參考，實際有交易的股票數量會少於清單總數

## 相關連結

- [台灣證券交易所 OpenAPI](https://openapi.twse.com.tw/)
- [證券櫃檯買賣中心 OpenAPI](https://www.tpex.org.tw/openapi/)
