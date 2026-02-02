"""
Database Loader for Data Transformer

從 PostgreSQL 載入股票資料到記憶體 (DataFrame)
取代原本的檔案系統載入方式
"""

import os
from typing import Optional, List, Union
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

import sys

# 設定專案路徑 - 相對於當前檔案的位置
current_dir = Path(__file__).parent  # data-transformer/app
transformer_root = current_dir.parent  # data-transformer
services_path = transformer_root.parent  # services
project_root = services_path.parent  # project root

# 加入路徑
sys.path.insert(0, str(services_path))  # services

# 匯入 common 模組
from common.utils import get_logger
from common.database import (
    DatabaseConfig,
    get_db_manager,
    StockPriceDaily,
    Stock,
)

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

logger = get_logger(__name__)


class DatabaseLoader:
    """
    資料庫載入器

    從 PostgreSQL 載入股票資料，替代原本的檔案系統載入
    """

    def __init__(self, config: Optional[DatabaseConfig] = None):
        """
        Args:
            config: 資料庫配置 (選用，None 則從環境變數載入)
        """
        self.db_manager = get_db_manager(config)
        self.logger = get_logger(self.__class__.__name__)

    def load_price_data(
        self,
        date: Union[str, datetime],
        stock_id: Optional[str] = None
    ) -> pd.DataFrame:
        """
        載入單日價格資料

        Args:
            date: 交易日期
            stock_id: 股票代碼 (選用，None 表示載入所有股票)

        Returns:
            pd.DataFrame: 價格資料，欄位對應 JSON 格式:
                - trade_date: 交易日期
                - stock_id: 股票代碼
                - open: 開盤價
                - high: 最高價
                - low: 最低價
                - close: 收盤價
                - volume: 成交量
                - amount: 成交金額
        """
        if isinstance(date, datetime):
            target_date = date.date()
        else:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()

        with self.db_manager.get_session() as session:
            # 建立查詢
            query = select(StockPriceDaily).where(
                StockPriceDaily.trade_date == target_date
            )

            # 如果指定股票代碼，加入篩選
            if stock_id:
                query = query.where(StockPriceDaily.stock_id == stock_id)

            # 執行查詢
            results = session.execute(query).scalars().all()

            if not results:
                self.logger.debug(f"無資料: date={target_date}, stock_id={stock_id}")
                return pd.DataFrame()

            # 轉換為 DataFrame
            data = []
            for row in results:
                data.append({
                    'trade_date': row.trade_date.strftime('%Y-%m-%d'),
                    'stock_id': row.stock_id,
                    'open': float(row.open_price) if row.open_price else None,
                    'high': float(row.high_price) if row.high_price else None,
                    'low': float(row.low_price) if row.low_price else None,
                    'close': float(row.close_price) if row.close_price else None,
                    'volume': int(row.volume) if row.volume else None,
                    'amount': float(row.amount) if row.amount else None,
                })

            df = pd.DataFrame(data)

            self.logger.info(
                f"載入資料: date={target_date}, "
                f"stock_id={stock_id or 'all'}, "
                f"records={len(df)}"
            )

            return df

    def load_price_data_range(
        self,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        stock_id: Optional[str] = None
    ) -> pd.DataFrame:
        """
        載入日期區間的價格資料

        Args:
            start_date: 開始日期
            end_date: 結束日期
            stock_id: 股票代碼 (選用，None 表示載入所有股票)

        Returns:
            pd.DataFrame: 價格資料
        """
        if isinstance(start_date, str):
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
        else:
            start = start_date.date() if isinstance(start_date, datetime) else start_date

        if isinstance(end_date, str):
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        else:
            end = end_date.date() if isinstance(end_date, datetime) else end_date

        with self.db_manager.get_session() as session:
            # 建立查詢
            query = select(StockPriceDaily).where(
                and_(
                    StockPriceDaily.trade_date >= start,
                    StockPriceDaily.trade_date <= end
                )
            )

            # 如果指定股票代碼，加入篩選
            if stock_id:
                query = query.where(StockPriceDaily.stock_id == stock_id)

            # 排序
            query = query.order_by(
                StockPriceDaily.stock_id,
                StockPriceDaily.trade_date
            )

            # 執行查詢
            results = session.execute(query).scalars().all()

            if not results:
                self.logger.debug(
                    f"無資料: start={start}, end={end}, stock_id={stock_id}"
                )
                return pd.DataFrame()

            # 轉換為 DataFrame
            data = []
            for row in results:
                data.append({
                    'trade_date': row.trade_date.strftime('%Y-%m-%d'),
                    'stock_id': row.stock_id,
                    'open': float(row.open_price) if row.open_price else None,
                    'high': float(row.high_price) if row.high_price else None,
                    'low': float(row.low_price) if row.low_price else None,
                    'close': float(row.close_price) if row.close_price else None,
                    'volume': int(row.volume) if row.volume else None,
                    'amount': float(row.amount) if row.amount else None,
                })

            df = pd.DataFrame(data)

            self.logger.info(
                f"載入區間資料: start={start}, end={end}, "
                f"stock_id={stock_id or 'all'}, "
                f"records={len(df)}, "
                f"stocks={df['stock_id'].nunique() if not df.empty else 0}"
            )

            return df

    def load_historical_data(
        self,
        target_date: Union[str, datetime],
        lookback_days: int = 550,
        stock_id: Optional[str] = None
    ) -> pd.DataFrame:
        """
        載入歷史資料 (用於計算技術指標)

        Args:
            target_date: 目標日期
            lookback_days: 回溯天數 (預設 550 天，約 1.5 年)
            stock_id: 股票代碼 (選用)

        Returns:
            pd.DataFrame: 歷史價格資料
        """
        if isinstance(target_date, str):
            target = datetime.strptime(target_date, "%Y-%m-%d")
        else:
            target = target_date

        # 計算起始日期
        start_date = target - timedelta(days=lookback_days)

        self.logger.info(
            f"載入歷史資料: {start_date.date()} 到 {target.date()}, "
            f"stock_id={stock_id or 'all'}"
        )

        # 載入區間資料
        df = self.load_price_data_range(start_date, target, stock_id)

        if df.empty:
            self.logger.warning("無歷史資料")
            return pd.DataFrame()

        # 確保日期格式正確
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df = df.sort_values(['stock_id', 'trade_date'])

        self.logger.info(
            f"歷史資料載入完成: {len(df)} 筆記錄, "
            f"{df['stock_id'].nunique()} 檔股票"
        )

        return df

    def get_available_dates(
        self,
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None
    ) -> List[str]:
        """
        獲取資料庫中可用的交易日期列表

        Args:
            start_date: 開始日期 (選用)
            end_date: 結束日期 (選用)

        Returns:
            List[str]: 交易日期列表 (YYYY-MM-DD 格式)
        """
        with self.db_manager.get_session() as session:
            query = select(StockPriceDaily.trade_date).distinct()

            # 加入日期範圍篩選
            if start_date:
                if isinstance(start_date, str):
                    start = datetime.strptime(start_date, "%Y-%m-%d").date()
                else:
                    start = start_date.date() if isinstance(start_date, datetime) else start_date
                query = query.where(StockPriceDaily.trade_date >= start)

            if end_date:
                if isinstance(end_date, str):
                    end = datetime.strptime(end_date, "%Y-%m-%d").date()
                else:
                    end = end_date.date() if isinstance(end_date, datetime) else end_date
                query = query.where(StockPriceDaily.trade_date <= end)

            # 排序
            query = query.order_by(StockPriceDaily.trade_date)

            # 執行查詢
            results = session.execute(query).scalars().all()

            # 轉換為字串列表
            dates = [date.strftime('%Y-%m-%d') for date in results]

            return dates

    def get_stock_list(self) -> pd.DataFrame:
        """
        獲取股票清單

        Returns:
            pd.DataFrame: 股票清單，包含 stock_id, stock_name, market_type
        """
        with self.db_manager.get_session() as session:
            query = select(Stock).order_by(Stock.stock_id)
            results = session.execute(query).scalars().all()

            if not results:
                return pd.DataFrame()

            data = [{
                'stock_id': row.stock_id,
                'stock_name': row.stock_name,
                'market_type': row.market_type,
            } for row in results]

            return pd.DataFrame(data)

    def test_connection(self) -> bool:
        """
        測試資料庫連線

        Returns:
            bool: 連線是否成功
        """
        return self.db_manager.test_connection()


# 建立全域載入器實例 (單例模式)
_database_loader: Optional[DatabaseLoader] = None


def get_database_loader(config: Optional[DatabaseConfig] = None) -> DatabaseLoader:
    """
    獲取全域資料庫載入器實例

    Args:
        config: 資料庫配置 (選用)

    Returns:
        DatabaseLoader: 資料庫載入器實例
    """
    global _database_loader

    if _database_loader is None:
        _database_loader = DatabaseLoader(config)

    return _database_loader
