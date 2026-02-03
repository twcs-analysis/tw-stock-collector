#!/usr/bin/env python3
"""
2026-02-02 股票推薦分析
根據技術指標篩選適合的標的並生成詳細報告
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

# 讀取 2026-02-02 的技術指標資料
data_path = Path(__file__).parent.parent.parent / "data/transformed/technical/2026-02-02_all.csv"
df = pd.read_csv(data_path)

print(f"載入 2026-02-02 技術指標資料，總共 {len(df)} 檔股票\n")

# 從資料庫查詢股票名稱（如果無法連接則使用代碼）
try:
    import psycopg2
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="tw_stock",
        user="postgres",
        password="tw_stock_dev_password_2024"
    )

    # 取得股票代碼和名稱的對應
    query = "SELECT DISTINCT stock_id, stock_name FROM stock_prices ORDER BY stock_id"
    stock_names = pd.read_sql(query, conn)
    stock_name_dict = dict(zip(stock_names['stock_id'], stock_names['stock_name']))
    conn.close()
    print(f"成功從資料庫載入 {len(stock_name_dict)} 檔股票名稱\n")
except Exception as e:
    print(f"無法連接資料庫，將使用股票代碼: {e}\n")
    stock_name_dict = {}

# 定義多頭選股條件
# 基於 transcript 中的技術指標邏輯

# 條件 1: 強勢多頭（適合積極投資者）
strong_bullish = (
    # 均線多頭排列
    (df['close'] > df['ma_5']) &
    (df['ma_5'] > df['ma_10']) &
    (df['ma_10'] > df['ma_20']) &

    # RSI 強勢（60-75）
    (df['rsi_14'] >= 60) &
    (df['rsi_14'] <= 75) &

    # MACD 黃金交叉且柱狀圖強勁
    (df['macd_dif'] > df['macd_dea']) &
    (df['macd_hist'] > 0.05) &

    # ADX > 30（趨勢非常強勁）
    (df['dmi_adx'] > 30) &

    # +DI 明顯大於 -DI
    (df['dmi_pdi'] > df['dmi_mdi'] + 15) &

    # 價格接近布林通道上軌（強勢）
    (df['close'] > df['bb_mid']) &

    # 成交量放大
    (df['vol_ratio'] > 1.3) &

    # 排除 ETF 和小型股
    (~df['stock_id'].astype(str).str.startswith('0')) &
    (df['volume'] > 1000000)
)

# 條件 2: 穩健多頭（適合穩健投資者）
steady_bullish = (
    # 均線多頭排列
    (df['close'] > df['ma_5']) &
    (df['ma_5'] > df['ma_20']) &

    # RSI 中性偏強（50-65）
    (df['rsi_14'] >= 50) &
    (df['rsi_14'] <= 65) &

    # MACD 黃金交叉
    (df['macd_dif'] > df['macd_dea']) &
    (df['macd_hist'] > 0) &

    # ADX > 25（趨勢明確）
    (df['dmi_adx'] > 25) &

    # +DI > -DI
    (df['dmi_pdi'] > df['dmi_mdi']) &

    # 價格在布林通道中軌之上
    (df['close'] > df['bb_mid']) &
    (df['close'] < df['bb_upper']) &

    # 成交量適中
    (df['vol_ratio'] > 1.0) &

    # 排除 ETF 和小型股
    (~df['stock_id'].astype(str).str.startswith('0')) &
    (df['volume'] > 1000000)
)

# 條件 3: 突破型（適合短線交易者）
breakout = (
    # 價格突破均線
    (df['close'] > df['ma_20']) &

    # RSI 快速上升（55-70）
    (df['rsi_14'] >= 55) &
    (df['rsi_14'] <= 70) &

    # MACD 剛黃金交叉
    (df['macd_dif'] > df['macd_dea']) &
    (df['macd_hist'] > 0) &
    (df['macd_hist'] < 0.3) &  # 剛交叉不久

    # ADX 上升中（20-35）
    (df['dmi_adx'] > 20) &
    (df['dmi_adx'] < 35) &

    # +DI 快速上升
    (df['dmi_pdi'] > df['dmi_mdi'] + 10) &

    # 突破布林通道中軌
    (df['close'] > df['bb_mid']) &

    # 大量突破
    (df['vol_ratio'] > 1.5) &

    # 排除 ETF 和小型股
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

    # RSI 評分（60 分最佳）
    stocks_df['rsi_score'] = 100 - abs(stocks_df['rsi_14'] - 60)

    # MACD 評分
    stocks_df['macd_score'] = stocks_df['macd_hist'] * 20

    # ADX 評分
    stocks_df['adx_score'] = stocks_df['dmi_adx']

    # DMI 評分（多頭力道）
    stocks_df['dmi_score'] = stocks_df['dmi_pdi'] - stocks_df['dmi_mdi']

    # 成交量評分
    stocks_df['vol_score'] = (stocks_df['vol_ratio'] - 1) * 30

    # 均線排列評分（短均線相對長均線的位置）
    stocks_df['ma_score'] = ((stocks_df['ma_5'] - stocks_df['ma_20']) / stocks_df['ma_20']) * 100

    # 綜合評分
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

# 生成報告
output_dir = Path.home() / "Downloads" / "股票推薦"
output_dir.mkdir(parents=True, exist_ok=True)

report_file = output_dir / f"股票推薦報告_2026-02-02.txt"
csv_file = output_dir / f"股票推薦清單_2026-02-02.csv"

def get_stock_name(stock_id):
    """取得股票名稱"""
    return stock_name_dict.get(stock_id, stock_id)

def format_stock_info(row, rank):
    """格式化股票資訊"""
    stock_id = row['stock_id']
    stock_name = get_stock_name(stock_id)

    info = f"""
{'=' * 80}
【第 {rank} 名】{stock_id} - {stock_name}
{'=' * 80}

