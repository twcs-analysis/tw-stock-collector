"""
收集三大法人資料
使用 voidful 方法的官方 API
"""

import requests
import pandas as pd
from datetime import datetime
import json
import os
from io import StringIO
from urllib3.exceptions import InsecureRequestWarning
import urllib3

urllib3.disable_warnings(InsecureRequestWarning)


def collect_twse_institutional(date_str):
    """
    收集 TWSE 三大法人資料

    Args:
        date_str: 日期字串 YYYY-MM-DD

    Returns:
        DataFrame
    """
    print(f"收集 TWSE 三大法人資料: {date_str}")

    # 轉換日期格式
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    twse_date = date_obj.strftime('%Y%m%d')

    url = "https://www.twse.com.tw/fund/T86"
    params = {
        "response": "csv",
        "date": twse_date,
        "selectType": "ALLBUT0999"
    }

    try:
        response = requests.get(url, params=params, timeout=20)
        response.encoding = 'cp950'

        if response.status_code != 200:
            print(f"❌ HTTP {response.status_code}")
            return pd.DataFrame()

        # 解析 CSV
        lines = response.text.split('\n')

        # 找到標題行
        start_idx = None
        for i, line in enumerate(lines):
            if '證券代號' in line or '股票代號' in line:
                start_idx = i
                break

        if start_idx is None:
            print("❌ 找不到資料標題行")
            return pd.DataFrame()

        # 從標題行開始解析
        data_content = '\n'.join(lines[start_idx:])
        df = pd.read_csv(StringIO(data_content))

        # 加入日期和類型
        df['date'] = date_str
        df['type'] = 'twse'

        # 只保留 4 位數字的股票代碼
        if '證券代號' in df.columns:
            df = df[df['證券代號'].str.len() == 4]
            df = df[df['證券代號'].str.isdigit()]

        print(f"✅ TWSE: {len(df)} 筆")
        return df

    except Exception as e:
        print(f"❌ TWSE 錯誤: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()


def collect_tpex_institutional(date_str):
    """
    收集 TPEx 三大法人資料

    Args:
        date_str: 日期字串 YYYY-MM-DD

    Returns:
        DataFrame
    """
    print(f"收集 TPEx 三大法人資料: {date_str}")

    # 轉換為民國曆
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    roc_year = date_obj.year - 1911
    roc_date = f"{roc_year}/{date_obj.month:02d}/{date_obj.day:02d}"

    url = "https://www.tpex.org.tw/web/stock/3insti/daily_trade/3itrade_hedge_result.php"
    params = {
        "d": roc_date,
        "l": "zh-tw",
        "o": "htm",
        "s": "0",
        "se": "EW",
        "t": "D"
    }

    try:
        response = requests.get(url, params=params, timeout=20, verify=False)
        response.encoding = 'utf-8'

        if response.status_code != 200:
            print(f"❌ HTTP {response.status_code}")
            return pd.DataFrame()

        # 解析 HTML 表格
        from io import StringIO
        tables = pd.read_html(StringIO(response.text))

        if len(tables) == 0:
            print("❌ 未找到表格")
            return pd.DataFrame()

        df = tables[0]

        # 檢查是否為空資料
        if len(df) <= 2 and '共0筆' in str(df.values):
            print("⚠️  TPEx: 無資料（可能是非交易日）")
            return pd.DataFrame()

        # TPEx 的欄位是 MultiIndex，需要扁平化
        if isinstance(df.columns, pd.MultiIndex):
            # 合併多層欄位名稱
            df.columns = ['_'.join(col).strip() if col[0] != col[1] else col[0] for col in df.columns]

        # 加入日期和類型
        df['date'] = date_str
        df['type'] = 'tpex'

        # 只保留 4 位數字的股票代碼
        if '代號' in df.columns:
            df = df[df['代號'].astype(str).str.len() == 4]
            df = df[df['代號'].astype(str).str.isdigit()]

        print(f"✅ TPEx: {len(df)} 筆")
        return df

    except Exception as e:
        print(f"❌ TPEx 錯誤: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()


def save_institutional_data(twse_df, tpex_df, date_str):
    """
    儲存三大法人資料

    Args:
        twse_df: TWSE DataFrame
        tpex_df: TPEx DataFrame
        date_str: 日期字串 YYYY-MM-DD
    """
    print(f"\n儲存資料到檔案...")

    # 建立目錄
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    year = date_obj.year
    month = date_obj.month

    output_dir = f"data/raw/institutional/{year}/{month:02d}"
    os.makedirs(output_dir, exist_ok=True)

    # 準備資料
    data = {
        "metadata": {
            "date": date_str,
            "collected_at": datetime.now().isoformat(),
            "twse_count": len(twse_df),
            "tpex_count": len(tpex_df),
            "total_count": len(twse_df) + len(tpex_df)
        },
        "twse": twse_df.to_dict('records') if not twse_df.empty else [],
        "tpex": tpex_df.to_dict('records') if not tpex_df.empty else []
    }

    # 儲存 JSON
    output_file = f"{output_dir}/{date_str}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 計算檔案大小
    file_size = os.path.getsize(output_file)
    size_kb = file_size / 1024

    print(f"✅ 儲存完成: {output_file}")
    print(f"   檔案大小: {size_kb:.1f} KB")
    print(f"   TWSE: {len(twse_df)} 筆")
    print(f"   TPEx: {len(tpex_df)} 筆")
    print(f"   總計: {len(twse_df) + len(tpex_df)} 筆")


if __name__ == "__main__":
    # 收集 2025-12-26 的資料
    date = "2025-12-26"

    print("=" * 60)
    print(f"收集三大法人資料: {date}")
    print("=" * 60)

    # 收集 TWSE
    twse_df = collect_twse_institutional(date)

    # 收集 TPEx
    tpex_df = collect_tpex_institutional(date)

    # 儲存
    if not twse_df.empty or not tpex_df.empty:
        save_institutional_data(twse_df, tpex_df, date)
    else:
        print("\n❌ 無資料可儲存")

    print("\n" + "=" * 60)
    print("完成")
    print("=" * 60)
