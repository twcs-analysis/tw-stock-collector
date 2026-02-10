# 變更日誌 (Changelog)

本文件記錄專案的所有重要變更。

## [Unreleased]

### 新增
- **個股營收深度分析報告**（2026-02-10）
  - 新增 `analysis/reports/個股分析/` 目錄
  - 新增 7610 聯友金屬-創營收深度分析報告
  - **報告內容**：
    - 📊 近 13 個月完整營收趨勢分析
    - 📈 年增率（YoY）與月增率（MoM）趨勢分析
    - 💡 關鍵轉折點與成長驅動因素解讀
    - ⚠️ 風險警示（低基期效應、營收波動、無 ETF 持股）
    - 🎯 投資評估與操作建議（含進場策略、風險控管）
    - 📝 SWOT 分析與總結
  - **分析發現**：
    - 連續 10 個月年增率改善（2025-02 至 2026-01）
    - 2026-01 營收創歷史新高（2.69 億元，YoY +422.68%）
    - 低基期效應顯著（2024-12/2025-01 基期異常低）
    - 營收波動大（最高/最低差 6.1 倍）
    - 風險等級：🔴 高風險
  - **用途**：用於深入研究個股營收表現，輔助投資決策

### 修正
- **Revenue Pipeline 自動計算目標月份**（2026-02-09）
  - **問題**：執行 `/revenue-pipeline` 時會收集當前月份（2026-02）資料，但該月尚無公告，導致收集 0 筆
  - **根本原因**：
    - `execute.sh` 未指定 `--year-month` 參數
    - `collect_revenue.py` 智慧判斷使用當前日期判斷模式，但沒有自動計算目標月份
    - 預設收集當前月份資料，而非上個月
  - **修正方法**：
    - 修改 `cron-automation/revenue-pipeline/execute.sh`
    - 新增自動計算邏輯：若未指定年月，自動計算為上個月（2026-02 → 2026-01）
    - 正確處理跨年情況（1月 → 上年12月）
  - **修正結果**：
    - ✅ 執行 `/revenue-pipeline` 自動收集上個月資料
    - ✅ 成功收集 1,138 檔（新增 520 檔，累計 58.7%）
    - ✅ 智慧判斷模式正常運作（9號使用 daily 模式）

### 新增
- **Revenue Pipeline 展示功能增強**（2026-02-09）
  - 修改 `cron-automation/revenue-pipeline/display_revenues.py`
  - 新增收盤價資訊（JOIN `stock_prices` 表）
  - 改為顯示今日新增的所有資料（不再隨機抽樣）
  - 前 10 檔顯示詳細資訊（含收盤價、ETF 持股）
  - 移除 `--sample` 參數（不再需要）

### 變更
- **Revenue Pipeline Skill 文檔更新**（2026-02-09）
  - 更新 `.claude/skills/revenue-pipeline/SKILL.md`
  - 更新 `.claude/skills/revenue-pipeline/instructions.md`
  - 說明自動計算目標月份機制
  - 說明展示今日新增資料功能
  - 移除 `--sample` 參數說明

### 新增
- **月營收報告自動化生成工具**（2026-02-09）
  - 新增 `analysis/ETF持股篩選/generate_reports.sh` - 自動化報告生成腳本
    - 自動計算目標月份（預設為上個月）
    - 同時生成嚴格版和寬鬆版報告
    - 自動執行 SQL 查詢並生成 Markdown
    - 使用 Python 清理 PostgreSQL 輸出格式（移除續行符號和多餘空白）
    - 自動轉換 Markdown 為 PDF（使用 md-to-pdf）
    - 輸出至 `analysis/reports/ETF持股篩選/YYYY-MM-DD/` 目錄
  - **報告內容**：
    - 篩選結果統計（符合條件股票數、創新高數量、平均增率）
    - 篩選結果明細（完整股票清單 + ETF 持股 + 最新收盤價）
    - 風險等級說明
    - 投資建議
  - **使用方式**：
    ```bash
    cd analysis/ETF持股篩選
    ./generate_reports.sh              # 使用上個月
    ./generate_reports.sh 2026-01      # 指定月份
    ```

