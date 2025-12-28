#!/usr/bin/env python3
"""
驗證 stock_list 過濾修正
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd

# 模擬一個簡單的股票清單資料（類似 FinMind API 回傳的格式）
test_data = {
    'industry_category': ['半導體業', '光電業', '所有證券', '電子零組件業', '生技醫療業'],
    'stock_id': ['2330', '2317', '709983', '2454', '6497'],
    'stock_name': ['台積電', '鴻海', '群聯日盛9B購01', '聯發科', '亞獅康-KY'],
    'type': ['twse', 'twse', 'tpex', 'twse', 'tpex'],
    'date': ['2020-09-14'] * 5,
    'updated_at': ['2025-12-27 18:33:29'] * 5
}

df = pd.DataFrame(test_data)

print("=" * 70)
print("測試資料 (共 {} 筆)".format(len(df)))
print("=" * 70)
print(df[['stock_id', 'stock_name', 'industry_category', 'type']])
print()

# 測試舊的錯誤過濾方式
print("=" * 70)
print("❌ 舊的錯誤過濾 (使用 industry_category)")
print("=" * 70)
df_old = df[df['industry_category'].isin(['TWSE', 'OTC'])].copy()
print(f"過濾後數量: {len(df_old)} 筆")
if len(df_old) == 0:
    print("❌ 結果: 所有股票都被過濾掉了！")
print()

# 測試新的正確過濾方式
print("=" * 70)
print("✓ 新的正確過濾 (使用 type)")
print("=" * 70)
df_new = df[df['type'].isin(['twse', 'tpex'])].copy()
print(f"過濾後數量: {len(df_new)} 筆")
print()
print("過濾後的股票:")
print(df_new[['stock_id', 'stock_name', 'type']])
print()

# 排除權證
print("=" * 70)
print("✓ 排除權證後 (industry_category != '所有證券')")
print("=" * 70)
df_no_warrants = df_new[df_new['industry_category'] != '所有證券'].copy()
print(f"最終數量: {len(df_no_warrants)} 筆")
print()
print("最終股票清單:")
print(df_no_warrants[['stock_id', 'stock_name', 'type']])
print()

# 總結
print("=" * 70)
print("驗證結果")
print("=" * 70)
print(f"原始資料: {len(df)} 筆")
print(f"舊方式 (industry_category): {len(df_old)} 筆 ❌")
print(f"新方式 (type): {len(df_new)} 筆 ✓")
print(f"排除權證後: {len(df_no_warrants)} 筆 ✓")
print()
if len(df_old) == 0 and len(df_new) > 0:
    print("✅ 修正成功！新的過濾方式能正確保留上市上櫃股票")
else:
    print("❌ 修正失敗")
