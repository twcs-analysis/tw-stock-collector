# Phase 1 使用指南

完整的 Phase 1 資料收集系統使用指南。

## 目錄

- [系統概述](#系統概述)
- [快速開始](#快速開始)
- [詳細使用說明](#詳細使用說明)
- [API 說明](#api-說明)
- [配置指南](#配置指南)
- [常見問題](#常見問題)
- [效能優化](#效能優化)

## 系統概述

Phase 1 提供完整的台股資料收集功能：

### 支援的資料類型

- **股票價格** (OHLCV) - 開高低收、成交量
- **法人買賣超** - 外資、投信、自營商買賣超資料
- **融資融券** - 融資買入、融券賣出與餘額變化
- **借券賣出** - 借券餘額與變化

### 核心特色

- ✅ **配置驅動架構**：透過 YAML 配置檔管理所有設定
- ✅ **智能重試機制**：使用 tenacity 實現自動重試與錯誤處理
- ✅ **資料驗證**：自動驗證資料完整性與邏輯正確性
- ✅ **彈性儲存**：支援 JSON、CSV、Parquet 多種格式
- ✅ **完整日誌**：結構化日誌記錄所有操作
- ✅ **高效收集**：使用 Aggregate API 優化收集效率（2.5 小時 → 5 分鐘）

## 快速開始

### 1. 安裝

```bash
# 建立虛擬環境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt
```

### 2. 配置（選用）

設定 FinMind API Token 以提高速率限制：

```bash
export FINMIND_API_TOKEN="your_token_here"
```

或編輯 `config/config.yaml`：

```yaml
finmind:
  api_token: your_token_here
```

### 3. 初始化股票清單

```bash
python scripts/init_stock_list.py
```

### 4. 開始收集

```bash
# 收集今天的資料
python scripts/run_collection.py

# 收集昨天的資料
python scripts/run_collection.py --date yesterday
```

## 詳細使用說明

### 執行腳本

#### init_stock_list.py - 初始化股票清單

獲取並儲存台股股票清單，排除權證、特別股等非標的股票。

```bash
# 基本用法
python scripts/init_stock_list.py

# 強制更新（忽略快取）
python scripts/init_stock_list.py --force

# 使用自訂 API Token
python scripts/init_stock_list.py --api-token YOUR_TOKEN
```

**輸出範例：**
```
======================================================================
股票清單統計
======================================================================
總數: 1800 檔
股票: 1650 檔
ETF: 150 檔
```

#### run_collection.py - 每日資料收集

收集指定日期的台股資料。

```bash
# 收集今天的資料（預設）
python scripts/run_collection.py

# 收集指定日期
python scripts/run_collection.py --date 2025-01-28

# 收集昨天
python scripts/run_collection.py --date yesterday

# 只收集特定類型
python scripts/run_collection.py --types price institutional

# 只收集指定股票
python scripts/run_collection.py --stocks 2330 2317 2454

# 完整範例：收集昨天的價格與法人資料
python scripts/run_collection.py \
  --date yesterday \
  --types price institutional \
  --api-token YOUR_TOKEN
```

**參數說明：**
- `--date`: 日期（today, yesterday, YYYY-MM-DD）
- `--types`: 資料類型（price, institutional, margin, lending）
- `--stocks`: 股票代碼列表（只對價格資料有效）
- `--api-token`: FinMind API Token

**輸出範例：**
```
======================================================================
收集完成
======================================================================
總收集次數: 1800
成功: 1795
失敗: 5
總筆數: 1795
成功率: 99.7%
======================================================================
```

#### backfill.py - 回補歷史資料

批次收集歷史資料。

```bash
# 回補指定日期範圍
python scripts/backfill.py \
  --start 2025-01-01 \
  --end 2025-01-31

# 回補最近 N 天
python scripts/backfill.py \
  --start 2025-01-01 \
  --days 7

# 只回補特定類型
python scripts/backfill.py \
  --start 2025-01-01 \
  --days 30 \
  --types price institutional

# 只回補指定股票
python scripts/backfill.py \
  --start 2025-01-01 \
  --end 2025-01-31 \
  --stocks 2330 2317
```

**參數說明：**
- `--start`: 開始日期（必填，YYYY-MM-DD）
- `--end`: 結束日期（與 days 二選一）
- `--days`: 回補天數（與 end 二選一）
- `--types`: 資料類型
- `--stocks`: 股票代碼列表
- `--api-token`: FinMind API Token

#### test_phase1.py - 測試系統

執行完整的 Phase 1 功能測試。

```bash
# 執行基礎測試（不含 API）
python scripts/test_phase1.py --skip-api

# 執行完整測試（含 API）
python scripts/test_phase1.py

# 顯示詳細錯誤訊息
python scripts/test_phase1.py --verbose
```

**測試項目：**
- ✅ 配置載入
- ✅ 檔案處理器
- ✅ 路徑建立
- ✅ 資料驗證器
- ✅ 收集器建立
- ✅ 收集器統計
- ✅ 實際 API 呼叫（選用）

## API 說明

### 基礎用法

```python
from src.collectors import create_price_collector

# 建立收集器
collector = create_price_collector()

# 收集單一股票
df = collector.collect('2025-01-28', stock_id='2330')

# 收集並儲存
success = collector.collect_and_save('2025-01-28', stock_id='2330')

# 查看統計
stats = collector.get_stats()
print(f"API 呼叫次數: {stats['api_calls']}")
print(f"總記錄數: {stats['total_records']}")
```

### 使用 Aggregate API

```python
from src.collectors import create_institutional_collector

# 建立收集器
collector = create_institutional_collector()

# 一次取得所有股票的法人資料
df = collector.collect('2025-01-28', stock_id=None)

# 儲存資料
collector.save_data(df, '2025-01-28')
```

### 自訂配置

```python
from src.utils import Config, get_logger
from src.collectors import PriceCollector

# 載入自訂配置
config = Config('path/to/config.yaml')

# 建立自訂 logger
logger = get_logger(__name__)

# 建立收集器
collector = PriceCollector(
    config=config,
    api_token='your_token'
)
```

### 資料驗證

```python
from src.utils import DataValidator, check_data_completeness

# 建立驗證器
validator = DataValidator()

# 驗證資料
is_valid = validator.validate(df, 'price', raise_on_error=False)

# 檢查完整性
completeness = check_data_completeness(df, 'price')
print(f"完整性: {completeness['completeness_rate']:.1%}")
print(f"缺失欄位: {completeness['missing_fields']}")
```

## 配置指南

### config/config.yaml

```yaml
# FinMind API 設定
finmind:
  # API Token（可使用環境變數）
  api_token: ${FINMIND_API_TOKEN:}
  
  # 速率限制（每分鐘）
  rate_limit: 600
  
  # 重試設定
  retry:
    max_attempts: 3
    wait_seconds: 10
    backoff_factor: 2

# 資料收集設定
collection:
  # 股票過濾
  stock_filter:
    mode: exclude
    exclude_types:
      - 權證
      - 特別股
      - REITs
      - 牛熊證
      - 可轉債
  
  # 批次處理
  batch:
    use_aggregate_api: true
    batch_size: 100

# 儲存設定
storage:
  # 基礎路徑
  base_path: data/raw
  
  # 目錄結構
  # - date_hierarchy: data/raw/price/2025/01/20250128/2330.json
  # - aggregate: data/raw/institutional/2025/01/2025-01-28.json
  # - flat: data/raw/price/2025-01-28_2330.json
  directory_structure: date_hierarchy
  
  # 檔案格式 (json, csv, parquet)
  file_format: json
  
  # 壓縮設定
  compression: false
  compression_format: gzip

# 驗證設定
validation:
  enabled: true
  strict_mode: false
  rules:
    price:
      required_columns:
        - stock_id
        - date
        - open
        - high
        - low
        - close
        - volume
      value_ranges:
        close: [0, null]
        volume: [0, null]
      logic_checks:
        - high >= low
        - high >= open
        - high >= close

# 監控設定
monitoring:
  log_level: INFO
  performance_tracking: true
  error_notification: false
```

### config/logging.yaml

```yaml
version: 1
disable_existing_loggers: false

formatters:
  standard:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  detailed:
    format: '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
  json:
    class: pythonjsonlogger.jsonlogger.JsonFormatter
    format: '%(asctime)s %(name)s %(levelname)s %(message)s'

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: standard
    stream: ext://sys.stdout

  file:
    class: logging.handlers.RotatingFileHandler
    level: DEBUG
    formatter: detailed
    filename: logs/collector.log
    maxBytes: 10485760  # 10MB
    backupCount: 5

  error_file:
    class: logging.handlers.RotatingFileHandler
    level: ERROR
    formatter: detailed
    filename: logs/error.log
    maxBytes: 10485760
    backupCount: 3

root:
  level: DEBUG
  handlers: [console, file, error_file]

loggers:
  src.collectors:
    level: DEBUG
  src.utils:
    level: DEBUG
```

## 常見問題

### Q: 為什麼需要 API Token？

**A:** FinMind 免費版有速率限制（600 次/分鐘）。使用 API Token 可以：
- 提高速率限制
- 存取更多歷史資料
- 獲得更穩定的服務

### Q: 如何處理非交易日？

**A:** 系統會自動處理：
- 非交易日不會有資料
- 日誌會記錄「無資料」狀態
- 不會產生錯誤
- 不會建立空檔案

### Q: 資料儲存在哪裡？

**A:** 預設儲存在 `data/raw/` 目錄：
```
data/raw/
├── price/         # 價格資料
├── institutional/ # 法人資料
├── margin/        # 融資融券
└── lending/       # 借券資料
```

可透過 `config/config.yaml` 修改：
```yaml
storage:
  base_path: /your/custom/path
```

### Q: 如何更換儲存格式？

**A:** 編輯 `config/config.yaml`：
```yaml
storage:
  file_format: csv  # 或 json、parquet
```

### Q: 測試失敗怎麼辦？

**A:** 使用 `--verbose` 查看詳細錯誤：
```bash
python scripts/test_phase1.py --verbose
```

常見問題：
1. **Missing module**: 確認已安裝所有依賴 `pip install -r requirements.txt`
2. **API Error**: 檢查網路連線和 API Token
3. **Permission Error**: 確認有寫入 `data/` 和 `logs/` 的權限

### Q: 如何提高收集速度？

**A:** 幾個方法：
1. 使用 Aggregate API（已預設啟用）
2. 使用 API Token 提高速率限制
3. 調整批次大小：
```yaml
collection:
  batch:
    batch_size: 200  # 增加批次大小
```

### Q: 資料驗證失敗怎麼辦？

**A:** 有兩種處理方式：

1. **寬鬆模式**（預設）：記錄錯誤但繼續執行
```yaml
validation:
  strict_mode: false
```

2. **嚴格模式**：驗證失敗時停止
```yaml
validation:
  strict_mode: true
```

## 效能優化

### Aggregate API 策略

本系統針對法人、融資、借券資料使用 **Aggregate API 策略**：

| 資料類型 | 傳統方式 | Aggregate API | 效能提升 |
|---------|---------|---------------|---------|
| 股票價格 | 2000+ 次 | 2000+ 次 | - |
| 法人買賣 | 2000+ 次 | **1 次** | **30 倍** |
| 融資融券 | 2000+ 次 | **1 次** | **30 倍** |
| 借券賣出 | 2000+ 次 | **1 次** | **30 倍** |

**總收集時間**：從 2.5 小時降低至 **5 分鐘**

### 重試機制

使用 tenacity 實現智能重試：

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def fetch_data():
    # API 呼叫
    pass
```

配置：
```yaml
finmind:
  retry:
    max_attempts: 3
    wait_seconds: 10
    backoff_factor: 2
```

### 平行處理（未來）

目前系統採用序列處理，未來可實作平行處理進一步提升效能：

```python
# 未來功能
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(collect, stock_id) for stock_id in stocks]
```

## 資料結構說明

### 價格資料 (price)

```json
{
  "stock_id": "2330",
  "date": "2025-01-28",
  "open": 650.0,
  "high": 655.0,
  "low": 648.0,
  "close": 652.0,
  "volume": 50000000,
  "trading_money": 32600000000
}
```

### 法人資料 (institutional)

```json
{
  "stock_id": "2330",
  "date": "2025-01-28",
  "foreign_investor_buy": 5000000,
  "foreign_investor_sell": 3000000,
  "foreign_investor_diff": 2000000,
  "investment_trust_buy": 1000000,
  "investment_trust_sell": 500000,
  "investment_trust_diff": 500000,
  "dealer_buy": 800000,
  "dealer_sell": 600000,
  "dealer_diff": 200000
}
```

### 融資融券 (margin)

```json
{
  "stock_id": "2330",
  "date": "2025-01-28",
  "margin_purchase_buy": 1000,
  "margin_purchase_sell": 800,
  "margin_purchase_balance": 50000,
  "short_sale_buy": 500,
  "short_sale_sell": 600,
  "short_sale_balance": 20000
}
```

## 故障排除

### API 呼叫失敗

**症狀：**
```
ERROR - API 呼叫失敗: Connection timeout
```

**解決方法：**
1. 檢查網路連線
2. 檢查 FinMind API 狀態
3. 增加重試次數：
```yaml
finmind:
  retry:
    max_attempts: 5
```

### 資料驗證錯誤

**症狀：**
```
ERROR - 驗證失敗: price - OHLC 資料邏輯錯誤
```

**解決方法：**
1. 檢查原始資料是否正確
2. 使用寬鬆模式：
```yaml
validation:
  strict_mode: false
```

### 磁碟空間不足

**症狀：**
```
ERROR - 檔案儲存失敗: No space left on device
```

**解決方法：**
1. 清理舊日誌：
```bash
find logs/ -name "*.log" -mtime +30 -delete
```

2. 啟用壓縮：
```yaml
storage:
  compression: true
  compression_format: gzip
```

3. 使用 Parquet 格式（更小）：
```yaml
storage:
  file_format: parquet
```

## 進階使用

### 自訂收集器

```python
from src.collectors import BaseCollector

class MyCustomCollector(BaseCollector):
    def get_data_type(self):
        return 'custom'
    
    def collect(self, date, stock_id=None, **kwargs):
        # 實作收集邏輯
        df = self.fetch_with_retry(
            self.dl.your_api_method,
            stock_id=stock_id,
            date=date
        )
        return self._process_data(df)
```

### 整合外部資料源

```python
from src.utils import FileHandler, DataValidator

# 讀取外部資料
handler = FileHandler()
external_data = handler.load_csv('external_data.csv')

# 驗證資料
validator = DataValidator()
if validator.validate(external_data, 'price'):
    # 合併資料
    combined = pd.concat([local_data, external_data])
```

## 授權

MIT License

---

**最後更新**：2025-12-28
**版本**：Phase 1 (v1.0.0)
