# 資料目錄說明

本目錄存放台股資料收集系統的所有原始資料。

## 📁 目錄結構

```
data/
├── raw/                    # 原始資料目錄
│   ├── price/              # 每日價格資料（開高低收、成交量）
│   ├── institutional/      # 三大法人買賣超資料（外資、投信、自營商）
│   ├── margin/             # 融資融券資料
│   └── lending/            # 借券賣出資料
└── README.md               # 本說明文件
```

## 📊 資料格式

### raw/ - 原始資料

所有原始資料採用 **按日期聚合** 的 JSON 格式儲存：

```
raw/
└── {type}/                 # 資料類型（price, institutional, margin, lending）
    └── {YYYY}/             # 年份目錄
        └── {MM}/           # 月份目錄
            └── {YYYY-MM-DD}.json  # 單日檔案，包含當日所有股票資料
```

#### 檔案命名規則
- **格式**: `YYYY-MM-DD.json`
- **範例**: `2025-12-28.json`
- **內容**: 當日所有股票（約 1,000～2,000 檔）的該類型資料

#### 資料類型說明

| 類型 | 目錄 | 說明 | 每日檔案大小 |
|------|------|------|--------------|
| **價格資料** | `price/` | 開盤價、最高價、最低價、收盤價、成交量 | ~600 KB |
| **三大法人** | `institutional/` | 外資、投信、自營商的買賣超金額與張數 | ~1 MB |
| **融資融券** | `margin/` | 融資/融券餘額、增減、使用率 | ~900 KB |
| **借券賣出** | `lending/` | 借券賣出餘額、增減 | ~450 KB |

### 檔案格式範例

每個 JSON 檔案包含兩個部分：

```json
{
  "metadata": {
    "date": "2025-12-28",
    "collected_at": "2025-12-28T18:30:45",
    "total_count": 1946,
    "source": "TWSE + TPEx Official API"
  },
  "data": [
    {
      "date": "2025-12-28",
      "stock_id": "2330",
      "stock_name": "台積電",
      "open": 1080.0,
      "high": 1095.0,
      "low": 1075.0,
      "close": 1090.0,
      "volume": 45678912,
      "type": "twse"
    },
    // ... 更多股票資料
  ]
}
```

## 📈 資料來源

- **上市股票**: 台灣證券交易所 (TWSE) 官方 API
- **上櫃股票**: 證券櫃買中心 (TPEx) 官方 API
- **更新時間**: 每交易日 18:00 自動收集
- **API 認證**: 無需 Token（使用官方免費 API）

## 🔄 資料更新

### 自動收集
- **每日收集**: GitHub Actions 每交易日 18:00 自動執行
- **回補資料**: 可透過 GitHub Actions 手動觸發回補任務

### 手動收集

```bash
# 收集今日所有資料
python scripts/run_collection.py

# 收集指定日期
python scripts/run_collection.py --date 2025-12-28

# 收集特定類型
python scripts/run_collection.py --date 2025-12-28 --types price margin
```

## 📊 資料統計

### 已收集資料範圍
- **起始日期**: 2025-01-01
- **資料類型**: 4 種（price, institutional, margin, lending）
- **總檔案數**: 約 240 個交易日 × 4 種類型 = ~960 個檔案/年
- **總大小**: 約 700 MB/年

### 單日資料量
- **總大小**: ~2.9 MB
- **總筆數**: ~5,800 筆
- **涵蓋範圍**: 1,000～2,000 檔股票（含上市+上櫃）

## 🔗 快速連結

- [價格資料](raw/price/) - 每日股票開高低收與成交量
- [三大法人](raw/institutional/) - 外資、投信、自營商買賣超
- [融資融券](raw/margin/) - 融資融券餘額與變化
- [借券賣出](raw/lending/) - 借券賣出餘額資料

## 🔤 資料欄位說明

### 通用欄位（所有資料類型）

| 欄位名稱 | 資料型態 | 說明 | 範例 |
|---------|---------|------|------|
| `date` | string | 交易日期 (YYYY-MM-DD) | "2025-12-28" |
| `stock_id` | string | 股票代碼 (4 位數字) | "2330" |
| `stock_name` | string | 股票名稱（已去除前後空白） | "台積電" |
| `type` | string | 市場類型 | "twse" 或 "tpex" |

### 價格資料 (price)

| 欄位名稱 | 資料型態 | 說明 | 單位 |
|---------|---------|------|------|
| `open` | float | 開盤價 | 元 |
| `high` | float | 最高價 | 元 |
| `low` | float | 最低價 | 元 |
| `close` | float | 收盤價 | 元 |
| `volume` | integer | 成交量 | 股 |

### 三大法人 (institutional)

| 欄位名稱 | 資料型態 | 說明 | 單位 |
|---------|---------|------|------|
| `foreign_buy` | float | 外資買進 | 股 |
| `foreign_sell` | float | 外資賣出 | 股 |
| `foreign_net` | float | 外資買賣超 | 股 |
| `trust_buy` | float | 投信買進 | 股 |
| `trust_sell` | float | 投信賣出 | 股 |
| `trust_net` | float | 投信買賣超 | 股 |
| `dealer_buy` | float | 自營商買進 | 股 |
| `dealer_sell` | float | 自營商賣出 | 股 |
| `dealer_net` | float | 自營商買賣超 | 股 |
| `total_net` | float | 三大法人買賣超合計 | 股 |

