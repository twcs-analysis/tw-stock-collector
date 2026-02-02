"""
Common Database Package

共用的資料庫連線管理和 ORM 模型定義
供所有服務使用（data-importer, data-transformer, api-service 等）
"""

from .models import (
    Base,
    Stock,
    StockPriceDaily,
    StockInstitutionalDaily,
    StockMarginDaily,
    StockLendingDaily,
    StockTop20VolumeDaily,
    StockAnalysisDaily,
    DataImportLog,
)
from .connection import (
    DatabaseConfig,
    DatabaseManager,
    get_db_manager,
    init_database,
)

__all__ = [
    # Models
    "Base",
    "Stock",
    "StockPriceDaily",
    "StockInstitutionalDaily",
    "StockMarginDaily",
    "StockLendingDaily",
    "StockTop20VolumeDaily",
    "StockAnalysisDaily",
    "DataImportLog",
    # Connection
    "DatabaseConfig",
    "DatabaseManager",
    "get_db_manager",
    "init_database",
]
