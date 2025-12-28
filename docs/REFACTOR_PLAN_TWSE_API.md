# Refactor 計畫：改用台灣證交所官方 API

## 📋 重構概述

**目標**: 將資料來源從 FinMind API 改為台灣證交所與櫃買中心官方 API

**原因**:
- FinMind 免費版無法取得近 30 天資料（需付費升級）
- 官方 API 免費、即時、資料最準確
- 減少對第三方服務的依賴

**影響範圍**:
- 資料收集器 (Collectors)
- API 呼叫邏輯
- 資料欄位對應
- 錯誤處理機制

---

## 🎯 Phase 1 資料來源對應

### 官方 API 資源清單

#### 1. 台灣證券交易所 (TWSE) - 上市股票

| 資料類型 | API 端點 | 說明 |
|---------|---------|------|
| 每日價量 | `https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL` | 當日所有上市股票成交資訊 |
| 三大法人 | `https://openapi.twse.com.tw/v1/exchangeReport/TWT38U` | 三大法人買賣超日報 |
| 融資融券 | `https://openapi.twse.com.tw/v1/exchangeReport/MI_MARGN` | 信用交易統計 |
| 借券賣出 | `https://openapi.twse.com.tw/v1/exchangeReport/TWT93U` | 借券賣出餘額 |
| 股票清單 | `https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL` | 從當日成交資訊提取 |

#### 2. 證券櫃買中心 (TPEx) - 上櫃股票

| 資料類型 | API 端點 | 說明 |
|---------|---------|------|
| 每日價量 | `https://www.tpex.org.tw/openapi/v1/tpex_mainboard_quotes` | 上櫃股票行情 |
| 三大法人 | `https://www.tpex.org.tw/openapi/v1/tpex_mainboard_peratio` | 含法人資訊 |
| 股票清單 | `https://www.tpex.org.tw/openapi/v1/tpex_mainboard_quotes` | 從行情提取 |

**API 特性**:
- ✅ 完全免費，無請求限制
- ✅ 即時更新（交易日收盤後約 30 分鐘）
- ✅ JSON 格式，易於解析
- ✅ 官方來源，資料最準確
- ⚠️ 需分別查詢上市/上櫃
- ⚠️ 欄位名稱與 FinMind 不同

---

## 🏗️ 重構架構設計

### 新架構：Multi-Source Collector Pattern

```
src/
├── collectors/
│   ├── base_collector.py           # 保持不變
│   ├── price_collector.py          # 重構 ⚠️
│   ├── institutional_collector.py  # 重構 ⚠️
│   ├── margin_collector.py         # 重構 ⚠️
│   └── lending_collector.py        # 重構 ⚠️
├── datasources/                    # 新增 ✨
│   ├── __init__.py
│   ├── base_datasource.py          # 資料源基礎類別
│   ├── finmind_datasource.py       # FinMind 資料源（保留作為備用）
│   ├── twse_datasource.py          # TWSE 官方 API 資料源
│   └── tpex_datasource.py          # TPEx 官方 API 資料源
└── utils/
    ├── field_mapper.py             # 新增：欄位對應工具 ✨
    └── data_merger.py              # 新增：資料合併工具 ✨
```

### 設計模式：Strategy Pattern

**核心概念**:
- Collector 不直接呼叫 API，而是透過 DataSource 抽象層
- 不同資料源實作相同介面
- 支援多資料源合併（上市 + 上櫃）

---

## 📝 詳細實作計畫

### Step 1: 建立資料源抽象層

#### 1.1 建立 `base_datasource.py`

