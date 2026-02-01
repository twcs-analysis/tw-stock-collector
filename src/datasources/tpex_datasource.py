"""
證券櫃買中心 (TPEx) 資料源

使用 TPEx OpenAPI 取得上櫃股票資料
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

        API: /web/stock/aftertrading/otc_quotes_no1430/stk_wn1430_result.php (舊版 API，支援歷史查詢)
        回傳指定日期上櫃股票行情
        """
        # 轉換日期格式：YYYY-MM-DD -> YYY/MM/DD (民國年)
        from datetime import datetime
        dt = datetime.strptime(date, '%Y-%m-%d')
        roc_year = dt.year - 1911  # 轉換為民國年
        date_str = f"{roc_year}/{dt.month:02d}/{dt.day:02d}"

        import time
        timestamp = int(time.time() * 1000)
        url = f"https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430_result.php?l=zh-tw&d={date_str}&se=AL&_={timestamp}"

        try:
            logger.info(f"查詢 TPEx API: {url}")
            response = self.session.get(url, timeout=self.timeout, verify=False)
            response.raise_for_status()
            result = response.json()

            # 檢查狀態（TPEx 返回小寫 "ok"）
            if result.get('stat') not in ['OK', 'ok']:
                logger.warning(f"TPEx 無資料: {date} (stat={result.get('stat')})")
                return pd.DataFrame()

            # 從 tables[0] 取得資料
            tables = result.get('tables', [])
            if not tables:
                logger.warning(f"TPEx 資料格式錯誤: {date}")
                return pd.DataFrame()

            table_data = tables[0].get('data', [])
            if not table_data:
                logger.warning(f"TPEx 無資料: {date}")
                return pd.DataFrame()

            logger.info(f"TPEx 原始資料: {len(table_data)} 筆")

            # 轉換為 DataFrame
            # 欄位: [代號, 名稱, 收盤, 漲跌, 開盤, 最高, 最低, 成交股數, 成交金額(元), 成交筆數, ...]
            df = pd.DataFrame(table_data)
            df.columns = ['stock_id', 'stock_name', 'close', 'change_price', 'open', 'high', 'low',
                         'volume', 'amount', 'transaction_count', 'last_buy_price', 'last_buy_volume',
                         'last_sell_price', 'last_sell_volume', 'issued_shares', 'next_ref_price', 'next_limit_up']

            # 只保留 4 位數股票代碼
            df = df[df['stock_id'].str.len() == 4]
            df = df[df['stock_id'].str.isdigit()]

            # 加入日期
            df['date'] = date

            # 資料清理：移除逗號、空白並轉換為數值
            numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount', 'transaction_count', 'change_price']
            for col in numeric_cols:
                if col in df.columns:
                    # 移除逗號、空白
                    df[col] = df[col].astype(str).str.replace(',', '').str.strip()
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # 篩選股票
            if stock_ids:
                df = df[df['stock_id'].isin(stock_ids)]

            # 加入市場類型
            df['type'] = 'tpex'

            # 只保留需要的欄位
            keep_cols = ['date', 'stock_id', 'stock_name', 'open', 'high', 'low', 'close',
                        'volume', 'amount', 'transaction_count', 'change_price', 'type']
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
