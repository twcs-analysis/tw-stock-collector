#!/bin/bash
#
# Revenue Pipeline 自動化執行腳本
#
# 功能：
#   - 自動執行月營收資料處理流程
#   - 智慧收集 → 匯入資料庫 → 展示結果
#   - 日誌自動儲存到 logs/ 目錄（以日期命名）
#
# 使用方式：
#   ./cron-automation/revenue-pipeline/run.sh
#
# Cron 設定範例：
#   # 每天早上 8:30 執行
#   30 8 * * * /Users/jasonhuang/github/personal/tw-stock-collector/cron-automation/revenue-pipeline/run.sh
#
#   # 每月 1-10 號早上 8:30 執行（公告期）
#   30 8 1-10 * * /Users/jasonhuang/github/personal/tw-stock-collector/cron-automation/revenue-pipeline/run.sh
#
# 日誌位置：
#   cron-automation/revenue-pipeline/logs/YYYY-MM-DD.log
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
log "Revenue Pipeline 自動化執行"
log "============================================================"
log "開始時間: $(date '+%Y-%m-%d %H:%M:%S')"
log "專案路徑: $PROJECT_ROOT"
log "日誌檔案: $LOG_FILE"
log ""

# 執行 Claude skill（輸出同時寫入終端和日誌）
claude "/revenue-pipeline" 2>&1 | tee -a "$LOG_FILE"
EXIT_CODE=${PIPESTATUS[0]}

# 記錄結束時間
log ""
log "============================================================"
log "結束時間: $(date '+%Y-%m-%d %H:%M:%S')"
log "執行狀態: $([ $EXIT_CODE -eq 0 ] && echo '✓ 成功' || echo '✗ 失敗 (exit code: '$EXIT_CODE')')"
log "日誌檔案: $LOG_FILE"
log "============================================================"

exit $EXIT_CODE
