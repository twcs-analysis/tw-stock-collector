"""
測試 TWSE/TPEx 三大法人 API 端點
"""

import requests
import json
from urllib3.exceptions import InsecureRequestWarning
import urllib3

urllib3.disable_warnings(InsecureRequestWarning)

def test_twse_endpoints():
    """測試 TWSE 可能的三大法人端點"""

    base_url = "https://openapi.twse.com.tw/v1"

    # 可能的端點列表（根據證交所網站和常見命名）
    endpoints = [
        "/fund/T86",  # 原始計畫
        "/exchangeReport/FMSRFK",  # 外資及陸資買賣超彙總表
        "/exchangeReport/BFI82U",  # 自營商買賣超彙總表
        "/exchangeReport/T86",  # 可能的三大法人
        "/fund/BFI82U",
        "/fund/FMSRFK",
    ]

    print("=" * 60)
    print("測試 TWSE 三大法人 API 端點")
    print("=" * 60)

    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n測試: {url}")

        try:
            response = requests.get(url, timeout=10, verify=False)
            print(f"狀態碼: {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        print(f"✅ 成功！資料筆數: {len(data)}")
                        print(f"第一筆資料: {json.dumps(data[0], ensure_ascii=False, indent=2)}")
                        return url, data
                    elif isinstance(data, dict):
                        print(f"✅ 成功！資料格式: dict")
                        print(f"鍵值: {list(data.keys())}")
                        print(f"資料: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}")
                        return url, data
                    else:
                        print(f"⚠️  回傳空資料或格式異常")
                except json.JSONDecodeError:
                    content = response.text[:200]
                    if "404" in content or "not found" in content.lower():
                        print(f"❌ 404 錯誤頁面")
                    else:
                        print(f"❌ 非 JSON 格式: {content}")
            else:
                print(f"❌ HTTP {response.status_code}")

        except Exception as e:
            print(f"❌ 錯誤: {e}")

    print("\n" + "=" * 60)
    print("結論: 未找到可用的 TWSE 三大法人端點")
    print("=" * 60)
    return None, None


def test_tpex_web_endpoints():
    """測試 TPEx /web/stock/ 路徑（根據融資融券成功經驗）"""

    base_url = "https://www.tpex.org.tw/web/stock"

    # 根據融資融券的成功模式，推測可能的路徑
    endpoints = [
        "/aftertrading/dealer_trading/dealer_trad_result.php",  # 三大法人
        "/aftertrading/institutional/institutional_result.php",
        "/institutional_trading/institutional_trad_result.php",
        "/dealer_trading/dealer_trad_result.php",
    ]

    print("\n" + "=" * 60)
    print("測試 TPEx 三大法人 API 端點 (/web/stock/ 路徑)")
    print("=" * 60)

    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n測試: {url}")

        try:
            response = requests.get(url, timeout=10, verify=False)
            print(f"狀態碼: {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()

                    # TPEx 特有的 {tables: [{fields, data}]} 格式
                    if isinstance(data, dict) and 'tables' in data:
                        tables = data.get('tables', [])
                        if len(tables) > 0:
                            table = tables[0]
                            fields = table.get('fields', [])
                            rows = table.get('data', [])
                            print(f"✅ 成功！TPEx 格式")
                            print(f"欄位: {fields}")
                            print(f"資料筆數: {len(rows)}")
                            if rows:
                                print(f"第一筆: {rows[0]}")
                            return url, data
                    else:
                        print(f"資料格式: {json.dumps(data, ensure_ascii=False, indent=2)[:300]}")

                except json.JSONDecodeError:
                    print(f"❌ 非 JSON 格式")
            else:
                print(f"❌ HTTP {response.status_code}")

        except Exception as e:
            print(f"❌ 錯誤: {e}")

    print("\n" + "=" * 60)
    print("需要使用瀏覽器 DevTools 找出正確的 TPEx 端點")
    print("=" * 60)
    return None, None


if __name__ == "__main__":
    # 測試 TWSE
    twse_url, twse_data = test_twse_endpoints()

    # 測試 TPEx
    tpex_url, tpex_data = test_tpex_web_endpoints()

    # 總結
    print("\n" + "=" * 60)
    print("測試總結")
    print("=" * 60)

    if twse_url:
        print(f"✅ TWSE 三大法人 API: {twse_url}")
    else:
        print("❌ TWSE: 未找到可用端點")
        print("   建議: 瀏覽 https://www.twse.com.tw/ 使用 DevTools 找出實際端點")

    if tpex_url:
        print(f"✅ TPEx 三大法人 API: {tpex_url}")
    else:
        print("❌ TPEx: 未找到可用端點")
        print("   建議: 瀏覽 https://www.tpex.org.tw/ 使用 DevTools 找出實際端點")
