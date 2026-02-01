# stock_analysis_daily 資料轉換方案

## 📋 概述

本文件說明如何將原始價格資料 (`data/raw/price/`) 轉換為技術分析寬表 (`stock_analysis_daily`)。

## 🎯 目標

將每日價量資料轉換為包含以下技術指標的寬表：
- 均線系統 (MA5, MA10, MA20, MA60, MA120, MA240)
- 技術指標 (RSI, MACD, DMI)
- 波動指標 (Bollinger Bands)
- 量能分析 (Volume MA, Volume Ratio, VWAP)

## 📊 資料來源

### 輸入資料
- **來源**: `data/raw/price/YYYY/MM/YYYY-MM-DD.json`
- **格式**: JSON (每日所有股票的價量資料)
- **欄位**:
  ```json
  {
    "date": "2024-12-27",
    "stock_id": "2330",
    "stock_name": "台積電",
    "open": 1080.0,
    "high": 1095.0,
    "low": 1075.0,
    "close": 1090.0,
    "volume": 45678912,
    "amount": 3296105464.0,
    "type": "twse"
  }
  ```

### 輸出資料
- **目標**: `stock_analysis_daily` 資料表
- **範圍**: 每個股票的每個交易日一筆記錄
- **技術指標**: 30+ 個欄位

## 🔧 技術方案

### 方案選擇: pandas-ta vs TA-Lib

| 比較項目 | pandas-ta | TA-Lib |
|---------|-----------|--------|
| **安裝難度** | ⭐⭐⭐⭐⭐ 簡單 (純 Python) | ⭐⭐⭐ 需編譯 |
| **依賴** | pandas, numpy | C 函式庫 + Python wrapper |
| **效能** | 中等 | 高 |
| **API 設計** | DataFrame 導向 | Array 導向 |
| **指標覆蓋** | 130+ 指標 | 150+ 指標 |
| **維護狀態** | 活躍 | 穩定但更新較慢 |

**建議**: 使用 **pandas-ta** (理由: 安裝簡單、API 友善、滿足需求)

## 📦 所需套件

```python
# 新增到 requirements.txt
pandas-ta>=0.3.14b0    # 技術分析指標計算
```

## 🏗️ 實作架構

### 1. 目錄結構

```
src/
├── transformers/              # 新增：資料轉換模組
│   ├── __init__.py
│   ├── base_transformer.py    # 基礎轉換器
│   └── technical_analysis_transformer.py  # 技術分析轉換器
└── indicators/                # 新增：技術指標計算
    ├── __init__.py
    ├── moving_average.py      # 均線計算
    ├── momentum.py            # RSI, MACD
    ├── trend.py               # DMI
    ├── volatility.py          # Bollinger Bands
    └── volume.py              # 量能分析

scripts/
└── transform_to_analysis.py   # 執行腳本
```

### 2. 核心類別設計

#### BaseTransformer (基礎轉換器)

```python
from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, List

class BaseTransformer(ABC):
    """資料轉換基礎類別"""

    def __init__(self):
        self.logger = setup_logger(__name__)

    @abstractmethod
    def load_data(self, date: str) -> pd.DataFrame:
        """載入原始資料"""
        pass

    @abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """轉換資料"""
        pass

    @abstractmethod
    def validate(self, df: pd.DataFrame) -> bool:
        """驗證轉換結果"""
        pass

    @abstractmethod
    def save(self, df: pd.DataFrame, date: str) -> None:
        """儲存轉換結果"""
        pass

    def run(self, date: str) -> bool:
        """執行完整轉換流程"""
        try:
            # 1. 載入
            df = self.load_data(date)

            # 2. 轉換
            df_transformed = self.transform(df)

            # 3. 驗證
            if not self.validate(df_transformed):
                raise ValueError("Validation failed")

            # 4. 儲存
            self.save(df_transformed, date)

            return True
        except Exception as e:
            self.logger.error(f"Transform failed: {e}")
            return False
```

#### TechnicalAnalysisTransformer (技術分析轉換器)

