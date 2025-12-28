"""
測試 BaseCollector 基礎架構
"""

import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.collectors.base import BaseCollector


class DummyCollector(BaseCollector):
    """測試用的虛擬收集器"""

    def get_data_type(self) -> str:
        return "test"

    def collect(self) -> dict:
        """模擬收集資料"""
        print(f"收集測試資料: {self.date}")

        # 模擬收集到 5 筆資料
        return {
            "metadata": {
                "date": self.date,
                "collected_at": datetime.now().isoformat(),
                "total_count": 5,
                "source": "Test Dummy Collector"
            },
            "data": [
                {"id": 1, "name": "測試1"},
                {"id": 2, "name": "測試2"},
                {"id": 3, "name": "測試3"},
                {"id": 4, "name": "測試4"},
                {"id": 5, "name": "測試5"},
            ]
        }


class EmptyCollector(BaseCollector):
    """測試無資料情況"""

    def get_data_type(self) -> str:
        return "empty"

    def collect(self) -> dict:
        """回傳空資料"""
        return {
            "metadata": {
                "date": self.date,
                "collected_at": datetime.now().isoformat(),
                "total_count": 0,
                "source": "Empty Collector"
            },
            "data": []
        }


class ErrorCollector(BaseCollector):
    """測試錯誤處理"""

    def get_data_type(self) -> str:
        return "error"

    def collect(self) -> dict:
        """模擬錯誤"""
        raise Exception("模擬收集錯誤")


def test_dummy_collector():
    """測試正常收集"""
    print("=" * 60)
    print("測試 1: 正常收集資料")
    print("=" * 60)

    collector = DummyCollector("2024-12-27")
    result = collector.run()

    print(f"\n結果: {result}")
    assert result['status'] == 'success'
    assert result['records'] == 5
    print("✅ 測試通過\n")


def test_empty_collector():
    """測試無資料情況"""
    print("=" * 60)
    print("測試 2: 無資料收集")
    print("=" * 60)

    collector = EmptyCollector("2024-12-27")
    result = collector.run()

    print(f"\n結果: {result}")
    assert result['status'] == 'no_data'
    print("✅ 測試通過\n")


def test_error_collector():
    """測試錯誤處理"""
    print("=" * 60)
    print("測試 3: 錯誤處理")
    print("=" * 60)

    collector = ErrorCollector("2024-12-27")
    result = collector.run()

    print(f"\n結果: {result}")
    assert result['status'] == 'error'
    assert '模擬收集錯誤' in result['error']
    print("✅ 測試通過\n")


if __name__ == "__main__":
    print("\n🧪 測試 BaseCollector 架構\n")

    try:
        test_dummy_collector()
        test_empty_collector()
        test_error_collector()

        print("=" * 60)
        print("🎉 所有測試通過！BaseCollector 架構正常運作")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ 測試失敗: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 執行錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
