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

from services.common.datasources import TWSEDataSource, TPExDataSource
from services.common.collectors import PriceCollector
from services.common.utils.date_helper import is_trading_day


def backfill_single_date(date: str, stock_ids: list = None):
    """
    回補單一日期的資料

    Args:
        date: 日期 (YYYY-MM-DD)
        stock_ids: 股票代碼列表（選用，用於篩選特定股票）
    """
    print(f"\n{'='*70}")
    print(f"回補日期: {date}")
    if stock_ids:
        print(f"股票代碼: {', '.join(stock_ids)} ({len(stock_ids)} 支)")
    print(f"{'='*70}\n")

    # 檢查是否為交易日（可選）
    if not is_trading_day(date):
        print(f"⚠️  警告: {date} 可能不是交易日")
        response = input("是否仍要繼續？ (y/N): ")
        if response.lower() != 'y':
            print("已取消")
            return False

    # 建立回補模式的資料源
    print("初始化資料源（回補模式 - MI_INDEX API）...")
    twse = TWSEDataSource(use_backfill_mode=True)
    # TODO: TPExDataSource 尚未實作 backfill 模式
    tpex = TPExDataSource()

    # 開始回補
    print(f"\n開始回補資料...")
    start_time = datetime.now()

    # 回補 TWSE（上市）
    print("回補 TWSE（上市）使用 MI_INDEX API...")
    twse_df = twse.get_daily_prices(date, stock_ids=stock_ids)
    print(f"✅ TWSE: {len(twse_df)} 筆")

    # 回補 TPEx（上櫃）- 使用標準 API（可能只能取得最新資料）
    print("回補 TPEx（上櫃）...")
    tpex_df = tpex.get_daily_prices(date, stock_ids=stock_ids)
    print(f"✅ TPEx: {len(tpex_df)} 筆")

    if twse_df.empty and tpex_df.empty:
        print(f"❌ 無資料: {date}")
        return False

    elapsed = (datetime.now() - start_time).total_seconds()
    total_records = len(twse_df) + len(tpex_df)
    print(f"\n✅ 回補完成: {total_records} 筆資料 ({len(twse_df)} 上市 + {len(tpex_df)} 上櫃)")
    print(f"耗時: {elapsed:.1f} 秒")

    # 儲存資料
    print(f"\n儲存資料...")
    collector = PriceCollector(date=date)

    # 合併 TWSE 和 TPEx 資料
    import pandas as pd
    combined_data = pd.concat([twse_df, tpex_df], ignore_index=True) if not tpex_df.empty else twse_df

    # 轉換為 PriceCollector 的格式（與 collect() 返回格式一致）
    result = {
        'metadata': {
            'date': date,
            'collected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_count': len(combined_data),
            'source': 'TWSE + TPEx Historical Backfill (MI_INDEX API)',
            'mode': 'backfill'
        },
        'data': combined_data.to_dict('records')
    }

    # 儲存
    file_path = collector.save(result)
    print(f"✅ 資料已儲存至: {file_path}")

    return True


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
        '--stocks',
        type=str,
        help='指定股票代碼，用逗號分隔 (例如: 2330,2337,2454)'
    )

    args = parser.parse_args()

    # 解析股票代碼
    stock_ids = None
    if args.stocks:
        stock_ids = [s.strip() for s in args.stocks.split(',')]

    # 單一日期回補
    if args.date:
        success = backfill_single_date(args.date, stock_ids)
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
        if stock_ids:
            print(f"股票數量: {len(stock_ids)} 支")
        print(f"預估時間: {len(dates) * 5:.0f} 秒 (每天約 2-3 秒)")
        print(f"{'='*70}\n")

        response = input("確定要執行批次回補嗎？ (y/N): ")
        if response.lower() != 'y':
            print("已取消")
            return 1

        success_count = 0
        for date in dates:
            if backfill_single_date(date, stock_ids):
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
