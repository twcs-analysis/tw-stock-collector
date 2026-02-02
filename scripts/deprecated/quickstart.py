#!/usr/bin/env python3
"""
快速開始 - 官方 API 使用範例

展示如何使用 PriceCollector 收集台股資料
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.collectors import PriceCollector


def main():
    print("=" * 70)
    print("台股資料收集器 - 快速開始範例")
    print("使用台灣證交所與櫃買中心官方 API")
    print("=" * 70)

    # 1. 建立收集器
    print("\n1️⃣ 建立 PriceCollector...")
    collector = PriceCollector(timeout=30)
    print("   ✅ 收集器已初始化")

    # 2. 收集所有股票資料
    print("\n2️⃣ 收集今日所有股票資料...")
    date = '2025-12-26'  # 可改為實際日期
    df = collector.collect(date)

    if not df.empty:
        print(f"   ✅ 成功收集 {len(df)} 檔股票")
        print(f"   📊 上市 (TWSE): {len(df[df['type'] == 'twse'])} 檔")
        print(f"   📊 上櫃 (TPEx): {len(df[df['type'] == 'tpex'])} 檔")

        # 顯示前 3 筆
        print("\n   前 3 筆資料:")
        for _, row in df.head(3).iterrows():
            print(f"   - {row['stock_id']} ({row['stock_name']}): "
                  f"收盤 {row['close']}, 成交量 {row['volume']:,.0f}")
    else:
        print("   ❌ 無資料")
        return 1

    # 3. 查詢特定股票
    print("\n3️⃣ 查詢台積電 (2330)...")
    tsmc = df[df['stock_id'] == '2330']
    if not tsmc.empty:
        row = tsmc.iloc[0]
        print(f"   ✅ 找到台積電")
        print(f"   📈 開盤: {row['open']}")
        print(f"   📈 最高: {row['high']}")
        print(f"   📈 最低: {row['low']}")
        print(f"   📈 收盤: {row['close']}")
        print(f"   📊 成交量: {row['volume']:,.0f}")

    # 4. 儲存資料 (optional)
    print("\n4️⃣ 儲存資料...")
    success = collector.save_data(df, date)
    if success:
        print("   ✅ 資料已儲存到 data/raw/price/")
    else:
        print("   ⚠️  資料儲存失敗（可能目錄不存在）")

    # 5. 統計資訊
    print("\n5️⃣ 統計資訊:")
    stats = collector.get_stats()
    print(f"   API 呼叫次數: {stats['api_calls']}")
    print(f"   成功次數: {stats['success_count']}")

    print("\n" + "=" * 70)
    print("🎉 完成！")
    print("=" * 70)
    print("\n💡 提示:")
    print("   - 無需 API Token（完全免費）")
    print("   - 只需 2 次 API 請求即可取得 1,946 檔股票")
    print("   - 資料即時，無延遲")
    print("   - 更多範例請參考 scripts/test_official_api.py")

    return 0


if __name__ == '__main__':
    sys.exit(main())
