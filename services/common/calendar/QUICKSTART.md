# 快速入門 - 證交所交易日曆服務

## 🚀 5 分鐘快速上手

### 1. 基本使用

```python
from services.common.calendar import TradingCalendarService

# 建立服務
calendar = TradingCalendarService()

# 檢查是否為交易日
if calendar.is_trading_day("2026-01-02"):
    print("今天是交易日！")
```

### 2. 取得交易日區間

```python
# 取得 2026 年 1 月的所有交易日
trading_days = calendar.get_trading_days_in_range(
    "2026-01-01",
    "2026-01-31"
)

print(f"共有 {len(trading_days)} 個交易日")
# 輸出: 共有 21 個交易日
```

### 3. 查詢最近/下一個交易日

```python
# 從休市日找最近的交易日
latest = calendar.get_latest_trading_day("2026-01-01")
print(f"最近的交易日: {latest}")  # 2025-12-31

# 找下一個交易日
next_day = calendar.get_next_trading_day("2026-01-01")
print(f"下一個交易日: {next_day}")  # 2026-01-02
```

## 📝 常見使用場景

### 場景 1: 資料收集前驗證

```python
def collect_stock_data(date: str):
    """收集股票資料（加入交易日驗證）"""
    calendar = TradingCalendarService()

    # 驗證是否為交易日
    if not calendar.is_trading_day(date):
        print(f"⚠️ {date} 不是交易日，跳過收集")
        return

    print(f"✅ {date} 是交易日，開始收集資料...")
    # 執行資料收集邏輯
```

### 場景 2: 批次回補歷史資料

```python
def backfill_data(start_date: str, end_date: str):
    """批次回補交易日資料"""
    calendar = TradingCalendarService()

    # 只回補交易日的資料
    trading_days = calendar.get_trading_days_in_range(start_date, end_date)

    for date in trading_days:
        collect_stock_data(date)
```

### 場景 3: 生成年度報表

```python
def generate_annual_report(year: int):
    """產生年度統計報表"""
    calendar = TradingCalendarService()

    summary = calendar.get_summary(year)

    print(f"{year} 年統計:")
    print(f"  交易日: {summary['trading_days_count']} 天")
    print(f"  休市日: {summary['holidays_count']} 天")
```

## 🛠️ 命令列工具

### 快速查詢工具

```bash
# 檢查是否為交易日
python scripts/common-tools/get_trading_days.py check 2026-01-01

# 查詢區間內的交易日
python scripts/common-tools/get_trading_days.py range 2026-01-01 2026-01-31

# 查看年度摘要
python scripts/common-tools/get_trading_days.py summary 2026

# 查看所有休市日
python scripts/common-tools/get_trading_days.py holidays --year 2026

# 查看特殊交易日
python scripts/common-tools/get_trading_days.py special
```

### 輸出範例

```bash
$ python scripts/common-tools/get_trading_days.py check 2026-01-01

📅 2026-01-01
❌ 不是交易日（休市）
   說明: 中華民國開國紀念日

   ← 最近的交易日: 2025-12-31
   → 下一個交易日: 2026-01-02
```

## ⚡ 效能特性

- **首次載入**: ~2-3 秒（從 API 取得）
- **快取載入**: ~0.01 秒（從檔案）
- **查詢速度**: ~100,000 次/秒（記憶體查詢）

## 🔧 進階設定

### 停用快取

```python
# 每次都從 API 取得最新資料
calendar = TradingCalendarService(use_cache=False)
```

### 手動更新快取

```python
# 強制從 API 更新
calendar.refresh(force=True)
```

### 自訂超時時間

```python
# 設定 30 秒超時
calendar = TradingCalendarService(timeout=30)
```

## 📚 更多資訊

- [完整 API 文檔](README.md)
- [測試範例](../../scripts/common-tools/test_trading_calendar.py)
- [證交所 OpenAPI](https://openapi.twse.com.tw/v1/news/holidaySchedule)

## ❓ 常見問題

### Q: 資料多久更新一次？
A: 證交所每年初會公布全年度的交易日曆，服務會自動偵測年度變更並更新。

### Q: 如果網路斷線怎麼辦？
A: 服務有三層備援機制：記憶體快取 → 檔案快取 → 本地備援清單。

### Q: 可以查詢過去年度的資料嗎？
A: API 只提供當年度資料。過去年度需要手動維護備援清單。

### Q: 支援哪些年度？
A: 目前支援 2026 年。其他年度可透過修改 `get_fallback_holidays()` 方法加入。

## 🎯 下一步

1. 閱讀 [完整 API 文檔](README.md)
2. 查看 [測試範例](../../scripts/common-tools/test_trading_calendar.py)
3. 整合到您的專案中

---

**製作者**: tw-stock-collector 專案團隊
**版本**: 1.0.0
**更新日期**: 2026-02-03
