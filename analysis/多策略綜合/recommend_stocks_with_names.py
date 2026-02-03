#!/usr/bin/env python3
"""
2026-02-02 股票推薦分析（含股票名稱）
生成 Markdown 格式報告並轉換為 PDF
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# 讀取原始價格資料以取得股票名稱
raw_data_path = Path(__file__).parent.parent.parent / "data/raw/price/2026/02/2026-02-02.json"
with open(raw_data_path, 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

# 建立股票代碼到名稱的對應
stock_name_dict = {item['stock_id']: item['stock_name'] for item in raw_data['data']}
print(f"載入 {len(stock_name_dict)} 檔股票名稱\n")

# 讀取 2026-02-02 的技術指標資料
data_path = Path(__file__).parent.parent.parent / "data/transformed/technical/2026-02-02_all.csv"
df = pd.read_csv(data_path)

print(f"載入 2026-02-02 技術指標資料，總共 {len(df)} 檔股票\n")

# 定義多頭選股條件

# 條件 1: 強勢多頭（適合積極投資者）
strong_bullish = (
    (df['close'] > df['ma_5']) &
    (df['ma_5'] > df['ma_10']) &
    (df['ma_10'] > df['ma_20']) &
    (df['rsi_14'] >= 60) &
    (df['rsi_14'] <= 75) &
    (df['macd_dif'] > df['macd_dea']) &
    (df['macd_hist'] > 0.05) &
    (df['dmi_adx'] > 30) &
    (df['dmi_pdi'] > df['dmi_mdi'] + 15) &
    (df['close'] > df['bb_mid']) &
    (df['vol_ratio'] > 1.3) &
    (~df['stock_id'].astype(str).str.startswith('0')) &
    (df['volume'] > 1000000)
)

# 條件 2: 穩健多頭（適合穩健投資者）
steady_bullish = (
    (df['close'] > df['ma_5']) &
    (df['ma_5'] > df['ma_20']) &
    (df['rsi_14'] >= 50) &
    (df['rsi_14'] <= 65) &
    (df['macd_dif'] > df['macd_dea']) &
    (df['macd_hist'] > 0) &
    (df['dmi_adx'] > 25) &
    (df['dmi_pdi'] > df['dmi_mdi']) &
    (df['close'] > df['bb_mid']) &
    (df['close'] < df['bb_upper']) &
    (df['vol_ratio'] > 1.0) &
    (~df['stock_id'].astype(str).str.startswith('0')) &
    (df['volume'] > 1000000)
)

# 條件 3: 突破型（適合短線交易者）
breakout = (
    (df['close'] > df['ma_20']) &
    (df['rsi_14'] >= 55) &
    (df['rsi_14'] <= 70) &
    (df['macd_dif'] > df['macd_dea']) &
    (df['macd_hist'] > 0) &
    (df['macd_hist'] < 0.3) &
    (df['dmi_adx'] > 20) &
    (df['dmi_adx'] < 35) &
    (df['dmi_pdi'] > df['dmi_mdi'] + 10) &
    (df['close'] > df['bb_mid']) &
    (df['vol_ratio'] > 1.5) &
    (~df['stock_id'].astype(str).str.startswith('0')) &
    (df['volume'] > 1000000)
)

# 篩選三種類型的股票
strong_stocks = df[strong_bullish].copy()
steady_stocks = df[steady_bullish].copy()
breakout_stocks = df[breakout].copy()

print(f"強勢多頭：{len(strong_stocks)} 檔")
print(f"穩健多頭：{len(steady_stocks)} 檔")
print(f"突破型：{len(breakout_stocks)} 檔\n")

# 計算評分
def calculate_score(stocks_df):
    """計算綜合評分"""
    stocks_df = stocks_df.copy()
    stocks_df['rsi_score'] = 100 - abs(stocks_df['rsi_14'] - 60)
    stocks_df['macd_score'] = stocks_df['macd_hist'] * 20
    stocks_df['adx_score'] = stocks_df['dmi_adx']
    stocks_df['dmi_score'] = stocks_df['dmi_pdi'] - stocks_df['dmi_mdi']
    stocks_df['vol_score'] = (stocks_df['vol_ratio'] - 1) * 30
    stocks_df['ma_score'] = ((stocks_df['ma_5'] - stocks_df['ma_20']) / stocks_df['ma_20']) * 100

    stocks_df['total_score'] = (
        stocks_df['rsi_score'] * 0.15 +
        stocks_df['macd_score'] * 0.20 +
        stocks_df['adx_score'] * 0.20 +
        stocks_df['dmi_score'] * 0.20 +
        stocks_df['vol_score'] * 0.15 +
        stocks_df['ma_score'] * 0.10
    )
    return stocks_df.sort_values('total_score', ascending=False)

# 計算各類型評分
strong_stocks = calculate_score(strong_stocks)
steady_stocks = calculate_score(steady_stocks)
breakout_stocks = calculate_score(breakout_stocks)

# 生成輸出目錄
output_dir = Path.home() / "Downloads" / "股票推薦"
output_dir.mkdir(parents=True, exist_ok=True)

md_file = output_dir / "股票推薦報告_2026-02-02.md"

def get_stock_name(stock_id):
    """取得股票名稱"""
    # 將 stock_id 轉為字串（因為 CSV 中是整數，字典鍵是字串）
    stock_id_str = str(int(stock_id)).zfill(4)  # 補齊到 4 位數
    return stock_name_dict.get(stock_id_str, stock_id_str)

# 生成 Markdown 報告
with open(md_file, 'w', encoding='utf-8') as f:
    # 標題
    f.write("# 台股技術分析推薦報告\n\n")
    f.write("---\n\n")
    f.write(f"**分析日期**: 2026-02-02  \n")
    f.write(f"**報告生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
    f.write(f"**資料來源**: 台股技術指標資料庫  \n")
    f.write(f"**分析股票數**: {len(df)} 檔  \n\n")

    f.write("---\n\n")

    # 摘要
    f.write("## 📊 推薦摘要\n\n")
    f.write(f"| 類型 | 符合條件檔數 | 推薦標的數 |\n")
    f.write(f"|------|------------|----------|\n")
    f.write(f"| 強勢多頭 | {len(strong_stocks)} | {min(5, len(strong_stocks))} |\n")
    f.write(f"| 穩健多頭 | {len(steady_stocks)} | {min(5, len(steady_stocks))} |\n")
    f.write(f"| 突破型 | {len(breakout_stocks)} | {min(5, len(breakout_stocks))} |\n\n")

    f.write("---\n\n")

    # 類型一：強勢多頭
    f.write("## 🚀 類型一：強勢多頭股（適合積極投資者）\n\n")
    f.write(f"**符合條件**: {len(strong_stocks)} 檔\n\n")

    f.write("### 選股邏輯\n\n")
    f.write("- ✅ 均線完整多頭排列（MA5 > MA10 > MA20）\n")
    f.write("- ✅ RSI 強勢區間（60-75）\n")
    f.write("- ✅ MACD 黃金交叉且柱狀圖強勁（> 0.05）\n")
    f.write("- ✅ ADX > 30（趨勢非常強勁）\n")
    f.write("- ✅ +DI 明顯大於 -DI（多頭力道強）\n")
    f.write("- ✅ 成交量放大（量比 > 1.3）\n\n")

    if len(strong_stocks) > 0:
        f.write("### 推薦標的\n\n")
        for idx, (i, row) in enumerate(strong_stocks.head(5).iterrows(), 1):
            stock_name = get_stock_name(row['stock_id'])
            f.write(f"#### {idx}. {row['stock_id']} - {stock_name}\n\n")
            f.write(f"**收盤價**: {row['close']:.2f} 元  \n")
            f.write(f"**綜合評分**: {row['total_score']:.2f}  \n\n")

            f.write("**價格資訊**\n\n")
            f.write(f"- 開盤: {row['open']:.2f}\n")
            f.write(f"- 最高: {row['high']:.2f}\n")
            f.write(f"- 最低: {row['low']:.2f}\n")
            f.write(f"- VWAP: {row['vwap']:.2f}\n\n")

            f.write("**技術指標**\n\n")
            f.write(f"| 指標 | 數值 | 狀態 |\n")
            f.write(f"|------|------|------|\n")
            f.write(f"| MA5 | {row['ma_5']:.2f} | 收盤 > MA5 ✓ |\n")
            f.write(f"| MA20 | {row['ma_20']:.2f} | 多頭排列 ✓ |\n")
            f.write(f"| RSI(14) | {row['rsi_14']:.2f} | {'強勢' if row['rsi_14'] > 60 else '偏強'} |\n")
            f.write(f"| MACD 柱狀圖 | {row['macd_hist']:.4f} | 黃金交叉 ✓ |\n")
            f.write(f"| ADX | {row['dmi_adx']:.2f} | {'趨勢強勁' if row['dmi_adx'] > 30 else '趨勢明確'} |\n")
            f.write(f"| 多頭力道 (+DI - -DI) | {row['dmi_pdi'] - row['dmi_mdi']:.2f} | +DI: {row['dmi_pdi']:.2f} |\n")
            f.write(f"| 成交量比率 | {row['vol_ratio']:.2f} | {'放量' if row['vol_ratio'] > 1.2 else '正常'} |\n\n")

            f.write("---\n\n")
    else:
        f.write("目前無符合條件的股票\n\n")

    # 類型二：穩健多頭
    f.write("## 💎 類型二：穩健多頭股（適合穩健投資者）\n\n")
    f.write(f"**符合條件**: {len(steady_stocks)} 檔\n\n")

    f.write("### 選股邏輯\n\n")
    f.write("- ✅ 均線多頭排列（收盤 > MA5 > MA20）\n")
    f.write("- ✅ RSI 中性偏強（50-65）\n")
    f.write("- ✅ MACD 黃金交叉\n")
    f.write("- ✅ ADX > 25（趨勢明確）\n")
    f.write("- ✅ 價格在布林通道中上軌\n")
    f.write("- ✅ 成交量適中（量比 > 1.0）\n\n")

    if len(steady_stocks) > 0:
        f.write("### 推薦標的\n\n")
        for idx, (i, row) in enumerate(steady_stocks.head(5).iterrows(), 1):
            stock_name = get_stock_name(row['stock_id'])
            f.write(f"#### {idx}. {row['stock_id']} - {stock_name}\n\n")
            f.write(f"**收盤價**: {row['close']:.2f} 元  \n")
            f.write(f"**綜合評分**: {row['total_score']:.2f}  \n\n")

            f.write("**技術指標**\n\n")
            f.write(f"| 指標 | 數值 | 狀態 |\n")
            f.write(f"|------|------|------|\n")
            f.write(f"| MA5 | {row['ma_5']:.2f} | 收盤 > MA5 ✓ |\n")
            f.write(f"| MA20 | {row['ma_20']:.2f} | 多頭排列 ✓ |\n")
            f.write(f"| RSI(14) | {row['rsi_14']:.2f} | {'強勢' if row['rsi_14'] > 60 else '偏強'} |\n")
            f.write(f"| MACD 柱狀圖 | {row['macd_hist']:.4f} | 黃金交叉 ✓ |\n")
            f.write(f"| ADX | {row['dmi_adx']:.2f} | {'趨勢強勁' if row['dmi_adx'] > 30 else '趨勢明確'} |\n")
            f.write(f"| 多頭力道 | {row['dmi_pdi'] - row['dmi_mdi']:.2f} | - |\n")
            f.write(f"| 成交量比率 | {row['vol_ratio']:.2f} | {'放量' if row['vol_ratio'] > 1.2 else '正常'} |\n\n")

            f.write("---\n\n")
    else:
        f.write("目前無符合條件的股票\n\n")

    # 類型三：突破型
    f.write("## ⚡ 類型三：突破型股票（適合短線交易者）\n\n")
    f.write(f"**符合條件**: {len(breakout_stocks)} 檔\n\n")

    f.write("### 選股邏輯\n\n")
    f.write("- ✅ 價格突破 MA20\n")
    f.write("- ✅ RSI 快速上升（55-70）\n")
    f.write("- ✅ MACD 剛黃金交叉（柱狀圖 0-0.3）\n")
    f.write("- ✅ ADX 上升中（20-35）\n")
    f.write("- ✅ +DI 快速上升\n")
    f.write("- ✅ 大量突破（量比 > 1.5）\n\n")

    if len(breakout_stocks) > 0:
        f.write("### 推薦標的\n\n")
        for idx, (i, row) in enumerate(breakout_stocks.head(5).iterrows(), 1):
            stock_name = get_stock_name(row['stock_id'])
            f.write(f"#### {idx}. {row['stock_id']} - {stock_name}\n\n")
            f.write(f"**收盤價**: {row['close']:.2f} 元  \n")
            f.write(f"**綜合評分**: {row['total_score']:.2f}  \n\n")

            f.write("**技術指標**\n\n")
            f.write(f"| 指標 | 數值 | 狀態 |\n")
            f.write(f"|------|------|------|\n")
            f.write(f"| RSI(14) | {row['rsi_14']:.2f} | 快速上升 |\n")
            f.write(f"| MACD 柱狀圖 | {row['macd_hist']:.4f} | 剛交叉 |\n")
            f.write(f"| ADX | {row['dmi_adx']:.2f} | 上升中 |\n")
            f.write(f"| 多頭力道 | {row['dmi_pdi'] - row['dmi_mdi']:.2f} | - |\n")
            f.write(f"| 成交量比率 | {row['vol_ratio']:.2f} | 大量突破 |\n\n")

            f.write("---\n\n")
    else:
        f.write("目前無符合條件的股票\n\n")

    # 風險提示
    f.write("## ⚠️ 風險提示與投資建議\n\n")
    f.write("1. 本報告僅供參考，不構成投資建議\n")
    f.write("2. 技術分析需搭配基本面、籌碼面、消息面綜合判斷\n")
    f.write("3. 建議設定停損停利點，控制風險\n")
    f.write("4. 強勢股適合追漲，但需注意回檔風險\n")
    f.write("5. 穩健股適合波段操作，風險相對較低\n")
    f.write("6. 突破股適合短線操作，需嚴格執行停損\n")
    f.write("7. 投資前請詳閱公開資訊觀測站的公司財報\n")
    f.write("8. 投資有風險，請謹慎評估自身風險承受能力\n\n")

    f.write("---\n\n")
    f.write("*本報告由台股資料收集系統自動生成*\n")

print(f"✓ Markdown 報告已生成：{md_file}")

# 生成 CSV
csv_file = output_dir / "股票推薦清單_2026-02-02.csv"
all_recommendations = []

for idx, (i, row) in enumerate(strong_stocks.head(5).iterrows(), 1):
    all_recommendations.append({
        '排名': idx,
        '類型': '強勢多頭',
        '股票代碼': row['stock_id'],
        '股票名稱': get_stock_name(row['stock_id']),
        '收盤價': row['close'],
        'RSI(14)': round(row['rsi_14'], 2),
        'MACD柱狀圖': round(row['macd_hist'], 4),
        'ADX': round(row['dmi_adx'], 2),
        '多頭力道': round(row['dmi_pdi'] - row['dmi_mdi'], 2),
        '量比': round(row['vol_ratio'], 2),
        '綜合評分': round(row['total_score'], 2)
    })

for idx, (i, row) in enumerate(steady_stocks.head(5).iterrows(), 1):
    all_recommendations.append({
        '排名': idx,
        '類型': '穩健多頭',
        '股票代碼': row['stock_id'],
        '股票名稱': get_stock_name(row['stock_id']),
        '收盤價': row['close'],
        'RSI(14)': round(row['rsi_14'], 2),
        'MACD柱狀圖': round(row['macd_hist'], 4),
        'ADX': round(row['dmi_adx'], 2),
        '多頭力道': round(row['dmi_pdi'] - row['dmi_mdi'], 2),
        '量比': round(row['vol_ratio'], 2),
        '綜合評分': round(row['total_score'], 2)
    })

for idx, (i, row) in enumerate(breakout_stocks.head(5).iterrows(), 1):
    all_recommendations.append({
        '排名': idx,
        '類型': '突破型',
        '股票代碼': row['stock_id'],
        '股票名稱': get_stock_name(row['stock_id']),
        '收盤價': row['close'],
        'RSI(14)': round(row['rsi_14'], 2),
        'MACD柱狀圖': round(row['macd_hist'], 4),
        'ADX': round(row['dmi_adx'], 2),
        '多頭力道': round(row['dmi_pdi'] - row['dmi_mdi'], 2),
        '量比': round(row['vol_ratio'], 2),
        '綜合評分': round(row['total_score'], 2)
    })

recommendations_df = pd.DataFrame(all_recommendations)
recommendations_df.to_csv(csv_file, index=False, encoding='utf-8-sig')
print(f"✓ CSV 檔案已生成：{csv_file}")

print("\n" + "=" * 80)
print("Markdown 報告生成完成！")
print("=" * 80)
print(f"\n輸出位置：{output_dir}")
print(f"• Markdown 報告：{md_file.name}")
print(f"• CSV 清單：{csv_file.name}")
