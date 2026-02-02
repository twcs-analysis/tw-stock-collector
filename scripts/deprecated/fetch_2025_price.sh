#!/bin/bash

# 2025 年 2-12 月的交易日（預估，實際可能有所不同）
# 由於是未來日期，大部分可能無資料

echo "開始抓取 2025 年 2-12 月 price 資料..."
echo "注意：由於是未來日期，大部分可能無資料"

# 2月 (假設交易日)
for day in 03 04 05 06 07 10 11 12 13 14 17 18 19 20 21 24 25 26 27 28; do
    python scripts/run_collection.py --date 2025-02-$day --types price --skip-trading-day-check 2>&1 | tail -3
    sleep 2
done

# 3月
for day in 03 04 05 06 07 10 11 12 13 14 17 18 19 20 21 24 25 26 27 28 31; do
    python scripts/run_collection.py --date 2025-03-$day --types price --skip-trading-day-check 2>&1 | tail -3
    sleep 2
done

# 4月
for day in 01 02 03 07 08 09 10 11 14 15 16 17 18 21 22 23 24 25 28 29 30; do
    python scripts/run_collection.py --date 2025-04-$day --types price --skip-trading-day-check 2>&1 | tail -3
    sleep 2
done

# 5月
for day in 01 02 05 06 07 08 09 12 13 14 15 16 19 20 21 22 23 26 27 28 29 30; do
    python scripts/run_collection.py --date 2025-05-$day --types price --skip-trading-day-check 2>&1 | tail -3
    sleep 2
done

# 6月
for day in 02 03 04 05 06 09 10 11 12 13 16 17 18 19 20 23 24 25 26 27 30; do
    python scripts/run_collection.py --date 2025-06-$day --types price --skip-trading-day-check 2>&1 | tail -3
    sleep 2
done

# 7月
for day in 01 02 03 04 07 08 09 10 11 14 15 16 17 18 21 22 23 24 25 28 29 30 31; do
    python scripts/run_collection.py --date 2025-07-$day --types price --skip-trading-day-check 2>&1 | tail -3
    sleep 2
done

# 8月
for day in 01 04 05 06 07 08 11 12 13 14 15 18 19 20 21 22 25 26 27 28 29; do
    python scripts/run_collection.py --date 2025-08-$day --types price --skip-trading-day-check 2>&1 | tail -3
    sleep 2
done

# 9月
for day in 01 02 03 04 05 08 09 10 11 12 15 16 17 18 19 22 23 24 25 26 29 30; do
    python scripts/run_collection.py --date 2025-09-$day --types price --skip-trading-day-check 2>&1 | tail -3
    sleep 2
done

# 10月
for day in 01 02 03 06 07 08 09 10 13 14 15 16 17 20 21 22 23 24 27 28 29 30 31; do
    python scripts/run_collection.py --date 2025-10-$day --types price --skip-trading-day-check 2>&1 | tail -3
    sleep 2
done

# 11月
for day in 03 04 05 06 07 10 11 12 13 14 17 18 19 20 21 24 25 26 27 28; do
    python scripts/run_collection.py --date 2025-11-$day --types price --skip-trading-day-check 2>&1 | tail -3
    sleep 2
done

# 12月
for day in 01 02 03 04 05 08 09 10 11 12 15 16 17 18 19 22 23 24 25 26 29 30 31; do
    python scripts/run_collection.py --date 2025-12-$day --types price --skip-trading-day-check 2>&1 | tail -3
    sleep 2
done

echo "=========================================="
echo "2025 年全年 price 資料抓取完成"
echo "=========================================="
