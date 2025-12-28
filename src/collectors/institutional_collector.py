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

                # 轉換欄位名稱（中文 → 英文）
                column_mapping = {
                    '證券代號': 'stock_id',
                    '證券名稱': 'stock_name',
                    '外陸資買進股數(不含外資自營商)': 'foreign_main_buy',
                    '外陸資賣出股數(不含外資自營商)': 'foreign_main_sell',
                    '外陸資買賣超股數(不含外資自營商)': 'foreign_main_net',
                    '外資自營商買進股數': 'foreign_dealer_buy',
                    '外資自營商賣出股數': 'foreign_dealer_sell',
                    '外資自營商買賣超股數': 'foreign_dealer_net',
                    '投信買進股數': 'trust_buy',
                    '投信賣出股數': 'trust_sell',
                    '投信買賣超股數': 'trust_net',
                    '自營商買賣超股數': 'dealer_net_total',
                    '自營商買進股數(自行買賣)': 'dealer_self_buy',
                    '自營商賣出股數(自行買賣)': 'dealer_self_sell',
                    '自營商買賣超股數(自行買賣)': 'dealer_self_net',
                    '自營商買進股數(避險)': 'dealer_hedge_buy',
                    '自營商賣出股數(避險)': 'dealer_hedge_sell',
                    '自營商買賣超股數(避險)': 'dealer_hedge_net',
                    '三大法人買賣超股數': 'total_net'
                }
                df = df.rename(columns=column_mapping)

                # Trim stock_name 空白
                if 'stock_name' in df.columns:
                    df['stock_name'] = df['stock_name'].str.strip()

                # 轉換所有數值欄位（去除逗號並轉為數值）
                numeric_columns = [
                    'foreign_main_buy', 'foreign_main_sell', 'foreign_main_net',
                    'foreign_dealer_buy', 'foreign_dealer_sell', 'foreign_dealer_net',
                    'trust_buy', 'trust_sell', 'trust_net',
                    'dealer_self_buy', 'dealer_self_sell', 'dealer_self_net',
                    'dealer_hedge_buy', 'dealer_hedge_sell', 'dealer_hedge_net',
                    'dealer_net_total', 'total_net'
                ]
                for col in numeric_columns:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0)

                # 計算外資總買賣超 (外資主力 + 外資自營商)
                if 'foreign_main_net' in df.columns and 'foreign_dealer_net' in df.columns:
                    df['foreign_buy'] = df['foreign_main_buy'] + df['foreign_dealer_buy']
                    df['foreign_sell'] = df['foreign_main_sell'] + df['foreign_dealer_sell']
                    df['foreign_net'] = df['foreign_main_net'] + df['foreign_dealer_net']

                # 自營商買賣超
                if 'dealer_self_net' in df.columns and 'dealer_hedge_net' in df.columns:
                    df['dealer_buy'] = df['dealer_self_buy'] + df['dealer_hedge_buy']
                    df['dealer_sell'] = df['dealer_self_sell'] + df['dealer_hedge_sell']
                    df['dealer_net'] = df['dealer_self_net'] + df['dealer_hedge_net']

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

                # 重新命名第一欄為 stock_id
                df = df.rename(columns={first_col: 'stock_id'})

                # TPEx 資料的欄位結構與 TWSE 不同，需要根據實際情況調整
                # 通常 TPEx HTML table 的欄位也是中文，需要轉換
                # 這裡暫時保留原有欄位名稱，後續可根據實際資料調整

                df['date'] = self.date
                df['type'] = 'tpex'
                df['stock_name'] = ''  # TPEx 資料可能沒有股票名稱，需要補上

                # 如果沒有標準欄位，設定預設值
                required_fields = ['foreign_buy', 'foreign_sell', 'foreign_net',
                                 'trust_buy', 'trust_sell', 'trust_net',
                                 'dealer_buy', 'dealer_sell', 'dealer_net']
                for field in required_fields:
                    if field not in df.columns:
                        df[field] = 0

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
