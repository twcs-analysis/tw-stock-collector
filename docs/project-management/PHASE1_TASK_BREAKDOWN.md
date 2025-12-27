# Phase 1: 資料擷取與儲存 - 任務拆解

**專案階段**: Phase 1 - Data Collection
**目標**: 建立自動化的台股資料收集系統,透過 GitHub Actions 定期收集並儲存至 Git 倉庫
**預估時間**: 2-3 週
**最後更新**: 2025-12-28

---

## 📋 任務總覽

| 模組 | 任務數 | 預估時間 | 優先級 | 狀態 |
|------|-------|---------|-------|------|
| 專案基礎建設 | 5 | 0.5 天 | P0 | ✅ 完成 |
| 工具模組 (utils) | 5 | 1 天 | P0 | ⏳ 待開始 |
| 收集器模組 (collectors) | 7 | 3 天 | P0 | ⏳ 待開始 |
| 執行腳本 (scripts) | 4 | 1 天 | P0 | ⏳ 待開始 |
| GitHub Actions | 3 | 0.5 天 | P1 | ⏳ 待開始 |
| 測試與文檔 | 3 | 1 天 | P1 | ⏳ 待開始 |
| **總計** | **27** | **7 天** | - | **4%** |

---

## 🏗️ 模組 1: 專案基礎建設

### ✅ 1.1 目錄結構建立
**狀態**: 完成
**負責**: Claude
**時間**: 已完成

- [x] 創建 `src/` 目錄結構
- [x] 創建 `scripts/` 目錄
- [x] 創建 `data/` 目錄結構
- [x] 創建 `logs/` 目錄
- [x] 創建 `config/` 目錄

**產出**:
```
tw-stock-collector/
├── src/
│   ├── __init__.py
│   ├── collectors/
│   │   └── __init__.py
│   └── utils/
│       └── __init__.py
├── scripts/
│   └── __init__.py
├── data/
│   ├── raw/
│   └── stock_list.csv (待產生)
├── logs/
└── config/
    ├── config.yaml
    └── logging.yaml
```

### ✅ 1.2 Docker 與 CI/CD 基礎建設
**狀態**: 完成
**時間**: 已完成

- [x] 建立 Dockerfile
- [x] 建立 docker-compose (分階段)
- [x] 建立資料庫初始化腳本
- [x] 建立 GitHub Actions docker-build-push workflow

### ⏳ 1.3 配置檔案設計
**狀態**: 待開始
**預估**: 0.5 小時
**優先級**: P0

**任務**:
- [ ] 設計 `config/config.yaml` 結構
- [ ] 設計 `config/logging.yaml` 日誌配置
- [ ] 建立 `.env.example` 環境變數範本

**config.yaml 結構**:
```yaml
# FinMind API 設定
finmind:
  api_token: ${FINMIND_API_TOKEN}
  request_timeout: 30
  retry_times: 3
  retry_delay: 10
  request_interval: 0.1  # 每次請求間隔 (秒)

# 資料收集設定
collection:
  start_date: "2020-01-01"  # 歷史資料起始日期
  stock_list_file: "data/stock_list.csv"
  batch_size: 100  # 批次處理大小

# 資料儲存設定
storage:
  base_path: "data/raw"
  format: "json"  # json 或 csv
  compression: false  # 是否壓縮

# 日誌設定
logging:
  level: "INFO"
  file: "logs/collector.log"
  max_bytes: 10485760  # 10MB
  backup_count: 5
  console: true
```

**deliverables**:
- `config/config.yaml`
- `config/logging.yaml`
- `.env.example`

---

## 🛠️ 模組 2: 工具模組 (src/utils)

### ⏳ 2.1 日誌系統 (logger.py)
**狀態**: 待開始
**預估**: 2 小時
**優先級**: P0
**依賴**: 1.3 配置檔案

**任務**:
- [ ] 實作 `setup_logger()` 函數
- [ ] 支援檔案與 console 雙輸出
- [ ] 支援日誌輪轉 (rotation)
- [ ] 支援不同級別的 logger

**功能需求**:
```python
# src/utils/logger.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name, log_file, level=logging.INFO):
    """設定 logger"""
    pass

def get_logger(name):
    """取得 logger 實例"""
    pass

# 使用範例
logger = get_logger('collector.price')
logger.info("開始收集價量資料")
logger.error("收集失敗", exc_info=True)
```

**測試**:
- [ ] 測試日誌檔案建立
- [ ] 測試日誌輪轉
- [ ] 測試不同級別輸出

