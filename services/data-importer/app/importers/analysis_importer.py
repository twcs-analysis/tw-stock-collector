"""
Technical Analysis Data Importer - 技術分析資料匯入器
"""

import logging
from datetime import date
from decimal import Decimal
from typing import Dict, Any, List

from ..db.models import StockAnalysisDaily
from .base_importer import BaseImporter


logger = logging.getLogger(__name__)


class AnalysisImporter(BaseImporter):
    """技術分析資料匯入器"""

    def __init__(self, session):
        super().__init__(session, data_type="analysis")

    def get_model_class(self):
        return StockAnalysisDaily

    def get_unique_keys(self) -> List[str]:
        return ['trade_date', 'stock_id']

    def transform_record(self, record: Dict[str, Any], import_date: date) -> Dict[str, Any]:
        """
        轉換技術分析資料記錄

        JSON 格式:
        {
            "trade_date": "2026-01-02",
            "stock_id": "0050",
            "open": 73.15,
            "high": 73.2,
            "low": 72.3,
            "close": 72.6,
            "volume": 175275799.0,
            "amount": 12738811404.0,
            "ma_5": 66.04,
            ...
        }

        Database 欄位 (對應 SQL schema):
        - trade_date, stock_id
        - open_price, high_price, low_price, close_price, volume, amount
        - ma_5, ma_10, ma_20, ma_60, ma_120, ma_240
        - rsi_6, rsi_14
        - macd_dif, macd_dea, macd_hist
        - dmi_pdi, dmi_mdi, dmi_adx, dmi_adxr
        - bb_upper, bb_mid, bb_lower
        - vol_ma5, vol_ma20, vol_ratio, vwap
        """
        return {
            'trade_date': import_date,
            'stock_id': record['stock_id'],
            # 基本價量
            'open_price': self._to_decimal(record.get('open')),
            'high_price': self._to_decimal(record.get('high')),
            'low_price': self._to_decimal(record.get('low')),
            'close_price': self._to_decimal(record.get('close')),
            'volume': self._to_int(record.get('volume')),
            'amount': self._to_decimal(record.get('amount')),
            # 移動平均線
            'ma_5': self._to_decimal(record.get('ma_5')),
            'ma_10': self._to_decimal(record.get('ma_10')),
            'ma_20': self._to_decimal(record.get('ma_20')),
            'ma_60': self._to_decimal(record.get('ma_60')),
            'ma_120': self._to_decimal(record.get('ma_120')),
            'ma_240': self._to_decimal(record.get('ma_240')),
            # RSI 指標
            'rsi_6': self._to_decimal(record.get('rsi_6')),
            'rsi_14': self._to_decimal(record.get('rsi_14')),
            # MACD 指標
            'macd_dif': self._to_decimal(record.get('macd_dif')),
            'macd_dea': self._to_decimal(record.get('macd_dea')),
            'macd_hist': self._to_decimal(record.get('macd_hist')),
            # DMI 指標
            'dmi_pdi': self._to_decimal(record.get('dmi_pdi')),
            'dmi_mdi': self._to_decimal(record.get('dmi_mdi')),
            'dmi_adx': self._to_decimal(record.get('dmi_adx')),
            'dmi_adxr': self._to_decimal(record.get('dmi_adxr')),
            # 布林通道
            'bb_upper': self._to_decimal(record.get('bb_upper')),
            'bb_mid': self._to_decimal(record.get('bb_mid')),
            'bb_lower': self._to_decimal(record.get('bb_lower')),
            # 成交量分析
            'vol_ma5': self._to_int(record.get('vol_ma5')),
            'vol_ma20': self._to_int(record.get('vol_ma20')),
            'vol_ratio': self._to_decimal(record.get('vol_ratio')),
            'vwap': self._to_decimal(record.get('vwap')),
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
