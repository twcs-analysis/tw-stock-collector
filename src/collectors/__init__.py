"""
收集器模組
"""

from .base import BaseCollector
from .price_collector import PriceCollector
from .margin_collector import MarginCollector
from .institutional_collector import InstitutionalCollector
from .lending_collector import LendingCollector

__all__ = [
    'BaseCollector',
    'PriceCollector',
    'MarginCollector',
    'InstitutionalCollector',
    'LendingCollector',
]
