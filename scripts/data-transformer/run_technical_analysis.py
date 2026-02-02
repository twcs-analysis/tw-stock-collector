#!/usr/bin/env python3
"""
技術分析轉換腳本

功能：
- 計算指定日期的技術指標
- 支援單日或日期區間轉換
- 自動載入資料庫資料並計算 30 個技術指標
- 輸出結果到終端或檔案

使用方式：
    # 轉換單日資料
    python scripts/data-transformer/run_technical_analysis.py --date 2026-02-02

    # 轉換日期區間
    python scripts/data-transformer/run_technical_analysis.py --start 2026-01-01 --end 2026-01-31

    # 轉換特定股票
    python scripts/data-transformer/run_technical_analysis.py --date 2026-02-02 --stock-id 2330

    # 輸出到檔案
    python scripts/data-transformer/run_technical_analysis.py --date 2026-02-02 --output result.csv

依賴：
- PostgreSQL 資料庫已啟動並包含價格資料
- services/data-transformer 模組
- services/common 共用模組
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import os

# 設定專案路徑
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
services_path = project_root / 'services'

# 加入路徑
sys.path.insert(0, str(services_path))
sys.path.insert(0, str(services_path / 'data-transformer'))

# 設定資料庫環境變數（如果未設定）
if 'DB_PASSWORD' not in os.environ:
    os.environ.setdefault('DB_TYPE', 'postgresql')
    os.environ.setdefault('DB_HOST', 'localhost')
    os.environ.setdefault('DB_PORT', '5432')
    os.environ.setdefault('DB_NAME', 'tw_stock')
    os.environ.setdefault('DB_USER', 'postgres')
    os.environ.setdefault('DB_PASSWORD', 'tw_stock_dev_password_2024')

from app.technical_analysis_transformer import TechnicalAnalysisTransformer
from common.utils import get_logger

logger = get_logger(__name__)


def parse_args():
    """解析命令列參數"""
    parser = argparse.ArgumentParser(
        description='技術分析轉換工具 - 計算股票技術指標',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例：
  # 轉換單日資料
  %(prog)s --date 2026-02-02

  # 轉換日期區間
  %(prog)s --start 2026-01-01 --end 2026-01-31

  # 轉換特定股票
  %(prog)s --date 2026-02-02 --stock-id 2330

  # 輸出到檔案
  %(prog)s --date 2026-02-02 --output result.csv
        """
    )

    # 日期參數
    date_group = parser.add_mutually_exclusive_group(required=True)
    date_group.add_argument(
        '--date',
        type=str,
        help='轉換單日資料 (格式: YYYY-MM-DD)'
    )
    date_group.add_argument(
        '--start',
        type=str,
        help='起始日期 (格式: YYYY-MM-DD，需搭配 --end 使用)'
    )

    parser.add_argument(
        '--end',
        type=str,
        help='結束日期 (格式: YYYY-MM-DD，需搭配 --start 使用)'
    )

    # 篩選參數
    parser.add_argument(
        '--stock-id',
        type=str,
        help='指定股票代碼 (例: 2330)'
    )

    # 輸出參數
    parser.add_argument(
        '--output',
        type=str,
        help='輸出檔案路徑 (支援 .csv 或 .json)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='顯示詳細日誌'
    )

    parser.add_argument(
        '--show-sample',
        type=int,
        default=10,
        help='顯示前 N 筆結果 (預設: 10)'
    )

    args = parser.parse_args()

    # 驗證參數
    if args.start and not args.end:
        parser.error('--start 需要搭配 --end 使用')
    if args.end and not args.start:
        parser.error('--end 需要搭配 --start 使用')

    return args