```python
"""
資料源基礎類別

定義所有資料源必須實作的介面
"""
from abc import ABC, abstractmethod
from typing import Optional, List
import pandas as pd
from datetime import datetime

class BaseDataSource(ABC):
    """資料源基礎抽象類別"""

    @abstractmethod
    def get_daily_prices(
        self,
        date: str,
        stock_ids: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        取得每日價量資料

        Args:
            date: YYYY-MM-DD
            stock_ids: 股票代碼列表，None = 全部

        Returns:
            DataFrame with columns:
                - date, stock_id, open, high, low, close
                - volume, amount, transaction_count
        """
        pass

    @abstractmethod
    def get_institutional_trades(
        self,
        date: str,
        stock_ids: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        取得三大法人買賣超

        Returns:
            DataFrame with columns:
                - date, stock_id
                - foreign_buy, foreign_sell, foreign_net
                - trust_buy, trust_sell, trust_net
                - dealer_buy, dealer_sell, dealer_net
        """
        pass

    @abstractmethod
    def get_margin_trades(
        self,
        date: str,
        stock_ids: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        取得融資融券資料

        Returns:
            DataFrame with columns:
                - date, stock_id
                - margin_balance, margin_change
                - short_balance, short_change
        """
        pass

    @abstractmethod
    def get_stock_list(self) -> pd.DataFrame:
        """
        取得股票清單

        Returns:
            DataFrame with columns:
                - stock_id, stock_name, type, industry_category
        """
        pass

    @abstractmethod
    def is_available(self, date: str) -> bool:
        """
        檢查該日期資料是否可用

        Args:
            date: YYYY-MM-DD

        Returns:
            bool: True if data is available
        """
        pass
```

#### 1.2 建立 `twse_datasource.py` (TWSE 官方 API)

```python
"""
台灣證券交易所 (TWSE) 資料源

使用 TWSE OpenAPI 取得上市股票資料
"""
import requests
import pandas as pd
from typing import Optional, List
from datetime import datetime

from .base_datasource import BaseDataSource
from ..utils import get_logger

logger = get_logger(__name__)


class TWSEDataSource(BaseDataSource):
    """TWSE 官方 API 資料源"""

    BASE_URL = "https://openapi.twse.com.tw/v1"

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()

    def get_daily_prices(
        self,
        date: str,
        stock_ids: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        取得 TWSE 每日價量資料

        API: /exchangeReport/STOCK_DAY_ALL
        """
        url = f"{self.BASE_URL}/exchangeReport/STOCK_DAY_ALL"

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            if not data:
                logger.warning(f"TWSE 無資料: {date}")
                return pd.DataFrame()

            # 轉換為 DataFrame
            df = pd.DataFrame(data)

            # 欄位對應
            df = df.rename(columns={
                'Code': 'stock_id',
                'Name': 'stock_name',
                'OpeningPrice': 'open',
                'HighestPrice': 'high',
                'LowestPrice': 'low',
                'ClosingPrice': 'close',
                'TradeVolume': 'volume',
                'TradeValue': 'amount',
                'Transaction': 'transaction_count',
                'Change': 'change_price'
            })

            # 只保留 4 位數股票代碼（排除 ETF、權證等）
            df = df[df['stock_id'].str.len() == 4]
            df = df[df['stock_id'].str.isdigit()]

            # 加入日期
            df['date'] = date

            # 資料清理：移除逗號並轉換為數值
            numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount', 'transaction_count']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.replace(',', '').replace('--', '0')
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # 篩選股票
            if stock_ids:
                df = df[df['stock_id'].isin(stock_ids)]

            # 加入市場類型
            df['type'] = 'twse'

            logger.info(f"TWSE 價量資料: {len(df)} 筆 ({date})")
            return df

        except Exception as e:
            logger.error(f"TWSE API 錯誤: {e}")
            return pd.DataFrame()

    def get_institutional_trades(
        self,
        date: str,
        stock_ids: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        取得 TWSE 三大法人買賣超

        API: /exchangeReport/TWT38U
        """
        url = f"{self.BASE_URL}/exchangeReport/TWT38U"

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            if not data:
                return pd.DataFrame()

            df = pd.DataFrame(data)

            # 欄位對應 (根據實際 API 回傳調整)
            df = df.rename(columns={
                'Code': 'stock_id',
                'Name': 'stock_name',
                'ForeignInvestorBuy': 'foreign_buy',
                'ForeignInvestorSell': 'foreign_sell',
                'TrustBuy': 'trust_buy',
                'TrustSell': 'trust_sell',
                'DealerBuy': 'dealer_buy',
                'DealerSell': 'dealer_sell'
            })

            # 計算淨買賣
            df['foreign_net'] = df['foreign_buy'] - df['foreign_sell']
            df['trust_net'] = df['trust_buy'] - df['trust_sell']
            df['dealer_net'] = df['dealer_buy'] - df['dealer_sell']

            df['date'] = date
            df['type'] = 'twse'

            if stock_ids:
                df = df[df['stock_id'].isin(stock_ids)]

            logger.info(f"TWSE 法人資料: {len(df)} 筆 ({date})")
            return df

        except Exception as e:
            logger.error(f"TWSE 法人 API 錯誤: {e}")
            return pd.DataFrame()

    def get_margin_trades(
        self,
        date: str,
        stock_ids: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """取得融資融券資料"""
        # TODO: 實作 TWSE 融資融券 API
        logger.warning("TWSE 融資融券 API 尚未實作")
        return pd.DataFrame()

    def get_stock_list(self) -> pd.DataFrame:
        """
        從當日成交資料提取股票清單
        """
        today = datetime.now().strftime('%Y-%m-%d')
        df = self.get_daily_prices(today)

        if df.empty:
            return pd.DataFrame()

        stock_list = df[['stock_id', 'stock_name', 'type']].copy()
        stock_list['industry_category'] = '上市'
        stock_list['date'] = today
        stock_list['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return stock_list.drop_duplicates('stock_id')

    def is_available(self, date: str) -> bool:
        """檢查資料是否可用"""
        df = self.get_daily_prices(date)
        return not df.empty
```

