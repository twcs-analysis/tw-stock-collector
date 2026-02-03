#!/usr/bin/env python3
"""
歷史資料回補腳本 - 使用 MI_INDEX API

使用 TWSE MI_INDEX API 快速回補歷史資料。
此 API 一次請求即可取得所有股票的歷史資料，速度快（約 2-3 秒）。

Usage:
    # 回補單一日期
    python scripts/data-collector/backfill_historical.py --date 2026-01-27

    # 回補日期範圍
    python scripts/data-collector/backfill_historical.py --start 2026-01-27 --end 2026-01-30

    # 回補特定股票
    python scripts/data-collector/backfill_historical.py --date 2026-01-27 --stocks 2330,2337,2454
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from services.common.collectors import (
    PriceCollector,
    MarginCollector,
    InstitutionalCollector,
    LendingCollector
)
from services.common.utils.date_helper import is_trading_day

# 可用的收集器對應表
COLLECTORS = {
    'price': PriceCollector,
    'margin': MarginCollector,
    'institutional': InstitutionalCollector,
    'lending': LendingCollector,
}


def backfill_single_date(date: str, data_types: list = None, stock_ids: list = None, skip_trading_day_check: bool = False):
    """
    回補單一日期的資料

    Args:
        date: 日期 (YYYY-MM-DD)
        data_types: 資料類型列表 (預設所有類型)
        stock_ids: 股票代碼列表（選用，用於篩選特定股票，僅 price 支援）
        skip_trading_day_check: 是否跳過交易日檢查
    """
    # 預設收集所有類型
    if data_types is None:
        data_types = ['price', 'margin', 'institutional', 'lending']

    print(f"\n{'='*70}")
    print(f"回補日期: {date}")
    print(f"資料類型: {', '.join(data_types)}")
    if stock_ids:
        print(f"股票代碼: {', '.join(stock_ids)} ({len(stock_ids)} 支)")
    print(f"{'='*70}\n")

    # 檢查是否為交易日（可選）
    if not skip_trading_day_check and not is_trading_day(date):
        print(f"⚠️  警告: {date} 可能不是交易日")
        response = input("是否仍要繼續？ (y/N): ")
        if response.lower() != 'y':
            print("已取消")
            return False

    # 開始回補
    start_time = datetime.now()
    date_success = True
    date_records = 0

    # 依序收集各類型資料
    for data_type in data_types:
        print(f"\n[{data_type.upper()}] 開始收集...")

        try:
            # 建立收集器
            collector_class = COLLECTORS.get(data_type)
            if not collector_class:
                print(f"❌ {data_type}: 不支援的資料類型")
                date_success = False
                continue

            collector = collector_class(date)

            # 執行收集（會自動驗證和產生 MD5）
            result = collector.run(enable_validation=True)

            # 統計結果
            if result['status'] == 'success':
                records = result.get('records', 0)
                date_records += records
                print(f"✅ {data_type}: {records} 筆")

                # 顯示驗證結果
                if 'validation' in result:
                    val = result['validation']
                    print(f"   驗證: {val.get('status')} ({val.get('grade')}, {val.get('accuracy', 0):.1f}%)")
            elif result['status'] == 'no_data':
                print(f"⚠️  {data_type}: 無資料")
            else:
                print(f"❌ {data_type}: {result.get('error')}")
                date_success = False

        except Exception as e:
            print(f"❌ {data_type}: 例外錯誤 - {e}")
            date_success = False

    elapsed = (datetime.now() - start_time).total_seconds()

    if date_success:
        print(f"\n✅ {date} 完成 - 共 {date_records} 筆記錄，耗時 {elapsed:.1f} 秒")
    else:
        print(f"\n⚠️  {date} 部分失敗 - 共 {date_records} 筆記錄，耗時 {elapsed:.1f} 秒")

    return date_success


def main():
    parser = argparse.ArgumentParser(
        description='歷史資料回補腳本（使用 MI_INDEX API）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--date',
        type=str,
        help='回補單一日期 (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--start',
        type=str,
        help='回補起始日期 (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--end',
        type=str,
        help='回補結束日期 (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--types',
        nargs='+',
        choices=list(COLLECTORS.keys()),
        default=None,
        help='要收集的資料類型（可指定多個，預設全部）'
    )
    parser.add_argument(
        '--stocks',
        type=str,
        help='指定股票代碼，用逗號分隔 (例如: 2330,2337,2454，僅 price 支援)'
    )
    parser.add_argument(
        '--skip-trading-day-check',
        action='store_true',
        help='跳過交易日檢查'
    )
    parser.add_argument(
        '--yes', '-y',
        action='store_true',
        help='自動確認，不詢問'
    )

    args = parser.parse_args()

    # 解析資料類型
    data_types = args.types if args.types else None

    # 解析股票代碼
    stock_ids = None
    if args.stocks:
        stock_ids = [s.strip() for s in args.stocks.split(',')]

    # 單一日期回補
    if args.date:
        success = backfill_single_date(args.date, data_types, stock_ids, args.skip_trading_day_check)
        return 0 if success else 1

    # 日期範圍回補
    if args.start and args.end:
        start = datetime.strptime(args.start, '%Y-%m-%d')
        end = datetime.strptime(args.end, '%Y-%m-%d')

        dates = []
        current = start
        while current <= end:
            dates.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)

        print(f"\n{'='*70}")
        print(f"批次回補")
        print(f"{'='*70}")
        print(f"日期範圍: {args.start} ~ {args.end} ({len(dates)} 天)")
        if data_types:
            print(f"資料類型: {', '.join(data_types)}")
        else:
            print(f"資料類型: 全部")
        if stock_ids:
            print(f"股票數量: {len(stock_ids)} 支")
        print(f"預估時間: {len(dates) * 5:.0f} 秒 (每天約 2-3 秒)")
        print(f"{'='*70}\n")

        if not args.yes:
            response = input("確定要執行批次回補嗎？ (y/N): ")
            if response.lower() != 'y':
                print("已取消")
                return 1

        success_count = 0
        for date in dates:
            if backfill_single_date(date, data_types, stock_ids, args.skip_trading_day_check):
                success_count += 1

        print(f"\n{'='*70}")
        print(f"批次回補完成")
        print(f"成功: {success_count}/{len(dates)} 天")
        print(f"{'='*70}")

        return 0 if success_count == len(dates) else 1

    # 沒有指定參數
    parser.print_help()
    return 1


if __name__ == '__main__':
    sys.exit(main())
