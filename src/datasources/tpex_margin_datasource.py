"""
TPEx 融資融券資料源

提供證券櫃買中心融資融券資料的存取功能
"""

from typing import Optional, List
import pandas as pd
import requests
from urllib3.exceptions import InsecureRequestWarning
import urllib3

# 停用 SSL 警告
urllib3.disable_warnings(InsecureRequestWarning)


class TPExMarginDataSource:
    """TPEx 融資融券資料源"""

    BASE_URL = "https://www.tpex.org.tw/web/stock/margin_trading/margin_balance"

    # 欄位對照表（根據實際 API 回傳）
    COLUMN_MAPPING = {
        '代號': 'stock_id',
        '名稱': 'stock_name',
        '前資餘額(張)': 'margin_balance_prev',
        '資買': 'margin_buy',
        '資賣': 'margin_sell',
        '資現償': 'margin_cash_repay',
        '今資餘額': 'margin_balance',
        '資限額': 'margin_quota',
        '前券餘額(張)': 'short_balance_prev',
        '券買': 'short_covering',
        '券賣': 'short_sell',
        '券償': 'short_repay',
        '今券餘額': 'short_balance',
        '券限額': 'short_quota',
        '資券相抵(張)': 'offset',
        '註記': 'note'
    }

    def __init__(self, timeout: int = 30):
        """
        初始化 TPEx 融資融券資料源

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
        # TPEx API 使用 result.php 端點
        url = f"{self.BASE_URL}/margin_bal_result.php"

        try:
            response = self.session.get(url, timeout=self.timeout, verify=False)
            response.raise_for_status()

            data = response.json()

            if data.get('stat') != 'ok' or 'tables' not in data or len(data['tables']) == 0:
                return pd.DataFrame()

            # 取得第一個 table 的資料
            table = data['tables'][0]
            fields = table.get('fields', [])
            rows = table.get('data', [])

            if not rows:
                return pd.DataFrame()

            # 建立 DataFrame
            df = pd.DataFrame(rows, columns=fields)

            # 欄位重新命名
            df = df.rename(columns=self.COLUMN_MAPPING)

            # 只保留有對應的欄位
            available_cols = [col for col in self.COLUMN_MAPPING.values() if col in df.columns]
            df = df[available_cols]

            # 只保留 4 位數字的股票代碼
            if 'stock_id' in df.columns:
                df = df[df['stock_id'].str.len() == 4]
                df = df[df['stock_id'].str.isdigit()]

            # 加入日期欄位
            df['date'] = date

            # 加入類型標記
            df['type'] = 'tpex'

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
                    # 移除逗號並轉為數值
                    df[col] = df[col].astype(str).str.replace(',', '').replace(['', ' ', '--', 'N/A'], None)
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
            raise Exception(f"TPEx 融資融券 API 請求失敗: {e}")
        except Exception as e:
            raise Exception(f"TPEx 融資融券資料處理失敗: {e}")

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
