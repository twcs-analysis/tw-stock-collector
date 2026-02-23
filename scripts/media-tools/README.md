# 影音轉文字工具

提供兩種影音轉文字功能：

1. **影音網址轉逐字稿**：自動下載影音並轉換為中文逐字稿
2. **批次 MP3 轉逐字稿**：批次處理本地 mp3 檔案，轉換為逐字稿

## 工具清單

### 1. video_to_transcript - 影音網址轉逐字稿

1. 使用 `yt-dlp` 下載影音網址，轉換為 mp3 格式
2. 使用 `whisper-cpp` 將 mp3 轉換為中文逐字稿
3. 儲存逐字稿到 `data/transcripts/{日期}/{檔名}.txt`

### 2. batch_mp3_to_transcript - 批次 MP3 轉逐字稿

1. 批次掃描指定目錄下所有 2026-* 子目錄的 mp3 檔案
2. 使用 `whisper-cpp` 將 mp3 轉換為中文逐字稿
3. 逐字稿保存在各自的原始目錄下（例如：`2026-01-02/錢線百分百_20260102_上集.txt`）
4. 自動跳過已存在的逐字稿，避免重複轉換
5. 顯示進度並記錄錯誤

## 環境需求

### 必要套件

1. **whisper-cpp**（語音轉文字）- 兩個工具都需要
   ```bash
   brew install whisper-cpp
   ```

2. **yt-dlp**（影音下載工具）- 僅 video_to_transcript 需要
   ```bash
   brew install yt-dlp
   ```

3. **Whisper 模型**（第一次使用時自動下載）
   - 模型位置：`/opt/homebrew/share/whisper-cpp/models/`
   - 可用模型：tiny, base, small, medium, large

### Python 環境

- Python 3.11+
- 標準函式庫（無需額外安裝套件）

---

## 使用方式

## 工具 1: video_to_transcript - 影音網址轉逐字稿

### 方法 1：使用 Shell 腳本（推薦）

```bash
# 基本使用（使用影片標題作為檔名）
./scripts/media-tools/video_to_transcript.sh "https://www.youtube.com/watch?v=xxx"

# 指定輸出檔名
./scripts/media-tools/video_to_transcript.sh "https://www.youtube.com/watch?v=xxx" --output "meeting_notes"

# 使用不同的 Whisper 模型
./scripts/media-tools/video_to_transcript.sh "https://www.youtube.com/watch?v=xxx" --model large
```

### 方法 2：直接執行 Python 腳本

```bash
# 基本使用
python3.11 scripts/media-tools/video_to_transcript.py "https://www.youtube.com/watch?v=xxx"

# 指定輸出檔名
python3.11 scripts/media-tools/video_to_transcript.py "https://www.youtube.com/watch?v=xxx" --output "meeting_notes"

# 使用不同的 Whisper 模型
python3.11 scripts/media-tools/video_to_transcript.py "https://www.youtube.com/watch?v=xxx" --model large
```

### 查看完整說明

```bash
python3.11 scripts/media-tools/video_to_transcript.py --help
```

---

## 工具 2: batch_mp3_to_transcript - 批次 MP3 轉逐字稿

### 方法 1：使用 Shell 腳本（推薦）

```bash
# 基本使用（使用預設 base 模型）
./scripts/media-tools/batch_mp3_to_transcript.sh /Users/jasonhuang/yt-video/yt-moneyline

# 使用不同的 Whisper 模型
./scripts/media-tools/batch_mp3_to_transcript.sh /Users/jasonhuang/yt-video/yt-moneyline --model small

# 強制重新轉換（忽略已存在的逐字稿）
./scripts/media-tools/batch_mp3_to_transcript.sh /Users/jasonhuang/yt-video/yt-moneyline --force

# 組合選項
./scripts/media-tools/batch_mp3_to_transcript.sh /Users/jasonhuang/yt-video/yt-moneyline --model small --force
```

### 方法 2：直接執行 Python 腳本

