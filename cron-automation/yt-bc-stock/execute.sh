#!/usr/bin/env bash
#
# YT BC-Stock 獨立執行腳本
#
# 功能：
#   - 直接執行 BC股市這檔事影片處理流程（不透過 Claude CLI）
#   - 1. 抓取最新影片
#   - 2. 下載影片音訊（MP3）
#   - 3. 轉換為逐字稿
#   - 4. AI 分析並產生報告
#
# 使用方式：
#   ./execute.sh [--date YYYY-MM-DD] [--skip-download] [--skip-transcript]
#

set -e

# 取得腳本所在目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 切換到專案根目錄
cd "$PROJECT_ROOT"

# 解析參數
TARGET_DATE=""
SKIP_DOWNLOAD=""
SKIP_TRANSCRIPT=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --date)
            TARGET_DATE="$2"
            shift 2
            ;;
        --skip-download)
            SKIP_DOWNLOAD="yes"
            shift
            ;;
        --skip-transcript)
            SKIP_TRANSCRIPT="yes"
            shift
            ;;
        *)
            echo "未知參數: $1"
            exit 1
            ;;
    esac
done

# 設定變數
TODAY=$(date '+%Y-%m-%d')
PROCESS_DATE="${TARGET_DATE:-$TODAY}"
TRANSCRIPT_DIR="data/transcripts/yt-bc-stock/$PROCESS_DATE"
mkdir -p "$TRANSCRIPT_DIR"

echo "============================================================"
echo "YT BC-Stock 執行開始"
echo "============================================================"
echo "時間: $(date '+%Y-%m-%d %H:%M:%S')"
echo "專案: $PROJECT_ROOT"
echo "處理日期: $PROCESS_DATE"
echo "參數: skip-download=$SKIP_DOWNLOAD, skip-transcript=$SKIP_TRANSCRIPT"
echo ""

# ============================================================
# Step 1: 抓取最新影片
# ============================================================
echo "[Step 1] 抓取 BC股市這檔事最新影片..."

# 使用 yt-dlp 搜尋最新影片
VIDEO_LIST=$(yt-dlp "ytsearch10:BC股市這檔事" --flat-playlist \
    --print "%(id)s|%(title)s|%(upload_date)s" 2>/dev/null)

if [ -z "$VIDEO_LIST" ]; then
    echo "✗ 無法抓取影片資訊"
    exit 1
fi

# 找出最新的影片（或指定日期的影片）
VIDEO_ID=""
VIDEO_TITLE=""
VIDEO_DATE=""

while IFS='|' read -r vid title upload_date; do
    # 格式化日期 YYYYMMDD -> YYYY-MM-DD
    formatted_date="${upload_date:0:4}-${upload_date:4:2}-${upload_date:6:2}"

    # 如果指定日期，只處理該日期的影片
    if [ -n "$TARGET_DATE" ] && [ "$formatted_date" != "$TARGET_DATE" ]; then
        continue
    fi

    # 找到第一個符合的影片
    VIDEO_ID="$vid"
    VIDEO_TITLE="$title"
    VIDEO_DATE="$formatted_date"
    break
done <<< "$VIDEO_LIST"

# 檢查是否找到影片
if [ -z "$VIDEO_ID" ]; then
    echo "✗ 找不到符合條件的影片"
    exit 1
fi

echo "✓ 已抓取影片"
echo "  影片 ID: $VIDEO_ID"
echo "  標題: $VIDEO_TITLE"
echo "  日期: $VIDEO_DATE"
echo "  網址: https://www.youtube.com/watch?v=$VIDEO_ID"
echo ""

# 更新處理日期為實際影片日期
PROCESS_DATE="$VIDEO_DATE"
TRANSCRIPT_DIR="data/transcripts/yt-bc-stock/$PROCESS_DATE"
mkdir -p "$TRANSCRIPT_DIR"

# ============================================================
# Step 2: 下載影片音訊（MP3）
# ============================================================
if [ -z "$SKIP_DOWNLOAD" ]; then
    echo "[Step 2] 下載影片音訊..."

    MP3_FILE="$TRANSCRIPT_DIR/bc_stock_$(echo $PROCESS_DATE | tr -d '-').mp3"

    if [ -f "$MP3_FILE" ]; then
        echo "⚠️  音訊檔案已存在: $MP3_FILE"
        echo "   跳過下載步驟"
    else
        echo "  下載中..."
        yt-dlp "https://www.youtube.com/watch?v=$VIDEO_ID" \
            -x --audio-format mp3 \
            -o "$MP3_FILE" \
            --quiet --no-warnings

        echo "✓ 音訊下載完成"
        echo "  檔案: $MP3_FILE"
        echo "  大小: $(du -h "$MP3_FILE" | cut -f1)"
    fi
    echo ""
