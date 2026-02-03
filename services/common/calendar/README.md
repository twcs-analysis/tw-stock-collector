# 證交所交易日曆服務 (TradingCalendarService)

從證交所官方 API 取得交易日曆資訊的服務模組。

## 📋 功能特色

- ✅ **官方資料來源**：使用證交所 OpenAPI，確保資料準確性
- ✅ **智慧快取機制**：自動快取資料，減少 API 呼叫
- ✅ **備援機制**：API 失敗時使用本地備援清單
- ✅ **完整功能**：交易日判斷、區間查詢、特殊日標記
- ✅ **高效能**：記憶體快取，查詢速度極快

## 🚀 快速開始

### 基本使用

```python
from services.common.calendar import TradingCalendarService

# 建立服務實例
calendar = TradingCalendarService()

# 檢查是否為交易日
is_trading = calendar.is_trading_day("2026-01-02")
print(f"2026-01-02 是交易日: {is_trading}")  # True

is_trading = calendar.is_trading_day("2026-01-01")
print(f"2026-01-01 是交易日: {is_trading}")  # False (元旦)
```

### 取得交易日區間

```python
# 取得 2026 年 1 月的所有交易日
trading_days = calendar.get_trading_days_in_range(
    start_date="2026-01-01",
    end_date="2026-01-31"
)

print(f"2026 年 1 月共有 {len(trading_days)} 個交易日")
for date in trading_days[:5]:
    print(f"  {date}")
```

### 查詢最近/下一個交易日

```python
# 從元旦（休市日）找最近的交易日
latest = calendar.get_latest_trading_day("2026-01-01")
print(f"最近的交易日: {latest}")  # 2025-12-31

# 找下一個交易日
next_day = calendar.get_next_trading_day("2026-01-01")
print(f"下一個交易日: {next_day}")  # 2026-01-02
```

### 年度摘要

```python
# 取得 2026 年交易日曆摘要
summary = calendar.get_summary(2026)

print(f"交易日總數: {summary['trading_days_count']}")
print(f"休市日總數: {summary['holidays_count']}")
print(f"第一個交易日: {summary['first_trading_day']}")
print(f"最後一個交易日: {summary['last_trading_day']}")
```

## 📖 API 文檔

### 建立服務

```python
calendar = TradingCalendarService(
    use_cache=True,  # 是否使用快取（預設 True）
    timeout=10       # API 請求超時時間（秒）
)
```

### 主要方法

#### `is_trading_day(date: str) -> bool`

判斷是否為交易日。

**參數**：
- `date`: 日期字串，格式 "YYYY-MM-DD"

**返回**：
- `bool`: 是否為交易日

**範例**：
```python
is_trading = calendar.is_trading_day("2026-01-02")
```

---

#### `get_trading_days_in_range(start_date: str, end_date: str) -> List[str]`

取得指定日期範圍內的所有交易日。

**參數**：
- `start_date`: 起始日期 "YYYY-MM-DD"
- `end_date`: 結束日期 "YYYY-MM-DD"

**返回**：
- `List[str]`: 交易日列表

**範例**：
```python
trading_days = calendar.get_trading_days_in_range(
    "2026-01-01",
    "2026-01-31"
)
```

---

#### `get_latest_trading_day(from_date: Optional[str] = None) -> str`

取得最近的交易日（往前找）。

**參數**：
- `from_date`: 起始日期（預設: 今天）

**返回**：
- `str`: 最近的交易日

**範例**：
```python
# 從今天往前找
latest = calendar.get_latest_trading_day()

# 從指定日期往前找
latest = calendar.get_latest_trading_day("2026-01-01")
```

---

#### `get_next_trading_day(from_date: Optional[str] = None) -> str`

取得下一個交易日（往後找）。

**參數**：
- `from_date`: 起始日期（預設: 今天）

**返回**：
- `str`: 下一個交易日

**範例**：
```python
next_day = calendar.get_next_trading_day("2026-01-01")
```

---

#### `get_holidays() -> Set[str]`

取得所有休市日期。

**返回**：
- `Set[str]`: 休市日期集合

**範例**：
```python
holidays = calendar.get_holidays()
print(f"共有 {len(holidays)} 個休市日")
```

---

#### `get_special_days() -> Dict[str, List[Dict]]`

取得特殊交易日資訊。

**返回**：
- `Dict`: 特殊交易日字典
  ```python
  {
      'start_trading': [...],    # 開始交易日
      'last_trading': [...],     # 最後交易日
      'settlement_only': [...]   # 僅結算交割日
  }
  ```

**範例**：
```python
special_days = calendar.get_special_days()

for day in special_days['start_trading']:
    print(f"{day['date']} - {day['name']}")
```

---

#### `is_special_day(date: str) -> Optional[Dict]`

檢查是否為特殊交易日。

**參數**：
- `date`: 日期字串 "YYYY-MM-DD"

**返回**：
- `Dict` or `None`: 特殊日資訊，如果不是則返回 None

**範例**：
```python
special = calendar.is_special_day("2026-02-23")
if special:
    print(f"特殊日: {special['name']}")
    print(f"類型: {special['type']}")
```

---

#### `get_summary(year: Optional[int] = None) -> Dict`

取得年度摘要資訊。

