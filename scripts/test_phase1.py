#!/usr/bin/env python3
"""
Phase 1 功能測試腳本

測試所有 Phase 1 的核心功能，包括：
1. 配置系統
2. 工具模組
3. 收集器模組
4. 執行腳本

Usage:
    python scripts/test_phase1.py
    python scripts/test_phase1.py --verbose  # 詳細輸出
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import (
    get_logger,
    get_global_config,
    FileHandler,
    DataValidator,
    StockListManager,
    build_file_path
)
from src.collectors import (
    create_price_collector,
    create_institutional_collector,
    create_margin_collector,
    create_lending_collector
)

# 設定簡單的 logger（不依賴配置檔）
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


def test_config_loading():
    """測試配置載入"""
    logger.info("測試配置載入...")

    config = get_global_config()

    # 檢查必要配置
    assert hasattr(config, 'finmind'), "缺少 finmind 配置"
    assert hasattr(config, 'collection'), "缺少 collection 配置"
    assert hasattr(config, 'storage'), "缺少 storage 配置"

    # 檢查點號語法
    rate_limit = config.finmind.rate_limit
    assert rate_limit == 600, f"rate_limit 應為 600，實際為 {rate_limit}"

    # 檢查 get 方法
    base_path = config.get('storage.base_path', 'default')
    assert base_path == 'data/raw', f"base_path 錯誤: {base_path}"

    logger.info("✓ 配置系統正常")


def test_file_handler():
    """測試檔案處理器"""
    logger.info("測試檔案處理器...")

    import pandas as pd
    import tempfile
    import os

    handler = FileHandler()

    # 建立測試資料
    test_data = {
        'stock_id': ['2330', '2317'],
        'date': ['2025-01-28', '2025-01-28'],
        'close': [650, 100]
    }
    df = pd.DataFrame(test_data)

    # 測試 JSON 儲存
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = Path(tmpdir) / 'test.json'
        success = handler.save_json(df.to_dict('records'), json_path)
        assert success, "JSON 儲存失敗"
        assert json_path.exists(), "JSON 檔案不存在"

        # 測試 JSON 讀取
        loaded = handler.load_json(json_path)
        assert loaded is not None, "JSON 讀取失敗"
        assert len(loaded) == 2, f"資料筆數錯誤: {len(loaded)}"

        # 測試 CSV 儲存
        csv_path = Path(tmpdir) / 'test.csv'
        success = handler.save_csv(df, csv_path)
        assert success, "CSV 儲存失敗"
        assert csv_path.exists(), "CSV 檔案不存在"

        # 測試 CSV 讀取
        loaded_df = handler.load_csv(csv_path)
        assert loaded_df is not None, "CSV 讀取失敗"
        assert len(loaded_df) == 2, f"CSV 資料筆數錯誤: {len(loaded_df)}"

    logger.info("✓ 檔案處理器正常")


def test_build_file_path():
    """測試檔案路徑建立"""
    logger.info("測試檔案路徑建立...")

    # 測試 date_hierarchy
    path = build_file_path(
        base_path='data/raw',
        data_type='price',
        date='2025-01-28',
        stock_id='2330',
        file_format='json',
        structure='date_hierarchy'
    )
    expected = Path('data/raw/price/2025/01/20250128/2330.json')
    assert path == expected, f"路徑錯誤: {path} != {expected}"

    # 測試 aggregate
    path = build_file_path(
        base_path='data/raw',
        data_type='institutional',
        date='2025-01-28',
        file_format='json',
        structure='aggregate'
    )
    expected = Path('data/raw/institutional/2025/01/2025-01-28.json')
    assert path == expected, f"Aggregate 路徑錯誤: {path} != {expected}"

    logger.info("✓ 路徑建立正常")


def test_data_validator():
    """測試資料驗證器"""
    logger.info("測試資料驗證器...")

    import pandas as pd

    validator = DataValidator()

    # 測試價格資料驗證
    valid_price_data = pd.DataFrame({
        'stock_id': ['2330'],
        'date': ['2025-01-28'],
        'open': [650],
        'high': [655],
        'low': [648],
        'close': [652],
        'volume': [50000]
    })

    result = validator.validate(valid_price_data, 'price', raise_on_error=False)
    assert result, "有效的價格資料驗證失敗"

    # 測試無效資料（收盤價為負）
    invalid_price_data = pd.DataFrame({
        'stock_id': ['2330'],
        'date': ['2025-01-28'],
        'close': [-100]
    })

    result = validator.validate(invalid_price_data, 'price', raise_on_error=False)
    assert not result, "無效資料應該驗證失敗"

    logger.info("✓ 資料驗證器正常")


def test_stock_list_manager():
    """測試股票清單管理器"""
    logger.info("測試股票清單管理器...")
    logger.warning("⚠️  此測試會呼叫 FinMind API，請確保網路連線正常")

    manager = StockListManager()

    # 測試獲取股票清單（使用快取）
    stocks = manager.get_stock_list(use_cache=True)

    assert stocks is not None, "股票清單為 None"
    assert not stocks.empty, "股票清單為空"
    assert len(stocks) > 1000, f"股票數量異常: {len(stocks)}"

    # 測試獲取股票代碼
    stock_ids = manager.get_stock_ids()
    assert len(stock_ids) > 0, "股票代碼列表為空"
    assert '2330' in stock_ids, "股票清單中應包含 2330"

    # 測試搜尋股票
    results = manager.search_stocks('台積', field='stock_name')
    assert not results.empty, "搜尋台積電應有結果"

    logger.info(f"✓ 股票清單管理器正常 (共 {len(stocks)} 檔股票)")


def test_collectors():
    """測試收集器（模擬模式）"""
    logger.info("測試收集器...")

    # 測試價格收集器建立
    price_collector = create_price_collector()
    assert price_collector is not None, "價格收集器建立失敗"
    assert price_collector.get_data_type() == 'price', "資料類型錯誤"

    # 測試法人收集器建立
    inst_collector = create_institutional_collector()
    assert inst_collector is not None, "法人收集器建立失敗"
    assert inst_collector.get_data_type() == 'institutional', "資料類型錯誤"

    # 測試融資融券收集器建立
    margin_collector = create_margin_collector()
    assert margin_collector is not None, "融資融券收集器建立失敗"
    assert margin_collector.get_data_type() == 'margin', "資料類型錯誤"

    # 測試借券收集器建立
    lending_collector = create_lending_collector()
    assert lending_collector is not None, "借券收集器建立失敗"
    assert lending_collector.get_data_type() == 'lending', "資料類型錯誤"

    logger.info("✓ 所有收集器建立正常")


def test_collector_with_real_api():
    """測試收集器實際 API 呼叫（單一股票）"""
    logger.info("測試實際 API 呼叫...")
    logger.warning("⚠️  此測試會呼叫 FinMind API")

    # 使用昨天的日期（避免當天無資料）
    test_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    # 測試價格收集器
    collector = create_price_collector()
    try:
        df = collector.collect(test_date, stock_id='2330')
        assert df is not None, "收集結果為 None"

        if not df.empty:
            logger.info(f"✓ 價格資料收集成功: {len(df)} 筆")
            # 驗證必要欄位
            assert 'stock_id' in df.columns, "缺少 stock_id 欄位"
            assert 'date' in df.columns, "缺少 date 欄位"
            assert 'close' in df.columns, "缺少 close 欄位"
        else:
            logger.warning(f"⚠️  {test_date} 無資料（可能非交易日）")

    except Exception as e:
        logger.error(f"API 呼叫失敗: {e}")
        raise


def test_collector_stats():
    """測試收集器統計功能"""
    logger.info("測試收集器統計...")

    collector = create_price_collector()

    # 檢查初始統計
    stats = collector.get_stats()
    assert stats['api_calls'] == 0, "初始 API 呼叫數應為 0"
    assert stats['total_records'] == 0, "初始記錄數應為 0"

    # 重置統計
    collector.reset_stats()
    stats = collector.get_stats()
    assert stats['api_calls'] == 0, "重置後 API 呼叫數應為 0"

    logger.info("✓ 收集器統計功能正常")


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='Phase 1 功能測試')
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='顯示詳細錯誤訊息'
    )
    parser.add_argument(
        '--skip-api',
        action='store_true',
        help='跳過需要 API 的測試'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("Phase 1 功能測試")
    print("=" * 70)
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    runner = TestRunner(verbose=args.verbose)

    # 配置與工具模組測試
    runner.test("配置載入", test_config_loading)
    runner.test("檔案處理器", test_file_handler)
    runner.test("路徑建立", test_build_file_path)
    runner.test("資料驗證器", test_data_validator)

    # 收集器基礎測試
    runner.test("收集器建立", test_collectors)
    runner.test("收集器統計", test_collector_stats)

    # API 測試（可選）
    if not args.skip_api:
        print("\n⚠️  以下測試需要網路連線和 FinMind API")
        runner.test("股票清單管理器", test_stock_list_manager)
        runner.test("實際 API 呼叫", test_collector_with_real_api)
    else:
        print("\n⚠️  已跳過 API 測試 (使用 --skip-api)")

    # 顯示總結
    success = runner.summary()

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
