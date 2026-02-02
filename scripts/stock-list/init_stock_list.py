#!/usr/bin/env python3
"""
初始化股票清單

從 FinMind API 獲取最新的股票清單並儲存到本地。

Usage:
    python scripts/init_stock_list.py
    python scripts/init_stock_list.py --force  # 強制更新
"""

import argparse
import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import get_logger, StockListManager

logger = get_logger(__name__)


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='初始化股票清單')
    parser.add_argument(
        '--force',
        action='store_true',
        help='強制更新（忽略快取）'
    )
    parser.add_argument(
        '--api-token',
        type=str,
        help='FinMind API Token（選用）'
    )

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("開始初始化股票清單")
    logger.info("=" * 60)

    try:
        # 建立管理器
        manager = StockListManager(api_token=args.api_token)

        # 獲取股票清單
        logger.info(f"強制更新: {args.force}")
        df = manager.get_stock_list(force_update=args.force)

        if df.empty:
            logger.error("股票清單為空")
            return 1

        # 統計資訊
        total_count = len(df)
        stock_count = len(df[df['type'] == '股票']) if 'type' in df.columns else 0
        etf_count = len(df[df['type'] == 'ETF']) if 'type' in df.columns else 0

        logger.info("")
        logger.info("=" * 60)
        logger.info("股票清單統計")
        logger.info("=" * 60)
        logger.info(f"總數: {total_count} 檔")
        logger.info(f"股票: {stock_count} 檔")
        logger.info(f"ETF: {etf_count} 檔")

        # 顯示前 10 筆
        logger.info("")
        logger.info("前 10 筆資料:")
        logger.info("-" * 60)
        for idx, row in df.head(10).iterrows():
            stock_id = row.get('stock_id', 'N/A')
            name = row.get('stock_name', row.get('name', 'N/A'))
            stock_type = row.get('type', 'N/A')
            logger.info(f"  {stock_id:6s} {name:10s} ({stock_type})")

        logger.info("=" * 60)
        logger.info("初始化完成！")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger.error(f"初始化失敗: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
