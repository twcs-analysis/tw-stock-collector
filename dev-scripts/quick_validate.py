#!/usr/bin/env python3
"""
快速驗證腳本 - 檢查資料欄位
"""

import json
import sys
from pathlib import Path

def validate_price_data(file_path):
    """驗證 price 資料"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    required_fields = ['date', 'stock_id', 'stock_name', 'open', 'high', 'low', 'close', 'volume', 'type']

    if 'data' not in data or len(data['data']) == 0:
        print(f"❌ 無資料")
        return False

    # 檢查第一筆資料
    first_record = data['data'][0]
    missing_fields = [f for f in required_fields if f not in first_record]

    if missing_fields:
        print(f"❌ 缺少必要欄位: {', '.join(missing_fields)}")
        return False

    print(f"✅ 所有必要欄位完整")
    print(f"   總筆數: {len(data['data'])}")
    return True

def validate_margin_data(file_path):
    """驗證 margin 資料"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    required_fields = ['date', 'stock_id', 'stock_name', 'margin_balance', 'margin_change', 'short_balance', 'short_change', 'type']

    if 'data' not in data or len(data['data']) == 0:
        print(f"❌ 無資料")
        return False

    # 檢查第一筆資料
    first_record = data['data'][0]
    missing_fields = [f for f in required_fields if f not in first_record]

    if missing_fields:
        print(f"❌ 缺少必要欄位: {', '.join(missing_fields)}")
        print(f"   實際欄位: {', '.join(first_record.keys())}")
        return False

    print(f"✅ 所有必要欄位完整")
    print(f"   總筆數: {len(data['data'])}")
    return True

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法: python scripts/quick_validate.py <type> <file_path>")
        sys.exit(1)

    data_type = sys.argv[1]
    file_path = sys.argv[2]

    print(f"\n驗證 {data_type} 資料: {file_path}")

    if data_type == 'price':
        result = validate_price_data(file_path)
    elif data_type == 'margin':
        result = validate_margin_data(file_path)
    else:
        print(f"不支援的資料類型: {data_type}")
        sys.exit(1)

    sys.exit(0 if result else 1)
