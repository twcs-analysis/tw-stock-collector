"""
TPEx 月營收資料源

提供櫃買中心月營收資料的存取功能
"""

from typing import Optional, List
import pandas as pd
import requests


class TPExRevenueDataSource:
    """TPEx 月營收資料源"""

    BASE_URL = "https://www.tpex.org.tw/openapi/v1"

    # 欄位對照表（與 TWSE 相同）
    COLUMN_MAPPING = {
        '出表日期': 'report_date',
        '資料年月': 'year_month',
        '公司代號': 'stock_id',
        '公司名稱': 'stock_name',
        '產業別': 'industry',
        '營業收入-當月營收': 'current_month_revenue',
        '營業收入-上月營收': 'last_month_revenue',
        '營業收入-去年當月營收': 'last_year_revenue',
        '營業收入-上月比較增減(%)': 'mom_change_pct',
        '營業收入-去年同月增減(%)': 'yoy_change_pct',
        '累計營業收入-當月累計營收': 'ytd_revenue',
        '累計營業收入-去年累計營收': 'ytd_last_year_revenue',
        '累計營業收入-前期比較增減(%)': 'ytd_yoy_change_pct',
        '備註': 'note'
    }

    def __init__(self, timeout: int = 30):
        """
        初始化 TPEx 月營收資料源

        Args:
            timeout: API 請求逾時時間（秒）
        """
        self.timeout = timeout
        self.session = requests.Session()

    def _convert_roc_date(self, roc_date: str) -> str:
        """
        轉換民國日期為西元日期

        Args:
            roc_date: 民國日期（例如：1150117 表示 115/01/17）

        Returns:
            西元日期（YYYY-MM-DD）
        """
        if not roc_date or len(roc_date) < 5:
            return None

        try:
            year = int(roc_date[:3]) + 1911
            month = roc_date[3:5]
            day = roc_date[5:7] if len(roc_date) >= 7 else "01"
            return f"{year}-{month}-{day}"
        except:
            return None

    def _convert_roc_yearmonth(self, roc_yearmonth: str) -> str:
        """
        轉換民國年月為西元年月

        Args:
            roc_yearmonth: 民國年月（例如：11412 表示 114/12）

        Returns:
            西元年月（YYYY-MM）
        """
        if not roc_yearmonth or len(roc_yearmonth) < 4:
            return None

        try:
            year = int(roc_yearmonth[:3]) + 1911
            month = roc_yearmonth[3:5]
            return f"{year}-{month}"
        except:
            return None

    def get_revenue_data(
        self,
        year_month: Optional[str] = None,
        stock_ids: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        取得月營收資料

        Args:
            year_month: 年月（YYYY-MM格式，會被忽略因 API 只提供最新資料）
            stock_ids: 股票代碼列表（None 表示全部）

        Returns:
            包含月營收資料的 DataFrame
        """
        url = f"{self.BASE_URL}/mopsfin_t187ap05_O"

        try:
            response = self.session.get(url, timeout=self.timeout)
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

            # 轉換日期格式
            if 'report_date' in df.columns:
                df['report_date'] = df['report_date'].apply(self._convert_roc_date)

            if 'year_month' in df.columns:
                df['year_month'] = df['year_month'].apply(self._convert_roc_yearmonth)

            # 加入類型標記
            df['type'] = 'tpex'

            # 過濾特定股票（如果有指定）
            if stock_ids:
                df = df[df['stock_id'].isin(stock_ids)]

            # 數值欄位轉換
            numeric_cols = [
                'current_month_revenue', 'last_month_revenue', 'last_year_revenue',
                'mom_change_pct', 'yoy_change_pct',
                'ytd_revenue', 'ytd_last_year_revenue', 'ytd_yoy_change_pct'
            ]

            for col in numeric_cols:
                if col in df.columns:
                    # 空字串轉為 NaN
                    df[col] = df[col].replace(['', ' ', '--', '-'], None)
                    # 轉為數值
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # 只保留必要欄位
            keep_cols = [
                'report_date', 'year_month', 'stock_id', 'stock_name', 'industry', 'type',
                'current_month_revenue', 'last_month_revenue', 'last_year_revenue',
                'mom_change_pct', 'yoy_change_pct',
                'ytd_revenue', 'ytd_last_year_revenue', 'ytd_yoy_change_pct',
                'note'
            ]

            df = df[[col for col in keep_cols if col in df.columns]]

            return df

        except requests.exceptions.RequestException as e:
            raise Exception(f"TPEx 月營收 API 請求失敗: {e}")
        except Exception as e:
            raise Exception(f"TPEx 月營收資料處理失敗: {e}")

    def is_available(self, year_month: Optional[str] = None) -> bool:
        """
        檢查資料是否可用

        Args:
            year_month: 年月（YYYY-MM格式）

        Returns:
            是否可用
        """
        try:
            df = self.get_revenue_data(year_month)
            return not df.empty
        except:
            return False
