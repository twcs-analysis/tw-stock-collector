"""
個股期貨資料收集器
"""

from typing import Dict, Any

from .base import BaseCollector
from ..datasources.taifex_datasource import TAIFEXDataSource


class StockFuturesCollector(BaseCollector):
    """
    個股期貨資料收集器

    從 TAIFEX OpenAPI 收集個股期貨每日交易資料
    """

    def __init__(self, date: str):
        """
        初始化個股期貨收集器

        Args:
            date: 收集日期 (YYYY-MM-DD)
        """
        super().__init__(date)
        self.taifex_source = TAIFEXDataSource()

    def get_data_type(self) -> str:
        """取得資料類型"""
        return "stock_futures"

    def collect(self) -> Dict[str, Any]:
        """
        收集個股期貨資料

        Returns:
            dict: 包含 metadata 和 data 的字典
                {
                    "metadata": {
                        "date": "2026-03-13",
                        "total_count": 154,
                        "total_contracts": 314,
                        "source": "TAIFEX OpenAPI"
                    },
                    "data": [
                        {
                            "date": "2026-03-13",
                            "contract": "CDF",
                            "stock_id": "2330",
                            "stock_name": "台積電",
                            "contract_month": "202603",
                            "open": 1050.0,
                            "high": 1065.0,
                            "low": 1048.0,
                            "close": 1060.0,
                            "change": "+5",
                            "change_percent": "+0.47%",
                            "volume": 15000,
                            "settlement_price": 1058.0,
                            "open_interest": 25000,
                            "best_bid": 1059.0,
                            "best_ask": 1061.0,
                            "trading_session": "一般",
                            "type": "taifex"
                        },
                        ...
                    ]
                }
        """
        # 收集 TAIFEX 個股期貨資料
        self.logger.info("收集 TAIFEX 個股期貨資料")
        df = self.taifex_source.get_daily_prices(self.date)

        if df.empty:
            self.logger.warning("無資料（可能是非交易日）")
            return {}

        futures_count = len(df)
        self.logger.info(f"TAIFEX: {futures_count} 筆個股期貨契約")

        # 統計獨特的股票數量
        unique_stocks = df['stock_id'].nunique()
        self.logger.info(f"涵蓋 {unique_stocks} 檔股票")

        # 取得總標的數（用於 metadata）
        all_contracts = self.taifex_source.get_all_contracts()
        total_contracts = len(all_contracts)

        # 轉換為 dict
        data_list = df.to_dict(orient='records')

        # 建立回傳結果
        result = {
            "metadata": {
                "date": self.date,
                "total_count": futures_count,
                "unique_stocks": unique_stocks,
                "total_contracts": total_contracts,
                "source": "TAIFEX OpenAPI",
                "api": "DailyMarketReportFut"
            },
            "data": data_list
        }

        self.logger.info(
            f"收集完成: {futures_count} 筆個股期貨契約資料 "
            f"（涵蓋 {unique_stocks} 檔股票，共 {total_contracts} 個標的）"
        )
        return result
