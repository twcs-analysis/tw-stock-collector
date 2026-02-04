#!/bin/bash
# ============================================================================
# 回頭買上漲選股報告生成腳本
# ============================================================================

set -e

cd "$(dirname "$0")"

# 取得日期參數（預設為今天）
DATE=${1:-$(date +%Y-%m-%d)}

echo "🚀 生成回頭買上漲選股報告"
echo "日期：$DATE"
echo ""

# 執行 Python 腳本生成 Markdown
python3 generate_report.py --date "$DATE" --no-pdf

# Markdown 檔案路徑
MD_FILE="../../analysis/reports/回頭買上漲/$DATE/回頭買上漲選股報告_$DATE.md"
PDF_FILE="../../analysis/reports/回頭買上漲/$DATE/回頭買上漲選股報告_$DATE.pdf"

# 轉換 PDF（使用 pandoc）
if command -v pandoc &> /dev/null; then
    echo ""
    echo "📄 轉換 PDF..."

    pandoc "$MD_FILE" \
        -o "$PDF_FILE" \
        --pdf-engine=xelatex \
        -V mainfont="PingFang TC" \
        -V geometry:margin=2cm \
        --syntax-definition tango \
        2>/dev/null || {
            echo "⚠️  PDF 轉換失敗，但 Markdown 已成功生成"
            echo "提示：請確認已安裝 xelatex (brew install basictex)"
        }

    if [ -f "$PDF_FILE" ]; then
        echo "✅ PDF 已生成：$PDF_FILE"
        echo ""
        echo "🌐 開啟報告："
        echo "   open $PDF_FILE"
    fi
else
    echo ""
    echo "⚠️  找不到 pandoc，跳過 PDF 轉換"
    echo "安裝方式：brew install pandoc"
fi

echo ""
echo "✅ 完成！"