▸ 價格資訊
  收盤價：{row['close']:.2f}
  開盤價：{row['open']:.2f} | 最高價：{row['high']:.2f} | 最低價：{row['low']:.2f}
  VWAP（成交均價）：{row['vwap']:.2f}

▸ 均線分析（多頭排列）
  MA5：  {row['ma_5']:.2f}  {'✓ 收盤價在 MA5 之上' if row['close'] > row['ma_5'] else ''}
  MA10： {row['ma_10']:.2f}  {'✓ MA5 在 MA10 之上' if row['ma_5'] > row['ma_10'] else ''}
  MA20： {row['ma_20']:.2f}  {'✓ MA10 在 MA20 之上' if row['ma_10'] > row['ma_20'] else ''}
  MA60： {row['ma_60']:.2f}

▸ 動能指標
  RSI(14)：{row['rsi_14']:.2f}  {'[強勢]' if row['rsi_14'] > 60 else '[偏強]' if row['rsi_14'] > 50 else ''}
  RSI(6)： {row['rsi_6']:.2f}

▸ MACD 指標（黃金交叉）
  DIF：  {row['macd_dif']:.4f}
  DEA：  {row['macd_dea']:.4f}
  HIST： {row['macd_hist']:.4f}  ✓ 黃金交叉（DIF > DEA）

▸ DMI/ADX 趨勢指標
  +DI：  {row['dmi_pdi']:.2f}  ✓ 多方力道
  -DI：  {row['dmi_mdi']:.2f}
  ADX：  {row['dmi_adx']:.2f}  {'[趨勢強勁]' if row['dmi_adx'] > 30 else '[趨勢明確]' if row['dmi_adx'] > 25 else '[趨勢形成中]'}
  多頭力道：{row['dmi_pdi'] - row['dmi_mdi']:.2f}

▸ 布林通道
  上軌：{row['bb_upper']:.2f}
  中軌：{row['bb_mid']:.2f}  {'✓ 收盤價在中軌之上' if row['close'] > row['bb_mid'] else ''}
  下軌：{row['bb_lower']:.2f}

▸ 成交量分析
  成交量：{int(row['volume']):,}
  5日均量： {int(row['vol_ma5']):,}
  20日均量：{int(row['vol_ma20']):,}
  量比：{row['vol_ratio']:.2f}  {'✓ 放量' if row['vol_ratio'] > 1.2 else ''}

▸ 綜合評分：{row['total_score']:.2f}

