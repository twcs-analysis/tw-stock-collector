#!/usr/bin/env python3
"""
從證交所網站抓取股票清單（不需要 API token）
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import requests
from datetime import datetime

def fetch_twse_stocks():
    """抓取上市股票"""
    print("正在從證交所抓取上市股票清單...")
    url = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2"
    response = requests.get(url)
    response.encoding = 'big5'

    stocks = []
    lines = response.text.split('\n')

    for line in lines:
        if '股票' in line and '<td>' in line:
            parts = line.split('<td>')
            if len(parts) >= 3:
                code_name = parts[1].replace('</td>', '').strip()

                if '\u3000' in code_name:
                    code, name = code_name.split('\u3000', 1)
                    code = code.strip()
                    name = name.strip()

                    if len(code) == 4 and code.isdigit():
                        stocks.append({
                            'stock_id': code,
                            'stock_name': name,
                            'type': 'twse',
                            'industry_category': '未分類',
                            'date': datetime.now().strftime('%Y-%m-%d'),
                            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })

    print(f"  上市股票: {len(stocks)} 檔")
    return stocks

def fetch_tpex_stocks():
    """抓取上櫃股票"""
    print("正在從證交所抓取上櫃股票清單...")
    url = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=4"
    response = requests.get(url)
    response.encoding = 'big5'

    stocks = []
    lines = response.text.split('\n')

    for line in lines:
        if '股票' in line and '<td>' in line:
            parts = line.split('<td>')
            if len(parts) >= 3:
                code_name = parts[1].replace('</td>', '').strip()

                if '\u3000' in code_name:
                    code, name = code_name.split('\u3000', 1)
                    code = code.strip()
                    name = name.strip()

                    if len(code) == 4 and code.isdigit():
                        stocks.append({
                            'stock_id': code,
                            'stock_name': name,
                            'type': 'tpex',
                            'industry_category': '未分類',
                            'date': datetime.now().strftime('%Y-%m-%d'),
                            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })

    print(f"  上櫃股票: {len(stocks)} 檔")
    return stocks

if __name__ == "__main__":
    print("=" * 70)
    print("從證交所抓取股票清單")
    print("=" * 70)

    # 抓取上市上櫃股票
    twse_stocks = fetch_twse_stocks()
    tpex_stocks = fetch_tpex_stocks()

    # 合併
    all_stocks = twse_stocks + tpex_stocks
    df = pd.DataFrame(all_stocks)

    print("\n" + "=" * 70)
    print(f"總計: {len(df)} 檔股票")
    print(f"  上市 (twse): {len(df[df['type']=='twse'])} 檔")
    print(f"  上櫃 (tpex): {len(df[df['type']=='tpex'])} 檔")
    print("=" * 70)

    # 儲存
    output_file = Path(__file__).parent.parent / 'data' / 'stock_list.csv'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False, encoding='utf-8-sig')

    print(f"\n✅ 已儲存到: {output_file}")
    print(f"\n前 10 檔股票:")
    print(df.head(10)[['stock_id', 'stock_name', 'type']])
