# Changelog

All notable changes to the YT Finance Show automation will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Fixed
- 🔧 **修正目錄結構**（2026-02-07）
  - 修改輸出路徑為 `data/transcripts/yt-finance-show/{date}/`
  - 遵循 skill 名稱 → 日期的目錄層級規範
  - 更新文檔說明

- 🔧 **優先抓取電視完整版**（2026-02-07）
  - 修改 `execute.sh` Step 1 邏輯
  - 優先抓取「電視完整版」影片（約 48 分鐘）
  - 若無完整版則降級抓取最新片段
  - 解決之前只抓到 part3 的問題

### Planned
- 整合完整的 Claude API 分析功能
- 支援多集影片批次處理
- 新增 Slack/Email 通知功能
- 結果匯出為 PDF 格式

---

## [1.0.0] - 2026-02-07

### Added
- 🎉 初始版本發布
- ✅ 自動抓取理財達人秀最新影片（YouTube @EBCmoneyshow）
- ✅ 使用 whisper-cpp 轉換為中文逐字稿
- ✅ AI 分析腳本框架（簡易模式）
- ✅ 完整的日誌記錄系統
- ✅ Cron 自動化執行支援
- 📝 完整的 README 文件

### Features
- **run.sh**: 主執行腳本，包含日誌記錄
- **execute.sh**: 獨立執行腳本，包含完整流程
- **analyze_transcript.py**: AI 分析腳本（Python 3.11）
- **logs/**: 日誌目錄（以日期命名）

### Dependencies
- yt-dlp: 影音下載
- whisper-cpp: 語音轉文字
- Python 3.11+

### Parameters
- `--video-id`: 指定影片 ID
- `--skip-transcript`: 跳過逐字稿轉換

### Output
- 逐字稿: `data/transcripts/yt-finance-show/{date}/{filename}.txt`
- 分析報告: `data/transcripts/yt-finance-show/{date}/{filename}_analysis.md`
- 執行日誌: `logs/{date}.log`

---

## Notes

### Future Improvements
1. **Claude API 整合**: 目前為簡易分析模式，需實作完整的 Claude API 呼叫
2. **錯誤重試機制**: 網路錯誤時自動重試
3. **增量更新**: 僅處理新影片，避免重複處理
4. **結果通知**: 完成後發送通知（Slack/Email）
5. **資料庫儲存**: 將分析結果存入資料庫

### Known Issues
- AI 分析功能需要設定 `ANTHROPIC_API_KEY` 才能啟用完整分析
- 目前無 API Key 時使用簡易分析模式（僅顯示逐字稿摘要）

---

**Changelog 格式說明**:
- **Added**: 新增功能
- **Changed**: 功能變更
- **Deprecated**: 即將移除的功能
- **Removed**: 已移除的功能
- **Fixed**: 錯誤修正
- **Security**: 安全性更新
