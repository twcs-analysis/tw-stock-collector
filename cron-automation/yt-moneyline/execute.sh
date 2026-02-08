#!/bin/bash
#
# YT Moneyline 獨立執行腳本
#
# 功能：
#   - 直接執行錢線百分百影片處理流程（不透過 Claude CLI）
#   - 1. 抓取最新三集影片（上、中、下）
#   - 2. 轉換為逐字稿
#   - 3. AI 分析並產生報告
#   - 4. 產生每日整合摘要
#
# 使用方式：
#   ./execute.sh [--date YYYY-MM-DD] [--skip-transcript] [--parts 1,2,3]
#

set -e

# 取得腳本所在目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 切換到專案根目錄
cd "$PROJECT_ROOT"

# 解析參數
TARGET_DATE=""
SKIP_TRANSCRIPT=""
PARTS="1,2,3"

while [[ $# -gt 0 ]]; do
    case $1 in
        --date)
            TARGET_DATE="$2"
            shift 2
            ;;
        --skip-transcript)
            SKIP_TRANSCRIPT="yes"
            shift
            ;;
        --parts)
            PARTS="$2"
            shift 2
            ;;
        *)
            echo "未知參數: $1"
            exit 1
            ;;
    esac
done

# 設定變數
TODAY=$(date '+%Y-%m-%d')
TRANSCRIPT_DIR="data/transcripts/yt-moneyline/$TODAY"
mkdir -p "$TRANSCRIPT_DIR"

echo "============================================================"
echo "YT Moneyline 執行開始"
echo "============================================================"
echo "時間: $(date '+%Y-%m-%d %H:%M:%S')"
echo "專案: $PROJECT_ROOT"
echo "參數: date=$TARGET_DATE, skip-transcript=$SKIP_TRANSCRIPT, parts=$PARTS"
echo ""

# 將 PARTS 轉換為陣列
IFS=',' read -ra PARTS_ARRAY <<< "$PARTS"

# ============================================================
# Step 1: 抓取最新三集影片
# ============================================================
echo "[Step 1] 抓取錢線百分百最新影片..."

# 使用 yt-dlp 搜尋最新影片（因為頻道 URL 可能變動，使用搜尋較穩定）
VIDEO_LIST=$(yt-dlp "ytsearch15:錢線百分百 完整版" --flat-playlist \
    --print "%(id)s|%(title)s|%(upload_date)s" 2>/dev/null)

if [ -z "$VIDEO_LIST" ]; then
    echo "✗ 無法抓取影片資訊"
    exit 1
fi

# 識別上中下集
declare -A VIDEO_IDS
declare -A VIDEO_TITLES

