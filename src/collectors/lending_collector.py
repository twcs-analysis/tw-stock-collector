"""
借券賣出資料收集器
"""

from datetime import datetime
from typing import Dict, Any
import pandas as pd
import urllib3

from .base import BaseCollector

# 關閉 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class LendingCollector(BaseCollector):
    """
    借券賣出資料收集器

    使用 TWSE TWT93U API（包含上市+上櫃所有股票）
    """

    def __init__(self, date: str):
        """
        初始化借券賣出收集器

        Args:
            date: 收集日期 (YYYY-MM-DD)
        """
        super().__init__(date)

    def get_data_type(self) -> str:
        """取得資料類型"""
        return "lending"

    def collect(self) -> Dict[str, Any]:
        """
        收集借券賣出資料

        Returns:
            dict: 包含 metadata 和 data 的字典
        """
        import requests

        self.logger.info("收集借券賣出資料（包含上市+上櫃）")

        # 轉換日期格式為 YYYYMMDD
        twse_date = self.date.replace('-', '')

        url = "https://www.twse.com.tw/exchangeReport/TWT93U"
        params = {
            "response": "json",
            "date": twse_date
        }

        try:
            response = requests.get(url, params=params, timeout=20, verify=False)

            if response.status_code != 200:
                self.logger.error(f"HTTP {response.status_code}")
                return {}

            data = response.json()

            # 檢查是否有資料
            if 'data' not in data or len(data['data']) == 0:
                self.logger.warning("無資料（可能是非交易日）")
                return {}

            # 取得欄位和資料
            fields = data.get('fields', [])
            rows = data.get('data', [])

            # 建立 DataFrame
            df = pd.DataFrame(rows, columns=fields)

            # 加入日期
            df['date'] = self.date

            # 只保留 4 位數字的股票代碼
            if '代號' in df.columns:
                df = df[df['代號'].astype(str).str.len() == 4]
                df = df[df['代號'].astype(str).str.isdigit()]

            total_count = len(df)
            self.logger.info(f"借券賣出: {total_count} 檔（上市+上櫃）")

            # 轉換為 dict
            data_list = df.to_dict(orient='records')

            # 建立回傳結果
            result = {
                "metadata": {
                    "date": self.date,
                    "collected_at": datetime.now().isoformat(),
                    "total_count": total_count,
                    "source": "TWSE TWT93U API (包含上市+上櫃)"
                },
                "data": data_list
            }

            self.logger.info(f"收集完成: 總計 {total_count} 檔")
            return result

        except Exception as e:
            self.logger.error(f"收集失敗: {e}")
            return {}
