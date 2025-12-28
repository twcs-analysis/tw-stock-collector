"""
融資融券收集器

使用官方 API 收集融資融券資料：
- TWSE: 台灣證券交易所
- TPEx: 證券櫃買中心

資料包含：
- 融資買進、賣出、現金償還、餘額、限額
- 融券買進、賣出、償還、餘額、限額
- 資券相抵
"""

from datetime import datetime
from typing import Optional, Union
import pandas as pd

from .base_collector import BaseCollector
from ..datasources.twse_margin_datasource import TWSEMarginDataSource
from ..datasources.tpex_margin_datasource import TPExMarginDataSource
from ..utils.data_merger import DataMerger
from ..utils import get_logger

logger = get_logger(__name__)


class MarginCollector(BaseCollector):
    """融資融券收集器 - 使用官方 API"""

    def __init__(self, config=None, timeout: int = 30):
        """
        初始化融資融券收集器

        Args:
            config: 配置物件
            timeout: API 請求逾時時間（秒）
        """
        super().__init__(config)
        self.twse_source = TWSEMarginDataSource(timeout=timeout)
        self.tpex_source = TPExMarginDataSource(timeout=timeout)
        self.merger = DataMerger()
        self.timeout = timeout

    def get_data_type(self) -> str:
        return 'margin'

    def collect(
        self,
        date: Union[str, datetime],
        stock_id: Optional[str] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        收集融資融券資料

        Args:
            date: 日期
            stock_id: 股票代碼（可選，None 表示全部股票）

        Returns:
            pd.DataFrame: 融資融券資料
        """
        date_str = self._format_date(date)

        if stock_id:
            self.logger.info(f"收集融資融券: {stock_id}, {date_str}")
        else:
            self.logger.info(f"收集全部融資融券資料: {date_str}")

        # 記錄 API 呼叫次數
        self.stats['api_calls'] += 2  # TWSE + TPEx

        # 收集 TWSE 上市資料
        try:
            twse_df = self.twse_source.get_margin_data(date_str)
            self.logger.info(f"TWSE 融資融券資料: {len(twse_df)} 筆")
        except Exception as e:
            self.logger.error(f"收集 TWSE 融資融券失敗: {e}")
            twse_df = pd.DataFrame()

        # 收集 TPEx 上櫃資料
        try:
            tpex_df = self.tpex_source.get_margin_data(date_str)
            self.logger.info(f"TPEx 融資融券資料: {len(tpex_df)} 筆")
        except Exception as e:
            self.logger.error(f"收集 TPEx 融資融券失敗: {e}")
            tpex_df = pd.DataFrame()

        # 合併資料
        merged_df = self.merger.merge_dataframes([twse_df, tpex_df], deduplicate_by='stock_id')

        if merged_df.empty:
            self.logger.warning(f"無融資融券資料: {date_str}")
            return pd.DataFrame()

        self.logger.info(f"合併後融資融券資料: {len(merged_df)} 筆")

        # 過濾特定股票（如果指定）
        if stock_id:
            merged_df = merged_df[merged_df['stock_id'] == stock_id]
            if merged_df.empty:
                self.logger.warning(f"查無股票 {stock_id} 的融資融券資料")

        # 處理資料
        processed_df = self._process_data(merged_df)

        # 記錄成功收集的資料筆數
        self.stats['records_collected'] += len(processed_df)

        return processed_df

    def _process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        處理資料

        Args:
            df: 原始資料

        Returns:
            處理後的資料
        """
        if df.empty:
            return df

        # 計算券資比
        if all(col in df.columns for col in ['short_balance', 'margin_balance']):
            df['short_to_margin_ratio'] = (
                df['short_balance'] / df['margin_balance'].replace(0, pd.NA)
            ).round(4)

        # 確保數值類型
        numeric_cols = [
            'margin_buy', 'margin_sell', 'margin_cash_repay',
            'margin_balance_prev', 'margin_balance', 'margin_quota',
            'short_covering', 'short_sell', 'short_repay',
            'short_balance_prev', 'short_balance', 'short_quota',
            'offset', 'short_to_margin_ratio'
        ]

        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 排序
        sort_cols = ['date', 'stock_id'] if 'stock_id' in df.columns else ['date']
        return df.sort_values(sort_cols, ignore_index=True)


def create_margin_collector(config=None, timeout: int = 30) -> MarginCollector:
    """
    建立融資融券收集器

    Args:
        config: 配置物件
        timeout: API 請求逾時時間（秒）

    Returns:
        MarginCollector: 融資融券收集器
    """
    return MarginCollector(config=config, timeout=timeout)
