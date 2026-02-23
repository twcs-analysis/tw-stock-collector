# 批次 MP3 轉逐字稿 - 快速開始

## 快速使用

```bash
# 基本使用（轉換所有 2026 年的 mp3 檔案）
./scripts/media-tools/batch_mp3_to_transcript.sh /Users/jasonhuang/yt-video/yt-moneyline
```

## 常用指令

```bash
# 1. 基本使用（使用預設 base 模型）
./scripts/media-tools/batch_mp3_to_transcript.sh /Users/jasonhuang/yt-video/yt-moneyline

# 2. 使用更高準確度的模型（推薦：small）
./scripts/media-tools/batch_mp3_to_transcript.sh /Users/jasonhuang/yt-video/yt-moneyline --model small

# 3. 強制重新轉換已存在的逐字稿
./scripts/media-tools/batch_mp3_to_transcript.sh /Users/jasonhuang/yt-video/yt-moneyline --force

# 4. 組合使用（small 模型 + 強制重新轉換）
./scripts/media-tools/batch_mp3_to_transcript.sh /Users/jasonhuang/yt-video/yt-moneyline --model small --force
```

## 模型選擇建議

| 模型 | 處理時間（79 個檔案） | 準確度 | 建議場景 |
|------|---------------------|--------|---------|
| tiny | ~40 分鐘 | 低 | 快速測試 |
| **base** | ~2 小時 | 中 | **一般使用（預設）** |
| **small** | ~4 小時 | 高 | **推薦使用** |
| medium | ~8 小時 | 很高 | 專業需求 |
| large | ~16 小時 | 最高 | 最高品質需求 |

> 💡 **建議**：第一次使用建議用 `base` 模型快速測試，確認無誤後再用 `small` 模型重新轉換。

## 執行流程

1. **檢查依賴**
   - 自動檢查 whisper-cpp 是否安裝
   - 自動檢查模型檔案是否存在

2. **搜尋檔案**
   - 掃描所有 `2026-*` 目錄
   - 找出所有 `.mp3` 檔案
   - 顯示總檔案數

3. **批次處理**
   - 依序處理每個 mp3 檔案
   - 自動跳過已存在的逐字稿（除非使用 `--force`）
   - 顯示進度（例如：處理中 10/79）
   - 逐字稿保存在原始目錄下（與 mp3 同名，副檔名為 `.txt`）

4. **結果統計**
   - 總檔案數
   - 成功轉換數
   - 跳過檔案數
   - 失敗檔案數（含列表）
   - 總耗時

## 輸出位置

逐字稿會保存在各自的原始目錄下：

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
│   └── ...
```

## 中斷與續傳

- **中斷處理**：按 `Ctrl+C` 可以隨時中斷
- **續傳機制**：再次執行時會自動跳過已轉換的檔案
- **重新轉換**：使用 `--force` 參數強制重新轉換

## 錯誤處理

腳本具備完整的錯誤處理機制：

1. **單一檔案失敗**：記錄錯誤但繼續處理下一個
2. **失敗檔案列表**：處理完成後顯示所有失敗的檔案
3. **錯誤訊息**：顯示詳細的錯誤原因

## 查看詳細說明

```bash
# Python 腳本說明
python3.11 scripts/media-tools/batch_mp3_to_transcript.py --help

# Shell 腳本說明
./scripts/media-tools/batch_mp3_to_transcript.sh --help

# 完整文檔
cat scripts/media-tools/README.md
```

## 疑難排解

### 錯誤：找不到 whisper-cli

```bash
brew install whisper-cpp
```

### 錯誤：找不到模型檔案

```bash
# 檢查模型是否存在
ls /opt/homebrew/share/whisper-cpp/models/

# 如果不存在，重新安裝 whisper-cpp
brew reinstall whisper-cpp
```

### 錯誤：找不到 python3.11

```bash
brew install python@3.11
```

### 轉換速度太慢

1. 使用更小的模型（如 `tiny` 或 `base`）
2. 減少要處理的檔案數量
3. 在效能較好的機器上執行

### 轉錄品質不佳

1. 使用更大的模型（如 `small` 或 `medium`）
2. 檢查原始 mp3 音質
3. 確認音訊語言正確（本工具使用中文）

## 技術細節

- **程式語言**：Python 3.11+
- **轉換引擎**：whisper-cpp（OpenAI Whisper 的 C++ 實作）
- **語言模型**：中文（-l zh）
- **輸出格式**：純文字（.txt）
- **編碼**：UTF-8

## 注意事項

1. ⏰ **時間需求**：158 個檔案使用 base 模型約需 2-3 小時
2. 💻 **資源需求**：轉換過程會佔用較多 CPU 資源
3. 📁 **檔案檢查**：轉換前會檢查是否已存在逐字稿，避免重複轉換
4. 🔄 **可中斷**：隨時可以中斷，下次執行會自動續傳
5. 📊 **結果追蹤**：處理完成後會顯示詳細的統計結果
