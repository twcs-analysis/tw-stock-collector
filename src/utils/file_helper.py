"""
檔案處理工具
"""

import os
import json


def ensure_dir(path: str) -> None:
    """
    確保目錄存在，不存在則建立

    Args:
        path: 目錄路徑
    """
    os.makedirs(path, exist_ok=True)


def save_json(data: dict, file_path: str, indent: int = 2) -> None:
    """
    儲存 JSON 檔案

    Args:
        data: 要儲存的資料
        file_path: 檔案路徑
        indent: 縮排空格數
    """
    # 確保目錄存在
    directory = os.path.dirname(file_path)
    if directory:
        ensure_dir(directory)

    # 儲存 JSON
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def load_json(file_path: str) -> dict:
    """
    載入 JSON 檔案

    Args:
        file_path: 檔案路徑

    Returns:
        dict: JSON 資料
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def file_exists(file_path: str) -> bool:
    """
    檢查檔案是否存在

    Args:
        file_path: 檔案路徑

    Returns:
        bool: 檔案是否存在
    """
    return os.path.exists(file_path)


def get_file_size(file_path: str) -> float:
    """
    取得檔案大小 (KB)

    Args:
        file_path: 檔案路徑

    Returns:
        float: 檔案大小 (KB)
    """
    if not file_exists(file_path):
        return 0.0

    size_bytes = os.path.getsize(file_path)
    return size_bytes / 1024


def get_file_path(data_type: str, date_str: str, extension: str = 'json') -> str:
    """
    產生標準化的檔案路徑

    Args:
        data_type: 資料類型 (price, margin, institutional, lending)
        date_str: 日期 YYYY-MM-DD
        extension: 副檔名

    Returns:
        str: 檔案路徑
    """
    year = date_str[:4]
    month = date_str[5:7]
    return f"data/raw/{data_type}/{year}/{month}/{date_str}.{extension}"
