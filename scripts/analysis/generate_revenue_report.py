#!/usr/bin/env python3.11
"""
月營收分析報告生成器

功能：
1. 撈取上個月已公布營收的股票
2. 加入最近交易日收盤價
3. 生成完整 Markdown 報告
4. 包含：完整清單、月增率前50（按年增率排序）、月減率前50（按年增率排序）
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from sqlalchemy import text

# 加入專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from services.common.database.connection import get_db_manager


def calculate_last_month() -> str:
    """計算上個月的年月字串"""
    today = datetime.now()
    last_month = today.replace(day=1) - timedelta(days=1)
    return last_month.strftime('%Y-%m')


def get_latest_trade_date(conn) -> str:
    """取得最近的交易日"""
    query = text("""
    SELECT trade_date
    FROM stock_prices
    ORDER BY trade_date DESC
    LIMIT 1;
    """)
    result = conn.execute(query).fetchone()
    return result[0].strftime('%Y-%m-%d') if result else None


def fetch_revenue_data(conn, year_month: str, trade_date: str) -> list:
    """
    撈取營收資料並加入收盤價

    Returns:
        list of dict: 包含營收和股價的完整資料
    """
    query = text(f"""
    SELECT
        r.stock_id,
        s.stock_name,
        s.market_type,
        r.current_month_revenue,
        ROUND(r.current_month_revenue / 100000.0, 2) AS revenue_billions,
        r.last_month_revenue,
        ROUND(r.mom_change_pct, 2) AS mom_pct,
        r.last_year_revenue,
        ROUND(r.yoy_change_pct, 2) AS yoy_pct,
        r.ytd_revenue,
        ROUND(r.ytd_revenue / 100000.0, 2) AS ytd_billions,
        ROUND(r.ytd_yoy_change_pct, 2) AS ytd_yoy_pct,
        r.note,
        r.collection_date,
        p.close_price
    FROM stock_revenues r
    JOIN stocks s ON r.stock_id = s.stock_id
    LEFT JOIN stock_prices p ON r.stock_id = p.stock_id AND p.trade_date = '{trade_date}'
    WHERE r.year_month = '{year_month}'
        AND r.mom_change_pct IS NOT NULL
    ORDER BY r.mom_change_pct DESC;
    """)

    results = conn.execute(query).fetchall()

    data = []
    for row in results:
        data.append({
            'stock_id': row[0],
            'stock_name': row[1],
            'market_type': row[2],
            'current_month_revenue': row[3],
            'revenue_billions': row[4],
            'last_month_revenue': row[5],
            'mom_pct': row[6],
            'last_year_revenue': row[7],
            'yoy_pct': row[8],
            'ytd_revenue': row[9],
            'ytd_billions': row[10],
            'ytd_yoy_pct': row[11],
            'note': row[12] or '-',
            'collection_date': row[13],
            'close_price': row[14]
        })

    return data


def get_statistics(conn, year_month: str) -> dict:
    """取得統計資訊"""
    query = text(f"""
    SELECT
        COUNT(*) AS total_stocks,
        COUNT(CASE WHEN mom_change_pct > 0 THEN 1 END) AS mom_positive,
        COUNT(CASE WHEN mom_change_pct < 0 THEN 1 END) AS mom_negative,
        ROUND(AVG(mom_change_pct), 2) AS avg_mom_pct,
        ROUND(AVG(yoy_change_pct), 2) AS avg_yoy_pct
    FROM stock_revenues
    WHERE year_month = '{year_month}'
        AND mom_change_pct IS NOT NULL;
    """)

    result = conn.execute(query).fetchone()

    return {
        'total_stocks': result[0],
        'mom_positive': result[1],
        'mom_negative': result[2],
        'avg_mom_pct': result[3],
        'avg_yoy_pct': result[4]
    }


def format_market_type(market_type: str) -> str:
    """格式化市場類型"""
    return '上市' if market_type == 'twse' else '上櫃'


def format_number(value, decimals=2) -> str:
    """格式化數字，處理 None 和極端值"""
    if value is None:
        return '-'
    if abs(value) > 999999:
        return '999,999+'
    return f"{value:,.{decimals}f}"


def format_percentage(value, decimals=2) -> str:
    """格式化百分比"""
    if value is None:
        return '-'
    if abs(value) > 999999:
        return '999,999%' if value > 0 else '-999,999%'
    sign = '+' if value > 0 else ''
    return f"{sign}{value:.{decimals}f}%"


def generate_table_row(stock: dict, rank: int = None) -> str:
    """生成表格行"""
    rank_str = f"| {rank} " if rank else ""

    return (
        f"{rank_str}| {stock['stock_id']} "
        f"| {stock['stock_name']} "
        f"| {format_market_type(stock['market_type'])} "
        f"| {format_number(stock['revenue_billions'])} "
        f"| {format_number(stock['close_price']) if stock['close_price'] else '-'} "
        f"| {format_percentage(stock['mom_pct'])} "
        f"| {format_percentage(stock['yoy_pct'])} "
        f"| {format_number(stock['ytd_billions'])} "
        f"| {format_percentage(stock['ytd_yoy_pct'])} |"
    )


def generate_full_report(data: list, stats: dict, year_month: str, trade_date: str) -> str:
    """生成完整報告"""

    report = f"""# {year_month} 月營收完整報告

**報告生成時間**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**資料期間**：{year_month}
**股價參考日期**：{trade_date}

---

## 📊 資料概況

- **已公布股票數**：{stats['total_stocks']:,} 檔
- **月增率為正**：{stats['mom_positive']:,} 檔（{stats['mom_positive']/stats['total_stocks']*100:.1f}%）
- **月增率為負**：{stats['mom_negative']:,} 檔（{stats['mom_negative']/stats['total_stocks']*100:.1f}%）
- **平均月增率**：{format_percentage(stats['avg_mom_pct'])}
- **平均年增率**：{format_percentage(stats['avg_yoy_pct'])}

