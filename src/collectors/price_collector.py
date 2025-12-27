"""
價格資料收集器

收集每日 OHLCV 資料：
- 開盤價、最高價、最低價、收盤價
- 成交量、成交金額
- 漲跌幅
"""

from datetime import datetime
from typing import List, Optional, Union
import pandas as pd

from .base_collector import BaseCollector, CollectorError
from ..utils import get_logger

logger = get_logger(__name__)


class PriceCollector(BaseCollector):
    """價格資料收集器"""

    def get_data_type(self) -> str:
        """返回資料類型"""
        return 'price'

    def collect(
        self,
        date: Union[str, datetime],
        stock_id: Optional[str] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        收集價格資料

        Args:
            date: 收集日期
            stock_id: 股票代碼 (必須提供)
            **kwargs: 其他參數

        Returns:
            pd.DataFrame: 價格資料

        Raises:
            CollectorError: 收集失敗

        Examples:
            >>> collector = PriceCollector()
            >>> df = collector.collect('2025-01-28', stock_id='2330')
            >>> print(df[['date', 'open', 'high', 'low', 'close', 'volume']])
        """
        if stock_id is None:
            raise CollectorError("價格資料收集需要提供 stock_id")

        date_str = self._format_date(date)
        self.logger.info(f"收集價格資料: {stock_id}, {date_str}")

        # 呼叫 FinMind API
        df = self.fetch_with_retry(
            self.dl.taiwan_stock_daily,
            stock_id=stock_id,
            start_date=date_str,
            end_date=date_str
        )

        if df is None or df.empty:
            self.logger.warning(f"無資料: {stock_id}, {date_str}")
            return pd.DataFrame()

        # 資料處理
        df = self._process_data(df)

        self.logger.debug(f"收集完成: {stock_id}, {len(df)} 筆")
        return df

    def collect_multiple_stocks(
        self,
        date: Union[str, datetime],
        stock_ids: List[str],
        **kwargs
    ) -> pd.DataFrame:
        """
        收集多檔股票的價格資料

        Args:
            date: 日期
            stock_ids: 股票代碼列表
            **kwargs: 其他參數

        Returns:
            pd.DataFrame: 所有股票的價格資料

        Examples:
            >>> collector = PriceCollector()
            >>> stock_ids = ['2330', '2317', '2454']
            >>> df = collector.collect_multiple_stocks('2025-01-28', stock_ids)
        """
        date_str = self._format_date(date)
        self.logger.info(f"收集多檔價格資料: {len(stock_ids)} 檔, {date_str}")

        all_data = []

        for stock_id in stock_ids:
            try:
                df = self.collect(date, stock_id, **kwargs)
                if not df.empty:
                    all_data.append(df)
            except Exception as e:
                self.logger.error(f"收集失敗: {stock_id}, {e}")
                continue

        if not all_data:
            return pd.DataFrame()

        # 合併所有資料
        combined_df = pd.concat(all_data, ignore_index=True)
        self.logger.info(f"收集完成: {len(combined_df)} 筆 ({len(all_data)} 檔股票)")

        return combined_df

    def _process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        處理原始資料

        Args:
            df: 原始 DataFrame

        Returns:
            pd.DataFrame: 處理後的 DataFrame
        """
        # 重新命名欄位 (根據 FinMind 實際返回的欄位)
        column_mapping = {
            'date': 'date',
            'stock_id': 'stock_id',
            'Trading_Volume': 'volume',
            'Trading_money': 'amount',
            'open': 'open',
            'max': 'high',
            'min': 'low',
            'close': 'close',
            'spread': 'change_price',
            'Trading_turnover': 'transaction_count'
        }

        # 只保留存在的欄位
        existing_cols = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df.rename(columns=existing_cols)

        # 計算漲跌幅 (如果還沒有)
        if 'change_rate' not in df.columns and 'change_price' in df.columns and 'close' in df.columns:
            df['change_rate'] = (df['change_price'] / (df['close'] - df['change_price'])).round(4)

        # 確保數值類型
        numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount', 'change_price', 'change_rate']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 排序
        if 'date' in df.columns:
            df = df.sort_values('date').reset_index(drop=True)

        return df


def create_price_collector(api_token: Optional[str] = None) -> PriceCollector:
    """
    建立價格收集器實例 (便利函數)

    Args:
        api_token: FinMind API Token

    Returns:
        PriceCollector 實例

    Examples:
        >>> collector = create_price_collector()
        >>> df = collector.collect('2025-01-28', '2330')
    """
    return PriceCollector(api_token=api_token)
