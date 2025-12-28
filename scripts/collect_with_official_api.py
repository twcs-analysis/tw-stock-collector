#!/usr/bin/env python3
"""
使用官方 API 收集資料並儲存

按照專案規範儲存到 data 目錄
"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.datasources import TWSEDataSource, TPExDataSource
from src.utils.data_merger import DataMerger


def save_to_json(df, output_path: Path, date: str, data_type: str):
    """
    將 DataFrame 儲存為 JSON 格式

    按照專案規範：data/raw/{data_type}/YYYY/MM/YYYY-MM-DD.json
    """
    # 建立目錄
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 轉換為 JSON 格式（records 格式，每筆資料為一個 dict）
    data_dict = df.to_dict(orient='records')

    # 加入 metadata
    output_data = {
        'metadata': {
            'date': date,
            'data_type': data_type,
            'source': 'TWSE + TPEx Official API',
            'collected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'record_count': len(data_dict),
            'twse_count': len(df[df['type'] == 'twse']) if 'type' in df.columns else 0,
            'tpex_count': len(df[df['type'] == 'tpex']) if 'type' in df.columns else 0
        },
        'data': data_dict
    }

    # 寫入 JSON 檔案（格式化輸出，便於閱讀）
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 已儲存: {output_path}")
    print(f"   筆數: {len(data_dict)} 筆")
    print(f"   上市: {output_data['metadata']['twse_count']} 檔")
    print(f"   上櫃: {output_data['metadata']['tpex_count']} 檔")


def main():
    # 收集日期
    date = '2025-12-26'
    data_type = 'price'

    print("=" * 70)
    print(f"使用官方 API 收集資料")
    print(f"日期: {date}")
    print(f"資料類型: {data_type}")
    print("=" * 70)

    # 1. 收集 TWSE 資料
    print("\n【收集 TWSE（上市）資料】")
    twse_source = TWSEDataSource()
    twse_df = twse_source.get_daily_prices(date)
    print(f"TWSE: {len(twse_df)} 檔")

    # 2. 收集 TPEx 資料
    print("\n【收集 TPEx（上櫃）資料】")
    tpex_source = TPExDataSource()
    tpex_df = tpex_source.get_daily_prices(date)
    print(f"TPEx: {len(tpex_df)} 檔")

    # 3. 合併資料
    print("\n【合併資料】")
    merger = DataMerger()
    merged_df = merger.merge_dataframes([twse_df, tpex_df])

    if merged_df.empty:
        print("❌ 無資料可儲存")
        return 1

    # 4. 儲存到 data 目錄
    print("\n【儲存資料】")

    # 解析日期：YYYY-MM-DD -> YYYY/MM/YYYY-MM-DD.json
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    year = date_obj.strftime('%Y')
    month = date_obj.strftime('%m')

    # 建立路徑：data/raw/price/2025/12/2025-12-26.json
    base_dir = Path(__file__).parent.parent / 'data' / 'raw' / data_type / year / month
    output_file = base_dir / f"{date}.json"

    # 儲存
    save_to_json(merged_df, output_file, date, data_type)

    # 5. 驗證檔案
    print("\n【驗證儲存結果】")
    if output_file.exists():
        file_size = output_file.stat().st_size / 1024  # KB
        print(f"✅ 檔案已建立: {output_file}")
        print(f"   檔案大小: {file_size:.2f} KB")

        # 讀取驗證
        with open(output_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
            print(f"   驗證筆數: {loaded_data['metadata']['record_count']} 筆")
    else:
        print(f"❌ 檔案建立失敗")
        return 1

    print("\n" + "=" * 70)
    print("✅ 收集完成")
    print("=" * 70)

    return 0


if __name__ == '__main__':
    sys.exit(main())
