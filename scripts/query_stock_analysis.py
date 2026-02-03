#!/usr/bin/env python3
"""
查詢股票技術分析資料

用法:
    # 查詢單一股票
    python scripts/query_stock_analysis.py 2330

    # 查詢多支股票
    python scripts/query_stock_analysis.py 2330 2539 2454

    # 指定日期查詢
    python scripts/query_stock_analysis.py 2330 --date 2026-02-03

    # 從 CSV 檔案查詢
    python scripts/query_stock_analysis.py 2330 --source csv --date 2026-02-03

    # 從資料庫查詢（預設）
    python scripts/query_stock_analysis.py 2330 --source db

    # 簡化輸出（只顯示關鍵指標）
    python scripts/query_stock_analysis.py 2330 --simple

    # 原始數值輸出（CSV 格式）
    python scripts/query_stock_analysis.py 2330 --raw
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd

# 加入專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def query_from_database(stock_ids: List[str], date: str) -> pd.DataFrame:
    """從資料庫查詢技術分析資料"""
    import psycopg2
    from psycopg2.extras import RealDictCursor

    conn = psycopg2.connect(
        host="localhost",
        database="tw_stock",
        user="postgres",
        password="tw_stock_dev_password_2024"
    )

    placeholders = ','.join(['%s'] * len(stock_ids))
    query = f"""
        SELECT
            trade_date, stock_id, open_price, high_price, low_price, close_price,
            volume, amount, ma_5, ma_10, ma_20, ma_60, ma_120, ma_240,
            rsi_6, rsi_14, macd_dif, macd_dea, macd_hist,
            dmi_pdi, dmi_mdi, dmi_adx, dmi_adxr,
            bb_upper, bb_mid, bb_lower,
            vol_ma5, vol_ma20, vol_ratio, vwap
        FROM stock_analysis_daily
        WHERE trade_date = %s AND stock_id IN ({placeholders})
        ORDER BY stock_id
    """

    df = pd.read_sql_query(query, conn, params=[date] + stock_ids)
    conn.close()

    # 重新命名欄位以符合 CSV 格式
    df = df.rename(columns={
        'open_price': 'open',
        'high_price': 'high',
        'low_price': 'low',
        'close_price': 'close'
    })

    return df


def query_from_csv(stock_ids: List[str], date: str) -> pd.DataFrame:
    """從 CSV 檔案查詢技術分析資料"""
    csv_file = project_root / f'data/transformed/technical/{date}_all.csv'

    if not csv_file.exists():
        raise FileNotFoundError(f"找不到檔案: {csv_file}")

    df = pd.read_csv(csv_file, encoding='utf-8-sig')

    # 篩選指定股票
    stock_ids_int = [int(sid) for sid in stock_ids]
    df = df[df['stock_id'].isin(stock_ids_int)]

    return df


def get_stock_name(stock_id: str) -> str:
    """取得股票名稱"""
    stock_names = {
        '2330': '台積電',
        '2317': '鴻海',
        '2454': '聯發科',
        '2308': '台達電',
        '2881': '富邦金',
        '2882': '國泰金',
        '2886': '兆豐金',
        '2891': '中信金',
        '2412': '中華電',
        '2303': '聯電',
        '2002': '中鋼',
        '1301': '台塑',
        '1303': '南亞',
        '1326': '台化',
        '2539': '櫻花建',
        '2884': '玉山金',
        '2912': '統一超',
        '5880': '合庫金',
        '6505': '台塑化',
    }

    return stock_names.get(stock_id, f'股票{stock_id}')


def display_full_analysis(row: pd.Series, stock_name: str):
    """顯示完整技術分析"""
    stock_id = str(int(row['stock_id']))

    print(f"\n{'='*85}")
    print(f"📊 {stock_name} ({stock_id}) - {row['trade_date']} 完整技術分析")
    print(f"{'='*85}\n")

    # 基本資料
    print("【1-8. 基本資料】")
    print(f"   1. 交易日期:   {row['trade_date']}")
    print(f"   2. 股票代號:   {stock_id}")
    print(f"   3. 開盤價:     {row['open']:>12,.2f}")
    print(f"   4. 最高價:     {row['high']:>12,.2f}")
    print(f"   5. 最低價:     {row['low']:>12,.2f}")
    print(f"   6. 收盤價:     {row['close']:>12,.2f}")
    print(f"   7. 成交量:     {int(row['volume']):>12,} 股")
    print(f"   8. 成交金額:   {int(row['amount']):>12,} 元")

    # 移動平均線
    print("\n【9-14. 移動平均線 (MA)】")
    print(f"   9. MA5:        {row['ma_5']:>12,.2f}")
    print(f"  10. MA10:       {row['ma_10']:>12,.2f}")
    print(f"  11. MA20:       {row['ma_20']:>12,.2f}")
    print(f"  12. MA60:       {row['ma_60']:>12,.2f}")
    if pd.notna(row['ma_120']):
        print(f"  13. MA120:      {row['ma_120']:>12,.2f}")
    else:
        print(f"  13. MA120:      {'N/A':>12}")
    if pd.notna(row['ma_240']):
        print(f"  14. MA240:      {row['ma_240']:>12,.2f}")
    else:
        print(f"  14. MA240:      {'N/A':>12}")

    # RSI
    print("\n【15-16. 相對強弱指標 (RSI)】")
    print(f"  15. RSI6:       {row['rsi_6']:>12,.2f}")
    print(f"  16. RSI14:      {row['rsi_14']:>12,.2f}")

    # MACD
    print("\n【17-19. MACD 指標】")
    print(f"  17. MACD_DIF:   {row['macd_dif']:>12,.2f}")
    print(f"  18. MACD_DEA:   {row['macd_dea']:>12,.2f}")
    print(f"  19. MACD_HIST:  {row['macd_hist']:>12,.2f}")

    # DMI/ADX
    print("\n【20-23. DMI/ADX 指標】")
    print(f"  20. +DI (PDI):  {row['dmi_pdi']:>12,.2f}")
    print(f"  21. -DI (MDI):  {row['dmi_mdi']:>12,.2f}")
    print(f"  22. ADX:        {row['dmi_adx']:>12,.2f}")
    if pd.notna(row['dmi_adxr']):
        print(f"  23. ADXR:       {row['dmi_adxr']:>12,.2f}")
    else:
        print(f"  23. ADXR:       {'N/A':>12}")

    # 布林通道
    print("\n【24-26. 布林通道 (Bollinger Bands)】")
    print(f"  24. 上軌:       {row['bb_upper']:>12,.2f}")
    print(f"  25. 中軌:       {row['bb_mid']:>12,.2f}")
    print(f"  26. 下軌:       {row['bb_lower']:>12,.2f}")

    # 成交量指標
    print("\n【27-29. 成交量指標】")
    print(f"  27. 量5日均:    {int(row['vol_ma5']):>12,} 股")
    print(f"  28. 量20日均:   {int(row['vol_ma20']):>12,} 股")
    print(f"  29. 量比:       {row['vol_ratio']:>12,.4f}")

    # VWAP
    print("\n【30. 成交量加權平均價 (VWAP)】")
    print(f"  30. VWAP:       {row['vwap']:>12,.2f}")

    # 技術分析摘要
    print(f"\n{'='*85}")
    print("📈 技術分析摘要")
    print(f"{'='*85}")

    # 趨勢判斷
    ma_trend = "多頭" if row['close'] > row['ma_5'] > row['ma_20'] > row['ma_60'] else \
               "空頭" if row['close'] < row['ma_5'] < row['ma_20'] < row['ma_60'] else "盤整"

    # RSI 判斷
    rsi_status = "超買" if row['rsi_14'] > 70 else \
                 "超賣" if row['rsi_14'] < 30 else \
                 "強勢" if row['rsi_14'] > 50 else "弱勢"

    # MACD 判斷
    macd_signal = "多頭" if row['macd_hist'] > 0 else "空頭"

    # DMI 判斷
    dmi_signal = "多頭" if row['dmi_pdi'] > row['dmi_mdi'] else "空頭"
    adx_strength = "強趨勢" if row['dmi_adx'] > 40 else \
                   "中等趨勢" if row['dmi_adx'] > 20 else "弱趨勢"

    # 價格位置
    bb_position = "上軌附近" if row['close'] > row['bb_upper'] * 0.98 else \
                  "下軌附近" if row['close'] < row['bb_lower'] * 1.02 else \
                  "中軌附近" if abs(row['close'] - row['bb_mid']) < (row['bb_upper'] - row['bb_mid']) * 0.3 else \
                  "中性"

    # 成交量
    vol_status = "放量" if row['vol_ratio'] > 1.2 else \
                 "縮量" if row['vol_ratio'] < 0.8 else "均量"

    print(f"\n  趨勢狀態:     {ma_trend}排列")
    print(f"  RSI 狀態:     {rsi_status} (RSI14={row['rsi_14']:.2f})")
    print(f"  MACD 訊號:    {macd_signal}柱狀 (HIST={row['macd_hist']:.2f})")
    print(f"  DMI 方向:     {dmi_signal}優勢 (+DI={row['dmi_pdi']:.2f}, -DI={row['dmi_mdi']:.2f})")
    print(f"  ADX 強度:     {adx_strength} (ADX={row['dmi_adx']:.2f})")
    print(f"  布林位置:     {bb_position}")
    print(f"  成交量:       {vol_status} (量比={row['vol_ratio']:.2f})")
    print()


def display_simple_analysis(row: pd.Series, stock_name: str):
    """顯示簡化技術分析（只顯示關鍵指標）"""
    stock_id = str(int(row['stock_id']))

    print(f"\n{'='*70}")
    print(f"📊 {stock_name} ({stock_id}) - {row['trade_date']}")
    print(f"{'='*70}")

    print(f"\n【價格】")
    print(f"  開盤: {row['open']:>8,.2f}  最高: {row['high']:>8,.2f}  "
          f"最低: {row['low']:>8,.2f}  收盤: {row['close']:>8,.2f}")

    print(f"\n【均線】")
    print(f"  MA5:  {row['ma_5']:>8,.2f}  MA10: {row['ma_10']:>8,.2f}  "
          f"MA20: {row['ma_20']:>8,.2f}  MA60: {row['ma_60']:>8,.2f}")

    print(f"\n【指標】")
    print(f"  RSI14:      {row['rsi_14']:>8,.2f}  {'(超買)' if row['rsi_14'] > 70 else '(超賣)' if row['rsi_14'] < 30 else ''}")
    print(f"  MACD_HIST:  {row['macd_hist']:>8,.2f}  {'(多頭)' if row['macd_hist'] > 0 else '(空頭)'}")
    print(f"  ADX:        {row['dmi_adx']:>8,.2f}  {'(強趨勢)' if row['dmi_adx'] > 40 else '(弱趨勢)' if row['dmi_adx'] < 20 else ''}")
    print(f"  量比:       {row['vol_ratio']:>8,.4f}  {'(放量)' if row['vol_ratio'] > 1.2 else '(縮量)' if row['vol_ratio'] < 0.8 else ''}")
    print()


def display_raw_data(df: pd.DataFrame):
    """顯示原始數值（CSV 格式）"""
    # 設定 pandas 顯示選項
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.float_format', lambda x: f'{x:.2f}' if pd.notna(x) else 'NaN')

    # 確保 stock_id 顯示為字串
    df_display = df.copy()
    df_display['stock_id'] = df_display['stock_id'].astype(int).astype(str)

    # 以 CSV 格式輸出
    print(df_display.to_csv(index=False, float_format='%.4f'))


def main():
    parser = argparse.ArgumentParser(
        description='查詢股票技術分析資料',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用範例:
  # 查詢台積電技術分析
  %(prog)s 2330

  # 查詢多支股票
  %(prog)s 2330 2454 2317

  # 指定日期查詢
  %(prog)s 2330 --date 2026-02-03

  # 從 CSV 檔案查詢
  %(prog)s 2330 --source csv --date 2026-02-03

  # 簡化輸出
  %(prog)s 2330 --simple

  # 原始數值輸出
  %(prog)s 2330 --raw
        '''
    )

    parser.add_argument(
        'stock_ids',
        nargs='+',
        help='股票代號（可指定多個）'
    )

    parser.add_argument(
        '--date',
        default=None,
        help='查詢日期 (YYYY-MM-DD)，預設為最近交易日'
    )

    parser.add_argument(
        '--source',
        choices=['db', 'csv'],
        default='db',
        help='資料來源：db=資料庫（預設）, csv=CSV檔案'
    )

    parser.add_argument(
        '--simple',
        action='store_true',
        help='簡化輸出（只顯示關鍵指標）'
    )

    parser.add_argument(
        '--raw',
        action='store_true',
        help='原始數值輸出（CSV 格式）'
    )

    args = parser.parse_args()

    # 如果沒有指定日期，使用今天或最近交易日
    if args.date is None:
        args.date = datetime.now().strftime('%Y-%m-%d')
        print(f"⚠️  未指定日期，使用今天: {args.date}")

    try:
        # 查詢資料
        if args.source == 'db':
            print(f"📊 從資料庫查詢 {args.date} 的技術分析資料...")
            df = query_from_database(args.stock_ids, args.date)
        else:
            print(f"📊 從 CSV 檔案查詢 {args.date} 的技術分析資料...")
            df = query_from_csv(args.stock_ids, args.date)

        if df.empty:
            print(f"❌ 找不到資料: {args.date}, 股票: {', '.join(args.stock_ids)}")
            return

        print(f"✅ 找到 {len(df)} 筆資料\n")

        # 顯示結果
        if args.raw:
            # 原始數值模式
            display_raw_data(df)
        else:
            # 格式化顯示模式
            for _, row in df.iterrows():
                stock_id = str(int(row['stock_id']))
                stock_name = get_stock_name(stock_id)

                if args.simple:
                    display_simple_analysis(row, stock_name)
                else:
                    display_full_analysis(row, stock_name)

    except FileNotFoundError as e:
        print(f"❌ 錯誤: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