---

## 📋 完整清單（按月增率排序）

| 代碼 | 名稱 | 市場 | 當月營收(億) | 收盤價 | 月增率(MoM) | 年增率(YoY) | YTD營收(億) | YTD年增率 |
|------|------|------|--------------|--------|-------------|-------------|-------------|-----------|
"""

    for stock in data:
        report += generate_table_row(stock) + "\n"

    return report


def generate_top50_mom_by_yoy(data: list, year_month: str, trade_date: str) -> str:
    """生成月增率前50名（按年增率排序）"""

    # 篩選月增率 > 0 的股票
    positive_mom = [s for s in data if s['mom_pct'] and s['mom_pct'] > 0]

    # 按年增率排序
    sorted_data = sorted(positive_mom, key=lambda x: x['yoy_pct'] if x['yoy_pct'] else -999999, reverse=True)[:50]

    report = f"""# {year_month} 月增率前50名（按年增率排序）

**報告生成時間**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**篩選條件**：月增率(MoM) > 0
**排序依據**：年增率(YoY) 降序
**股價參考日期**：{trade_date}

---

## 📈 月增 + 年增雙強股票

這些股票不僅月營收較上月成長，且年增率表現優異，顯示持續成長動能。

| 排名 | 代碼 | 名稱 | 市場 | 當月營收(億) | 收盤價 | 月增率(MoM) | 年增率(YoY) | YTD營收(億) | YTD年增率 |
|------|------|------|------|--------------|--------|-------------|-------------|-------------|-----------|
"""

    for idx, stock in enumerate(sorted_data, 1):
        report += generate_table_row(stock, idx) + "\n"

    return report


def generate_bottom50_mom_by_yoy(data: list, year_month: str, trade_date: str) -> str:
    """生成月減率前50名（按年增率排序）"""

    # 篩選月增率 < 0 的股票
    negative_mom = [s for s in data if s['mom_pct'] and s['mom_pct'] < 0]

    # 按年增率排序（由高到低）
    sorted_data = sorted(negative_mom, key=lambda x: x['yoy_pct'] if x['yoy_pct'] else -999999, reverse=True)[:50]

    report = f"""# {year_month} 月減率前50名（按年增率排序）

**報告生成時間**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**篩選條件**：月增率(MoM) < 0
**排序依據**：年增率(YoY) 降序
**股價參考日期**：{trade_date}

---

## 📉 月減但年增表現佳的股票

這些股票雖然月營收較上月衰退，但年增率仍為正值或表現相對較好，可能是短期調整或季節性因素。

| 排名 | 代碼 | 名稱 | 市場 | 當月營收(億) | 收盤價 | 月增率(MoM) | 年增率(YoY) | YTD營收(億) | YTD年增率 |
|------|------|------|------|--------------|--------|-------------|-------------|-------------|-----------|
"""

    for idx, stock in enumerate(sorted_data, 1):
        report += generate_table_row(stock, idx) + "\n"

    return report


def save_report(content: str, filename: str, year_month: str):
    """儲存報告到檔案"""
    # 建立目錄
    output_dir = project_root / 'data' / 'revenue' / year_month
    output_dir.mkdir(parents=True, exist_ok=True)

    # 寫入檔案
    output_path = output_dir / filename
    output_path.write_text(content, encoding='utf-8')

    print(f"✓ 已儲存: {output_path}")
    print(f"  檔案大小: {output_path.stat().st_size:,} bytes")


def main():
    """主程式"""
    print("=" * 60)
    print("月營收分析報告生成器")
    print("=" * 60)

    # 計算上個月
    year_month = calculate_last_month()
    print(f"分析期間: {year_month}")

    # 連接資料庫
    print("\n連接資料庫...")
    db_manager = get_db_manager()
    conn = db_manager.engine.connect()

    # 取得最近交易日
    trade_date = get_latest_trade_date(conn)
    print(f"股價參考日期: {trade_date}")

    # 取得統計資訊
    print("\n取得統計資訊...")
    stats = get_statistics(conn, year_month)
    print(f"  已公布股票數: {stats['total_stocks']:,} 檔")

    # 撈取完整資料
    print("\n撈取營收資料...")
    data = fetch_revenue_data(conn, year_month, trade_date)
    print(f"  成功取得 {len(data):,} 筆資料")

    # 關閉連線
    conn.close()

    # 生成報告
    print("\n生成報告...")

    # 1. 完整報告
    print("  [1/3] 完整清單...")
    full_report = generate_full_report(data, stats, year_month, trade_date)
    save_report(full_report, '完整清單_按月增率排序.md', year_month)

    # 2. 月增率前50（按年增率排序）
    print("  [2/3] 月增率前50（按年增率排序）...")
    top50_report = generate_top50_mom_by_yoy(data, year_month, trade_date)
    save_report(top50_report, '月增率前50_按年增率排序.md', year_month)

    # 3. 月減率前50（按年增率排序）
    print("  [3/3] 月減率前50（按年增率排序）...")
    bottom50_report = generate_bottom50_mom_by_yoy(data, year_month, trade_date)
    save_report(bottom50_report, '月減率前50_按年增率排序.md', year_month)

    print("\n" + "=" * 60)
    print("✓ 所有報告生成完成！")
    print("=" * 60)
    print(f"\n報告位置: data/revenue/{year_month}/")
    print(f"  - 完整清單_按月增率排序.md")
    print(f"  - 月增率前50_按年增率排序.md")
    print(f"  - 月減率前50_按年增率排序.md")


if __name__ == '__main__':
    main()
