"""
回後買上漲型態篩選器

篩選條件：
A. 股票型態是否為「頭頭高 底底高」（上升趨勢）
B. 股價是否在月線之上且前低未破
C. 今日紅 K 是否站上 5 均
D. 收盤是否過昨日高

使用方式:
    python analysis/filter_recovery_stocks.py --date 2026-02-02
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import argparse
import sys

# 加入專案根目錄到 sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from services.common.utils.logger import setup_logger

logger = setup_logger(__name__)


class RecoveryStockFilter:
    """回後買上漲型態篩選器"""

    def __init__(self, base_date: str):
        """
        初始化篩選器

        Args:
            base_date: 分析基準日期 (YYYY-MM-DD)
        """
        self.base_date = base_date
        self.data_dir = project_root / 'data' / 'transformed' / 'technical'
        self.min_conditions = 4  # 預設需要所有條件都符合

    def load_historical_data(self, days: int = 20) -> pd.DataFrame:
        """
        載入歷史技術指標資料

        Args:
            days: 需要載入的歷史天數

        Returns:
            合併的歷史資料 DataFrame
        """
        all_data = []
        base_dt = datetime.strptime(self.base_date, '%Y-%m-%d')

        # 往前推 days*2 天（因為有非交易日）
        for i in range(days * 2):
            check_date = base_dt - timedelta(days=i)
            file_path = self.data_dir / f"{check_date.strftime('%Y-%m-%d')}_all.csv"

            if file_path.exists():
                df = pd.read_csv(file_path)
                df['trade_date'] = pd.to_datetime(df['trade_date'])
                all_data.append(df)

                # 收集到足夠的交易日就停止
                if len(all_data) >= days:
                    break

        if not all_data:
            raise FileNotFoundError(f"找不到 {self.base_date} 附近的技術指標資料")

        # 合併並排序
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df = combined_df.sort_values(['stock_id', 'trade_date'])

        logger.info(f"載入了 {len(all_data)} 個交易日的資料")
        return combined_df

    def find_peaks_and_troughs(self, prices: pd.Series, window: int = 5) -> tuple:
        """
        尋找價格的高點和低點

        Args:
            prices: 價格序列
            window: 檢測窗口大小

        Returns:
            (peaks, troughs) - 高點和低點的索引列表
        """
        peaks = []
        troughs = []

        if len(prices) < window * 2 + 1:
            return peaks, troughs

        for i in range(window, len(prices) - window):
            current_value = prices.iloc[i]

            # 高點：當前值大於左右 window 個值
            left_max = prices.iloc[i-window:i].max()
            right_max = prices.iloc[i+1:i+window+1].max()
            if current_value > left_max and current_value > right_max:
                peaks.append(i)

            # 低點：當前值小於左右 window 個值
            left_min = prices.iloc[i-window:i].min()
            right_min = prices.iloc[i+1:i+window+1].min()
            if current_value < left_min and current_value < right_min:
                troughs.append(i)

        return peaks, troughs

    def check_condition_a(self, stock_data: pd.DataFrame) -> bool:
        """
        條件 A：股票型態是否為「頭頭高 底底高」（上升趨勢）

        簡化邏輯：檢查最近 5 天的趨勢
        - 最近 5 天的最高價整體呈上升趨勢
        - 最近 5 天的最低價整體呈上升趨勢
        """
        if len(stock_data) < 10:
            return False

        # 取最近 10 天資料
        recent_data = stock_data.tail(10)

        # 簡化版：比較前 5 天與後 5 天
        first_half = recent_data.head(5)
        second_half = recent_data.tail(5)

        # 後半段的平均高點 > 前半段的平均高點
        avg_high_first = first_half['high'].mean()
        avg_high_second = second_half['high'].mean()

        # 後半段的平均低點 > 前半段的平均低點
        avg_low_first = first_half['low'].mean()
        avg_low_second = second_half['low'].mean()

        return avg_high_second > avg_high_first and avg_low_second > avg_low_first

    def check_condition_b(self, stock_data: pd.DataFrame) -> bool:
        """
        條件 B：股價是否在月線之上且前低未破

        - 今日收盤 > ma_20（月線）
        - 近期最低點高於前一個低點（前低未破）
        """
        latest = stock_data.iloc[-1]

        # 檢查是否在月線之上
        if pd.isna(latest['ma_20']) or latest['close'] <= latest['ma_20']:
            return False

        # 檢查前低未破
        if len(stock_data) < 10:
            return False

        low_prices = stock_data['low'].reset_index(drop=True)
        _, troughs = self.find_peaks_and_troughs(low_prices, window=3)

        # 需要至少 2 個低點
        if len(troughs) < 2:
            return False

        # 最近的低點要高於前一個低點
        recent_low = low_prices.iloc[troughs[-1]]
        previous_low = low_prices.iloc[troughs[-2]]

        return recent_low > previous_low

    def check_condition_c(self, stock_data: pd.DataFrame) -> bool:
        """
        條件 C：今日紅 K 是否站上 5 均

        - 紅 K：收盤 > 開盤
        - 站上 5 均：收盤 > ma_5
        """
        latest = stock_data.iloc[-1]

        # 檢查紅 K
        is_red_candle = latest['close'] > latest['open']

        # 檢查站上 5 均
        if pd.isna(latest['ma_5']):
            return False

        above_ma5 = latest['close'] > latest['ma_5']

        return is_red_candle and above_ma5

    def check_condition_d(self, stock_data: pd.DataFrame) -> bool:
        """
        條件 D：收盤是否過昨日高

        - 今日收盤 > 昨日最高價
        """
        if len(stock_data) < 2:
            return False

        today = stock_data.iloc[-1]
        yesterday = stock_data.iloc[-2]

        return today['close'] > yesterday['high']

    def filter_stocks(self, show_stats: bool = True) -> pd.DataFrame:
        """
        執行完整的篩選流程

        Args:
            show_stats: 是否顯示各條件的統計資訊

        Returns:
            符合條件的股票 DataFrame
        """
        logger.info(f"開始篩選 {self.base_date} 的回後買上漲型態股票")

        # 載入歷史資料
        df = self.load_historical_data(days=20)

        # 僅保留目標日期的資料作為最終輸出基準
        target_date = pd.to_datetime(self.base_date)
        today_data = df[df['trade_date'] == target_date].copy()

        if len(today_data) == 0:
            logger.warning(f"找不到 {self.base_date} 的資料")
            return pd.DataFrame()

        logger.info(f"共有 {len(today_data)} 支股票待篩選")

        # 對每支股票進行條件檢查
        results = []
        condition_stats = {
            'condition_a': 0,
            'condition_b': 0,
            'condition_c': 0,
            'condition_d': 0,
        }

        for stock_id in today_data['stock_id'].unique():
            stock_historical = df[df['stock_id'] == stock_id].copy()
            stock_historical = stock_historical.sort_values('trade_date')

            # 確保有今天的資料
            if stock_historical.iloc[-1]['trade_date'] != target_date:
                continue

            # 檢查四個條件
            conditions = {
                'condition_a_higher_highs_lows': self.check_condition_a(stock_historical),
                'condition_b_above_ma20_low_hold': self.check_condition_b(stock_historical),
                'condition_c_red_above_ma5': self.check_condition_c(stock_historical),
                'condition_d_break_yesterday_high': self.check_condition_d(stock_historical),
            }

            # 統計各條件通過數量
            if conditions['condition_a_higher_highs_lows']:
                condition_stats['condition_a'] += 1
            if conditions['condition_b_above_ma20_low_hold']:
                condition_stats['condition_b'] += 1
            if conditions['condition_c_red_above_ma5']:
                condition_stats['condition_c'] += 1
            if conditions['condition_d_break_yesterday_high']:
                condition_stats['condition_d'] += 1

            # 計算符合條件的數量
            passed_count = sum(conditions.values())

            # 根據設定的最小條件數來決定是否加入結果
            if passed_count >= self.min_conditions:
                today_info = stock_historical.iloc[-1].to_dict()
                today_info.update(conditions)
                today_info['passed_conditions'] = passed_count
                results.append(today_info)

        # 顯示統計資訊
        if show_stats:
            total_stocks = len(today_data)
            logger.info(f"\n各條件通過統計:")
            logger.info(f"  條件 A (頭頭高底底高): {condition_stats['condition_a']}/{total_stocks} ({condition_stats['condition_a']/total_stocks*100:.1f}%)")
            logger.info(f"  條件 B (在月線上且前低未破): {condition_stats['condition_b']}/{total_stocks} ({condition_stats['condition_b']/total_stocks*100:.1f}%)")
            logger.info(f"  條件 C (紅K站上5均): {condition_stats['condition_c']}/{total_stocks} ({condition_stats['condition_c']/total_stocks*100:.1f}%)")
            logger.info(f"  條件 D (收盤過昨高): {condition_stats['condition_d']}/{total_stocks} ({condition_stats['condition_d']/total_stocks*100:.1f}%)")

        if not results:
            logger.info(f"沒有找到符合至少 {self.min_conditions} 個條件的股票")
            return pd.DataFrame()

        result_df = pd.DataFrame(results)
        # 依照符合條件數排序
        result_df = result_df.sort_values('passed_conditions', ascending=False)

        logger.info(f"找到 {len(result_df)} 支符合至少 {self.min_conditions} 個條件的股票")

        return result_df

    def export_results(self, result_df: pd.DataFrame, output_file: str = None):
        """
        匯出篩選結果

        Args:
            result_df: 結果 DataFrame
            output_file: 輸出檔案路徑（預設自動產生）
        """
        if len(result_df) == 0:
            logger.info("沒有結果需要匯出")
            return

        if output_file is None:
            output_dir = project_root / 'analysis' / 'results'
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"recovery_stocks_{self.base_date}.csv"

        # 選擇重要欄位輸出
        output_columns = [
            'trade_date', 'stock_id', 'passed_conditions',
            'close', 'open', 'high', 'low', 'volume',
            'ma_5', 'ma_20', 'ma_60',
            'rsi_14', 'macd_hist',
            'condition_a_higher_highs_lows',
            'condition_b_above_ma20_low_hold',
            'condition_c_red_above_ma5',
            'condition_d_break_yesterday_high',
        ]

        available_columns = [col for col in output_columns if col in result_df.columns]
        export_df = result_df[available_columns]

        export_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        logger.info(f"結果已匯出至: {output_file}")

        # 顯示簡易摘要
        print("\n" + "="*60)
        print(f"篩選日期: {self.base_date}")
        print(f"符合條件股票數: {len(result_df)}")
        print("="*60)
        print("\n股票清單:")
        for idx, row in export_df.iterrows():
            passed = int(row.get('passed_conditions', 4))
            stock_id = str(row['stock_id'])
            close = float(row['close'])
            ma5 = float(row['ma_5']) if pd.notna(row['ma_5']) else 0.0
            ma20 = float(row['ma_20']) if pd.notna(row['ma_20']) else 0.0
            print(f"  {stock_id:>6s} [{passed}/4]  收盤: {close:>7.2f}  "
                  f"5MA: {ma5:>7.2f}  20MA: {ma20:>7.2f}")
        print("="*60 + "\n")


def main():
    """主程式"""
    parser = argparse.ArgumentParser(description='回後買上漲型態股票篩選器')
    parser.add_argument(
        '--date',
        type=str,
        default='2026-02-02',
        help='分析基準日期 (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='輸出檔案路徑（選填，預設自動產生）'
    )
    parser.add_argument(
        '--min-conditions',
        type=int,
        default=4,
        help='至少符合幾個條件（1-4，預設 4 表示全部符合）'
    )

    args = parser.parse_args()

    # 執行篩選
    filter_engine = RecoveryStockFilter(base_date=args.date)
    filter_engine.min_conditions = args.min_conditions
    result_df = filter_engine.filter_stocks()
    filter_engine.export_results(result_df, output_file=args.output)


if __name__ == '__main__':
    main()
