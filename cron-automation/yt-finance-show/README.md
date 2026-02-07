# YT Finance Show 自動化執行

自動化處理理財達人秀影片：抓取 → 轉換逐字稿 → AI 分析。

---

## 📋 功能概述

1. **自動抓取最新影片**
   - 從 YouTube 頻道 `@EBCmoneyshow` 抓取最新一集
   - **優先抓取「電視完整版」**（約 48 分鐘完整節目）
   - 若無完整版則抓取最新片段
   - 自動取得影片 ID、標題、發布日期

2. **轉換為逐字稿**
   - 使用 `scripts/media-tools/video_to_transcript.py`
   - whisper-cpp 語音轉文字（中文）
   - 儲存到 `data/transcripts/{日期}/`

3. **AI 分析報告**
   - 使用 Claude API 深度分析（需設定 API Key）
   - 產生結構化 Markdown 報告
   - 儲存到 `data/transcripts/{日期}/{檔名}_analysis.md`

4. **日誌記錄**
   - 自動儲存執行日誌到 `logs/YYYY-MM-DD.log`
   - 包含完整執行過程與錯誤訊息

---

## 🚀 使用方式

### 1. 手動執行

```bash
# 基本執行（自動抓取最新影片）
./cron-automation/yt-finance-show/run.sh

# 指定影片 ID
./cron-automation/yt-finance-show/execute.sh --video-id sUPMZ7gdk4o

# 跳過逐字稿轉換（僅分析現有逐字稿）
./cron-automation/yt-finance-show/execute.sh --skip-transcript
```

### 2. Cron 自動執行

編輯 crontab：

```bash
crontab -e
```

新增排程：

```bash
# 每天晚上 22:00 執行（理財達人秀通常晚上 8-9 點播出）
0 22 * * * /Users/jasonhuang/github/personal/tw-stock-collector/cron-automation/yt-finance-show/run.sh

# 每週一到五晚上 22:00 執行
0 22 * * 1-5 /Users/jasonhuang/github/personal/tw-stock-collector/cron-automation/yt-finance-show/run.sh

# 每週一、三、五晚上 22:00 執行
0 22 * * 1,3,5 /Users/jasonhuang/github/personal/tw-stock-collector/cron-automation/yt-finance-show/run.sh
```

查看 cron 日誌：

```bash
# macOS
log show --predicate 'process == "cron"' --last 1h

# 或查看腳本日誌
tail -f cron-automation/yt-finance-show/logs/$(date '+%Y-%m-%d').log
```

---

## ⚙️ 環境設定

### 必要工具

- **yt-dlp**（影音下載）
  ```bash
  brew install yt-dlp
  ```

- **whisper-cpp**（語音轉文字）
  ```bash
  brew install whisper-cpp
  ```

- **Python 3.11+**
  ```bash
  brew install python@3.11
  ```

### 選用設定

- **Claude API Key**（啟用完整 AI 分析）

  在 `~/.zshrc` 或 `~/.bash_profile` 加入：
  ```bash
  export ANTHROPIC_API_KEY="your-api-key-here"
  ```

  重新載入：
  ```bash
  source ~/.zshrc
  ```

---

## 📂 檔案結構

```
cron-automation/yt-finance-show/
├── run.sh                    # 主執行腳本（包含日誌）
├── execute.sh                # 獨立執行腳本（核心邏輯）
├── analyze_transcript.py     # AI 分析腳本
├── README.md                 # 說明文件
└── logs/                     # 執行日誌
    ├── .gitkeep
    └── YYYY-MM-DD.log        # 每日日誌
```

---

## 📊 輸出內容

### 1. 逐字稿

**位置**: `data/transcripts/{日期}/{檔名}.txt`

**格式**:
```
# 逐字稿 - finance_show_20260207
# 來源網址: https://www.youtube.com/watch?v=xxx
# 轉換日期: 2026-02-07 22:35:12
# Whisper 模型: base

================================================================================

[逐字稿內容]
...
```

### 2. 分析報告

**位置**: `data/transcripts/{日期}/{檔名}_analysis.md`

