"""
工具類模組
"""

from .date_helper import is_trading_day, get_latest_trading_day, to_roc_date
from .file_helper import ensure_dir, save_json, file_exists, get_file_path
from .logger import setup_logger, log_collection_start, log_collection_result
from .config import get_global_config, get_config, Config
from .file_handler import FileHandler, build_file_path
from .validator import DataValidator, ValidationError


def get_logger(name: str = __name__):
    """
    取得 logger 實例的便利函數

    Args:
        name: Logger 名稱

    Returns:
        logging.Logger: Logger 實例
    """
    return setup_logger(name)


__all__ = [
    'is_trading_day',
    'get_latest_trading_day',
    'to_roc_date',
    'ensure_dir',
    'save_json',
    'file_exists',
    'get_file_path',
    'setup_logger',
    'log_collection_start',
    'log_collection_result',
    'get_logger',
    'get_global_config',
    'get_config',
    'Config',
    'FileHandler',
    'build_file_path',
    'DataValidator',
    'ValidationError',
]
