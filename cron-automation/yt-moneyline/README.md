# YT Moneyline 自動處理系統

自動抓取「錢線百分百」YouTube 節目最新三集（上、中、下），轉換為逐字稿並進行 AI 分析。

## 功能特色

- ✅ 自動抓取最新三集影片（上、中、下）
- ✅ 使用 whisper-cpp 轉換為中文逐字稿
- ✅ AI 深度分析產生結構化報告
- ✅ 產生每日整合摘要
- ✅ 支援 cron 自動化執行
- ✅ 完整的日誌記錄

## 快速開始

### 手動執行

```bash
# 執行完整流程（抓取、轉換、分析）
./cron-automation/yt-moneyline/execute.sh

# 跳過逐字稿轉換（僅分析已有的逐字稿）
./cron-automation/yt-moneyline/execute.sh --skip-transcript

# 指定處理特定集數（例如只處理上集）
./cron-automation/yt-moneyline/execute.sh --parts 1

# 指定處理多個集數（例如上中兩集）
./cron-automation/yt-moneyline/execute.sh --parts 1,2

# 處理特定日期的影片
./cron-automation/yt-moneyline/execute.sh --date 2026-02-06
```

### Cron 自動化

```bash
# 設定 crontab（每日 22:00 執行）
0 22 * * * /path/to/tw-stock-collector/cron-automation/yt-moneyline/run.sh

# 或使用 run.sh 手動執行（包含日誌管理）
./cron-automation/yt-moneyline/run.sh
```

## 執行流程

### 1. 抓取最新影片

- 使用 `yt-dlp` 查詢 YouTube 頻道 `@TVBSMONEYGO`
- 自動識別同一天的上、中、下三集
- 提取影片 ID、標題、發布日期

### 2. 轉換逐字稿

- 依序處理三集影片（避免系統負載過高）
- 下載影音檔案並轉換為 mp3
- 使用 whisper-cpp 進行語音辨識
- 產生中文逐字稿（plain text 格式）

**輸出路徑**：
```
data/transcripts/yt-moneyline/YYYY-MM-DD/
├── moneyline_YYYYMMDD_part1.txt  # 上集逐字稿
├── moneyline_YYYYMMDD_part2.txt  # 中集逐字稿
└── moneyline_YYYYMMDD_part3.txt  # 下集逐字稿
```

### 3. AI 分析

**重要**：分析採用 **Claude Code 互動式分析**，而非自動化 API 呼叫。

#### 工作流程

1. **自動產生占位報告**
   - `analyze_transcript.py` 產生基本結構報告
   - 包含節目資訊、字數統計、內容預覽

2. **使用 Claude Code 深度分析**（需人工執行）
   - 在 Claude Code 中執行 `/yt-moneyline` skill
   - 或直接請求分析逐字稿檔案
   - Claude Code 會進行深度閱讀與分析

3. **分析內容包含**
   - 市場總體觀察（台股、美股、國際）
   - 產業分析與投資建議
   - 個股推薦（含目標價、停損點）
   - 技術面分析與操作策略
   - 來賓金句整理
   - 專業名詞解釋

**輸出路徑**：
```
data/transcripts/yt-moneyline/YYYY-MM-DD/
├── moneyline_YYYYMMDD_part1_analysis.md  # 占位報告 → Claude Code 更新
├── moneyline_YYYYMMDD_part2_analysis.md
└── moneyline_YYYYMMDD_part3_analysis.md
```

### 4. 每日整合摘要

整合三集的分析重點：

- 今日核心重點
- 關鍵個股清單
- 產業趨勢總結
- 技術面總結
- 風險提示

**輸出路徑**：
```
data/transcripts/yt-moneyline/YYYY-MM-DD/
└── daily_summary.md
```

## 檔案結構

```
cron-automation/yt-moneyline/
├── execute.sh              # 主執行腳本
├── run.sh                  # Cron 執行腳本（含日誌）
├── analyze_transcript.py   # AI 分析程式
├── logs/                   # 執行日誌
│   └── YYYY-MM-DD.log
└── README.md               # 本說明文件
```

## 參數說明

### execute.sh

| 參數 | 說明 | 範例 |
|------|------|------|
| `--date` | 指定處理日期 | `--date 2026-02-06` |
| `--skip-transcript` | 跳過逐字稿轉換 | `--skip-transcript` |
| `--parts` | 指定處理集數 | `--parts 1,2,3` |

### analyze_transcript.py

```bash
# 分析單一集數
python3.11 analyze_transcript.py \
    <transcript_file> \
    <output_file> \
    --part <1|2|3>

# 產生每日整合摘要
python3.11 analyze_transcript.py \
    --generate-summary \
    --analysis-files <file1> <file2> <file3> \
    --output <summary_file>
```

## 依賴套件

### 系統工具

- **yt-dlp**：YouTube 影片下載
- **whisper-cpp**：語音轉文字（需先安裝並編譯）
- **Python 3.11+**

### Python 套件

- `argparse`：命令列參數解析（內建）
- `pathlib`：路徑處理（內建）
- `datetime`：日期時間處理（內建）

