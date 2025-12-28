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

            # 只保留 4 位數字的股票代碼
            if '代號' in df.columns:
                df = df[df['代號'].astype(str).str.len() == 4]
                df = df[df['代號'].astype(str).str.isdigit()]

            # 依據 API 回傳的欄位順序重新命名
            # fields: ["代號","名稱","前日餘額","賣出","買進","現券","今日餘額","次一營業日限額",
            #          "前日餘額","當日賣出","當日還券","當日調整","當日餘額","次一營業日可限額","備註"]
            # 第1組是融券，第2組是借券
            expected_columns = [
                'stock_id', 'stock_name',
                'margin_prev_balance', 'margin_sell', 'margin_buy', 'margin_securities',
                'margin_today_balance', 'margin_next_day_limit',
                'prev_balance', 'daily_sell', 'daily_return', 'daily_adjust',
                'lending_balance', 'next_day_available', 'note'
            ]
            if len(fields) == len(expected_columns):
                df.columns = expected_columns
            else:
                # 如果欄位數量不符，使用原來的 mapping 方式
                column_mapping = {
                    '代號': 'stock_id',
                    '名稱': 'stock_name',
                    '備註': 'note'
                }
                df = df.rename(columns=column_mapping)

            # 加入日期
            df['date'] = self.date

            # Trim stock_name 空白
            if 'stock_name' in df.columns:
                df['stock_name'] = df['stock_name'].str.strip()

            # 轉換數值欄位（去除逗號並轉為數值）
            numeric_columns = ['prev_balance', 'sell', 'buy', 'securities', 'today_balance',
                              'next_day_limit', 'daily_sell', 'daily_return', 'daily_adjust',
                              'lending_balance', 'next_day_available']
            for col in numeric_columns:
                if col in df.columns:
                    # 確保先轉為 str 才能使用 str.replace
                    df[col] = df[col].astype(str).str.replace(',', '')
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            # 計算借券變化量 (當日餘額 - 前日餘額)
            if 'lending_balance' in df.columns and 'prev_balance' in df.columns:
                df['lending_change'] = df['lending_balance'] - df['prev_balance']

            # 加入 type 欄位（借券資料包含上市+上櫃，無法明確區分來源）
            df['type'] = 'twse'  # 預設為 twse，因為 API 來自 TWSE

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
