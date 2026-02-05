#!/bin/bash

# 批次分析多支股票
# 使用方式：bash scripts/gas/batch_analyze.sh

STOCKS=(2330 2317 3008 2454 3167)
DATE="2026-02-05"

echo "開始批次分析 ${#STOCKS[@]} 支股票..."
echo ""

for stock in "${STOCKS[@]}"; do
    echo "▶ 分析 $stock..."
    python3.11 scripts/gas/gas_caller.py --stock-id "$stock" --date "$DATE"
    echo ""
    echo "⏳ 等待 2 秒避免請求過快..."
    sleep 2
    echo ""
done

echo "✅ 批次分析完成！"
