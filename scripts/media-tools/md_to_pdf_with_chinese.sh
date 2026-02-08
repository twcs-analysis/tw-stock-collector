#!/bin/bash
# Markdown 轉 PDF（支援繁體中文）
# 使用方式: ./md_to_pdf_with_chinese.sh <input.md> [output.pdf]

set -e

if [ $# -lt 1 ]; then
    echo "使用方式: $0 <input.md> [output.pdf]"
    exit 1
fi

INPUT_MD="$1"
OUTPUT_PDF="${2:-${INPUT_MD%.md}.pdf}"

# 檢查檔案是否存在
if [ ! -f "$INPUT_MD" ]; then
    echo "✗ 找不到檔案: $INPUT_MD"
    exit 1
fi

echo "============================================================"
echo "Markdown → PDF 轉換（繁體中文支援）"
echo "============================================================"
echo "輸入: $INPUT_MD"
echo "輸出: $OUTPUT_PDF"
echo ""

# 暫存 HTML 檔案
TEMP_HTML="${INPUT_MD%.md}_temp.html"

# Step 1: 使用 pandoc 轉換為 HTML（加入中文字體 CSS）
echo "[1/2] 轉換 Markdown → HTML..."

pandoc "$INPUT_MD" -o "$TEMP_HTML" \
    --standalone \
    --metadata title="$(basename "$INPUT_MD" .md)" \
    --css <(cat <<'EOF'
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700&family=Noto+Serif+TC:wght@400;700&display=swap');

body {
    font-family: 'Noto Sans TC', 'PingFang TC', 'Microsoft JhengHei', sans-serif;
    line-height: 1.8;
    max-width: 900px;
    margin: 40px auto;
    padding: 20px;
    color: #333;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Noto Serif TC', 'PingFang TC', serif;
    color: #1a1a1a;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
}

h1 { font-size: 2em; border-bottom: 3px solid #0066cc; padding-bottom: 0.3em; }
h2 { font-size: 1.5em; border-bottom: 2px solid #0099ff; padding-bottom: 0.2em; }
h3 { font-size: 1.3em; color: #0066cc; }

table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
}

th, td {
    border: 1px solid #ddd;
    padding: 12px;
    text-align: left;
}

th {
    background-color: #f5f5f5;
    font-weight: bold;
}

code {
    font-family: 'Monaco', 'Consolas', monospace;
    background-color: #f5f5f5;
    padding: 2px 6px;
    border-radius: 3px;
}

pre {
    background-color: #f5f5f5;
    padding: 15px;
    border-radius: 5px;
    overflow-x: auto;
}

blockquote {
    border-left: 4px solid #0066cc;
    padding-left: 20px;
    margin-left: 0;
    color: #666;
    font-style: italic;
}

strong {
    color: #d63031;
    font-weight: 700;
}

ul, ol {
    line-height: 1.8;
}
EOF
)

if [ ! -f "$TEMP_HTML" ]; then
    echo "✗ HTML 轉換失敗"
    exit 1
fi

echo "✓ HTML 已產生: $TEMP_HTML"

# Step 2: 使用 weasyprint 轉換為 PDF
echo "[2/2] 轉換 HTML → PDF..."

python3.11 -m weasyprint "$TEMP_HTML" "$OUTPUT_PDF" 2>&1 | grep -v "WARNING" || true

if [ -f "$OUTPUT_PDF" ]; then
    FILE_SIZE=$(du -h "$OUTPUT_PDF" | cut -f1)
    echo "✓ PDF 已產生: $OUTPUT_PDF ($FILE_SIZE)"

    # 清理暫存檔案
    # rm -f "$TEMP_HTML"
    echo "  (保留暫存 HTML: $TEMP_HTML)"
else
    echo "✗ PDF 轉換失敗"
    exit 1
fi

echo ""
echo "============================================================"
echo "✓ 轉換完成"
echo "============================================================"
echo ""
echo "建議使用瀏覽器開啟 HTML 檔案來檢查格式："
echo "  open $TEMP_HTML"
echo ""
