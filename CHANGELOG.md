# 變更日誌 (Changelog)

本文件記錄專案的所有重要變更。

## [Unreleased]

### 新增
- **主升段加速突破選股策略**（全新積極型策略）
  - 新增 `analysis/主升段加速突破/` 目錄
  - `selector.sql`：五大核心條件 + 兩層防護機制
    - 條件 A：中期趨勢不死（收盤 > MA20，MA20 ≥ MA60）
    - 條件 B：收盤創 20 日新高（脫離整理區）
    - 條件 C：失控式放量（量比 ≥ 1.5）
    - 條件 D：價格加速（當日漲幅 ≥ 4%）
    - 條件 E：收在日內高檔（收盤位置 ≥ 0.75）
    - 防護 1：排除末升段過熱股（60日漲幅 ≤ 35%）
    - 防護 2：嚴格流動性門檻（今日量 ≥ 3,000 張，20日均量 ≥ 1,500 張）
  - `generate_report.py`：自動生成選股報告（Markdown + PDF）
  - `run.sh`：快速執行 SQL 查詢
  - `run_report.sh`：一鍵生成報告
  - `README.md`：完整策略文檔（9.7 KB）
    - 策略定位：專抓「主升段第一波」，風險中高，預期勝率 40-55%，單筆報酬 10-20%
    - 與「回頭買上漲」策略的比較與切換建議
    - 實戰技巧、進場原則、停損停利策略
    - 適用情境與風險警示
- **回頭買上漲選股報告系統**
  - 新增 `generate_report.py`：自動生成 Markdown 和 PDF 報告
  - 新增 `run_report.sh`：一鍵生成報告的便捷腳本
  - 報告包含股票名稱、市場別、完整技術指標、條件檢查
  - 使用專案現有的 `markdown_to_pdf.py` 工具轉換 PDF（Chrome headless）
  - 報告儲存路徑：`analysis/reports/回頭買上漲/{日期}/`
- **SQL 優化與文檔增強**
  - `selector.sql` 加入股票名稱（JOIN stocks 表）
  - README.md 新增「SQL 執行階段詳解」章節
  - 詳細說明 params、all_indicators、enriched_data、final_data 各階段
  - 新增資料庫索引優化說明與效能提升數據
  - 新增報告生成使用說明

### 重構
- **回頭買上漲選股策略**（原「回檔買進」策略重構）
  - 目錄重新命名：`回檔買進/` → `回頭買上漲/`
  - 整合完整版 SQL 為高效能版本 (`selector.sql`)
  - 七大核心條件 + 三層防護機制
  - 效能優化：90天資料限制 + WINDOW 子句，執行時間 1-2 秒
  - 撰寫完整策略文檔（README.md），包含條件詳解、SQL 實作、案例說明
  - 移除舊版檔案（Python 腳本、舊 SQL、results 目錄）

### 已完成功能
- **Claude Code Skills**
  - `data-collect`: 資料收集操作技能
  - `data-import`: 資料匯入操作技能
  - `data-transform`: 資料轉換操作技能
- **多策略綜合分析 SQL**
  - `analysis/多策略綜合/multi_strategy_selector.sql`
- **趨勢追蹤策略 SQL**
  - `analysis/趨勢追蹤/find_bullish_stocks.sql`
- **分析推薦腳本**
  - `scripts/analyze_and_recommend.py`

### 改進
- CLAUDE.md 新增「執行腳本規範」章節
  - 強制優先使用現有腳本，禁止自行撰寫程式
  - 適用於資料收集、匯入、轉換、分析等所有操作
  - 提供執行前檢查清單與範例
- 回檔買進策略 SQL 查詢優化
  - 修正 `stock_id` 型別比較錯誤（字串 vs 整數）
  - 新增參數化日期設定（使用 CTE `params`）
  - 提升 SQL 可維護性與靈活性
- 分析腳本路徑修正與命令列參數支援
  - `pullback_buy_selector.py`: 修正專案根目錄路徑計算
  - `pullback_buy_selector.py`: 支援命令列參數傳入日期
  - `filter_recovery_stocks.py`: 修正專案根目錄路徑
  - `run_all_analysis.py`: 啟用先前跳過的分析腳本
- 分析工具文檔重構
  - 按策略分類組織（回檔買進、趨勢追蹤、多策略綜合）
  - 新增對應 SQL 查詢檔案說明
  - 提升文檔結構與可讀性

### 新增
- 新增證交所交易日曆服務 (`TradingCalendarService`)
  - 從證交所 OpenAPI 取得官方交易日曆資料
  - 支援交易日判斷、區間查詢、最近/下一個交易日查詢
  - 三層快取機制（記憶體 → 檔案 → 備援清單）
  - 查詢效能達 ~100,000 次/秒
  - 提供命令列工具 `get_trading_days.py`
  - 完整測試套件（8 個測試案例全部通過）
  - 應用於資料收集前的日期驗證

### 改進
- 重構歷史資料回補腳本 (`backfill_historical.py`)
  - 支援多種資料類型回補（price, margin, institutional, lending）
  - 從直接使用資料源改為統一使用收集器架構
  - 簡化程式碼邏輯，提升可維護性
  - 新增 `--types` 參數支援指定資料類型

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