**細分欄位**（供進階分析使用）：
- `foreign_main_*`: 外資主力（不含外資自營商）
- `foreign_dealer_*`: 外資自營商
- `dealer_self_*`: 自營商自行買賣
- `dealer_hedge_*`: 自營商避險

### 融資融券 (margin)

| 欄位名稱 | 資料型態 | 說明 | 單位 |
|---------|---------|------|------|
| `margin_balance` | float | 融資餘額 | 千元 |
| `margin_change` | float | 融資增減 | 千元 |
| `short_balance` | float | 融券餘額 | 股 |
| `short_change` | float | 融券增減 | 股 |

### 借券賣出 (lending)

| 欄位名稱 | 資料型態 | 說明 | 單位 |
|---------|---------|------|------|
| `lending_balance` | float | 借券餘額 | 股 |
| `lending_change` | float | 借券增減 | 股 |
| `prev_balance` | float | 前日餘額 | 股 |
| `daily_sell` | float | 當日賣出 | 股 |
| `daily_return` | float | 當日還券 | 股 |
| `daily_adjust` | float | 當日調整 | 股 |
| `next_day_available` | float | 次一營業日可限額 | 股 |

**融券相關欄位**（供參考，主要使用借券欄位）：
- `margin_*`: 融券相關欄位（同一 API 回傳）

## 🔄 中英文欄位對應

### API 原始欄位 → 標準化英文欄位

#### 三大法人 (Institutional)

| API 原始欄位（中文） | 標準化英文欄位 |
|-------------------|---------------|
| 證券代號 | stock_id |
| 證券名稱 | stock_name |
| 外陸資買進股數(不含外資自營商) | foreign_main_buy |
| 外陸資賣出股數(不含外資自營商) | foreign_main_sell |
| 外陸資買賣超股數(不含外資自營商) | foreign_main_net |
| 外資自營商買進股數 | foreign_dealer_buy |
| 外資自營商賣出股數 | foreign_dealer_sell |
| 外資自營商買賣超股數 | foreign_dealer_net |
| 投信買進股數 | trust_buy |
| 投信賣出股數 | trust_sell |
| 投信買賣超股數 | trust_net |
| 自營商買進股數(自行買賣) | dealer_self_buy |
| 自營商賣出股數(自行買賣) | dealer_self_sell |
| 自營商買賣超股數(自行買賣) | dealer_self_net |
| 自營商買進股數(避險) | dealer_hedge_buy |
| 自營商賣出股數(避險) | dealer_hedge_sell |
| 自營商買賣超股數(避險) | dealer_hedge_net |
| 自營商買賣超股數 | dealer_net_total |
| 三大法人買賣超股數 | total_net |

**計算欄位**（程式自動產生）：
- `foreign_buy = foreign_main_buy + foreign_dealer_buy`
- `foreign_sell = foreign_main_sell + foreign_dealer_sell`
- `foreign_net = foreign_main_net + foreign_dealer_net`
- `dealer_buy = dealer_self_buy + dealer_hedge_buy`
- `dealer_sell = dealer_self_sell + dealer_hedge_sell`
- `dealer_net = dealer_self_net + dealer_hedge_net`

#### 借券賣出 (Lending)

TWSE TWT93U API 回傳 15 個欄位（包含融券與借券）：

| 順序 | API 原始欄位（中文） | 標準化英文欄位 |
|-----|-------------------|---------------|
| 1 | 代號 | stock_id |
| 2 | 名稱 | stock_name |
| 3 | 前日餘額（融券） | margin_prev_balance |
| 4 | 賣出（融券） | margin_sell |
| 5 | 買進（融券） | margin_buy |
| 6 | 現券（融券） | margin_securities |
| 7 | 今日餘額（融券） | margin_today_balance |
| 8 | 次一營業日限額（融券） | margin_next_day_limit |
| 9 | 前日餘額（借券） | prev_balance |
| 10 | 當日賣出 | daily_sell |
| 11 | 當日還券 | daily_return |
| 12 | 當日調整 | daily_adjust |
| 13 | 當日餘額 | lending_balance |
| 14 | 次一營業日可限額 | next_day_available |
| 15 | 備註 | note |

**計算欄位**（程式自動產生）：
- `lending_change = lending_balance - prev_balance`

**注意事項**：
- API 的「前日餘額」欄位出現兩次（位置 3 和 9），分別對應融券和借券
- 使用欄位順序直接重新命名，而非 dict mapping
- `stock_name` 已自動去除前後空白

## 📝 注意事項

1. **交易日限制**: 只有交易日才會有資料，週末和國定假日無資料
2. **資料完整性**: 某些股票在特定日期可能因停牌等原因無資料
3. **版本控制**: 所有資料檔案都納入 Git 版本控制，可追蹤歷史變更
4. **儲存空間**: 完整一年資料約需 700 MB 空間
5. **欄位標準化**: 所有 API 回傳的中文欄位均已轉換為英文欄位名稱
6. **數值處理**: 所有數值欄位已去除逗號並轉換為適當的數值型態

---

**最後更新**: 2025-12-28
**維護者**: tw-stock-collector 專案團隊
