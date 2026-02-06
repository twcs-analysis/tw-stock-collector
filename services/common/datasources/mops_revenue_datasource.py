"""
MOPS 月營收資料源（每日模式）

提供公開資訊觀測站的月營收查詢功能，用於逐一查詢個股是否已公告月營收
"""

from typing import Optional, Dict, Any
import pandas as pd
import requests
import random
import time


class MOPSRevenueDataSource:
    """MOPS 月營收資料源（用於 daily 模式）"""

    BASE_URL = "https://mops.twse.com.tw/mops/api/t05st10_ifrs"

    # 欄位對照表（與 TWSE/TPEx 統一格式）
    FIELD_MAPPING = {
        '本月': 'current_month_revenue',
        '去年同期': 'last_year_revenue',
        '增減金額': 'revenue_change',
        '增減百分比': 'yoy_change_pct',
        '本年累計': 'ytd_revenue',
        '去年累計': 'ytd_last_year_revenue',
        '備註/營收變化原因說明': 'note'
    }

    # User-Agent 候選列表（隨機選擇，模擬真實瀏覽器）
    USER_AGENTS = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0',
    ]

    def __init__(self, timeout: int = 30, delay: float = 0.5):
        """
        初始化 MOPS 月營收資料源

        Args:
            timeout: API 請求逾時時間（秒）
            delay: 每次請求之間的延遲（秒），避免過度請求
        """
        self.timeout = timeout
        self.delay = delay
        self.session = requests.Session()

    def _get_headers(self) -> Dict[str, str]:
        """
        產生請求 headers（隨機 User-Agent，模擬真實瀏覽器）

        Returns:
            headers 字典
        """
        return {
            'User-Agent': random.choice(self.USER_AGENTS),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en,zh-TW;q=0.9,zh;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'Origin': 'https://mops.twse.com.tw',
            'Referer': 'https://mops.twse.com.tw/mops/web/t05st10_ifrs',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }

    def _convert_roc_yearmonth(self, roc_yearmonth: str) -> str:
        """
        轉換民國年月為西元年月

        Args:
            roc_yearmonth: 民國年月（例如：11412 表示 114/12）

        Returns:
            西元年月（YYYY-MM）
        """
        if not roc_yearmonth or len(roc_yearmonth) < 4:
            return None

        try:
            year = int(roc_yearmonth[:3]) + 1911
            month = roc_yearmonth[3:5]
            return f"{year}-{month}"
        except:
            return None

    def _parse_revenue_data(
        self,
        result: Dict[str, Any],
        stock_id: str,
        year_month: str
    ) -> Optional[Dict[str, Any]]:
        """
        解析 API 回傳的營收資料

        Args:
            result: API 回傳的 result 欄位
            stock_id: 股票代碼
            year_month: 西元年月（YYYY-MM）

        Returns:
            解析後的資料字典，若無資料則回傳 None
        """
        if not result or 'data' not in result:
            return None

        data = result['data']
        if not data:
            return None

        # 建立基本資料
        revenue_data = {
            'year_month': year_month,
            'stock_id': stock_id,
            'stock_name': result.get('companyAbbreviation', ''),
            'type': 'twse' if result.get('marketKindName') == '上市公司' else 'tpex',
        }

        # 解析資料列
        for row in data:
            if len(row) >= 2:
                field_name = row[0]
                field_value = row[1]

                # 轉換欄位名稱
                if field_name in self.FIELD_MAPPING:
                    mapped_name = self.FIELD_MAPPING[field_name]

                    # 轉換數值（移除逗號）
                    if field_value and field_value != '-':
                        try:
                            # 移除逗號和空白
                            clean_value = field_value.replace(',', '').replace(' ', '')
                            revenue_data[mapped_name] = float(clean_value)
                        except:
                            revenue_data[mapped_name] = field_value
                    else:
                        revenue_data[mapped_name] = None

        # 計算 mom_change_pct（如果有 current_month_revenue 和 last_month_revenue）
        # 注意：MOPS API 沒有直接提供上月營收和 MoM，需要從其他來源補充
        # 這裡先設為 None
        revenue_data['last_month_revenue'] = None
        revenue_data['mom_change_pct'] = None

        # 計算 ytd_yoy_change_pct（如果有累計營收）
        if 'ytd_revenue' in revenue_data and 'ytd_last_year_revenue' in revenue_data:
            if revenue_data['ytd_revenue'] and revenue_data['ytd_last_year_revenue']:
                ytd_change = revenue_data['ytd_revenue'] - revenue_data['ytd_last_year_revenue']
                revenue_data['ytd_yoy_change_pct'] = (ytd_change / revenue_data['ytd_last_year_revenue']) * 100

        return revenue_data

    def get_single_revenue(
        self,
        stock_id: str,
        year_month: str
    ) -> Optional[Dict[str, Any]]:
        """
        查詢單一股票的月營收資料

        Args:
            stock_id: 股票代碼（4 位數字）
            year_month: 西元年月（YYYY-MM）

        Returns:
            月營收資料字典，若無資料則回傳 None
        """
        # 轉換為民國年月
        year, month = year_month.split('-')
        roc_year = int(year) - 1911
        roc_month = int(month)

        # 建立請求 payload
        payload = {
            "companyId": stock_id,
            "dataType": "2",  # 2 = 月營收
            "month": str(roc_month),
            "year": str(roc_year),
            "subsidiaryCompanyId": ""
        }

        try:
            # 發送請求
            response = self.session.post(
                self.BASE_URL,
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response.raise_for_status()

            # 解析回應
            json_data = response.json()

            # 檢查回應狀態
            if json_data.get('code') != 200:
                # 406 = 查無相符資料（尚未公告）
                return None

            # 解析資料
            result = json_data.get('result')
            if not result:
                return None

            # 轉換年月格式
            actual_year_month = self._convert_roc_yearmonth(result.get('yymm'))
            if not actual_year_month:
                actual_year_month = year_month

            # 解析營收資料
            revenue_data = self._parse_revenue_data(result, stock_id, actual_year_month)

            # 延遲避免過度請求
            time.sleep(self.delay)

            return revenue_data

        except requests.exceptions.RequestException as e:
            # 網路錯誤，回傳 None
            return None
        except Exception as e:
            # 其他錯誤，回傳 None
            return None

    def is_available(self, stock_id: str, year_month: str) -> bool:
        """
        檢查該股票是否已公告月營收

        Args:
            stock_id: 股票代碼
            year_month: 西元年月（YYYY-MM）

        Returns:
            是否已公告
        """
        return self.get_single_revenue(stock_id, year_month) is not None
