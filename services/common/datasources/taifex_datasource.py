"""
台灣期貨交易所 (TAIFEX) 資料源

提供個股期貨每日交易資料
"""
import requests
import pandas as pd
from typing import Optional, List, Dict
from datetime import datetime
import logging

from .base_datasource import BaseDataSource

logger = logging.getLogger(__name__)


class TAIFEXDataSource(BaseDataSource):
    """TAIFEX OpenAPI 資料源"""

    BASE_URL = "https://openapi.taifex.com.tw/v1"

    def __init__(self, timeout: int = 30):
        """
        初始化 TAIFEX 資料源

        Args:
            timeout: API 請求超時時間（秒）
        """
        self.timeout = timeout
        self.session = requests.Session()
        self._contract_mapping = None  # 快取期貨代碼對應表

    def get_daily_prices(
        self,
        date: str,
        stock_ids: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        取得個股期貨每日交易資料

        Args:
            date: 查詢日期 (YYYY-MM-DD)
            stock_ids: 股票代碼列表（選用，用於篩選特定股票）

        Returns:
            pd.DataFrame: 個股期貨交易資料
                欄位: date, contract, stock_id, stock_name, contract_month,
                     open, high, low, close, change, change_percent,
                     volume, settlement_price, open_interest,
                     best_bid, best_ask, trading_session, type
        """
        try:
            # 取得所有期貨資料
            all_futures_data = self._get_all_futures_data(date)

            if not all_futures_data:
                logger.warning(f"TAIFEX 無資料: {date}")
                return pd.DataFrame()

            # 過濾出個股期貨（Contract 開頭為 C）
            stock_futures = [
                item for item in all_futures_data
                if item.get('Contract', '').startswith('C')
            ]

            if not stock_futures:
                logger.warning(f"無個股期貨資料: {date}")
                return pd.DataFrame()

            # 轉換為 DataFrame
            df = pd.DataFrame(stock_futures)
            logger.info(f"TAIFEX 個股期貨原始資料: {len(df)} 筆")

            # 取得期貨代碼對應表（期貨代碼 -> 股票代碼）
            contract_mapping = self._get_contract_mapping()

            # 轉換資料格式
            df = self._transform_data(df, contract_mapping, date)

            # 如果指定了股票代碼，進行篩選
            if stock_ids:
                df = df[df['stock_id'].isin(stock_ids)]
                logger.info(f"篩選指定股票後: {len(df)} 筆")

            logger.info(f"TAIFEX 處理完成: {len(df)} 筆個股期貨資料")
            return df

        except Exception as e:
            logger.error(f"取得 TAIFEX 資料失敗: {e}", exc_info=True)
            return pd.DataFrame()

    def _get_all_futures_data(self, date: str) -> List[Dict]:
        """
        取得所有期貨商品的每日交易資料

        Args:
            date: YYYY-MM-DD

        Returns:
            list: 所有期貨資料
        """
        # 轉換日期格式為 YYYY-MM-DD（API 要求格式）
        url = f"{self.BASE_URL}/DailyMarketReportFut"
        params = {"date": date}

        logger.info(f"查詢 TAIFEX API: {url}?date={date}")

        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()

        data = response.json()

        if not data:
            logger.warning(f"API 回傳空資料: {date}")
            return []

        logger.info(f"TAIFEX API 回傳: {len(data)} 筆期貨資料")
        return data

    def _get_contract_mapping(self) -> Dict[str, Dict[str, str]]:
        """
        取得期貨代碼與股票代碼的對應關係

        Returns:
            dict: {期貨代碼: {stock_code: 股票代碼, stock_name: 股票名稱}}
        """
        # 使用快取避免重複查詢
        if self._contract_mapping is not None:
            return self._contract_mapping

        url = f"{self.BASE_URL}/SSFLists"

        try:
            logger.info(f"查詢期貨標的對應表: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            # 建立對應字典
            mapping = {
                item['Contract']: {
                    'stock_code': item['StockCode'],
                    'stock_name': item['StockName']
                }
                for item in data
            }

            self._contract_mapping = mapping
            logger.info(f"期貨標的對應表: {len(mapping)} 個標的")
            return mapping

        except Exception as e:
            logger.error(f"取得期貨標的對應表失敗: {e}", exc_info=True)
            return {}

    def _transform_data(
        self,
        df: pd.DataFrame,
        contract_mapping: Dict[str, Dict[str, str]],
        date: str
    ) -> pd.DataFrame:
        """
        轉換資料格式為統一格式

        Args:
            df: 原始資料 DataFrame
            contract_mapping: 期貨代碼對應表
            date: 日期 (YYYY-MM-DD)

        Returns:
            pd.DataFrame: 轉換後的資料
        """
        # 新增股票代碼和名稱欄位
        df['stock_id'] = df['Contract'].map(
            lambda x: contract_mapping.get(x, {}).get('stock_code', '')
        )
        df['stock_name'] = df['Contract'].map(
            lambda x: contract_mapping.get(x, {}).get('stock_name', '')
        )

        # 欄位對應與重新命名
        df = df.rename(columns={
            'Contract': 'contract',
            'ContractMonth(Week)': 'contract_month',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Last': 'close',
            'Change': 'change',
            '%': 'change_percent',
            'Volume': 'volume',
            'SettlementPrice': 'settlement_price',
            'OpenInterest': 'open_interest',
            'BestBid': 'best_bid',
            'BestAsk': 'best_ask',
            'TradingSession': 'trading_session',
        })

        # 新增日期欄位（統一格式 YYYY-MM-DD）
        df['date'] = date

        # 新增 type 欄位（標記為期貨）
        df['type'] = 'taifex'

        # 處理數值欄位（將 "-" 轉換為 None）
        numeric_columns = [
            'open', 'high', 'low', 'close',
            'volume', 'settlement_price', 'open_interest',
            'best_bid', 'best_ask'
        ]

        for col in numeric_columns:
            if col in df.columns:
                # 將 "-" 和空字串轉為 None
                df[col] = df[col].replace(['-', ''], None)
                # 轉換為數值型態（會自動處理千分位逗號）
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')

        # 選擇需要的欄位
        columns = [
            'date', 'contract', 'stock_id', 'stock_name', 'contract_month',
            'open', 'high', 'low', 'close', 'change', 'change_percent',
            'volume', 'settlement_price', 'open_interest',
            'best_bid', 'best_ask', 'trading_session', 'type'
        ]

        # 只保留存在的欄位
        available_columns = [col for col in columns if col in df.columns]
        df = df[available_columns]

        return df

    def is_available(self, date: str) -> bool:
        """
        檢查該日期資料是否可用

        Args:
            date: YYYY-MM-DD

        Returns:
            bool: True 表示有資料
        """
        try:
            data = self._get_all_futures_data(date)
            return len(data) > 0
        except Exception as e:
            logger.error(f"檢查資料可用性失敗: {e}")
            return False

    def get_contract_info(self, contract_code: str) -> Optional[Dict[str, str]]:
        """
        取得指定期貨代碼的標的資訊

        Args:
            contract_code: 期貨代碼（例如：CDF）

        Returns:
            dict: {stock_code: 股票代碼, stock_name: 股票名稱}
                  若找不到則返回 None
        """
        mapping = self._get_contract_mapping()
        return mapping.get(contract_code)

    def get_all_contracts(self) -> List[Dict[str, str]]:
        """
        取得所有個股期貨標的清單

        Returns:
            list: [{contract: 期貨代碼, stock_code: 股票代碼, stock_name: 股票名稱}]
        """
        mapping = self._get_contract_mapping()
        return [
            {
                'contract': contract,
                'stock_code': info['stock_code'],
                'stock_name': info['stock_name']
            }
            for contract, info in mapping.items()
        ]
