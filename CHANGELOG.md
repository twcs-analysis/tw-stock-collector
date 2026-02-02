# 變更日誌 (Changelog)

本文件記錄專案的所有重要變更。

## [Unreleased]

### 修正
- 修正歷史資料收集 API 問題
  - `PriceCollector`: 新增自動判斷日期模式，歷史日期自動使用回補模式
  - `TPExDataSource`: 實作雙模式架構（即時模式 + 回補模式）
  - 回補模式使用 MI_INDEX API（TWSE）和傳統 API（TPEx）取得正確的歷史資料
  - 修正因使用 OpenAPI 導致歷史資料重複/錯誤的問題
  - 重新收集 2026-01-27 至 2026-02-02 的正確資料
  - 技術指標計算修正（RSI、MACD 等指標恢復正常）

### 移除
- 移除臨時測試腳本 `scripts/data-transformer/transform_by_month.sh`

### 新增
- 新增資料匯入服務 (`data-importer`)
  - 資料庫初始化腳本
  - 支援本地和遠端資料庫配置
  - requirements.txt 依賴管理
- 新增資料轉換服務完整實作 (`data-transformer`)
  - `TechnicalAnalysisTransformer` - 技術分析轉換器
  - `indicators.py` - 技術指標計算模組
  - `database_saver.py` - 資料庫儲存功能
  - `json_saver.py` - JSON 儲存功能
  - 完整的 requirements.txt 和測試腳本
- 新增技術分析文檔 (`docs/TECHNICAL_ANALYSIS_TRANSFORM.md`)
- 新增技術分析資料轉換功能
  - 新增 `FileHandler.load_dataframe()` 方法支援 JSON/CSV 資料載入
  - 新增 `get_logger()` 便利函數簡化 logger 使用
  - 匯出核心工具模組：`FileHandler`, `DataValidator`, `build_file_path` 等
  - 完成 2026-01 技術分析資料轉換（21 個交易日，40,845 筆記錄）
  - 計算 30+ 個技術指標（MA、RSI、MACD、DMI、布林通道、成交量指標等）
- 新增教學影片逐字稿目錄 (`transcripts/`)
  - 包含 29 集技術分析教學影片原始逐字稿
  - 建立 `raw/` 存放原始逐字稿
  - 建立 `notes/` 用於存放重點整理（29 個 Markdown 檔案）
  - 完整的主題索引與學習路徑（技術指標、K線、型態學等）
  - 每份筆記包含核心重點、實戰案例、技術分析 Prompt（4種）、延伸學習、關鍵金句
  - 提供初學者→進階→高手的學習路徑
  - 依交易週期分類（當沖、短線、波段、長線）
  - 新增 transcripts/README.md 完整使用指南
- 新增成交量前 20 名資料收集器 (`Top20VolumeCollector`)
  - 使用 TWSE OpenAPI `/exchangeReport/MI_INDEX20`
  - 收集每日成交量排名前 20 名股票資訊
  - 包含價格、成交量、成交金額等完整資訊
- 新增 TWSE API 參考文件 (`docs/TWSE_API_REFERENCE.md`)
  - 記錄 TWSE OpenAPI 143 個端點
  - 包含本專案已使用和值得收集的 API
- 新增成交量前 20 名使用說明 (`docs/TOP20_VOLUME_USAGE.md`)
  - 包含資料欄位說明、使用範例、分析範例
- 新增測試腳本 (`scripts/test_top20_volume.py`)
- 新增歷史資料回補腳本
  - `scripts/refetch_2025.sh`: 重新抓取 2025 年 1 月股價資料
  - `scripts/fetch_2025_price.sh`: 抓取 2025 年 2-12 月股價資料

### 修改
- 修正 data-transformer import 路徑
  - `main.py`: 修正 `TechnicalAnalysisTransformer` import 路徑為 `app.technical_analysis_transformer`
  - `technical_analysis_transformer.py`: 修正 `BaseTransformer` 和 `indicators` import 路徑為 `app.*`
