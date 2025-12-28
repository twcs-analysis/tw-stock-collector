"""
收集借券賣出資料
使用 TWSE TWT93U API（包含上市+上櫃所有股票）
"""

import requests
import pandas as pd
from datetime import datetime
import json
import os


def collect_twse_lending(date_str):
    """
    收集 TWSE 借券賣出資料（包含上市+上櫃）

    Args:
        date_str: 日期字串 YYYY-MM-DD

    Returns:
        DataFrame
    """
    print(f"收集借券賣出資料: {date_str}")

    # 轉換日期格式
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    twse_date = date_obj.strftime('%Y%m%d')

    url = "https://www.twse.com.tw/exchangeReport/TWT93U"
    params = {
        "response": "json",
        "date": twse_date
    }

    try:
        response = requests.get(url, params=params, timeout=20)

        if response.status_code != 200:
            print(f"❌ HTTP {response.status_code}")
            return pd.DataFrame()

        data = response.json()

        # 檢查是否有資料
        if 'data' not in data or len(data['data']) == 0:
            print("⚠️  無資料（可能是非交易日）")
            return pd.DataFrame()

        # 取得欄位和資料
        fields = data.get('fields', [])
        rows = data.get('data', [])

        # 建立 DataFrame
        df = pd.DataFrame(rows, columns=fields)

        # 加入日期
        df['date'] = date_str

        # 只保留 4 位數字的股票代碼
        if '代號' in df.columns:
            df = df[df['代號'].astype(str).str.len() == 4]
            df = df[df['代號'].astype(str).str.isdigit()]

        print(f"✅ 借券賣出: {len(df)} 檔（上市+上櫃）")
        return df

    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()


def save_lending_data(df, date_str):
    """
    儲存借券賣出資料

    Args:
        df: DataFrame
        date_str: 日期字串 YYYY-MM-DD
    """
    print(f"\n儲存資料到檔案...")

    # 建立目錄
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    year = date_obj.year
    month = date_obj.month

    output_dir = f"data/raw/lending/{year}/{month:02d}"
    os.makedirs(output_dir, exist_ok=True)

    # 準備資料
    data = {
        "metadata": {
            "date": date_str,
            "collected_at": datetime.now().isoformat(),
            "total_count": len(df),
            "source": "TWSE TWT93U API (包含上市+上櫃)"
        },
        "data": df.to_dict('records') if not df.empty else []
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
    print(f"   總計: {len(df)} 檔")


if __name__ == "__main__":
    # 收集 2024-12-27 的資料
    date = "2024-12-27"

    print("=" * 60)
    print(f"收集借券賣出資料: {date}")
    print("=" * 60)

    # 收集資料
    df = collect_twse_lending(date)

    # 儲存
    if not df.empty:
        save_lending_data(df, date)
    else:
        print("\n❌ 無資料可儲存")

    print("\n" + "=" * 60)
    print("完成")
    print("=" * 60)
