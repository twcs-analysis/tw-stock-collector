"""
測試證交所交易日曆服務

展示 TradingCalendarService 的各種使用方式
"""

import sys
from pathlib import Path

# 加入專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from services.common.calendar import TradingCalendarService
from datetime import datetime
import logging

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_basic_usage():
    """測試基本使用"""
    print("\n" + "=" * 60)
    print("測試 1: 基本使用")
    print("=" * 60)

    # 建立服務實例
    calendar = TradingCalendarService()

    # 測試幾個日期
    test_dates = [
        "2026-01-01",  # 元旦（休市）
        "2026-01-02",  # 交易日
        "2026-02-15",  # 春節（休市）
        "2026-02-23",  # 春節後開始交易
        "2026-12-25",  # 行憲紀念日（休市）
    ]

    print("\n檢查特定日期是否為交易日:")
    for date in test_dates:
        is_trading = calendar.is_trading_day(date)
        status = "✅ 交易日" if is_trading else "❌ 休市"
        print(f"  {date}: {status}")

        # 檢查是否為特殊日
        special = calendar.is_special_day(date)
        if special:
            print(f"    → 特殊日: {special['name']} ({special['type']})")


def test_trading_days_range():
    """測試取得交易日區間"""
    print("\n" + "=" * 60)
    print("測試 2: 取得交易日區間")
    print("=" * 60)

    calendar = TradingCalendarService()

    # 取得 2026 年 1 月的所有交易日
    start_date = "2026-01-01"
    end_date = "2026-01-31"

    trading_days = calendar.get_trading_days_in_range(start_date, end_date)

    print(f"\n{start_date} 至 {end_date} 的交易日:")
    print(f"總計: {len(trading_days)} 天\n")

    for i, date in enumerate(trading_days, 1):
        print(f"  {i:2d}. {date}")


def test_year_summary():
    """測試年度摘要"""
    print("\n" + "=" * 60)
    print("測試 3: 年度摘要")
    print("=" * 60)

    calendar = TradingCalendarService()

    # 取得 2026 年摘要
    summary = calendar.get_summary(2026)

    print(f"\n2026 年交易日曆摘要:")
    print(f"  交易日總數: {summary['trading_days_count']} 天")
    print(f"  休市日總數: {summary['holidays_count']} 天")
    print(f"  第一個交易日: {summary['first_trading_day']}")
    print(f"  最後一個交易日: {summary['last_trading_day']}")
    print(f"  資料來源: {summary['data_source']}")

    print(f"\n  特殊交易日統計:")
    for day_type, count in summary['special_days'].items():
        type_name = {
            'start_trading': '開始交易日',
            'last_trading': '最後交易日',
            'settlement_only': '僅結算交割日'
        }.get(day_type, day_type)
        print(f"    {type_name}: {count} 天")


def test_latest_and_next_trading_day():
    """測試最近/下一個交易日"""
    print("\n" + "=" * 60)
    print("測試 4: 最近/下一個交易日")
    print("=" * 60)

    calendar = TradingCalendarService()

    # 測試幾個日期
    test_dates = [
        "2026-01-01",  # 元旦（休市）
        "2026-02-15",  # 春節（休市）
        "2026-04-05",  # 清明（休市）
    ]

    print("\n從休市日找最近/下一個交易日:")
    for date in test_dates:
        latest = calendar.get_latest_trading_day(date)
        next_day = calendar.get_next_trading_day(date)

        print(f"\n  {date} (休市日):")
        print(f"    ← 最近的交易日: {latest}")
        print(f"    → 下一個交易日: {next_day}")


def test_special_days():
    """測試特殊交易日"""
    print("\n" + "=" * 60)
    print("測試 5: 特殊交易日")
    print("=" * 60)

    calendar = TradingCalendarService()

    special_days = calendar.get_special_days()

    print("\n2026 年特殊交易日:")

    for day_type, days in special_days.items():
        type_name = {
            'start_trading': '開始交易日',
            'last_trading': '最後交易日',
            'settlement_only': '僅結算交割日'
        }.get(day_type, day_type)

        if days:
            print(f"\n  【{type_name}】")
            for day in days:
                print(f"    {day['date']} ({day['weekday']}) - {day['name']}")


