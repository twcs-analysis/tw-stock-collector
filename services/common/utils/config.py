"""
配置管理模組

提供統一的配置管理功能，支援：
- YAML 配置檔載入
- 環境變數替換
- Singleton 模式（全域唯一實例）
- 點號語法存取嵌套配置
- 配置驗證
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, Optional, Union
import yaml


class Config:
    """
    配置管理器 (Singleton)

    使用點號語法存取配置:
        config.finmind.api_token
        config.collection.batch.use_aggregate_api

    Examples:
        >>> config = Config()
        >>> api_token = config.finmind.api_token
        >>> use_agg = config.collection.batch.use_aggregate_api
        >>> config.get('finmind.rate_limit', default=600)
    """

    _instance: Optional['Config'] = None
    _config_data: Dict[str, Any] = {}
    _config_path: Optional[Path] = None

    def __new__(cls, config_path: Optional[str] = None):
        """
        Singleton 實現

        Args:
            config_path: 配置檔路徑，僅在首次建立時有效
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config(config_path)
        return cls._instance

    def _load_config(self, config_path: Optional[str] = None) -> None:
        """
        載入配置檔

        Args:
            config_path: 配置檔路徑，預設為 config/config.yaml

        Raises:
            FileNotFoundError: 配置檔不存在
            yaml.YAMLError: 配置檔格式錯誤
        """
        if config_path is None:
            config_path = "config/config.yaml"

        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"配置檔不存在: {config_file}")

        # 載入 YAML
        with open(config_file, 'r', encoding='utf-8') as f:
            raw_config = yaml.safe_load(f)

        # 處理環境變數替換
        self._config_data = self._resolve_env_vars(raw_config)
        self._config_path = config_file

    def _resolve_env_vars(self, data: Any) -> Any:
        """
        遞迴處理環境變數替換

        支援格式: ${ENV_VAR} 或 ${ENV_VAR:default_value}

        Args:
            data: 待處理的資料

        Returns:
            處理後的資料
        """
        if isinstance(data, dict):
            return {k: self._resolve_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._resolve_env_vars(item) for item in data]
        elif isinstance(data, str):
            return self._replace_env_var(data)
        else:
            return data

    def _replace_env_var(self, value: str) -> str:
        """
        替換單一字串中的環境變數

        Args:
            value: 原始字串

        Returns:
            替換後的字串
        """
        # 匹配 ${VAR} 或 ${VAR:default}
        pattern = r'\$\{([A-Z_][A-Z0-9_]*):?([^}]*)\}'

        def replacer(match):
            var_name = match.group(1)
            default_value = match.group(2) if match.group(2) else ''
            return os.environ.get(var_name, default_value)

        return re.sub(pattern, replacer, value)

    def get(self, key: str, default: Any = None) -> Any:
        """
        使用點號語法獲取配置值

        Args:
            key: 配置鍵，支援嵌套 (如 'finmind.api_token')
            default: 預設值

        Returns:
            配置值或預設值

        Examples:
            >>> config.get('finmind.rate_limit', 600)
            >>> config.get('collection.batch.use_aggregate_api', True)
        """
        keys = key.split('.')
        value = self._config_data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def __getattr__(self, name: str) -> Union['ConfigSection', Any]:
        """
        支援點號語法存取

        Args:
            name: 屬性名稱

        Returns:
            ConfigSection 或具體的配置值
        """
        if name.startswith('_'):
            # 避免與內部屬性衝突
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        if name in self._config_data:
            value = self._config_data[name]
            if isinstance(value, dict):
                return ConfigSection(value, name)
            return value

        raise AttributeError(f"配置項 '{name}' 不存在")

    def set(self, key: str, value: Any) -> None:
        """
        設定配置值（僅影響記憶體，不會寫入檔案）

        Args:
            key: 配置鍵，支援嵌套
            value: 配置值

        Examples:
            >>> config.set('development.debug_mode', True)
        """
        keys = key.split('.')
        data = self._config_data

        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]

        data[keys[-1]] = value

    def reload(self) -> None:
        """重新載入配置檔"""
        if self._config_path:
            self._load_config(str(self._config_path))

    def to_dict(self) -> Dict[str, Any]:
        """
        轉換為字典

        Returns:
            配置字典
        """
        return self._config_data.copy()

    def __repr__(self) -> str:
        return f"Config(config_path={self._config_path})"


class ConfigSection:
    """
    配置區段，用於支援嵌套點號語法

    內部類別，使用者不應直接建立
    """

    def __init__(self, data: Dict[str, Any], path: str):
        self._data = data
        self._path = path

    def __getattr__(self, name: str) -> Union['ConfigSection', Any]:
        if name.startswith('_'):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        if name in self._data:
            value = self._data[name]
            if isinstance(value, dict):
                return ConfigSection(value, f"{self._path}.{name}")
            return value

        raise AttributeError(f"配置項 '{self._path}.{name}' 不存在")

    def __getitem__(self, key: str) -> Any:
        """支援字典語法"""
        return self._data[key]

    def __contains__(self, key: str) -> bool:
        """支援 in 運算子"""
        return key in self._data

    def get(self, key: str, default: Any = None) -> Any:
        """類似字典的 get 方法"""
        return self._data.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return self._data.copy()

    def __repr__(self) -> str:
        return f"ConfigSection(path={self._path})"


def get_config(config_path: Optional[str] = None) -> Config:
    """
    獲取配置實例（便利函數）

    Args:
        config_path: 配置檔路徑，僅在首次呼叫時有效

    Returns:
        Config 實例

    Examples:
        >>> config = get_config()
        >>> api_token = config.finmind.api_token
    """
    return Config(config_path)


def validate_config(config: Config) -> bool:
    """
    驗證配置完整性

    Args:
        config: Config 實例

    Returns:
        是否通過驗證

    Raises:
        ValueError: 配置驗證失敗
    """
    # 檢查必要的配置項
    required_sections = [
        'finmind',
        'collection',
        'storage',
        'logging'
    ]

    for section in required_sections:
        try:
            getattr(config, section)
        except AttributeError:
            raise ValueError(f"缺少必要配置區段: {section}")

    # 檢查資料類型設定
    data_types = config.collection.data_types.to_dict()
    if not any(data_types.values()):
        raise ValueError("至少需要啟用一種資料類型")

    # 檢查儲存路徑
    storage_path = config.storage.base_path
    if not storage_path:
        raise ValueError("storage.base_path 不能為空")

    # 檢查日誌目錄
    log_dir = config.logging.log_dir
    if not log_dir:
        raise ValueError("logging.log_dir 不能為空")

    return True


# 預先建立全域實例（如果配置檔存在）
_global_config: Optional[Config] = None

try:
    if Path("config/config.yaml").exists():
        _global_config = Config()
except Exception:
    # 靜默失敗，讓使用者決定如何初始化
    pass


def get_global_config() -> Config:
    """
    獲取全域配置實例

    Returns:
        Config 實例

    Raises:
        RuntimeError: 配置未初始化
    """
    global _global_config
    if _global_config is None:
        _global_config = Config()
    return _global_config
