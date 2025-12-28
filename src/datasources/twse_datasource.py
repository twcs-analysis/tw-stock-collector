"""
台灣證券交易所 (TWSE) 資料源

使用 TWSE OpenAPI 取得上市股票資料
"""
import requests
import pandas as pd
from typing import Optional, List
import logging

from .base_datasource import BaseDataSource

logger = logging.getLogger(__name__)


class TWSEDataSource(BaseDataSource):
    """TWSE 官方 API 資料源"""

    BASE_URL = "https://openapi.twse.com.tw/v1"

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()

    def get_daily_prices(
        self,
        date: str,
        stock_ids: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        取得 TWSE 每日價量資料

        API: /exchangeReport/STOCK_DAY_ALL
        回傳當日所有上市股票成交資訊
        """
        url = f"{self.BASE_URL}/exchangeReport/STOCK_DAY_ALL"

        try:
            logger.info(f"查詢 TWSE API: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            if not data:
                logger.warning(f"TWSE 無資料: {date}")
                return pd.DataFrame()

            # 轉換為 DataFrame
            df = pd.DataFrame(data)
            logger.info(f"TWSE 原始資料: {len(df)} 筆")

            # 欄位對應
            df = df.rename(columns={
                'Code': 'stock_id',
                'Name': 'stock_name',
                'OpeningPrice': 'open',
                'HighestPrice': 'high',
                'LowestPrice': 'low',
                'ClosingPrice': 'close',
                'TradeVolume': 'volume',
                'TradeValue': 'amount',
                'Transaction': 'transaction_count',
                'Change': 'change_price'
            })

            # 只保留 4 位數股票代碼（排除 ETF、權證等）
            df = df[df['stock_id'].str.len() == 4]
            df = df[df['stock_id'].str.isdigit()]

            # 加入日期
            df['date'] = date

            # 資料清理：移除逗號並轉換為數值
            numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount', 'transaction_count', 'change_price']
            for col in numeric_cols:
                if col in df.columns:
                    # 移除逗號、處理特殊符號
                    df[col] = df[col].astype(str).str.replace(',', '').str.replace('--', '0').str.replace('X', '0')
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # 篩選股票
            if stock_ids:
                df = df[df['stock_id'].isin(stock_ids)]

            # 加入市場類型
            df['type'] = 'twse'

            # 只保留需要的欄位，移除多餘欄位
            keep_cols = ['date', 'stock_id', 'stock_name', 'open', 'high', 'low', 'close',
                        'volume', 'amount', 'transaction_count', 'change_price', 'type']
            df = df[[col for col in keep_cols if col in df.columns]]

            logger.info(f"TWSE 價量資料（篩選後）: {len(df)} 筆 ({date})")
            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"TWSE API 請求錯誤: {e}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"TWSE API 處理錯誤: {e}", exc_info=True)
            return pd.DataFrame()

    def is_available(self, date: str) -> bool:
        """檢查資料是否可用"""
        df = self.get_daily_prices(date)
        return not df.empty
