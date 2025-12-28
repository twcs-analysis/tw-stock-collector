"""
融資融券收集器

收集融資融券資料：
- 融資買進、賣出、餘額
- 融券賣出、買進、餘額
- 券資比

使用 aggregate API
"""

from datetime import datetime
from typing import Optional, Union
import pandas as pd

from .base_collector import BaseCollector
from ..utils import get_logger

logger = get_logger(__name__)


class MarginCollector(BaseCollector):
    """融資融券收集器"""

    def get_data_type(self) -> str:
        return 'margin'

    def collect(
        self,
        date: Union[str, datetime],
        stock_id: str,
        **kwargs
    ) -> pd.DataFrame:
        """
        收集融資融券資料

        Args:
            date: 日期
            stock_id: 股票代碼

        Returns:
            pd.DataFrame: 融資融券資料
        """
        date_str = self._format_date(date)
        self.logger.info(f"收集融資融券: {stock_id}, {date_str}")

        df = self.fetch_with_retry(
            self.dl.taiwan_stock_margin_purchase_short_sale,
            stock_id=stock_id,
            start_date=date_str,
            end_date=date_str
        )

        if df is None or df.empty:
            return pd.DataFrame()

        return self._process_data(df)

    def _process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """處理資料"""
        column_mapping = {
            'date': 'date',
            'stock_id': 'stock_id',
            # 融資
            'MarginPurchaseBuy': 'margin_purchase',
            'MarginPurchaseSell': 'margin_sale',
            'MarginPurchaseCashRepayment': 'margin_cash_repayment',
            'MarginPurchaseYesterdayBalance': 'margin_yesterday_balance',
            'MarginPurchaseTodayBalance': 'margin_balance',
            # 融券
            'ShortSaleBuy': 'short_covering',
            'ShortSaleSell': 'short_sale',
            'ShortSaleCashRepayment': 'short_cash_repayment',
            'ShortSaleYesterdayBalance': 'short_yesterday_balance',
            'ShortSaleTodayBalance': 'short_balance',
            # 券資比
            'MarginPurchaseLimit': 'margin_limit',
            'ShortSaleLimit': 'short_limit'
        }

        existing_cols = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df.rename(columns=existing_cols)

        # 計算券資比
        if all(col in df.columns for col in ['short_balance', 'margin_balance']):
            df['short_to_margin_ratio'] = (
                df['short_balance'] / df['margin_balance'].replace(0, pd.NA)
            ).round(4)

        # 數值類型轉換
        numeric_cols = [col for col in df.columns if col not in ['date', 'stock_id']]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        return df.sort_values(['date', 'stock_id'], ignore_index=True) if 'stock_id' in df.columns else df


def create_margin_collector(api_token: Optional[str] = None) -> MarginCollector:
    """建立融資融券收集器"""
    return MarginCollector(api_token=api_token)
