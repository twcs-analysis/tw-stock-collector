"""
借券賣出收集器
"""

from datetime import datetime
from typing import Optional, Union
import pandas as pd

from .base_collector import BaseCollector
from ..utils import get_logger

logger = get_logger(__name__)


class LendingCollector(BaseCollector):
    """借券賣出收集器"""

    def get_data_type(self) -> str:
        return 'lending'

    def collect(
        self,
        date: Union[str, datetime],
        stock_id: str,
        **kwargs
    ) -> pd.DataFrame:
        """收集借券賣出資料"""
        date_str = self._format_date(date)

        df = self.fetch_with_retry(
            self.dl.taiwan_stock_securities_lending,
            stock_id=stock_id,
            start_date=date_str,
            end_date=date_str
        )

        return self._process_data(df) if df is not None and not df.empty else pd.DataFrame()

    def _process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """處理資料"""
        column_mapping = {
            'date': 'date',
            'stock_id': 'stock_id',
            'Securities_Lending_Sale': 'lending_sale',
            'Securities_Lending_Return': 'lending_return',
            'Securities_Lending_Balance': 'lending_balance',
            'Securities_Lending_Limit': 'lending_limit'
        }

        existing_cols = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df.rename(columns=existing_cols)

        numeric_cols = [col for col in df.columns if col not in ['date', 'stock_id']]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        return df.sort_values(['date', 'stock_id'], ignore_index=True) if 'stock_id' in df.columns else df


def create_lending_collector(api_token: Optional[str] = None) -> LendingCollector:
    return LendingCollector(api_token=api_token)