#### 1.3 建立 `tpex_datasource.py` (TPEx 官方 API)

```python
"""
證券櫃買中心 (TPEx) 資料源

使用 TPEx OpenAPI 取得上櫃股票資料
"""
import requests
import pandas as pd
from typing import Optional, List
from datetime import datetime

from .base_datasource import BaseDataSource
from ..utils import get_logger

logger = get_logger(__name__)


class TPExDataSource(BaseDataSource):
    """TPEx 官方 API 資料源"""

    BASE_URL = "https://www.tpex.org.tw/openapi/v1"

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()

    def get_daily_prices(
        self,
        date: str,
        stock_ids: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        取得 TPEx 每日價量資料

        API: /tpex_mainboard_quotes
        """
        url = f"{self.BASE_URL}/tpex_mainboard_quotes"

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            if not data:
                logger.warning(f"TPEx 無資料: {date}")
                return pd.DataFrame()

            df = pd.DataFrame(data)

            # 欄位對應 (根據 TPEx API 實際欄位調整)
            df = df.rename(columns={
                'SecuritiesCompanyCode': 'stock_id',
                'CompanyName': 'stock_name',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume',
                'Value': 'amount'
            })

            # 只保留 4 位數股票代碼
            df = df[df['stock_id'].str.len() == 4]
            df = df[df['stock_id'].str.isdigit()]

            df['date'] = date
            df['type'] = 'tpex'

            # 資料清理
            numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            if stock_ids:
                df = df[df['stock_id'].isin(stock_ids)]

            logger.info(f"TPEx 價量資料: {len(df)} 筆 ({date})")
            return df

        except Exception as e:
            logger.error(f"TPEx API 錯誤: {e}")
            return pd.DataFrame()

    def get_institutional_trades(
        self,
        date: str,
        stock_ids: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """取得三大法人買賣超"""
        # TODO: 實作 TPEx 法人 API
        logger.warning("TPEx 法人 API 尚未實作")
        return pd.DataFrame()

    def get_margin_trades(
        self,
        date: str,
        stock_ids: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """取得融資融券資料"""
        # TODO: 實作 TPEx 融資融券 API
        logger.warning("TPEx 融資融券 API 尚未實作")
        return pd.DataFrame()

    def get_stock_list(self) -> pd.DataFrame:
        """從當日行情提取股票清單"""
        today = datetime.now().strftime('%Y-%m-%d')
        df = self.get_daily_prices(today)

        if df.empty:
            return pd.DataFrame()

        stock_list = df[['stock_id', 'stock_name', 'type']].copy()
        stock_list['industry_category'] = '上櫃'
        stock_list['date'] = today
        stock_list['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return stock_list.drop_duplicates('stock_id')

    def is_available(self, date: str) -> bool:
        """檢查資料是否可用"""
        df = self.get_daily_prices(date)
        return not df.empty
```

