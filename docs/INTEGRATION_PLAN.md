# 收集腳本整合計劃

**日期**: 2025-12-28
**目標**: 建立統一的執行架構，整合現有的獨立收集腳本

---

## 📋 現況分析

### 已完成的收集腳本

| 腳本 | 資料類型 | 狀態 | 備註 |
|------|---------|------|------|
| `collect_with_official_api.py` | 價格資料 | ✅ | TWSE + TPEx |
| `collect_margin_data.py` | 融資融券 | ✅ | TWSE + TPEx |
| `collect_institutional_data.py` | 三大法人 | ✅ | TWSE + TPEx |
| `collect_lending_data.py` | 借券賣出 | ✅ | TWSE only |

### 主要問題

1. **缺乏統一入口**: 每個腳本獨立執行，無法一次收集所有資料
2. **重複程式碼**: 日期處理、檔案儲存邏輯分散在各腳本
3. **無交易日判斷**: 無法自動判斷是否為交易日
4. **缺少錯誤處理**: 沒有統一的重試機制和錯誤記錄
5. **無執行日誌**: 無法追蹤執行歷史和狀態

---

## 🎯 整合目標

### 1. 建立工具類 (Utils)

#### `src/utils/date_helper.py`
**功能**:
- 判斷是否為交易日
- 取得最近的交易日
- 日期格式轉換（西元 ↔ 民國）
- 產生日期範圍（用於回補）

**主要函數**:
```python
def is_trading_day(date: str) -> bool:
    """判斷是否為交易日"""

def get_latest_trading_day() -> str:
    """取得最近的交易日"""

def to_roc_date(date: str) -> str:
    """轉換為民國曆 (YYY/MM/DD)"""

def get_date_range(start: str, end: str) -> list:
    """產生日期範圍"""
```

**實作方式**:
- 初期: 簡單規則（排除週末、已知假日）
- 進階: 從 TWSE API 取得交易日曆

#### `src/utils/file_helper.py`
**功能**:
- 建立目錄結構
- 儲存 JSON 檔案
- 檢查檔案是否存在
- 計算檔案大小

**主要函數**:
```python
def ensure_dir(path: str) -> None:
    """確保目錄存在"""

def save_json(data: dict, file_path: str) -> None:
    """儲存 JSON 檔案"""

def file_exists(file_path: str) -> bool:
    """檢查檔案是否存在"""

def get_file_size(file_path: str) -> float:
    """取得檔案大小 (KB)"""
```

#### `src/utils/logger.py`
**功能**:
- 統一的日誌記錄
- 執行日誌儲存
- 錯誤追蹤

**主要函數**:
```python
def setup_logger(name: str) -> logging.Logger:
    """設定 logger"""

def log_collection_result(data_type: str, result: dict) -> None:
    """記錄收集結果"""
```

---

### 2. 重構收集器 (Collectors)

#### 目標結構
```
src/
├── collectors/
│   ├── __init__.py
│   ├── base.py              # 基礎收集器類別
│   ├── price_collector.py   # 價格資料收集器
│   ├── margin_collector.py  # 融資融券收集器
│   ├── institutional_collector.py  # 三大法人收集器
│   └── lending_collector.py # 借券賣出收集器
```

#### `base.py` - 基礎收集器類別
```python
class BaseCollector:
    """收集器基礎類別"""

    def __init__(self, date: str):
        self.date = date
        self.logger = setup_logger(self.__class__.__name__)

    def collect(self) -> dict:
        """收集資料（子類別必須實作）"""
        raise NotImplementedError

    def save(self, data: dict) -> str:
        """儲存資料"""
        file_path = self.get_file_path()
        save_json(data, file_path)
        return file_path

    def get_file_path(self) -> str:
        """取得檔案路徑（子類別必須實作）"""
        raise NotImplementedError

    def run(self) -> dict:
        """執行收集與儲存"""
        try:
            data = self.collect()
            if data:
                file_path = self.save(data)
                return {"status": "success", "file": file_path, "records": len(data.get('data', []))}
            else:
                return {"status": "no_data"}
        except Exception as e:
            self.logger.error(f"收集失敗: {e}")
            return {"status": "error", "error": str(e)}
```

#### 收集器重構策略

**保留核心邏輯**:
- 從現有腳本提取 `collect_*` 函數
- 保留 API 呼叫和資料解析邏輯
- 移除獨立的 `main` 區塊

**包裝為類別**:
```python
class PriceCollector(BaseCollector):
    def collect(self) -> dict:
        # 原本的 collect_twse_price() 和 collect_tpex_price() 邏輯
        twse_df = self._collect_twse()
        tpex_df = self._collect_tpex()

        return {
            "metadata": {...},
            "twse": twse_df.to_dict('records'),
            "tpex": tpex_df.to_dict('records')
        }

    def get_file_path(self) -> str:
        return f"data/raw/price/{self.date[:4]}/{self.date[5:7]}/{self.date}.json"
```

---

### 3. 統一執行腳本 (run_collection.py)

