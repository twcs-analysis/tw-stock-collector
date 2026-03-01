# YT BC-Stock 自動化處理

自動化處理 BC股市這檔事 YouTube 影片的完整流程。

## 📋 功能說明

### 完整處理流程

1. **抓取最新影片** - 使用 yt-dlp 搜尋最新影片
2. **下載音訊** - 下載為 MP3 格式
3. **轉換逐字稿** - 使用 whisper-cpp 語音轉文字
4. **AI 分析** - 產生投資分析報告（需透過 Claude Code）

## 🚀 使用方式

### 方法 1: 手動執行（推薦）

```bash
# 處理今天的影片
./execute.sh

# 處理指定日期的影片
./execute.sh --date 2026-03-01

# 跳過下載，僅轉換與分析
./execute.sh --skip-download

# 跳過逐字稿轉換
./execute.sh --skip-transcript
```

### 方法 2: 透過 Claude Code Skill

```bash
# 在 Claude Code 中執行
/yt-bc-stock                    # 處理今天的影片
/yt-bc-stock 2026-03-01        # 處理指定日期
/yt-bc-stock --skip-download   # 跳過下載
```

### 方法 3: Crontab 自動化（每日執行）

```bash
# 編輯 crontab
crontab -e

# 加入以下設定（每日 22:00 執行）
0 22 * * * /Users/jasonhuang/github/personal/tw-stock-collector/cron-automation/yt-bc-stock/run.sh
```

## 📁 檔案結構

```
cron-automation/yt-bc-stock/
├── README.md           # 本文件
├── run.sh              # Cron 執行腳本（含日誌管理）
├── execute.sh          # 主要處理腳本
└── logs/               # 執行日誌目錄
    └── YYYY-MM-DD.log  # 每日日誌
```

## 📊 輸出位置

所有檔案儲存在：

```
data/transcripts/yt-bc-stock/{日期}/
├── bc_stock_{YYYYMMDD}.mp3    # 影片音訊
├── bc_stock_{YYYYMMDD}.txt    # 逐字稿
└── analysis.md                 # AI 分析報告（占位，需透過 Claude Code 完成）
```

## 🔧 前置需求

### 必要工具

1. **yt-dlp** - YouTube 影片下載
   ```bash
   brew install yt-dlp
   ```

2. **whisper-cpp** - 語音轉文字
   ```bash
   # 參考 scripts/media-tools/README.md 安裝
   ```

3. **Python 3.11+**
   ```bash
   python3.11 --version
   ```

### Python 套件

```bash
pip install -r requirements.txt
```

## 📝 參數說明

### execute.sh 參數

- `--date YYYY-MM-DD` - 指定處理日期（預設：今天）
- `--skip-download` - 跳過影片下載
- `--skip-transcript` - 跳過逐字稿轉換

### 使用範例

```bash
# 處理今天的影片（完整流程）
./execute.sh

# 處理 2026-03-01 的影片
./execute.sh --date 2026-03-01

# 僅下載與轉換，不分析
./execute.sh --skip-analysis

# 僅分析現有逐字稿
./execute.sh --skip-download --skip-transcript
```

## 🎯 AI 分析完成步驟

腳本會產生占位分析報告，需要透過 Claude Code 完成深度分析：

### 步驟 1: 執行腳本產生逐字稿

```bash
./execute.sh
```

### 步驟 2: 在 Claude Code 中完成分析

```bash
/yt-bc-stock 2026-03-01 --skip-download
```

或手動分析：

```
請分析以下逐字稿：
data/transcripts/yt-bc-stock/2026-03-01/bc_stock_20260301.txt
```

## 📅 Crontab 設定範例

### 每日自動執行（週一到週五 22:00）

```cron
0 22 * * 1-5 /Users/jasonhuang/github/personal/tw-stock-collector/cron-automation/yt-bc-stock/run.sh
```

### 每週執行（週日 22:00）

```cron
0 22 * * 0 /Users/jasonhuang/github/personal/tw-stock-collector/cron-automation/yt-bc-stock/run.sh
```

## 📊 日誌管理

### 查看最新日誌

```bash
tail -f logs/$(date '+%Y-%m-%d').log
```

### 查看歷史日誌

```bash
ls -lh logs/
cat logs/2026-03-01.log
```

### 清理舊日誌

```bash
# 刪除 30 天前的日誌
find logs/ -name "*.log" -mtime +30 -delete
```

## ⚠️ 注意事項

### 影片下載

- YouTube 影片可能有地區限制
- 需要穩定的網路連線
- 建議使用最新版本的 yt-dlp

### 逐字稿轉換

- whisper-cpp base 模型已足夠準確
- 如需更高準確度，可使用 medium 或 large 模型（需更長時間）
- 音訊品質會影響逐字稿準確度

### AI 分析

- 自動化腳本僅產生占位報告
- 深度分析需透過 Claude Code 的 /yt-bc-stock skill
- 確保 ANTHROPIC_API_KEY 已設定（Claude Code 內建）

## 🔗 相關文檔

- **Skill 文檔**: `~/.claude/skills/yt-bc-stock/SKILL.md`
- **影片工具**: `scripts/media-tools/README.md`
- **錢線百分百**: `cron-automation/yt-moneyline/README.md`

## 🆘 疑難排解

### Q: yt-dlp 下載失敗？

A:
```bash
# 更新 yt-dlp
brew upgrade yt-dlp

# 測試下載
yt-dlp "ytsearch1:BC股市這檔事" --print "%(id)s|%(title)s"
```

### Q: whisper-cpp 轉換錯誤？

A:
```bash
# 檢查安裝
which whisper-cpp
whisper-cpp --version

# 參考安裝文檔
cat ../../scripts/media-tools/README.md
```

### Q: 找不到影片？

A:
- 確認影片標題包含 "BC股市這檔事"
- 檢查是否為私人影片或已刪除
- 嘗試手動搜尋 YouTube 確認

---

**建立日期**: 2026-03-01
**維護者**: Jason Huang
**專案**: tw-stock-collector
