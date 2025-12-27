"""
檔案處理模組

提供統一的檔案儲存與讀取功能，支援：
- JSON 格式 (縮排、UTF-8)
- CSV 格式 (DataFrame)
- 目錄自動建立
- 檔案備份
- 壓縮支援 (gzip, zip)
"""

import gzip
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import pandas as pd

from .logger import get_logger
from .config import get_global_config

logger = get_logger(__name__)


class FileHandler:
    """檔案處理器"""

    def __init__(self, config: Optional[Any] = None):
        """
        Args:
            config: 配置實例，預設使用全域配置
        """
        if config is None:
            config = get_global_config()
        self.config = config

    def save_json(
        self,
        data: Union[Dict, List],
        file_path: Union[str, Path],
        ensure_ascii: bool = False,
        indent: int = 2,
        create_backup: bool = False
    ) -> bool:
        """
        儲存 JSON 檔案

        Args:
            data: 要儲存的資料 (dict 或 list)
            file_path: 檔案路徑
            ensure_ascii: 是否使用 ASCII 編碼（False 允許中文）
            indent: 縮排空格數 (None 為不格式化)
            create_backup: 是否建立備份（如果檔案已存在）

        Returns:
            bool: 是否成功

        Examples:
            >>> handler = FileHandler()
            >>> data = {'stock_id': '2330', 'name': '台積電'}
            >>> handler.save_json(data, 'data/stocks/2330.json')
        """
        file_path = Path(file_path)

        try:
            # 確保目錄存在
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # 備份現有檔案
            if create_backup and file_path.exists():
                self._create_backup(file_path)

            # 寫入 JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=ensure_ascii, indent=indent)

            logger.debug(f"JSON 儲存成功: {file_path}")
            return True

        except Exception as e:
            logger.error(f"JSON 儲存失敗: {file_path} - {e}", exc_info=True)
            return False

    def load_json(self, file_path: Union[str, Path]) -> Optional[Union[Dict, List]]:
        """
        讀取 JSON 檔案

        Args:
            file_path: 檔案路徑

        Returns:
            Dict 或 List，失敗時返回 None

        Examples:
            >>> handler = FileHandler()
            >>> data = handler.load_json('data/stocks/2330.json')
        """
        file_path = Path(file_path)

        if not file_path.exists():
            logger.warning(f"檔案不存在: {file_path}")
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            logger.debug(f"JSON 讀取成功: {file_path}")
            return data

        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失敗: {file_path} - {e}")
            return None
        except Exception as e:
            logger.error(f"JSON 讀取失敗: {file_path} - {e}", exc_info=True)
            return None

    def save_csv(
        self,
        df: pd.DataFrame,
        file_path: Union[str, Path],
        encoding: str = 'utf-8-sig',
        index: bool = False,
        create_backup: bool = False
    ) -> bool:
        """
        儲存 CSV 檔案

        Args:
            df: pandas DataFrame
            file_path: 檔案路徑
            encoding: 編碼格式 (utf-8-sig 支援 Excel)
            index: 是否儲存 index
            create_backup: 是否建立備份

        Returns:
            bool: 是否成功

        Examples:
            >>> handler = FileHandler()
            >>> df = pd.DataFrame({'stock_id': ['2330'], 'name': ['台積電']})
            >>> handler.save_csv(df, 'data/stocks.csv')
        """
        file_path = Path(file_path)

        try:
            # 確保目錄存在
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # 備份現有檔案
            if create_backup and file_path.exists():
                self._create_backup(file_path)

            # 寫入 CSV
            df.to_csv(file_path, encoding=encoding, index=index)

            logger.debug(f"CSV 儲存成功: {file_path} ({len(df)} rows)")
            return True

        except Exception as e:
            logger.error(f"CSV 儲存失敗: {file_path} - {e}", exc_info=True)
            return False

    def load_csv(
        self,
        file_path: Union[str, Path],
        encoding: str = 'utf-8-sig',
        **kwargs
    ) -> Optional[pd.DataFrame]:
        """
        讀取 CSV 檔案

        Args:
            file_path: 檔案路徑
            encoding: 編碼格式
            **kwargs: 傳遞給 pd.read_csv 的其他參數

        Returns:
            pd.DataFrame 或 None

        Examples:
            >>> handler = FileHandler()
            >>> df = handler.load_csv('data/stocks.csv')
        """
        file_path = Path(file_path)

        if not file_path.exists():
            logger.warning(f"檔案不存在: {file_path}")
            return None

        try:
            df = pd.read_csv(file_path, encoding=encoding, **kwargs)
            logger.debug(f"CSV 讀取成功: {file_path} ({len(df)} rows)")
            return df

        except Exception as e:
            logger.error(f"CSV 讀取失敗: {file_path} - {e}", exc_info=True)
            return None

    def save_dataframe(
        self,
        df: pd.DataFrame,
        file_path: Union[str, Path],
        format: str = 'auto',
        **kwargs
    ) -> bool:
        """
        自動根據副檔名儲存 DataFrame

        Args:
            df: pandas DataFrame
            file_path: 檔案路徑
            format: 格式 ('auto', 'json', 'csv', 'parquet')
            **kwargs: 傳遞給對應方法的參數

        Returns:
            bool: 是否成功

        Examples:
            >>> handler = FileHandler()
            >>> df = pd.DataFrame({'stock_id': ['2330']})
            >>> handler.save_dataframe(df, 'data/stocks.csv')  # 自動偵測 CSV
            >>> handler.save_dataframe(df, 'data/stocks.json')  # 自動偵測 JSON
        """
        file_path = Path(file_path)

        # 自動偵測格式
        if format == 'auto':
            suffix = file_path.suffix.lower()
            format_map = {
                '.json': 'json',
                '.csv': 'csv',
                '.parquet': 'parquet'
            }
            format = format_map.get(suffix, 'csv')

        # 根據格式儲存
        if format == 'json':
            # DataFrame 轉 JSON
            json_data = df.to_dict(orient='records')
            return self.save_json(json_data, file_path, **kwargs)

        elif format == 'csv':
            return self.save_csv(df, file_path, **kwargs)

        elif format == 'parquet':
            try:
                file_path.parent.mkdir(parents=True, exist_ok=True)
                df.to_parquet(file_path, **kwargs)
                logger.debug(f"Parquet 儲存成功: {file_path}")
                return True
            except Exception as e:
                logger.error(f"Parquet 儲存失敗: {file_path} - {e}", exc_info=True)
                return False

        else:
            logger.error(f"不支援的格式: {format}")
            return False

    def _create_backup(self, file_path: Path) -> bool:
        """
        建立檔案備份

        Args:
            file_path: 原始檔案路徑

        Returns:
            bool: 是否成功
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = file_path.with_name(f"{file_path.stem}_{timestamp}{file_path.suffix}")

        try:
            shutil.copy2(file_path, backup_path)
            logger.debug(f"建立備份: {backup_path}")
            return True
        except Exception as e:
            logger.warning(f"建立備份失敗: {e}")
            return False

    def compress_file(
        self,
        file_path: Union[str, Path],
        compression: str = 'gzip',
        remove_original: bool = False
    ) -> Optional[Path]:
        """
        壓縮檔案

        Args:
            file_path: 檔案路徑
            compression: 壓縮格式 ('gzip', 'zip')
            remove_original: 是否刪除原始檔案

        Returns:
            壓縮後的檔案路徑，失敗時返回 None

        Examples:
            >>> handler = FileHandler()
            >>> compressed = handler.compress_file('data/large_file.json', compression='gzip')
        """
        file_path = Path(file_path)

        if not file_path.exists():
            logger.error(f"檔案不存在: {file_path}")
            return None

        try:
            if compression == 'gzip':
                compressed_path = file_path.with_suffix(file_path.suffix + '.gz')

                with open(file_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)

                logger.info(f"壓縮完成: {compressed_path}")

                if remove_original:
                    file_path.unlink()
                    logger.debug(f"刪除原始檔案: {file_path}")

                return compressed_path

            elif compression == 'zip':
                compressed_path = file_path.with_suffix('.zip')
                shutil.make_archive(
                    str(compressed_path.with_suffix('')),
                    'zip',
                    file_path.parent,
                    file_path.name
                )

                logger.info(f"壓縮完成: {compressed_path}")

                if remove_original:
                    file_path.unlink()

                return compressed_path

            else:
                logger.error(f"不支援的壓縮格式: {compression}")
                return None

        except Exception as e:
            logger.error(f"壓縮失敗: {file_path} - {e}", exc_info=True)
            return None

    def get_file_size(self, file_path: Union[str, Path]) -> int:
        """
        獲取檔案大小 (bytes)

        Args:
            file_path: 檔案路徑

        Returns:
            檔案大小（bytes）
        """
        file_path = Path(file_path)
        if file_path.exists():
            return file_path.stat().st_size
        return 0

    def ensure_directory(self, dir_path: Union[str, Path]) -> bool:
        """
        確保目錄存在

        Args:
            dir_path: 目錄路徑

        Returns:
            bool: 是否成功
        """
        dir_path = Path(dir_path)

        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"建立目錄失敗: {dir_path} - {e}", exc_info=True)
            return False


def build_file_path(
    base_path: Union[str, Path],
    data_type: str,
    date: Union[str, datetime],
    stock_id: Optional[str] = None,
    file_format: str = 'json',
    structure: str = 'date_hierarchy'
) -> Path:
    """
    根據配置建立檔案路徑

    Args:
        base_path: 基礎路徑 (如 data/raw)
        data_type: 資料類型 (如 price, institutional)
        date: 日期 (字串或 datetime)
        stock_id: 股票代碼（選用，用於個股資料）
        file_format: 檔案格式 (json, csv)
        structure: 目錄結構 (date_hierarchy, flat, aggregate)

    Returns:
        Path: 完整檔案路徑

    Examples:
        >>> path = build_file_path('data/raw', 'price', '2025-01-28', '2330')
        # data/raw/price/2025/01/20250128/2330.json

        >>> path = build_file_path('data/raw', 'institutional', '2025-01-28', structure='aggregate')
        # data/raw/institutional/2025/01/2025-01-28.json
    """
    base = Path(base_path)

    # 處理日期
    if isinstance(date, str):
        date_obj = datetime.strptime(date, '%Y-%m-%d')
    else:
        date_obj = date

    year = date_obj.strftime('%Y')
    month = date_obj.strftime('%m')
    date_str = date_obj.strftime('%Y%m%d')
    date_dash = date_obj.strftime('%Y-%m-%d')

    # 根據結構模式建立路徑
    if structure == 'date_hierarchy':
        # data/raw/price/2025/01/20250128/2330.json
        if stock_id:
            return base / data_type / year / month / date_str / f"{stock_id}.{file_format}"
        else:
            return base / data_type / year / month / f"{date_dash}.{file_format}"

    elif structure == 'flat':
        # data/raw/price/2025-01-28_2330.json
        if stock_id:
            return base / data_type / f"{date_dash}_{stock_id}.{file_format}"
        else:
            return base / data_type / f"{date_dash}.{file_format}"

    elif structure == 'aggregate':
        # data/raw/institutional/2025/01/2025-01-28.json
        return base / data_type / year / month / f"{date_dash}.{file_format}"

    else:
        raise ValueError(f"不支援的目錄結構: {structure}")