def validate_date(date_str: str) -> bool:
    """驗證日期格式"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def transform_single_date(transformer, date: str, stock_id: str = None):
    """轉換單日資料"""
    logger.info(f"開始轉換 {date} 的技術指標")

    result_df = transformer.transform(date)

    if result_df.empty:
        logger.warning(f"日期 {date} 無資料")
        return None

    # 如果指定股票，篩選結果
    if stock_id:
        result_df = result_df[result_df['stock_id'] == stock_id]
        if result_df.empty:
            logger.warning(f"股票 {stock_id} 在 {date} 無資料")
            return None

    logger.info(f"轉換完成: {len(result_df)} 筆記錄")
    return result_df


def transform_date_range(transformer, start_date: str, end_date: str, stock_id: str = None):
    """轉換日期區間資料"""
    logger.info(f"開始轉換 {start_date} 到 {end_date} 的技術指標")

    # 解析日期
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')

    all_results = []
    current = start

    while current <= end:
        date_str = current.strftime('%Y-%m-%d')
        logger.info(f"處理日期: {date_str}")

        result_df = transformer.transform(date_str)

        if not result_df.empty:
            if stock_id:
                result_df = result_df[result_df['stock_id'] == stock_id]

            if not result_df.empty:
                all_results.append(result_df)

        current += timedelta(days=1)

    if not all_results:
        logger.warning("區間內無資料")
        return None

    # 合併所有結果
    import pandas as pd
    final_df = pd.concat(all_results, ignore_index=True)

    logger.info(f"轉換完成: {len(final_df)} 筆記錄")
    return final_df


def display_results(df, show_sample: int = 10):
    """顯示結果摘要"""
    print("\n" + "="*70)
    print("轉換結果摘要")
    print("="*70)

    print(f"\n總記錄數: {len(df)}")
    print(f"股票數量: {df['stock_id'].nunique()}")
    print(f"日期範圍: {df['trade_date'].min()} 到 {df['trade_date'].max()}")

    print(f"\n欄位列表 ({len(df.columns)} 個):")
    print(", ".join(df.columns.tolist()))

    print(f"\n前 {show_sample} 筆資料:")
    print(df.head(show_sample).to_string())

    print("\n" + "="*70)


def save_results(df, output_path: str):
    """儲存結果到檔案"""
    output_file = Path(output_path)

    # 建立目錄
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # 根據副檔名決定格式
    if output_file.suffix == '.csv':
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        logger.info(f"結果已儲存到: {output_file} (CSV 格式)")
    elif output_file.suffix == '.json':
        df.to_json(output_file, orient='records', force_ascii=False, indent=2)
        logger.info(f"結果已儲存到: {output_file} (JSON 格式)")
    else:
        logger.error(f"不支援的檔案格式: {output_file.suffix}")
        return False

    return True


def main():
    """主程式"""
    args = parse_args()

    # 設定日誌等級
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)

    print("="*70)
    print("技術分析轉換工具")
    print("="*70)

    # 建立轉換器
    try:
        transformer = TechnicalAnalysisTransformer()
        logger.info("轉換器初始化完成")
    except Exception as e:
        logger.error(f"初始化失敗: {e}")
        return 1

    # 執行轉換
    try:
        if args.date:
            # 驗證日期格式
            if not validate_date(args.date):
                logger.error(f"日期格式錯誤: {args.date}，應為 YYYY-MM-DD")
                return 1

            result_df = transform_single_date(transformer, args.date, args.stock_id)
        else:
            # 驗證日期格式
            if not validate_date(args.start) or not validate_date(args.end):
                logger.error("日期格式錯誤，應為 YYYY-MM-DD")
                return 1

            result_df = transform_date_range(
                transformer,
                args.start,
                args.end,
                args.stock_id
            )

        if result_df is None or result_df.empty:
            logger.warning("無資料產生")
            return 1

        # 顯示結果
        display_results(result_df, args.show_sample)

        # 儲存結果
        if args.output:
            if save_results(result_df, args.output):
                print(f"\n✅ 結果已儲存到: {args.output}")
            else:
                return 1

        print("\n✅ 轉換完成")
        return 0

    except KeyboardInterrupt:
        logger.warning("使用者中斷執行")
        return 130
    except Exception as e:
        logger.error(f"執行失敗: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
