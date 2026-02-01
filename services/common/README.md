# Common Library

微服務共用程式庫，提供所有服務共用的工具函式、資料模型、驗證器等。

## 功能

- 工具函式 (日期處理、檔案操作、日誌)
- 資料模型定義
- 資料驗證器
- 資料源 API 封裝 (TWSE, TPEx)
- 常數與設定

## 目錄結構

```
common/
├── __init__.py
├── utils/                  # 工具函式
│   ├── __init__.py
│   ├── date_helper.py      # 日期與交易日處理
│   ├── file_handler.py     # 檔案操作
│   ├── logger.py           # 日誌記錄
│   ├── config.py           # 設定管理
│   ├── validator.py        # 通用驗證器
│   └── stock_list.py       # 股票清單管理
│
├── models/                 # 資料模型
│   ├── __init__.py
│   ├── stock.py            # 股票資料模型
│   ├── price.py            # 價格資料模型
│   ├── institutional.py    # 法人資料模型
│   └── margin.py           # 融資融券模型
│
├── validators/             # 資料驗證器
│   ├── __init__.py
│   ├── base_validator.py   # 基礎驗證器
│   ├── price_validator.py
│   ├── institutional_validator.py
│   ├── margin_validator.py
│   └── lending_validator.py
│
├── datasources/            # 資料源 API
│   ├── __init__.py
│   ├── base_datasource.py  # 基礎資料源類別
│   ├── twse_datasource.py  # 證交所 API
│   ├── tpex_datasource.py  # 櫃買中心 API
│   ├── twse_margin_datasource.py
│   └── tpex_margin_datasource.py
│
└── README.md               # 本文件
```

## 使用方式

### 日期處理

```python
from common.utils.date_helper import is_trading_day, get_latest_trading_day

# 判斷是否為交易日
if is_trading_day("2024-12-27"):
    print("這是交易日")

# 取得最近的交易日
latest = get_latest_trading_day()
print(f"最近交易日: {latest}")
```

### 檔案操作

```python
from common.utils.file_handler import save_json, load_json, ensure_dir

# 儲存 JSON 檔案
data = {"stock_id": "2330", "name": "台積電"}
save_json(data, "data/stocks/2330.json")

# 載入 JSON 檔案
data = load_json("data/stocks/2330.json")

# 確保目錄存在
ensure_dir("data/raw/price/2024/12")
```

### 日誌記錄

```python
from common.utils.logger import get_logger

logger = get_logger(__name__)

logger.info("開始收集資料")
logger.warning("API 回應時間較長")
logger.error("資料收集失敗", exc_info=True)
```

### 資料驗證

```python
from common.validators.price_validator import PriceValidator

validator = PriceValidator()

# 驗證價格資料
data = {
    "metadata": {...},
    "data": [...]
}

is_valid, errors = validator.validate(data)
if not is_valid:
    print(f"驗證失敗: {errors}")
```

### 資料源 API

```python
from common.datasources.twse_datasource import TWSeDataSource

# 建立資料源
twse = TWSeDataSource()

# 取得價格資料
price_data = twse.get_price_data("2024-12-27")

# 取得法人資料
institutional_data = twse.get_institutional_data("2024-12-27")
```

## 工具函式說明

### date_helper.py

- `is_trading_day(date)` - 判斷是否為交易日
- `get_latest_trading_day()` - 取得最近的交易日
- `get_trading_days(start, end)` - 取得日期區間的所有交易日
- `format_date(date)` - 日期格式轉換

### file_handler.py

- `save_json(data, filepath)` - 儲存 JSON 檔案
- `load_json(filepath)` - 載入 JSON 檔案
- `ensure_dir(dirpath)` - 確保目錄存在
- `get_data_path(type, date)` - 取得資料檔案路徑

### logger.py

- `get_logger(name)` - 取得 logger 實例
- `setup_logging(level)` - 設定日誌等級

### config.py

- `get_config(key)` - 取得設定值
- `load_env()` - 載入環境變數

## 資料模型

### Stock

```python
from common.models.stock import Stock

stock = Stock(
    stock_id="2330",
    stock_name="台積電",
    market="TWSE",
    industry="半導體"
)
```

### Price

```python
from common.models.price import Price

price = Price(
    date="2024-12-27",
    stock_id="2330",
    open=1080.0,
    high=1095.0,
    low=1075.0,
    close=1090.0,
    volume=45678912
)
```

## 驗證規則

### 價格資料

- 開高低收價格必須為正數
- 最高價 >= 收盤價 >= 最低價
- 成交量必須為正整數
- 日期格式必須為 YYYY-MM-DD

### 法人資料

- 買賣超金額範圍合理
- 買入 - 賣出 = 淨買超

### 融資融券

- 融資餘額、融券餘額必須為正數
- 資券比計算正確

## 相關服務

- [Data Collector](../data-collector/) - 資料收集服務
- [Data Importer](../data-importer/) - 資料匯入服務
- [API Service](../api-service/) - REST API 服務
- [Analyzer Service](../analyzer-service/) - 分析服務
