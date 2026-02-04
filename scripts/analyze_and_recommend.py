#!/usr/bin/env python3
"""
綜合分析推薦工具
從多個分析結果中篩選出最佳推薦標的

用法:
    # 從今天的分析結果推薦
    python scripts/analyze_and_recommend.py

    # 從指定日期的分析結果推薦
    python scripts/analyze_and_recommend.py --date 2026-02-03

    # 指定推薦數量
    python scripts/analyze_and_recommend.py --top 10
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
import argparse

# 加入專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class StockRecommender:
    """綜合分析推薦器"""

    def __init__(self, date: str):
        self.date = date
        self.project_root = project_root
        self.results_dir = project_root / 'analysis' / 'results' / date
        self.technical_data_path = project_root / 'data' / 'transformed' / 'technical' / f'{date}_all.csv'

    def load_technical_data(self) -> pd.DataFrame:
        """載入技術指標資料"""
        if not self.technical_data_path.exists():
            print(f"❌ 找不到技術指標資料: {self.technical_data_path}")
            return pd.DataFrame()

        df = pd.read_csv(self.technical_data_path)
        print(f"✓ 載入 {len(df)} 檔股票技術指標")
        return df

    def load_recovery_stocks(self) -> set:
        """載入回後買上漲型態的股票"""
        csv_file = self.results_dir / f'02_回檔買進_回後買上漲型態_{self.date}.csv'
        if not csv_file.exists():
            print(f"⚠️  找不到回後買上漲型態資料")
            return set()

        df = pd.read_csv(csv_file)
        # 只取 4/4 條件的股票
        df_perfect = df[df['passed_conditions'] == 4]
        stocks = set(df_perfect['stock_id'].astype(int))
        print(f"✓ 載入 {len(stocks)} 支回後買上漲型態股票 (4/4)")
        return stocks

    def load_pullback_stocks(self) -> set:
        """載入回檔買進選股器的股票"""
        csv_file = Path.home() / 'Downloads' / '股票推薦' / f'回檔買上漲選股_{self.date}.csv'
        if not csv_file.exists():
            print(f"⚠️  找不到回檔買進選股器資料")
            return set()

        df = pd.read_csv(csv_file)
        stocks = set(df['stock_id'].astype(int))
        print(f"✓ 載入 {len(stocks)} 支回檔買進選股器股票")
        return stocks

    def calculate_score(self, row: pd.Series) -> float:
        """
        計算綜合評分

        評分標準:
        - RSI (30-70 最佳): 20分
        - MACD 柱狀圖 > 0: 20分
        - ADX > 25: 20分
        - 量比 1.0-2.0: 20分
        - 收盤 > MA5 > MA20: 20分
        """
        score = 0.0

        # RSI 評分 (30-70 最佳)
        rsi = row.get('rsi_14', 50)
        if 40 <= rsi <= 60:
            score += 20
        elif 30 <= rsi <= 70:
            score += 15
        elif 20 <= rsi <= 80:
            score += 10

        # MACD 評分
        macd_hist = row.get('macd_hist', 0)
        if macd_hist > 0:
            score += 20
        elif macd_hist > -0.5:
            score += 10

        # ADX 評分 (趨勢強度)
        adx = row.get('dmi_adx', 0)
        if adx > 40:
            score += 20
        elif adx > 25:
            score += 15
        elif adx > 20:
            score += 10

        # 量比評分
        vol_ratio = row.get('vol_ratio', 1.0)
        if 1.0 <= vol_ratio <= 2.0:
            score += 20
        elif 0.8 <= vol_ratio <= 3.0:
            score += 15
        elif vol_ratio > 0.5:
            score += 10

        # 均線排列評分
        close = row.get('close', 0)
        ma5 = row.get('ma_5', 0)
        ma20 = row.get('ma_20', 0)

        if close > ma5 > ma20:
            score += 20
        elif close > ma5:
            score += 15
        elif close > ma20:
            score += 10

        return score

    def generate_recommendation(self, top_n: int = 20) -> pd.DataFrame:
        """生成推薦清單"""
        print(f"\n{'='*80}")
        print(f"綜合分析推薦 - {self.date}")
        print(f"{'='*80}\n")

        # 載入資料
        technical_df = self.load_technical_data()
        if technical_df.empty:
            return pd.DataFrame()

        recovery_stocks = self.load_recovery_stocks()
        pullback_stocks = self.load_pullback_stocks()

        # 找出共同推薦的股票
        common_stocks = recovery_stocks & pullback_stocks
        print(f"\n✨ 兩個分析共同推薦: {len(common_stocks)} 支")

        # 合併所有候選股票
        all_candidates = recovery_stocks | pullback_stocks
        print(f"📊 總候選股票: {len(all_candidates)} 支\n")

        # 篩選技術指標資料
        technical_df['stock_id'] = technical_df['stock_id'].astype(int)
        candidates_df = technical_df[technical_df['stock_id'].isin(all_candidates)].copy()

        # 計算評分
        candidates_df['score'] = candidates_df.apply(self.calculate_score, axis=1)

        # 標記來源
        candidates_df['in_recovery'] = candidates_df['stock_id'].isin(recovery_stocks)
        candidates_df['in_pullback'] = candidates_df['stock_id'].isin(pullback_stocks)
        candidates_df['in_both'] = candidates_df['stock_id'].isin(common_stocks)

        # 共同推薦的加分
        candidates_df.loc[candidates_df['in_both'], 'score'] += 10

        # 排序
        result_df = candidates_df.sort_values('score', ascending=False).head(top_n)

        return result_df

    def display_recommendation(self, df: pd.DataFrame):
        """顯示推薦結果"""
        if df.empty:
            print("❌ 沒有推薦結果")
            return

        print(f"\n{'='*80}")
        print(f"🏆 TOP {len(df)} 推薦股票")
        print(f"{'='*80}\n")

        for idx, (_, row) in enumerate(df.iterrows(), 1):
            stock_id = int(row['stock_id'])
            score = row['score']

            # 標記來源
            sources = []
            if row['in_both']:
                sources.append("⭐兩者皆推薦")
            else:
                if row['in_recovery']:
                    sources.append("回後買上漲")
                if row['in_pullback']:
                    sources.append("回檔買進")

            source_str = " + ".join(sources)

            print(f"【第 {idx} 名】{stock_id} - 評分: {score:.0f}/110")
            print(f"  來源: {source_str}")
            print(f"  收盤: {row['close']:.2f} | MA5: {row['ma_5']:.2f} | MA20: {row['ma_20']:.2f}")
            print(f"  RSI: {row['rsi_14']:.2f} | MACD: {row['macd_hist']:.4f} | ADX: {row['dmi_adx']:.2f}")
            print(f"  成交量: {int(row['volume']):,} | 量比: {row['vol_ratio']:.2f}")

            # 評分細節
            print(f"  評分分析:")

            # RSI
            rsi = row['rsi_14']
            if 40 <= rsi <= 60:
                print(f"    RSI {rsi:.1f} ✓ (理想區間)")
            elif 30 <= rsi <= 70:
                print(f"    RSI {rsi:.1f} ○ (正常)")
            else:
                print(f"    RSI {rsi:.1f} {'(超買)' if rsi > 70 else '(超賣)'}")

            # MACD
            macd = row['macd_hist']
            print(f"    MACD {macd:.4f} {'✓ (多頭)' if macd > 0 else '✗ (空頭)'}")

            # ADX
            adx = row['dmi_adx']
            if adx > 40:
                print(f"    ADX {adx:.1f} ✓ (強趨勢)")
            elif adx > 25:
                print(f"    ADX {adx:.1f} ○ (中等趨勢)")
            else:
                print(f"    ADX {adx:.1f} ✗ (弱趨勢)")

            # 量比
            vol_ratio = row['vol_ratio']
            if 1.0 <= vol_ratio <= 2.0:
                print(f"    量比 {vol_ratio:.2f} ✓ (理想)")
            elif vol_ratio > 2.0:
                print(f"    量比 {vol_ratio:.2f} ! (爆量)")
            else:
                print(f"    量比 {vol_ratio:.2f} ○ (縮量)")

            # 均線排列
            close, ma5, ma20 = row['close'], row['ma_5'], row['ma_20']
            if close > ma5 > ma20:
                print(f"    均線排列 ✓ (多頭排列)")
            elif close > ma5:
                print(f"    均線排列 ○ (站上短均)")
            else:
                print(f"    均線排列 ✗ (空頭)")

            print(f"\n{'-'*80}\n")

    def export_recommendation(self, df: pd.DataFrame):
        """匯出推薦結果"""
        if df.empty:
            return

        output_dir = self.results_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        # 選擇輸出欄位
        output_columns = [
            'stock_id', 'score', 'close', 'open', 'high', 'low', 'volume',
            'ma_5', 'ma_10', 'ma_20', 'ma_60',
            'rsi_14', 'macd_hist', 'dmi_adx', 'vol_ratio',
            'in_recovery', 'in_pullback', 'in_both'
        ]

        export_df = df[[col for col in output_columns if col in df.columns]]

        # 匯出 CSV
        csv_file = output_dir / f'05_綜合推薦_{self.date}.csv'
        export_df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"\n✅ 推薦結果已匯出: {csv_file}")


def main():
    parser = argparse.ArgumentParser(
        description='綜合分析推薦工具',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--date',
        default=None,
        help='分析日期 (YYYY-MM-DD)，預設為今天'
    )

    parser.add_argument(
        '--top',
        type=int,
        default=20,
        help='推薦數量，預設 20'
    )

    args = parser.parse_args()

    # 設定日期
    if args.date:
        date = args.date
    else:
        date = datetime.now().strftime('%Y-%m-%d')

    print(f"\n📊 開始綜合分析推薦...")
    print(f"日期: {date}")
    print(f"推薦數量: TOP {args.top}\n")

    # 執行推薦
    recommender = StockRecommender(date)
    result_df = recommender.generate_recommendation(top_n=args.top)

    if not result_df.empty:
        recommender.display_recommendation(result_df)
        recommender.export_recommendation(result_df)
    else:
        print("❌ 無法產生推薦結果")


if __name__ == '__main__':
    main()
