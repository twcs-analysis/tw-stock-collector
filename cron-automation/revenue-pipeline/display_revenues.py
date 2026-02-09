#!/usr/bin/env python3.11
"""
月營收資料展示腳本

從資料庫讀取最新月份的營收資料並以格式化方式展示。
"""

import sys
import os
import psycopg2
import random

def main():
    # 從環境變數取得資料庫密碼
    db_password = os.environ.get("DB_PASSWORD", "tw_stock_dev_password_2024")
    sample_size = int(sys.argv[1]) if len(sys.argv) > 1 else 8

    # 連線資料庫
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            dbname="tw_stock",
            user="postgres",
            password=db_password
        )
    except Exception as e:
        print(f"⚠️  資料庫連線失敗: {e}")
        sys.exit(1)

    cur = conn.cursor()

    # 查詢最新月份
    cur.execute("SELECT MAX(year_month) FROM stock_revenues")
    latest_year_month = cur.fetchone()[0]

    if not latest_year_month:
        print("\n⚠️  資料庫中無月營收資料")
        cur.close()
        conn.close()
        sys.exit(0)

    # 查詢該月份的所有資料（包含 ETF 持股資訊）
    cur.execute("""
        WITH etf_holdings_agg AS (
            SELECT
                distinct_holdings.stock_id,
                COUNT(DISTINCT distinct_holdings.etf_id) AS etf_count,
                STRING_AGG(distinct_holdings.etf_id || ':' || e.etf_name, ', ' ORDER BY distinct_holdings.etf_id) AS etf_detail
            FROM (
                SELECT DISTINCT eh.stock_id, eh.etf_id
                FROM etf_holdings eh
                WHERE eh.snapshot_date = (SELECT MAX(snapshot_date) FROM etf_holdings)
            ) AS distinct_holdings
            INNER JOIN etfs e ON distinct_holdings.etf_id = e.etf_id
            GROUP BY distinct_holdings.stock_id
        )
        SELECT r.stock_id, s.stock_name, s.market_type,
               r.current_month_revenue, r.last_month_revenue, r.last_year_revenue,
               r.mom_change_pct, r.yoy_change_pct,
               r.ytd_revenue, r.ytd_yoy_change_pct,
               r.collection_date, r.note,
               COALESCE(etf.etf_count, 0) AS etf_count,
               COALESCE(etf.etf_detail, '-') AS etf_detail
        FROM stock_revenues r
        JOIN stocks s ON r.stock_id = s.stock_id
        LEFT JOIN etf_holdings_agg etf ON r.stock_id = etf.stock_id
        WHERE r.year_month = %s
        ORDER BY r.current_month_revenue DESC
    """, (latest_year_month,))

    all_data = cur.fetchall()
    total_count = len(all_data)

    if total_count == 0:
        print(f"\n⚠️  {latest_year_month} 目前無月營收資料")
        cur.close()
        conn.close()
        sys.exit(0)

    # 隨機挑選
    actual_sample_size = min(sample_size, total_count)
    sample_data = random.sample(all_data, actual_sample_size)

    print(f"\n最新月份營收資料 ({latest_year_month}) - 隨機展示 {actual_sample_size} 檔")
    print(f"{'='*80}\n")

    # 表格標題
    print(f"| {'代碼':<6} | {'名稱':<10} | {'市場':<4} | {'當月營收(億)':>12} | {'月增率':>8} | {'年增率':>9} | {'YTD營收(億)':>12} | {'YTD年增率':>10} | {'ETF數':>6} |")
    print(f"|{'-'*8}|{'-'*12}|{'-'*6}|{'-'*14}|{'-'*10}|{'-'*11}|{'-'*14}|{'-'*12}|{'-'*8}|")

    for row in sample_data:
        stock_id, stock_name, market_type, revenue, last_month_rev, last_year_rev, mom, yoy, ytd_revenue, ytd_yoy, collection_date, note, etf_count, etf_detail = row

        # 市場類型轉換
        market_display = "上市" if market_type == "twse" else "上櫃"

        # 千元轉億元
        revenue_billion = float(revenue) / 100000 if revenue else 0
        ytd_revenue_billion = float(ytd_revenue) / 100000 if ytd_revenue else 0

        # 格式化百分比
        mom_str = f"{float(mom):+.2f}%" if mom is not None else "N/A"
        yoy_str = f"{float(yoy):+.2f}%" if yoy is not None else "N/A"
        ytd_yoy_str = f"{float(ytd_yoy):+.2f}%" if ytd_yoy is not None else "N/A"

        # ETF 數量
        etf_count_display = str(int(etf_count)) if etf_count else "0"

        print(f"| {stock_id:<6} | {stock_name:<10} | {market_display:<4} | {revenue_billion:>12,.0f} | {mom_str:>8} | {yoy_str:>9} | {ytd_revenue_billion:>12,.0f} | {ytd_yoy_str:>10} | {etf_count_display:>6} |")

    print(f"\n{'='*80}\n")

    # 詳細資料（前 3 檔）
    print("詳細資料（前 3 檔）：\n")
    for i, row in enumerate(sample_data[:3], 1):
        stock_id, stock_name, market_type, revenue, last_month_rev, last_year_rev, mom, yoy, ytd_revenue, ytd_yoy, collection_date, note, etf_count, etf_detail = row

        market_display = "上市" if market_type == "twse" else "上櫃"
        revenue_billion = float(revenue) / 100000 if revenue else 0
        last_month_billion = float(last_month_rev) / 100000 if last_month_rev else 0
        last_year_billion = float(last_year_rev) / 100000 if last_year_rev else 0
        ytd_revenue_billion = float(ytd_revenue) / 100000 if ytd_revenue else 0

        print(f"[{i}] {stock_id} {stock_name} ({market_display})")
        print(f"    當月營收: {float(revenue):,.0f} 千元 ({revenue_billion:,.2f} 億)")

        if last_month_rev and mom is not None:
            print(f"    上月營收: {float(last_month_rev):,.0f} 千元 ({last_month_billion:,.2f} 億) | 月增率: {float(mom):+.2f}%")
        if last_year_rev and yoy is not None:
            print(f"    去年同期: {float(last_year_rev):,.0f} 千元 ({last_year_billion:,.2f} 億) | 年增率: {float(yoy):+.2f}%")
        if ytd_revenue:
            ytd_yoy_display = f" | YTD年增率: {float(ytd_yoy):+.2f}%" if ytd_yoy is not None else ""
            print(f"    年初至今: {float(ytd_revenue):,.0f} 千元 ({ytd_revenue_billion:,.2f} 億){ytd_yoy_display}")

        # ETF 持股資訊
        if etf_count and int(etf_count) > 0:
            # 風險等級
            etf_num = int(etf_count)
            if etf_num >= 4:
                risk_level = "低風險"
            elif etf_num >= 2:
                risk_level = "中風險"
            elif etf_num == 1:
                risk_level = "中高風險"
            else:
                risk_level = "高風險"

            print(f"    ETF 持股: {etf_num} 個 ({risk_level}) | {etf_detail}")
        else:
            print(f"    ETF 持股: 0 個 (高風險) | 未被 ETF 持有")

        note_display = note if (note and note.strip() and note.strip() != '-') else "-"
        print(f"    收集日期: {collection_date} | 備註: {note_display}")
        print()

    print(f"{'='*80}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