### ⏳ 2.2 配置管理 (config.py)
**狀態**: 待開始
**預估**: 1.5 小時
**優先級**: P0
**依賴**: 1.3 配置檔案

**任務**:
- [ ] 實作 `load_config()` 讀取 YAML 配置
- [ ] 實作環境變數替換 (`${VAR}` 語法)
- [ ] 實作配置驗證
- [ ] 實作 Singleton 模式

**功能需求**:
```python
# src/utils/config.py
import yaml
import os

class Config:
    """配置管理器 (Singleton)"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.load()
        return cls._instance

    def load(self, config_path='config/config.yaml'):
        """載入配置"""
        pass

    def get(self, key, default=None):
        """取得配置值"""
        pass

# 使用範例
config = Config()
api_token = config.get('finmind.api_token')
retry_times = config.get('finmind.retry_times', 3)
```

**測試**:
- [ ] 測試 YAML 載入
- [ ] 測試環境變數替換
- [ ] 測試 Singleton 模式
- [ ] 測試缺少必要配置時拋出錯誤

### ⏳ 2.3 檔案處理 (file_handler.py)
**狀態**: 待開始
**預估**: 2 小時
**優先級**: P0

**任務**:
- [ ] 實作 `save_json()` 儲存 JSON
- [ ] 實作 `save_csv()` 儲存 CSV
- [ ] 實作 `load_json()` 讀取 JSON
- [ ] 實作 `ensure_dir()` 確保目錄存在
- [ ] 實作檔案壓縮功能 (選用)

**功能需求**:
```python
# src/utils/file_handler.py
import json
import pandas as pd
from pathlib import Path

def save_json(data, file_path, ensure_dir=True):
    """儲存 JSON 檔案"""
    pass

def save_csv(df, file_path, ensure_dir=True):
    """儲存 CSV 檔案"""
    pass

def load_json(file_path):
    """讀取 JSON 檔案"""
    pass

def ensure_dir(dir_path):
    """確保目錄存在"""
    pass

def get_data_path(data_type, date, stock_id=None):
    """產生資料檔案路徑"""
    # 範例: data/raw/price/2025/01/20250128/2330.json
    pass
```

**測試**:
- [ ] 測試 JSON 儲存與讀取
- [ ] 測試 CSV 儲存
- [ ] 測試自動建立目錄
- [ ] 測試路徑產生邏輯

### ⏳ 2.4 資料驗證 (validator.py)
**狀態**: 待開始
**預估**: 2 小時
**優先級**: P1

**任務**:
- [ ] 實作欄位驗證
- [ ] 實作資料範圍驗證
- [ ] 實作完整性檢查
- [ ] 實作異常值檢測

**功能需求**:
```python
# src/utils/validator.py
import pandas as pd

class DataValidator:
    """資料驗證器"""

    def validate_price_data(self, df):
        """驗證價量資料"""
        # 檢查必要欄位
        # 檢查價格範圍 (open, high, low, close > 0)
        # 檢查 high >= low
        # 檢查 volume >= 0
        pass

    def validate_institutional_data(self, df):
        """驗證法人資料"""
        pass

    def check_completeness(self, df, expected_count):
        """檢查完整性"""
        pass

# 使用範例
validator = DataValidator()
is_valid, errors = validator.validate_price_data(price_df)
if not is_valid:
    logger.warning(f"資料驗證失敗: {errors}")
```

**測試**:
- [ ] 測試欄位驗證
- [ ] 測試數值範圍檢查
- [ ] 測試異常資料檢測

### ⏳ 2.5 股票清單管理 (stock_list.py)
**狀態**: 待開始
**預估**: 2 小時
**優先級**: P0

**任務**:
- [ ] 實作 `fetch_stock_list()` 取得所有台股
- [ ] 實作 `filter_stock_list()` 篩選股票
- [ ] 實作 `update_stock_list()` 更新清單
- [ ] 實作 `load_stock_list()` 讀取本地清單

**功能需求**:
```python
# src/utils/stock_list.py
from FinMind.data import DataLoader
import pandas as pd

class StockListManager:
    """股票清單管理器"""

    def __init__(self):
        self.dl = DataLoader()
        self.stock_list_file = 'data/stock_list.csv'

    def fetch_all_stocks(self):
        """從 FinMind 取得所有股票"""
        pass

    def filter_stocks(self, all_stocks):
        """篩選股票 (只保留普通股票和 ETF)"""
        pass

    def update_stock_list(self):
        """更新股票清單並記錄變更"""
        pass

    def load_stock_list(self):
        """讀取本地股票清單"""
        pass

    def get_active_stocks(self):
        """取得活躍股票清單"""
        pass

# 使用範例
manager = StockListManager()
manager.update_stock_list()  # 更新清單
stocks = manager.get_active_stocks()  # 取得清單
```

