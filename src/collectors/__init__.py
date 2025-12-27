"""
資料收集器模組

提供各類台股資料的收集功能。
"""

from .base_collector import BaseCollector, CollectorError
from .price_collector import PriceCollector, create_price_collector
from .institutional_collector import InstitutionalCollector, create_institutional_collector
from .margin_collector import MarginCollector, create_margin_collector
from .lending_collector import LendingCollector, create_lending_collector

__all__ = [
    # Base
    'BaseCollector',
    'CollectorError',

    # Collectors
    'PriceCollector',
    'InstitutionalCollector',
    'MarginCollector',
    'LendingCollector',

    # Factory functions
    'create_price_collector',
    'create_institutional_collector',
    'create_margin_collector',
    'create_lending_collector',
]
