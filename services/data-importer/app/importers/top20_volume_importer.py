"""
Top 20 Volume Data Importer - 成交量前20名資料匯入器
"""

import logging
from datetime import date
from decimal import Decimal
from typing import Dict, Any, List

from ..db.models import StockTop20VolumeDaily
from .base_importer import BaseImporter


logger = logging.getLogger(__name__)


class Top20VolumeImporter(BaseImporter):
    """成交量前20名資料匯入器"""

    def __init__(self, session):
        super().__init__(session, data_type="top20_volume")

    def get_model_class(self):
        return StockTop20VolumeDaily

    def get_unique_keys(self) -> List[str]:
        return ['trade_date', 'rank']

    def transform_record(self, record: Dict[str, Any], import_date: date) -> Dict[str, Any]:
        """
        轉換成交量前20名資料記錄

        JSON 格式:
        {
            "date": "2024-12-27",
            "rank": 1,
            "stock_id": "2330",
            "stock_name": "台積電",
            "volume": 45678912,
            "amount": 49000000000.0,
            "close": 1090.0,
            "change": 10.0,
            "change_pct": 0.92,
            "type": "twse"
        }
        """
        return {
            'stock_id': record['stock_id'],
            'trade_date': import_date,
            'rank': self._to_int(record.get('rank')),
            'volume': self._to_int(record.get('volume')),
            'amount': self._to_decimal(record.get('amount')),
            'transaction_count': self._to_int(record.get('transaction_count')),
            # 價格資料
            'open_price': self._to_decimal(record.get('open')),
            'high_price': self._to_decimal(record.get('high')),
            'low_price': self._to_decimal(record.get('low')),
            'close_price': self._to_decimal(record.get('close')),
            'change_price': self._to_decimal(record.get('change')),
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
