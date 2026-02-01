"""
Securities Lending Data Importer - 借券賣出資料匯入器
"""

import logging
from datetime import date
from decimal import Decimal
from typing import Dict, Any, List

from ..db.models import StockLendingDaily
from .base_importer import BaseImporter


logger = logging.getLogger(__name__)


class LendingImporter(BaseImporter):
    """借券賣出資料匯入器"""

    def __init__(self, session):
        super().__init__(session, data_type="lending")

    def get_model_class(self):
        return StockLendingDaily

    def get_unique_keys(self) -> List[str]:
        return ['trade_date', 'stock_id']

    def transform_record(self, record: Dict[str, Any], import_date: date) -> Dict[str, Any]:
        """
        轉換借券賣出資料記錄

        JSON 格式:
        {
            "date": "2024-12-27",
            "stock_id": "2330",
            "stock_name": "台積電",
            "lending_balance": 1000000,
            "lending_balance_amount": 1090000000.0,
            "lending_quota": 5000000,
            "lending_utilization": 20.0,
            "type": "twse"
        }
        """
        return {
            'stock_id': record['stock_id'],
            'trade_date': import_date,
            # 借券資料
            'lending_balance': self._to_int(record.get('lending_balance')),
            'lending_change': self._to_int(record.get('lending_change')),
            'prev_balance': self._to_int(record.get('prev_balance')),
            'daily_sell': self._to_int(record.get('daily_sell')),
            'daily_return': self._to_int(record.get('daily_return')),
            'daily_adjust': self._to_int(record.get('daily_adjust')),
            'next_day_available': self._to_int(record.get('next_day_available')),
        }

    @staticmethod
    def _to_int(value) -> int | None:
        """轉換為整數"""
        if value is None or value == '':
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _to_decimal(value) -> Decimal | None:
        """轉換為 Decimal"""
        if value is None or value == '':
            return None
        try:
            return Decimal(str(value))
        except (ValueError, TypeError):
            return None
