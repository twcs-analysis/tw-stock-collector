#!/usr/bin/env python3
"""
回檔買上漲選股工具
基於型態分析定義篩選符合條件的股票

選股條件：
- 條件 A：股票型態是否為 頭頭高 底底高
- 條件 B：股價是否在月線之上且前低未破？
- 條件 C：今日紅 K 是否站上 5 均？
- 條件 D：收盤是否過昨日高？
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta

def get_stock_name(stock_id, stock_name_dict):
    """取得股票名稱"""
    stock_id_str = str(int(stock_id)).zfill(4)
    return stock_name_dict.get(stock_id_str, stock_id_str)

def load_historical_data(date_str, days_back=20):
    """
    載入歷史資料（用於判斷頭頭高底底高）

    Args:
        date_str: 目標日期 (YYYY-MM-DD)
        days_back: 往前取幾天的資料

    Returns:
        dict: {stock_id: [日期資料列表]}
    """
    target_date = datetime.strptime(date_str, '%Y-%m-%d')
    base_path = Path(__file__).parent.parent.parent / "data/transformed/technical"

    stock_history = {}

    # 往前找 days_back 個交易日的資料
    for i in range(days_back + 1):
        check_date = target_date - timedelta(days=i)
        csv_file = base_path / f"{check_date.strftime('%Y-%m-%d')}_all.csv"

        if csv_file.exists():
            try:
                df = pd.read_csv(csv_file)
                for _, row in df.iterrows():
                    stock_id = int(row['stock_id'])
                    if stock_id not in stock_history:
                        stock_history[stock_id] = []
                    stock_history[stock_id].append({
                        'date': row['trade_date'],
                        'high': row['high'],
                        'low': row['low'],
                        'close': row['close'],
                        'open': row['open']
                    })
            except Exception as e:
                print(f"警告：無法讀取 {csv_file}: {e}")
                continue

    # 排序（由舊到新）
    for stock_id in stock_history:
        stock_history[stock_id].sort(key=lambda x: x['date'])

    return stock_history

def check_higher_highs_higher_lows(history, lookback=10):
    """
    檢查條件 A：頭頭高 底底高

    Args:
        history: 股票歷史資料列表
        lookback: 檢查最近幾天

    Returns:
        bool: 是否符合頭頭高底底高
    """
    if len(history) < lookback:
        return False

    recent = history[-lookback:]

    # 找出最近的高點和低點
    highs = [d['high'] for d in recent]
    lows = [d['low'] for d in recent]

    # 至少要有 3 個高點和 3 個低點來判斷趨勢
    if len(highs) < 3 or len(lows) < 3:
        return False

    # 簡化判斷：最近 5 天的高點要比前 5 天高，低點也要比前 5 天高
    mid = lookback // 2

    recent_highs = highs[mid:]
    earlier_highs = highs[:mid]
    recent_lows = lows[mid:]
    earlier_lows = lows[:mid]

    # 最近的平均高點 > 早期的平均高點
    higher_highs = sum(recent_highs) / len(recent_highs) > sum(earlier_highs) / len(earlier_highs)

    # 最近的平均低點 > 早期的平均低點
    higher_lows = sum(recent_lows) / len(recent_lows) > sum(earlier_lows) / len(earlier_lows)

    return higher_highs and higher_lows

def check_above_ma20_and_prev_low(row, history):
    """
    檢查條件 B：股價是否在月線之上且前低未破

    Args:
        row: 當日資料
        history: 歷史資料

    Returns:
        tuple: (是否在月線上, 是否未破前低)
    """
    # 檢查是否在 MA20 之上
    above_ma20 = row['close'] > row['ma_20']

    # 檢查前低（最近 10 天的最低點）
    if len(history) < 10:
        return above_ma20, False

    recent_lows = [d['low'] for d in history[-10:]]
    prev_low = min(recent_lows[:-1])  # 排除今天

    # 今天的最低價未破前低
    not_break_prev_low = row['low'] >= prev_low

    return above_ma20, not_break_prev_low

def check_red_k_above_ma5(row):
    """
    檢查條件 C：今日紅 K 是否站上 5 均

    Args:
        row: 當日資料

    Returns:
        tuple: (是否紅 K, 是否站上 MA5)
    """
    # 紅 K：收盤 > 開盤
    is_red_k = row['close'] > row['open']

    # 站上 MA5：收盤 > MA5
    above_ma5 = row['close'] > row['ma_5']

    return is_red_k, above_ma5

def check_break_yesterday_high(row, history):
    """
    檢查條件 D：收盤是否過昨日高

    Args:
        row: 當日資料
        history: 歷史資料

    Returns:
        bool: 是否突破昨日高
    """
    if len(history) < 2:
        return False

    yesterday_high = history[-2]['high']  # -1 是今天，-2 是昨天

    return row['close'] > yesterday_high

def main():
    """主程式"""
    import sys

    print("=" * 80)
    print("回檔買上漲選股工具")
    print("=" * 80)
    print()

    # 設定日期（可從命令列參數取得，預設為今天）
    if len(sys.argv) > 1:
        target_date = sys.argv[1]
    else:
        target_date = datetime.now().strftime('%Y-%m-%d')

    # 載入股票名稱
    print("📊 載入股票資料...")
    # 從日期提取年月
    date_parts = target_date.split('-')
    year, month = date_parts[0], date_parts[1]
    raw_data_path = Path(__file__).parent.parent.parent / f"data/raw/price/{year}/{month}/{target_date}.json"

    stock_name_dict = {}
    if raw_data_path.exists():
        with open(raw_data_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            stock_name_dict = {item['stock_id']: item['stock_name'] for item in raw_data['data']}
        print(f"✓ 載入 {len(stock_name_dict)} 檔股票名稱")
    else:
        print(f"⚠️  原始資料不存在，將僅顯示股票代碼")

    # 載入技術指標資料
    data_path = Path(__file__).parent.parent.parent / f"data/transformed/technical/{target_date}_all.csv"

    if not data_path.exists():
        print(f"❌ 找不到技術指標資料：{data_path}")
        return

    df = pd.read_csv(data_path)
    print(f"✓ 載入 {len(df)} 檔股票技術指標")
    print()

    # 載入歷史資料
    print("📈 載入歷史資料（用於型態判斷）...")
    stock_history = load_historical_data(target_date, days_back=20)
    print(f"✓ 載入 {len(stock_history)} 檔股票歷史資料")
    print()

    print("🔍 開始篩選符合條件的股票...")
    print()

    # 篩選結果
    results = []

    for idx, row in df.iterrows():
        stock_id = int(row['stock_id'])

        # 排除 ETF 和小型股
        if str(stock_id).startswith('0') or row['volume'] < 1000000:
            continue

        # 取得歷史資料
        history = stock_history.get(stock_id, [])
        if len(history) < 10:
            continue

        # 檢查四個條件
        # 條件 A：頭頭高 底底高
        condition_a = check_higher_highs_higher_lows(history, lookback=10)

        # 條件 B：股價在月線之上且前低未破
        above_ma20, not_break_prev_low = check_above_ma20_and_prev_low(row, history)
        condition_b = above_ma20 and not_break_prev_low

        # 條件 C：今日紅 K 站上 5 均
        is_red_k, above_ma5 = check_red_k_above_ma5(row)
        condition_c = is_red_k and above_ma5

        # 條件 D：收盤過昨日高
        condition_d = check_break_yesterday_high(row, history)

        # 符合所有條件
        if condition_a and condition_b and condition_c and condition_d:
            stock_name = get_stock_name(stock_id, stock_name_dict)

            results.append({
                'stock_id': stock_id,
                'stock_name': stock_name,
                'close': row['close'],
                'open': row['open'],
                'high': row['high'],
                'low': row['low'],
                'ma_5': row['ma_5'],
                'ma_20': row['ma_20'],
                'volume': row['volume'],
                'vol_ratio': row['vol_ratio'],
                'rsi_14': row['rsi_14'],
                'macd_hist': row['macd_hist'],
                'condition_a': '✓',
                'condition_b': '✓',
                'condition_c': '✓',
                'condition_d': '✓'
            })

    print(f"✓ 篩選完成！符合條件的股票共 {len(results)} 檔")
    print()

    if len(results) == 0:
        print("😢 沒有符合所有條件的股票")
        print()
        print("建議：")
        print("1. 調整篩選條件（放寬某些條件）")
        print("2. 檢查是否有足夠的歷史資料")
        print("3. 市場可能處於盤整或空頭，符合條件的股票較少")
        return

    # 顯示結果
    print("=" * 80)
    print(f"符合「回檔買上漲」條件的股票（{target_date}）")
    print("=" * 80)
    print()

    for idx, stock in enumerate(results, 1):
        print(f"【第 {idx} 名】{stock['stock_id']} - {stock['stock_name']}")
        print(f"  收盤價：{stock['close']:.2f} 元")
        print(f"  開盤：{stock['open']:.2f} | 最高：{stock['high']:.2f} | 最低：{stock['low']:.2f}")
        print(f"  MA5：{stock['ma_5']:.2f} | MA20：{stock['ma_20']:.2f}")
        print(f"  成交量：{int(stock['volume']):,} | 量比：{stock['vol_ratio']:.2f}")
        print(f"  RSI(14)：{stock['rsi_14']:.2f} | MACD 柱狀圖：{stock['macd_hist']:.4f}")
        print()
        print(f"  條件檢查：")
        print(f"    條件 A（頭頭高底底高）：{stock['condition_a']}")
        print(f"    條件 B（在月線上且前低未破）：{stock['condition_b']}")
        print(f"    條件 C（紅 K 站上 5 均）：{stock['condition_c']}")
        print(f"    條件 D（收盤過昨日高）：{stock['condition_d']}")
        print()
        print("-" * 80)
        print()

    # 輸出到檔案
    output_dir = Path.home() / "Downloads" / "股票推薦"
    output_dir.mkdir(parents=True, exist_ok=True)

    # CSV 檔案
    csv_file = output_dir / f"回檔買上漲選股_{target_date}.csv"
    results_df = pd.DataFrame(results)
    results_df.to_csv(csv_file, index=False, encoding='utf-8-sig')

    print()
    print("=" * 80)
    print("✅ 分析完成！")
    print("=" * 80)
    print()
    print(f"CSV 檔案已生成：{csv_file}")
    print()

if __name__ == "__main__":
    main()
