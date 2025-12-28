"""
資料合併工具

負責合併多個資料源（TWSE + TPEx）的資料
"""
import pandas as pd
from typing import List
import logging

logger = logging.getLogger(__name__)


class DataMerger:
    """資料合併器"""

    @staticmethod
    def merge_dataframes(
        dataframes: List[pd.DataFrame],
        deduplicate_by: str = 'stock_id'
    ) -> pd.DataFrame:
        """
        合併多個 DataFrame

        Args:
            dataframes: DataFrame 列表
            deduplicate_by: 去重欄位

        Returns:
            合併後的 DataFrame
        """
        # 過濾空 DataFrame
        valid_dfs = [df for df in dataframes if not df.empty]

        if not valid_dfs:
            logger.warning("所有 DataFrame 都是空的")
            return pd.DataFrame()

        # 合併
        merged = pd.concat(valid_dfs, ignore_index=True)

        # 去重（如果有重複的股票代碼，保留第一筆）
        if deduplicate_by and deduplicate_by in merged.columns:
            before_count = len(merged)
            merged = merged.drop_duplicates(subset=[deduplicate_by, 'date'], keep='first')
            after_count = len(merged)

            if before_count != after_count:
                logger.info(f"去重: {before_count} -> {after_count} (移除 {before_count - after_count} 筆)")

        # 排序
        if 'stock_id' in merged.columns:
            merged = merged.sort_values('stock_id').reset_index(drop=True)

        logger.info(f"合併完成: {len(merged)} 筆資料")
        return merged