---

### Step 2: 建立資料合併工具

#### 2.1 建立 `data_merger.py`

```python
"""
資料合併工具

負責合併多個資料源（TWSE + TPEx）的資料
"""
import pandas as pd
from typing import List
from ..utils import get_logger

logger = get_logger(__name__)


class DataMerger:
    """資料合併器"""

    @staticmethod
    def merge_dataframes(
        dataframes: List[pd.DataFrame],
        deduplicate_by: str = 'stock_id'
    ) -> pd.DataFrame:
        """
        合併多個 DataFrame

        Args:
            dataframes: DataFrame 列表
            deduplicate_by: 去重欄位

        Returns:
            合併後的 DataFrame
        """
        # 過濾空 DataFrame
        valid_dfs = [df for df in dataframes if not df.empty]

        if not valid_dfs:
            logger.warning("所有 DataFrame 都是空的")
            return pd.DataFrame()

        # 合併
        merged = pd.concat(valid_dfs, ignore_index=True)

        # 去重（如果有重複的股票代碼，保留第一筆）
        if deduplicate_by and deduplicate_by in merged.columns:
            before_count = len(merged)
            merged = merged.drop_duplicates(subset=[deduplicate_by, 'date'], keep='first')
            after_count = len(merged)

            if before_count != after_count:
                logger.info(f"去重: {before_count} -> {after_count} (移除 {before_count - after_count} 筆)")

        # 排序
        if 'stock_id' in merged.columns:
            merged = merged.sort_values('stock_id').reset_index(drop=True)

        logger.info(f"合併完成: {len(merged)} 筆資料")
        return merged
```

---

### Step 3: 重構 Collector

#### 3.1 修改 `price_collector.py`

```python
"""
價格資料收集器 (重構版)

支援多資料源（TWSE + TPEx）
"""
from datetime import datetime
from typing import List, Optional, Union
import pandas as pd

from .base_collector import BaseCollector
from ..datasources import TWSEDataSource, TPExDataSource
from ..utils import get_logger, DataMerger

logger = get_logger(__name__)


class PriceCollector(BaseCollector):
    """價格資料收集器（官方 API 版本）"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # 初始化多個資料源
        self.twse_source = TWSEDataSource()
        self.tpex_source = TPExDataSource()
        self.merger = DataMerger()

    def get_data_type(self) -> str:
        return 'price'

    def collect(
        self,
        date: Union[str, datetime],
        stock_id: Optional[str] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        收集價格資料（從 TWSE + TPEx）

        Args:
            date: 收集日期
            stock_id: 股票代碼（None = 全部股票）

        Returns:
            pd.DataFrame: 合併後的價格資料（上市 + 上櫃）
        """
        date_str = self._format_date(date)
        stock_ids = [stock_id] if stock_id else None

        self.logger.info(f"收集價格資料: {date_str} (TWSE + TPEx)")

        # 從 TWSE 收集上市股票
        twse_df = self.twse_source.get_daily_prices(date_str, stock_ids)

        # 從 TPEx 收集上櫃股票
        tpex_df = self.tpex_source.get_daily_prices(date_str, stock_ids)

        # 合併
        merged_df = self.merger.merge_dataframes([twse_df, tpex_df])

        if merged_df.empty:
            self.logger.warning(f"無資料: {date_str}")
            return pd.DataFrame()

        # 資料處理
        merged_df = self._process_data(merged_df)

        self.logger.info(
            f"收集完成: {len(merged_df)} 筆 "
            f"(TWSE: {len(twse_df)}, TPEx: {len(tpex_df)})"
        )

        return merged_df

    def _process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """處理原始資料"""
        # 確保必要欄位存在
        required_cols = ['date', 'stock_id', 'open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            if col not in df.columns:
                logger.warning(f"缺少欄位: {col}")

        # 計算漲跌幅
        if 'change_price' in df.columns and 'close' in df.columns:
            df['change_rate'] = (
                df['change_price'] / (df['close'] - df['change_price'])
            ).round(4)

        # 確保數值類型
        numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 排序
        if 'stock_id' in df.columns:
            df = df.sort_values(['date', 'stock_id']).reset_index(drop=True)

        return df
```

