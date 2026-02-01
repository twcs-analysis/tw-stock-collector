# Data Transformer Service

資料轉換服務，將原始資料轉換為分析用途的衍生資料。

## 📋 功能概述

### 轉換類型

1. **Technical Analysis** (技術分析)
   - 將原始價格資料轉換為包含技術指標的分析資料
   - 計算 30+ 個技術指標
   - 支援批次轉換

## 🏗️ 架構設計

### 目錄結構

```
data-transformer/
├── app/
│   ├── __init__.py
│   ├── base_transformer.py              # 基礎轉換器類別
│   ├── technical_analysis_transformer.py # 技術分析轉換器
│   └── main.py                          # 主程式入口
├── tests/                               # 測試
├── requirements.txt                     # Python 依賴
└── README.md                            # 本文件
```

### 核心類別

#### BaseTransformer

所有轉換器的基礎類別，提供：
- 資料載入與儲存
- 轉換流程管理
- 驗證機制
- 效能監控
- 錯誤處理

#### TechnicalAnalysisTransformer

技術分析轉換器，計算以下指標：

| 類別 | 指標 | 說明 |
|------|------|------|
| 均線 | MA5, MA10, MA20, MA60, MA120, MA240 | 短中長期均線 |
| 動量 | RSI6, RSI14 | 相對強弱指標 |
| 趨勢 | MACD (DIF, DEA, Hist) | 指數平滑異同移動平均線 |
| 趨勢 | DMI (PDI, MDI, ADX, ADXR) | 趨向指標 |
| 波動 | Bollinger Bands | 布林通道 (上軌、中軌、下軌) |
| 量能 | Volume MA5, MA20, Ratio, VWAP | 成交量分析 |

## 🚀 使用方式

### 安裝依賴

```bash
cd services/data-transformer
pip install -r requirements.txt
```

### 基本用法

```bash
# 轉換指定日期的資料
python app/main.py --date 2024-12-27

# 轉換昨天的資料 (預設)
python app/main.py

# 批次轉換
python app/main.py --start 2024-01-01 --end 2024-12-31

# 指定轉換類型
python app/main.py --type technical_analysis --date 2024-12-27
```

### 進階用法

```bash
# 只轉換特定股票
python app/main.py --date 2024-12-27 --stock-id 2330

# 使用自訂配置檔
python app/main.py --date 2024-12-27 --config /path/to/config.yaml
```

## 📊 資料流程

### 輸入資料

- **來源**: `data/raw/price/YYYY/MM/YYYY-MM-DD.json`
- **格式**: JSON (包含所有股票的每日價量資料)
- **欄位**:
  ```json
  {
    "date": "2024-12-27",
    "stock_id": "2330",
    "open": 1080.0,
    "high": 1095.0,
    "low": 1075.0,
    "close": 1090.0,
    "volume": 45678912,
    "amount": 3296105464.0
  }
  ```

### 輸出資料

- **目標**: `data/transformed/technical_analysis/YYYY/MM/YYYY-MM-DD.json`
- **格式**: JSON (包含技術指標的分析資料)
- **欄位**: 原始欄位 + 30+ 個技術指標

### 轉換邏輯

1. **載入歷史資料** - 往前回溯約 550 天 (確保有 240 個交易日)
2. **按股票分組** - 每檔股票獨立計算指標
3. **計算技術指標** - 使用 pandas-ta 計算 30+ 個指標
4. **篩選目標日期** - 只保留指定日期的資料
5. **驗證與儲存** - 驗證資料完整性並儲存

## 📈 效能指標

### 處理速度

| 範圍 | 股票數 | 預估時間 |
|------|--------|---------|
| 單日 | 1,900 檔 | 10-15 秒 |
| 一個月 (20 天) | 1,900 檔 | 5-7 分鐘 |
| 一年 (240 天) | 1,900 檔 | 60-90 分鐘 |

### 資料需求

- **最少歷史天數**: 240 個交易日 (用於計算 MA240)
- **回溯天數**: 550 天 (約 1.5 年)
- **新股處理**: 上市未滿一年的股票，長期指標會是 NULL

## 🔧 配置說明

### 環境變數

```bash
# 日誌等級
export LOG_LEVEL=INFO

# 時區
export TZ=Asia/Taipei
```

### 配置檔 (YAML)

```yaml
storage:
  base_path: data/transformed
  file_format: json
  directory_structure: aggregate

validation:
  on_validation_error: warn
```

## 📝 開發指南

### 新增轉換器

1. 繼承 `BaseTransformer`
2. 實作 `transform()` 方法
3. 實作 `get_source_data_type()` 和 `get_target_data_type()`
4. 在 `main.py` 註冊新的轉換器類型

範例:

```python
from base_transformer import BaseTransformer

class MyCustomTransformer(BaseTransformer):
    def get_source_data_type(self) -> str:
        return "price"

    def get_target_data_type(self) -> str:
        return "my_custom_data"

    def transform(self, date, stock_id=None, **kwargs):
        # 載入資料
        df = self.load_source_data(date, stock_id)

        # 轉換邏輯
        # ...

        return transformed_df
```

### 測試

```bash
# 執行測試
cd services/data-transformer
pytest tests/

# 測試單一檔案
pytest tests/test_technical_analysis_transformer.py -v
```

## 🐛 常見問題

### Q: 為什麼需要載入這麼多歷史資料？

A: 計算 MA240 需要至少 240 個交易日的歷史資料。載入 550 天的資料約可涵蓋 240 個交易日 (扣除週末和國定假日)。

### Q: 新股票如何處理？

A: 上市未滿一年的股票，長期指標 (如 MA120, MA240) 會是 NULL。這是正常現象，不影響其他指標計算。

### Q: 某些指標為什麼是 NULL？

A: 技術指標需要足夠的歷史資料才能計算：
- MA5 需要 5 天
- MA240 需要 240 天
- RSI14 需要 14 天
- MACD 需要 26 天

前幾天的資料會因為歷史資料不足而顯示 NULL。

### Q: 如何提升處理速度？

A: 可以考慮以下優化：
1. 使用平行處理 (multiprocessing)
2. 快取歷史資料
3. 使用 TA-Lib (效能較好，但安裝較複雜)
4. 增量更新 (只計算新的日期)

## 📚 參考資源

- [pandas-ta Documentation](https://github.com/twopirllc/pandas-ta)
- [技術分析指標說明](https://school.stockcharts.com/doku.php?id=technical_indicators)
- [專案技術文件](../../docs/TECHNICAL_ANALYSIS_TRANSFORM.md)

## 🔗 相關服務

- [Data Collector](../data-collector/) - 原始資料收集
- [Data Importer](../data-importer/) - 資料匯入資料庫
- [Analyzer Service](../analyzer-service/) - 進階分析與回測

---

**維護者**: Jason Huang
**最後更新**: 2026-02-01
**版本**: 1.0.0