**測試**:
- [ ] 測試股票清單獲取
- [ ] 測試篩選邏輯
- [ ] 測試清單更新與差異檢測

---

## 📡 模組 3: 收集器模組 (src/collectors)

### ⏳ 3.1 基礎收集器 (base_collector.py)
**狀態**: 待開始
**預估**: 3 小時
**優先級**: P0
**依賴**: 2.1, 2.2, 2.3

**任務**:
- [ ] 實作 `BaseCollector` 抽象基類
- [ ] 實作 FinMind API 初始化
- [ ] 實作錯誤重試機制 (使用 tenacity)
- [ ] 實作請求限速 (rate limiting)
- [ ] 實作收集進度追蹤

**功能需求**:
```python
# src/collectors/base_collector.py
from abc import ABC, abstractmethod
from FinMind.data import DataLoader
from tenacity import retry, stop_after_attempt, wait_fixed
import time

class BaseCollector(ABC):
    """收集器基類"""

    def __init__(self, api_token=None):
        self.dl = DataLoader()
        if api_token:
            self.dl.login_by_token(api_token=api_token)

        self.logger = get_logger(self.__class__.__name__)
        self.config = Config()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(10))
    def fetch_data(self, *args, **kwargs):
        """帶重試的資料獲取"""
        pass

    @abstractmethod
    def collect(self, date, stock_id=None):
        """收集資料 (子類必須實作)"""
        pass

    def save(self, data, file_path):
        """儲存資料"""
        pass

    def validate(self, data):
        """驗證資料"""
        pass
```

**測試**:
- [ ] 測試 API 初始化
- [ ] 測試重試機制
- [ ] 測試請求限速

### ⏳ 3.2 價量資料收集器 (price_collector.py)
**狀態**: 待開始
**預估**: 3 小時
**優先級**: P0
**依賴**: 3.1

**任務**:
- [ ] 繼承 `BaseCollector`
- [ ] 實作單一股票收集
- [ ] 實作批次股票收集
- [ ] 實作資料儲存 (依日期/股票代碼分層)

**功能需求**:
```python
# src/collectors/price_collector.py
class PriceCollector(BaseCollector):
    """價量資料收集器"""

    def collect_single(self, stock_id, date):
        """收集單一股票的價量資料"""
        data = self.dl.taiwan_stock_daily(
            stock_id=stock_id,
            start_date=date,
            end_date=date
        )

        # 驗證
        if not self.validate(data):
            return None

        # 儲存
        file_path = get_data_path('price', date, stock_id)
        self.save(data, file_path)

        return data

    def collect_batch(self, stock_list, date):
        """批次收集多檔股票"""
        results = []
        total = len(stock_list)

        for idx, stock_id in enumerate(stock_list):
            self.logger.info(f"[{idx+1}/{total}] 收集 {stock_id}")

            try:
                data = self.collect_single(stock_id, date)
                results.append((stock_id, 'success', data))
                time.sleep(self.config.get('finmind.request_interval', 0.1))
            except Exception as e:
                self.logger.error(f"收集失敗 {stock_id}: {e}")
                results.append((stock_id, 'failed', None))

        return results

    def collect(self, date, stock_id=None):
        """收集資料 (實作抽象方法)"""
        if stock_id:
            return self.collect_single(stock_id, date)
        else:
            stock_list = load_stock_list()
            return self.collect_batch(stock_list, date)
```

**檔案結構**:
```
data/raw/price/
├── 2025/
│   └── 01/
│       └── 20250128/
│           ├── 2330.json
│           ├── 2317.json
│           └── ...
```

**測試**:
- [ ] 測試單一股票收集
- [ ] 測試批次收集
- [ ] 測試檔案儲存路徑
- [ ] 測試錯誤處理

### ⏳ 3.3 法人買賣收集器 (institutional_collector.py)
**狀態**: 待開始
**預估**: 2 小時
**優先級**: P0
**依賴**: 3.1

**任務**:
- [ ] 實作總表收集 (一次取得所有股票)
- [ ] 實作資料儲存

