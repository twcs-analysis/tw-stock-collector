"""
資料源基礎類別

定義所有資料源必須實作的介面
"""
from abc import ABC, abstractmethod
from typing import Optional, List
import pandas as pd


class BaseDataSource(ABC):
    """資料源基礎抽象類別"""

    @abstractmethod
    def get_daily_prices(
        self,
        date: str,
        stock_ids: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        取得每日價量資料

        Args:
            date: YYYY-MM-DD
            stock_ids: 股票代碼列表，None = 全部

        Returns:
            DataFrame with columns:
                - date, stock_id, open, high, low, close
                - volume, amount, transaction_count
        """
        pass

    @abstractmethod
    def is_available(self, date: str) -> bool:
        """
        檢查該日期資料是否可用

        Args:
            date: YYYY-MM-DD

        Returns:
            bool: True if data is available
        """
        pass
