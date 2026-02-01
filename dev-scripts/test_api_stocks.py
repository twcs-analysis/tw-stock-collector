#!/usr/bin/env python3
"""
測試 FinMind API 對特定股票的資料是否可用
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from FinMind.data import DataLoader

def test_stock(dl, stock_id, stock_name, date):
    """測試單一股票"""
    print(f"測試 {stock_id} ({stock_name}):")
    try:
        df = dl.taiwan_stock_daily(
            stock_id=stock_id,
            start_date=date,
            end_date=date
        )

        if df is None or df.empty:
            print(f"  ❌ 無資料")
            return False
        else:
            print(f"  ✅ 有資料: {len(df)} 筆")
            print(f"     收盤價: {df['close'].values[0]}, 成交量: {df['Trading_Volume'].values[0]}")
            return True
    except Exception as e:
        print(f"  ❌ 錯誤: {e}")
        return False

def main():
    dl = DataLoader()
    date = '2025-12-26'

    print(f"測試日期: {date}")
    print("=" * 70)

    # 測試有問題的營建股
    print("\n營建股:")
    test_stock(dl, '2528', '皇普', date)
    test_stock(dl, '2539', '櫻花建', date)

    # 測試有資料的營建股
    print("\n其他營建股:")
    test_stock(dl, '2501', '國建', date)
    test_stock(dl, '2504', '國產', date)

    # 測試台積電作為對照
    print("\n對照組 (台積電):")
    test_stock(dl, '2330', '台積電', date)

    print("\n" + "=" * 70)
    print("測試完成")

if __name__ == '__main__':
    main()
