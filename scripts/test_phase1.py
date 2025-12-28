#!/usr/bin/env python3
"""
Phase 1 功能測試腳本

測試所有 Phase 1 的核心功能，包括：
1. 工具模組
2. 收集器模組

Usage:
    python scripts/test_phase1.py
    python scripts/test_phase1.py --skip-api  # 跳過 API 測試
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import (
    is_trading_day,
    get_latest_trading_day,
    ensure_dir,
    save_json,
    file_exists,
    get_file_path,
)
from src.collectors import (
    PriceCollector,
    MarginCollector,
    InstitutionalCollector,
    LendingCollector
)

# 設定簡單的 logger
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestRunner:
    """測試執行器"""

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.passed = 0
        self.failed = 0
        self.tests = []

    def test(self, name: str, func):
        """執行單一測試"""
        print(f"\n{'='*70}")
        print(f"測試: {name}")
        print(f"{'='*70}")

        try:
            func()
            self.passed += 1
            self.tests.append((name, True, None))
            print(f"✅ 通過: {name}")
        except Exception as e:
            self.failed += 1
            self.tests.append((name, False, str(e)))
            print(f"❌ 失敗: {name}")
            print(f"   錯誤: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()

    def summary(self):
        """顯示測試總結"""
        print(f"\n{'='*70}")
        print("測試總結")
        print(f"{'='*70}")
        print(f"總測試數: {self.passed + self.failed}")
        print(f"通過: {self.passed}")
        print(f"失敗: {self.failed}")
        print(f"成功率: {self.passed / (self.passed + self.failed) * 100:.1f}%")

        if self.failed > 0:
            print(f"\n失敗的測試:")
            for name, passed, error in self.tests:
                if not passed:
                    print(f"  ❌ {name}")
                    if error:
                        print(f"     {error}")

        print(f"{'='*70}")
        return self.failed == 0


def test_date_utils():
    """測試日期工具函式"""
    logger.info("測試日期工具函式...")

    # 測試週末（一定不是交易日）
    weekend = '2025-01-25'  # 星期六
    assert not is_trading_day(weekend), f"{weekend} 不應該是交易日"

    # 測試週日（一定不是交易日）
    sunday = '2025-01-26'  # 星期日
    assert not is_trading_day(sunday), f"{sunday} 不應該是交易日"

    # 測試取得最近交易日
    latest = get_latest_trading_day()
    assert latest is not None, "應該能取得最近交易日"
    assert isinstance(latest, str), "最近交易日應該是字串"

    logger.info("✓ 日期工具正常")


def test_file_utils():
    """測試檔案工具函式"""
    logger.info("測試檔案工具函式...")

    import tempfile
    import json

    # 測試 ensure_dir
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir) / 'test' / 'nested'
        ensure_dir(str(test_dir))
        assert test_dir.exists(), "目錄應該被建立"

        # 測試 save_json
        test_data = {'test': 'data', 'count': 123}
        json_file = test_dir / 'test.json'
        save_json(test_data, str(json_file))
        assert json_file.exists(), "JSON 檔案應該被建立"

        # 驗證內容
        with open(json_file, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        assert loaded == test_data, "JSON 內容應該一致"

        # 測試 file_exists
        assert file_exists(str(json_file)), "應該檢測到檔案存在"
        assert not file_exists(str(test_dir / 'nonexist.json')), "應該檢測到檔案不存在"

    logger.info("✓ 檔案工具正常")


def test_collectors_initialization():
    """測試收集器初始化"""
    logger.info("測試收集器初始化...")

    test_date = '2025-01-28'

    # 測試各種收集器初始化
    price_collector = PriceCollector(test_date)
    assert price_collector.date == test_date, "PriceCollector 日期設定錯誤"

    margin_collector = MarginCollector(test_date)
    assert margin_collector.date == test_date, "MarginCollector 日期設定錯誤"

    inst_collector = InstitutionalCollector(test_date)
    assert inst_collector.date == test_date, "InstitutionalCollector 日期設定錯誤"

    lending_collector = LendingCollector(test_date)
    assert lending_collector.date == test_date, "LendingCollector 日期設定錯誤"

    # 測試 get_data_type
    assert price_collector.get_data_type() == 'price', "資料類型錯誤"
    assert margin_collector.get_data_type() == 'margin', "資料類型錯誤"
    assert inst_collector.get_data_type() == 'institutional', "資料類型錯誤"
    assert lending_collector.get_data_type() == 'lending', "資料類型錯誤"

    logger.info("✓ 收集器初始化正常")


def test_price_collector_api(skip_api=False):
    """測試價格收集器 API 呼叫"""
    if skip_api:
        logger.info("跳過 API 測試")
        return

    logger.info("測試價格收集器 API...")

    # 使用昨天的日期（避免今天可能沒資料）
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    collector = PriceCollector(yesterday)
    result = collector.collect()

    # 檢查結果結構
    assert isinstance(result, dict), "結果應該是 dict"

    if result:  # 如果有資料
        assert 'metadata' in result, "應該有 metadata"
        assert 'data' in result, "應該有 data"
        assert isinstance(result['data'], list), "data 應該是 list"

        if len(result['data']) > 0:
            # 檢查第一筆資料
            first_record = result['data'][0]
            assert 'stock_id' in first_record or '證券代號' in first_record, "應該有股票代號欄位"

    logger.info("✓ 價格收集器 API 正常")


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='Phase 1 功能測試')
    parser.add_argument('--verbose', action='store_true', help='顯示詳細錯誤訊息')
    parser.add_argument('--skip-api', action='store_true', help='跳過 API 測試（不連線外部）')
    args = parser.parse_args()

    print("=" * 70)
    print("Phase 1 功能測試")
    print("=" * 70)
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"跳過 API 測試: {'是' if args.skip_api else '否'}")
    print("=" * 70)

    runner = TestRunner(verbose=args.verbose)

    # 執行測試
    runner.test("日期工具函式", test_date_utils)
    runner.test("檔案工具函式", test_file_utils)
    runner.test("收集器初始化", test_collectors_initialization)

    if not args.skip_api:
        runner.test("價格收集器 API", lambda: test_price_collector_api(args.skip_api))

    # 顯示總結
    success = runner.summary()

    # 回傳狀態碼
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
