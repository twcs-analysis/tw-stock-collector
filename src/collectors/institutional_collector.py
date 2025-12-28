"""
三大法人資料收集器
"""

from datetime import datetime
from typing import Dict, Any

from .base import BaseCollector


class InstitutionalCollector(BaseCollector):
    """
    三大法人資料收集器

    使用官方 API 收集 TWSE 和 TPEx 三大法人資料
    使用 collect_institutional_data.py 的邏輯
    """

    def __init__(self, date: str):
        """
        初始化三大法人收集器

        Args:
            date: 收集日期 (YYYY-MM-DD)
        """
        super().__init__(date)

    def get_data_type(self) -> str:
        """取得資料類型"""
        return "institutional"

    def collect(self) -> Dict[str, Any]:
        """
        收集三大法人資料

        Returns:
            dict: 包含 metadata 和 data 的字典
        """
        import requests
        import pandas as pd
        from io import StringIO
        from ..utils import to_roc_date

        all_data = []
        total_count = 0

        # 收集 TWSE 資料
        self.logger.info("收集 TWSE（上市）三大法人資料")
        try:
            twse_date = self.date.replace('-', '')
            url = f"https://www.twse.com.tw/fund/T86?response=csv&date={twse_date}&selectType=ALLBUT0999"

            response = requests.get(url, timeout=30, verify=False)
            response.encoding = 'cp950'  # Big5

            lines = response.text.split('\n')
            start_idx = None
            for i, line in enumerate(lines):
                if '證券代號' in line:
                    start_idx = i
                    break

            if start_idx is not None:
                data_content = '\n'.join(lines[start_idx:])
                df = pd.read_csv(StringIO(data_content))

                # 只保留 4 位數字的股票代碼
                df = df[df['證券代號'].astype(str).str.len() == 4]
                df = df[df['證券代號'].astype(str).str.isdigit()]

                df['date'] = self.date
                df['type'] = 'twse'

                twse_count = len(df)
                self.logger.info(f"TWSE: {twse_count} 檔")
                all_data.extend(df.to_dict('records'))
                total_count += twse_count

        except Exception as e:
            self.logger.error(f"TWSE 收集失敗: {e}")

        # 收集 TPEx 資料
        self.logger.info("收集 TPEx（上櫃）三大法人資料")
        try:
            roc_date = to_roc_date(self.date)
            url = f"https://www.tpex.org.tw/web/stock/3insti/daily_trade/3itrade_hedge_result.php?d={roc_date}&l=zh-tw&o=htm"

            tables = pd.read_html(url)
            if tables and len(tables) > 0:
                df = tables[0]

                # 扁平化 MultiIndex 欄位
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = ['_'.join(map(str, col)).strip() for col in df.columns.values]

                # 只保留 4 位數字的股票代碼（假設第一欄是股票代碼）
                first_col = df.columns[0]
                df = df[df[first_col].astype(str).str.len() == 4]
                df = df[df[first_col].astype(str).str.isdigit()]

                df['date'] = self.date
                df['type'] = 'tpex'

                tpex_count = len(df)
                self.logger.info(f"TPEx: {tpex_count} 檔")
                all_data.extend(df.to_dict('records'))
                total_count += tpex_count

        except Exception as e:
            self.logger.error(f"TPEx 收集失敗: {e}")

        if not all_data:
            self.logger.warning("無資料（可能是非交易日）")
            return {}

        # 建立回傳結果
        result = {
            "metadata": {
                "date": self.date,
                "collected_at": datetime.now().isoformat(),
                "total_count": total_count,
                "source": "TWSE T86 + TPEx Official API"
            },
            "data": all_data
        }

        self.logger.info(f"收集完成: 總計 {total_count} 檔")
        return result
