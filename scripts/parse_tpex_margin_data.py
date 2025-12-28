#!/usr/bin/env python3
"""
解析 TPEx 融資融券 API 回傳的資料格式
"""

import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# TPEx 融資融券 API
url = "https://www.tpex.org.tw/web/stock/margin_trading/margin_sbl/margin_sbl_result.php"

print("="*70)
print("解析 TPEx 融資融券 API 資料")
print("="*70)

response = requests.get(url, timeout=30, verify=False)
data = response.json()

print(f"\nJSON 結構:")
print(f"Keys: {list(data.keys())}")
print(f"\ndate: {data.get('date')}")
print(f"stat: {data.get('stat')}")

if 'tables' in data and len(data['tables']) > 0:
    table = data['tables'][0]
    print(f"\nTable info:")
    print(f"  title: {table.get('title')}")
    print(f"  date: {table.get('date')}")
    print(f"  totalCount: {table.get('totalCount')}")
    print(f"  fields: {table.get('fields')}")

    if 'data' in table and len(table['data']) > 0:
        print(f"\n  data 筆數: {len(table['data'])}")
        print(f"\n  前 3 筆資料:")
        for i, row in enumerate(table['data'][:3]):
            print(f"\n  #{i+1}: {row}")

        # 顯示欄位對照
        fields = table.get('fields', [])
        print(f"\n欄位對照表（共 {len(fields)} 個欄位）:")
        for i, field in enumerate(fields):
            if len(table['data']) > 0:
                sample_value = table['data'][0][i] if i < len(table['data'][0]) else 'N/A'
                print(f"  [{i}] {field} = {sample_value}")

print("\n" + "="*70)
