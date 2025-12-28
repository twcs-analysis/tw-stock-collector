#!/bin/bash
# 批次驗證 2025 年所有資料
# 使用方式: bash scripts/batch_validate.sh

set -e

YEAR=2025
BASE_DIR="data/raw"
MONTHS=(01 02 03 04 05 06 07 08 09 10 11 12)

echo "開始批次驗證 ${YEAR} 年資料..."
echo ""

for MONTH in "${MONTHS[@]}"; do
    echo "========================================="
    echo "驗證 ${YEAR}-${MONTH}"
    echo "========================================="

    # 找出該月份所有的資料日期
    DATES=$(find "${BASE_DIR}/price/${YEAR}/${MONTH}" -name "*.json" -type f 2>/dev/null | \
            grep -v report | \
            sed 's/.*\///; s/\.json$//' | \
            sort -u)

    if [ -z "$DATES" ]; then
        echo "⚠️  ${YEAR}-${MONTH} 無資料，跳過"
        echo ""
        continue
    fi

    # 逐日驗證
    for DATE in $DATES; do
        echo "正在驗證: $DATE"

        # 使用 Docker 執行驗證
        docker run --rm \
            -v "$(pwd)/data:/app/data" \
            tw-stock-validator \
            python /app/scripts/validate_data.py \
            --date "$DATE" \
            --base-dir /app/data/raw \
            2>&1 | grep -E "(✅|❌|⚠️|驗證)" || true

        echo ""
    done

    echo ""
done

echo "========================================="
echo "批次驗證完成"
echo "========================================="