```bash
# 基本使用
python3.11 scripts/media-tools/batch_mp3_to_transcript.py /Users/jasonhuang/yt-video/yt-moneyline

# 使用不同的 Whisper 模型
python3.11 scripts/media-tools/batch_mp3_to_transcript.py /Users/jasonhuang/yt-video/yt-moneyline --model small

# 強制重新轉換
python3.11 scripts/media-tools/batch_mp3_to_transcript.py /Users/jasonhuang/yt-video/yt-moneyline --force
```

### 查看完整說明

```bash
python3.11 scripts/media-tools/batch_mp3_to_transcript.py --help
```

### 輸出說明

批次工具會在每個 mp3 檔案所在的目錄下產生同名的 txt 檔案：

```
/Users/jasonhuang/yt-video/yt-moneyline/
├── 2026-01-02/
│   ├── 錢線百分百_20260102_上集.mp3
│   ├── 錢線百分百_20260102_上集.txt    ← 轉換後的逐字稿
│   ├── 錢線百分百_20260102_中集.mp3
│   ├── 錢線百分百_20260102_中集.txt    ← 轉換後的逐字稿
│   ├── 錢線百分百_20260102_下集.mp3
│   └── 錢線百分百_20260102_下集.txt    ← 轉換後的逐字稿
├── 2026-01-03/
│   ├── ...
```

### 執行範例輸出

```
🔍 檢查依賴套件...
✅ whisper-cpp 已安裝
✅ 模型檔案存在: /opt/homebrew/share/whisper-cpp/models/ggml-base.bin

📂 搜尋 /Users/jasonhuang/yt-video/yt-moneyline 下的 2026-* 目錄...
✅ 找到 158 個 mp3 檔案

準備處理 158 個 mp3 檔案
模型: base
強制重新轉換: 否

按 Enter 繼續，或 Ctrl+C 取消...

================================================================================
開始批次處理
================================================================================

[1/158] 處理中: 錢線百分百_20260102_上集.mp3
  目錄: /Users/jasonhuang/yt-video/yt-moneyline/2026-01-02
  🎤 開始轉換（模型: base）...
  ✅ 轉換完成

[2/158] 處理中: 錢線百分百_20260102_中集.mp3
  目錄: /Users/jasonhuang/yt-video/yt-moneyline/2026-01-02
  ⏭️  逐字稿已存在，跳過

...

================================================================================
📊 處理結果統計
================================================================================
總檔案數: 158
成功轉換: 120
跳過檔案: 35
失敗檔案: 3
總耗時: 2:15:30

❌ 失敗的檔案:
  - /Users/jasonhuang/yt-video/yt-moneyline/2026-01-15/錢線百分百_20260115_上集.mp3
  - ...

================================================================================
⚠️  部分檔案處理失敗
================================================================================
```

---

## 參數說明

### 必要參數

- `url`：影音網址（支援 YouTube、Vimeo 等 yt-dlp 支援的網站）

### 選用參數

- `-o, --output`：輸出檔名（不含副檔名），預設使用影片標題
- `-m, --model`：Whisper 模型，預設為 `base`

## Whisper 模型選擇

| 模型 | 大小 | 速度 | 準確度 | 適用情境 |
|------|------|------|--------|----------|
| tiny | 39M | 最快 | 低 | 快速測試 |
| base | 74M | 快 | 中 | **一般使用（預設）** |
| small | 244M | 中 | 高 | 重要會議 |
| medium | 769M | 慢 | 很高 | 專業轉錄 |
| large | 1.5G | 最慢 | 最高 | 最高品質需求 |

## 輸出格式

逐字稿會儲存在 `data/transcripts/{日期}/{檔名}.txt`，包含：

```
# 逐字稿 - {檔名}
# 來源網址: {URL}
# 轉換日期: {日期時間}
# Whisper 模型: {模型}

================================================================================

{逐字稿內容}
```

## 目錄結構

```
data/
├── temp/                    # 暫存目錄（mp3 檔案，自動清理）
└── transcripts/             # 逐字稿輸出目錄
    └── 2026-02-07/          # 依日期分類
        ├── video1.txt
        └── meeting_notes.txt
```

## 使用範例

### 範例 1：轉換 YouTube 影片

```bash
./scripts/media-tools/video_to_transcript.sh "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

輸出：
```
🔍 檢查依賴套件...
✅ yt-dlp 已安裝
✅ whisper-cpp 已安裝

