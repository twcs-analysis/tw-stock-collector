# Development Scripts

開發與測試腳本目錄，包含各種測試、驗證與研究用途的腳本。

## 📁 目錄說明

此目錄包含開發階段使用的腳本，**不應該在生產環境中使用**。

## 腳本分類

### API 測試腳本

測試證交所與櫃買中心的 API 連線與資料格式：

- `test_official_api.py` - 測試官方 API
- `test_institutional_api.py` - 測試法人 API
- `test_lending_api.py` - 測試借券 API
- `test_tpex_actual_api.py` - 測試櫃買 API
- `test_api_stocks.py` - 測試股票 API

### Collector 測試腳本

測試各類資料收集器的功能：

- `test_base_collector.py` - 測試基礎 Collector
- `test_price_collector.py` - 測試價格 Collector
- `test_refactored_collector.py` - 測試重構後的 Collector
- `test_top20_volume.py` - 測試成交量前 20 名

### 資料收集腳本 (已整合到服務中)

這些腳本已整合到 `services/data-collector`：

- `collect_institutional_data.py` - 收集法人資料
- `collect_lending_data.py` - 收集借券資料
- `collect_margin_data.py` - 收集融資融券
- `collect_with_official_api.py` - 使用官方 API 收集

### 驗證與研究腳本

資料驗證與 API 研究：

- `quick_validate.py` - 快速驗證資料
- `verify_fix.py` - 驗證修復
- `research_official_apis.py` - 研究官方 API
- `parse_tpex_margin_data.py` - 解析櫃買融資融券

### Phase 測試

階段性整合測試：

- `test_phase1.py` - Phase 1 整合測試

## 使用方式

```bash
# 進入開發腳本目錄
cd dev-scripts

# 執行特定測試腳本
python test_official_api.py

# 快速驗證資料
python quick_validate.py --date 2024-12-27
```

## 注意事項

- ⚠️ **這些腳本僅供開發測試使用**
- ⚠️ **不保證向後相容性**
- ⚠️ **可能包含過時的程式碼**
- ⚠️ **不建議在生產環境使用**

## 生產環境腳本

生產環境請使用以下服務：

- **資料收集** → `services/data-collector/`
- **資料匯入** → `services/data-importer/`
- **API 服務** → `services/api-service/`
- **分析服務** → `services/analyzer-service/`

## 維護狀態

此目錄中的腳本可能隨時更新或移除，不保證長期維護。
