"""
Margin Trading Data Importer - 融資融券資料匯入器
"""

import logging
from datetime import date
from decimal import Decimal
from typing import Dict, Any, List

from ..db.models import StockMarginDaily
from .base_importer import BaseImporter


logger = logging.getLogger(__name__)


class MarginImporter(BaseImporter):
    """融資融券資料匯入器"""

    def __init__(self, session):
        super().__init__(session, data_type="margin")

    def get_model_class(self):
        return StockMarginDaily

    def get_unique_keys(self) -> List[str]:
        return ['trade_date', 'stock_id']

    def transform_record(self, record: Dict[str, Any], import_date: date) -> Dict[str, Any]:
        """
        轉換融資融券資料記錄

        JSON 格式:
        {
            "date": "2024-12-27",
            "stock_id": "2330",
            "stock_name": "台積電",
            "margin_buy": 100000,
            "margin_sell": 50000,
            "margin_redemption": 20000,
            "margin_balance": 5000000,
            "margin_quota": 10000000,
            "short_sell": 30000,
            "short_cover": 20000,
            "short_redemption": 5000,
            "short_balance": 200000,
            "short_quota": 500000,
            "offset": 1000,
            "margin_utilization": 50.0,
            "short_utilization": 40.0,
            "type": "twse"
        }
        """
        return {
            'stock_id': record['stock_id'],
            'trade_date': import_date,
            # 融資 (Margin Trading) - 單位：千元
            'margin_balance': self._to_decimal(record.get('margin_balance')),
            'margin_change': self._to_decimal(record.get('margin_change')),
            # 融券 (Short Selling) - 單位：股
            'short_balance': self._to_int(record.get('short_balance')),
            'short_change': self._to_int(record.get('short_change')),
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