**功能需求**:
```python
# src/collectors/institutional_collector.py
class InstitutionalCollector(BaseCollector):
    """法人買賣收集器"""

    def collect(self, date, stock_id=None):
        """收集法人買賣資料 (使用總表)"""

        # 不帶 stock_id 參數,一次取得所有股票
        data = self.dl.taiwan_stock_institutional_investors(date=date)

        if data.empty:
            self.logger.warning(f"無法取得 {date} 的法人資料")
            return None

        # 儲存總表
        file_path = f"data/raw/institutional/{date[:4]}/{date[5:7]}/{date}.json"
        self.save(data, file_path)

        self.logger.info(f"收集 {len(data)} 筆法人資料")
        return data
```

**檔案結構**:
```
data/raw/institutional/
└── 2025/
    └── 01/
        ├── 2025-01-28.json  # 包含所有股票
        └── 2025-01-29.json
```

**測試**:
- [ ] 測試總表收集
- [ ] 測試資料完整性

### ⏳ 3.4 融資融券收集器 (margin_collector.py)
**狀態**: 待開始
**預估**: 1.5 小時
**優先級**: P0
**依賴**: 3.1

**任務**: 同 3.3 (使用總表 API)

### ⏳ 3.5 借券收集器 (lending_collector.py)
**狀態**: 待開始
**預估**: 1.5 小時
**優先級**: P0
**依賴**: 3.1

**任務**: 同 3.3 (使用總表 API)

### ⏳ 3.6 外資持股收集器 (foreign_holding_collector.py)
**狀態**: 待開始
**預估**: 2 小時
**優先級**: P1
**依賴**: 3.1

**任務**: 需逐檔收集 (無總表 API)

### ⏳ 3.7 股權分散收集器 (shareholding_collector.py)
**狀態**: 待開始
**預估**: 2 小時
**優先級**: P1
**依賴**: 3.1

**任務**: 需逐檔收集,每週更新

---

## 🚀 模組 4: 執行腳本 (scripts/)

### ⏳ 4.1 股票清單初始化 (init_stock_list.py)
**狀態**: 待開始
**預估**: 1 小時
**優先級**: P0
**依賴**: 2.5

**任務**:
- [ ] 實作股票清單初始化腳本
- [ ] 支援命令列參數

**功能需求**:
```python
# scripts/init_stock_list.py
"""
初始化股票清單

使用方式:
    python scripts/init_stock_list.py
    python scripts/init_stock_list.py --output data/stock_list.csv
"""

import argparse
from src.utils.stock_list import StockListManager

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='data/stock_list.csv')
    args = parser.parse_args()

    manager = StockListManager()
    manager.update_stock_list()

    print(f"股票清單已儲存至 {args.output}")

if __name__ == '__main__':
    main()
```

### ⏳ 4.2 每日資料收集 (run_collection.py)
**狀態**: 待開始
**預估**: 3 小時
**優先級**: P0
**依賴**: 3.2, 3.3, 3.4, 3.5

**任務**:
- [ ] 整合所有收集器
- [ ] 實作命令列參數 (日期、資料類型等)
- [ ] 實作收集報告
- [ ] 實作失敗重試

**功能需求**:
```python
# scripts/run_collection.py
"""
每日資料收集腳本

使用方式:
    python scripts/run_collection.py --date 2025-01-28
    python scripts/run_collection.py --date today
    python scripts/run_collection.py --date today --types price,institutional
"""

import argparse
from datetime import datetime, timedelta
from src.collectors.price_collector import PriceCollector
from src.collectors.institutional_collector import InstitutionalCollector
# ... 其他 collectors

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', default='today')
    parser.add_argument('--types', default='all')  # all, price, institutional, etc.
    args = parser.parse_args()

    # 處理日期
    if args.date == 'today':
        date = datetime.now().strftime('%Y-%m-%d')
    elif args.date == 'yesterday':
        date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        date = args.date

    # 初始化收集器
    collectors = {
        'price': PriceCollector(),
        'institutional': InstitutionalCollector(),
        'margin': MarginCollector(),
        'lending': LendingCollector(),
    }

    # 執行收集
    results = {}
    for name, collector in collectors.items():
        if args.types == 'all' or name in args.types.split(','):
            print(f"\n收集 {name} 資料...")
            try:
                data = collector.collect(date=date)
                results[name] = {'status': 'success', 'records': len(data) if data is not None else 0}
            except Exception as e:
                results[name] = {'status': 'failed', 'error': str(e)}

    # 產生報告
    generate_report(date, results)

if __name__ == '__main__':
    main()
```

