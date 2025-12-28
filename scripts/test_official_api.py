#!/usr/bin/env python3
"""
測試台灣證交所與櫃買中心官方 API

驗證是否能取得 2025-12-26 的完整資料
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.datasources import TWSEDataSource, TPExDataSource
from src.utils.data_merger import DataMerger


def main():
    date = '2025-12-26'

    print("=" * 70)
    print(f"測試官方 API - 日期: {date}")
    print("=" * 70)

    # 測試 TWSE（上市股票）
    print("\n【測試 TWSE - 台灣證券交易所（上市）】")
    print("-" * 70)

    twse_source = TWSEDataSource(timeout=30)
    twse_df = twse_source.get_daily_prices(date)

    if not twse_df.empty:
        print(f"✅ TWSE 資料取得成功")
        print(f"   總筆數: {len(twse_df)} 檔")

        # 顯示前 5 筆
        print(f"\n   前 5 檔股票:")
        display_cols = ['stock_id', 'stock_name', 'close', 'volume']
        print(twse_df[display_cols].head().to_string(index=False))

        # 檢查測試股票
        test_stocks = {
            '2330': '台積電',
            '2317': '鴻海',
            '2454': '聯發科'
        }

        print(f"\n   測試特定股票:")
        for stock_id, stock_name in test_stocks.items():
            stock_data = twse_df[twse_df['stock_id'] == stock_id]
            if not stock_data.empty:
                close_price = stock_data.iloc[0]['close']
                volume = stock_data.iloc[0]['volume']
                print(f"   ✅ {stock_id} ({stock_name}): 收盤 {close_price}, 成交量 {volume:,.0f}")
            else:
                print(f"   ❌ {stock_id} ({stock_name}): 找不到資料")
    else:
        print(f"❌ TWSE 資料取得失敗")

    # 測試 TPEx（上櫃股票）
    print("\n【測試 TPEx - 證券櫃買中心（上櫃）】")
    print("-" * 70)

    tpex_source = TPExDataSource(timeout=30)
    tpex_df = tpex_source.get_daily_prices(date)

    if not tpex_df.empty:
        print(f"✅ TPEx 資料取得成功")
        print(f"   總筆數: {len(tpex_df)} 檔")

        # 顯示前 5 筆
        print(f"\n   前 5 檔股票:")
        display_cols = ['stock_id', 'stock_name', 'close', 'volume']
        print(tpex_df[display_cols].head().to_string(index=False))

        # 檢查測試股票（營建股）
        test_stocks = {
            '2528': '皇普',
            '2539': '櫻花建'
        }

        print(f"\n   測試特定股票:")
        for stock_id, stock_name in test_stocks.items():
            stock_data = tpex_df[tpex_df['stock_id'] == stock_id]
            if not stock_data.empty:
                close_price = stock_data.iloc[0]['close']
                volume = stock_data.iloc[0]['volume']
                print(f"   ✅ {stock_id} ({stock_name}): 收盤 {close_price}, 成交量 {volume:,.0f}")
            else:
                print(f"   ❌ {stock_id} ({stock_name}): 找不到資料")
    else:
        print(f"❌ TPEx 資料取得失敗")

    # 合併測試
    print("\n【測試資料合併】")
    print("-" * 70)

    merger = DataMerger()
    merged_df = merger.merge_dataframes([twse_df, tpex_df])

    if not merged_df.empty:
        print(f"✅ 資料合併成功")
        print(f"   合併總筆數: {len(merged_df)} 檔")
        print(f"   上市 (TWSE): {len(merged_df[merged_df['type'] == 'twse'])} 檔")
        print(f"   上櫃 (TPEx): {len(merged_df[merged_df['type'] == 'tpex'])} 檔")

        # 驗證所有測試股票
        all_test_stocks = {
            '2330': '台積電（上市）',
            '2528': '皇普（上櫃）',
            '2539': '櫻花建（上市）'
        }

        print(f"\n   完整測試股票驗證:")
        for stock_id, stock_name in all_test_stocks.items():
            stock_data = merged_df[merged_df['stock_id'] == stock_id]
            if not stock_data.empty:
                close_price = stock_data.iloc[0]['close']
                volume = stock_data.iloc[0]['volume']
                market_type = stock_data.iloc[0]['type']
                print(f"   ✅ {stock_id} ({stock_name}): 收盤 {close_price}, 成交量 {volume:,.0f} [{market_type}]")
            else:
                print(f"   ❌ {stock_id} ({stock_name}): 找不到資料")

    else:
        print(f"❌ 資料合併失敗")

    # 總結
    print("\n" + "=" * 70)
    print("測試總結")
    print("=" * 70)

    twse_ok = not twse_df.empty
    tpex_ok = not tpex_df.empty
    merge_ok = not merged_df.empty

    print(f"TWSE (上市): {'✅ 成功' if twse_ok else '❌ 失敗'} ({len(twse_df) if twse_ok else 0} 檔)")
    print(f"TPEx (上櫃): {'✅ 成功' if tpex_ok else '❌ 失敗'} ({len(tpex_df) if tpex_ok else 0} 檔)")
    print(f"資料合併:    {'✅ 成功' if merge_ok else '❌ 失敗'} ({len(merged_df) if merge_ok else 0} 檔)")

    if twse_ok and tpex_ok and merge_ok:
        print(f"\n🎉 所有測試通過！可以取得 {date} 的完整台股資料！")
        return 0
    else:
        print(f"\n⚠️  部分測試失敗，請檢查 API 狀態")
        return 1


if __name__ == '__main__':
    sys.exit(main())
