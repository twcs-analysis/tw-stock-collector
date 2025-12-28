#!/usr/bin/env python3
"""
建立台股上市上櫃股票清單
從證交所 OpenAPI 抓取完整股票清單
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import requests
from datetime import datetime
import time

def fetch_twse_stocks():
    """
    從證交所 OpenAPI 抓取上市股票清單
    API: https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL
    """
    print("正在從證交所 OpenAPI 抓取上市股票清單...")

    try:
        # 使用證交所 OpenAPI (當日所有股票成交資訊)
        url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        data = response.json()
        stocks = []

        for item in data:
            code = item.get('Code', '').strip()
            name = item.get('Name', '').strip()

            # 只保留 4 位數的股票代碼（排除 ETF、權證等）
            if len(code) == 4 and code.isdigit():
                stocks.append({
                    'stock_id': code,
                    'stock_name': name,
                    'type': 'twse',
                    'industry_category': '上市',
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

        print(f"  上市股票: {len(stocks)} 檔")
        return stocks

    except Exception as e:
        print(f"  ❌ 錯誤: {e}")
        return []

def fetch_tpex_stocks():
    """
    從櫃買中心抓取上櫃股票清單
    API: https://www.tpex.org.tw/openapi/v1/tpex_mainboard_quotes
    """
    print("正在從櫃買中心 OpenAPI 抓取上櫃股票清單...")

    try:
        url = "https://www.tpex.org.tw/openapi/v1/tpex_mainboard_quotes"
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        data = response.json()
        stocks = []

        for item in data:
            code = item.get('SecuritiesCompanyCode', '').strip()
            name = item.get('CompanyName', '').strip()

            # 只保留 4 位數的股票代碼
            if len(code) == 4 and code.isdigit():
                stocks.append({
                    'stock_id': code,
                    'stock_name': name,
                    'type': 'tpex',
                    'industry_category': '上櫃',
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

        print(f"  上櫃股票: {len(stocks)} 檔")
        return stocks

    except Exception as e:
        print(f"  ❌ 錯誤: {e}")
        return []

def save_stock_list(stocks, output_dir):
    """儲存股票清單"""
    if not stocks:
        print("❌ 沒有股票資料")
        return False

    df = pd.DataFrame(stocks)

    # 按股票代碼排序
    df = df.sort_values('stock_id')

    # 儲存到指定目錄
    output_path = Path(output_dir) / 'stock_list_reference.csv'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')

    print(f"\n✅ 已儲存到: {output_path}")
    print(f"   總計: {len(df)} 檔股票")
    print(f"   上市: {len(df[df['type']=='twse'])} 檔")
    print(f"   上櫃: {len(df[df['type']=='tpex'])} 檔")

    # 顯示前 10 筆
    print(f"\n前 10 檔股票:")
    print(df.head(10)[['stock_id', 'stock_name', 'type']].to_string(index=False))

    return True

if __name__ == "__main__":
    print("=" * 70)
    print("建立台股上市上櫃股票清單")
    print("=" * 70)
    print()

    # 抓取上市股票
    twse_stocks = fetch_twse_stocks()
    time.sleep(1)  # 避免請求太頻繁

    # 抓取上櫃股票
    tpex_stocks = fetch_tpex_stocks()

    # 合併
    all_stocks = twse_stocks + tpex_stocks

    if all_stocks:
        print("\n" + "=" * 70)
        print(f"總計抓取: {len(all_stocks)} 檔股票")
        print("=" * 70)

        # 儲存到 data/reference 目錄
        output_dir = Path(__file__).parent.parent / 'data' / 'reference'
        save_stock_list(all_stocks, output_dir)
    else:
        print("\n❌ 無法抓取股票清單")
        sys.exit(1)