### ⏳ 4.3 歷史資料回補 (backfill.py)
**狀態**: 待開始
**預估**: 2 小時
**優先級**: P1
**依賴**: 4.2

**任務**:
- [ ] 實作日期範圍收集
- [ ] 實作進度追蹤與中斷恢復

**功能需求**:
```python
# scripts/backfill.py
"""
歷史資料回補

使用方式:
    python scripts/backfill.py --start 2024-01-01 --end 2024-12-31
    python scripts/backfill.py --start 2024-01-01 --end 2024-12-31 --types price
"""
```

### ⏳ 4.4 收集報告產生 (generate_report.py)
**狀態**: 待開始
**預估**: 1 小時
**優先級**: P1

**任務**:
- [ ] 產生 JSON 格式報告
- [ ] 產生 Markdown 格式報告
- [ ] 統計收集成功率

---

## 🔄 模組 5: GitHub Actions

### ⏳ 5.1 每日收集 workflow
**狀態**: 待開始
**預估**: 1 小時
**優先級**: P1
**依賴**: 4.2

**檔案**: `.github/workflows/daily-collection.yml`

**任務**:
- [ ] 設定 cron 排程 (每交易日 18:00)
- [ ] 執行資料收集
- [ ] Commit 並 Push 資料
- [ ] 失敗通知

### ⏳ 5.2 每週收集 workflow
**狀態**: 待開始
**預估**: 0.5 小時
**優先級**: P1

**任務**:
- [ ] 股權分散表收集 (每週六)
- [ ] 股票清單更新

### ⏳ 5.3 手動回補 workflow
**狀態**: 待開始
**預估**: 0.5 小時
**優先級**: P2

**任務**:
- [ ] 支援手動觸發
- [ ] 支援日期範圍輸入

---

## 🧪 模組 6: 測試與文檔

### ⏳ 6.1 單元測試
**狀態**: 待開始
**預估**: 3 小時
**優先級**: P1

**任務**:
- [ ] 工具模組測試 (utils)
- [ ] 收集器測試 (collectors)
- [ ] 測試覆蓋率 > 80%

### ⏳ 6.2 整合測試
**狀態**: 待開始
**預估**: 2 小時
**優先級**: P1

**任務**:
- [ ] 端到端收集流程測試
- [ ] GitHub Actions 本地測試 (使用 act)

### ⏳ 6.3 使用文檔
**狀態**: 待開始
**預估**: 1 小時
**優先級**: P1

**任務**:
- [ ] 撰寫 Phase 1 使用說明
- [ ] 撰寫 API 文檔
- [ ] 撰寫故障排除指南

---

## 📅 開發時程規劃

### Week 1: 基礎建設與工具模組
- Day 1-2: 工具模組開發 (logger, config, file_handler, validator, stock_list)
- Day 3: 基礎收集器開發
- Day 4-5: 價量與籌碼收集器開發

### Week 2: 執行腳本與 GitHub Actions
- Day 1-2: 執行腳本開發 (collection, backfill, report)
- Day 3: GitHub Actions workflows
- Day 4: 測試與修正
- Day 5: 文檔撰寫與整理

### Week 3: 測試與優化
- Day 1-2: 整合測試與 bug 修正
- Day 3: 效能優化
- Day 4: 回補歷史資料測試
- Day 5: 最終驗收與文檔完善

---

## ✅ 驗收標準

### 功能驗收
- [ ] 可以成功取得並儲存股票清單
- [ ] 可以收集指定日期的所有資料類型
- [ ] 資料儲存格式正確且完整
- [ ] GitHub Actions 可以自動執行
- [ ] 錯誤處理與重試機制正常運作
- [ ] 日誌記錄完整

### 效能驗收
- [ ] 每日收集時間 < 10 分鐘
- [ ] API 請求不超過限制 (600次/分鐘)
- [ ] 儲存空間合理 (< 100MB/月)

### 品質驗收
- [ ] 測試覆蓋率 > 80%
- [ ] 無 critical bugs
- [ ] 程式碼符合 PEP 8 規範
- [ ] 文檔完整

---

## 🎯 下一步行動

**立即開始**:
1. 建立 `config/config.yaml` 和 `config/logging.yaml`
2. 實作 `src/utils/logger.py`
3. 實作 `src/utils/config.py`

**本週目標**: 完成所有工具模組

**里程碑**: Week 1 結束前完成基礎收集器

---

**專案負責人**: Jason Huang
**最後更新**: 2025-12-28
**文檔版本**: 1.0
