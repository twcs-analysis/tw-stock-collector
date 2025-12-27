"""
基礎收集器類別

所有資料收集器的抽象基礎類別，提供：
- FinMind API 整合
- 重試機制
- 日誌記錄
- 效能監控
- 錯誤處理
"""

import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import pandas as pd
from FinMind.data import DataLoader
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from ..utils import (
    get_logger,
    get_global_config,
    FileHandler,
    DataValidator,
    build_file_path
)

logger = get_logger(__name__)


class CollectorError(Exception):
    """收集器錯誤"""
    pass


class BaseCollector(ABC):
    """
    基礎收集器抽象類別

    所有具體收集器都應繼承此類別並實作 collect() 方法
    """

    def __init__(
        self,
        config: Optional[Any] = None,
        api_token: Optional[str] = None
    ):
        """
        Args:
            config: 配置實例
            api_token: FinMind API Token (選用)
        """
        if config is None:
            config = get_global_config()

        self.config = config
        self.file_handler = FileHandler(config)
        self.validator = DataValidator(config)

        # FinMind DataLoader
        self.dl = DataLoader()
        if api_token:
            self.dl.login_by_token(api_token=api_token)

        # Logger
        self.logger = get_logger(self.__class__.__name__)

        # 統計資訊
        self.stats = {
            'api_calls': 0,
            'total_records': 0,
            'success_count': 0,
            'failed_count': 0,
            'start_time': None,
            'end_time': None
        }

    @abstractmethod
    def collect(
        self,
        date: Union[str, datetime],
        stock_id: Optional[str] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        收集資料 (抽象方法，子類必須實作)

        Args:
            date: 收集日期
            stock_id: 股票代碼 (選用，某些資料類型不需要)
            **kwargs: 其他參數

        Returns:
            pd.DataFrame: 收集到的資料

        Raises:
            CollectorError: 收集失敗
        """
        pass

    @abstractmethod
    def get_data_type(self) -> str:
        """
        返回資料類型名稱

        Returns:
            str: 資料類型 (如 'price', 'institutional')
        """
        pass

    def fetch_with_retry(
        self,
        fetch_func,
        *args,
        **kwargs
    ) -> pd.DataFrame:
        """
        帶重試機制的 API 呼叫

        Args:
            fetch_func: API 呼叫函數
            *args, **kwargs: 傳遞給函數的參數

        Returns:
            pd.DataFrame: API 返回的資料

        Raises:
            CollectorError: API 呼叫失敗
        """
        retry_config = self.config.finmind.retry

        @retry(
            stop=stop_after_attempt(retry_config.max_attempts),
            wait=wait_fixed(retry_config.wait_seconds),
            retry=retry_if_exception_type(Exception),
            reraise=True
        )
        def _fetch():
            self.stats['api_calls'] += 1
            start_time = time.time()

            try:
                df = fetch_func(*args, **kwargs)
                elapsed = time.time() - start_time

                self.logger.debug(
                    f"API 呼叫成功: {fetch_func.__name__}, "
                    f"耗時 {elapsed:.2f}s, 筆數 {len(df) if df is not None else 0}"
                )

                return df

            except KeyError as e:
                # KeyError 通常表示 API 返回沒有 data 欄位(非交易日或無資料)
                # 這是正常情況,不需要重試,直接返回空 DataFrame
                elapsed = time.time() - start_time
                if 'data' in str(e):
                    self.logger.info(
                        f"查詢日期無資料(可能是非交易日): {fetch_func.__name__}, "
                        f"耗時 {elapsed:.2f}s"
                    )
                    return pd.DataFrame()
                else:
                    # 其他 KeyError 還是要報錯
                    raise

            except Exception as e:
                elapsed = time.time() - start_time
                self.logger.warning(
                    f"API 呼叫失敗: {fetch_func.__name__}, "
                    f"耗時 {elapsed:.2f}s, 錯誤: {e}"
                )
                raise

        try:
            return _fetch()
        except KeyError:
            # KeyError 已經在 _fetch 中處理了,這裡直接返回空 DataFrame
            return pd.DataFrame()
        except Exception as e:
            self.logger.error(f"API 呼叫最終失敗: {e}", exc_info=True)
            raise CollectorError(f"API 呼叫失敗: {e}") from e

    def save_data(
        self,
        df: pd.DataFrame,
        date: Union[str, datetime],
        stock_id: Optional[str] = None,
        validate: bool = True
    ) -> bool:
        """
        儲存資料到檔案

        Args:
            df: 要儲存的 DataFrame
            date: 日期
            stock_id: 股票代碼 (選用)
            validate: 是否驗證資料

        Returns:
            bool: 是否成功
        """
        if df is None or df.empty:
            self.logger.warning("資料為空，跳過儲存")
            return False

        # 驗證資料
        if validate:
            try:
                data_type = self.get_data_type()
                if not self.validator.validate(df, data_type, raise_on_error=False):
                    self.logger.warning(f"資料驗證失敗: {data_type}")
                    # 根據配置決定是否繼續
                    if self.config.validation.on_validation_error == 'raise':
                        return False
            except Exception as e:
                self.logger.error(f"驗證過程發生錯誤: {e}")

        # 建立檔案路徑
        storage_config = self.config.storage
        file_path = build_file_path(
            base_path=storage_config.base_path,
            data_type=self.get_data_type(),
            date=date,
            stock_id=stock_id,
            file_format=storage_config.file_format,
            structure=storage_config.directory_structure
        )

        # 決定合併模式
        # aggregate 結構：多個股票存入同一個檔案，使用 merge_by_key
        # 其他結構：每個股票獨立檔案，使用 overwrite
        merge_mode = 'merge_by_key' if storage_config.directory_structure == 'aggregate' else 'overwrite'

        # 儲存
        success = self.file_handler.save_dataframe(
            df=df,
            file_path=file_path,
            format=storage_config.file_format,
            merge_mode=merge_mode,
            create_backup=storage_config.options.create_backup
        )

        if success:
            self.stats['success_count'] += 1
            self.stats['total_records'] += len(df)
            self.logger.info(
                f"資料已儲存: {file_path} ({len(df)} 筆)"
            )
        else:
            self.stats['failed_count'] += 1
            self.logger.error(f"資料儲存失敗: {file_path}")

        return success

    def collect_and_save(
        self,
        date: Union[str, datetime],
        stock_id: Optional[str] = None,
        **kwargs
    ) -> bool:
        """
        收集並儲存資料 (便利方法)

        Args:
            date: 日期
            stock_id: 股票代碼
            **kwargs: 其他參數

        Returns:
            bool: 是否成功
        """
        try:
            # 收集
            df = self.collect(date, stock_id, **kwargs)

            # 如果是空資料(例如非交易日),記錄訊息但不算失敗
            if df is None or df.empty:
                self.logger.info(
                    f"查詢日期無資料: date={date}, stock_id={stock_id} (可能是非交易日)"
                )
                return True  # 無資料不算失敗,返回 True

            # 儲存
            return self.save_data(df, date, stock_id)

        except Exception as e:
            self.logger.error(
                f"收集或儲存失敗: date={date}, stock_id={stock_id}, 錯誤={e}",
                exc_info=True
            )
            self.stats['failed_count'] += 1
            return False

    def batch_collect(
        self,
        dates: List[Union[str, datetime]],
        stock_ids: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        批次收集資料

        Args:
            dates: 日期列表
            stock_ids: 股票代碼列表 (選用)
            **kwargs: 其他參數

        Returns:
            Dict: 收集統計資訊
        """
        self.stats['start_time'] = datetime.now()
        self.logger.info(
            f"開始批次收集: {len(dates)} 個日期, "
            f"{len(stock_ids) if stock_ids else 0} 檔股票"
        )

        success_count = 0
        failed_count = 0

        # 根據是否需要股票代碼來決定收集方式
        if stock_ids:
            # 需要逐一收集每檔股票
            for date in dates:
                for stock_id in stock_ids:
                    try:
                        if self.collect_and_save(date, stock_id, **kwargs):
                            success_count += 1
                        else:
                            failed_count += 1
                    except Exception as e:
                        self.logger.error(
                            f"批次收集失敗: {date}, {stock_id}, {e}"
                        )
                        failed_count += 1
        else:
            # 不需要股票代碼 (使用 aggregate API)
            for date in dates:
                try:
                    if self.collect_and_save(date, stock_id=None, **kwargs):
                        success_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    self.logger.error(f"批次收集失敗: {date}, {e}")
                    failed_count += 1

        self.stats['end_time'] = datetime.now()
        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()

        summary = {
            'success_count': success_count,
            'failed_count': failed_count,
            'total_records': self.stats['total_records'],
            'api_calls': self.stats['api_calls'],
            'duration_seconds': duration,
            'records_per_second': self.stats['total_records'] / duration if duration > 0 else 0
        }

        self.logger.info(
            f"批次收集完成: 成功 {success_count}, 失敗 {failed_count}, "
            f"耗時 {duration:.2f}s"
        )

        return summary

    def get_stats(self) -> Dict[str, Any]:
        """
        獲取統計資訊

        Returns:
            Dict: 統計資訊
        """
        return self.stats.copy()

    def reset_stats(self) -> None:
        """重置統計資訊"""
        self.stats = {
            'api_calls': 0,
            'total_records': 0,
            'success_count': 0,
            'failed_count': 0,
            'start_time': None,
            'end_time': None
        }

    def _format_date(self, date: Union[str, datetime]) -> str:
        """
        格式化日期為 YYYY-MM-DD

        Args:
            date: 日期

        Returns:
            str: 格式化後的日期
        """
        if isinstance(date, str):
            return date
        elif isinstance(date, datetime):
            return date.strftime('%Y-%m-%d')
        else:
            raise ValueError(f"不支援的日期格式: {type(date)}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(data_type={self.get_data_type()})"
