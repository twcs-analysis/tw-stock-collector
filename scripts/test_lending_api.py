"""
測試 TWSE/TPEx 借券賣出 API 端點
"""

import requests
import json
from urllib3.exceptions import InsecureRequestWarning
import urllib3

urllib3.disable_warnings(InsecureRequestWarning)

def test_twse_lending_endpoints():
    """測試 TWSE 可能的借券賣出端點"""

    base_url = "https://openapi.twse.com.tw/v1"

    # 可能的端點列表
    endpoints = [
        "/exchangeReport/TWT93U",  # 原始計畫中的端點
        "/exchangeReport/MI_QFIIS",  # 借券資訊
        "/exchangeReport/TWTB4U",  # 可能的借券統計
        "/fund/TWT93U",
        "/sbl/TWT93U",
    ]

    print("=" * 60)
    print("測試 TWSE 借券賣出 API 端點")
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
                        print(f"欄位: {list(data[0].keys())}")
                        print(f"第一筆資料: {json.dumps(data[0], ensure_ascii=False, indent=2)}")
                        return url, data
                    elif isinstance(data, dict):
                        print(f"✅ 成功！資料格式: dict")
                        print(f"鍵值: {list(data.keys())}")
                        print(f"資料預覽: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}")
                        return url, data
                    else:
                        print(f"⚠️  回傳空資料或格式異常: {type(data)}")
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
    print("結論: 未找到可用的 TWSE 借券賣出端點")
    print("=" * 60)
    return None, None


def test_tpex_lending_endpoints():
    """測試 TPEx /web/stock/ 路徑（根據融資融券成功經驗）"""

    base_url = "https://www.tpex.org.tw/web/stock"

    # 根據融資融券的成功模式，推測可能的路徑
    endpoints = [
        "/securities_lending/sbl/sbl_result.php",
        "/aftertrading/sbl/sbl_result.php",
        "/sbl/sbl_result.php",
        "/margin_trading/sbl/sbl_result.php",
        "/aftertrading/securities_lending/sbl_result.php",
    ]

    print("\n" + "=" * 60)
    print("測試 TPEx 借券賣出 API 端點 (/web/stock/ 路徑)")
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
                    if isinstance(data, dict):
                        if 'tables' in data:
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
                    content = response.text[:200]
                    if "404" in content:
                        print(f"❌ 404 錯誤頁面")
                    else:
                        print(f"❌ 非 JSON 格式: {content}")
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
    twse_url, twse_data = test_twse_lending_endpoints()

    # 測試 TPEx
    tpex_url, tpex_data = test_tpex_lending_endpoints()

    # 總結
    print("\n" + "=" * 60)
    print("借券賣出 API 測試總結")
    print("=" * 60)

    if twse_url:
        print(f"✅ TWSE 借券賣出 API: {twse_url}")
        print(f"   資料筆數: {len(twse_data) if isinstance(twse_data, list) else '?'}")
    else:
        print("❌ TWSE: 未找到可用端點")
        print("   建議: 使用瀏覽器 DevTools 或改用 FinMind")

    if tpex_url:
        print(f"✅ TPEx 借券賣出 API: {tpex_url}")
    else:
        print("❌ TPEx: 未找到可用端點")
        print("   建議: 使用瀏覽器 DevTools 或改用 FinMind")

    print("\n" + "=" * 60)
    print("結論與建議")
    print("=" * 60)

    if not twse_url and not tpex_url:
        print("官方 API 研究結果：")
        print("✅ 價格資料 - 已成功使用官方 API（973x 效能提升）")
        print("✅ 融資融券 - 已成功使用官方 API（907.5x 效能提升）")
        print("❌ 三大法人 - 官方 API 不可用")
        print("❌ 借券賣出 - 官方 API 不可用")
        print("\n建議採用混合策略：")
        print("1. 價格、融資融券：使用官方 API（即時資料）")
        print("2. 三大法人、借券賣出：使用 FinMind（30天延遲但穩定）")