def test_cache_mechanism():
    """測試快取機制"""
    print("\n" + "=" * 60)
    print("測試 6: 快取機制")
    print("=" * 60)

    # 第一次建立（從 API 取得）
    print("\n第一次建立服務（應從 API 取得）:")
    calendar1 = TradingCalendarService(use_cache=True)
    calendar1.refresh()

    # 第二次建立（從快取取得）
    print("\n第二次建立服務（應從快取取得）:")
    calendar2 = TradingCalendarService(use_cache=True)
    calendar2.refresh()

    # 驗證資料一致
    holidays1 = calendar1.get_holidays()
    holidays2 = calendar2.get_holidays()

    print(f"\n資料一致性檢查:")
    print(f"  第一次取得的休市日數: {len(holidays1)}")
    print(f"  第二次取得的休市日數: {len(holidays2)}")
    print(f"  資料是否一致: {'✅ 是' if holidays1 == holidays2 else '❌ 否'}")

    # 檢查快取檔案
    if calendar1.CACHE_FILE.exists():
        print(f"\n快取檔案位置: {calendar1.CACHE_FILE}")
        print(f"快取檔案大小: {calendar1.CACHE_FILE.stat().st_size} bytes")


def test_performance():
    """測試效能"""
    print("\n" + "=" * 60)
    print("測試 7: 效能測試")
    print("=" * 60)

    import time
    from datetime import timedelta

    calendar = TradingCalendarService()

    # 測試 1000 次查詢
    test_count = 1000
    start_date = "2026-01-01"

    print(f"\n執行 {test_count} 次 is_trading_day() 查詢:")

    start_time = time.time()

    for i in range(test_count):
        date = (datetime.strptime(start_date, '%Y-%m-%d') +
                timedelta(days=i % 365)).strftime('%Y-%m-%d')
        calendar.is_trading_day(date)

    elapsed = time.time() - start_time

    print(f"  總耗時: {elapsed:.4f} 秒")
    print(f"  平均每次: {elapsed/test_count*1000:.4f} 毫秒")
    print(f"  每秒查詢數: {test_count/elapsed:.0f} 次/秒")


def test_fallback_mechanism():
    """測試備援機制"""
    print("\n" + "=" * 60)
    print("測試 8: 備援機制")
    print("=" * 60)

    # 使用無效的 API URL 測試備援
    calendar = TradingCalendarService(use_cache=False)
    calendar.API_URL = "https://invalid-url.example.com"

    print("\n使用無效的 API URL（應啟用備援機制）:")

    try:
        calendar.refresh()
        holidays = calendar.get_holidays()

        print(f"  成功取得 {len(holidays)} 個休市日（來自備援清單）")

        # 測試幾個日期
        test_dates = ["2026-01-01", "2026-02-16", "2026-10-10"]
        print(f"\n  驗證備援資料:")
        for date in test_dates:
            is_trading = calendar.is_trading_day(date)
            print(f"    {date}: {'交易日' if is_trading else '休市'}")

    except Exception as e:
        print(f"  錯誤: {e}")


def main():
    """主測試函式"""
    from datetime import timedelta

    print("\n" + "=" * 60)
    print("證交所交易日曆服務 - 完整測試")
    print("=" * 60)

    try:
        test_basic_usage()
        test_trading_days_range()
        test_year_summary()
        test_latest_and_next_trading_day()
        test_special_days()
        test_cache_mechanism()
        test_performance()
        test_fallback_mechanism()

        print("\n" + "=" * 60)
        print("✅ 所有測試完成")
        print("=" * 60)

    except Exception as e:
        logger.error(f"測試過程發生錯誤: {e}", exc_info=True)
        print("\n" + "=" * 60)
        print("❌ 測試失敗")
        print("=" * 60)


if __name__ == '__main__':
    main()
