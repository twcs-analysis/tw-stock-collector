#!/usr/bin/env python3
"""
創建測試用的股票清單（不需要 API token）
使用 FinMind 免費 API（不需登入）獲取股票清單
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from FinMind.data import DataLoader

print("正在從 FinMind 免費 API 獲取股票清單...")
print("(不需要 API token)")

dl = DataLoader()

try:
    # 使用免費 API 獲取股票資訊
    df = dl.taiwan_stock_info()

    print(f"\n獲取到 {len(df)} 筆股票資料")

    # 顯示欄位
    print(f"\n欄位: {list(df.columns)}")

    # 顯示前幾筆
    print(f"\n前 5 筆資料:")
    print(df.head())

    # 儲存到檔案
    output_file = Path(__file__).parent.parent / 'data' / 'stock_list.csv'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False, encoding='utf-8-sig')

    print(f"\n✅ 股票清單已儲存到: {output_file}")
    print(f"總計: {len(df)} 筆")

    # 統計
    if 'type' in df.columns:
        print(f"\n市場分類:")
        print(df['type'].value_counts())

    if 'industry_category' in df.columns:
        print(f"\n產業分類 (前 10):")
        print(df['industry_category'].value_counts().head(10))

except Exception as e:
    print(f"\n❌ 錯誤: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