```python
import pandas as pd
import pandas_ta as ta
from pathlib import Path
import json

class TechnicalAnalysisTransformer(BaseTransformer):
    """技術分析轉換器 - 計算技術指標並生成分析寬表"""

    def __init__(self, data_dir: str = "data/raw/price"):
        super().__init__()
        self.data_dir = Path(data_dir)
        self.min_periods = 240  # 最少需要 240 天資料才能計算 MA240

    def load_data(self, date: str) -> pd.DataFrame:
        """
        載入指定日期及其歷史資料

        需要載入足夠的歷史資料來計算技術指標：
        - MA240 需要至少 240 天
        - 其他指標需要的天數較少

        策略: 載入過去一年的資料 (約 240 交易日)
        """
        from datetime import datetime, timedelta

        # 計算起始日期 (往前推一年半，確保有足夠交易日)
        target_date = datetime.strptime(date, "%Y-%m-%d")
        start_date = target_date - timedelta(days=550)  # 約 1.5 年

        # 收集所有歷史資料
        all_data = []
        current = start_date

        while current <= target_date:
            file_path = self.data_dir / str(current.year) / \
                       f"{current.month:02d}" / f"{current.strftime('%Y-%m-%d')}.json"

            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_data.extend(data['data'])

            current += timedelta(days=1)

        # 轉換為 DataFrame
        df = pd.DataFrame(all_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(['stock_id', 'date'])

        self.logger.info(f"Loaded {len(df)} records from {start_date.date()} to {date}")
        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        計算技術指標

        處理流程:
        1. 按股票分組
        2. 對每個股票計算指標
        3. 合併結果
        """
        result_list = []

        grouped = df.groupby('stock_id')
        total_stocks = len(grouped)

        self.logger.info(f"Processing {total_stocks} stocks...")

        for idx, (stock_id, stock_df) in enumerate(grouped, 1):
            # 只保留有足夠資料的股票
            if len(stock_df) < self.min_periods:
                self.logger.warning(
                    f"Skip {stock_id}: only {len(stock_df)} records "
                    f"(need {self.min_periods})"
                )
                continue

            # 計算技術指標
            stock_df = stock_df.copy()
            stock_df = self._calculate_indicators(stock_df)

            result_list.append(stock_df)

            if idx % 100 == 0:
                self.logger.info(f"Processed {idx}/{total_stocks} stocks")

        # 合併所有股票
        result_df = pd.concat(result_list, ignore_index=True)

        self.logger.info(f"Transform completed: {len(result_df)} records")
        return result_df

    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """計算單一股票的所有技術指標"""

        # 設定索引為日期 (pandas-ta 需要)
        df = df.set_index('date').sort_index()

        # ========================================
        # 1. 均線系統 (Moving Averages)
        # ========================================
        df['ma_5'] = ta.sma(df['close'], length=5)
        df['ma_10'] = ta.sma(df['close'], length=10)
        df['ma_20'] = ta.sma(df['close'], length=20)
        df['ma_60'] = ta.sma(df['close'], length=60)
        df['ma_120'] = ta.sma(df['close'], length=120)
        df['ma_240'] = ta.sma(df['close'], length=240)

        # ========================================
        # 2. RSI (相對強弱指標)
        # ========================================
        df['rsi_6'] = ta.rsi(df['close'], length=6)
        df['rsi_14'] = ta.rsi(df['close'], length=14)

        # ========================================
        # 3. MACD (指數平滑異同移動平均線)
        # ========================================
        macd = ta.macd(df['close'], fast=12, slow=26, signal=9)
        df['macd_dif'] = macd['MACD_12_26_9']      # DIF (快線)
        df['macd_dea'] = macd['MACDs_12_26_9']     # DEA (慢線/訊號線)
        df['macd_hist'] = macd['MACDh_12_26_9']    # Histogram (柱狀體)

        # ========================================
        # 4. DMI (趨向指標)
        # ========================================
        adx = ta.adx(df['high'], df['low'], df['close'], length=14)
        df['dmi_pdi'] = adx['DMP_14']   # +DI
        df['dmi_mdi'] = adx['DMN_14']   # -DI
        df['dmi_adx'] = adx['ADX_14']   # ADX
        df['dmi_adxr'] = adx['ADXR_14'] # ADXR

        # ========================================
        # 5. Bollinger Bands (布林通道)
        # ========================================
        bbands = ta.bbands(df['close'], length=20, std=2)
        df['bb_upper'] = bbands['BBU_20_2.0']
        df['bb_mid'] = bbands['BBM_20_2.0']
        df['bb_lower'] = bbands['BBL_20_2.0']

        # ========================================
        # 6. 成交量分析
        # ========================================
        df['vol_ma5'] = ta.sma(df['volume'], length=5)
        df['vol_ma20'] = ta.sma(df['volume'], length=20)

        # 量比 (當日量 / 5日均量)
        df['vol_ratio'] = df['volume'] / df['vol_ma5']

        # VWAP (成交量加權平均價)
        df['vwap'] = ta.vwap(df['high'], df['low'], df['close'], df['volume'])

        # ========================================
        # 重置索引，保留原始欄位
        # ========================================
        df = df.reset_index()

        # 只保留需要的欄位
        output_columns = [
            # 基礎資料
            'date', 'stock_id', 'open', 'high', 'low', 'close', 'volume', 'amount',
            # 均線
            'ma_5', 'ma_10', 'ma_20', 'ma_60', 'ma_120', 'ma_240',
            # RSI
            'rsi_6', 'rsi_14',
            # MACD
            'macd_dif', 'macd_dea', 'macd_hist',
            # DMI
            'dmi_pdi', 'dmi_mdi', 'dmi_adx', 'dmi_adxr',
            # Bollinger
            'bb_upper', 'bb_mid', 'bb_lower',
            # Volume
            'vol_ma5', 'vol_ma20', 'vol_ratio', 'vwap'
        ]

        return df[output_columns]

    def validate(self, df: pd.DataFrame) -> bool:
        """驗證轉換結果"""

        # 1. 檢查必要欄位
        required_columns = [
            'date', 'stock_id', 'close',
            'ma_5', 'ma_20', 'ma_60', 'ma_240',
            'rsi_14', 'macd_dif', 'dmi_adx', 'bb_mid', 'vol_ma20'
        ]

        missing = set(required_columns) - set(df.columns)
        if missing:
            self.logger.error(f"Missing columns: {missing}")
            return False

        # 2. 檢查資料筆數 (應該 > 0)
        if len(df) == 0:
            self.logger.error("No data in transformed DataFrame")
            return False

        # 3. 檢查是否有重複
        duplicates = df.duplicated(subset=['date', 'stock_id']).sum()
        if duplicates > 0:
            self.logger.error(f"Found {duplicates} duplicate records")
            return False

        # 4. 檢查 NULL 值比例 (允許最近幾天的指標為 NULL)
        null_ratio = df[required_columns].isnull().sum() / len(df)
        if (null_ratio > 0.3).any():
            self.logger.warning(f"High NULL ratio in some columns:\n{null_ratio[null_ratio > 0.3]}")

        self.logger.info("Validation passed")
        return True

    def save(self, df: pd.DataFrame, date: str) -> None:
        """儲存轉換結果"""
        # 目前先儲存為 CSV，後續可改為直接寫入資料庫
        output_dir = Path("data/transformed/analysis_daily")
        output_dir.mkdir(parents=True, exist_ok=True)

        # 只保留目標日期的資料
        df_target = df[df['date'] == date].copy()

        # 儲存為 CSV
        output_file = output_dir / f"{date}.csv"
        df_target.to_csv(output_file, index=False)

        self.logger.info(f"Saved {len(df_target)} records to {output_file}")
```

