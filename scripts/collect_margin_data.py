#!/usr/bin/env python3
"""
收集 TWSE + TPEx 融資融券資料並匯出

測試新建立的官方 API 資料源，收集上市+上櫃融資融券資料
"""

import sys
import os
from datetime import datetime
from pathlib import Path
import json

# 加入專案根目錄到 Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.datasources.twse_margin_datasource import TWSEMarginDataSource
from src.datasources.tpex_margin_datasource import TPExMarginDataSource
from src.utils.data_merger import DataMerger


def main():
    """主程式"""
    print("=" * 70)
    print("收集 TWSE + TPEx 融資融券資料")
    print("=" * 70)
    
    # 使用今天日期
    date = datetime.now().strftime('%Y-%m-%d')
    print(f"\n收集日期: {date}")
    
    # 初始化資料源
    print("\n初始化資料源...")
    twse_source = TWSEMarginDataSource(timeout=30)
    tpex_source = TPExMarginDataSource(timeout=30)
    merger = DataMerger()
    
    # 收集 TWSE 資料
    print("\n收集 TWSE 上市融資融券資料...")
    try:
        twse_df = twse_source.get_margin_data(date)
        print(f"✅ TWSE: {len(twse_df)} 檔股票")
        print(f"   欄位: {list(twse_df.columns)}")
    except Exception as e:
        print(f"❌ TWSE 收集失敗: {e}")
        twse_df = None
    
    # 收集 TPEx 資料
    print("\n收集 TPEx 上櫃融資融券資料...")
    try:
        tpex_df = tpex_source.get_margin_data(date)
        print(f"✅ TPEx: {len(tpex_df)} 檔股票")
        print(f"   欄位: {list(tpex_df.columns)}")
    except Exception as e:
        print(f"❌ TPEx 收集失敗: {e}")
        tpex_df = None
    
    # 合併資料
    print("\n合併資料...")
    dataframes = []
    if twse_df is not None and not twse_df.empty:
        dataframes.append(twse_df)
    if tpex_df is not None and not tpex_df.empty:
        dataframes.append(tpex_df)
    
    if not dataframes:
        print("❌ 沒有資料可以合併")
        return
    
    merged_df = merger.merge_dataframes(dataframes, deduplicate_by='stock_id')
    print(f"✅ 合併後總計: {len(merged_df)} 檔股票")
    
    # 顯示統計資訊
    print("\n資料統計:")
    print(f"  TWSE 上市: {len(merged_df[merged_df['type'] == 'twse'])} 檔")
    print(f"  TPEx 上櫃: {len(merged_df[merged_df['type'] == 'tpex'])} 檔")
    
    # 顯示範例資料
    print("\n前 3 筆資料:")
    print(merged_df.head(3).to_string())
    
    # 準備匯出
    output_dir = Path('data/raw/margin') / date[:4] / date[5:7]
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{date}.json"
    
    # 轉換為 JSON 格式
    data_dict = {
        'metadata': {
            'date': date,
            'data_type': 'margin',
            'sources': ['TWSE', 'TPEx'],
            'total_stocks': len(merged_df),
            'twse_stocks': len(merged_df[merged_df['type'] == 'twse']),
            'tpex_stocks': len(merged_df[merged_df['type'] == 'tpex']),
            'collected_at': datetime.now().isoformat(),
            'fields': list(merged_df.columns)
        },
        'data': merged_df.to_dict('records')
    }
    
    # 寫入檔案
    print(f"\n匯出資料到: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data_dict, f, ensure_ascii=False, indent=2)
    
    file_size = output_file.stat().st_size / 1024
    print(f"✅ 匯出成功！檔案大小: {file_size:.1f} KB")
    
    print("\n" + "=" * 70)
    print("收集完成！")
    print("=" * 70)


if __name__ == '__main__':
    main()
