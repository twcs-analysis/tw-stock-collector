#!/usr/bin/env python3
"""
測試重構後的 PriceCollector

驗證移除 FinMind 後，使用官方 API 的收集器是否正常運作
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.collectors import PriceCollector


def main():
    date = '2025-12-26'

    print("=" * 70)
    print(f"測試重構後的 PriceCollector")
    print(f"日期: {date}")
    print("=" * 70)

    # 測試 1: 初始化收集器
    print("\n【測試 1: 初始化 PriceCollector】")
    print("-" * 70)
    try:
        collector = PriceCollector(timeout=30)
        print("✅ PriceCollector 初始化成功")
    except Exception as e:
        print(f"❌ PriceCollector 初始化失敗: {e}")
        return 1

    # 測試 2: 收集所有股票
    print("\n【測試 2: 收集所有股票】")
    print("-" * 70)
    try:
        df = collector.collect(date, stock_id=None)

        if not df.empty:
            print(f"✅ 資料收集成功")
            print(f"   總筆數: {len(df)} 筆")
            print(f"   上市 (TWSE): {len(df[df['type'] == 'twse'])} 筆")
            print(f"   上櫃 (TPEx): {len(df[df['type'] == 'tpex'])} 筆")

            # 顯示前 5 筆
            print(f"\n   前 5 筆資料:")
            display_cols = ['stock_id', 'stock_name', 'close', 'volume', 'type']
            print(df[display_cols].head().to_string(index=False))
        else:
            print(f"❌ 無資料")
            return 1
    except Exception as e:
        print(f"❌ 收集失敗: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # 測試 3: 收集單一股票
    print("\n【測試 3: 收集單一股票 (2330 台積電)】")
    print("-" * 70)
    try:
        df_single = collector.collect(date, stock_id='2330')

        if not df_single.empty:
            print(f"✅ 資料收集成功")
            row = df_single.iloc[0]
            print(f"   股票代碼: {row['stock_id']}")
            print(f"   股票名稱: {row['stock_name']}")
            print(f"   收盤價: {row['close']}")
            print(f"   成交量: {row['volume']:,.0f}")
            print(f"   市場別: {row['type']}")
        else:
            print(f"❌ 無資料")
            return 1
    except Exception as e:
        print(f"❌ 收集失敗: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # 測試 4: 收集多檔股票
    print("\n【測試 4: 收集多檔股票】")
    print("-" * 70)
    test_stocks = ['2330', '2317', '2454', '2528']
    try:
        df_multiple = collector.collect_multiple_stocks(date, test_stocks)

        if not df_multiple.empty:
            print(f"✅ 資料收集成功")
            print(f"   總筆數: {len(df_multiple)} 筆")

            print(f"\n   收集的股票:")
            for _, row in df_multiple.iterrows():
                print(f"   - {row['stock_id']} ({row['stock_name']}): "
                      f"收盤 {row['close']}, 成交量 {row['volume']:,.0f} [{row['type']}]")
        else:
            print(f"❌ 無資料")
            return 1
    except Exception as e:
        print(f"❌ 收集失敗: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # 測試 5: 檢查統計資訊
    print("\n【測試 5: 統計資訊】")
    print("-" * 70)
    stats = collector.get_stats()
    print(f"API 呼叫次數: {stats['api_calls']}")
    print(f"總記錄數: {stats['total_records']}")
    print(f"成功次數: {stats['success_count']}")
    print(f"失敗次數: {stats['failed_count']}")

    # 總結
    print("\n" + "=" * 70)
    print("測試總結")
    print("=" * 70)
    print("✅ 所有測試通過")
    print(f"✅ 重構成功 - PriceCollector 已改用官方 API")
    print(f"✅ 不再依賴 FinMind")
    print(f"✅ 可收集 {len(df)} 檔股票的資料")

    return 0


if __name__ == '__main__':
    sys.exit(main())