- **月營收篩選 + ETF 持股分析系統**（2026-02-09）
  - 新增 `analysis/ETF持股篩選/月營收篩選_ETF持股_報告版_v2.sql`（嚴格版）
    - 篩選條件：連續 3 個月 YoY 遞增 + 最新月份（2026-01）仍維持正成長
    - 從資料庫讀取 ETF 持股資料（取代 hardcode）
    - 輸出 Markdown 格式報告，包含最新收盤價
  - 新增 `analysis/ETF持股篩選/月營收篩選_ETF持股_報告版_v3_寬鬆.sql`（寬鬆版）
    - 篩選條件：近三個月中任意兩個月連續 YoY 遞增
    - 擴大選股範圍，適合積極型投資者
  - 新增 `analysis/ETF持股篩選/月營收篩選_純營收版.sql`（無 ETF 限制版）
    - 不限 ETF 持股，擴大選股範圍
  - 更新 `analysis/ETF持股篩選/README.md` - 新增自動化工具使用說明
    - 版本升級至 v2.2
    - 新增自動化腳本使用方式
    - 新增嚴格版與寬鬆版差異說明
    - 新增報告輸出路徑與檔案格式說明
  - 新增 `analysis/ETF持股篩選/QUICKSTART.md` - 快速開始指南

### 變更
- **Markdown 轉 PDF 工具升級**（2026-02-09）
  - 修改 `scripts/media-tools/md_to_pdf_with_chinese.sh`
  - 從 `pandoc + weasyprint` 改用 `md-to-pdf`（基於 Puppeteer/Chrome）
  - 優點：
    - 完美支援中文（系統字體）
    - 表格格式正確（斑馬紋）
    - CSS 載入穩定
    - 無 URLError: Bad file descriptor 錯誤
  - 新增工具存在性檢查與安裝提示

### 修正
- **月營收資料 MoM 計算錯誤修正**（2026-02-09）
  - **問題**：2025-02 至 2025-11 的月增率（MoM）計算錯誤
  - **根本原因**：平行收集歷史資料時，所有月份的 `last_month_revenue` 都指向同一個月份（2024-12），而非正確的上個月
  - **影響範圍**：21,329 筆資料（11 個月 × 約 1,940 檔股票）
  - **修正方法**：
    - 建立修正腳本 `/tmp/fix_revenue_mom.py`
    - 從本地 JSON 檔案按時間順序重新計算正確的 `last_month_revenue`
    - 重新計算所有月增率 MoM 並更新資料庫
  - **修正結果**：
    - 成功更新 21,329 筆資料
    - 所有 MoM 計算已驗證正確
    - 範例：台積電 2025-02 MoM 從 -22.39% 修正為 -11.35%
  - **新增文件**：`docs/revenue_data_fixes.md` - 完整問題分析與修正報告
  - **更新文件**：`revenue_collection_status.md` - 新增問題記錄與修正狀態

### 變更
- **文檔重構：README.md 與 CLAUDE.md 精簡優化**（2026-02-08）
  - **README.md 重構**（從 573 行精簡至 399 行，精簡 31%）：
    - 移除與「快速開始」重複的「快速命令參考」章節（62 行）
    - 精簡「專案結構」章節：從 85 行縮減至 15 行，保留核心目錄
    - 精簡「資料庫架構」章節：從 52 行縮減至 20 行，移除詳細指標列表
    - 精簡「效能指標」章節：從 27 行縮減至 15 行，保留關鍵數據
    - 消除重複內容，提升閱讀體驗

  - **CLAUDE.md 重構**（從 769 行精簡至 542 行，精簡 30%）：
    - 完全移除與 README.md 重複的「專案結構」章節（60 行）
    - 移除與 README.md 重複的「效能指標」章節（17 行）
    - 精簡「常用指令」章節：從 125 行縮減至 50 行，保留關鍵範例
    - 精簡「資料結構」章節：從 57 行縮減至 25 行，移除 JSON 範例
    - 合併「開發提示」至「開發規範」章節（27 行）
    - 精簡「已知問題」章節：從 44 行縮減至 15 行
    - 精簡「常見問題」章節：從 29 行縮減至 15 行
    - 新增「Claude Skills 快速參考」章節（20 行）：列出所有可用 skills

  - **重構效益**：
    - 總計精簡 401 行（README: 174 行 + CLAUDE: 227 行）
    - 消除重複內容，保持資訊一致性
    - 保留所有關鍵環境資訊和開發規範
    - 提升文檔可讀性和維護性

