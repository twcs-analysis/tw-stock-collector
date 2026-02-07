"""
月營收資料收集器
"""

import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional, Literal

from .base import BaseCollector
from ..datasources.twse_revenue_datasource import TWSERevenueDataSource
from ..datasources.tpex_revenue_datasource import TPExRevenueDataSource
from ..datasources.mops_revenue_datasource import MOPSRevenueDataSource


class RevenueCollector(BaseCollector):
    """
    月營收資料收集器

    使用官方 API 收集 TWSE 和 TPEx 月營收資料

    支援兩種模式：
    - daily: 每日收集模式（1-10 日，資料漸進累積）
    - monthly: 月度收集模式（10 日後，一次取得完整資料）
    """

    def __init__(
        self,
        year_month: Optional[str] = None,
        mode: Literal["daily", "monthly"] = "monthly",
        collection_date: Optional[str] = None
    ):
        """
        初始化月營收收集器

        Args:
            year_month: 收集年月 (YYYY-MM)，若為 None 則收集最新資料
            mode: 收集模式，"daily" 或 "monthly"
            collection_date: 收集日期 (YYYY-MM-DD)，僅用於 daily 模式
        """
        # 如果沒有指定年月，使用當前年月
        if year_month is None:
            year_month = datetime.now().strftime("%Y-%m")

        # 如果沒有指定收集日期，使用當前日期
        if collection_date is None:
            collection_date = datetime.now().strftime("%Y-%m-%d")

        # BaseCollector 需要 date 參數
        date = collection_date if mode == "daily" else f"{year_month}-01"
        super().__init__(date)

        self.year_month = year_month
        self.mode = mode
        self.collection_date = collection_date
        self.twse_source = TWSERevenueDataSource()
        self.tpex_source = TPExRevenueDataSource()
        self.mops_source = MOPSRevenueDataSource(delay=0.3)  # daily 模式使用

    def get_data_type(self) -> str:
        """取得資料類型"""
        return "revenue"

    def get_save_path(self, actual_year_month: str = None) -> str:
        """
        取得儲存路徑，根據模式決定儲存路徑

        Args:
            actual_year_month: 實際年月（若未提供則使用 self.year_month）

        Returns:
            str: 儲存路徑
        """
        # 使用實際年月或預設年月
        year_month = actual_year_month or self.year_month
        year, month = year_month.split('-')

        if self.mode == "daily":
            # daily 模式：data/raw/revenue-daily/YYYY/YYYY-MM.json（同一個月同一個檔案）
            return f"data/raw/revenue-daily/{year}/{year_month}.json"
        else:
            # monthly 模式：data/raw/revenue-monthly/YYYY/YYYY-MM.json（使用實際年月）
            return f"data/raw/revenue-monthly/{year}/{year_month}.json"

    def get_file_path(self) -> str:
        """
        覆寫 BaseCollector 的 get_file_path 方法

        Returns:
            str: 檔案路徑
        """
        # 如果有實際年月（從上次收集結果中取得），使用實際年月
        # 否則使用預設年月
        if hasattr(self, '_actual_year_month') and self._actual_year_month:
            return self.get_save_path(self._actual_year_month)
        return self.get_save_path()

    def collect(self) -> Dict[str, Any]:
        """
        收集月營收資料

        Returns:
            dict: 包含 metadata 和 data 的字典
        """
        if self.mode == "daily":
            result = self._collect_daily()
        else:
            result = self._collect_monthly()

        # 儲存實際年月供 get_file_path() 使用
        if result and 'metadata' in result:
            self._actual_year_month = result['metadata'].get('year_month')

        return result

    def _collect_monthly(self) -> Dict[str, Any]:
        """
        月度收集模式：一次取得所有公司完整資料

        Returns:
            dict: 包含 metadata 和 data 的字典
        """
        # 收集 TWSE 資料
        self.logger.info("收集 TWSE（上市）月營收資料")
        twse_df = self.twse_source.get_revenue_data(self.year_month)
        twse_count = len(twse_df)
        self.logger.info(f"TWSE: {twse_count} 檔")

        # 收集 TPEx 資料
        self.logger.info("收集 TPEx（上櫃）月營收資料")
        tpex_df = self.tpex_source.get_revenue_data(self.year_month)
        tpex_count = len(tpex_df)
        self.logger.info(f"TPEx: {tpex_count} 檔")

        # 合併資料（手動合併，因為 DataMerger 期望 date 欄位）
        self.logger.info("合併資料")
        valid_dfs = [df for df in [twse_df, tpex_df] if not df.empty]

        if not valid_dfs:
            self.logger.warning("無資料")
            return {}

        merged_df = pd.concat(valid_dfs, ignore_index=True)

        # 去重（如果有重複的股票代碼，保留第一筆）
        if 'stock_id' in merged_df.columns and 'year_month' in merged_df.columns:
            before_count = len(merged_df)
            merged_df = merged_df.drop_duplicates(subset=['stock_id', 'year_month'], keep='first')
            after_count = len(merged_df)

            if before_count != after_count:
                self.logger.info(f"去重: {before_count} -> {after_count} (移除 {before_count - after_count} 筆)")

        # 排序
        if 'stock_id' in merged_df.columns:
            merged_df = merged_df.sort_values('stock_id').reset_index(drop=True)

        self.logger.info(f"合併完成: {len(merged_df)} 筆資料")

        # 轉換為 dict
        data_list = merged_df.to_dict(orient='records')

        # 取得實際的年月（從資料中取得，因為 API 只提供最新資料）
        actual_year_month = None
        if len(data_list) > 0 and 'year_month' in data_list[0]:
            actual_year_month = data_list[0]['year_month']

        # 建立回傳結果
        metadata = {
            "year_month": actual_year_month or self.year_month,
            "mode": self.mode,
            "total_count": len(data_list),
            "twse_count": twse_count,
            "tpex_count": tpex_count,
            "source": "TWSE + TPEx Official API"
        }

        # daily 模式額外記錄收集日期
        if self.mode == "daily":
            metadata["collection_date"] = self.collection_date

        result = {
            "metadata": metadata,
            "data": data_list
        }

        self.logger.info(f"收集完成: 總計 {len(data_list)} 檔 (上市 {twse_count} + 上櫃 {tpex_count})")

        # 如果實際年月與請求年月不同，記錄警告
        if actual_year_month and actual_year_month != self.year_month:
            self.logger.warning(f"請求年月 {self.year_month}，但 API 回傳 {actual_year_month} 的資料")

        return result

    def _get_stock_list(self) -> list:
        """
        取得股票代碼列表（從 monthly API 取得）

        Returns:
            股票代碼列表
        """
        self.logger.info("取得股票代碼列表...")

        stock_ids = []

        # 從 TWSE 取得上市股票列表
        try:
            twse_df = self.twse_source.get_revenue_data(self.year_month)
            if not twse_df.empty and 'stock_id' in twse_df.columns:
                twse_ids = twse_df['stock_id'].tolist()
                stock_ids.extend(twse_ids)
                self.logger.info(f"TWSE 上市股票: {len(twse_ids)} 檔")
        except Exception as e:
            self.logger.warning(f"取得 TWSE 股票列表失敗: {e}")

        # 從 TPEx 取得上櫃股票列表
        try:
            tpex_df = self.tpex_source.get_revenue_data(self.year_month)
            if not tpex_df.empty and 'stock_id' in tpex_df.columns:
                tpex_ids = tpex_df['stock_id'].tolist()
                stock_ids.extend(tpex_ids)
                self.logger.info(f"TPEx 上櫃股票: {len(tpex_ids)} 檔")
        except Exception as e:
            self.logger.warning(f"取得 TPEx 股票列表失敗: {e}")

        self.logger.info(f"總計: {len(stock_ids)} 檔股票")
        return stock_ids

    def _load_existing_data(self) -> Dict[str, Any]:
        """
        載入已存在的 daily 資料

        Returns:
            已存在的資料字典，若無則回傳空字典
        """
        import json
        from pathlib import Path

        save_path = self.get_save_path()

        if not Path(save_path).exists():
            self.logger.info("尚無已收集的資料")
            return {"data": [], "announced_stocks": set()}

        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                existing = json.load(f)

            # 取得已公告的股票代碼集合
            announced_stocks = {item['stock_id'] for item in existing.get('data', [])}

            self.logger.info(f"載入已收集資料: {len(announced_stocks)} 檔已公告")
            return {
                "data": existing.get('data', []),
                "announced_stocks": announced_stocks
            }
        except Exception as e:
            self.logger.warning(f"載入已存在資料失敗: {e}")
            return {"data": [], "announced_stocks": set()}

    def _get_last_month_revenue(self) -> Dict[str, float]:
        """
        從 OpenAPI 取得上月營收資料（用於計算 MoM）

        Returns:
            dict: {stock_id: last_month_revenue}
        """
        from datetime import datetime

        # 計算上個月年月
        year, month = map(int, self.year_month.split('-'))
        if month == 1:
            last_year = year - 1
            last_month = 12
        else:
            last_year = year
            last_month = month - 1
        last_year_month = f"{last_year}-{last_month:02d}"

        self.logger.info(f"取得上月營收資料 ({last_year_month})...")

        last_month_map = {}

        # 從 TWSE OpenAPI 取得上月資料
        try:
            twse_df = self.twse_source.get_revenue_data(last_year_month)
            if not twse_df.empty and 'stock_id' in twse_df.columns and 'current_month_revenue' in twse_df.columns:
                for _, row in twse_df.iterrows():
                    stock_id = row['stock_id']
                    revenue = row['current_month_revenue']
                    if stock_id and revenue:
                        last_month_map[stock_id] = revenue
                self.logger.info(f"TWSE 上月資料: {len(last_month_map)} 檔")
        except Exception as e:
            self.logger.warning(f"取得 TWSE 上月資料失敗: {e}")

        # 從 TPEx OpenAPI 取得上月資料
        try:
            tpex_df = self.tpex_source.get_revenue_data(last_year_month)
            if not tpex_df.empty and 'stock_id' in tpex_df.columns and 'current_month_revenue' in tpex_df.columns:
                tpex_count = 0
                for _, row in tpex_df.iterrows():
                    stock_id = row['stock_id']
                    revenue = row['current_month_revenue']
                    if stock_id and revenue:
                        last_month_map[stock_id] = revenue
                        tpex_count += 1
                self.logger.info(f"TPEx 上月資料: {tpex_count} 檔")
        except Exception as e:
            self.logger.warning(f"取得 TPEx 上月資料失敗: {e}")

        self.logger.info(f"上月營收總計: {len(last_month_map)} 檔")
        return last_month_map

    def _collect_daily(self) -> Dict[str, Any]:
        """
        每日收集模式：逐一查詢各公司是否已公告（增量更新）

        Returns:
            dict: 包含 metadata 和 data 的字典
        """
        self.logger.info("每日收集模式：逐一查詢已公告公司（增量更新）")

        # 載入已存在的資料
        existing = self._load_existing_data()
        existing_data = existing['data']
        announced_stocks = existing['announced_stocks']

        # 取得股票代碼列表
        stock_ids = self._get_stock_list()

        if not stock_ids:
            self.logger.error("無法取得股票代碼列表")
            return {}

        # 取得上月營收資料（用於計算 MoM）
        last_month_revenue_map = self._get_last_month_revenue()

        # 過濾掉已公告的股票
        remaining_stocks = [sid for sid in stock_ids if sid not in announced_stocks]

        self.logger.info(f"股票總數: {len(stock_ids)} 檔")
        self.logger.info(f"已公告: {len(announced_stocks)} 檔")
        self.logger.info(f"待查詢: {len(remaining_stocks)} 檔")

        if not remaining_stocks:
            self.logger.info("所有股票都已公告，無需查詢")
            # 回傳現有資料
            twse_count = sum(1 for d in existing_data if d.get('type') == 'twse')
            tpex_count = sum(1 for d in existing_data if d.get('type') == 'tpex')

            metadata = {
                "year_month": self.year_month,
                "mode": self.mode,
                "collection_date": self.collection_date,
                "total_count": len(existing_data),
                "twse_count": twse_count,
                "tpex_count": tpex_count,
                "total_stocks": len(stock_ids),
                "announced_ratio": f"{len(existing_data)/len(stock_ids)*100:.1f}%",
                "new_announced": 0,
                "source": "MOPS API"
            }

            return {
                "metadata": metadata,
                "data": existing_data
            }

        # 逐一查詢未公告的股票
        new_data_list = []
        new_announced_count = 0
        total_to_query = len(remaining_stocks)

        self.logger.info(f"開始查詢 {total_to_query} 檔股票...")
        self.logger.info(f"（每次查詢間隔 0.3 秒，預估需時 {total_to_query * 0.3 / 60:.1f} 分鐘）")

        for idx, stock_id in enumerate(remaining_stocks, 1):
            # 顯示進度
            if idx % 100 == 0 or idx == total_to_query:
                self.logger.info(f"進度: {idx}/{total_to_query} ({idx/total_to_query*100:.1f}%), 新公告: {new_announced_count}")

            # 查詢該股票月營收
            revenue_data = self.mops_source.get_single_revenue(stock_id, self.year_month)

            if revenue_data:
                # 填入上月營收並計算 MoM
                last_month_rev = last_month_revenue_map.get(stock_id)
                if last_month_rev:
                    revenue_data['last_month_revenue'] = last_month_rev
                    # 計算月增率 (MoM)
                    current_rev = revenue_data.get('current_month_revenue')
                    if current_rev and last_month_rev:
                        revenue_data['mom_change_pct'] = ((current_rev - last_month_rev) / last_month_rev) * 100

                new_data_list.append(revenue_data)
                new_announced_count += 1

        # 合併新舊資料
        all_data = existing_data + new_data_list
        total_count = len(stock_ids)

        # 統計上市/上櫃數量
        twse_count = sum(1 for d in all_data if d.get('type') == 'twse')
        tpex_count = sum(1 for d in all_data if d.get('type') == 'tpex')

        # 建立回傳結果
        metadata = {
            "year_month": self.year_month,
            "mode": self.mode,
            "collection_date": self.collection_date,
            "total_count": len(all_data),
            "twse_count": twse_count,
            "tpex_count": tpex_count,
            "total_stocks": total_count,
            "announced_ratio": f"{len(all_data)/total_count*100:.1f}%",
            "new_announced": new_announced_count,
            "source": "MOPS API"
        }

        result = {
            "metadata": metadata,
            "data": all_data
        }

        self.logger.info(f"收集完成:")
        self.logger.info(f"  本次新增: {new_announced_count} 檔")
        self.logger.info(f"  累計公告: {len(all_data)}/{total_count} 檔 ({len(all_data)/total_count*100:.1f}%)")
        self.logger.info(f"  上市 (TWSE): {twse_count} 檔")
        self.logger.info(f"  上櫃 (TPEx): {tpex_count} 檔")

        return result
