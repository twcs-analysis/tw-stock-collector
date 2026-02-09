#!/bin/bash
#
# 月營收報告生成工具
#
# 功能：
#   - 執行 SQL 查詢生成 Markdown 報告
#   - 自動轉換為 PDF
#
# 使用方式：
#   ./generate_reports.sh [target_month]
#
# 範例：
#   ./generate_reports.sh 2026-01
#   ./generate_reports.sh  # 使用上個月
#

set -e

# 取得腳本所在目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 資料庫設定
export DB_PASSWORD="${DB_PASSWORD:-tw_stock_dev_password_2024}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-tw_stock}"
DB_USER="${DB_USER:-postgres}"

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日誌函式
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 計算目標月份
calculate_target_month() {
    if [ -n "$1" ]; then
        echo "$1"
    else
        # 計算上個月
        local current_year=$(date '+%Y')
        local current_month=$(date '+%m')

        if [ "$current_month" == "01" ]; then
            local target_year=$((current_year - 1))
            local target_month="12"
        else
            local target_year=$current_year
            local target_month=$(printf "%02d" $((10#$current_month - 1)))
        fi

        echo "$target_year-$target_month"
    fi
}

# 執行 SQL 並生成 Markdown
generate_markdown() {
    local sql_file="$1"
    local output_file="$2"
    local target_month="$3"

    log_info "執行 SQL: $sql_file"
    log_info "輸出檔案: $output_file"

    # 建立臨時 SQL 檔案，修改參數
    local temp_sql="/tmp/$(basename "$sql_file")"
    sed "s/'[0-9]\{4\}-[0-9]\{2\}'/'$target_month'/g" "$sql_file" > "$temp_sql"

    # 執行 SQL
    PGPASSWORD="$DB_PASSWORD" psql-17 -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        -f "$temp_sql" -t > "$output_file.tmp"

    # 使用 Python 清理格式（更可靠）
    python3.11 -c "
import sys
with open('$output_file.tmp', 'r', encoding='utf-8') as f:
    lines = f.readlines()

cleaned = []
for line in lines:
    # 移除行尾的空白和 '+'
    line = line.rstrip(' +\n')
    # 移除行首的空白
    line = line.lstrip()
    # 只保留非空行
    if line:
        cleaned.append(line)

# 輸出清理後的內容
with open('$output_file', 'w', encoding='utf-8') as f:
    f.write('\n'.join(cleaned) + '\n')
"

    rm -f "$temp_sql" "$output_file.tmp"

    if [ -s "$output_file" ]; then
        local file_size=$(ls -lh "$output_file" | awk '{print $5}')
        log_info "✓ Markdown 已生成: $output_file ($file_size)"
        return 0
    else
        log_error "✗ Markdown 生成失敗或內容為空"
        return 1
    fi
}

# 轉換為 PDF
convert_to_pdf() {
    local md_file="$1"
    local pdf_file="${md_file%.md}.pdf"

    log_info "轉換 PDF: $md_file → $pdf_file"

    # 建立 PDF 轉換設定
    local config_file="/tmp/md2pdf_config_$(date +%s).json"
    cat > "$config_file" << 'EOF'
{
  "pdf_options": {
    "format": "A4",
    "margin": {
      "top": "20mm",
      "right": "15mm",
      "bottom": "20mm",
      "left": "15mm"
    },
    "printBackground": true,
    "preferCSSPageSize": true
  },
  "stylesheet": [
    "https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.1.0/github-markdown.min.css"
  ],
  "body_class": "markdown-body",
  "css": "body { font-size: 11px; } table { font-size: 10px; width: 100%; table-layout: auto; word-wrap: break-word; } th, td { padding: 4px 6px; } .markdown-body { max-width: none; }"
}
EOF

    # 執行轉換
    cd "$(dirname "$md_file")"
    md-to-pdf --config-file "$config_file" "$(basename "$md_file")" > /dev/null 2>&1
    cd - > /dev/null

    rm -f "$config_file"

    if [ -f "$pdf_file" ]; then
        local file_size=$(ls -lh "$pdf_file" | awk '{print $5}')
        log_info "✓ PDF 已生成: $pdf_file ($file_size)"
        return 0
    else
        log_error "✗ PDF 生成失敗"
        return 1
    fi
}

# 主程式
main() {
    echo "============================================================"
    echo "月營收報告生成工具"
    echo "============================================================"
    echo ""

    # 計算目標月份
    local target_month=$(calculate_target_month "$1")
    log_info "目標月份: $target_month"
    echo ""

    # 報告配置（使用數組代替關聯數組以避免中文鍵值問題）
    local sql_files=(
        "月營收篩選_ETF持股_報告版_v2.sql"
        "月營收篩選_ETF持股_報告版_v3_寬鬆.sql"
    )
    local report_names=(
        "月營收報告_${target_month}_嚴格版"
        "月營收報告_${target_month}_寬鬆版"
    )

    local success_count=0
    local total_count=${#sql_files[@]}

    # 建立輸出目錄（以今天日期命名）
    local today=$(date '+%Y-%m-%d')
    local output_dir="$PROJECT_ROOT/analysis/reports/ETF持股篩選/$today"

    if [ ! -d "$output_dir" ]; then
        mkdir -p "$output_dir"
        log_info "建立輸出目錄: $output_dir"
    fi
    echo ""

    # 生成所有報告
    for i in "${!sql_files[@]}"; do
        local sql_file="${sql_files[$i]}"
        local report_name="${report_names[$i]}"
        local sql_path="$SCRIPT_DIR/$sql_file"
        local md_path="$output_dir/${report_name}.md"

        echo "------------------------------------------------------------"
        log_info "處理報告: $report_name"
        echo ""

        if [ ! -f "$sql_path" ]; then
            log_error "SQL 檔案不存在: $sql_path"
            continue
        fi

        # 生成 Markdown
        if generate_markdown "$sql_path" "$md_path" "$target_month"; then
            # 轉換 PDF
            if convert_to_pdf "$md_path"; then
                ((success_count++))
            fi
        fi

        echo ""
    done

    echo "============================================================"
    echo "報告生成完成"
    echo "============================================================"
    log_info "成功: $success_count / $total_count"
    echo ""

    if [ $success_count -eq $total_count ]; then
        log_info "✓ 所有報告生成成功"
        return 0
    else
        log_warn "⚠ 部分報告生成失敗"
        return 1
    fi
}

# 執行主程式
main "$@"
