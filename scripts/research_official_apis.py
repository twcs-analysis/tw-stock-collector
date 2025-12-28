#!/usr/bin/env python3
"""
研究官方 API 端點

測試 TWSE/TPEx 的三大法人、融資融券、借券賣出 API
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
import json
import urllib3

# 停用 SSL 警告（僅用於測試）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_api(name, url):
    """測試 API 端點"""
    print(f"\n{'='*70}")
    print(f"測試: {name}")
    print(f"URL: {url}")
    print('='*70)

    try:
        response = requests.get(url, timeout=30, verify=False)
        response.raise_for_status()

        data = response.json()

        if isinstance(data, list):
            print(f"✅ 成功！共 {len(data)} 筆資料")
            if len(data) > 0:
                print(f"\n第一筆資料:")
                print(json.dumps(data[0], ensure_ascii=False, indent=2))

                if len(data) > 1:
                    print(f"\n欄位列表:")
                    for key in data[0].keys():
                        print(f"  - {key}")
        else:
            print(f"✅ 成功！資料類型: {type(data)}")
            print(json.dumps(data, ensure_ascii=False, indent=2)[:500])

    except requests.exceptions.RequestException as e:
        print(f"❌ 失敗: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析失敗: {e}")
        print(f"HTTP Status: {response.status_code}")
        print(f"回應內容前 500 字元:")
        print(response.text[:500])
    except Exception as e:
        print(f"❌ 未知錯誤: {e}")


def main():
    """測試所有 API"""

    print("=" * 70)
    print("官方 API 端點研究")
    print("=" * 70)

    apis = {
        # TWSE 融資融券
        "TWSE - 融資融券": "https://openapi.twse.com.tw/v1/exchangeReport/MI_MARGN",

        # TWSE 三大法人
        "TWSE - 三大法人買賣超": "https://openapi.twse.com.tw/v1/fund/T86",

        # TWSE 借券賣出
        "TWSE - 借券賣出": "https://openapi.twse.com.tw/v1/exchangeReport/TWT93U",

        # TPEx 融資融券
        "TPEx - 融資融券": "https://www.tpex.org.tw/openapi/v1/tpex_margintrading_bal",

        # TPEx 三大法人
        "TPEx - 三大法人買賣超": "https://www.tpex.org.tw/openapi/v1/tpex_dealer_trading",

        # TPEx 借券賣出
        "TPEx - 借券賣出": "https://www.tpex.org.tw/openapi/v1/tpex_sbl_total",
    }

    for name, url in apis.items():
        test_api(name, url)

    print("\n" + "=" * 70)
    print("測試完成！")
    print("=" * 70)


if __name__ == '__main__':
    main()