else
    echo "[Step 2] 跳過音訊下載（--skip-download）"
    echo ""
fi

# ============================================================
# Step 3: 轉換為逐字稿
# ============================================================
if [ -z "$SKIP_TRANSCRIPT" ]; then
    echo "[Step 3] 轉換影片為逐字稿..."

    TRANSCRIPT_FILE="$TRANSCRIPT_DIR/bc_stock_$(echo $PROCESS_DATE | tr -d '-').txt"

    if [ -f "$TRANSCRIPT_FILE" ]; then
        echo "⚠️  逐字稿已存在: $TRANSCRIPT_FILE"
        echo "   跳過轉換步驟"
    else
        # 找出 MP3 檔案
        MP3_FILE=$(ls "$TRANSCRIPT_DIR"/*.mp3 2>/dev/null | head -1 || echo "")

        if [ -z "$MP3_FILE" ]; then
            echo "✗ 找不到 MP3 檔案，無法轉換逐字稿"
            exit 1
        fi

        echo "  音訊檔: $MP3_FILE"
        echo "  轉換中（使用 whisper-cpp base 模型）..."

        # 使用 batch_mp3_to_transcript.py 進行轉換
        python3.11 scripts/media-tools/batch_mp3_to_transcript.py \
            "$TRANSCRIPT_DIR" \
            --model base \
            --language zh

        echo "✓ 逐字稿轉換完成"
        echo "  檔案: $TRANSCRIPT_FILE"
        echo "  大小: $(du -h "$TRANSCRIPT_FILE" | cut -f1)"
    fi
    echo ""
else
    echo "[Step 3] 跳過逐字稿轉換（--skip-transcript）"
    echo ""
fi

# ============================================================
# Step 4: AI 分析逐字稿
# ============================================================
echo "[Step 4] AI 分析逐字稿..."

# 找到逐字稿檔案
TRANSCRIPT_FILE=$(ls "$TRANSCRIPT_DIR"/*.txt 2>/dev/null | head -1 || echo "")

if [ -z "$TRANSCRIPT_FILE" ]; then
    echo "✗ 找不到逐字稿檔案"
    exit 1
fi

ANALYSIS_FILE="$TRANSCRIPT_DIR/analysis.md"

# 檢查分析報告是否已存在
if [ -f "$ANALYSIS_FILE" ]; then
    echo "⚠️  分析報告已存在: $ANALYSIS_FILE"
    echo "   跳過分析步驟"
else
    echo "  逐字稿: $TRANSCRIPT_FILE"
    echo "  分析中..."

    # 產生占位分析報告
    cat > "$ANALYSIS_FILE" <<EOF
# BC股市這檔事投資分析報告 - $PROCESS_DATE

## 📺 節目基本資訊

- **播出日期**: $PROCESS_DATE
- **影片標題**: $VIDEO_TITLE
- **影片網址**: https://www.youtube.com/watch?v=$VIDEO_ID

---

## ⚠️ 待完成

此報告尚未完成 AI 深度分析，請使用 Claude Code 執行以下指令：

\`\`\`
請分析以下逐字稿並更新分析報告：
$TRANSCRIPT_FILE
\`\`\`

---

*此占位報告由自動化腳本產生*
*生成時間: $(date '+%Y-%m-%d %H:%M:%S')*
EOF

    echo "✓ 占位報告已產生"
    echo "  報告: $ANALYSIS_FILE"
    echo "  ⚠️  需要使用 Claude Code 進行深度分析"
fi

echo ""

# ============================================================
# 顯示摘要
# ============================================================
echo "============================================================"
echo "⚠️  占位報告已產生，需要使用 Claude Code 進行深度分析"
echo "============================================================"
echo ""
echo "請在 Claude Code 中執行以下指令來完成分析："
echo ""
echo "  /yt-bc-stock $PROCESS_DATE --skip-download"
echo ""
echo "或手動分析逐字稿："
echo "  $TRANSCRIPT_FILE"
echo ""
echo "============================================================"
echo ""

echo "============================================================"
echo "YT BC-Stock 執行完成"
echo "============================================================"
echo "結束時間: $(date '+%Y-%m-%d %H:%M:%S')"
echo "處理日期: $PROCESS_DATE"
echo "影片標題: $VIDEO_TITLE"
echo "檔案位置: $TRANSCRIPT_DIR"
echo "============================================================"
