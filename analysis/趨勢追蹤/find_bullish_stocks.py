#!/usr/bin/env python3
"""
多頭市場技術分析選股腳本
根據技術指標篩選適合的多頭標的
"""

import pandas as pd
import sys
from pathlib import Path

# 讀取最新的技術指標資料
data_path = Path(__file__).parent.parent.parent / "data/transformed/technical/2026-01-30_all.csv"
df = pd.read_csv(data_path)

print(f"總共載入 {len(df)} 檔股票資料\n")

# 多頭選股條件
# 1. 價格在均線之上（多頭排列）
# 2. RSI 在 50-70 之間（強勢但未超買）
# 3. MACD 黃金交叉（DIF > DEA）且柱狀圖為正
# 4. ADX > 25（趨勢強勁）
# 5. 價格在布林通道中上軌
# 6. 成交量大於 20 日均量（活躍）

conditions = (
    # 均線多頭排列：收盤價 > MA5 > MA20
    (df['close'] > df['ma_5']) &
    (df['ma_5'] > df['ma_20']) &

    # RSI 強勢但未超買
    (df['rsi_14'] > 50) &
    (df['rsi_14'] < 70) &

    # MACD 黃金交叉
    (df['macd_dif'] > df['macd_dea']) &
    (df['macd_hist'] > 0) &

    # ADX 趨勢強勁
    (df['dmi_adx'] > 25) &

    # +DI > -DI（多頭趨勢）
    (df['dmi_pdi'] > df['dmi_mdi']) &

    # 價格在布林通道中上軌（布林中線到上軌之間）
    (df['close'] > df['bb_mid']) &
    (df['close'] < df['bb_upper']) &

    # 成交量活躍
    (df['volume'] > df['vol_ma20']) &

    # 排除 ETF（股票代碼以 0 開頭）和小型股（成交量過低）
    (~df['stock_id'].astype(str).str.startswith('0')) &
    (df['volume'] > 1000000)
)

# 篩選符合條件的股票
bullish_stocks = df[conditions].copy()

# 計算綜合評分
# 評分因子：
# 1. RSI 分數（越接近 60 越好）
# 2. MACD 柱狀圖強度
# 3. ADX 強度
# 4. 多頭力道（+DI - -DI）
# 5. 成交量比率

bullish_stocks['rsi_score'] = 100 - abs(bullish_stocks['rsi_14'] - 60)
bullish_stocks['macd_score'] = bullish_stocks['macd_hist'] * 10
bullish_stocks['adx_score'] = bullish_stocks['dmi_adx']
bullish_stocks['dmi_score'] = bullish_stocks['dmi_pdi'] - bullish_stocks['dmi_mdi']
bullish_stocks['vol_score'] = (bullish_stocks['vol_ratio'] - 1) * 50

# 綜合評分（加權平均）
bullish_stocks['total_score'] = (
    bullish_stocks['rsi_score'] * 0.2 +
    bullish_stocks['macd_score'] * 0.2 +
    bullish_stocks['adx_score'] * 0.2 +
    bullish_stocks['dmi_score'] * 0.2 +
    bullish_stocks['vol_score'] * 0.2
)

# 按評分排序
bullish_stocks = bullish_stocks.sort_values('total_score', ascending=False)

print(f"符合多頭條件的股票共 {len(bullish_stocks)} 檔\n")
print("=" * 100)
print("推薦前 10 檔標的：")
print("=" * 100)

# 顯示前 10 名
top_10 = bullish_stocks.head(10)

for idx, (i, row) in enumerate(top_10.iterrows(), 1):
    print(f"\n【第 {idx} 名】股票代碼：{row['stock_id']}")
    print(f"  收盤價：{row['close']:.2f}")
    print(f"  技術指標：")
    print(f"    • MA5: {row['ma_5']:.2f} | MA20: {row['ma_20']:.2f} | 均線排列：多頭")
    print(f"    • RSI(14): {row['rsi_14']:.2f} | 狀態：{'強勢' if row['rsi_14'] > 60 else '偏強'}")
    print(f"    • MACD 柱狀圖: {row['macd_hist']:.4f} | 狀態：黃金交叉")
    print(f"    • ADX: {row['dmi_adx']:.2f} | 趨勢：{'強勁' if row['dmi_adx'] > 30 else '中等'}")
    print(f"    • +DI: {row['dmi_pdi']:.2f} | -DI: {row['dmi_mdi']:.2f} | 多頭力道：{row['dmi_pdi'] - row['dmi_mdi']:.2f}")
    print(f"    • 成交量比率: {row['vol_ratio']:.2f} | 狀態：{'放量' if row['vol_ratio'] > 1.2 else '正常'}")
    print(f"  綜合評分：{row['total_score']:.2f}")

print("\n" + "=" * 100)
print("\n備註：")
print("• 以上推薦僅供參考，投資有風險，請自行評估")
print("• 建議搭配基本面分析和產業趨勢判斷")
print("• 技術指標基於 2026-01-30 資料計算")
print("• 已排除 ETF 和成交量過低的股票")
