"""
成交量前 20 名資料收集器
"""

from datetime import datetime
from typing import Dict, Any
import requests

from .base import BaseCollector


class Top20VolumeCollector(BaseCollector):
    """
    成交量前 20 名資料收集器

    使用 TWSE OpenAPI 收集每日成交量前 20 名股票資料
    API: https://openapi.twse.com.tw/v1/exchangeReport/MI_INDEX20
    """

    def __init__(self, date: str):
        """
        初始化成交量前 20 名收集器

        Args:
            date: 收集日期 (YYYY-MM-DD)
        """
        super().__init__(date)

    def get_data_type(self) -> str:
        """取得資料類型"""
        return "top20_volume"

    def collect(self) -> Dict[str, Any]:
        """
        收集成交量前 20 名資料

        Returns:
            dict: 包含 metadata 和 data 的字典
        """
        self.logger.info(f"開始收集 top20_volume 資料: {self.date}")

        try:
            # 轉換日期格式：YYYY-MM-DD -> YYYYMMDD
            date_str = self.date.replace('-', '')
            # 使用舊版 TWSE API（支援歷史查詢）
            url = f"https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX20?date={date_str}&response=json"

            self.logger.info(f"查詢 TWSE API: {url}")
            response = requests.get(url, timeout=30, verify=False)
            response.raise_for_status()
            result = response.json()

            # 檢查狀態
            if result.get('stat') != 'OK':
                self.logger.warning(f"TWSE 無資料: {self.date} (stat={result.get('stat')})")
                return {}

            # 從 data 欄位取得資料
            data = result.get('data', [])
            if not data:
                self.logger.warning(f"TWSE 無資料: {self.date}")
                return {}

            # 處理資料
            # 資料格式: [排名, 代號, 名稱, 成交股數, 成交筆數, 開盤價, 最高價, 最低價, 收盤價, 漲跌方向, 漲跌價差, ...]
            processed_data = []
            for item in data:
                if len(item) < 11:
                    continue
                record = {
                    'rank': item[0],
                    'date': self.date,
                    'stock_id': str(item[1]),
                    'stock_name': str(item[2]).strip(),
                    'volume': self._parse_number(item[3]),
                    'transaction_count': self._parse_number(item[4]),
                    'open': self._parse_number(item[5]),
                    'high': self._parse_number(item[6]),
                    'low': self._parse_number(item[7]),
                    'close': self._parse_number(item[8]),
                    # item[9] 是漲跌方向 HTML 標籤，跳過
                    'change': self._parse_number(item[10]),
                    'amount': 0.0,  # 舊版 API 沒有成交金額
                    'type': 'twse'
                }
                processed_data.append(record)

            # 建立回傳結果
            result = {
                "metadata": {
                    "date": self.date,
                    "collected_at": datetime.now().isoformat(),
                    "total_count": len(processed_data),
                    "source": "TWSE OpenAPI MI_INDEX20"
                },
                "data": processed_data
            }

            self.logger.info(f"收集完成: 總計 {len(processed_data)} 檔")
            return result

        except requests.exceptions.RequestException as e:
            self.logger.error(f"TWSE API 請求錯誤: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"收集失敗: {e}", exc_info=True)
            return {}

    def _parse_number(self, value) -> float:
        """
        解析數值（移除逗號、處理特殊符號）

        Args:
            value: 原始數值

        Returns:
            float: 解析後的數值
        """
        if value is None:
            return 0.0

        # 轉換為字串並清理
        str_value = str(value).replace(',', '').replace('--', '0').replace('X', '0').strip()

        try:
            return float(str_value) if str_value else 0.0
        except ValueError:
            return 0.0
