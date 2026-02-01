"""
簡單測試腳本 - 測試技術分析轉換器

不依賴複雜的配置系統，直接測試核心功能
"""

import sys
from pathlib import Path
import pandas as pd
import json
from datetime import datetime, timedelta

# 加入 app 模組路徑
sys.path.insert(0, str(Path(__file__).parent / 'app'))

import indicators
from json_saver import save_analysis_to_json


def load_test_data(date_str: str, data_dir: str = 'data/raw/price') -> pd.DataFrame:
    """載入測試資料"""
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    year = date_obj.year
    month = f'{date_obj.month:02d}'

    file_path = Path(data_dir) / str(year) / month / f'{date_str}.json'

    if not file_path.exists():
        print(f'✗ 檔案不存在: {file_path}')
        return pd.DataFrame()

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    df = pd.DataFrame(data['data'])
    df['trade_date'] = pd.to_datetime(df['date'])

    print(f'✓ 載入資料: {file_path}')
    print(f'  記錄數: {len(df)}')
    print(f'  股票數: {df["stock_id"].nunique()}')

    return df


def load_historical_data(target_date: str, lookback_days: int = 250) -> pd.DataFrame:
    """載入歷史資料"""
    target = datetime.strptime(target_date, '%Y-%m-%d')
    start_date = target - timedelta(days=lookback_days)

    all_data = []
    current = start_date

    print(f'\n載入歷史資料: {start_date.date()} 到 {target.date()}')

    while current <= target:
        date_str = current.strftime('%Y-%m-%d')
        df = load_test_data(date_str)

        if not df.empty:
            all_data.append(df)

        current += timedelta(days=1)

    if not all_data:
        return pd.DataFrame()

    result = pd.concat(all_data, ignore_index=True)
    result = result.sort_values(['stock_id', 'trade_date'])

    print(f'\n✓ 歷史資料載入完成:')
    print(f'  總記錄數: {len(result)}')
    print(f'  股票數: {result["stock_id"].nunique()}')
    print(f'  日期範圍: {result["trade_date"].min()} 到 {result["trade_date"].max()}')

    return result


def calculate_indicators_for_stock(stock_df: pd.DataFrame) -> pd.DataFrame:
    """計算單一股票的技術指標"""
    df = stock_df.set_index('trade_date').sort_index()

    # 均線
    df['ma_5'] = indicators.sma(df['close'], 5)
    df['ma_10'] = indicators.sma(df['close'], 10)
    df['ma_20'] = indicators.sma(df['close'], 20)
    df['ma_60'] = indicators.sma(df['close'], 60)
    df['ma_120'] = indicators.sma(df['close'], 120)
    df['ma_240'] = indicators.sma(df['close'], 240)

    # RSI
    df['rsi_6'] = indicators.rsi(df['close'], 6)
    df['rsi_14'] = indicators.rsi(df['close'], 14)

    # MACD
    macd_df = indicators.macd(df['close'])
    df['macd_dif'] = macd_df['DIF']
    df['macd_dea'] = macd_df['DEA']
    df['macd_hist'] = macd_df['Histogram']

    # ADX
    adx_df = indicators.adx(df['high'], df['low'], df['close'])
    df['dmi_pdi'] = adx_df['PDI']
    df['dmi_mdi'] = adx_df['MDI']
    df['dmi_adx'] = adx_df['ADX']

    # Bollinger Bands
    bb_df = indicators.bollinger_bands(df['close'])
    df['bb_upper'] = bb_df['upper']
    df['bb_mid'] = bb_df['middle']
    df['bb_lower'] = bb_df['lower']

    # Volume
    df['vol_ma5'] = indicators.sma(df['volume'], 5)
    df['vol_ma20'] = indicators.sma(df['volume'], 20)
    df['vol_ratio'] = df['volume'] / df['vol_ma5']
    df['vwap'] = indicators.vwap(df['high'], df['low'], df['close'], df['volume'])

    return df.reset_index()


def test_transformation(target_date: str = '2026-01-30'):
    """測試轉換功能"""
    print(f'=== 技術分析轉換器測試 ===\n')
    print(f'目標日期: {target_date}\n')

    # 1. 載入歷史資料
    historical_df = load_historical_data(target_date, lookback_days=300)

    if historical_df.empty:
        print('✗ 無歷史資料')
        return False

    # 2. 計算技術指標
    print(f'\n開始計算技術指標...')
    result_list = []

    grouped = historical_df.groupby('stock_id')
    for stock_id, stock_df in grouped:
        print(f'  處理 {stock_id}... ({len(stock_df)} 筆)')

        # 調整為只需要 20 天資料即可測試
        if len(stock_df) < 20:
            print(f'    跳過: 資料不足 (< 20 天)')
            continue

        indicators_df = calculate_indicators_for_stock(stock_df)
        result_list.append(indicators_df)

    if not result_list:
        print('✗ 沒有股票有足夠資料')
        return False

    # 3. 合併結果
    result_df = pd.concat(result_list, ignore_index=True)

    # 4. 篩選目標日期
    result_df = result_df[result_df['trade_date'] == target_date].copy()

    print(f'\n✓ 技術指標計算完成')
    print(f'  目標日期記錄數: {len(result_df)}')

    # 5. 顯示結果樣本
    if len(result_df) > 0:
        print(f'\n結果樣本 (第一筆):')
        sample = result_df.iloc[0]
        print(f'  股票: {sample["stock_id"]}')
        print(f'  日期: {sample["trade_date"]}')
        print(f'  收盤價: {sample["close"]:.2f}')
        print(f'  MA5: {sample["ma_5"]:.2f}')
        print(f'  MA20: {sample["ma_20"]:.2f}')
        print(f'  MA240: {sample["ma_240"]:.2f}')
        print(f'  RSI14: {sample["rsi_14"]:.2f}')
        print(f'  MACD DIF: {sample["macd_dif"]:.4f}')

        # 檢查 NULL 值
        null_counts = result_df.isnull().sum()
        print(f'\n欄位 NULL 值統計:')
        for col in ['ma_240', 'rsi_14', 'macd_dif', 'dmi_adx', 'bb_mid']:
            if col in null_counts:
                print(f'  {col}: {null_counts[col]}/{len(result_df)}')

    # 6. 儲存為 JSON
    print(f'\n儲存結果...')
    success = save_analysis_to_json(result_df, target_date)

    if success:
        print(f'✓ 資料已儲存為 JSON')
    else:
        print(f'✗ JSON 儲存失敗')
        return False

    return True


if __name__ == '__main__':
    success = test_transformation()
    sys.exit(0 if success else 1)