#### 架構
```python
#!/usr/bin/env python3
"""
統一資料收集執行腳本
"""
import argparse
from datetime import datetime
from src.utils.date_helper import is_trading_day, get_latest_trading_day
from src.utils.logger import setup_logger
from src.collectors.price_collector import PriceCollector
from src.collectors.margin_collector import MarginCollector
from src.collectors.institutional_collector import InstitutionalCollector
from src.collectors.lending_collector import LendingCollector

# 可用的收集器
COLLECTORS = {
    'price': PriceCollector,
    'margin': MarginCollector,
    'institutional': InstitutionalCollector,
    'lending': LendingCollector,
}

def main():
    parser = argparse.ArgumentParser(description='台股資料收集')
    parser.add_argument('--date', help='收集日期 YYYY-MM-DD (預設: 最近交易日)')
    parser.add_argument('--types', nargs='+', choices=list(COLLECTORS.keys()) + ['all'],
                       default=['all'], help='資料類型 (預設: all)')
    parser.add_argument('--force', action='store_true', help='強制執行（忽略交易日檢查）')

    args = parser.parse_args()

    # 確定收集日期
    date = args.date or get_latest_trading_day()

    # 交易日檢查
    if not args.force and not is_trading_day(date):
        print(f"⚠️  {date} 不是交易日，跳過收集")
        return

    # 確定要收集的類型
    types = list(COLLECTORS.keys()) if 'all' in args.types else args.types

    print(f"開始收集 {date} 的資料")
    print(f"資料類型: {', '.join(types)}")
    print("=" * 60)

    results = {}

    # 執行收集
    for data_type in types:
        print(f"\n收集 {data_type} 資料...")
        collector = COLLECTORS[data_type](date)
        result = collector.run()
        results[data_type] = result

        if result['status'] == 'success':
            print(f"✅ {data_type}: {result['records']} 筆")
        elif result['status'] == 'no_data':
            print(f"⚠️  {data_type}: 無資料")
        else:
            print(f"❌ {data_type}: {result.get('error', '未知錯誤')}")

    # 總結
    print("\n" + "=" * 60)
    success = sum(1 for r in results.values() if r['status'] == 'success')
    print(f"完成: {success}/{len(types)} 項成功")

if __name__ == "__main__":
    main()
```

#### 使用範例
```bash
# 收集所有資料（最近交易日）
python scripts/run_collection.py

# 收集特定日期
python scripts/run_collection.py --date 2024-12-27

# 只收集特定類型
python scripts/run_collection.py --types price margin

# 強制執行（非交易日）
python scripts/run_collection.py --date 2024-12-28 --force
```

---

## 🚀 實作步驟

### Step 1: 建立工具類 (2-3 小時)
1. ✅ 建立 `src/utils/__init__.py`
2. ✅ 實作 `date_helper.py` (交易日判斷)
3. ✅ 實作 `file_helper.py` (檔案操作)
4. ✅ 實作 `logger.py` (日誌記錄)

### Step 2: 建立收集器架構 (1-2 小時)
1. ✅ 建立 `src/collectors/__init__.py`
2. ✅ 實作 `base.py` (基礎類別)
3. ⚠️ 測試基礎架構

### Step 3: 重構現有收集器 (3-4 小時)
1. ✅ 重構 `price_collector.py`
   - 提取 `collect_with_official_api.py` 邏輯
   - 包裝為 `PriceCollector` 類別

2. ✅ 重構 `margin_collector.py`
   - 提取 `collect_margin_data.py` 邏輯
   - 包裝為 `MarginCollector` 類別

3. ✅ 重構 `institutional_collector.py`
   - 提取 `collect_institutional_data.py` 邏輯
   - 包裝為 `InstitutionalCollector` 類別

4. ✅ 重構 `lending_collector.py`
   - 提取 `collect_lending_data.py` 邏輯
   - 包裝為 `LendingCollector` 類別

### Step 4: 建立統一執行腳本 (1 小時)
1. ✅ 實作 `run_collection.py`
2. ✅ 加入命令列參數處理
3. ✅ 整合所有收集器

### Step 5: 測試與驗證 (1-2 小時)
1. ⚠️ 測試單一收集器
2. ⚠️ 測試完整流程
3. ⚠️ 測試錯誤處理
4. ⚠️ 驗證資料完整性

### Step 6: 更新 GitHub Actions (1 小時)
1. ⚠️ 修改 `daily-collection.yml` 使用新腳本
2. ⚠️ 修改 `backfill.yml` 使用新腳本
3. ⚠️ 測試自動化流程

---

## 📂 最終目錄結構

```
tw-stock-collector/
├── src/
│   ├── __init__.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── date_helper.py    # 日期工具
│   │   ├── file_helper.py    # 檔案工具
│   │   └── logger.py         # 日誌工具
│   └── collectors/
│       ├── __init__.py
│       ├── base.py           # 基礎收集器
│       ├── price_collector.py
│       ├── margin_collector.py
│       ├── institutional_collector.py
│       └── lending_collector.py
├── scripts/
│   ├── run_collection.py     # 主執行腳本 ⭐
│   ├── collect_*.py          # 舊腳本（保留作為參考）
│   └── test_*.py             # 測試腳本
├── data/
│   ├── raw/                  # 原始資料
│   └── logs/                 # 執行日誌
└── docs/
    └── INTEGRATION_PLAN.md   # 本文件
```

---

## ✅ 成功標準

整合完成後應達成:

1. **統一入口**: 使用 `run_collection.py` 一次收集所有資料
2. **自動判斷**: 自動識別交易日，非交易日跳過
3. **錯誤處理**: 單一收集器失敗不影響其他收集器
4. **日誌完整**: 所有執行結果都有記錄
5. **向後相容**: 舊的獨立腳本仍可運行（保留作為備份）

---

## 🔄 遷移策略

### 保留舊腳本
- 將現有的 `collect_*.py` 移至 `scripts/legacy/`
- 作為參考和備份
- 逐步淘汰

### 測試新架構
- 先在本地環境完整測試
- 確認所有資料類型正常運作
- 驗證檔案路徑和格式一致

### GitHub Actions 更新
- 逐步更新工作流程
- 先測試手動觸發
- 確認穩定後啟用定時執行

---

**預估總時間**: 9-13 小時

**優先級**: 🔥 高（整合後才能有效率地新增其他資料收集器）