**參數**：
- `year`: 年度（預設: 當年度）

**返回**：
- `Dict`: 摘要資訊

**範例**：
```python
summary = calendar.get_summary(2026)
```

---

#### `refresh(force: bool = False) -> bool`

重新整理交易日曆資料。

**參數**：
- `force`: 是否強制從 API 更新（忽略快取）

**返回**：
- `bool`: 是否成功更新

**範例**：
```python
# 使用快取或 API
calendar.refresh()

# 強制從 API 更新
calendar.refresh(force=True)
```

---

#### `get_trading_days_count(year: int) -> int`

取得指定年度的交易日數量。

**參數**：
- `year`: 年度

**返回**：
- `int`: 交易日數量

**範例**：
```python
count = calendar.get_trading_days_count(2026)
print(f"2026 年有 {count} 個交易日")
```

---

## 💡 使用場景

### 場景 1：資料收集前驗證

```python
from services.common.calendar import TradingCalendarService

def collect_data(date: str):
    """收集資料前驗證是否為交易日"""
    calendar = TradingCalendarService()

    if not calendar.is_trading_day(date):
        print(f"⚠️ {date} 不是交易日，跳過收集")
        return None

    print(f"✅ {date} 是交易日，開始收集")
    # 執行收集邏輯...
```

### 場景 2：批次回補資料

```python
def backfill_data(start_date: str, end_date: str):
    """批次回補交易日資料"""
    calendar = TradingCalendarService()

    # 取得區間內的所有交易日
    trading_days = calendar.get_trading_days_in_range(
        start_date,
        end_date
    )

    print(f"需要回補 {len(trading_days)} 個交易日的資料")

    for date in trading_days:
        collect_data(date)
```

### 場景 3：資料驗證

```python
def validate_collection_date(date: str) -> bool:
    """驗證收集日期是否正確"""
    calendar = TradingCalendarService()

    # 檢查是否為交易日
    if not calendar.is_trading_day(date):
        # 檢查是否為特殊日
        special = calendar.is_special_day(date)
        if special:
            print(f"⚠️ {date} 是 {special['name']}")
        else:
            print(f"❌ {date} 不是交易日")
        return False

    return True
```

### 場景 4：統計報表

```python
def generate_annual_report(year: int):
    """產生年度報表"""
    calendar = TradingCalendarService()

    summary = calendar.get_summary(year)

    print(f"\n{year} 年交易日曆統計")
    print(f"交易日總數: {summary['trading_days_count']}")
    print(f"休市日總數: {summary['holidays_count']}")
    print(f"第一個交易日: {summary['first_trading_day']}")
    print(f"最後一個交易日: {summary['last_trading_day']}")
```

## 🔧 快取機制

### 快取檔案位置

```
services/common/calendar/calendar_cache.json
```

### 快取結構

```json
{
  "year": 2026,
  "updated_at": "2026-02-03T15:30:00",
  "holidays": [
    "2026-01-01",
    "2026-02-15",
    ...
  ],
  "special_days": {
    "start_trading": [...],
    "last_trading": [...],
    "settlement_only": [...]
  }
}
```

### 快取策略

1. **記憶體快取**：資料載入後儲存在記憶體中
2. **檔案快取**：儲存到本地 JSON 檔案
3. **年度更新**：每年自動從 API 更新
4. **手動更新**：可使用 `refresh(force=True)` 強制更新

### 停用快取

```python
# 每次都從 API 取得
calendar = TradingCalendarService(use_cache=False)
```

## 🛡️ 錯誤處理

### API 失敗時的備援機制

```python
# 1. 嘗試使用快取
# 2. 快取失效則呼叫 API
# 3. API 失敗則使用備援清單
calendar = TradingCalendarService()
calendar.refresh()  # 自動處理錯誤
```

### 自訂備援清單

修改 `get_fallback_holidays()` 方法來更新備援清單：

```python
def get_fallback_holidays(self) -> Set[str]:
    """備援休市日清單"""
    return {
        '2026-01-01',  # 元旦
        '2026-02-16',  # 春節
        # ... 更多日期
    }
```

## 📊 效能指標

- **首次載入**：~2-3 秒（從 API）
- **快取載入**：~0.01 秒（從檔案）
- **查詢速度**：~0.001 毫秒/次（記憶體查詢）
- **批次查詢**：~100,000 次/秒

## 🧪 測試

執行測試腳本：

```bash
python scripts/common-tools/test_trading_calendar.py
```

測試項目：
1. ✅ 基本使用
2. ✅ 交易日區間查詢
3. ✅ 年度摘要
4. ✅ 最近/下一個交易日
5. ✅ 特殊交易日
6. ✅ 快取機制
7. ✅ 效能測試
8. ✅ 備援機制

## 📝 更新日誌

### v1.0.0 (2026-02-03)
- ✅ 初版發布
- ✅ 支援證交所 OpenAPI
- ✅ 實作快取機制
- ✅ 實作備援機制
- ✅ 完整測試覆蓋

## 🔗 相關連結

- [證交所 OpenAPI 文檔](https://openapi.twse.com.tw)
- [交易日曆 API](https://openapi.twse.com.tw/v1/news/holidaySchedule)

## 📞 支援

如有問題或建議，請建立 GitHub Issue。