### 3. 執行腳本

```python
# scripts/transform_to_analysis.py

import argparse
from datetime import datetime, timedelta
from src.transformers.technical_analysis_transformer import TechnicalAnalysisTransformer
from src.utils.logger import setup_logger

def main():
    parser = argparse.ArgumentParser(description="Transform price data to technical analysis")
    parser.add_argument('--date', help='Target date (YYYY-MM-DD)', default=None)
    parser.add_argument('--start', help='Start date for batch processing')
    parser.add_argument('--end', help='End date for batch processing')

    args = parser.parse_args()
    logger = setup_logger(__name__)

    transformer = TechnicalAnalysisTransformer()

    # 單日處理
    if args.date:
        logger.info(f"Processing single date: {args.date}")
        success = transformer.run(args.date)
        exit(0 if success else 1)

    # 批次處理
    if args.start and args.end:
        start_date = datetime.strptime(args.start, "%Y-%m-%d")
        end_date = datetime.strptime(args.end, "%Y-%m-%d")

        logger.info(f"Batch processing from {args.start} to {args.end}")

        current = start_date
        success_count = 0
        failed_count = 0

        while current <= end_date:
            date_str = current.strftime("%Y-%m-%d")
            logger.info(f"Processing {date_str}...")

            if transformer.run(date_str):
                success_count += 1
            else:
                failed_count += 1

            current += timedelta(days=1)

        logger.info(f"Batch completed: {success_count} success, {failed_count} failed")
        exit(0 if failed_count == 0 else 1)

    # 預設：處理昨天的資料
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    logger.info(f"Processing yesterday: {yesterday}")
    success = transformer.run(yesterday)
    exit(0 if success else 1)

if __name__ == "__main__":
    main()
```

## 🚀 使用方式

### 安裝依賴

```bash
pip install pandas-ta>=0.3.14b0
```