---

### Step 4: 更新配置與相依性

#### 4.1 修改 `requirements.txt`

```txt
# 移除
# FinMind==4.1.0

# 保留其他
pandas>=2.0.0
requests>=2.31.0
tenacity>=8.2.0
python-dotenv>=1.0.0
PyYAML>=6.0.0
```

#### 4.2 更新 `config.yaml` (如果有)

```yaml
# 新增資料源配置
datasources:
  primary: official  # official | finmind

  official:
    twse:
      base_url: https://openapi.twse.com.tw/v1
      timeout: 30
    tpex:
      base_url: https://www.tpex.org.tw/openapi/v1
      timeout: 30

  # 保留 FinMind 作為備用
  finmind:
    enabled: false
    api_token: ${FINMIND_API_TOKEN}
```

---

## 🧪 測試計畫

### 測試項目

#### 1. 單元測試

```python
# tests/test_twse_datasource.py
def test_twse_get_daily_prices():
    """測試 TWSE 價量資料"""
    source = TWSEDataSource()
    df = source.get_daily_prices('2025-12-26')

    assert not df.empty
    assert 'stock_id' in df.columns
    assert 'close' in df.columns
    assert len(df) > 1000  # 上市股票應該有 1000+ 檔

def test_tpex_get_daily_prices():
    """測試 TPEx 價量資料"""
    source = TPExDataSource()
    df = source.get_daily_prices('2025-12-26')

    assert not df.empty
    assert 'stock_id' in df.columns
```

#### 2. 整合測試

```python
# tests/test_price_collector_integration.py
def test_price_collector_with_official_api():
    """測試價格收集器（官方 API）"""
    collector = PriceCollector()
    df = collector.collect('2025-12-26')

    assert not df.empty
    assert len(df) > 1800  # 上市 + 上櫃應該有 1800+ 檔

    # 確認包含測試股票
    assert '2330' in df['stock_id'].values  # 台積電（上市）
    assert '2528' in df['stock_id'].values  # 皇普（上櫃）
```

#### 3. 資料一致性測試

```bash
# 執行腳本測試
python scripts/run_collection.py --date 2025-12-26 --types price
```

---

## 📅 實作時程

| 階段 | 任務 | 預估時間 | 優先級 |
|------|------|---------|--------|
| **Phase 1** | 建立資料源抽象層 | 3h | P0 |
| | - BaseDataSource | 1h | |
| | - TWSEDataSource | 1.5h | |
| | - TPExDataSource | 0.5h | |
| **Phase 2** | 建立資料合併工具 | 1h | P0 |
| **Phase 3** | 重構 PriceCollector | 2h | P0 |
| **Phase 4** | 測試與驗證 | 2h | P0 |
| | - 單元測試 | 1h | |
| | - 整合測試 | 1h | |
| **Phase 5** | 重構其他 Collectors | 4h | P1 |
| | - InstitutionalCollector | 2h | |
| | - MarginCollector | 1h | |
| | - LendingCollector | 1h | |
| **Phase 6** | 文檔與部署 | 1h | P1 |
| **總計** | | **13h** | |