"""
    return info

# 寫入報告
with open(report_file, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("台股技術分析推薦報告\n")
    f.write("=" * 80 + "\n")
    f.write(f"分析日期：2026-02-02\n")
    f.write(f"報告生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"資料來源：台股技術指標資料庫\n")
    f.write("=" * 80 + "\n\n")

    # 強勢多頭推薦
    f.write("\n" + "█" * 80 + "\n")
    f.write("【類型一】強勢多頭股（適合積極投資者）\n")
    f.write("█" * 80 + "\n")
    f.write(f"\n符合條件：{len(strong_stocks)} 檔\n")
    f.write("\n選股邏輯：\n")
    f.write("• 均線完整多頭排列（MA5 > MA10 > MA20）\n")
    f.write("• RSI 強勢區間（60-75）\n")
    f.write("• MACD 黃金交叉且柱狀圖強勁（> 0.05）\n")
    f.write("• ADX > 30（趨勢非常強勁）\n")
    f.write("• +DI 明顯大於 -DI（多頭力道強）\n")
    f.write("• 成交量放大（量比 > 1.3）\n")

    if len(strong_stocks) > 0:
        f.write("\n推薦前 5 名：\n")
        for idx, (i, row) in enumerate(strong_stocks.head(5).iterrows(), 1):
            f.write(format_stock_info(row, idx))
    else:
        f.write("\n目前無符合條件的股票\n")

    # 穩健多頭推薦
    f.write("\n\n" + "█" * 80 + "\n")
    f.write("【類型二】穩健多頭股（適合穩健投資者）\n")
    f.write("█" * 80 + "\n")
    f.write(f"\n符合條件：{len(steady_stocks)} 檔\n")
    f.write("\n選股邏輯：\n")
    f.write("• 均線多頭排列（收盤 > MA5 > MA20）\n")
    f.write("• RSI 中性偏強（50-65）\n")
    f.write("• MACD 黃金交叉\n")
    f.write("• ADX > 25（趨勢明確）\n")
    f.write("• 價格在布林通道中上軌\n")
    f.write("• 成交量適中（量比 > 1.0）\n")

    if len(steady_stocks) > 0:
        f.write("\n推薦前 5 名：\n")
        for idx, (i, row) in enumerate(steady_stocks.head(5).iterrows(), 1):
            f.write(format_stock_info(row, idx))
    else:
        f.write("\n目前無符合條件的股票\n")

    # 突破型推薦
    f.write("\n\n" + "█" * 80 + "\n")
    f.write("【類型三】突破型股票（適合短線交易者）\n")
    f.write("█" * 80 + "\n")
    f.write(f"\n符合條件：{len(breakout_stocks)} 檔\n")
    f.write("\n選股邏輯：\n")
    f.write("• 價格突破 MA20\n")
    f.write("• RSI 快速上升（55-70）\n")
    f.write("• MACD 剛黃金交叉（柱狀圖 0-0.3）\n")
    f.write("• ADX 上升中（20-35）\n")
    f.write("• +DI 快速上升\n")
    f.write("• 大量突破（量比 > 1.5）\n")

    if len(breakout_stocks) > 0:
        f.write("\n推薦前 5 名：\n")
        for idx, (i, row) in enumerate(breakout_stocks.head(5).iterrows(), 1):
            f.write(format_stock_info(row, idx))
    else:
        f.write("\n目前無符合條件的股票\n")

    # 風險提示
    f.write("\n\n" + "=" * 80 + "\n")
    f.write("【風險提示與投資建議】\n")
    f.write("=" * 80 + "\n\n")
    f.write("1. 本報告僅供參考，不構成投資建議\n")
    f.write("2. 技術分析需搭配基本面、籌碼面、消息面綜合判斷\n")
    f.write("3. 建議設定停損停利點，控制風險\n")
    f.write("4. 強勢股適合追漲，但需注意回檔風險\n")
    f.write("5. 穩健股適合波段操作，風險相對較低\n")
    f.write("6. 突破股適合短線操作，需嚴格執行停損\n")
    f.write("7. 投資前請詳閱公開資訊觀測站的公司財報\n")
    f.write("8. 投資有風險，請謹慎評估自身風險承受能力\n\n")

print(f"✓ 報告已生成：{report_file}")

# 生成 CSV 檔案（方便 Excel 開啟）
all_recommendations = []

for idx, (i, row) in enumerate(strong_stocks.head(5).iterrows(), 1):
    all_recommendations.append({
        '排名': idx,
        '類型': '強勢多頭',
        '股票代碼': row['stock_id'],
        '股票名稱': get_stock_name(row['stock_id']),
        '收盤價': row['close'],
        'RSI(14)': row['rsi_14'],
        'MACD柱狀圖': row['macd_hist'],
        'ADX': row['dmi_adx'],
        '多頭力道': row['dmi_pdi'] - row['dmi_mdi'],
        '量比': row['vol_ratio'],
        '綜合評分': row['total_score']
    })

for idx, (i, row) in enumerate(steady_stocks.head(5).iterrows(), 1):
    all_recommendations.append({
        '排名': idx,
        '類型': '穩健多頭',
        '股票代碼': row['stock_id'],
        '股票名稱': get_stock_name(row['stock_id']),
        '收盤價': row['close'],
        'RSI(14)': row['rsi_14'],
        'MACD柱狀圖': row['macd_hist'],
        'ADX': row['dmi_adx'],
        '多頭力道': row['dmi_pdi'] - row['dmi_mdi'],
        '量比': row['vol_ratio'],
        '綜合評分': row['total_score']
    })

for idx, (i, row) in enumerate(breakout_stocks.head(5).iterrows(), 1):
    all_recommendations.append({
        '排名': idx,
        '類型': '突破型',
        '股票代碼': row['stock_id'],
        '股票名稱': get_stock_name(row['stock_id']),
        '收盤價': row['close'],
        'RSI(14)': row['rsi_14'],
        'MACD柱狀圖': row['macd_hist'],
        'ADX': row['dmi_adx'],
        '多頭力道': row['dmi_pdi'] - row['dmi_mdi'],
        '量比': row['vol_ratio'],
        '綜合評分': row['total_score']
    })

recommendations_df = pd.DataFrame(all_recommendations)
recommendations_df.to_csv(csv_file, index=False, encoding='utf-8-sig')
print(f"✓ CSV 檔案已生成：{csv_file}")

print("\n" + "=" * 80)
print("分析完成！")
print("=" * 80)
print(f"\n輸出位置：{output_dir}")
print(f"• 詳細報告：{report_file.name}")
print(f"• CSV 清單：{csv_file.name}")
