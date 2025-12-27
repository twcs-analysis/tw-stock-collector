"""
日誌模組

提供統一的日誌記錄功能，支援：
- 從 YAML 配置檔載入日誌設定
- 自動建立日誌目錄
- 支援多個 logger 實例
- 日誌輪替與備份
"""

import logging
import logging.config
import os
from pathlib import Path
from typing import Optional
import yaml


class LoggerManager:
    """日誌管理器"""

    _initialized = False
    _config_path: Optional[Path] = None

    @classmethod
    def initialize(cls, config_path: Optional[str] = None) -> None:
        """
        初始化日誌系統

        Args:
            config_path: 日誌配置檔路徑，預設為 config/logging.yaml

        Raises:
            FileNotFoundError: 配置檔不存在
            yaml.YAMLError: 配置檔格式錯誤
        """
        if cls._initialized:
            return

        # 預設配置檔路徑
        if config_path is None:
            config_path = "config/logging.yaml"

        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"日誌配置檔不存在: {config_file}")

        # 載入配置
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # 確保所有日誌目錄存在
        cls._ensure_log_directories(config)

        # 套用配置
        logging.config.dictConfig(config)

        cls._initialized = True
        cls._config_path = config_file

        # 記錄初始化成功
        root_logger = logging.getLogger()
        root_logger.info(f"日誌系統初始化完成，配置檔: {config_file}")

    @classmethod
    def _ensure_log_directories(cls, config: dict) -> None:
        """
        確保所有日誌目錄存在

        Args:
            config: 日誌配置字典
        """
        handlers = config.get('handlers', {})

        for handler_name, handler_config in handlers.items():
            if 'filename' in handler_config:
                log_file = Path(handler_config['filename'])
                log_dir = log_file.parent

                # 建立目錄
                if not log_dir.exists():
                    log_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def reset(cls) -> None:
        """重置日誌系統（主要用於測試）"""
        cls._initialized = False
        cls._config_path = None


def get_logger(name: str, initialize: bool = True) -> logging.Logger:
    """
    獲取 logger 實例

    Args:
        name: Logger 名稱，建議使用模組名稱 (如 __name__)
        initialize: 是否自動初始化日誌系統

    Returns:
        logging.Logger: Logger 實例

    Examples:
        >>> logger = get_logger(__name__)
        >>> logger.info("開始收集資料")
        >>> logger.error("發生錯誤", exc_info=True)
    """
    # 自動初始化
    if initialize and not LoggerManager._initialized:
        try:
            LoggerManager.initialize()
        except FileNotFoundError:
            # 如果配置檔不存在，使用基本配置
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

    return logging.getLogger(name)


def setup_simple_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    建立簡單的 logger（不使用 YAML 配置）

    Args:
        name: Logger 名稱
        level: 日誌等級 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日誌檔案路徑（選用）
        format_string: 自訂格式字串

    Returns:
        logging.Logger: Logger 實例

    Examples:
        >>> logger = setup_simple_logger(
        ...     "test",
        ...     level=logging.DEBUG,
        ...     log_file="logs/test.log"
        ... )
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 預設格式
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    formatter = logging.Formatter(format_string, datefmt='%Y-%m-%d %H:%M:%S')

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (選用)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


class LogContext:
    """
    日誌上下文管理器，用於追蹤特定操作的日誌

    Examples:
        >>> with LogContext(logger, "收集台積電資料"):
        ...     # 執行收集邏輯
        ...     pass
        # 自動記錄開始與結束
    """

    def __init__(self, logger: logging.Logger, operation: str):
        """
        Args:
            logger: Logger 實例
            operation: 操作描述
        """
        self.logger = logger
        self.operation = operation

    def __enter__(self):
        self.logger.info(f"開始: {self.operation}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.logger.info(f"完成: {self.operation}")
        else:
            self.logger.error(
                f"失敗: {self.operation} - {exc_type.__name__}: {exc_val}",
                exc_info=True
            )
        return False


# 預先初始化（如果配置檔存在）
try:
    if Path("config/logging.yaml").exists():
        LoggerManager.initialize()
except Exception:
    # 靜默失敗，讓使用者決定如何初始化
    pass
