#!/bin/bash
#
# YT Finance Show 獨立執行腳本
#
# 功能：
#   - 直接執行理財達人秀影片處理流程（不透過 Claude CLI）
#   - 1. 抓取最新影片
#   - 2. 轉換為逐字稿
#   - 3. AI 分析並產生報告
#
# 使用方式：
#   ./execute.sh [--video-id VIDEO_ID] [--skip-transcript]
#

set -e

# 取得腳本所在目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 切換到專案根目錄
cd "$PROJECT_ROOT"

# 解析參數
VIDEO_ID=""
SKIP_TRANSCRIPT=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --video-id)
            VIDEO_ID="$2"
            shift 2
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
TRANSCRIPT_DIR="data/transcripts/yt-finance-show/$TODAY"

echo "============================================================"
echo "YT Finance Show 執行開始"
echo "============================================================"
echo "時間: $(date '+%Y-%m-%d %H:%M:%S')"
echo "專案: $PROJECT_ROOT"
echo "參數: video-id=$VIDEO_ID, skip-transcript=$SKIP_TRANSCRIPT"
echo ""

# ============================================================
# Step 1: 抓取最新影片（如果沒有指定 video-id）
# ============================================================
if [ -z "$VIDEO_ID" ]; then
    echo "[Step 1] 抓取理財達人秀最新影片..."

    # 使用 yt-dlp 抓取最新「電視完整版」影片（優先）
    VIDEO_INFO=$(yt-dlp --flat-playlist --print "%(id)s|%(title)s|%(upload_date)s" \
        "https://www.youtube.com/@EBCmoneyshow/videos" 2>/dev/null | grep "電視完整版" | head -1)

    # 如果沒有完整版，則抓取最新影片
    if [ -z "$VIDEO_INFO" ]; then
        echo "⚠️  找不到「電視完整版」，改抓最新影片..."
        VIDEO_INFO=$(yt-dlp --flat-playlist --print "%(id)s|%(title)s|%(upload_date)s" \
            "https://www.youtube.com/@EBCmoneyshow/videos" 2>/dev/null | head -1)
    fi

    if [ -z "$VIDEO_INFO" ]; then
        echo "✗ 無法抓取影片資訊"
        exit 1
    fi

    VIDEO_ID=$(echo "$VIDEO_INFO" | cut -d'|' -f1)
    VIDEO_TITLE=$(echo "$VIDEO_INFO" | cut -d'|' -f2)
    UPLOAD_DATE=$(echo "$VIDEO_INFO" | cut -d'|' -f3)

    # 格式化日期 YYYYMMDD -> YYYY-MM-DD
    UPLOAD_DATE_FORMATTED="${UPLOAD_DATE:0:4}-${UPLOAD_DATE:4:2}-${UPLOAD_DATE:6:2}"

    echo "✓ 已抓取最新影片"
    echo "  影片 ID: $VIDEO_ID"
    echo "  標題: $VIDEO_TITLE"
    echo "  日期: $UPLOAD_DATE_FORMATTED"
    echo "  網址: https://www.youtube.com/watch?v=$VIDEO_ID"
    echo ""
else
    echo "[Step 1] 使用指定影片 ID: $VIDEO_ID"
    echo ""
fi

# ============================================================
# Step 2: 轉換為逐字稿
# ============================================================
if [ -z "$SKIP_TRANSCRIPT" ]; then
    echo "[Step 2] 轉換影片為逐字稿..."

    # 產生輸出檔名（使用今天日期）
    OUTPUT_NAME="finance_show_$(date '+%Y%m%d')"

    # 檢查逐字稿是否已存在
    TRANSCRIPT_FILE="$TRANSCRIPT_DIR/${OUTPUT_NAME}.txt"

    if [ -f "$TRANSCRIPT_FILE" ]; then
        echo "⚠️  逐字稿已存在: $TRANSCRIPT_FILE"
        echo "   跳過轉換步驟"
    else
        echo "執行指令: python3.11 scripts/media-tools/video_to_transcript.py"
        python3.11 scripts/media-tools/video_to_transcript.py \
            "https://www.youtube.com/watch?v=$VIDEO_ID" \
            --output "$OUTPUT_NAME" \
            --model base

        echo "✓ 逐字稿轉換完成"
    fi

    # 檢查檔案大小
    if [ -f "$TRANSCRIPT_FILE" ]; then
        FILE_SIZE=$(du -h "$TRANSCRIPT_FILE" | cut -f1)
        echo "  檔案: $TRANSCRIPT_FILE"
        echo "  大小: $FILE_SIZE"
    fi
    echo ""
else
    echo "[Step 2] 跳過逐字稿轉換（--skip-transcript）"
    echo ""
fi

# ============================================================
# Step 3: AI 分析逐字稿
# ============================================================
echo "[Step 3] AI 分析逐字稿..."

# 找到最新的逐字稿檔案
LATEST_TRANSCRIPT=$(ls -t "$TRANSCRIPT_DIR"/*.txt 2>/dev/null | head -1 || echo "")

if [ -z "$LATEST_TRANSCRIPT" ]; then
    echo "✗ 找不到逐字稿檔案"
    exit 1
fi

TRANSCRIPT_BASENAME=$(basename "$LATEST_TRANSCRIPT" .txt)
ANALYSIS_FILE="$TRANSCRIPT_DIR/${TRANSCRIPT_BASENAME}_analysis.md"

# 檢查分析報告是否已存在
if [ -f "$ANALYSIS_FILE" ]; then
    echo "⚠️  分析報告已存在: $ANALYSIS_FILE"
    echo "   跳過分析步驟"
else
    echo "  逐字稿: $LATEST_TRANSCRIPT"
    echo "  分析中..."

    # 使用 Python 執行 AI 分析
    python3.11 "$SCRIPT_DIR/analyze_transcript.py" \
        "$LATEST_TRANSCRIPT" \
        "$ANALYSIS_FILE"

    echo "✓ AI 分析完成"
    echo "  報告: $ANALYSIS_FILE"
fi

echo ""

# ============================================================
# Step 4: 顯示摘要
# ============================================================
echo "[Step 4] 顯示摘要..."
echo ""

if [ -f "$ANALYSIS_FILE" ]; then
    # 提取前幾行作為摘要
    echo "分析報告預覽："
    echo "=========================================="
    head -30 "$ANALYSIS_FILE"
    echo "..."
    echo "=========================================="
    echo ""
    echo "完整報告: $ANALYSIS_FILE"
else
    echo "⚠️  找不到分析報告"
fi

echo ""
echo "============================================================"
echo "YT Finance Show 執行完成"
echo "============================================================"
echo "結束時間: $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"
