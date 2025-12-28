#!/usr/bin/env python3
"""
測試 TPEx 實際使用的 API 端點

根據網頁分析，TPEx 使用 /api/ 路徑而非 /openapi/v1/
"""

import requests
import json
from datetime import datetime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def test_tpex_api(endpoint_name, url, params=None):
    """測試 TPEx API 端點"""
    print(f"\n{'='*70}")
    print(f"測試: {endpoint_name}")
    print(f"URL: {url}")
    if params:
        print(f"參數: {params}")
    print('='*70)

    try:
        response = requests.get(url, params=params, timeout=30, verify=False)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")

        # 顯示前 200 字元
        print(f"\n前 200 字元:")
        print(response.text[:200])

        # 嘗試解析 JSON
        try:
            data = response.json()
            print(f"\n✅ JSON 解析成功")
            print(f"資料類型: {type(data)}")

            if isinstance(data, dict):
                print(f"Keys: {list(data.keys())}")
                # 檢查是否有 iTotalRecords
                if 'iTotalRecords' in data:
                    print(f"總筆數: {data['iTotalRecords']}")
                if 'aaData' in data:
                    print(f"資料筆數: {len(data['aaData'])}")
                    if len(data['aaData']) > 0:
                        print(f"\n第一筆資料:")
                        print(json.dumps(data['aaData'][0], ensure_ascii=False, indent=2))
            elif isinstance(data, list):
                print(f"陣列長度: {len(data)}")
                if len(data) > 0:
                    print(f"\n第一筆資料:")
                    print(json.dumps(data[0], ensure_ascii=False, indent=2))

        except json.JSONDecodeError as e:
            print(f"\n❌ JSON 解析失敗: {e}")

    except Exception as e:
        print(f"\n❌ 請求失敗: {e}")


def main():
    """測試 TPEx 各種 API 端點"""

    print("="*70)
    print("TPEx 實際 API 端點測試")
    print("="*70)

    # 1. 測試融資融券 API（使用 /api/ 路徑）
    test_tpex_api(
        "融資融券 - /api/ 路徑",
        "https://www.tpex.org.tw/api/margin/sbl"
    )

    # 2. 嘗試帶日期參數
    today = datetime.now()
    date_roc = f"{today.year - 1911}/{today.month:02d}/{today.day:02d}"  # 民國年格式

    test_tpex_api(
        "融資融券 - 帶日期參數（民國年）",
        "https://www.tpex.org.tw/api/margin/sbl",
        params={'d': date_roc}
    )

    # 3. 測試其他可能的融資融券端點
    endpoints = [
        ("融資融券餘額", "https://www.tpex.org.tw/api/margin_balance"),
        ("每日融資融券", "https://www.tpex.org.tw/api/daily_margin"),
        ("信用交易", "https://www.tpex.org.tw/api/credit_trading"),
        ("融資融券 - 舊路徑", "https://www.tpex.org.tw/web/stock/margin_trading/margin_sbl/margin_sbl_result.php"),
    ]

    for name, url in endpoints:
        test_tpex_api(name, url)

    # 4. 測試行情 API（我們已知可用）
    test_tpex_api(
        "行情資料 - /openapi/v1/",
        "https://www.tpex.org.tw/openapi/v1/tpex_mainboard_quotes"
    )

    print("\n" + "="*70)
    print("測試完成！")
    print("="*70)


if __name__ == '__main__':
    main()