### 安裝 whisper-cpp

```bash
# 下載並編譯 whisper-cpp
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp
make

# 下載模型（建議使用 base 模型）
bash ./models/download-ggml-model.sh base

# 設定路徑（加入 ~/.bashrc 或 ~/.zshrc）
export PATH="/path/to/whisper.cpp:$PATH"
```

## 分析模式

本系統採用 **Claude Code 互動式分析**，不使用 Claude API。

### 為什麼使用 Claude Code？

1. **更深入的理解**：Claude Code 可以完整閱讀逐字稿
2. **互動式調整**：可以針對分析結果進行追問和調整
3. **無 API 成本**：不需要額外的 API 費用
4. **靈活性高**：可以根據需求調整分析重點

### 工作流程

```bash
# 1. 執行自動化腳本（產生逐字稿 + 占位報告）
./cron-automation/yt-moneyline/execute.sh

# 2. 使用 Claude Code 進行深度分析
# 在 Claude Code 中執行：
/yt-moneyline

# 或直接請求分析：
# 「請分析 data/transcripts/yt-moneyline/2026-02-07/ 目錄下的逐字稿並更新分析報告」
```

## 執行時間估計

| 步驟 | 時間（單集） | 時間（三集） |
|------|--------------|--------------|
| 抓取影片 | 5 秒 | 5 秒 |
| 轉換逐字稿 | 5-10 分鐘 | 15-30 分鐘 |
| AI 分析 | 10-30 秒 | 30-90 秒 |
| 整合摘要 | 10-20 秒 | 10-20 秒 |
| **總計** | **約 10 分鐘** | **約 20-35 分鐘** |

**建議**：
- 使用 cron 在非工作時間執行（如 22:00）
- 確保網路連線穩定
- 預留充足的磁碟空間（每日約 500 MB）

## 疑難排解

### 問題：找不到影片

**可能原因**：
- YouTube 頻道未上傳新影片
- 影片標題格式變更
- 網路連線問題

**解決方法**：
```bash
# 手動檢查頻道
yt-dlp --flat-playlist --print "%(id)s|%(title)s|%(upload_date)s" \
    "https://www.youtube.com/@TVBSMONEYGO/videos" | head -10

# 使用 --date 參數指定日期
./execute.sh --date 2026-02-06
```

### 問題：逐字稿轉換失敗

**可能原因**：
- whisper-cpp 未正確安裝
- 模型檔案遺失
- 音檔下載失敗

**解決方法**：
```bash
# 檢查 whisper-cpp
which whisper

# 檢查模型檔案
ls -lh /path/to/whisper.cpp/models/

# 手動測試轉換
python3.11 scripts/media-tools/video_to_transcript.py \
    "https://www.youtube.com/watch?v=<VIDEO_ID>" \
    --output "test" \
    --model base
```

### 問題：分析報告為空或簡易模式

**可能原因**：
- 未設定 `ANTHROPIC_API_KEY`
- API Key 無效或過期

**解決方法**：
```bash
# 設定環境變數
export ANTHROPIC_API_KEY="your-api-key"

# 重新執行
./execute.sh --skip-transcript
```

## 日誌管理

### 日誌位置

```
cron-automation/yt-moneyline/logs/
└── YYYY-MM-DD.log
```

### 查看日誌

```bash
# 查看最新日誌
tail -f cron-automation/yt-moneyline/logs/$(date '+%Y-%m-%d').log

# 查看歷史日誌
ls -lh cron-automation/yt-moneyline/logs/

# 清理舊日誌（保留最近 30 天）
find cron-automation/yt-moneyline/logs/ -name "*.log" -mtime +30 -delete
```

## 與 Claude CLI Skill 整合

本系統可與 Claude CLI 的 `/yt-moneyline` skill 整合使用：

```bash
# 在 Claude CLI 中使用
/yt-moneyline

# 或在對話中
請執行 yt-moneyline skill
```

**差異**：
- **execute.sh**：獨立執行，適合 cron 自動化
- **Claude Skill**：互動式執行，適合手動操作和深度分析

## 資料儲存結構

```
data/transcripts/yt-moneyline/
├── 2026-02-01/
│   ├── moneyline_20260201_part1.txt
│   ├── moneyline_20260201_part1_analysis.md
│   ├── moneyline_20260201_part2.txt
│   ├── moneyline_20260201_part2_analysis.md
│   ├── moneyline_20260201_part3.txt
│   ├── moneyline_20260201_part3_analysis.md
│   └── daily_summary.md
├── 2026-02-02/
│   └── ...
└── 2026-02-03/
    └── ...
```

## 授權與聲明

- 本工具僅供個人學習與研究使用
- 逐字稿與分析報告版權歸原節目所有
- 請勿用於商業用途
- 使用 Claude API 需遵守 Anthropic 使用條款

## 更新日誌

### 2026-02-07
- ✅ 初始版本
- ✅ 支援抓取上中下三集
- ✅ 整合 whisper-cpp 轉換
- ✅ AI 分析與每日摘要
- ✅ Cron 自動化執行

---

**維護者**：Jason Huang
**最後更新**：2026-02-07
