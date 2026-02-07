"""
Revenue Data Importer - 月營收資料匯入器
"""

import logging
from datetime import date
from decimal import Decimal
from typing import Dict, Any, List

from ..db.models import StockRevenue
from .base_importer import BaseImporter


logger = logging.getLogger(__name__)


class RevenueImporter(BaseImporter):
    """月營收資料匯入器"""

    def __init__(self, session):
        super().__init__(session, data_type="revenue")

    def get_model_class(self):
        return StockRevenue

    def get_unique_keys(self) -> List[str]:
        return ['year_month', 'stock_id']

    def transform_record(self, record: Dict[str, Any], import_date: date) -> Dict[str, Any]:
        """
        轉換月營收資料記錄

        JSON 格式:
        {
            "year_month": "2026-01",
            "stock_id": "2330",
            "stock_name": "台積電",
            "current_month_revenue": 123456.78,
            "last_month_revenue": 120000.00,
            "last_year_revenue": 110000.00,
            "mom_change_pct": 2.88,
            "yoy_change_pct": 12.23,
            "ytd_revenue": 123456.78,
            "ytd_last_year_revenue": 110000.00,
            "ytd_yoy_change_pct": 12.23,
            "note": "營收成長說明",
            "data_source": "daily",
            "collection_date": "2026-02-06",
            "type": "twse"
        }
        """
        return {
            'year_month': record['year_month'],
            'stock_id': record['stock_id'],
            # 營收資料（千元）
            'current_month_revenue': self._to_decimal(record.get('current_month_revenue')),
            'last_month_revenue': self._to_decimal(record.get('last_month_revenue')),
            'last_year_revenue': self._to_decimal(record.get('last_year_revenue')),
            # 成長率（%）
            'mom_change_pct': self._to_decimal(record.get('mom_change_pct')),
            'yoy_change_pct': self._to_decimal(record.get('yoy_change_pct')),
            # 累計資料（千元）
            'ytd_revenue': self._to_decimal(record.get('ytd_revenue')),
            'ytd_last_year_revenue': self._to_decimal(record.get('ytd_last_year_revenue')),
            'ytd_yoy_change_pct': self._to_decimal(record.get('ytd_yoy_change_pct')),
            # 其他欄位
            'note': record.get('note'),
            'data_source': record.get('data_source'),
            'collection_date': self._to_date(record.get('collection_date')),
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
    def _to_date(value) -> date | None:
        """轉換為 date"""
        if value is None or value == '':
            return None
        try:
            if isinstance(value, str):
                return date.fromisoformat(value)
            elif isinstance(value, date):
                return value
            else:
                return None
        except (ValueError, TypeError):
            return None
