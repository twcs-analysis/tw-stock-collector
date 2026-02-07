# Changelog - Revenue Pipeline Automation

所有關於 Revenue Pipeline 自動化執行的重要變更都會記錄在此檔案。

---

## [1.1.0] - 2026-02-07

### 修正
- **修復 "No messages returned" 錯誤**
  - 原因：`run.sh` 透過 `claude "/revenue-pipeline"` 呼叫 skill 在 cron 環境下失敗
  - 解決方案：創建獨立的 `execute.sh` 腳本，直接執行 Pipeline 流程
  - 影響：現在可以在 cron 環境下穩定執行

### 新增
- **execute.sh**：獨立執行腳本
  - 直接執行 5 個步驟：確認 PostgreSQL → 檢查 monthly 資料 → 收集目標月 → 匯入資料庫 → 展示結果
  - 支援參數：`--year-month`、`--sample`、`--dry-run`
  - 完整的錯誤處理和日誌輸出

### 變更
- **run.sh**：改為呼叫 `execute.sh`
  - 從 `claude "/revenue-pipeline"` 改為 `"$SCRIPT_DIR/execute.sh"`
  - 保留日誌管理功能

### 改進
- **錯誤處理**：Step 2（檢查 monthly 資料）失敗時不影響後續步驟
  - API 超時或網路問題時會記錄警告並繼續執行
  - 主要收集流程（Step 3）獨立運作

---

## [1.0.0] - 2026-02-07

### 新增
- **初始版本**：Revenue Pipeline 自動化執行框架
  - `run.sh`：主執行腳本
  - `logs/`：日誌目錄（以日期命名）
  - `README.md`：使用說明

### 功能
- 自動執行月營收資料處理流程
- 日誌自動儲存到 `logs/YYYY-MM-DD.log`
- 支援 cron 排程執行
- 整合 `/revenue-pipeline` skill

---

**版本格式**: [主版本.次版本.修訂版本]
- **主版本**：不相容的 API 變更
- **次版本**：向下相容的功能新增
- **修訂版本**：向下相容的問題修正
