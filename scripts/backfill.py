#!/usr/bin/env python3
"""
回補歷史資料

回補指定日期範圍的歷史資料。

Usage:
    python scripts/backfill.py --start 2025-01-01 --end 2025-01-31
    python scripts/backfill.py --start 2025-01-01 --days 7  # 回補 7 天
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import get_logger, StockListManager
from src.collectors import (
    create_price_collector,
    create_institutional_collector,
    create_margin_collector,
    create_lending_collector
)

logger = get_logger(__name__)


def generate_date_range(start_date: str, end_date: str = None, days: int = None) -> list:
    """
    產生日期範圍

    Args:
        start_date: 開始日期 (YYYY-MM-DD)
        end_date: 結束日期 (YYYY-MM-DD)，與 days 二選一
        days: 天數，與 end_date 二選一

    Returns:
        list: 日期列表
    """
    start = datetime.strptime(start_date, '%Y-%m-%d')

    if end_date:
        end = datetime.strptime(end_date, '%Y-%m-%d')
    elif days:
        end = start + timedelta(days=days - 1)
    else:
        raise ValueError("必須指定 end_date 或 days")

    date_list = []
    current = start
    while current <= end:
        date_list.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)

    return date_list


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='回補歷史資料')
    parser.add_argument(
        '--start',
        type=str,
        required=True,
        help='開始日期 (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--end',
        type=str,
        help='結束日期 (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--days',
        type=int,
        help='回補天數'
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
        help='指定股票代碼（價格資料用）'
    )

    args = parser.parse_args()

    # 產生日期範圍
    try:
        dates = generate_date_range(args.start, args.end, args.days)
    except ValueError as e:
        logger.error(str(e))
        return 1

    logger.info("=" * 70)
    logger.info("歷史資料回補")
    logger.info("=" * 70)
    logger.info(f"日期範圍: {dates[0]} ~ {dates[-1]}")
    logger.info(f"總天數: {len(dates)} 天")
    logger.info(f"資料類型: {', '.join(args.types)}")
    logger.info("=" * 70)

    # 獲取股票清單（僅用於價格資料）
    if 'price' in args.types:
        if args.stocks:
            stock_ids = args.stocks
            logger.info(f"指定股票: {len(stock_ids)} 檔")
        else:
            stock_manager = StockListManager(api_token=args.api_token)
            stock_ids = stock_manager.get_stock_ids()
            logger.info(f"股票清單: {len(stock_ids)} 檔")
    else:
        stock_ids = []

    # 總統計
    total_stats = {
        'dates_processed': 0,
        'dates_success': 0,
        'dates_failed': 0,
        'total_records': 0
    }

    # 逐日收集
    for idx, date in enumerate(dates, 1):
        logger.info("")
        logger.info("=" * 70)
        logger.info(f"處理日期 {idx}/{len(dates)}: {date}")
        logger.info("=" * 70)

        total_stats['dates_processed'] += 1
        date_success = True

        # 價格資料
        if 'price' in args.types and stock_ids:
            logger.info(f"[{date}] 收集價格資料...")
            collector = create_price_collector(api_token=args.api_token)

            for stock_id in stock_ids:
                try:
                    collector.collect_and_save(date, stock_id)
                except Exception as e:
                    logger.error(f"[{date}] 價格收集失敗 ({stock_id}): {e}")
                    date_success = False

            stats = collector.get_stats()
            total_stats['total_records'] += stats.get('total_records', 0)
            logger.info(f"[{date}] 價格: {stats.get('total_records', 0)} 筆")

        # 法人買賣
        if 'institutional' in args.types:
            logger.info(f"[{date}] 收集法人買賣...")
            collector = create_institutional_collector(api_token=args.api_token)
            try:
                collector.collect_and_save(date, stock_id=None)
                stats = collector.get_stats()
                total_stats['total_records'] += stats.get('total_records', 0)
                logger.info(f"[{date}] 法人: {stats.get('total_records', 0)} 筆")
            except Exception as e:
                logger.error(f"[{date}] 法人收集失敗: {e}")
                date_success = False

        # 融資融券
        if 'margin' in args.types:
            logger.info(f"[{date}] 收集融資融券...")
            collector = create_margin_collector(api_token=args.api_token)
            try:
                collector.collect_and_save(date, stock_id=None)
                stats = collector.get_stats()
                total_stats['total_records'] += stats.get('total_records', 0)
                logger.info(f"[{date}] 融資融券: {stats.get('total_records', 0)} 筆")
            except Exception as e:
                logger.error(f"[{date}] 融資融券收集失敗: {e}")
                date_success = False

        # 借券賣出
        if 'lending' in args.types:
            logger.info(f"[{date}] 收集借券賣出...")
            collector = create_lending_collector(api_token=args.api_token)
            try:
                collector.collect_and_save(date, stock_id=None)
                stats = collector.get_stats()
                total_stats['total_records'] += stats.get('total_records', 0)
                logger.info(f"[{date}] 借券: {stats.get('total_records', 0)} 筆")
            except Exception as e:
                logger.error(f"[{date}] 借券收集失敗: {e}")
                date_success = False

        if date_success:
            total_stats['dates_success'] += 1
        else:
            total_stats['dates_failed'] += 1

    # 最終統計
    logger.info("")
    logger.info("=" * 70)
    logger.info("回補完成")
    logger.info("=" * 70)
    logger.info(f"處理天數: {total_stats['dates_processed']}")
    logger.info(f"成功: {total_stats['dates_success']}")
    logger.info(f"失敗: {total_stats['dates_failed']}")
    logger.info(f"總筆數: {total_stats['total_records']}")
    logger.info("=" * 70)

    return 0 if total_stats['dates_failed'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