📥 下載影音: https://www.youtube.com/watch?v=dQw4w9WgXcQ
✅ 下載完成: data/temp/Rick Astley - Never Gonna Give You Up.mp3

🎤 轉換為逐字稿 (模型: base)...
✅ 轉換完成

💾 儲存逐字稿: data/transcripts/2026-02-07/Rick Astley - Never Gonna Give You Up.txt
✅ 逐字稿已儲存

🧹 清理暫存檔案...
✅ 已刪除: data/temp/Rick Astley - Never Gonna Give You Up.mp3

✅ 轉換完成！
```

### 範例 2：指定檔名和模型

```bash
./scripts/media-tools/video_to_transcript.sh \
  "https://www.youtube.com/watch?v=xxx" \
  --output "2026-Q1-meeting" \
  --model medium
```

### 範例 3：批次處理多個影片

```bash
# 建立批次處理腳本
cat > process_videos.sh << 'EOF'
#!/bin/bash

# 影片清單
videos=(
  "https://www.youtube.com/watch?v=xxx"
  "https://www.youtube.com/watch?v=yyy"
  "https://www.youtube.com/watch?v=zzz"
)

# 對應的檔名
names=(
  "video1"
  "video2"
  "video3"
)

# 批次處理
for i in "${!videos[@]}"; do
  echo "處理第 $((i+1)) 個影片..."
  ./scripts/media-tools/video_to_transcript.sh "${videos[$i]}" --output "${names[$i]}"
done
EOF

chmod +x process_videos.sh
./process_videos.sh
```

## 支援的影音網站

yt-dlp 支援超過 1000+ 個網站，包括：

- YouTube
- Vimeo
- Facebook
- Twitter
- Instagram
- TikTok
- Twitch
- Bilibili
- 等等...

完整清單請參考：https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md

## 疑難排解

### 錯誤：找不到 yt-dlp

```bash
# 安裝 yt-dlp
brew install yt-dlp
```

### 錯誤：找不到 whisper-cli

```bash
# 安裝 whisper-cpp
brew install whisper-cpp
```

### 錯誤：找不到模型檔案

whisper-cpp 第一次使用時會自動下載模型，請確保網路連線正常。

如果下載失敗，可手動下載：

```bash
# 下載 base 模型（預設）
cd /opt/homebrew/share/whisper-cpp/models/
wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin
```

### 下載速度過慢

如果下載 YouTube 影片速度過慢，可以嘗試：

```bash
# 更新 yt-dlp 到最新版本
brew upgrade yt-dlp
```

### 轉錄品質不佳

1. 使用更大的模型（如 `medium` 或 `large`）
2. 確保原始音訊品質良好
3. 避免背景雜音過大的影片

## 注意事項

1. **暫存檔案會自動清理**：mp3 檔案在轉換完成後會自動刪除
2. **逐字稿不會覆蓋**：如果同名檔案存在，需手動刪除
3. **版權遵守**：請確保你有權下載和轉錄該影音內容
4. **網路需求**：首次使用會下載 Whisper 模型（約 100MB - 1.5GB）

## 整合到專案

這些工具已整合到專案中，目錄結構：

```
scripts/media-tools/
├── README.md                         # 本說明文件
├── video_to_transcript.py            # 影音網址轉逐字稿（Python）
├── video_to_transcript.sh            # 影音網址轉逐字稿（Shell）
├── batch_mp3_to_transcript.py        # 批次 MP3 轉逐字稿（Python）
├── batch_mp3_to_transcript.sh        # 批次 MP3 轉逐字稿（Shell）
├── html_to_pdf.py                    # HTML 轉 PDF
└── md_to_pdf_with_chinese.sh         # Markdown 轉 PDF

data/
├── temp/                             # 暫存目錄（已加入 .gitignore）
└── transcripts/                      # 逐字稿目錄（已加入 .gitignore）
```

## 授權

本工具使用的外部套件：

- **yt-dlp**: Unlicense（公共領域）
- **whisper-cpp**: MIT License
- **Whisper 模型**: OpenAI（請遵守使用條款）
