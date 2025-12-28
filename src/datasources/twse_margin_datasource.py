"""
TWSE 融資融券資料源

提供台灣證券交易所融資融券資料的存取功能
"""

from typing import Optional, List
import pandas as pd
import requests
from urllib3.exceptions import InsecureRequestWarning
import urllib3

# 停用 SSL 警告（TWSE API SSL 憑證問題）
urllib3.disable_warnings(InsecureRequestWarning)


class TWSEMarginDataSource:
    """TWSE 融資融券資料源"""

    BASE_URL = "https://openapi.twse.com.tw/v1"

    # 欄位對照表
    COLUMN_MAPPING = {
        '股票代號': 'stock_id',
        '股票名稱': 'stock_name',
        '融資買進': 'margin_buy',
        '融資賣出': 'margin_sell',
        '融資現金償還': 'margin_cash_repay',
        '融資前日餘額': 'margin_balance_prev',
        '融資今日餘額': 'margin_balance',
        '融資限額': 'margin_quota',
        '融券買進': 'short_covering',
        '融券賣出': 'short_sell',
        '融券現券償還': 'short_repay',
        '融券前日餘額': 'short_balance_prev',
        '融券今日餘額': 'short_balance',
        '融券限額': 'short_quota',
        '資券互抵': 'offset',
        '註記': 'note'
    }

    def __init__(self, timeout: int = 30):
        """
        初始化 TWSE 融資融券資料源

        Args:
            timeout: API 請求逾時時間（秒）
        """
        self.timeout = timeout
        self.session = requests.Session()

    def get_margin_data(
        self,
        date: str,
        stock_ids: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        取得融資融券資料

        Args:
            date: 日期（YYYY-MM-DD格式，會被忽略因 API 只提供最新資料）
            stock_ids: 股票代碼列表（None 表示全部）

        Returns:
            包含融資融券資料的 DataFrame
        """
        url = f"{self.BASE_URL}/exchangeReport/MI_MARGN"

        try:
            # 注意：TWSE API 有 SSL 憑證問題，暫時停用驗證
            response = self.session.get(url, timeout=self.timeout, verify=False)
            response.raise_for_status()

            data = response.json()

            if not data:
                return pd.DataFrame()

            # 轉換為 DataFrame
            df = pd.DataFrame(data)

            # 欄位重新命名
            df = df.rename(columns=self.COLUMN_MAPPING)

            # 只保留 4 位數字的股票代碼
            if 'stock_id' in df.columns:
                df = df[df['stock_id'].str.len() == 4]
                df = df[df['stock_id'].str.isdigit()]

            # 加入日期欄位
            df['date'] = date

            # 加入類型標記
            df['type'] = 'twse'

            # 過濾特定股票（如果有指定）
            if stock_ids:
                df = df[df['stock_id'].isin(stock_ids)]

            # 數值欄位轉換
            numeric_cols = [
                'margin_buy', 'margin_sell', 'margin_cash_repay',
                'margin_balance_prev', 'margin_balance', 'margin_quota',
                'short_covering', 'short_sell', 'short_repay',
                'short_balance_prev', 'short_balance', 'short_quota',
                'offset'
            ]

            for col in numeric_cols:
                if col in df.columns:
                    # 空字串轉為 NaN
                    df[col] = df[col].replace(['', ' ', '--'], None)
                    # 轉為數值
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # 只保留必要欄位
            keep_cols = [
                'date', 'stock_id', 'stock_name', 'type',
                'margin_buy', 'margin_sell', 'margin_cash_repay',
                'margin_balance_prev', 'margin_balance', 'margin_quota',
                'short_covering', 'short_sell', 'short_repay',
                'short_balance_prev', 'short_balance', 'short_quota',
                'offset'
            ]

            df = df[[col for col in keep_cols if col in df.columns]]

            return df

        except requests.exceptions.RequestException as e:
            raise Exception(f"TWSE 融資融券 API 請求失敗: {e}")
        except Exception as e:
            raise Exception(f"TWSE 融資融券資料處理失敗: {e}")

    def is_available(self, date: str) -> bool:
        """
        檢查該日期資料是否可用

        Args:
            date: 日期（YYYY-MM-DD格式）

        Returns:
            是否可用
        """
        try:
            df = self.get_margin_data(date)
            return not df.empty
        except:
            return False
