#!/usr/bin/env python3.11
"""
ETF 持股資料匯入腳本

功能:
1. 從 data/raw/etf-holdings/ 讀取 ETF 持股 JSON 檔案
2. 匯入到 PostgreSQL 資料庫 (etfs, etf_holdings 表)
3. 自動建立不存在的 ETF 基本資訊
4. 支援批次匯入與錯誤處理

使用方式:
    python3.11 scripts/etf-importer/import_etf_holdings.py
    python3.11 scripts/etf-importer/import_etf_holdings.py --etf 0050
    python3.11 scripts/etf-importer/import_etf_holdings.py --snapshot-date 2026-02-04
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Optional

# 加入專案根目錄到 Python Path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from services.common.database.models import Base, ETF, ETFHolding, Stock
from services.common.database.connection import get_connection_string

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ETFHoldingsImporter:
    """ETF 持股資料匯入器"""

    def __init__(self, db_url: str, data_dir: Path):
        """
        初始化匯入器

        Args:
            db_url: 資料庫連線字串
            data_dir: ETF 持股資料目錄 (data/raw/etf-holdings/)
        """
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.data_dir = data_dir

        if not self.data_dir.exists():
            raise ValueError(f"資料目錄不存在: {self.data_dir}")

    def load_etf_data(self, etf_id: str) -> Optional[Dict]:
        """
        載入 ETF 持股資料

        Args:
            etf_id: ETF 代碼 (例: 0050, 00733)

        Returns:
            ETF 持股資料字典，若檔案不存在則返回 None
        """
        file_path = self.data_dir / f"{etf_id}.json"

        if not file_path.exists():
            logger.warning(f"檔案不存在: {file_path}")
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"成功載入 {etf_id} 持股資料: {len(data['holdings'])} 筆")
            return data
        except Exception as e:
            logger.error(f"載入 {etf_id} 失敗: {e}")
            return None

    def import_etf_info(self, session, metadata: Dict) -> None:
        """
        匯入或更新 ETF 基本資訊

        Args:
            session: SQLAlchemy Session
            metadata: ETF metadata 資料
        """
        etf_id = metadata['etf_id']
        etf_name = metadata['etf_name']

        # 檢查 ETF 是否已存在
        etf = session.query(ETF).filter_by(etf_id=etf_id).first()

        if etf:
            # 更新資訊
            etf.etf_name = etf_name
            etf.updated_at = datetime.now()
            logger.info(f"更新 ETF 資訊: {etf_id} - {etf_name}")
        else:
            # 新增 ETF
            etf = ETF(
                etf_id=etf_id,
                etf_name=etf_name,
                description=None
            )
            session.add(etf)
            logger.info(f"新增 ETF 資訊: {etf_id} - {etf_name}")

    def import_holdings(
        self,
        session,
        etf_id: str,
        holdings: List[Dict],
        snapshot_date: date
    ) -> int:
        """
        匯入 ETF 持股明細

        Args:
            session: SQLAlchemy Session
            etf_id: ETF 代碼
            holdings: 持股清單
            snapshot_date: 快照日期

        Returns:
            成功匯入的筆數
        """
        imported_count = 0
        skipped_count = 0

        for holding_data in holdings:
            stock_id = holding_data['stock_id']
            stock_name = holding_data['stock_name']
            weight = holding_data.get('weight')
            shares = holding_data.get('shares')

            # 檢查股票是否存在
            stock = session.query(Stock).filter_by(stock_id=stock_id).first()
            if not stock:
                logger.warning(f"股票 {stock_id} ({stock_name}) 不存在於資料庫，跳過")
                skipped_count += 1
                continue

            # 檢查持股記錄是否已存在
            existing = session.query(ETFHolding).filter_by(
                etf_id=etf_id,
                stock_id=stock_id,
                snapshot_date=snapshot_date
            ).first()

            if existing:
                # 更新現有記錄
                existing.weight = weight
                existing.shares = shares
            else:
                # 新增持股記錄
                holding = ETFHolding(
                    etf_id=etf_id,
                    stock_id=stock_id,
                    snapshot_date=snapshot_date,
                    weight=weight,
                    shares=shares
                )
                session.add(holding)

            imported_count += 1

        if skipped_count > 0:
            logger.warning(f"跳過 {skipped_count} 筆持股（股票不存在於資料庫）")

        return imported_count

    def import_single_etf(self, etf_id: str, snapshot_date: date) -> bool:
        """
        匯入單一 ETF 的持股資料

        Args:
            etf_id: ETF 代碼
            snapshot_date: 快照日期

        Returns:
            匯入是否成功
        """
        # 載入資料
        data = self.load_etf_data(etf_id)
        if not data:
            return False

        session = self.Session()
        try:
            # 1. 匯入 ETF 基本資訊
            self.import_etf_info(session, data['metadata'])

            # 2. 匯入持股明細
            imported_count = self.import_holdings(
                session,
                etf_id,
                data['holdings'],
                snapshot_date
            )

            # 3. 提交事務
            session.commit()
            logger.info(f"✅ {etf_id} 匯入完成: {imported_count} 筆持股")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"❌ {etf_id} 匯入失敗: {e}")
            return False

        finally:
            session.close()

    def import_all_etfs(self, snapshot_date: date) -> Dict[str, bool]:
        """
        匯入所有 ETF 持股資料

        Args:
            snapshot_date: 快照日期

        Returns:
            各 ETF 匯入結果
        """
        results = {}

        # 掃描所有 JSON 檔案
        json_files = list(self.data_dir.glob("*.json"))
        logger.info(f"找到 {len(json_files)} 個 ETF 持股檔案")

        for json_file in json_files:
            etf_id = json_file.stem
            logger.info(f"\n{'='*60}")
            logger.info(f"處理 ETF: {etf_id}")
            logger.info(f"{'='*60}")

            success = self.import_single_etf(etf_id, snapshot_date)
            results[etf_id] = success

        return results


def main():
    """主程式"""
    parser = argparse.ArgumentParser(description='ETF 持股資料匯入工具')
    parser.add_argument(
        '--etf',
        type=str,
        help='指定要匯入的 ETF 代碼（不指定則匯入全部）'
    )
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

    # 設定資料目錄
    data_dir = project_root / "data" / "raw" / "etf-holdings"

    logger.info(f"")
    logger.info(f"{'='*60}")
    logger.info(f"ETF 持股資料匯入工具")
    logger.info(f"{'='*60}")
    logger.info(f"快照日期: {snapshot_date}")
    logger.info(f"資料目錄: {data_dir}")
    logger.info(f"{'='*60}\n")

    # 建立匯入器
    importer = ETFHoldingsImporter(db_url, data_dir)

    # 執行匯入
    if args.etf:
        # 匯入單一 ETF
        success = importer.import_single_etf(args.etf, snapshot_date)
        sys.exit(0 if success else 1)
    else:
        # 匯入所有 ETF
        results = importer.import_all_etfs(snapshot_date)

        # 顯示摘要
        logger.info(f"\n{'='*60}")
        logger.info(f"匯入摘要")
        logger.info(f"{'='*60}")

        success_count = sum(1 for v in results.values() if v)
        total_count = len(results)

        for etf_id, success in results.items():
            status = "✅ 成功" if success else "❌ 失敗"
            logger.info(f"{etf_id}: {status}")

        logger.info(f"\n總計: {success_count}/{total_count} 個 ETF 匯入成功")
        logger.info(f"{'='*60}")

        sys.exit(0 if success_count == total_count else 1)


if __name__ == "__main__":
    main()
