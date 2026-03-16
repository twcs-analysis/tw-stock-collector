#!/usr/bin/env python3
"""
TAIFEX API 測試腳本

用途：測試台灣期貨交易所 OpenAPI 的各個端點

作者：Claude Sonnet 4.5
日期：2026-03-15
"""

import requests
import json
from datetime import datetime
from typing import Dict, List


class TAIFEXAPITester:
    """TAIFEX OpenAPI 測試器"""

    BASE_URL = "https://openapi.taifex.com.tw/v1"

    def __init__(self):
        self.session = requests.Session()

    def test_daily_market_report(self, date: str = None) -> Dict:
        """
        測試每日期貨交易行情 API

        Args:
            date: 日期（格式：YYYY-MM-DD），不指定則取最新交易日

        Returns:
            API 回應資料
        """
        url = f"{self.BASE_URL}/DailyMarketReportFut"
        if date:
            url += f"?date={date}"

        print(f"\n{'='*60}")
        print(f"測試 API: DailyMarketReportFut")
        print(f"URL: {url}")
        print(f"{'='*60}")

        response = self.session.get(url)
        response.raise_for_status()

        data = response.json()
        print(f"✅ 成功取得資料")
        print(f"   總筆數: {len(data)}")

        # 過濾出個股期貨
        stock_futures = [item for item in data if item['Contract'].startswith('C')]
        print(f"   個股期貨: {len(stock_futures)} 筆")

        # 顯示第一筆個股期貨範例
        if stock_futures:
            print(f"\n範例資料（第一筆個股期貨）:")
            print(json.dumps(stock_futures[0], ensure_ascii=False, indent=2))

        return data

    def test_ssf_lists(self) -> List[Dict]:
        """
        測試個股期貨交易標的清單 API

        Returns:
            個股期貨標的清單
        """
        url = f"{self.BASE_URL}/SSFLists"

        print(f"\n{'='*60}")
        print(f"測試 API: SSFLists")
        print(f"URL: {url}")
        print(f"{'='*60}")

        response = self.session.get(url)
        response.raise_for_status()

        data = response.json()
        print(f"✅ 成功取得資料")
        print(f"   個股期貨標的總數: {len(data)}")

        # 顯示前 10 個標的
        print(f"\n前 10 個標的:")
        for item in data[:10]:
            print(f"   {item['Contract']}: {item['StockCode']} {item['StockName']}")

        return data

    def test_daily_volume_stats(self) -> List[Dict]:
        """
        測試每日個股期貨交易量統計 API

        Returns:
            交易量統計資料
        """
        url = f"{self.BASE_URL}/va12"

        print(f"\n{'='*60}")
        print(f"測試 API: va12 (每日交易量統計)")
        print(f"URL: {url}")
        print(f"{'='*60}")

        response = self.session.get(url)
        response.raise_for_status()

        data = response.json()
        print(f"✅ 成功取得資料")

        for item in data:
            contract_type = "股票期貨" if item['ContractType'] == 'STF' else "ETF 期貨"
            volume = int(item['Volume'])
            print(f"   {contract_type}: {volume:,} 口")

        return data

    def test_csv_format(self) -> str:
        """
        測試 CSV 格式回傳

        Returns:
            CSV 格式資料（字串）
        """
        url = f"{self.BASE_URL}/DailyMarketReportFut"

        print(f"\n{'='*60}")
        print(f"測試 CSV 格式")
        print(f"URL: {url}")
        print(f"{'='*60}")

        headers = {'Accept': 'text/csv'}
        response = self.session.get(url, headers=headers)

        # 檢查是否真的回傳 CSV
        content_type = response.headers.get('Content-Type', '')
        print(f"Content-Type: {content_type}")

        if 'csv' in content_type.lower():
            print(f"✅ 成功取得 CSV 格式資料")
            lines = response.text.split('\n')
            print(f"   總行數: {len(lines)}")
            print(f"\n前 5 行:")
            for line in lines[:5]:
                print(f"   {line}")
        else:
            print(f"⚠️  回傳格式不是 CSV（可能仍為 JSON）")
            print(f"   前 200 字元: {response.text[:200]}")

        return response.text

    def get_contract_to_stock_mapping(self) -> Dict[str, Dict]:
        """
        取得期貨代碼與股票代碼的對應關係

        Returns:
            對應字典 {期貨代碼: {stock_code, stock_name}}
        """
        data = self.test_ssf_lists()

        mapping = {
            item['Contract']: {
                'stock_code': item['StockCode'],
                'stock_name': item['StockName']
            }
            for item in data
        }

        return mapping

    def run_all_tests(self, date: str = None):
        """
        執行所有測試

        Args:
            date: 測試日期（格式：YYYY-MM-DD）
        """
        print(f"\n🚀 開始測試 TAIFEX OpenAPI")
        print(f"   時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if date:
            print(f"   測試日期: {date}")

        try:
            # 測試 1: 每日期貨交易行情
            self.test_daily_market_report(date)

            # 測試 2: 個股期貨標的清單
            self.test_ssf_lists()

            # 測試 3: 每日交易量統計
            self.test_daily_volume_stats()

            # 測試 4: CSV 格式
            # self.test_csv_format()  # 目前 TAIFEX API 似乎不支援 CSV

            print(f"\n{'='*60}")
            print(f"✅ 所有測試完成")
            print(f"{'='*60}")

        except Exception as e:
            print(f"\n❌ 測試失敗: {e}")
            raise


def main():
    """主程式"""
    import argparse

    parser = argparse.ArgumentParser(description='TAIFEX OpenAPI 測試工具')
    parser.add_argument(
        '--date',
        type=str,
        help='測試日期（格式：YYYY-MM-DD），不指定則使用最新交易日'
    )

    args = parser.parse_args()

    tester = TAIFEXAPITester()
    tester.run_all_tests(date=args.date)


if __name__ == '__main__':
    main()