### 新增
- **2025 年月營收資料收集完成**（2026-02-08）
  - ✅ 完成 2025-01 至 2025-11 共 11 個月份月營收資料收集
  - 總資料量：約 10.3 MB（21,340 筆資料，1,940 檔股票 × 11 月）
  - 資料儲存位置：`data/raw/revenue-daily/2025/`
  - 收集模式：Daily 模式（支援歷史資料查詢）
  - 資料內容：當月營收、年增率、月增率
  - 資料來源：MOPS API（逐一查詢股票）
  - 執行時間：約 2 小時 14 分鐘（平均 12 分鐘/月份）
  - 成功率：100%
  - 狀態追蹤文件：`revenue_collection_status.md`

- **月營收資料收集系統文檔更新**（2026-02-08）
  - 更新 `README.md`：
    - 新增「基本面資料」區塊，包含月營收資料說明
    - 新增月營收收集指令（Daily/Monthly 模式）
    - 更新資料目錄架構（revenue-daily/revenue-monthly）
    - 更新效能指標（月營收收集時間和資料量）
    - 新增「最新進展」區塊，記錄 2025 年月營收收集完成
  - 更新 `analysis/README.md`：新增月營收選股工具說明
  - 更新 `analysis/封關選股/README.md`：重構文檔結構
  - 新增 `revenue_collection_status.md`：詳細記錄所有月份收集狀態

- **封關選股系統 - 年線策略分析工具**（2026-02-07）
  - 新增 `analysis/封關選股/` 完整選股分析系統
  - **SQL 查詢**：
    - `年線附近選股.sql`：6 層篩選機制（年線位置、斜率、下跌趨勢、成交量、安全評分）
    - `篩選ETF成分股.sql`：從選股結果中找出 ETF 持股標的
  - **執行腳本**：`run.sh` 一鍵執行選股並產生報告
  - **技術指標匯入**：修正 `stock_analysis_daily` 表格匯入流程
  - **選股結果**（2026-02-06 封關前）：
    - 從 878 檔股票篩選出 30 檔年線附近標的
    - 完整報告：TXT、CSV、Markdown 三種格式
    - 包含停損價、目標價、安全評分、操作建議
  - **文檔**：
    - `README.md`：策略說明與使用指南
    - `QUICKSTART.md`：5 分鐘快速入門
    - `年線選股報告_2026-02-06.md`：詳細選股邏輯與投資建議
    - `年線選股清單_2026-02-06.md`：30 檔標的完整清單
  - 策略來源：錢線百分百 2026-02-07 技術面分析建議
  - 核心理念：「買在年線，睡得安穩」

- **YT Finance Show 自動化處理系統**（2026-02-07）
  - 新增 `cron-automation/yt-finance-show/` 自動化目錄
  - 自動抓取理財達人秀 YouTube 頻道最新影片
  - 使用 whisper-cpp 轉換為中文逐字稿
  - AI 分析逐字稿產生結構化報告（支援 Claude API）
  - 完整的執行腳本：`run.sh`（日誌管理）、`execute.sh`（獨立執行）
  - 支援參數：`--video-id`（指定影片）、`--skip-transcript`（跳過轉換）
  - 範例 cron 設定：每晚 22:00 自動執行
  - 檔案位置：`cron-automation/yt-finance-show/`

