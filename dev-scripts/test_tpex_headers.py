#!/usr/bin/env python3
"""
測試 TPEx API Headers 問題

比較不同 Headers 組合的效果
"""

import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def test_with_headers(url, headers_name, headers):
    """測試特定 Headers"""
    print(f"\n{'='*70}")
    print(f"測試: {headers_name}")
    print('='*70)
    print(f"Headers: {json.dumps(headers, indent=2, ensure_ascii=False)}")

    try:
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Content-Length: {response.headers.get('Content-Length')}")

        if response.text:
            print(f"\n前 200 字元:")
            print(response.text[:200])

            try:
                data = response.json()
                if isinstance(data, list):
                    print(f"\n✅ 成功！共 {len(data)} 筆資料")
                else:
                    print(f"\n✅ 成功！資料類型: {type(data)}")
            except json.JSONDecodeError:
                print(f"\n❌ JSON 解析失敗")
        else:
            print("\n❌ 回應內容為空")

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")


def main():
    """測試各種 Headers 組合"""
    url = "https://www.tpex.org.tw/openapi/v1/tpex_margintrading_bal"

    print("="*70)
    print("TPEx API Headers 測試")
    print("="*70)
    print(f"測試 URL: {url}\n")

    # 測試 1: 無 Headers
    test_with_headers(url, "無 Headers", {})

    # 測試 2: 基本瀏覽器 Headers
    test_with_headers(url, "基本瀏覽器 Headers", {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })

    # 測試 3: 完整瀏覽器 Headers
    test_with_headers(url, "完整瀏覽器 Headers", {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.tpex.org.tw/',
        'Origin': 'https://www.tpex.org.tw'
    })

    # 測試 4: curl 模擬
    test_with_headers(url, "curl 模擬", {
        'User-Agent': 'curl/7.68.0',
        'Accept': '*/*'
    })

    print("\n" + "="*70)
    print("測試完成！")
    print("="*70)


if __name__ == '__main__':
    main()