---

## ✅ 驗收標準

### 必須達成 (Must Have)

- [ ] ✅ 可收集 2025-12-26 的完整價量資料（所有上市 + 上櫃股票）
- [ ] ✅ 包含測試股票：2330 (台積電)、2528 (皇普)、2539 (櫻花建)
- [ ] ✅ 資料筆數 ≥ 1,800 檔
- [ ] ✅ 所有必要欄位完整：date, stock_id, open, high, low, close, volume
- [ ] ✅ 通過單元測試與整合測試
- [ ] ✅ 更新文檔與 README

### 應該達成 (Should Have)

- [ ] 📊 重構 InstitutionalCollector (三大法人)
- [ ] 📊 重構 MarginCollector (融資融券)
- [ ] 📊 支援錯誤降級（官方 API 失敗時使用 FinMind 備用）

### 可以達成 (Could Have)

- [ ] 💾 加入快取機制（避免重複查詢）
- [ ] 📈 效能優化（並行查詢 TWSE + TPEx）
- [ ] 🔔 Slack/Email 通知機制

---

## 🚨 風險與應對

### 風險 1: 官方 API 欄位變更

**影響**: 中
**應對**:
- 實作欄位對應 Mapper，集中管理對應關係
- 加入欄位驗證與錯誤提示

### 風險 2: 官方 API 不穩定或限流

**影響**: 中
**應對**:
- 保留 FinMind 作為備用資料源
- 實作重試機制（tenacity）
- 加入請求間隔 (rate limiting)

### 風險 3: 上市/上櫃資料格式不一致

**影響**: 低
**應對**:
- 使用統一的 DataMerger 處理合併
- 標準化欄位名稱

---

## 📚 參考資源

### 官方 API 文檔

