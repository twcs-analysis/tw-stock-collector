#!/usr/bin/env python3
"""
執行資料收集

收集指定日期的台股資料。

Usage:
    python scripts/run_collection.py                    # 收集今天的資料
    python scripts/run_collection.py --date 2025-01-28  # 收集指定日期
    python scripts/run_collection.py --date yesterday   # 收集昨天
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import get_logger, get_global_config, StockListManager
from src.collectors import (
    create_price_collector,
    create_institutional_collector,
    create_margin_collector,
    create_lending_collector
)

logger = get_logger(__name__)


def parse_date(date_str: str) -> str:
    """
    解析日期字串

    Args:
        date_str: 日期字串 (today, yesterday, YYYY-MM-DD)

    Returns:
        str: YYYY-MM-DD 格式的日期
    """
    if date_str == 'today':
        return datetime.now().strftime('%Y-%m-%d')
    elif date_str == 'yesterday':
        return (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        # 驗證日期格式
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return date_str
        except ValueError:
            raise ValueError(f"無效的日期格式: {date_str}，請使用 YYYY-MM-DD")


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='執行台股資料收集')
    parser.add_argument(
        '--date',
        type=str,
        default='today',
        help='收集日期 (today, yesterday, YYYY-MM-DD)，預設為 today'
    )
    parser.add_argument(
        '--api-token',
        type=str,
        help='FinMind API Token（選用）'
    )
    parser.add_argument(
        '--types',
        type=str,
        nargs='+',
        default=['price', 'institutional', 'margin', 'lending'],
        choices=['price', 'institutional', 'margin', 'lending'],
        help='要收集的資料類型'
    )
    parser.add_argument(
        '--stocks',
        type=str,
        nargs='+',
        help='指定股票代碼（不指定則收集所有股票）'
    )

    args = parser.parse_args()

    # 解析日期
    try:
        collection_date = parse_date(args.date)
    except ValueError as e:
        logger.error(str(e))
        return 1

    logger.info("=" * 70)
    logger.info("台股資料收集")
    logger.info("=" * 70)
    logger.info(f"收集日期: {collection_date}")
    logger.info(f"資料類型: {', '.join(args.types)}")
    logger.info("=" * 70)

    # 載入配置
    config = get_global_config()

    # 獲取股票清單
    if args.stocks:
        stock_ids = args.stocks
        logger.info(f"指定股票: {len(stock_ids)} 檔")
    else:
        stock_manager = StockListManager(api_token=args.api_token)
        stock_ids = stock_manager.get_stock_ids()
        logger.info(f"股票清單: {len(stock_ids)} 檔")

    # 統計資訊
    stats = {
        'total_collections': 0,
        'success_collections': 0,
        'failed_collections': 0,
        'total_records': 0
    }

    # 收集價格資料
    if 'price' in args.types:
        logger.info("")
        logger.info("-" * 70)
        logger.info("收集價格資料")
        logger.info("-" * 70)

        collector = create_price_collector(api_token=args.api_token)

        for stock_id in stock_ids:
            stats['total_collections'] += 1
            try:
                if collector.collect_and_save(collection_date, stock_id):
                    stats['success_collections'] += 1
                else:
                    stats['failed_collections'] += 1
            except Exception as e:
                logger.error(f"收集失敗 ({stock_id}): {e}")
                stats['failed_collections'] += 1

        collector_stats = collector.get_stats()
        stats['total_records'] += collector_stats.get('total_records', 0)
        logger.info(f"完成: {collector_stats.get('success_count', 0)} 成功, "
                   f"{collector_stats.get('failed_count', 0)} 失敗")

    # 收集法人買賣資料
    if 'institutional' in args.types:
        logger.info("")
        logger.info("-" * 70)
        logger.info("收集法人買賣資料（使用 Aggregate API）")
        logger.info("-" * 70)

        collector = create_institutional_collector(api_token=args.api_token)
        stats['total_collections'] += 1

        try:
            # 使用 aggregate API 一次取得所有股票
            if collector.collect_and_save(collection_date, stock_id=None):
                stats['success_collections'] += 1
            else:
                stats['failed_collections'] += 1

            collector_stats = collector.get_stats()
            stats['total_records'] += collector_stats.get('total_records', 0)
            logger.info(f"完成: {collector_stats.get('total_records', 0)} 筆")

        except Exception as e:
            logger.error(f"收集失敗: {e}")
            stats['failed_collections'] += 1

    # 收集融資融券資料
    if 'margin' in args.types:
        logger.info("")
        logger.info("-" * 70)
        logger.info("收集融資融券資料（使用 Aggregate API）")
        logger.info("-" * 70)

        collector = create_margin_collector(api_token=args.api_token)
        stats['total_collections'] += 1

        try:
            if collector.collect_and_save(collection_date, stock_id=None):
                stats['success_collections'] += 1
            else:
                stats['failed_collections'] += 1

            collector_stats = collector.get_stats()
            stats['total_records'] += collector_stats.get('total_records', 0)
            logger.info(f"完成: {collector_stats.get('total_records', 0)} 筆")

        except Exception as e:
            logger.error(f"收集失敗: {e}")
            stats['failed_collections'] += 1

    # 收集借券賣出資料
    if 'lending' in args.types:
        logger.info("")
        logger.info("-" * 70)
        logger.info("收集借券賣出資料（使用 Aggregate API）")
        logger.info("-" * 70)

        collector = create_lending_collector(api_token=args.api_token)
        stats['total_collections'] += 1

        try:
            if collector.collect_and_save(collection_date, stock_id=None):
                stats['success_collections'] += 1
            else:
                stats['failed_collections'] += 1

            collector_stats = collector.get_stats()
            stats['total_records'] += collector_stats.get('total_records', 0)
            logger.info(f"完成: {collector_stats.get('total_records', 0)} 筆")

        except Exception as e:
            logger.error(f"收集失敗: {e}")
            stats['failed_collections'] += 1

    # 總結
    logger.info("")
    logger.info("=" * 70)
    logger.info("收集完成")
    logger.info("=" * 70)
    logger.info(f"總收集次數: {stats['total_collections']}")
    logger.info(f"成功: {stats['success_collections']}")
    logger.info(f"失敗: {stats['failed_collections']}")
    logger.info(f"總筆數: {stats['total_records']}")
    logger.info(f"成功率: {stats['success_collections'] / stats['total_collections'] * 100:.1f}%"
               if stats['total_collections'] > 0 else "N/A")
    logger.info("=" * 70)

    return 0 if stats['failed_collections'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
