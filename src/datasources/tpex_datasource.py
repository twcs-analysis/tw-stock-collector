"""
證券櫃買中心 (TPEx) 資料源

使用 TPEx OpenAPI 取得上櫃股票資料
"""
import requests
import pandas as pd
from typing import Optional, List
import logging

from .base_datasource import BaseDataSource

logger = logging.getLogger(__name__)


class TPExDataSource(BaseDataSource):
    """TPEx 官方 API 資料源"""

    BASE_URL = "https://www.tpex.org.tw/openapi/v1"

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()

    def get_daily_prices(
        self,
        date: str,
        stock_ids: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        取得 TPEx 每日價量資料

        API: /tpex_mainboard_quotes
        回傳上櫃股票行情
        """
        url = f"{self.BASE_URL}/tpex_mainboard_quotes"

        try:
            logger.info(f"查詢 TPEx API: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            if not data:
                logger.warning(f"TPEx 無資料: {date}")
                return pd.DataFrame()

            df = pd.DataFrame(data)
            logger.info(f"TPEx 原始資料: {len(df)} 筆")

            # 欄位對應（根據 TPEx API 實際欄位）
            df = df.rename(columns={
                'SecuritiesCompanyCode': 'stock_id',
                'CompanyName': 'stock_name',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'TradingShares': 'volume',
                'TransactionAmount': 'amount',
                'TransactionNumber': 'transaction_count'
            })

            # 只保留 4 位數股票代碼
            df = df[df['stock_id'].str.len() == 4]
            df = df[df['stock_id'].str.isdigit()]

            df['date'] = date
            df['type'] = 'tpex'

            # 資料清理
            numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount', 'transaction_count']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.replace(',', '')
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            if stock_ids:
                df = df[df['stock_id'].isin(stock_ids)]

            # 只保留需要的欄位，移除多餘欄位
            keep_cols = ['date', 'stock_id', 'stock_name', 'open', 'high', 'low', 'close',
                        'volume', 'amount', 'transaction_count', 'type']
            df = df[[col for col in keep_cols if col in df.columns]]

            logger.info(f"TPEx 價量資料（篩選後）: {len(df)} 筆 ({date})")
            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"TPEx API 請求錯誤: {e}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"TPEx API 處理錯誤: {e}", exc_info=True)
            return pd.DataFrame()

    def is_available(self, date: str) -> bool:
        """檢查資料是否可用"""
        df = self.get_daily_prices(date)
        return not df.empty