**章節**:
- 📺 節目資訊
- 📊 市場總體觀察
- 💼 產業分析與投資建議
- 🔬 前瞻技術深度解析
- 📈 投資策略總結
- 💡 來賓金句
- 📚 名詞解釋

### 3. 執行日誌

**位置**: `cron-automation/yt-finance-show/logs/YYYY-MM-DD.log`

**內容**:
```
============================================================
YT Finance Show 自動化執行
============================================================
開始時間: 2026-02-07 22:00:15
...
結束時間: 2026-02-07 22:12:45
執行狀態: ✓ 成功
============================================================
```

---

## ⏱️ 執行時間估計

- **抓取影片資訊**: ~5 秒
- **下載音訊**: ~2-3 分鐘（1 小時影片）
- **語音轉文字**: ~5-10 分鐘（取決於影片長度）
- **AI 分析**: ~1-2 分鐘（使用 API）

**總計**: 約 **10-15 分鐘**

---

## 🔧 疑難排解

### 1. yt-dlp 抓取失敗

**錯誤**: `✗ 無法抓取影片資訊`

**解決方式**:
```bash
# 更新 yt-dlp
brew upgrade yt-dlp

# 手動測試
yt-dlp --flat-playlist "https://www.youtube.com/@EBCmoneyshow/videos" | head -1
```

### 2. whisper-cpp 模型未下載

**錯誤**: `找不到模型檔案 ggml-base.bin`

**解決方式**:
```bash
# 下載 base 模型
cd /opt/homebrew/share/whisper-cpp/models/
curl -L -o ggml-base.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin
```

### 3. 逐字稿檔案已存在

**訊息**: `⚠️ 逐字稿已存在，跳過轉換步驟`

這是正常行為，腳本會自動跳過已處理的影片。

如需重新處理：
```bash
# 刪除現有逐字稿
rm data/transcripts/2026-02-07/finance_show_20260207.txt

# 重新執行
./cron-automation/yt-finance-show/run.sh
```

### 4. Cron 執行失敗

**檢查方式**:
```bash
# macOS: 查看系統日誌
log show --predicate 'process == "cron"' --last 1h --style syslog

# 查看腳本日誌
cat cron-automation/yt-finance-show/logs/$(date '+%Y-%m-%d').log
```

**常見原因**:
- 路徑錯誤（cron 環境變數不同）
- 權限問題（確保腳本有執行權限）
- 工具未安裝（確保 yt-dlp、whisper-cpp 在 PATH 中）

---

## 📈 與 Claude Skill 的差異

### Cron 自動化腳本

- ✅ **自動執行**：無需人工介入
- ✅ **排程靈活**：可設定每日、每週執行
- ✅ **日誌完整**：保存所有執行記錄
- ⚠️ **AI 分析有限**：需要 API Key（目前為簡易模式）

### Claude Skill (`/yt-finance-show`)

- ✅ **AI 分析完整**：使用 Claude 進行深度互動分析
- ✅ **即時回饋**：可以提問和討論
- ⚠️ **需手動執行**：需要人工呼叫 skill

### 建議使用方式

1. **日常監控**: 使用 Cron 自動執行，每天抓取最新影片
2. **深度分析**: 使用 `/yt-finance-show` skill 進行互動式分析
3. **快速查看**: Cron 產生的簡易報告可先快速瀏覽

---

## 📝 更新日誌

### 2026-02-07
- ✨ 初始版本
- ✅ 自動抓取、轉換、分析流程
- ✅ 日誌記錄功能
- ⚠️ AI 分析功能（待完善 Claude API 整合）

---

## 🔗 相關資源

- [理財達人秀 YouTube 頻道](https://www.youtube.com/@EBCmoneyshow)
- [yt-dlp 文件](https://github.com/yt-dlp/yt-dlp)
- [whisper-cpp 文件](https://github.com/ggerganov/whisper.cpp)
- Claude Skill: `.claude/skills/yt-finance-show/`
- 轉換腳本: `scripts/media-tools/video_to_transcript.py`

---

**最後更新**: 2026-02-07
**維護者**: Jason Huang