- [TWSE OpenAPI](https://openapi.twse.com.tw/)
- [TPEx OpenAPI](https://www.tpex.org.tw/openapi/)

### 相關工具

- [requests](https://requests.readthedocs.io/)
- [pandas](https://pandas.pydata.org/)

---

**維護者**: Jason Huang
**建立日期**: 2025-12-28
**最後更新**: 2025-12-28
**版本**: 2.0
**狀態**: 🚧 進行中

---

## 🔄 最新研究結果與實作狀態（2025-12-28）

### ✅ 已完成

#### 價格資料（Price）
- ✅ TWSE 價格 API - 完全可用
- ✅ TPEx 價格 API - 完全可用
- ✅ TWSEDataSource - 已實作
- ✅ TPExDataSource - 已實作
- ✅ PriceCollector - 已重構並測試
- ✅ 測試驗證：1,946 檔股票成功收集

#### 融資融券（Margin）
- ✅ TWSE 融資融券 API - 完全可用（1,243 筆）
- ✅ TWSEMarginDataSource - 已實作 ([twse_margin_datasource.py](../src/datasources/twse_margin_datasource.py:1-166))
- ⏳ TPEx 融資融券 API - 有問題（回傳 HTML redirect）
- ⏳ TPExMarginDataSource - 待實作
- ⏳ MarginCollector - 待重構

### ⚠️ 發現的問題

#### TPEx API 問題
**現象**: 所有 TPEx OpenAPI 端點回傳 HTTP 302 redirect 並導向 HTML 頁面

**影響範圍**:
- `/tpex_margintrading_bal` - 融資融券
- `/tpex_dealer_trading` - 三大法人
- `/tpex_sbl_total` - 借券賣出

**可能原因**:
1. API 端點路徑錯誤或已棄用
2. 需要特定認證或 Cookies
3. 需要特定 Headers（User-Agent 等）
4. API 已遷移到新位置

**測試結果**:
- 無 Headers: HTML 頁面
- 瀏覽器 Headers: HTML 頁面
- curl Headers: HTML 頁面
- 各種組合: 全部失敗

#### TWSE 其他 API 狀態
- `/fund/T86` (三大法人) - 回傳空內容
- `/exchangeReport/TWT93U` (借券賣出) - 回傳空內容

**推測**: 這些端點可能需要特定參數或日期格式

### 📋 API 可用性總表

| 資料類型 | TWSE API | 狀態 | 筆數 | TPEx API | 狀態 |
|---------|----------|------|------|----------|------|
| **價格資料** | `/exchangeReport/STOCK_DAY_ALL` | ✅ | 1,075 | `/tpex_mainboard_quotes` | ✅ 871 |
| **融資融券** | `/exchangeReport/MI_MARGN` | ✅ | 1,243 | `/tpex_margintrading_bal` | ❌ HTML |
| **三大法人** | `/fund/T86` | ❌ 空 | 0 | `/tpex_dealer_trading` | ❌ HTML |
| **借券賣出** | `/exchangeReport/TWT93U` | ❌ 空 | 0 | `/tpex_sbl_total` | ❌ HTML |

---

## 🎯 實作策略調整

### 方案 A：混合模式（推薦）

對於上櫃股票，採用混合策略：
- **上市股票（TWSE）**: 使用官方 API
- **上櫃股票（TPEx）**:
  - 價格資料：官方 API ✅
  - 其他資料：保留 FinMind（暫時）或待研究

**優點**:
- 可立即獲得上市股票的全部效能提升
- 不會中斷現有服務
- 給予充足時間研究 TPEx API

**實作優先序**:
1. ✅ PriceCollector - 已完成（TWSE + TPEx）
2. 🚧 MarginCollector - 進行中（TWSE + FinMind for TPEx）
3. ⏳ InstitutionalCollector - 待研究（可能全部使用 FinMind）
4. ⏳ LendingCollector - 待研究（可能全部使用 FinMind）

### 方案 B：深入研究 TPEx

**目標**: 找到正確的 TPEx API 端點

**步驟**:
1. 分析 TPEx 網站實際請求（Browser DevTools）
2. 檢查是否有其他 API 文檔
3. 測試不同的端點路徑
4. 聯繫 TPEx 技術支援（如可行）

**時程**: 預估 4-8 小時

---

## 🔨 詳細實作清單

### Phase 1: 融資融券（Margin） - 優先

#### 1.1 上市融資融券（TWSE）✅
- [x] TWSEMarginDataSource 實作
- [x] API 測試驗證（1,243 筆）
- [x] 欄位對照表建立

#### 1.2 上櫃融資融券（TPEx）⏳
**選項 1: 混合模式（推薦）**
```python
class TPExMarginDataSource(BaseDataSource):
    def get_margin_data(self, date, stock_ids=None):
        """暫時使用 FinMind API"""
        # TODO: 待 TPEx 官方 API 問題解決後改用
        return self._fetch_from_finmind(date, stock_ids)
```

**選項 2: 繼續研究**
- 嘗試不同 API 路徑
- 檢查 TPEx 網站實際請求
- 測試其他可能的端點

#### 1.3 MarginCollector 重構
```python
class MarginCollector(BaseCollector):
    def __init__(self):
        self.twse_source = TWSEMarginDataSource()  # 官方 API
        self.tpex_source = TPExMarginDataSource()   # FinMind 或待實作
        self.merger = DataMerger()

    def collect(self, date, stock_id=None):
        # 收集上市（TWSE 官方 API）
        twse_df = self.twse_source.get_margin_data(date)

        # 收集上櫃（FinMind 暫時，或等待官方 API）
        tpex_df = self.tpex_source.get_margin_data(date)

        # 合併
        return self.merger.merge_dataframes([twse_df, tpex_df])
```

### Phase 2: 三大法人（Institutional） - 次要

#### 2.1 研究 TWSE API
- [ ] 測試 `/fund/T86` 是否需要參數
- [ ] 嘗試其他相關端點
- [ ] 檢查 API 文檔

#### 2.2 研究 TPEx API
- [ ] 解決 redirect 問題
- [ ] 找到正確端點

#### 2.3 實作策略
**暫時方案**: 全部使用 FinMind
**長期目標**: 改用官方 API（待研究完成）

### Phase 3: 借券賣出（Lending） - 最後

#### 3.1 研究階段
- [ ] TWSE `/exchangeReport/TWT93U` 測試
- [ ] TPEx endpoint 研究

#### 3.2 實作策略
**暫時方案**: 保持使用 FinMind
**長期目標**: 官方 API（優先級最低）

---

## 📊 效能提升預測

### 當前實作（混合模式）

| 資料類型 | 上市（TWSE） | 上櫃（TPEx） | 總提升 |
|---------|-------------|-------------|--------|
| **價格** | 1 req（官方） | 1 req（官方） | **973x** |
| **融資融券** | 1 req（官方） | 871 req（FinMind） | **1.4x** |
| **三大法人** | 1,075 req（FinMind） | 871 req（FinMind） | **1x** |
| **借券賣出** | 1,075 req（FinMind） | 871 req（FinMind） | **1x** |

### 理想狀態（全部官方 API）

| 資料類型 | 請求次數 | 提升倍數 |
|---------|---------|---------|
| **價格** | 2 | 973x ✅ |
| **融資融券** | 2 | 973x ⏳ |
| **三大法人** | 2 | 973x ⏳ |
| **借券賣出** | 2 | 973x ⏳ |

---

## 📁 檔案結構更新

```
src/
├── datasources/
│   ├── __init__.py
│   ├── base_datasource.py                  ✅ 已實作
│   ├── twse_datasource.py                  ✅ 已實作（價格）
│   ├── tpex_datasource.py                  ✅ 已實作（價格）
│   ├── twse_margin_datasource.py           ✅ 已實作（融資融券）
│   ├── tpex_margin_datasource.py           ⏳ 待實作（混合模式）
│   ├── twse_institutional_datasource.py    ⏳ 待研究
│   ├── tpex_institutional_datasource.py    ⏳ 待研究
│   ├── twse_lending_datasource.py          ⏳ 待研究
│   └── tpex_lending_datasource.py          ⏳ 待研究
├── collectors/
│   ├── price_collector.py                  ✅ 已重構（官方 API）
│   ├── margin_collector.py                 🚧 進行中（混合模式）
│   ├── institutional_collector.py          ⏳ 待重構
│   └── lending_collector.py                ⏳ 待重構
└── utils/
    └── data_merger.py                      ✅ 已實作
```

---

## 🚀 下一步行動

### 立即執行（今天）
1. ✅ 完成 TWSEMarginDataSource
2. 🚧 實作 TPExMarginDataSource（混合模式：使用 FinMind）
3. 🚧 重構 MarginCollector
4. 🚧 測試融資融券收集器

### 短期（本週）
5. 研究 TWSE 三大法人 API（/fund/T86）
6. 研究 TPEx redirect 問題解法
7. 決定 InstitutionalCollector 實作策略

### 中期（下週）
8. 實作 InstitutionalCollector（可能混合模式）
9. 研究借券賣出 API
10. 完善文檔與測試

---

## 📝 相關文檔

- [API 研究結果](API_RESEARCH_RESULTS.md) - 詳細測試結果
- [遷移指南](MIGRATION_GUIDE.md) - 從 FinMind 遷移到官方 API
- [重構完成報告](REFACTOR_SUMMARY.md) - 價格資料重構總結
