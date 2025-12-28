"""
測試 voidful 方法的三大法人 API
參考: https://github.com/voidful/tw-institutional-stocker
"""

import requests
import pandas as pd
from datetime import datetime
from urllib3.exceptions import InsecureRequestWarning
import urllib3
import json

urllib3.disable_warnings(InsecureRequestWarning)


def test_twse_t86():
    """
    測試 TWSE T86 三大法人買賣超
    參考: voidful/tw-institutional-stocker/update_all.py
    """
    print("=" * 60)
    print("測試 TWSE T86 三大法人買賣超")
    print("=" * 60)

    # 使用今天的日期
    date = datetime.now()
    datestr = date.strftime('%Y%m%d')

    url = "https://www.twse.com.tw/fund/T86"
    params = {
        "response": "csv",
        "date": datestr,
        "selectType": "ALLBUT0999"
    }

    print(f"\nURL: {url}")
    print(f"參數: {params}")
    print(f"日期: {datestr}")

    try:
        response = requests.get(url, params=params, timeout=20)
        print(f"狀態碼: {response.status_code}")

        if response.status_code == 200:
            # TWSE 使用 Big5 編碼
            response.encoding = 'cp950'
            content = response.text

            print(f"\n前 500 字元:")
            print(content[:500])

            # 解析 CSV
            from io import StringIO

            # 跳過前面的說明行，找到實際資料
            lines = content.split('\n')

            # 尋找包含「證券代號」的行作為開始
            start_idx = None
            for i, line in enumerate(lines):
                if '證券代號' in line or '股票代號' in line:
                    start_idx = i
                    break

            if start_idx is not None:
                # 從找到的位置開始解析
                data_content = '\n'.join(lines[start_idx:])
                df = pd.read_csv(StringIO(data_content))

                print(f"\n✅ 成功解析！")
                print(f"資料筆數: {len(df)}")
                print(f"欄位: {list(df.columns)}")
                print(f"\n前 5 筆資料:")
                print(df.head())

                return url, df
            else:
                print("❌ 找不到資料標題行")
                return None, None
        else:
            print(f"❌ HTTP {response.status_code}")
            return None, None

    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def test_tpex_3itrade():
    """
    測試 TPEx 三大法人買賣超
    參考: voidful/tw-institutional-stocker/update_all.py
    """
    print("\n" + "=" * 60)
    print("測試 TPEx 三大法人買賣超")
    print("=" * 60)

    # 使用今天的日期（民國曆）
    date = datetime.now()
    roc_year = date.year - 1911
    roc_date = f"{roc_year}/{date.month:02d}/{date.day:02d}"

    url = "https://www.tpex.org.tw/web/stock/3insti/daily_trade/3itrade_hedge_result.php"
    params = {
        "d": roc_date,
        "l": "zh-tw",
        "o": "htm",
        "s": "0",
        "se": "EW",
        "t": "D"
    }

    print(f"\nURL: {url}")
    print(f"參數: {params}")
    print(f"日期（民國曆）: {roc_date}")

    try:
        response = requests.get(url, params=params, timeout=20, verify=False)
        print(f"狀態碼: {response.status_code}")

        if response.status_code == 200:
            response.encoding = 'utf-8'

            # 使用 pandas 解析 HTML 表格
            tables = pd.read_html(response.text)

            print(f"\n找到 {len(tables)} 個表格")

            if len(tables) > 0:
                # 通常資料在第一個表格
                df = tables[0]

                print(f"\n✅ 成功解析！")
                print(f"資料筆數: {len(df)}")
                print(f"欄位: {list(df.columns)}")
                print(f"\n前 5 筆資料:")
                print(df.head())

                return url, df
            else:
                print("❌ 未找到表格")
                return None, None
        else:
            print(f"❌ HTTP {response.status_code}")
            return None, None

    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        return None, None


if __name__ == "__main__":
    # 測試 TWSE
    twse_url, twse_df = test_twse_t86()

    # 測試 TPEx
    tpex_url, tpex_df = test_tpex_3itrade()

    # 總結
    print("\n" + "=" * 60)
    print("測試總結")
    print("=" * 60)

    if twse_url:
        print(f"✅ TWSE T86 三大法人: {twse_url}")
        print(f"   資料筆數: {len(twse_df)}")
    else:
        print("❌ TWSE: 測試失敗")

    if tpex_url:
        print(f"✅ TPEx 三大法人: {tpex_url}")
        print(f"   資料筆數: {len(tpex_df)}")
    else:
        print("❌ TPEx: 測試失敗")

    print("\n" + "=" * 60)
    print("參考來源: https://github.com/voidful/tw-institutional-stocker")
    print("=" * 60)
