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
            date: 日期（YYYY-MM-DD格式）
            stock_ids: 股票代碼列表（None 表示全部）

        Returns:
            包含融資融券資料的 DataFrame
        """
        # 轉換日期格式：YYYY-MM-DD -> YYYYMMDD
        date_str = date.replace('-', '')
        url = f"https://www.twse.com.tw/rwd/zh/marginTrading/MI_MARGN?date={date_str}&selectType=STOCK&response=json"

        try:
            # 注意：TWSE API 有 SSL 憑證問題，暫時停用驗證
            response = self.session.get(url, timeout=self.timeout, verify=False)
            response.raise_for_status()

            result = response.json()

            # 檢查狀態
            if result.get('stat') != 'OK':
                return pd.DataFrame()

            # 從 tables[1] 取得個股融資融券資料
            tables = result.get('tables', [])
            if len(tables) < 2:
                return pd.DataFrame()

            table_data = tables[1].get('data', [])
            if not table_data:
                return pd.DataFrame()

            # 轉換為 DataFrame
            # 欄位: [代號, 名稱, 融資買進, 融資賣出, 現金償還, 融資前日餘額, 融資今日餘額, 融資限額,
            #       融券買進, 融券賣出, 現券償還, 融券前日餘額, 融券今日餘額, 融券限額, 資券互抵, 註記]
            df = pd.DataFrame(table_data, columns=[
                'stock_id', 'stock_name', 'margin_buy', 'margin_sell', 'margin_cash_repay',
                'margin_balance_prev', 'margin_balance', 'margin_quota',
                'short_covering', 'short_sell', 'short_repay',
                'short_balance_prev', 'short_balance', 'short_quota',
                'offset', 'note'
            ])

            # 移除合計列（代號為空白）
            df = df[df['stock_id'].str.strip() != '']

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
                    # 移除逗號、空白，空字串轉為 NaN
                    df[col] = df[col].astype(str).str.replace(',', '').str.strip()
                    df[col] = df[col].replace(['', ' ', '--'], None)
                    # 轉為數值
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # 計算 margin_change 和 short_change
            if 'margin_balance' in df.columns and 'margin_balance_prev' in df.columns:
                df['margin_change'] = df['margin_balance'] - df['margin_balance_prev']

            if 'short_balance' in df.columns and 'short_balance_prev' in df.columns:
                df['short_change'] = df['short_balance'] - df['short_balance_prev']

            # 只保留必要欄位
            keep_cols = [
                'date', 'stock_id', 'stock_name', 'type',
                'margin_buy', 'margin_sell', 'margin_cash_repay',
                'margin_balance_prev', 'margin_balance', 'margin_quota', 'margin_change',
                'short_covering', 'short_sell', 'short_repay',
                'short_balance_prev', 'short_balance', 'short_quota', 'short_change',
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