while IFS='|' read -r vid title upload_date; do
    # 格式化日期 YYYYMMDD -> YYYY-MM-DD
    formatted_date="${upload_date:0:4}-${upload_date:4:2}-${upload_date:6:2}"

    # 如果指定日期，只處理該日期的影片
    if [ -n "$TARGET_DATE" ] && [ "$formatted_date" != "$TARGET_DATE" ]; then
        continue
    fi

    # 識別上中下集
    if [[ $title == *"完整版（上）"* ]] || [[ $title == *"上集"* ]]; then
        VIDEO_IDS[1]="$vid"
        VIDEO_TITLES[1]="$title"
        VIDEO_DATE="$formatted_date"
    elif [[ $title == *"完整版（中）"* ]] || [[ $title == *"中集"* ]]; then
        VIDEO_IDS[2]="$vid"
        VIDEO_TITLES[2]="$title"
        VIDEO_DATE="$formatted_date"
    elif [[ $title == *"完整版（下）"* ]] || [[ $title == *"下集"* ]]; then
        VIDEO_IDS[3]="$vid"
        VIDEO_TITLES[3]="$title"
        VIDEO_DATE="$formatted_date"
    fi

    # 如果已找到三集，停止搜尋
    if [ ${#VIDEO_IDS[@]} -eq 3 ]; then
        break
    fi
done <<< "$VIDEO_LIST"

# 檢查是否找到影片
if [ ${#VIDEO_IDS[@]} -eq 0 ]; then
    echo "✗ 找不到符合條件的影片"
    exit 1
fi

echo "✓ 已抓取影片"
for part in "${!VIDEO_IDS[@]}"; do
    echo "  第 $part 集: ${VIDEO_IDS[$part]}"
    echo "    標題: ${VIDEO_TITLES[$part]}"
    echo "    日期: $VIDEO_DATE"
    echo "    網址: https://www.youtube.com/watch?v=${VIDEO_IDS[$part]}"
done
echo ""

# ============================================================
# Step 2: 轉換為逐字稿（三集分別執行）
# ============================================================
if [ -z "$SKIP_TRANSCRIPT" ]; then
    echo "[Step 2] 轉換影片為逐字稿..."

    for part in "${PARTS_ARRAY[@]}"; do
        part_num=$(echo "$part" | tr -d ' ')

        if [ -z "${VIDEO_IDS[$part_num]}" ]; then
            echo "⚠️  跳過第 $part_num 集（未找到影片）"
            continue
        fi

        echo ""
        echo "處理第 $part_num 集..."

        # 產生輸出檔名
        OUTPUT_NAME="moneyline_$(date '+%Y%m%d')_part${part_num}"
        TRANSCRIPT_FILE="$TRANSCRIPT_DIR/${OUTPUT_NAME}.txt"

        # 檢查逐字稿是否已存在
        if [ -f "$TRANSCRIPT_FILE" ]; then
            echo "⚠️  逐字稿已存在: $TRANSCRIPT_FILE"
            echo "   跳過轉換步驟"
        else
            echo "執行指令: python3.11 scripts/media-tools/video_to_transcript.py"
            python3.11 scripts/media-tools/video_to_transcript.py \
                "https://www.youtube.com/watch?v=${VIDEO_IDS[$part_num]}" \
                --output "$OUTPUT_NAME" \
                --model base

            # video_to_transcript.py 預設輸出到 data/transcripts/{日期}/
            # 需要移動到 skill 專屬目錄
            DEFAULT_OUTPUT="data/transcripts/$TODAY/${OUTPUT_NAME}.txt"
            if [ -f "$DEFAULT_OUTPUT" ] && [ "$DEFAULT_OUTPUT" != "$TRANSCRIPT_FILE" ]; then
                echo "  移動檔案到 skill 目錄..."
                mv "$DEFAULT_OUTPUT" "$TRANSCRIPT_FILE"
            fi

            echo "✓ 第 $part_num 集逐字稿轉換完成"
        fi

        # 檢查檔案大小
        if [ -f "$TRANSCRIPT_FILE" ]; then
            FILE_SIZE=$(du -h "$TRANSCRIPT_FILE" | cut -f1)
            echo "  檔案: $TRANSCRIPT_FILE"
            echo "  大小: $FILE_SIZE"
        fi
    done

    echo ""
else
    echo "[Step 2] 跳過逐字稿轉換（--skip-transcript）"
    echo ""
fi

# ============================================================
# Step 3: AI 分析逐字稿（三集分別執行）
# ============================================================
echo "[Step 3] AI 分析逐字稿..."

ANALYSIS_FILES=()

for part in "${PARTS_ARRAY[@]}"; do
    part_num=$(echo "$part" | tr -d ' ')

    # 找到對應的逐字稿檔案
    TRANSCRIPT_FILE=$(ls "$TRANSCRIPT_DIR"/*_part${part_num}.txt 2>/dev/null | head -1 || echo "")

    if [ -z "$TRANSCRIPT_FILE" ]; then
        echo "⚠️  跳過第 $part_num 集（找不到逐字稿）"
        continue
    fi

    echo ""
    echo "分析第 $part_num 集..."

    TRANSCRIPT_BASENAME=$(basename "$TRANSCRIPT_FILE" .txt)
    ANALYSIS_FILE="$TRANSCRIPT_DIR/${TRANSCRIPT_BASENAME}_analysis.md"

    # 檢查分析報告是否已存在
    if [ -f "$ANALYSIS_FILE" ]; then
        echo "⚠️  分析報告已存在: $ANALYSIS_FILE"
        echo "   跳過分析步驟"
    else
        echo "  逐字稿: $TRANSCRIPT_FILE"
        echo "  分析中..."

        # 產生占位分析報告
        python3.11 "$SCRIPT_DIR/analyze_transcript.py" \
            "$TRANSCRIPT_FILE" \
            "$ANALYSIS_FILE" \
            --part "$part_num"

        echo "✓ 第 $part_num 集占位報告已產生"
        echo "  報告: $ANALYSIS_FILE"
        echo "  ⚠️  需要使用 Claude Code 進行深度分析"
    fi

    ANALYSIS_FILES+=("$ANALYSIS_FILE")
done

echo ""
echo "============================================================"
echo "⚠️  占位報告已產生，需要使用 Claude Code 進行深度分析"
echo "============================================================"
echo ""
echo "請在 Claude Code 中執行以下指令來完成分析："
echo ""
echo "  請分析以下逐字稿並更新分析報告："
for part in "${PARTS_ARRAY[@]}"; do
    part_num=$(echo "$part" | tr -d ' ')
    TRANSCRIPT_FILE=$(ls "$TRANSCRIPT_DIR"/*_part${part_num}.txt 2>/dev/null | head -1 || echo "")
    if [ -n "$TRANSCRIPT_FILE" ]; then
        echo "  - 第 ${part_num} 集: $TRANSCRIPT_FILE"
    fi
done
echo ""
echo "============================================================"
echo ""

# ============================================================
# Step 4: 產生每日整合摘要
# ============================================================
echo "[Step 4] 產生每日整合摘要..."

SUMMARY_FILE="$TRANSCRIPT_DIR/daily_summary.md"

if [ ${#ANALYSIS_FILES[@]} -gt 0 ]; then
    echo "  整合 ${#ANALYSIS_FILES[@]} 份分析報告..."

    # 使用 Python 整合摘要
    python3.11 "$SCRIPT_DIR/analyze_transcript.py" \
        --generate-summary \
        --analysis-files "${ANALYSIS_FILES[@]}" \
        --output "$SUMMARY_FILE"

    echo "✓ 每日摘要完成"
    echo "  檔案: $SUMMARY_FILE"
else
    echo "⚠️  沒有分析報告可整合"
fi

echo ""

# ============================================================
# Step 5: 顯示摘要
# ============================================================
echo "[Step 5] 顯示摘要..."
echo ""

if [ -f "$SUMMARY_FILE" ]; then
    echo "每日整合摘要："
    echo "=========================================="
    head -50 "$SUMMARY_FILE"
    echo "..."
    echo "=========================================="
    echo ""
    echo "完整報告: $SUMMARY_FILE"
else
    echo "⚠️  找不到整合摘要"
fi

echo ""
echo "============================================================"
echo "YT Moneyline 執行完成"
echo "============================================================"
echo "結束時間: $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"
