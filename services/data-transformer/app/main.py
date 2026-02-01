"""
Data Transformer Service - Main Entry Point

資料轉換服務主程式
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.technical_analysis_transformer import TechnicalAnalysisTransformer
from common.utils import get_logger, get_global_config

logger = get_logger(__name__)


def parse_arguments():
    """解析命令列參數"""
    parser = argparse.ArgumentParser(
        description="資料轉換服務 - 將原始資料轉換為分析資料"
    )

    # 轉換類型
    parser.add_argument(
        '--type',
        choices=['technical_analysis'],
        default='technical_analysis',
        help='轉換類型 (預設: technical_analysis)'
    )

    # 日期參數
    parser.add_argument(
        '--date',
        type=str,
        help='指定日期 (YYYY-MM-DD)'
    )

    parser.add_argument(
        '--start',
        type=str,
        help='起始日期 (YYYY-MM-DD，用於批次轉換)'
    )

    parser.add_argument(
        '--end',
        type=str,
        help='結束日期 (YYYY-MM-DD，用於批次轉換)'
    )

    # 股票參數
    parser.add_argument(
        '--stock-id',
        type=str,
        help='指定股票代碼 (選用)'
    )

    # 配置
    parser.add_argument(
        '--config',
        type=str,
        help='配置檔路徑'
    )

    return parser.parse_args()


def get_transformer(transform_type: str, config=None):
    """
    根據類型取得轉換器實例

    Args:
        transform_type: 轉換類型
        config: 配置實例

    Returns:
        BaseTransformer: 轉換器實例
    """
    transformers = {
        'technical_analysis': TechnicalAnalysisTransformer,
    }

    transformer_class = transformers.get(transform_type)
    if not transformer_class:
        raise ValueError(f"不支援的轉換類型: {transform_type}")

    return transformer_class(config)


def transform_single_date(transformer, date: str, stock_id=None):
    """
    轉換單一日期的資料

    Args:
        transformer: 轉換器實例
        date: 日期 (YYYY-MM-DD)
        stock_id: 股票代碼 (選用)

    Returns:
        bool: 是否成功
    """
    logger.info(f"開始轉換: date={date}, stock_id={stock_id or '全部'}")

    try:
        result = transformer.transform_and_save(
            date=date,
            stock_id=stock_id
        )

        if result['status'] == 'success':
            logger.info(f"轉換成功: {date}, 記錄數: {result['records']}")
            return True
        elif result['status'] == 'no_data':
            logger.warning(f"轉換完成但無資料: {date}")
            return True  # 無資料不算失敗
        else:
            logger.error(f"轉換失敗: {date}, 錯誤: {result.get('error')}")
            return False

    except Exception as e:
        logger.error(f"轉換時發生錯誤: {e}", exc_info=True)
        return False


def transform_date_range(transformer, start_date: str, end_date: str, stock_id=None):
    """
    轉換日期範圍的資料

    Args:
        transformer: 轉換器實例
        start_date: 起始日期 (YYYY-MM-DD)
        end_date: 結束日期 (YYYY-MM-DD)
        stock_id: 股票代碼 (選用)

    Returns:
        dict: 統計資訊
    """
    logger.info(
        f"開始批次轉換: {start_date} 到 {end_date}, "
        f"stock_id={stock_id or '全部'}"
    )

    # 生成日期列表
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')

    dates = []
    current = start
    while current <= end:
        dates.append(current)
        current += timedelta(days=1)

    # 批次轉換
    stats = transformer.batch_transform(
        dates=dates,
        stock_ids=[stock_id] if stock_id else None
    )

    logger.info(
        f"批次轉換完成:\n"
        f"  成功: {stats['success_count']}\n"
        f"  失敗: {stats['failed_count']}\n"
        f"  總記錄數: {stats['total_records']}\n"
        f"  耗時: {stats['duration_seconds']:.2f}秒\n"
        f"  速度: {stats['records_per_second']:.2f} 筆/秒"
    )

    return stats


def main():
    """主程式"""
    args = parse_arguments()

    try:
        # 載入配置
        if args.config:
            # TODO: 實作從檔案載入配置
            config = get_global_config()
        else:
            config = get_global_config()

        # 取得轉換器
        transformer = get_transformer(args.type, config)

        logger.info(f"使用轉換器: {transformer}")

        # 根據參數決定執行模式
        if args.start and args.end:
            # 批次轉換模式
            stats = transform_date_range(
                transformer=transformer,
                start_date=args.start,
                end_date=args.end,
                stock_id=args.stock_id
            )
            exit_code = 0 if stats['failed_count'] == 0 else 1

        elif args.date:
            # 單日轉換模式
            success = transform_single_date(
                transformer=transformer,
                date=args.date,
                stock_id=args.stock_id
            )
            exit_code = 0 if success else 1

        else:
            # 預設: 轉換昨天的資料
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            logger.info(f"未指定日期，轉換昨天的資料: {yesterday}")

            success = transform_single_date(
                transformer=transformer,
                date=yesterday,
                stock_id=args.stock_id
            )
            exit_code = 0 if success else 1

        sys.exit(exit_code)

    except KeyboardInterrupt:
        logger.warning("使用者中斷執行")
        sys.exit(130)

    except Exception as e:
        logger.error(f"程式執行失敗: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
