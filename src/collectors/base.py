"""
收集器基礎類別
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from ..utils import setup_logger, save_json, get_file_path, log_collection_start, log_collection_result


class BaseCollector(ABC):
    """
    資料收集器基礎類別

    所有收集器都必須繼承此類別並實作 collect() 和 get_data_type() 方法
    """

    def __init__(self, date: str):
        """
        初始化收集器

        Args:
            date: 收集日期 (YYYY-MM-DD)
        """
        self.date = date
        self.logger = setup_logger(self.__class__.__name__)

    @abstractmethod
    def collect(self) -> Dict[str, Any]:
        """
        收集資料 (子類別必須實作)

        Returns:
            dict: 包含 metadata 和 data 的字典
                {
                    "metadata": {
                        "date": "2024-12-27",
                        "collected_at": "2024-12-27T10:30:00",
                        "total_count": 100,
                        "source": "TWSE API"
                    },
                    "data": [...]
                }
        """
        raise NotImplementedError("子類別必須實作 collect() 方法")

    @abstractmethod
    def get_data_type(self) -> str:
        """
        取得資料類型 (子類別必須實作)

        Returns:
            str: 資料類型 (price, margin, institutional, lending)
        """
        raise NotImplementedError("子類別必須實作 get_data_type() 方法")

    def get_file_path(self) -> str:
        """
        取得檔案儲存路徑

        Returns:
            str: 檔案路徑
        """
        return get_file_path(self.get_data_type(), self.date)

    def save(self, data: Dict[str, Any]) -> str:
        """
        儲存資料到檔案

        Args:
            data: 要儲存的資料

        Returns:
            str: 儲存的檔案路徑
        """
        file_path = self.get_file_path()
        save_json(data, file_path)
        self.logger.info(f"資料已儲存: {file_path}")
        return file_path

    def run(self) -> Dict[str, Any]:
        """
        執行收集流程: 記錄開始 → 收集資料 → 儲存 → 記錄結果

        Returns:
            dict: 執行結果
                {
                    "status": "success" | "no_data" | "error",
                    "file": "path/to/file.json",  # 僅 success 時
                    "records": 100,  # 僅 success 時
                    "error": "錯誤訊息"  # 僅 error 時
                }
        """
        data_type = self.get_data_type()

        # 記錄開始
        log_collection_start(self.logger, data_type, self.date)

        try:
            # 收集資料
            data = self.collect()

            # 檢查是否有資料
            if not data or not data.get('data'):
                result = {
                    'status': 'no_data',
                    'message': '無資料（可能是非交易日）'
                }
                log_collection_result(self.logger, data_type, result)
                return result

            # 儲存資料
            file_path = self.save(data)

            # 成功結果
            result = {
                'status': 'success',
                'file': file_path,
                'records': len(data.get('data', []))
            }
            log_collection_result(self.logger, data_type, result)
            return result

        except Exception as e:
            # 錯誤處理
            self.logger.exception(f"收集 {data_type} 資料時發生錯誤")
            result = {
                'status': 'error',
                'error': str(e)
            }
            log_collection_result(self.logger, data_type, result)
            return result
