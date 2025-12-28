"""
股票清單管理模組

提供股票清單的：
- 從本地檔案讀取
- 快取管理
- 過濾與篩選

注意：不再使用 FinMind API，改用本地 stock_list_reference.csv
"""

import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Set
import pandas as pd

from .logger import get_logger
from .config import get_global_config
from .file_handler import FileHandler

logger = get_logger(__name__)


class StockListManager:
    """股票清單管理器（使用本地檔案）"""

    def __init__(
        self,
        config: Optional[any] = None
    ):
        """
        Args:
            config: 配置實例
        """
        if config is None:
            config = get_global_config()

        self.config = config
        self.file_handler = FileHandler(config)

        # 快取
        self._cache: Optional[pd.DataFrame] = None
        self._cache_time: Optional[datetime] = None

    def get_stock_list(
        self,
        force_update: bool = False,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        獲取股票清單

        優先順序:
        1. 記憶體快取 (如果啟用且未過期)
        2. 本地檔案 (如果存在且未過期)
        3. 從 API 重新獲取

        Args:
            force_update: 是否強制更新 (忽略快取)
            use_cache: 是否使用快取

        Returns:
            pd.DataFrame: 股票清單

        Examples:
            >>> manager = StockListManager()
            >>> stocks = manager.get_stock_list()
            >>> print(f"共 {len(stocks)} 檔股票")
        """
        # 檢查記憶體快取
        if use_cache and not force_update and self._is_cache_valid():
            logger.debug("使用記憶體快取")
            return self._cache.copy()

        # 檢查檔案快取
        file_path = Path(self.config.stock_list.file_path)
        if use_cache and not force_update and self._is_file_cache_valid(file_path):
            logger.info(f"從檔案載入股票清單: {file_path}")
            df = self.file_handler.load_csv(file_path)
            if df is not None:
                self._update_cache(df)
                return df.copy()

        # 從 API 獲取
        logger.info("從 FinMind API 獲取股票清單")
        df = self._fetch_from_api()

        # 過濾
        df = self._filter_stocks(df)

        # 儲存
        self._save_to_file(df, file_path)
        self._update_cache(df)

        logger.info(f"股票清單更新完成: {len(df)} 檔股票")
        return df.copy()

    def _fetch_from_api(self) -> pd.DataFrame:
        """
        從 FinMind API 獲取股票清單

        Returns:
            pd.DataFrame: 原始股票清單
        """
        try:
            df = self.dl.taiwan_stock_info()
            logger.info(f"API 返回 {len(df)} 檔股票")
            return df

        except Exception as e:
            logger.error(f"API 獲取失敗: {e}", exc_info=True)

            # 嘗試載入本地備份
            file_path = Path(self.config.stock_list.file_path)
            if file_path.exists():
                logger.warning("使用本地備份檔案")
                df = self.file_handler.load_csv(file_path)
                if df is not None:
                    return df

            raise

    def _filter_stocks(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        根據配置過濾股票

        Args:
            df: 原始股票 DataFrame

        Returns:
            pd.DataFrame: 過濾後的 DataFrame
        """
        original_count = len(df)
        filter_config = self.config.collection.stock_filter

        mode = filter_config.mode

        if mode == 'exclude':
            # 排除模式
            exclude_types = filter_config.exclude_types
            df = df[~df['type'].isin(exclude_types)]
            logger.info(f"排除 {exclude_types}: {original_count} -> {len(df)}")

        elif mode == 'regex':
            # 正則表達式模式
            pattern = filter_config.regex_pattern
            df = df[df['stock_id'].str.match(pattern)]
            logger.info(f"正則過濾 '{pattern}': {original_count} -> {len(df)}")

        elif mode == 'include':
            # 包含模式 (需要額外配置)
            include_types = filter_config.get('include_types', [])
            if include_types:
                df = df[df['type'].isin(include_types)]
                logger.info(f"僅保留 {include_types}: {original_count} -> {len(df)}")

        # 只保留上市上櫃股票 (使用 type 欄位: twse=上市, tpex=上櫃)
        df = df[df['type'].isin(['twse', 'tpex'])].copy()

        # 只保留活躍股票
        df = df[df['stock_id'].notna()].copy()

        return df

    def _save_to_file(self, df: pd.DataFrame, file_path: Path) -> None:
        """儲存到檔案"""
        try:
            # 添加更新時間
            df_to_save = df.copy()
            df_to_save['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            self.file_handler.save_csv(
                df_to_save,
                file_path,
                create_backup=True
            )
            logger.info(f"股票清單已儲存: {file_path}")

        except Exception as e:
            logger.error(f"儲存失敗: {e}", exc_info=True)

    def _update_cache(self, df: pd.DataFrame) -> None:
        """更新記憶體快取"""
        cache_config = self.config.stock_list.cache

        if cache_config.enabled:
            self._cache = df.copy()
            self._cache_time = datetime.now()
            logger.debug("記憶體快取已更新")

    def _is_cache_valid(self) -> bool:
        """檢查記憶體快取是否有效"""
        if self._cache is None or self._cache_time is None:
            return False

        cache_config = self.config.stock_list.cache
        if not cache_config.enabled:
            return False

        ttl = cache_config.ttl_seconds
        elapsed = (datetime.now() - self._cache_time).total_seconds()

        return elapsed < ttl

    def _is_file_cache_valid(self, file_path: Path) -> bool:
        """檢查檔案快取是否有效"""
        if not file_path.exists():
            return False

        # 檢查檔案修改時間
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        update_interval = self.config.stock_list.update_interval_days
        elapsed_days = (datetime.now() - mtime).days

        return elapsed_days < update_interval

    def get_stock_ids(self, **kwargs) -> List[str]:
        """
        獲取股票代碼清單

        Returns:
            List[str]: 股票代碼列表

        Examples:
            >>> manager = StockListManager()
            >>> stock_ids = manager.get_stock_ids()
            >>> print(stock_ids[:5])  # ['0050', '0051', '0052', '1101', '1102']
        """
        df = self.get_stock_list(**kwargs)
        return df['stock_id'].tolist()

    def get_stock_info(self, stock_id: str) -> Optional[dict]:
        """
        獲取單一股票資訊

        Args:
            stock_id: 股票代碼

        Returns:
            dict 或 None

        Examples:
            >>> manager = StockListManager()
            >>> info = manager.get_stock_info('2330')
            >>> print(info['stock_name'])  # 台積電
        """
        df = self.get_stock_list()
        stock_data = df[df['stock_id'] == stock_id]

        if stock_data.empty:
            logger.warning(f"找不到股票: {stock_id}")
            return None

        return stock_data.iloc[0].to_dict()

    def search_stocks(self, keyword: str, field: str = 'stock_name') -> pd.DataFrame:
        """
        搜尋股票

        Args:
            keyword: 關鍵字
            field: 搜尋欄位 ('stock_name', 'stock_id', 'industry')

        Returns:
            pd.DataFrame: 符合的股票

        Examples:
            >>> manager = StockListManager()
            >>> results = manager.search_stocks('台積')
            >>> results = manager.search_stocks('2330', field='stock_id')
        """
        df = self.get_stock_list()

        if field not in df.columns:
            logger.warning(f"欄位不存在: {field}")
            return pd.DataFrame()

        # 使用字串包含來搜尋
        mask = df[field].astype(str).str.contains(keyword, case=False, na=False)
        return df[mask].copy()

    def get_stocks_by_industry(self, industry: str) -> pd.DataFrame:
        """
        根據產業分類獲取股票

        Args:
            industry: 產業名稱

        Returns:
            pd.DataFrame: 該產業的股票

        Examples:
            >>> manager = StockListManager()
            >>> semiconductor = manager.get_stocks_by_industry('半導體業')
        """
        df = self.get_stock_list()

        if 'industry' not in df.columns:
            logger.warning("缺少 industry 欄位")
            return pd.DataFrame()

        return df[df['industry'] == industry].copy()

    def clear_cache(self) -> None:
        """清除記憶體快取"""
        self._cache = None
        self._cache_time = None
        logger.info("記憶體快取已清除")


def get_stock_list_manager(api_token: Optional[str] = None) -> StockListManager:
    """
    獲取股票清單管理器實例 (便利函數)

    Args:
        api_token: FinMind API Token

    Returns:
        StockListManager 實例

    Examples:
        >>> manager = get_stock_list_manager()
        >>> stocks = manager.get_stock_list()
    """
    return StockListManager(api_token=api_token)


def quick_get_stock_ids(force_update: bool = False) -> List[str]:
    """
    快速獲取股票代碼清單 (便利函數)

    Args:
        force_update: 是否強制更新

    Returns:
        List[str]: 股票代碼清單

    Examples:
        >>> stock_ids = quick_get_stock_ids()
        >>> print(f"共 {len(stock_ids)} 檔股票")
    """
    manager = StockListManager()
    return manager.get_stock_ids(force_update=force_update)
