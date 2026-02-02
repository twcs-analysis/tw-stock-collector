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

    def run(self, enable_validation: bool = True) -> Dict[str, Any]:
        """
        執行收集流程: 記錄開始 → 收集資料 → 儲存 → 驗證 → 記錄結果

        Args:
            enable_validation: 是否啟用驗證（預設為 True）

        Returns:
            dict: 執行結果
                {
                    "status": "success" | "no_data" | "error",
                    "file": "path/to/file.json",  # 僅 success 時
                    "records": 100,  # 僅 success 時
                    "validation": {...},  # 僅 success 且 enable_validation 時
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

            # 驗證資料（如果啟用）
            if enable_validation:
                validation_result = self._validate_data(file_path)
                result['validation'] = validation_result

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

    def _validate_data(self, file_path: str) -> Dict[str, Any]:
        """
        驗證收集的資料並生成報告

        Args:
            file_path: 資料檔案路徑

        Returns:
            dict: 驗證結果摘要
        """
        try:
            # 動態匯入驗證器（避免循環依賴）
            from ..validators import (
                PriceValidator,
                MarginValidator,
                InstitutionalValidator,
                LendingValidator
            )

            # 選擇對應的驗證器
            validator_map = {
                'price': PriceValidator,
                'margin': MarginValidator,
                'institutional': InstitutionalValidator,
                'lending': LendingValidator
            }

            data_type = self.get_data_type()
            validator_class = validator_map.get(data_type)

            if not validator_class:
                self.logger.warning(f"找不到 {data_type} 對應的驗證器")
                return {'status': 'skipped', 'message': '無對應驗證器'}

            # 執行驗證
            validator = validator_class(file_path)
            validation_result = validator.validate()

            # 生成報告
            report_path = validator.generate_report()

            self.logger.info(
                f"驗證完成 - 狀態: {validation_result.status}, "
                f"評分: {validation_result.grade} ({validation_result.accuracy:.1f}%)"
            )

            return {
                'status': validation_result.status,
                'grade': validation_result.grade,
                'accuracy': validation_result.accuracy,
                'report': report_path,
                'passed': validation_result.passed_checks,
                'warned': validation_result.warned_checks,
                'failed': validation_result.failed_checks
            }

        except Exception as e:
            self.logger.error(f"驗證時發生錯誤: {e}", exc_info=True)
            return {'status': 'error', 'error': str(e)}