### 執行轉換

```bash
# 轉換指定日期
python scripts/transform_to_analysis.py --date 2024-12-27

# 批次轉換
python scripts/transform_to_analysis.py --start 2024-01-01 --end 2024-12-31

# 轉換昨天的資料（預設）
python scripts/transform_to_analysis.py
```

### 輸出位置

- **暫存**: `data/transformed/analysis_daily/YYYY-MM-DD.csv`
- **最終**: 匯入到 `stock_analysis_daily` 資料表

## 📈 效能考量

### 計算時間估算

| 處理範圍 | 股票數 | 預估時間 |
|---------|-------|---------|
| 單日 | 1,900 檔 | 10-15 秒 |
| 一個月 | 1,900 檔 × 20 天 | 5-7 分鐘 |
| 一年 | 1,900 檔 × 240 天 | 60-90 分鐘 |

### 最佳化建議

1. **平行處理**: 使用 multiprocessing 處理不同股票
2. **增量更新**: 只計算新的日期，不重算歷史資料
3. **快取機制**: 快取歷史資料，避免重複載入
4. **批次寫入**: 累積多筆再寫入資料庫

## 🔍 資料驗證

### 檢查點

1. **完整性**: 是否有遺漏的股票或日期
2. **合理性**:
   - RSI 應在 0-100 之間
   - MA 長期線 > 短期線（多頭市場）
   - 成交量應 > 0
3. **一致性**:
   - bb_mid 應等於 ma_20
   - vol_ratio = volume / vol_ma5

### 驗證腳本

```python
def validate_analysis_data(df: pd.DataFrame) -> Dict[str, bool]:
    """驗證技術分析資料"""

    checks = {
        'rsi_range': ((df['rsi_14'] >= 0) & (df['rsi_14'] <= 100)).all(),
        'bb_mid_equals_ma20': (df['bb_mid'] - df['ma_20']).abs().max() < 0.01,
        'volume_positive': (df['volume'] > 0).all(),
        'ma_order': (df['ma_5'] is not None).all(),  # 基本檢查
    }

    return checks
```

## 📝 注意事項

### 資料需求

1. **最少資料量**: 需要至少 240 個交易日的歷史資料才能計算 MA240
2. **新股處理**: 上市未滿一年的股票，長期指標會是 NULL
3. **停牌處理**: 停牌日期需要特別處理（跳過或使用前一日收盤價）

### 技術指標說明

| 指標 | 所需天數 | NULL 處理 |
|------|---------|-----------|
| MA5 | 5 | 前 4 天為 NULL |
| MA240 | 240 | 前 239 天為 NULL |
| RSI14 | 14 | 前 13 天為 NULL |
| MACD | 26 | 前 25 天為 NULL |
| DMI | 14 | 前 13 天為 NULL |
| Bollinger | 20 | 前 19 天為 NULL |

### 股價還原

**重要**: 建議使用**還原股價** (Adjusted Close) 而非原始股價，以處理：
- 除權除息
- 股票分割
- 合併

目前資料收集器回傳的是**原始股價**，未來可考慮新增還原機制。

## 🔄 後續整合

### 與資料庫整合

```python
# 將 CSV 匯入 PostgreSQL
import psycopg2
import pandas as pd

def import_to_database(csv_file: str, conn):
    df = pd.read_csv(csv_file)

    # 使用 COPY 快速匯入
    cursor = conn.cursor()

    # 建立暫存資料
    buffer = StringIO()
    df.to_csv(buffer, index=False, header=False)
    buffer.seek(0)

    # 執行 COPY
    cursor.copy_expert(
        sql="COPY stock_analysis_daily FROM STDIN WITH CSV",
        file=buffer
    )

    conn.commit()
```

### GitHub Actions 自動化

```yaml
# .github/workflows/daily-transform.yml
name: Daily Transform to Analysis

on:
  schedule:
    - cron: '0 22 * * 1-5'  # 每交易日 22:00 執行（收集後一小時）
  workflow_dispatch:

jobs:
  transform:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Transform to analysis
        run: |
          python scripts/transform_to_analysis.py

      - name: Import to database
        run: |
          python scripts/import_to_database.py --table stock_analysis_daily
```

## 📚 參考資源

- [pandas-ta Documentation](https://github.com/twopirllc/pandas-ta)
- [技術分析指標說明](https://school.stockcharts.com/doku.php?id=technical_indicators)
- [TA-Lib Documentation](https://mrjbq7.github.io/ta-lib/)

---

**最後更新**: 2026-02-01
**狀態**: 設計完成，待實作
