"""
台灣證券交易所 (TWSE) 資料源 - 雙模式架構

策略：
1. 即時模式：使用 STOCK_DAY_ALL OpenAPI（當日最新資料，快速）
   - API: https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL
   - 速度：~2-3 秒
   - 用途：每日自動收集

2. 回補模式：使用 MI_INDEX API（歷史資料，快速）
   - API: https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX
   - 速度：~2-3 秒（一次取得所有股票）
   - 用途：歷史資料回補
   - 說明：此 API 支援歷史日期查詢，比逐股查詢快得多
"""
import requests
import pandas as pd
from typing import Optional, List
from datetime import datetime
import logging
import urllib3
import time

from .base_datasource import BaseDataSource

# 關閉 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class TWSEDataSource(BaseDataSource):
    """TWSE 官方 API 資料源"""

    BASE_URL = "https://www.twse.com.tw"
    # OpenAPI 僅支援當日最新資料
    BASE_URL_OPENAPI = "https://openapi.twse.com.tw/v1"

    def __init__(self, timeout: int = 30, use_backfill_mode: bool = False):
        """
        Args:
            timeout: API 請求超時時間
            use_backfill_mode: 是否使用回補模式（逐股查詢，慢但可取得歷史資料）
        """
        self.timeout = timeout
        self.use_backfill_mode = use_backfill_mode
        self.session = requests.Session()

    def get_daily_prices(
        self,
        date: str,
        stock_ids: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        取得 TWSE 每日價量資料

        Args:
            date: 查詢日期 (YYYY-MM-DD)
            stock_ids: 股票代碼列表（選用，回補模式下使用）

        Returns:
            pd.DataFrame: 價格資料，若無資料或非交易日則返回空 DataFrame
        """
        if self.use_backfill_mode:
            return self._get_daily_prices_backfill(date, stock_ids)
        else:
            return self._get_daily_prices_realtime(date)

    def _get_daily_prices_realtime(self, date: str) -> pd.DataFrame:
        """
        即時模式：使用 OpenAPI 取得當日所有股票資料

        注意：此 API 只能取得最新交易日資料，無法指定歷史日期
        """
        url = f"{self.BASE_URL_OPENAPI}/exchangeReport/STOCK_DAY_ALL"

        try:
            logger.info(f"查詢 TWSE OpenAPI (當日模式): {url}")
            response = self.session.get(url, timeout=self.timeout, verify=False)
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
                    df[col] = df[col].astype(str).str.replace(',', '').str.replace('--', '0').str.replace('X', '0')
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # 加入市場類型
            df['type'] = 'twse'

            # 只保留需要的欄位
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

    def _get_daily_prices_backfill(
        self,
        date: str,
        stock_ids: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        回補模式：使用 MI_INDEX API 取得歷史資料（快速版本）

        此方法使用 MI_INDEX API，一次請求即可取得所有股票資料，速度快！
        約 2-3 秒即可完成（vs 舊方法需要 20-30 分鐘）

        Args:
            date: 查詢日期 (YYYY-MM-DD)
            stock_ids: 股票代碼列表（選用，用於篩選特定股票）
        """
        # 將日期轉換為 YYYYMMDD 格式
        date_str = date.replace('-', '')
        url = f"{self.BASE_URL}/rwd/zh/afterTrading/MI_INDEX"
        params = {
            'date': date_str,
            'type': 'ALL',
            'response': 'json'
        }

        try:
            logger.info(f"查詢 TWSE MI_INDEX (回補模式): {url}?date={date_str}")
            response = self.session.get(url, params=params, timeout=self.timeout, verify=False)
            response.raise_for_status()
            data = response.json()

            # 檢查 API 狀態
            if data.get('stat') != 'OK':
                logger.warning(f"TWSE MI_INDEX API 返回非 OK 狀態: {data.get('stat', 'N/A')}")
                return pd.DataFrame()

            # 取得 tables[8] 的股票資料
            tables = data.get('tables', [])
            if len(tables) <= 8:
                logger.warning(f"TWSE MI_INDEX 無 tables[8] 資料: {date}")
                return pd.DataFrame()

            table_8 = tables[8]
            columns = table_8.get('fields', [])
            rows = table_8.get('data', [])

            if not rows:
                logger.warning(f"TWSE MI_INDEX 無資料: {date}")
                return pd.DataFrame()

            # 轉換為 DataFrame
            df = pd.DataFrame(rows, columns=columns)
            logger.info(f"TWSE MI_INDEX 原始資料: {len(df)} 筆")

            # 欄位對應（繁體中文 → 英文）
            df = df.rename(columns={
                '證券代號': 'stock_id',
                '證券名稱': 'stock_name',
                '開盤價': 'open',
                '最高價': 'high',
                '最低價': 'low',
                '收盤價': 'close',
                '成交股數': 'volume',
                '成交金額': 'amount',
                '成交筆數': 'transaction_count',
                '漲跌價差': 'change_price'
            })

            # 只保留 4 位數股票代碼（排除 ETF、權證等）
            df = df[df['stock_id'].str.len() == 4]
            df = df[df['stock_id'].str.isdigit()]

            # 如果有指定股票清單，進行篩選
            if stock_ids:
                df = df[df['stock_id'].isin(stock_ids)]

            # 加入日期
            df['date'] = date

            # 資料清理：移除逗號並轉換為數值
            numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount', 'transaction_count', 'change_price']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.replace(',', '').str.replace('--', '0').str.replace('X', '0')
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # 加入市場類型
            df['type'] = 'twse'

            # 只保留需要的欄位
            keep_cols = ['date', 'stock_id', 'stock_name', 'open', 'high', 'low', 'close',
                        'volume', 'amount', 'transaction_count', 'change_price', 'type']
            df = df[[col for col in keep_cols if col in df.columns]]

            logger.info(f"TWSE 回補模式完成: {len(df)} 筆 ({date})")
            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"TWSE MI_INDEX API 請求錯誤: {e}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"TWSE MI_INDEX API 處理錯誤: {e}", exc_info=True)
            return pd.DataFrame()

    def is_available(self, date: str) -> bool:
        """檢查資料是否可用"""
        df = self.get_daily_prices(date)
        return not df.empty
