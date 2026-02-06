#!/usr/bin/env python3
"""
月營收資料收集腳本

收集台股上市櫃公司月營收資料
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
import json

# 加入專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from services.common.collectors.revenue_collector import RevenueCollector
from services.common.utils.logger import setup_logger


def main():
    """主程式"""
    parser = argparse.ArgumentParser(
        description='收集台股月營收資料',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  # 每日收集模式（1-10 日使用，漸進式累積）
  python scripts/data-collector/collect_revenue.py --mode daily

  # 月度收集模式（10 日後使用，完整資料）
  python scripts/data-collector/collect_revenue.py --mode monthly

  # 指定年月
  python scripts/data-collector/collect_revenue.py --mode monthly --year-month 2026-01

  # 指定收集日期（daily 模式）
  python scripts/data-collector/collect_revenue.py --mode daily --date 2026-02-05

  # 顯示詳細日誌
  python scripts/data-collector/collect_revenue.py --verbose
        """
    )

    parser.add_argument(
        '--mode',
        type=str,
        choices=['daily', 'monthly'],
        default='monthly',
        help='收集模式：daily (每日漸進) 或 monthly (月度完整)，預設 monthly'
    )

    parser.add_argument(
        '--year-month',
        type=str,
        help='指定年月 (YYYY-MM)，若不指定則收集最新資料'
    )

    parser.add_argument(
        '--date',
        type=str,
        help='指定收集日期 (YYYY-MM-DD)，僅用於 daily 模式'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='顯示詳細日誌'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='僅測試不儲存'
    )

    args = parser.parse_args()

    # 設定日誌
    log_level = 'DEBUG' if args.verbose else 'INFO'
    logger = setup_logger('collect_revenue', level=log_level)

    try:
        # 顯示執行資訊
        year_month_str = args.year_month or "最新"
        mode_str = "每日收集" if args.mode == "daily" else "月度收集"
        logger.info(f"{'='*60}")
        logger.info(f"月營收資料收集")
        logger.info(f"模式: {mode_str} ({args.mode})")
        logger.info(f"年月: {year_month_str}")
        if args.mode == "daily" and args.date:
            logger.info(f"日期: {args.date}")
        logger.info(f"{'='*60}")

        # 初始化收集器
        collector = RevenueCollector(
            year_month=args.year_month,
            mode=args.mode,
            collection_date=args.date
        )

        # 收集資料
        logger.info("開始收集資料...")
        result = collector.collect()

        if not result or not result.get('data'):
            logger.error("收集失敗：無資料")
            return 1

        # 顯示結果
        metadata = result.get('metadata', {})
        logger.info(f"\n收集結果:")
        logger.info(f"  模式: {metadata.get('mode')}")
        logger.info(f"  實際年月: {metadata.get('year_month')}")
        if metadata.get('collection_date'):
            logger.info(f"  收集日期: {metadata.get('collection_date')}")
        logger.info(f"  總計: {metadata.get('total_count')} 檔")
        logger.info(f"  上市 (TWSE): {metadata.get('twse_count')} 檔")
        logger.info(f"  上櫃 (TPEx): {metadata.get('tpex_count')} 檔")

        # 顯示範例資料
        if args.verbose and result.get('data'):
            logger.debug(f"\n範例資料（前 3 筆）:")
            for i, item in enumerate(result['data'][:3], 1):
                logger.debug(f"\n  [{i}] {item.get('stock_id')} {item.get('stock_name')}")
                logger.debug(f"      當月營收: {item.get('current_month_revenue'):,} 千元")
                logger.debug(f"      月增率: {item.get('mom_change_pct'):.2f}%")
                logger.debug(f"      年增率: {item.get('yoy_change_pct'):.2f}%")

        # 儲存資料
        if not args.dry_run:
            logger.info("\n儲存資料...")
            save_path = collector.get_save_path()

            # 確保目錄存在
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)

            # 寫入檔案
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            logger.info(f"✓ 已儲存至: {save_path}")

            # 檔案大小
            file_size = Path(save_path).stat().st_size
            logger.info(f"  檔案大小: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        else:
            logger.info("\n[DRY RUN] 跳過儲存")

        logger.info(f"\n{'='*60}")
        logger.info("✓ 收集完成")
        logger.info(f"{'='*60}")

        return 0

    except KeyboardInterrupt:
        logger.warning("\n使用者中斷")
        return 130
    except Exception as e:
        logger.error(f"\n執行失敗: {e}", exc_info=args.verbose)
        return 1


if __name__ == '__main__':
    sys.exit(main())
