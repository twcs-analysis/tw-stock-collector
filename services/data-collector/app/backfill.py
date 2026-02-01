#!/usr/bin/env python3
"""
回補歷史資料

回補指定日期範圍的歷史資料。

Usage:
    python scripts/backfill.py --start 2025-01-01 --end 2025-01-31
    python scripts/backfill.py --start 2025-01-01 --days 7  # 回補 7 天
    python scripts/backfill.py --start 2025-01-01 --end 2025-01-31 --types price margin
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.collectors import (
    PriceCollector,
    MarginCollector,
    InstitutionalCollector,
    LendingCollector
)
from src.utils import is_trading_day

# 可用的收集器對應表
COLLECTORS = {
    'price': PriceCollector,
    'margin': MarginCollector,
    'institutional': InstitutionalCollector,
    'lending': LendingCollector,
}


def generate_date_range(start_date: str, end_date: str = None, days: int = None) -> list:
    """
    產生日期範圍

    Args:
        start_date: 開始日期 (YYYY-MM-DD)
        end_date: 結束日期 (YYYY-MM-DD)，與 days 二選一
        days: 天數，與 end_date 二選一

    Returns:
        list: 日期列表
    """
    start = datetime.strptime(start_date, '%Y-%m-%d')

    if end_date:
        end = datetime.strptime(end_date, '%Y-%m-%d')
    elif days:
        end = start + timedelta(days=days - 1)
    else:
        raise ValueError("必須指定 end_date 或 days")

    date_list = []
    current = start
    while current <= end:
        date_list.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)

    return date_list


def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description='回補歷史資料',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  # 回補 2025-01-01 到 2025-01-31 的所有資料
  python scripts/backfill.py --start 2025-01-01 --end 2025-01-31

  # 回補最近 7 天的資料
  python scripts/backfill.py --start 2025-01-01 --days 7

  # 只回補價格和融資融券資料
  python scripts/backfill.py --start 2025-01-01 --end 2025-01-31 --types price margin

  # 跳過交易日檢查（測試用）
  python scripts/backfill.py --start 2025-01-01 --days 7 --skip-trading-day-check
        """
    )
    parser.add_argument(
        '--start',
        type=str,
        required=True,
        help='開始日期 (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--end',
        type=str,
        help='結束日期 (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--days',
        type=int,
        help='回補天數'
    )
    parser.add_argument(
        '--types',
        nargs='+',
        choices=list(COLLECTORS.keys()),
        default=['price', 'institutional', 'margin', 'lending'],
        help='要收集的資料類型（可指定多個）'
    )
    parser.add_argument(
        '--skip-trading-day-check',
        action='store_true',
        help='跳過交易日檢查（適用於測試或補資料）'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=10,
        help='批次大小（每批處理天數），用於進度顯示'
    )

    args = parser.parse_args()

    # 產生日期範圍
    try:
        dates = generate_date_range(args.start, args.end, args.days)
    except ValueError as e:
        print(f"❌ 錯誤: {e}")
        return 1

    print("=" * 70)
    print("歷史資料回補")
    print("=" * 70)
    print(f"日期範圍: {dates[0]} ~ {dates[-1]}")
    print(f"總天數: {len(dates)} 天")
    print(f"資料類型: {', '.join(args.types)}")
    print(f"跳過交易日檢查: {'是' if args.skip_trading_day_check else '否'}")
    print("=" * 70)
    print()

    # 總統計
    total_stats = {
        'dates_processed': 0,
        'dates_success': 0,
        'dates_skipped': 0,
        'dates_failed': 0,
        'total_records': 0
    }

    # 逐日收集
    for idx, date in enumerate(dates, 1):
        print(f"\n[{idx}/{len(dates)}] 處理日期: {date}")
        print("-" * 70)

        # 檢查是否為交易日
        if not args.skip_trading_day_check:
            if not is_trading_day(date):
                print(f"⚠️  跳過（非交易日）: {date}")
                total_stats['dates_skipped'] += 1
                continue

        total_stats['dates_processed'] += 1
        date_success = True
        date_records = 0

        # 依序收集各類型資料
        for data_type in args.types:
            print(f"  [{data_type.upper()}] 開始收集...")

            try:
                # 建立收集器
                collector_class = COLLECTORS[data_type]
                collector = collector_class(date)

                # 執行收集
                result = collector.run()

                # 統計結果
                if result['status'] == 'success':
                    records = result.get('records', 0)
                    date_records += records
                    print(f"  ✅ {data_type}: {records} 筆")
                elif result['status'] == 'no_data':
                    print(f"  ⚠️  {data_type}: 無資料")
                else:
                    print(f"  ❌ {data_type}: {result.get('error')}")
                    date_success = False

            except Exception as e:
                print(f"  ❌ {data_type}: 例外錯誤 - {e}")
                date_success = False

        # 更新統計
        if date_success:
            total_stats['dates_success'] += 1
            total_stats['total_records'] += date_records
            print(f"✅ {date} 完成 - 共 {date_records} 筆記錄")
        else:
            total_stats['dates_failed'] += 1
            print(f"❌ {date} 有錯誤")

    # 最終統計
    print("\n" + "=" * 70)
    print("回補完成")
    print("=" * 70)
    print(f"總天數: {len(dates)}")
    print(f"  處理: {total_stats['dates_processed']}")
    print(f"  成功: {total_stats['dates_success']}")
    print(f"  跳過: {total_stats['dates_skipped']}")
    print(f"  失敗: {total_stats['dates_failed']}")
    print(f"總筆數: {total_stats['total_records']:,}")
    print("=" * 70)

    return 0 if total_stats['dates_failed'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
