#!/usr/bin/env python3
"""
快速查詢交易日的命令列工具

使用範例:
    python scripts/common-tools/get_trading_days.py check 2026-01-01
    python scripts/common-tools/get_trading_days.py range 2026-01-01 2026-01-31
    python scripts/common-tools/get_trading_days.py summary 2026
"""

import sys
from pathlib import Path

# 加入專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from services.common.calendar import TradingCalendarService
import argparse


def cmd_check(args):
    """檢查是否為交易日"""
    calendar = TradingCalendarService()

    is_trading = calendar.is_trading_day(args.date)

    print(f"\n📅 {args.date}")
    if is_trading:
        print("✅ 是交易日")
    else:
        print("❌ 不是交易日（休市）")

        # 檢查是否為特殊日
        special = calendar.is_special_day(args.date)
        if special:
            print(f"   說明: {special['name']}")

        # 顯示最近和下一個交易日
        latest = calendar.get_latest_trading_day(args.date)
        next_day = calendar.get_next_trading_day(args.date)
        print(f"\n   ← 最近的交易日: {latest}")
        print(f"   → 下一個交易日: {next_day}")


def cmd_range(args):
    """取得日期區間的交易日"""
    calendar = TradingCalendarService()

    trading_days = calendar.get_trading_days_in_range(
        args.start_date,
        args.end_date
    )

    print(f"\n📅 {args.start_date} 至 {args.end_date}")
    print(f"共有 {len(trading_days)} 個交易日\n")

    for i, date in enumerate(trading_days, 1):
        special = calendar.is_special_day(date)
        if special:
            print(f"  {i:3d}. {date} ⭐ {special['name']}")
        else:
            print(f"  {i:3d}. {date}")


def cmd_summary(args):
    """顯示年度摘要"""
    calendar = TradingCalendarService()

    summary = calendar.get_summary(args.year)

    print(f"\n📊 {args.year} 年交易日曆摘要")
    print("=" * 50)
    print(f"\n交易日總數: {summary['trading_days_count']} 天")
    print(f"休市日總數: {summary['holidays_count']} 天")
    print(f"\n第一個交易日: {summary['first_trading_day']}")
    print(f"最後一個交易日: {summary['last_trading_day']}")
    print(f"\n資料來源: {summary['data_source']}")

    print(f"\n特殊交易日統計:")
    for day_type, count in summary['special_days'].items():
        type_name = {
            'start_trading': '開始交易日',
            'last_trading': '最後交易日',
            'settlement_only': '僅結算交割日'
        }.get(day_type, day_type)
        print(f"  {type_name}: {count} 天")


def cmd_holidays(args):
    """顯示休市日列表"""
    calendar = TradingCalendarService()

    holidays = sorted(calendar.get_holidays())

    # 過濾指定年度
    if args.year:
        holidays = [h for h in holidays if h.startswith(str(args.year))]

    print(f"\n📅 休市日列表 ({len(holidays)} 天)")
    print("=" * 50)

    for i, date in enumerate(holidays, 1):
        special = calendar.is_special_day(date)
        if special:
            print(f"  {i:3d}. {date} - {special['name']}")
        else:
            print(f"  {i:3d}. {date}")


def cmd_special(args):
    """顯示特殊交易日"""
    calendar = TradingCalendarService()

    special_days = calendar.get_special_days()

    print(f"\n⭐ 特殊交易日")
    print("=" * 50)

    for day_type, days in special_days.items():
        type_name = {
            'start_trading': '開始交易日',
            'last_trading': '最後交易日',
            'settlement_only': '僅結算交割日'
        }.get(day_type, day_type)

        if days:
            print(f"\n【{type_name}】({len(days)} 天)")
            for day in days:
                print(f"  {day['date']} ({day['weekday']}) - {day['name']}")


def main():
    parser = argparse.ArgumentParser(
        description='證交所交易日曆查詢工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用範例:
  檢查是否為交易日:
    %(prog)s check 2026-01-01

  查詢區間內的交易日:
    %(prog)s range 2026-01-01 2026-01-31

  查看年度摘要:
    %(prog)s summary 2026

  查看休市日:
    %(prog)s holidays --year 2026

  查看特殊交易日:
    %(prog)s special
        '''
    )

    subparsers = parser.add_subparsers(
        title='可用指令',
        dest='command',
        required=True
    )

    # check 指令
    parser_check = subparsers.add_parser(
        'check',
        help='檢查是否為交易日'
    )
    parser_check.add_argument('date', help='日期 (YYYY-MM-DD)')
    parser_check.set_defaults(func=cmd_check)

    # range 指令
    parser_range = subparsers.add_parser(
        'range',
        help='查詢區間內的交易日'
    )
    parser_range.add_argument('start_date', help='起始日期 (YYYY-MM-DD)')
    parser_range.add_argument('end_date', help='結束日期 (YYYY-MM-DD)')
    parser_range.set_defaults(func=cmd_range)

    # summary 指令
    parser_summary = subparsers.add_parser(
        'summary',
        help='顯示年度摘要'
    )
    parser_summary.add_argument('year', type=int, help='年度 (YYYY)')
    parser_summary.set_defaults(func=cmd_summary)

    # holidays 指令
    parser_holidays = subparsers.add_parser(
        'holidays',
        help='顯示休市日列表'
    )
    parser_holidays.add_argument(
        '--year',
        type=int,
        help='過濾指定年度'
    )
    parser_holidays.set_defaults(func=cmd_holidays)

    # special 指令
    parser_special = subparsers.add_parser(
        'special',
        help='顯示特殊交易日'
    )
    parser_special.set_defaults(func=cmd_special)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