- **Cron 自動化執行框架**（2026-02-07）
  - 新增 `cron-automation/revenue-pipeline/` 自動化執行目錄
  - `run.sh`：主執行腳本（日誌管理 + 呼叫 execute.sh）
  - `execute.sh`：獨立執行腳本（完整 pipeline 流程，不依賴 Claude CLI）
  - 日誌自動儲存到 `logs/YYYY-MM-DD.log`（以日期命名）
  - 支援同時輸出到終端和日誌檔案
  - 完整的錯誤處理和執行狀態記錄
  - 範例 cron 設定（每日、公告期、每週）

- **月營收資料庫整合系統**（2026-02-07）
  - 新增 `stock_revenues` 資料表與 5 個索引
  - 新增 `RevenueImporter` 匯入器支援 UPSERT 機制
  - 資料匯入支援 monthly/daily 兩種模式檔案自動判斷
  - 檔案位置：
    - `database/schemas/common/01-tables.sql`（表結構）
    - `database/schemas/common/02-indexes.sql`（索引）
    - `services/data-importer/app/importers/revenue_importer.py`（匯入器）
    - `services/data-importer/app/db/models.py`（ORM 模型）

- **Claude Code Skill: revenue-pipeline**（2026-02-07）
  - 一鍵執行月營收資料處理流程：檢查完整資料 → 智慧收集 → 匯入 → 展示
  - 智慧模式判斷：10號前自動 daily，10號後自動 monthly，API 不符自動切換
  - 支援參數：`--mode`, `--year-month`, `--date`, `--sample`, `--dry-run`, `--force`
  - **表格展示格式**：總覽表格（8檔）+ 詳細資料（前3檔）
  - 自動查詢最新月份營收資料（不再隨機月份）
  - 完整顯示 13 個欄位（包含 YTD 累積數據）
  - 檔案位置：`.claude/skills/revenue-pipeline/`

### 改進
- **Revenue Pipeline 獨立執行架構**（2026-02-07）
  - 從呼叫 Claude CLI 改為獨立執行模式
  - `execute.sh`：實作完整 pipeline 邏輯（PostgreSQL 檢查 → 收集 → 匯入 → 展示）
  - 支援參數：`--year-month`、`--sample`、`--dry-run`
  - 更新文檔：`cron-automation/README.md`、`revenue-pipeline/README.md`
  - 新增 Step 2 容錯機制：API 失敗不影響後續步驟
  - 改進展示格式：表格 + 詳細資料（前 3 檔）

- **營收單位轉換規則文檔化**（2026-02-07）
  - CLAUDE.md 新增「月營收資料處理」區塊
  - 明確標示資料庫儲存單位：千元
  - 正確轉換公式：億元 = 千元 ÷ 100,000
  - 提供實際範例：730,039,420 千元 ÷ 100,000 = 7,300.39 億元
  - 避免單位轉換錯誤（常見錯誤：多除或少除單位）

- **月營收收集腳本智慧化**（2026-02-07）
  - `collect_revenue.py` 新增智慧模式：不指定 `--mode` 時自動判斷（10號前=daily，10號後=monthly）
  - API 年月不符時自動切換模式（monthly 返回舊月份 → 自動降級 daily）
  - 新增 `--force` 參數強制重新收集
  - 新增本地檔案存在檢查，避免重複下載
  - 檔案：`scripts/data-collector/collect_revenue.py`

- **資料匯入腳本增強**（2026-02-07）
  - `import.sh` 新增 revenue 資料類型支援
  - `all` 類型自動包含 revenue（price, institutional, margin, lending, top20_volume, revenue）
  - 匯入器支援 revenue-monthly 和 revenue-daily 檔案自動優先順序判斷
  - 檔案：`scripts/data-importer/import.sh`, `services/data-importer/app/main.py`

