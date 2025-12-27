"""
法人買賣收集器

收集三大法人買賣超資料：
- 外資買賣超
- 投信買賣超
- 自營商買賣超

使用 aggregate API 一次取得所有股票的資料
"""

from datetime import datetime
from typing import Optional, Union
import pandas as pd

from .base_collector import BaseCollector, CollectorError
from ..utils import get_logger

logger = get_logger(__name__)


class InstitutionalCollector(BaseCollector):
    """法人買賣收集器"""

    def get_data_type(self) -> str:
        """返回資料類型"""
        return 'institutional'

    def collect(
        self,
        date: Union[str, datetime],
        stock_id: Optional[str] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        收集法人買賣資料

        Args:
            date: 收集日期
            stock_id: 股票代碼 (選用，不提供時取得所有股票)
            **kwargs: 其他參數

        Returns:
            pd.DataFrame: 法人買賣資料

        Examples:
            >>> collector = InstitutionalCollector()

            # 單一股票
            >>> df = collector.collect('2025-01-28', stock_id='2330')

            # 所有股票 (推薦，使用 aggregate API)
            >>> df = collector.collect('2025-01-28')
        """
        date_str = self._format_date(date)

        if stock_id:
            self.logger.info(f"收集法人買賣: {stock_id}, {date_str}")
            # 單一股票
            df = self.fetch_with_retry(
                self.dl.taiwan_stock_institutional_investors,
                stock_id=stock_id,
                start_date=date_str,
                end_date=date_str
            )
        else:
            # 所有股票 (aggregate API)
            self.logger.info(f"收集法人買賣 (所有股票): {date_str}")
            df = self.fetch_with_retry(
                self.dl.taiwan_stock_institutional_investors,
                start_date=date_str,
                end_date=date_str
            )

        if df is None or df.empty:
            self.logger.warning(f"無資料: {date_str}")
            return pd.DataFrame()

        # 資料處理
        df = self._process_data(df)

        self.logger.debug(f"收集完成: {len(df)} 筆")
        return df

    def _process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        處理原始資料

        Args:
            df: 原始 DataFrame

        Returns:
            pd.DataFrame: 處理後的 DataFrame
        """
        # FinMind 返回的欄位:
        # date, stock_id, name,
        # Foreign_Investor_Buy, Foreign_Investor_Sell, Foreign_Investor_Net,
        # Investment_Trust_Buy, Investment_Trust_Sell, Investment_Trust_Net,
        # Dealer_self_Buy, Dealer_self_Sell, Dealer_self_Net,
        # Dealer_Hedging_Buy, Dealer_Hedging_Sell, Dealer_Hedging_Net

        # 重新命名為更簡潔的名稱
        column_mapping = {
            'date': 'date',
            'stock_id': 'stock_id',
            'name': 'stock_name',
            # 外資
            'Foreign_Investor_Buy': 'foreign_buy',
            'Foreign_Investor_Sell': 'foreign_sell',
            'Foreign_Investor_Net': 'foreign_net',
            # 投信
            'Investment_Trust_Buy': 'trust_buy',
            'Investment_Trust_Sell': 'trust_sell',
            'Investment_Trust_Net': 'trust_net',
            # 自營商 (自行買賣)
            'Dealer_self_Buy': 'dealer_self_buy',
            'Dealer_self_Sell': 'dealer_self_sell',
            'Dealer_self_Net': 'dealer_self_net',
            # 自營商 (避險)
            'Dealer_Hedging_Buy': 'dealer_hedging_buy',
            'Dealer_Hedging_Sell': 'dealer_hedging_sell',
            'Dealer_Hedging_Net': 'dealer_hedging_net'
        }

        existing_cols = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df.rename(columns=existing_cols)

        # 計算自營商合計
        if all(col in df.columns for col in ['dealer_self_net', 'dealer_hedging_net']):
            df['dealer_net'] = df['dealer_self_net'] + df['dealer_hedging_net']

        # 確保數值類型
        numeric_cols = [
            'foreign_buy', 'foreign_sell', 'foreign_net',
            'trust_buy', 'trust_sell', 'trust_net',
            'dealer_self_buy', 'dealer_self_sell', 'dealer_self_net',
            'dealer_hedging_buy', 'dealer_hedging_sell', 'dealer_hedging_net',
            'dealer_net'
        ]

        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 排序
        if all(col in df.columns for col in ['date', 'stock_id']):
            df = df.sort_values(['date', 'stock_id']).reset_index(drop=True)

        return df


def create_institutional_collector(api_token: Optional[str] = None) -> InstitutionalCollector:
    """
    建立法人買賣收集器實例 (便利函數)

    Args:
        api_token: FinMind API Token

    Returns:
        InstitutionalCollector 實例

    Examples:
        >>> collector = create_institutional_collector()
        >>> # 推薦：一次取得所有股票
        >>> df = collector.collect('2025-01-28')
        >>> df.to_csv('data/institutional_2025-01-28.csv', index=False)
    """
    return InstitutionalCollector(api_token=api_token)
