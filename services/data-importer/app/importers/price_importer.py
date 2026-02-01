"""
Price Data Importer - 每日價格資料匯入器
"""

import logging
from datetime import date
from decimal import Decimal
from typing import Dict, Any, List

from ..db.models import StockPriceDaily
from .base_importer import BaseImporter


logger = logging.getLogger(__name__)


class PriceImporter(BaseImporter):
    """每日價格資料匯入器"""

    def __init__(self, session):
        super().__init__(session, data_type="price")

    def get_model_class(self):
        return StockPriceDaily

    def get_unique_keys(self) -> List[str]:
        return ['trade_date', 'stock_id']

    def transform_record(self, record: Dict[str, Any], import_date: date) -> Dict[str, Any]:
        """
        轉換價格資料記錄

        JSON 格式:
        {
            "date": "2024-12-27",
            "stock_id": "2330",
            "stock_name": "台積電",
            "open": 1080.0,
            "high": 1095.0,
            "low": 1075.0,
            "close": 1090.0,
            "volume": 45678912,
            "amount": 49000000000.0,
            "transaction": 12345,
            "change": 10.0,
            "change_pct": 0.92,
            "type": "twse"
        }

        Database 欄位 (對應 SQL schema):
        - trade_date, stock_id
        - open_price, high_price, low_price, close_price
        - volume, amount
        """
        return {
            'trade_date': import_date,
            'stock_id': record['stock_id'],
            'open_price': self._to_decimal(record.get('open')),
            'high_price': self._to_decimal(record.get('high')),
            'low_price': self._to_decimal(record.get('low')),
            'close_price': self._to_decimal(record.get('close')),
            'volume': self._to_int(record.get('volume')),
            'amount': self._to_decimal(record.get('amount')),
        }

    @staticmethod
    def _to_decimal(value) -> Decimal | None:
        """轉換為 Decimal"""
        if value is None or value == '':
            return None
        try:
            return Decimal(str(value))
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _to_int(value) -> int | None:
        """轉換為整數"""
        if value is None or value == '':
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
