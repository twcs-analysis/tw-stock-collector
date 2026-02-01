"""
測試 PriceCollector
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.collectors import PriceCollector


def main():
    print("=" * 60)
    print("測試 PriceCollector")
    print("=" * 60)

    # 測試收集 2024-12-27 的資料
    date = "2024-12-27"
    print(f"\n收集日期: {date}\n")

    collector = PriceCollector(date)
    result = collector.run()

    print(f"\n執行結果:")
    print(f"  狀態: {result.get('status')}")
    if result['status'] == 'success':
        print(f"  檔案: {result.get('file')}")
        print(f"  筆數: {result.get('records')}")
    elif result['status'] == 'error':
        print(f"  錯誤: {result.get('error')}")

    print("\n" + "=" * 60)
    print("完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
