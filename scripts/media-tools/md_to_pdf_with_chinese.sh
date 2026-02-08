#!/bin/bash
# Markdown 轉 PDF（支援繁體中文）
# 使用 md-to-pdf（基於 Puppeteer/Chrome）
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

# 檢查 md-to-pdf 是否安裝
if ! command -v md-to-pdf &> /dev/null; then
    echo "✗ 找不到 md-to-pdf 工具"
    echo "請先安裝: npm install -g md-to-pdf"
    exit 1
fi

echo "============================================================"
echo "Markdown → PDF 轉換（繁體中文支援）"
echo "============================================================"
echo "輸入: $INPUT_MD"
echo "輸出: $OUTPUT_PDF"
echo ""

# 取得輸入檔案的目錄
INPUT_DIR=$(dirname "$INPUT_MD")
INPUT_FILE=$(basename "$INPUT_MD")

# 切換到輸入檔案目錄（避免路徑問題）
cd "$INPUT_DIR"

# 使用 md-to-pdf 轉換
echo "[1/1] 轉換 Markdown → PDF..."

md-to-pdf \
    --css "body { font-family: 'PingFang TC', 'Microsoft JhengHei', 'Noto Sans TC', sans-serif; line-height: 1.6; max-width: 1200px; margin: 40px auto; padding: 20px; } h1, h2, h3 { color: #2c3e50; } h1 { border-bottom: 3px solid #3498db; padding-bottom: 10px; } h2 { border-bottom: 2px solid #3498db; padding-bottom: 8px; } table { border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 0.9em; } th, td { border: 1px solid #ddd; padding: 8px; text-align: left; } th { background-color: #f2f2f2; font-weight: bold; color: #2c3e50; } tr:nth-child(even) { background-color: #f9f9f9; } strong { color: #e74c3c; } code { background-color: #f4f4f4; padding: 2px 6px; border-radius: 3px; }" \
    "$INPUT_FILE"

if [ -f "$(basename "$OUTPUT_PDF")" ]; then
    FILE_SIZE=$(du -h "$(basename "$OUTPUT_PDF")" | cut -f1)
    echo "✓ PDF 已產生: $OUTPUT_PDF ($FILE_SIZE)"
else
    echo "✗ PDF 轉換失敗"
    exit 1
fi

echo ""
echo "============================================================"
echo "✓ 轉換完成"
echo "============================================================"
echo ""
