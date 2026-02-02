"""
證券櫃買中心 (TPEx) 資料源 - 雙模式架構

策略：
1. 即時模式：使用 TPEx OpenAPI（當日最新資料，快速）
   - API: https://www.tpex.org.tw/openapi/v1/tpex_mainboard_quotes
   - 速度：~2-3 秒
   - 用途：每日自動收集

2. 回補模式：使用傳統 API（歷史資料，快速）
   - API: https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php
   - 速度：~2-3 秒
   - 用途：歷史資料回補
"""
import requests
import pandas as pd
from typing import Optional, List
import logging
import urllib3

from .base_datasource import BaseDataSource

# 關閉 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class TPExDataSource(BaseDataSource):
    """TPEx 官方 API 資料源"""

    BASE_URL = "https://www.tpex.org.tw/openapi/v1"
    BASE_URL_LEGACY = "https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes"

    def __init__(self, timeout: int = 30, use_backfill_mode: bool = False):
        """
        Args:
            timeout: API 請求超時時間
            use_backfill_mode: 是否使用回補模式（可取得歷史資料）
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
        取得 TPEx 每日價量資料

        Args:
            date: 查詢日期 (YYYY-MM-DD)
            stock_ids: 股票代碼列表（選用）

        Returns:
            pd.DataFrame: 價格資料，若無資料或非交易日則返回空 DataFrame
        """
        if self.use_backfill_mode:
            return self._get_daily_prices_backfill(date, stock_ids)
        else:
            return self._get_daily_prices_realtime(date, stock_ids)

    def _get_daily_prices_realtime(
        self,
        date: str,
        stock_ids: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        即時模式：使用 OpenAPI 取得當日所有股票資料

        注意：此 API 只能取得最新交易日資料，無法指定歷史日期
        """
        url = f"{self.BASE_URL}/tpex_mainboard_quotes"

        try:
            logger.info(f"查詢 TPEx API: {url}")
            response = self.session.get(url, timeout=self.timeout, verify=False)
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

    def _get_daily_prices_backfill(
        self,
        date: str,
        stock_ids: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        回補模式：使用傳統 API 取得歷史資料

        此方法使用舊版 API，可取得歷史日期的資料

        Args:
            date: 查詢日期 (YYYY-MM-DD)
            stock_ids: 股票代碼列表（選用，用於篩選特定股票）
        """
        from datetime import datetime

        # 將日期轉換為民國年格式 (YYY/MM/DD)
        dt = datetime.strptime(date, '%Y-%m-%d')
        roc_year = dt.year - 1911
        date_str = f"{roc_year}/{dt.month:02d}/{dt.day:02d}"

        url = f"{self.BASE_URL_LEGACY}/stk_quote_result.php"
        params = {
            'l': 'zh-tw',
            'd': date_str,
            '_': str(int(datetime.now().timestamp() * 1000))
        }

        try:
            logger.info(f"查詢 TPEx Legacy API (回補模式): {url}?d={date_str}")
            response = self.session.get(url, params=params, timeout=self.timeout, verify=False)
            response.raise_for_status()
            data = response.json()

            # 檢查 API 狀態
            if not data or 'tables' not in data or len(data['tables']) == 0:
                logger.warning(f"TPEx Legacy API 無資料: {date}")
                return pd.DataFrame()

            # 取得第一個表格的資料
            table = data['tables'][0]
            columns = table.get('fields', [])
            rows = table.get('data', [])

            if not rows:
                logger.warning(f"TPEx Legacy API 無資料: {date}")
                return pd.DataFrame()

            # 轉換為 DataFrame
            df = pd.DataFrame(rows, columns=columns)
            logger.info(f"TPEx Legacy API 原始資料: {len(df)} 筆")

            # 欄位對應（繁體中文 → 英文）
            df = df.rename(columns={
                '代號': 'stock_id',
                '名稱': 'stock_name',
                '開盤': 'open',
                '最高': 'high',
                '最低': 'low',
                '收盤': 'close',
                '成交股數': 'volume',
                '成交金額(元)': 'amount',
                '成交筆數': 'transaction_count'
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
            numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount', 'transaction_count']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.replace(',', '').str.replace('---', '0').str.replace('--', '0')
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # 加入市場類型
            df['type'] = 'tpex'

            # 只保留需要的欄位
            keep_cols = ['date', 'stock_id', 'stock_name', 'open', 'high', 'low', 'close',
                        'volume', 'amount', 'transaction_count', 'type']
            df = df[[col for col in keep_cols if col in df.columns]]

            logger.info(f"TPEx 回補模式完成: {len(df)} 筆 ({date})")
            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"TPEx Legacy API 請求錯誤: {e}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"TPEx Legacy API 處理錯誤: {e}", exc_info=True)
            return pd.DataFrame()

    def is_available(self, date: str) -> bool:
        """檢查資料是否可用"""
        df = self.get_daily_prices(date)
        return not df.empty