- 修正資料收集 API 以支援歷史查詢
  - 改用支援歷史查詢的舊版 TWSE/TPEx API
  - `twse_datasource.py`: 改用 `/rwd/zh/afterTrading/MI_INDEX` API
  - `tpex_datasource.py`: 改用 `/web/stock/aftertrading/otc_quotes_no1430` API
  - `twse_margin_datasource.py`: 改用 `/marginTrading/MI_MARGN?selectType=STOCK` API
  - `tpex_margin_datasource.py`: 加入日期參數支援
  - `top20_volume_collector.py`: 改用 `/rwd/zh/afterTrading/MI_INDEX20` API
  - 加入 User-Agent headers 避免 API 封鎖
  - 修正 2024-2025 年資料收集問題（之前所有日期都返回相同資料）
- 修正 `BaseTransformer` 輸出路徑
  - 轉換後的資料儲存至 `data/transformed/` 而非 `data/raw/`
  - 新增 `output_base_path` 屬性區分原始資料與轉換資料
- 修正循環導入問題
  - `file_handler.py` 和 `validator.py` 改用 `setup_logger()` 而非 `get_logger()`
- 更新 `README.md` 加入 TWSE API 參考文件連結
- 更新 `data/README.md` 加入成交量前 20 名資料說明
- 修正 `institutional_collector.py` TPEx 資料收集的 SSL 憑證問題
  - 使用 requests 先取得 HTML 再解析，避免 pandas.read_html 的憑證錯誤
- 修正 `scripts/backfill.py` 加入 Top20VolumeCollector 支援
  - 將 top20_volume 加入預設收集類型
  - 確保歷史資料回補時包含成交量前 20 名資料

### 資料
- 回補 2024 年完整資料（全年）
  - 價格資料 (price) - 完整
  - 三大法人買賣超資料 (institutional) - 完整
  - 融資融券資料 (margin) - 完整
  - 借券賣出資料 (lending) - 完整
  - 成交量前 20 名資料 (top20_volume) - 完整
- 回補 2025 年完整資料
  - 價格資料 (price) - 1-12 月完整
  - 三大法人買賣超資料 (institutional) - 1-12 月完整
  - 融資融券資料 (margin) - 1-12 月完整
  - 借券賣出資料 (lending) - 1-12 月完整
  - 成交量前 20 名資料 (top20_volume) - 1-12 月完整
- 新增 2026-01 完整資料
  - 價格資料 (price) - 21 個交易日
  - 三大法人買賣超資料 (institutional) - 21 個交易日
  - 融資融券資料 (margin) - 21 個交易日
  - 借券賣出資料 (lending) - 21 個交易日
  - 成交量前 20 名資料 (top20_volume) - 21 個交易日
- 新增 2026-01 技術分析轉換資料
  - 位置: `data/transformed/technical_analysis/2026/01/`
  - 21 個 JSON 檔案，每個約 1.4-1.5 MB
  - 總計 40,845 筆技術分析記錄
  - 融資融券資料
  - 借券賣出資料
  - 成交量前 20 名資料

### 計劃功能
- 實作 FinMind 資料收集器
- 建立資料庫初始化腳本
- 實作每日自動排程
- 加入資料驗證機制

---

## [0.1.0] - 2025-12-28

### 新增
- 初始化專案結構
- 建立完整目錄架構
- 新增專案說明文件 (README.md)
- 新增系統規格書 (SPECIFICATION.md)
- 新增 FinMind 實作規格 (SPECIFICATION_FINMIND.md)
- 建立 Python 套件依賴清單 (requirements.txt)
- 建立配置檔範本 (config.yaml, database.yaml)
- 建立環境變數範例 (.env.example)
- 建立 .gitignore 檔案
- 建立文檔中心 (docs/)
  - API 範例目錄
  - Notebooks 目錄
  - 規格書目錄

### 目錄結構
```
tw-stock-collector/
├── config/              # 配置檔案
├── data/               # 資料檔案
├── docs/               # 文檔目錄
│   ├── api-examples/
│   ├── notebooks/
│   └── specifications/
├── logs/               # 日誌檔案
├── scripts/            # 執行腳本
├── src/                # 原始碼
│   ├── collectors/
│   ├── database/
│   ├── models/
│   ├── schedulers/
│   └── utils/
└── tests/              # 測試檔案
```

---

## 版本說明

版本號格式: `主版本.次版本.修訂號`
- **主版本**: 重大功能變更或不相容的 API 變更
- **次版本**: 新增功能且向下相容
- **修訂號**: 向下相容的問題修正

---

**維護者**: Jason Huang
