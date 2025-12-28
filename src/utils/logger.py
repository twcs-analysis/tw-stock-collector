"""
日誌工具
"""

import logging
import sys


def setup_logger(name: str = __name__, level: int = logging.INFO) -> logging.Logger:
    """
    設定 Logger
    
    Args:
        name: Logger 名稱
        level: 日誌等級
    
    Returns:
        logging.Logger: Logger 實例
    """
    logger = logging.getLogger(name)
    
    # 避免重複設定
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger


def log_collection_start(logger: logging.Logger, data_type: str, date: str) -> None:
    """記錄收集開始"""
    logger.info(f"開始收集 {data_type} 資料: {date}")


def log_collection_result(logger: logging.Logger, data_type: str, result: dict) -> None:
    """記錄收集結果"""
    status = result.get('status')
    
    if status == 'success':
        records = result.get('records', 0)
        logger.info(f"✅ {data_type}: 成功收集 {records} 筆資料")
    elif status == 'no_data':
        logger.warning(f"⚠️  {data_type}: 無資料")
    else:
        error = result.get('error', '未知錯誤')
        logger.error(f"❌ {data_type}: 收集失敗 - {error}")
