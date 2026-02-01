"""
台灣證券交易所 (TWSE) 資料源

使用 TWSE OpenAPI 取得上市股票資料
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


class TWSEDataSource(BaseDataSource):
    """TWSE 官方 API 資料源"""

    BASE_URL = "https://openapi.twse.com.tw/v1"

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
        # 添加 headers 避免被封鎖
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def get_daily_prices(
        self,
        date: str,
        stock_ids: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        取得 TWSE 每日價量資料

        API: /rwd/zh/afterTrading/MI_INDEX (舊版 API，支援歷史查詢)
        回傳指定日期所有上市股票成交資訊
        """
        # 轉換日期格式：YYYY-MM-DD -> YYYYMMDD
        date_str = date.replace('-', '')
        url = f"https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?date={date_str}&type=ALL&response=json"

        try:
            logger.info(f"查詢 TWSE API: {url}")
            response = self.session.get(url, timeout=self.timeout, verify=False)
            response.raise_for_status()
            result = response.json()

            # 檢查狀態
            if result.get('stat') != 'OK':
                logger.warning(f"TWSE 無資料: {date} (stat={result.get('stat')})")
                return pd.DataFrame()

            # 從 tables[8] 取得每日收盤行情資料
            tables = result.get('tables', [])
            if len(tables) < 9:
                logger.warning(f"TWSE 資料格式錯誤: {date}")
                return pd.DataFrame()

            table_data = tables[8].get('data', [])
            if not table_data:
                logger.warning(f"TWSE 無資料: {date}")
                return pd.DataFrame()

            logger.info(f"TWSE 原始資料: {len(table_data)} 筆")

            # 轉換為 DataFrame
            # 欄位: [證券代號, 證券名稱, 成交股數, 成交筆數, 成交金額, 開盤價, 最高價, 最低價, 收盤價, 漲跌(+/-), 漲跌價差, ...]
            df = pd.DataFrame(table_data, columns=[
                'stock_id', 'stock_name', 'volume', 'transaction_count', 'amount',
                'open', 'high', 'low', 'close', 'change_direction', 'change_price',
                'last_buy_price', 'last_buy_volume', 'last_sell_price', 'last_sell_volume', 'pe_ratio'
            ])

            # 只保留 4 位數股票代碼（排除 ETF、權證等）
            df = df[df['stock_id'].str.len() == 4]
            df = df[df['stock_id'].str.isdigit()]

            # 加入日期
            df['date'] = date

            # 資料清理：移除逗號、HTML 標籤並轉換為數值
            numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount', 'transaction_count', 'change_price']
            for col in numeric_cols:
                if col in df.columns:
                    # 移除逗號、HTML 標籤、處理特殊符號
                    df[col] = df[col].astype(str).str.replace(',', '').str.replace('--', '0').str.replace('X', '0')
                    # 移除 HTML 標籤（如 <p style= color:green>-</p>）
                    df[col] = df[col].str.replace(r'<[^>]+>', '', regex=True)
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # 篩選股票
            if stock_ids:
                df = df[df['stock_id'].isin(stock_ids)]

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

    def is_available(self, date: str) -> bool:
        """檢查資料是否可用"""
        df = self.get_daily_prices(date)
        return not df.empty
