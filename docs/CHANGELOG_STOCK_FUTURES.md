# 個股期貨資料收集功能 - 變更記錄

**版本**: 1.0.0
**日期**: 2026-03-15
**開發者**: Claude Sonnet 4.5

---

## 🎉 新功能：個股期貨資料收集

本次更新新增**個股期貨（Stock Futures）**每日交易資料收集功能，使用台灣期貨交易所（TAIFEX）免費 OpenAPI。

---

## 📦 新增檔案

### 核心模組

1. **資料源** - `services/common/datasources/taifex_datasource.py`
   - `TAIFEXDataSource` 類別
   - 提供 TAIFEX OpenAPI 整合
   - 包含期貨代碼與股票代碼對應功能

2. **收集器** - `services/common/collectors/stock_futures_collector.py`
   - `StockFuturesCollector` 類別
   - 繼承自 `BaseCollector`
   - 自動收集並格式化個股期貨資料

### 執行腳本

3. **Python 腳本** - `scripts/data-collector/collect_stock_futures.py`
   - 命令列介面
   - 支援指定日期收集
   - 支援驗證開關

4. **Shell 腳本** - `scripts/data-collector/collect_stock_futures.sh`
   - 簡化的執行介面
   - 自動環境檢查
   - 友善的輸出格式

### 測試工具

5. **API 測試器** - `scripts/research/test_taifex_api.py`
   - TAIFEX OpenAPI 測試工具
   - 用於驗證 API 可用性

### 文件

6. **使用指南** - `docs/STOCK_FUTURES_COLLECTION.md`
   - 完整的使用說明
   - 資料格式說明
   - 範例程式碼

7. **研究報告** - `docs/research/TAIFEX_API_RESEARCH.md`
   - TAIFEX API 完整研究
   - API 端點說明
   - 整合建議

8. **變更記錄** - `docs/CHANGELOG_STOCK_FUTURES.md`（本檔案）
   - 功能變更記錄
   - 技術細節說明

---

## 🔧 修改檔案

### 模組匯入更新

1. **`services/common/datasources/__init__.py`**
   - 新增 `TAIFEXDataSource` 匯入

2. **`services/common/collectors/__init__.py`**
   - 新增 `StockFuturesCollector` 匯入

---

## 📊 功能特性

### 資料收集
- ✅ 支援指定日期收集
- ✅ 自動取得所有個股期貨契約
- ✅ 自動對應期貨代碼與股票代碼
- ✅ 包含多個契約月份資料
- ✅ 區分一般交易與盤後交易

### 資料內容
- 📈 **交易資料**: 開高低收、成交量
- 📊 **期貨資訊**: 結算價、未平倉量
- 💰 **報價資訊**: 最佳買賣價
- 🏷️ **契約資訊**: 期貨代碼、契約月份、交易時段

### 資料格式
- 📁 JSON 格式儲存
- 📂 依年月分層目錄
- 🔖 包含 metadata 和 data
- 🏷️ 統一的資料結構

---

## 🎯 測試結果

### 測試日期：2026-03-13

#### 資料統計
- **總筆數**: 154 筆個股期貨契約
- **涵蓋股票**: 21 檔
- **標的總數**: 314 檔（TAIFEX 提供）
- **資料來源**: TAIFEX OpenAPI

#### 契約數量前 5 名
1. 台積電 (2330) - 22 個契約
2. 聯電 (2303) - 13 個契約
3. 華新 (1605) - 10 個契約
4. 友達 (2409) - 8 個契約
5. 長榮 (2603) - 7 個契約

#### 台積電期貨範例
- **近月契約 (202603)**: 收盤 1870.0, 成交量 7706 口
- **次月契約 (202604)**: 收盤 1880.0, 成交量 4693 口

---

## 🚀 使用方式

### 快速開始

```bash
# 收集今天的資料
./scripts/data-collector/collect_stock_futures.sh

# 收集指定日期的資料
./scripts/data-collector/collect_stock_futures.sh 2026-03-13
```

### Python 程式碼

```python
from services.common.collectors import StockFuturesCollector

collector = StockFuturesCollector(date='2026-03-13')
result = collector.run()

if result['status'] == 'success':
    print(f"成功收集 {result['records']} 筆資料")
```

詳細使用說明請參考：[個股期貨資料收集指南](STOCK_FUTURES_COLLECTION.md)

---

## 📁 資料儲存

### 目錄結構
```
data/raw/stock_futures/
└── 2026/
    └── 03/
        └── 2026-03-13.json
```

### 檔案格式
```json
{
  "metadata": {
    "date": "2026-03-13",
    "total_count": 154,
    "unique_stocks": 21,
    "total_contracts": 314,
    "source": "TAIFEX OpenAPI"
  },
  "data": [...]
}
```

---

## 🔍 技術細節

### API 整合
- **Base URL**: https://openapi.taifex.com.tw/v1
- **端點**: `/DailyMarketReportFut`
- **參數**: `?date=YYYY-MM-DD`
- **認證**: 無需 API Key
- **回應**: JSON 格式

### 資料處理流程
1. 呼叫 TAIFEX API 取得所有期貨資料
2. 過濾出個股期貨（Contract 開頭為 C）
3. 查詢期貨代碼對應表（`/SSFLists`）
4. 轉換資料格式為統一結構
5. 儲存為 JSON 檔案

### 期貨代碼對應
- 自動查詢 `/SSFLists` API
- 建立期貨代碼 → 股票代碼的對應
- 快取對應表避免重複查詢

---

## ⚠️ 注意事項

### 資料特性
1. 每檔股票有多個契約月份
2. 包含一般交易和盤後交易資料
3. 某些契約可能無成交量（NaN）
4. 非交易日會回傳空資料

### 與現貨差異
- 成交量單位為「口」（現貨為「股」）
- 期貨價格可能與現貨有價差
- 期貨有到期日需注意轉倉

---

## 🔗 相關資源

### 系統文件
- [TAIFEX API 研究報告](research/TAIFEX_API_RESEARCH.md)
- [個股期貨收集指南](STOCK_FUTURES_COLLECTION.md)
- [專案說明文件](../README.md)

### 官方資源
- [TAIFEX 官網](https://www.taifex.com.tw)
- [TAIFEX OpenAPI](https://openapi.taifex.com.tw/)
- [期貨交易規則](https://www.taifex.com.tw/cht/2/stockLists)

---

## 📝 未來規劃

### 短期計畫
- [ ] 新增資料驗證器（`StockFuturesValidator`）
- [ ] 整合到 `run_collection.py` 主腳本
- [ ] 新增資料庫匯入功能

### 中期計畫
- [ ] 支援歷史資料回補
- [ ] 新增技術分析指標計算
- [ ] 整合到 GitHub Actions 自動化

### 長期計畫
- [ ] 新增選擇權資料收集
- [ ] 新增三大法人期貨留倉資料
- [ ] 建立期現貨套利分析工具

---

## 🙏 致謝

感謝 TAIFEX 提供免費且完整的 OpenAPI！

---

**版本**: 1.0.0
**最後更新**: 2026-03-15
**維護者**: Claude Sonnet 4.5
