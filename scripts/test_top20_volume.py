#!/usr/bin/env python3
"""
測試成交量前 20 名資料收集器

使用方式:
    python scripts/test_top20_volume.py
    python scripts/test_top20_volume.py --date 2026-01-27
"""

import sys
import os
from pathlib import Path
from datetime import date
import argparse

# 加入專案根目錄到 sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.collectors import Top20VolumeCollector


def main():
    """主程式"""
    parser = argparse.ArgumentParser(description='測試成交量前 20 名資料收集')
    parser.add_argument(
        '--date',
        type=str,
        default=date.today().strftime('%Y-%m-%d'),
        help='收集日期 (YYYY-MM-DD)，預設為今天'
    )
    parser.add_argument(
        '--no-validation',
        action='store_true',
        help='不執行資料驗證'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("成交量前 20 名資料收集測試")
    print("=" * 70)
    print(f"日期: {args.date}")
    print(f"驗證: {'關閉' if args.no_validation else '開啟'}")
    print("=" * 70)
    print()

    # 建立收集器
    collector = Top20VolumeCollector(date=args.date)

    # 執行收集
    result = collector.run(enable_validation=not args.no_validation)

    # 顯示結果
    print()
    print("=" * 70)
    print("收集結果")
    print("=" * 70)

    if result['status'] == 'success':
        print(f"✅ 成功: {result['records']} 筆資料")
        print(f"   檔案: {result['file']}")

        if 'validation' in result:
            val = result['validation']
            print(f"   驗證: {val.get('status', 'N/A')} ({val.get('grade', 'N/A')}, {val.get('accuracy', 0):.1f}%)")
            if 'report' in val:
                print(f"   報告: {val['report']}")

    elif result['status'] == 'no_data':
        print(f"⚠️  無資料: {result.get('message', '可能是非交易日')}")

    else:
        print(f"❌ 失敗: {result.get('error', '未知錯誤')}")

    print("=" * 70)

    return 0 if result['status'] == 'success' else 1


if __name__ == '__main__':
    sys.exit(main())
