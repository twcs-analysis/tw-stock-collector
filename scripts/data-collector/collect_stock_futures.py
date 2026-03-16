#!/usr/bin/env python3
"""
個股期貨資料收集腳本

用途：收集 TAIFEX 個股期貨每日交易資料

範例：
    # 收集今天的資料
    python3 scripts/data-collector/collect_stock_futures.py

    # 收集指定日期的資料
    python3 scripts/data-collector/collect_stock_futures.py --date 2026-03-13

作者：Claude Sonnet 4.5
日期：2026-03-15
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# 加入專案根目錄到 Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from services.common.collectors import StockFuturesCollector
from services.common.utils import setup_logger


def main():
    """主程式"""
    parser = argparse.ArgumentParser(
        description='收集 TAIFEX 個股期貨每日交易資料',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  %(prog)s                            # 收集今天的資料
  %(prog)s --date 2026-03-13          # 收集指定日期的資料
  %(prog)s --date 2026-03-13 --no-validation  # 不執行驗證
        """
    )

    parser.add_argument(
        '--date',
        type=str,
        default=datetime.now().strftime('%Y-%m-%d'),
        help='收集日期 (YYYY-MM-DD)，預設為今天'
    )

    parser.add_argument(
        '--no-validation',
        action='store_true',
        help='不執行資料驗證'
    )

    args = parser.parse_args()

    # 設定 logger
    logger = setup_logger('collect_stock_futures')

    logger.info("="*60)
    logger.info("個股期貨資料收集")
    logger.info("="*60)
    logger.info(f"收集日期: {args.date}")
    logger.info(f"執行驗證: {not args.no_validation}")
    logger.info("")

    try:
        # 建立收集器
        collector = StockFuturesCollector(date=args.date)

        # 執行收集
        enable_validation = not args.no_validation
        result = collector.run(enable_validation=enable_validation)

        # 顯示結果
        logger.info("")
        logger.info("="*60)
        logger.info("收集結果")
        logger.info("="*60)

        if result['status'] == 'success':
            logger.info(f"✅ 成功")
            logger.info(f"   檔案: {result['file']}")
            logger.info(f"   筆數: {result['records']}")

            if 'validation' in result:
                validation = result['validation']
                logger.info(f"   驗證: {validation.get('status', 'N/A')}")
                if validation.get('status') != 'error':
                    logger.info(f"   評分: {validation.get('grade', 'N/A')}")
                    logger.info(f"   準確度: {validation.get('accuracy', 0):.1f}%")

        elif result['status'] == 'no_data':
            logger.warning(f"⚠️  {result.get('message', '無資料')}")
            sys.exit(0)

        else:  # error
            logger.error(f"❌ 失敗: {result.get('error', '未知錯誤')}")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.warning("\n⚠️  使用者中斷")
        sys.exit(130)

    except Exception as e:
        logger.exception(f"❌ 執行失敗: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
