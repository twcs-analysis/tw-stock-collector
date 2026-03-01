#!/usr/bin/env bash
#
# YT BC-Stock Cron 執行腳本
#
# 功能：
#   - 呼叫 execute.sh 執行 BC股市這檔事處理流程
#   - 管理執行日誌
#   - 適合 crontab 自動化執行
#
# 使用方式：
#   ./run.sh
#
# Crontab 設定範例：
#   0 22 * * * /path/to/tw-stock-collector/cron-automation/yt-bc-stock/run.sh
#

set -e

# 取得腳本所在目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 設定日誌目錄
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"

# 日誌檔案
LOG_FILE="$LOG_DIR/$(date '+%Y-%m-%d').log"

echo "============================================================" | tee -a "$LOG_FILE"
echo "YT BC-Stock Cron 執行" | tee -a "$LOG_FILE"
echo "============================================================" | tee -a "$LOG_FILE"
echo "時間: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
echo "日誌: $LOG_FILE" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 執行處理腳本
"$SCRIPT_DIR/execute.sh" 2>&1 | tee -a "$LOG_FILE"

EXIT_CODE=${PIPESTATUS[0]}

echo "" | tee -a "$LOG_FILE"
echo "============================================================" | tee -a "$LOG_FILE"
echo "執行結束: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
echo "結果: $([ $EXIT_CODE -eq 0 ] && echo '成功' || echo '失敗')" | tee -a "$LOG_FILE"
echo "============================================================" | tee -a "$LOG_FILE"

exit $EXIT_CODE
