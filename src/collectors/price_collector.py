"""
價格資料收集器
"""

from datetime import datetime
from typing import Dict, Any

from .base import BaseCollector
from ..datasources import TWSEDataSource, TPExDataSource
from ..utils.data_merger import DataMerger


class PriceCollector(BaseCollector):
    """
    價格資料收集器

    使用官方 API 收集 TWSE 和 TPEx 價格資料
    """

    def __init__(self, date: str):
        """
        初始化價格收集器

        Args:
            date: 收集日期 (YYYY-MM-DD)
        """
        super().__init__(date)
        self.twse_source = TWSEDataSource()
        self.tpex_source = TPExDataSource()
        self.merger = DataMerger()

    def get_data_type(self) -> str:
        """取得資料類型"""
        return "price"

    def collect(self) -> Dict[str, Any]:
        """
        收集價格資料

        Returns:
            dict: 包含 metadata 和 data 的字典
        """
        # 收集 TWSE 資料
        self.logger.info("收集 TWSE（上市）資料")
        twse_df = self.twse_source.get_daily_prices(self.date)
        twse_count = len(twse_df)
        self.logger.info(f"TWSE: {twse_count} 檔")

        # 收集 TPEx 資料
        self.logger.info("收集 TPEx（上櫃）資料")
        tpex_df = self.tpex_source.get_daily_prices(self.date)
        tpex_count = len(tpex_df)
        self.logger.info(f"TPEx: {tpex_count} 檔")

        # 合併資料
        self.logger.info("合併資料")
        merged_df = self.merger.merge_dataframes([twse_df, tpex_df])

        if merged_df.empty:
            self.logger.warning("無資料（可能是非交易日）")
            return {}

        # 轉換為 dict
        data_list = merged_df.to_dict(orient='records')

        # 建立回傳結果
        result = {
            "metadata": {
                "date": self.date,
                "collected_at": datetime.now().isoformat(),
                "total_count": len(data_list),
                "twse_count": twse_count,
                "tpex_count": tpex_count,
                "source": "TWSE + TPEx Official API"
            },
            "data": data_list
        }

        self.logger.info(f"收集完成: 總計 {len(data_list)} 檔 (上市 {twse_count} + 上櫃 {tpex_count})")
        return result