- **月營收資料收集系統**（2026-02-06）
  - 新增 `RevenueCollector` 支援雙模式收集
  - **Daily 模式**（1-10 日）：MOPS API 逐一查詢，增量更新
  - **Monthly 模式**（10 日後）：OpenAPI 批次取得完整資料
  - 自動從 OpenAPI 取得上月營收並計算月增率 (MoM)
  - 增量更新機制：載入已收集資料，只查詢未公告股票
  - 檔案位置：
    - `services/common/collectors/revenue_collector.py`
    - `services/common/datasources/twse_revenue_datasource.py`
    - `services/common/datasources/tpex_revenue_datasource.py`
    - `services/common/datasources/mops_revenue_datasource.py`
    - `scripts/data-collector/collect_revenue.py`
  - 資料儲存：
    - `data/raw/revenue-daily/YYYY/YYYY-MM.json`（同月同檔案）
    - `data/raw/revenue-monthly/YYYY/YYYY-MM.json`
  - 文檔：
    - `data/raw/revenue-daily/README.md`
    - `data/raw/revenue-monthly/README.md`
    - `docs/specifications/MONTHLY_REVENUE_COLLECTION_DESIGN.md`
    - `docs/specifications/HISTORICAL_REVENUE_BACKFILL_STRATEGY.md`

- **Claude Code Skill: data-pipeline**（2026-02-06）
  - 自動化資料處理完整流程：收集 → 匯入 → 轉換 → Git 提交
  - 支援日期指定（預設今日）、資料類型篩選
  - TodoWrite 任務追蹤，四階段錯誤處理
  - 自動呼叫 git skill 完成提交與推送
  - **資料收集完成後自動顯示重點股票**：台積電 (2330)、櫻花建 (2539)
  - **日期驗證機制**：收集後驗證資料日期，不符時停止後續處理
  - 檔案位置：`.claude/skills/data-pipeline/SKILL.md`

### 改進
- **TWSE API 參考文檔擴充**（2026-02-06）
  - 新增月營收 API (`t187ap05_L`, `t187ap05_P`) 詳細說明
  - 新增 API 分類概覽表（證券交易、公司治理、財務報表等）
  - 補充 Swagger UI 和 API 總數資訊（145 個 endpoints）
  - 檔案：`docs/TWSE_API_REFERENCE.md`

- **CLAUDE.md 文檔優化**（2026-02-06）
  - 新增月營收資料類型與檔案組織說明
  - 更新資料源整合章節，新增 `RevenueCollector` 雙模式說明
  - 新增月營收收集指令範例（daily/monthly 模式）
  - 優化專案結構說明，新增 `revenue-daily/` 和 `revenue-monthly/` 目錄

- **CLAUDE.md 文檔優化**（2026-02-06）
  - 新增「資料匯入」和「技術分析轉換」指令範例
  - 強調優先使用 shell 腳本（而非直接執行 Python）
  - 更新「執行腳本規範」：明確標註必須使用 `transform.sh`
  - 移除硬編碼密碼，改為佔位符

- **data-pipeline SKILL.md 修正**（2026-02-06）
  - 修正腳本路徑：`transform_technical.py` → `transform.sh`
  - 調整參數格式：`--date` → 直接日期參數
  - 移除硬編碼密碼，統一使用佔位符

- **ETF 持股篩選系統 - 標註版策略**
  - 新增 3 個標註版 SQL（不強制 ETF 持有，改為標註）：
    - `analysis/ETF持股篩選/回頭買上漲_ETF標註版.sql`：完整版（25 檔）
    - `analysis/ETF持股篩選/回頭買上漲_ETF標註版_含明細.sql`：含 ETF 明細
    - `analysis/ETF持股篩選/寬鬆版選股_ETF標註.sql`：寬鬆版（131 檔）
  - 綜合評分系統（0-100 分）：漲幅（40%）+ 量比（30%）+ ETF持有（20%）+ 流動性（10%）
  - 趨勢標註：📈 多頭 / 📉 整理
  - ETF 明細顯示：具體 ETF 名稱與權重

- **分析報告自動生成**（2026-02-05）
  - 完整 Markdown 報告（含統計分析、投資建議、風險提示）
  - 自動轉換 HTML + PDF（使用 `scripts/common-tools/markdown_to_pdf.py`）
  - 報告目錄：`analysis/reports/ETF持股篩選/2026-02-05/`

