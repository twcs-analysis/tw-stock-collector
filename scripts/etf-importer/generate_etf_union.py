#!/usr/bin/env python3.11
"""
ETF 持股去重清單產生器

功能:
1. 從 etf_holdings 表讀取所有 ETF 持股
2. 計算每個股票被多少 ETF 持有 (etf_count)
3. 計算每個股票在所有 ETF 中的權重總和 (total_weight)
4. 更新 etf_stock_union 表

使用方式:
    python3.11 scripts/etf-importer/generate_etf_union.py
    python3.11 scripts/etf-importer/generate_etf_union.py --snapshot-date 2026-02-04
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List

# 加入專案根目錄到 Python Path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker

from services.common.database.models import ETFHolding, ETFStockUnion, Stock
from services.common.database.connection import get_connection_string

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ETFUnionGenerator:
    """ETF 持股去重清單產生器"""

    def __init__(self, db_url: str):
        """
        初始化產生器

        Args:
            db_url: 資料庫連線字串
        """
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

    def calculate_union(self, snapshot_date: date) -> List[Dict]:
        """
        計算 ETF 持股去重清單

        Args:
            snapshot_date: 快照日期

        Returns:
            去重後的股票清單，包含 etf_count 和 total_weight
        """
        session = self.Session()

        try:
            # 使用 SQL 聚合查詢計算
            # SELECT stock_id,
            #        COUNT(DISTINCT etf_id) as etf_count,
            #        SUM(weight) as total_weight
            # FROM etf_holdings
            # WHERE snapshot_date = '2026-02-04'
            # GROUP BY stock_id
            query = session.query(
                ETFHolding.stock_id,
                func.count(func.distinct(ETFHolding.etf_id)).label('etf_count'),
                func.sum(ETFHolding.weight).label('total_weight')
            ).filter(
                ETFHolding.snapshot_date == snapshot_date
            ).group_by(
                ETFHolding.stock_id
            )

            results = query.all()
            logger.info(f"計算完成: {len(results)} 檔股票")

            # 轉換為字典列表
            union_data = [
                {
                    'stock_id': row.stock_id,
                    'etf_count': row.etf_count,
                    'total_weight': float(row.total_weight) if row.total_weight else 0.0,
                    'latest_update': snapshot_date
                }
                for row in results
            ]

            return union_data

        finally:
            session.close()

    def update_union_table(self, union_data: List[Dict]) -> int:
        """
        更新 etf_stock_union 表

        Args:
            union_data: 去重後的股票清單

        Returns:
            更新的筆數
        """
        session = self.Session()

        try:
            # 清空現有資料
            deleted_count = session.query(ETFStockUnion).delete()
            logger.info(f"清空現有資料: {deleted_count} 筆")

            # 批次插入新資料
            for data in union_data:
                union_record = ETFStockUnion(**data)
                session.add(union_record)

            session.commit()
            logger.info(f"成功更新 {len(union_data)} 筆資料")

            return len(union_data)

        except Exception as e:
            session.rollback()
            logger.error(f"更新失敗: {e}")
            raise

        finally:
            session.close()

    def show_statistics(self) -> None:
        """顯示統計資訊"""
        session = self.Session()

        try:
            # 總股票數
            total_stocks = session.query(ETFStockUnion).count()

            # 被多個 ETF 持有的股票數
            multi_etf_stocks = session.query(ETFStockUnion).filter(
                ETFStockUnion.etf_count > 1
            ).count()

            # 平均被持有次數
            avg_count = session.query(
                func.avg(ETFStockUnion.etf_count)
            ).scalar()

            # 最多被持有次數
            max_count = session.query(
                func.max(ETFStockUnion.etf_count)
            ).scalar()

            # Top 10 重倉股（依 total_weight 排序）
            top_stocks = session.query(
                ETFStockUnion.stock_id,
                ETFStockUnion.etf_count,
                ETFStockUnion.total_weight,
                Stock.stock_name
            ).join(
                Stock, ETFStockUnion.stock_id == Stock.stock_id
            ).order_by(
                ETFStockUnion.total_weight.desc()
            ).limit(10).all()

            logger.info(f"\n{'='*60}")
            logger.info(f"ETF 持股統計")
            logger.info(f"{'='*60}")
            logger.info(f"總股票數: {total_stocks} 檔")
            logger.info(f"被多個 ETF 持有: {multi_etf_stocks} 檔 ({multi_etf_stocks/total_stocks*100:.1f}%)")
            logger.info(f"平均被持有次數: {avg_count:.2f}")
            logger.info(f"最多被持有次數: {max_count}")

            logger.info(f"\nTop 10 重倉股（依總權重）:")
            logger.info(f"{'-'*60}")
            for stock in top_stocks:
                logger.info(
                    f"{stock.stock_id:6} {stock.stock_name:10} | "
                    f"ETF數: {stock.etf_count:2} | "
                    f"總權重: {stock.total_weight:6.2f}%"
                )

            logger.info(f"{'='*60}\n")

        finally:
            session.close()

    def generate(self, snapshot_date: date) -> bool:
        """
        執行完整的去重清單產生流程

        Args:
            snapshot_date: 快照日期

        Returns:
            是否成功
        """
        try:
            logger.info(f"開始計算 ETF 持股去重清單（快照日期: {snapshot_date}）")

            # 1. 計算去重清單
            union_data = self.calculate_union(snapshot_date)

            if not union_data:
                logger.warning("沒有找到任何 ETF 持股資料")
                return False

            # 2. 更新資料表
            self.update_union_table(union_data)

            # 3. 顯示統計
            self.show_statistics()

            logger.info("✅ ETF 持股去重清單產生完成")
            return True

        except Exception as e:
            logger.error(f"❌ 產生失敗: {e}")
            return False


def main():
    """主程式"""
    parser = argparse.ArgumentParser(description='ETF 持股去重清單產生器')
    parser.add_argument(
        '--snapshot-date',
        type=str,
        default=datetime.now().strftime('%Y-%m-%d'),
        help='持股快照日期（預設: 今天）'
    )
    parser.add_argument(
        '--db-url',
        type=str,
        help='資料庫連線字串（預設: 從環境變數或設定檔讀取）'
    )

    args = parser.parse_args()

    # 解析日期
    try:
        snapshot_date = datetime.strptime(args.snapshot_date, '%Y-%m-%d').date()
    except ValueError:
        logger.error(f"日期格式錯誤: {args.snapshot_date}，請使用 YYYY-MM-DD 格式")
        sys.exit(1)

    # 取得資料庫連線
    db_url = args.db_url or get_connection_string()

    logger.info(f"")
    logger.info(f"{'='*60}")
    logger.info(f"ETF 持股去重清單產生器")
    logger.info(f"{'='*60}")
    logger.info(f"快照日期: {snapshot_date}")
    logger.info(f"{'='*60}\n")

    # 建立產生器
    generator = ETFUnionGenerator(db_url)

    # 執行產生
    success = generator.generate(snapshot_date)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
