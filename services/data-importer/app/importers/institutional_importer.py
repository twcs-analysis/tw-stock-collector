"""
Institutional Data Importer - 三大法人買賣超資料匯入器
"""

import logging
from datetime import date
from decimal import Decimal
from typing import Dict, Any, List

from ..db.models import StockInstitutionalDaily
from .base_importer import BaseImporter


logger = logging.getLogger(__name__)


class InstitutionalImporter(BaseImporter):
    """三大法人買賣超資料匯入器"""

    def __init__(self, session):
        super().__init__(session, data_type="institutional")

    def get_model_class(self):
        return StockInstitutionalDaily

    def get_unique_keys(self) -> List[str]:
        return ['trade_date', 'stock_id']

    def transform_record(self, record: Dict[str, Any], import_date: date) -> Dict[str, Any]:
        """
        轉換三大法人資料記錄

        JSON 格式:
        {
            "date": "2024-12-27",
            "stock_id": "2330",
            "stock_name": "台積電",
            "foreign_buy": 5000000,
            "foreign_sell": 3000000,
            "foreign_net": 2000000,
            "trust_buy": 1000000,
            "trust_sell": 500000,
            "trust_net": 500000,
            "dealer_buy": 200000,
            "dealer_sell": 300000,
            "dealer_net": -100000,
            "total_net": 2400000,
            "type": "twse"
        }
        """
        return {
            'trade_date': import_date,
            'stock_id': record['stock_id'],
            # 外資
            'foreign_buy': self._to_int(record.get('foreign_buy')),
            'foreign_sell': self._to_int(record.get('foreign_sell')),
            'foreign_net': self._to_int(record.get('foreign_net')),
            # 投信
            'trust_buy': self._to_int(record.get('trust_buy')),
            'trust_sell': self._to_int(record.get('trust_sell')),
            'trust_net': self._to_int(record.get('trust_net')),
            # 自營商
            'dealer_buy': self._to_int(record.get('dealer_buy')),
            'dealer_sell': self._to_int(record.get('dealer_sell')),
            'dealer_net': self._to_int(record.get('dealer_net')),
            # 合計
            'total_net': self._to_int(record.get('total_net')),
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