- **Google Apps Script 整合工具**
  - 新增 `scripts/gas/` 目錄：GAS 呼叫器與網路診斷分析器
  - 安全配置：`.gitignore` 排除 `config.gs` 和 `*_secret.gs`

### 修正
- **技術分析路徑統一**
  - `services/data-transformer/app/json_saver.py`：目錄名稱修正
  - `technical_analysis` → `technical`（與其他模組一致）

### 資料更新
- **2026-02-06 資料收集**
  - price: 1,958 筆（上市 1,080 + 上櫃 878）
  - institutional: 1,838 筆（上市 1,068 + 上櫃 770）
  - margin: 1,821 筆（上市 1,044 + 上櫃 777）
  - top20_volume: 20 筆
  - 技術分析轉換：1,921 檔股票（30 個指標）

- **2026-02-05 資料收集**
  - price: 1,958 筆
  - margin: 1,820 筆
  - top20_volume: 20 筆
  - 技術分析轉換：2026/ 目錄

- **2026-02-04 資料重新處理**
  - institutional, lending, margin, price 的 MD5 更新
  - 報告文件同步更新

- **ETF 持股篩選系統**
  - 資料庫 Schema：新增 3 個表格（etfs, etf_holdings, etf_stock_union）
  - ETF 持股資料：2 個 ETF（00733 富邦臺灣中小、0051 元大中型100）
  - 自動化腳本：
    - `scripts/etf-importer/import_etf_holdings.py`：ETF 持股匯入工具
    - `scripts/etf-importer/generate_etf_union.py`：去重清單生成器
    - `scripts/etf-importer/run_all.sh`：一鍵執行完整流程
  - 選股策略 SQL（ETF 篩選版）：
    - `analysis/ETF持股篩選/回頭買上漲_ETF篩選.sql`：嚴格版（4 檔精選）
    - `analysis/ETF持股篩選/回頭買上漲_ETF篩選_寬鬆版.sql`：寬鬆版（28 檔預備池）
    - `analysis/ETF持股篩選/主升段加速突破_ETF篩選.sql`：ETF 背書版
  - 資料統計：
    - 總持股數：150 筆（00733: 50 檔，0051: 100 檔）
    - 去重後股票：147 檔
    - 被多個 ETF 持有：3 檔（2313 華通、3481 群創、2404 漢唐）

### 資料更新
- 2026-02-04 完整資料處理流程
  - **原始資料收集**: price (1,957 筆), margin (1,820 筆), institutional (761 筆), top20_volume (20 筆)
  - **資料匯入資料庫**: stock_prices (1,957 筆)
  - **技術分析計算**: 1,921 檔股票，30 個技術指標
  - **技術分析匯入**: stock_analysis_daily (1,921 筆)
  - **選股分析執行**:
    - 主升段加速突破: 3 檔（8213 志超、1708 東鹼、3209 全科）
    - 回頭買上漲: 6 檔（2436 偉詮電、1301 台塑、2031 新光鋼、2605 新興、1471 首利、1455 集盛）

### 修正
- **Python 版本統一**
  - 修正 `scripts/data-importer/import.sh`：`python` → `python3.11`
  - 確保所有腳本使用 Python 3.11 執行
  - 原因：專案依賴 pandas>=2.0.0、sqlalchemy>=2.0.0 需要 Python 3.8+

### 文檔更新
- **CLAUDE.md** 新增 Python 環境說明
  - 明確指定使用 Python 3.11（不可使用系統預設的 python3 3.7）
  - 記錄套件管理器優先使用 `uv`
  - 說明套件安裝方式（uv vs pip）
  - 記錄 PostgreSQL CLI 工具使用 `psql-17`
- **CLAUDE.md** 更新資料庫狀態
  - 資料範圍更新至 2026-02-04
  - 交易日數: 513 → 514 天
  - 總記錄數: 958,793 → 960,750 筆
  - 補充表欄位名稱說明（trade_date, stock_id 等）

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
