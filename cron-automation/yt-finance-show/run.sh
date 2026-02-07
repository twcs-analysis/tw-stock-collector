#!/bin/bash
#
# YT Finance Show 自動化執行腳本
#
# 功能：
#   - 自動執行理財達人秀影片處理流程
#   - 抓取最新影片 → 轉換逐字稿 → AI 分析
#   - 日誌自動儲存到 logs/ 目錄（以日期命名）
#
# 使用方式：
#   ./cron-automation/yt-finance-show/run.sh
#
# Cron 設定範例：
#   # 每天晚上 22:00 執行（理財達人秀通常晚上 8-9 點播出）
#   0 22 * * * /Users/jasonhuang/github/personal/tw-stock-collector/cron-automation/yt-finance-show/run.sh
#
#   # 每週一到五晚上 22:00 執行
#   0 22 * * 1-5 /Users/jasonhuang/github/personal/tw-stock-collector/cron-automation/yt-finance-show/run.sh
#
# 日誌位置：
#   cron-automation/yt-finance-show/logs/YYYY-MM-DD.log
#

set -e

# 取得腳本所在目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 日誌目錄和檔案
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/$(date '+%Y-%m-%d').log"

# 確保日誌目錄存在
mkdir -p "$LOG_DIR"

# 定義日誌函式（同時輸出到終端和檔案）
log() {
    echo "$@" | tee -a "$LOG_FILE"
}

# 切換到專案根目錄
cd "$PROJECT_ROOT"

# 設定環境變數
export CLAUDE_TRUST_WORKSPACE=1

# 記錄開始時間
log "============================================================"
log "YT Finance Show 自動化執行"
log "============================================================"
log "開始時間: $(date '+%Y-%m-%d %H:%M:%S')"
log "專案路徑: $PROJECT_ROOT"
log "日誌檔案: $LOG_FILE"
log ""

# 執行獨立腳本（輸出同時寫入終端和日誌）
"$SCRIPT_DIR/execute.sh" 2>&1 | tee -a "$LOG_FILE"
EXIT_CODE=${PIPESTATUS[0]}

# 記錄結束時間
log ""
log "============================================================"
log "結束時間: $(date '+%Y-%m-%d %H:%M:%S')"
log "執行狀態: $([ $EXIT_CODE -eq 0 ] && echo '✓ 成功' || echo '✗ 失敗 (exit code: '$EXIT_CODE')')"
log "日誌檔案: $LOG_FILE"
log "============================================================"

exit $EXIT_CODE
