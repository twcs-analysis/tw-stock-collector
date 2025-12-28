#!/usr/bin/env python3
"""
統一資料收集腳本

使用方式:
    python scripts/run_collection.py --date 2024-12-27 --types price margin institutional lending
    python scripts/run_collection.py --date 2024-12-27  # 收集所有類型
    python scripts/run_collection.py  # 使用最近交易日，收集所有類型
"""

import sys
import os
import argparse
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.collectors import (
    PriceCollector,
    MarginCollector,
    InstitutionalCollector,
    LendingCollector
)
from src.utils import is_trading_day, get_latest_trading_day


# 可用的收集器對應表
COLLECTORS = {
    'price': PriceCollector,
    'margin': MarginCollector,
    'institutional': InstitutionalCollector,
    'lending': LendingCollector,
}


def parse_args():
    """解析命令列參數"""
    parser = argparse.ArgumentParser(
        description='台股資料收集統一執行腳本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  # 收集指定日期的所有資料
  python scripts/run_collection.py --date 2024-12-27

  # 只收集價格和融資融券資料
  python scripts/run_collection.py --date 2024-12-27 --types price margin

  # 使用最近交易日
  python scripts/run_collection.py
        """
    )

    parser.add_argument(
        '--date',
        type=str,
        help='收集日期 (YYYY-MM-DD)，不指定則使用最近交易日'
    )

    parser.add_argument(
        '--types',
        nargs='+',
        choices=list(COLLECTORS.keys()),
        help='要收集的資料類型（可指定多個），不指定則收集所有類型'
    )

    parser.add_argument(
        '--skip-trading-day-check',
        action='store_true',
        help='跳過交易日檢查（適用於測試或補資料）'
    )

    parser.add_argument(
        '--no-validation',
        action='store_true',
        help='跳過資料驗證（預設會進行驗證）'
    )

    return parser.parse_args()


def main():
    """主程式"""
    args = parse_args()

    # 決定收集日期
    if args.date:
        date = args.date
    else:
        date = get_latest_trading_day()
        print(f"未指定日期，使用最近交易日: {date}")

    # 檢查是否為交易日
    if not args.skip_trading_day_check:
        if not is_trading_day(date):
            print(f"⚠️  警告: {date} 不是交易日（週末或國定假日）")
            response = input("是否繼續收集? (y/N): ")
            if response.lower() != 'y':
                print("已取消收集")
                return 1

    # 決定收集類型
    if args.types:
        types_to_collect = args.types
    else:
        types_to_collect = list(COLLECTORS.keys())

    print("=" * 70)
    print(f"台股資料收集")
    print("=" * 70)
    print(f"日期: {date}")
    print(f"類型: {', '.join(types_to_collect)}")
    print(f"驗證: {'關閉' if args.no_validation else '開啟'}")
    print("=" * 70)
    print()

    # 收集結果統計
    results = {}
    success_count = 0
    no_data_count = 0
    error_count = 0

    # 依序收集各類型資料
    for data_type in types_to_collect:
        print(f"\n[{data_type.upper()}] 開始收集")
        print("-" * 70)

        try:
            # 建立收集器
            collector_class = COLLECTORS[data_type]
            collector = collector_class(date)

            # 執行收集（包含驗證）
            enable_validation = not args.no_validation
            result = collector.run(enable_validation=enable_validation)

            # 記錄結果
            results[data_type] = result

            # 統計
            if result['status'] == 'success':
                success_count += 1
                print(f"✅ 成功: {result.get('records')} 筆資料")
                print(f"   檔案: {result.get('file')}")

                # 顯示驗證結果
                if 'validation' in result:
                    validation = result['validation']
                    if validation.get('status') == 'PASS':
                        print(f"   驗證: ✅ {validation.get('status')} ({validation.get('grade')}, {validation.get('accuracy'):.1f}%)")
                    elif validation.get('status') == 'WARN':
                        print(f"   驗證: ⚠️  {validation.get('status')} ({validation.get('grade')}, {validation.get('accuracy'):.1f}%)")
                    elif validation.get('status') == 'FAIL':
                        print(f"   驗證: ❌ {validation.get('status')} ({validation.get('grade')}, {validation.get('accuracy'):.1f}%)")
                    elif validation.get('status') == 'error':
                        print(f"   驗證: ❌ 錯誤: {validation.get('error')}")
                    else:
                        print(f"   驗證: ⏭️  {validation.get('message', '已跳過')}")

                    if validation.get('report'):
                        print(f"   報告: {validation.get('report')}")

            elif result['status'] == 'no_data':
                no_data_count += 1
                print(f"⚠️  無資料")
            else:  # error
                error_count += 1
                print(f"❌ 失敗: {result.get('error')}")

        except Exception as e:
            error_count += 1
            results[data_type] = {'status': 'error', 'error': str(e)}
            print(f"❌ 例外錯誤: {e}")

        print("-" * 70)

    # 輸出總結
    print("\n" + "=" * 70)
    print("收集總結")
    print("=" * 70)
    print(f"日期: {date}")
    print(f"總計: {len(types_to_collect)} 種資料類型")
    print(f"  成功: {success_count}")
    print(f"  無資料: {no_data_count}")
    print(f"  失敗: {error_count}")
    print("=" * 70)

    # 詳細結果
    if success_count > 0:
        print("\n成功收集的資料:")
        for data_type, result in results.items():
            if result['status'] == 'success':
                print(f"  - {data_type}: {result.get('records')} 筆")

    if error_count > 0:
        print("\n失敗的資料:")
        for data_type, result in results.items():
            if result['status'] == 'error':
                print(f"  - {data_type}: {result.get('error')}")

    # 回傳狀態碼
    if error_count > 0:
        return 1  # 有錯誤
    elif no_data_count == len(types_to_collect):
        return 2  # 全部無資料
    else:
        return 0  # 成功


if __name__ == '__main__':
    sys.exit(main())
