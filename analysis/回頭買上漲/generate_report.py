#!/usr/bin/env python3
"""
回頭買上漲選股報告生成器

功能：
1. 執行選股 SQL 查詢
2. 生成 Markdown 格式報告
3. 儲存到 analysis/reports/回頭買上漲/{日期}/
"""

import subprocess
from datetime import datetime
from pathlib import Path

# 資料庫連線設定
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'tw_stock',
    'user': 'postgres'
}

MARKDOWN_TEMPLATE = """# 回頭買上漲選股報告

---

**分析日期**: {trade_date}
**報告生成時間**: {report_time}
**選股策略**: 回檔縮量後突破買進
**篩選結果**: {stock_count} 檔

---

## 📊 策略說明

### 核心邏輯

在多頭趨勢中，股價短暫回檔並縮量整理後，重新站上均線突破的買點。

### 七大篩選條件

| 條件 | 說明 | 目的 |
|------|------|------|
| A. 頭頭高底底高 | 近5天高低點 > 前5天高低點 | 確認上升趨勢 |
| B. 月線支撐 | 收盤 > MA20 且未破前低 | 支撐有效 |
| C. 紅K站5均 | 收盤 > 開盤 且 > MA5 | 轉強訊號 |
| D. 過昨日高 | 收盤 > 昨日最高 | 突破確認 |
| E. 月線向上 | MA20 斜率 > 0 | 趨勢強度 |
| F. 縮量40-70% | 量比 0.4-0.7 | 健康回檔 |
| G. 收相對高點 | 收盤位置 ≥ 65% | 下檔有撐 |

### 三層防護機制

- ✅ 排除「價跌量不減」的出貨型態
- ✅ 多頭排列確認（MA5 > MA20 > MA60）
- ✅ 流動性保護（量能要求）

---

## 🎯 推薦標的

{stock_list}

---

## 📈 技術指標詳情

{stock_details}

---

## ⚠️ 風險提示與投資建議

1. **本報告僅供參考，不構成投資建議**
2. 技術分析需搭配基本面、籌碼面、消息面綜合判斷
3. 建議設定停損停利點，控制風險
4. **停損建議**：跌破月線（MA20）或跌幅超過 5%
5. **停利建議**：獲利 10-15% 或出現放量長上影線
6. 回檔買進策略適合波段操作，不適合當沖
7. 建議分批進場，降低風險
8. 投資前請詳閱公開資訊觀測站的公司財報
9. **投資有風險，請謹慎評估自身風險承受能力**

---

*本報告由台股資料收集系統 - 回頭買上漲策略自動生成*
*資料來源：台灣證交所 + 自建技術分析系統*
"""


def run_sql_query(trade_date: str) -> list:
    """執行 SQL 查詢並返回結果"""

    # 讀取 selector.sql
    sql_file = Path(__file__).parent / 'selector.sql'
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql = f.read()

    # 替換日期
    sql = sql.replace("'2026-02-03'::date", f"'{trade_date}'::date")

    # 透過 Docker 執行 SQL
    cmd = [
        'docker', 'exec', '-i', 'tw-stock-postgres',
        'psql', '-U', 'postgres', '-d', 'tw_stock',
        '-F', '\t',  # Tab 分隔
        '--no-align',  # 不對齊
        '-c', sql
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ SQL 執行失敗：{result.stderr}")
        return []

    # 解析結果
    lines = result.stdout.strip().split('\n')
    if len(lines) < 2:
        return []

    headers = lines[0].split('\t')
    stocks = []

    for line in lines[1:]:
        values = line.split('\t')
        if len(values) == len(headers):
            stock = dict(zip(headers, values))
            stocks.append(stock)

    return stocks


def format_stock_summary(stocks: list) -> str:
    """格式化股票摘要列表"""

    lines = ["| 代號 | 名稱 | 市場 | 收盤價 | 漲跌% | 量比 | 月線斜率% | 收盤位置 |"]
    lines.append("|------|------|------|--------|-------|------|-----------|----------|")

    for stock in stocks:
        close_pos_pct = int(float(stock['收盤位置']) * 100)
        market_zh = '上市' if stock['市場別'] == 'twse' else '上櫃'
        line = f"| {stock['股票代號']} | {stock['股票名稱']} | {market_zh} | {stock['收盤價']} | {stock['日漲跌%']} | {stock['量比']} | {stock['月線斜率%']} | {close_pos_pct}% |"
        lines.append(line)

    return '\n'.join(lines)


def format_stock_detail(stock: dict, index: int) -> str:
    """格式化單一股票詳細資訊"""

    close_pos_pct = int(float(stock['收盤位置']) * 100)
    volume_k = int(float(stock['成交量(張)']))
    market_zh = '上市' if stock['市場別'] == 'twse' else '上櫃'

    # 計算 MA5 和 MA20
    close_price = float(stock['收盤價'])
    dist_ma5 = float(stock['距MA5%'])
    dist_ma20 = float(stock['距MA20%'])

    ma5 = round(close_price / (1 + dist_ma5/100), 2)
    ma20 = round(close_price / (1 + dist_ma20/100), 2)

    detail = f"""### {index}. {stock['股票代號']} - {stock['股票名稱']}

**市場別**: {market_zh}
**收盤價**: {stock['收盤價']} 元
**日漲跌**: {stock['日漲跌%']}%
**成交量**: {volume_k:,} 張
**量比**: {stock['量比']}
**收盤位置**: {close_pos_pct}%

#### 技術指標

| 指標 | 數值 | 說明 |
|------|------|------|
| MA5 | {ma5} | 距離 {stock['距MA5%']}% |
| MA20 (月線) | {ma20} | 距離 {stock['距MA20%']}% / 斜率 {stock['月線斜率%']}% |
| 多頭排列 | MA5 > MA20 > MA60 | ✓ 確認 |
| 趨勢確認 | 頭高底高 | ✓ 上升趨勢 |
| 突破訊號 | 紅K站5均 + 過昨高 | ✓ 轉強 |
| 量能狀態 | 縮量 {stock['量比']} | ✓ 健康回檔 |

#### 條件檢查

- {stock['A_頭高']} 頭頭高
- {stock['A_底高']} 底底高
- {stock['B_月線支撐']} 月線支撐
- {stock['C_紅K站5均']} 紅K站5均
- {stock['D_過昨高']} 過昨日高
- {stock['E_月線↑']} 月線向上
- {stock['F_縮量']} 縮量40-70%
- {stock['G_收高點']} 收相對高點

---
"""

    return detail


def generate_markdown_report(trade_date: str, output_dir: Path) -> Path:
    """生成 Markdown 報告"""

    print(f"📊 開始生成 {trade_date} 的選股報告...")

    # 執行 SQL 查詢
    stocks = run_sql_query(trade_date)

    if not stocks:
        print("❌ 沒有符合條件的股票")
        return None

    print(f"✅ 找到 {len(stocks)} 支符合條件的股票")

    # 生成摘要表格
    stock_list = format_stock_summary(stocks)

    # 生成詳細資訊
    stock_details = '\n'.join([
        format_stock_detail(stock, i+1)
        for i, stock in enumerate(stocks)
    ])

    # 生成完整 Markdown
    markdown = MARKDOWN_TEMPLATE.format(
        trade_date=trade_date,
        report_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        stock_count=len(stocks),
        stock_list=stock_list,
        stock_details=stock_details
    )

    # 建立輸出目錄
    output_dir.mkdir(parents=True, exist_ok=True)

    # 儲存 Markdown
    md_file = output_dir / f'回頭買上漲選股報告_{trade_date}.md'
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(markdown)

    print(f"✅ Markdown 報告已儲存：{md_file}")

    return md_file


def convert_to_pdf(md_file: Path) -> Path:
    """將 Markdown 轉換為 PDF (使用專案的 markdown_to_pdf.py 工具)"""

    pdf_file = md_file.with_suffix('.pdf')

    print(f"📄 轉換 PDF：{md_file.name} -> {pdf_file.name}")

    # 使用專案的 markdown_to_pdf.py 工具
    project_root = Path(__file__).parent.parent.parent
    converter_script = project_root / 'scripts' / 'common-tools' / 'markdown_to_pdf.py'

    if not converter_script.exists():
        print(f"⚠️  找不到轉換工具：{converter_script}")
        print("請確認 scripts/common-tools/markdown_to_pdf.py 存在")
        return None

    try:
        # 呼叫轉換腳本（非互動模式）
        result = subprocess.run(
            ['python3', str(converter_script), str(md_file)],
            capture_output=True,
            text=True,
            input='n\n'  # 自動回答 "不開啟 PDF"
        )

        if result.returncode != 0:
            print(f"❌ PDF 轉換失敗：{result.stderr}")
            return None

        if not pdf_file.exists():
            print(f"❌ PDF 檔案未生成")
            return None

        # 取得檔案大小
        file_size = pdf_file.stat().st_size / 1024
        print(f"✅ PDF 已生成：{pdf_file.name} ({file_size:.1f} KB)")
        return pdf_file

    except Exception as e:
        print(f"❌ 轉換過程發生錯誤：{e}")
        return None


def main():
    """主程式"""
    import argparse

    parser = argparse.ArgumentParser(description='生成回頭買上漲選股報告')
    parser.add_argument('--date', type=str, help='查詢日期 (YYYY-MM-DD)，預設為今天')
    parser.add_argument('--no-pdf', action='store_true', help='只生成 Markdown，不轉 PDF')
    args = parser.parse_args()

    # 決定查詢日期
    trade_date = args.date or datetime.now().strftime('%Y-%m-%d')

    # 輸出目錄
    project_root = Path(__file__).parent.parent.parent
    output_dir = project_root / 'analysis' / 'reports' / '回頭買上漲' / trade_date

    # 生成 Markdown 報告
    md_file = generate_markdown_report(trade_date, output_dir)

    if not md_file:
        return

    print(f"\n📄 Markdown 路徑：{md_file}")

    # 轉換 PDF
    if not args.no_pdf:
        pdf_file = convert_to_pdf(md_file)
        if pdf_file:
            print(f"📄 PDF 路徑：{pdf_file}")
            print(f"🌐 開啟 PDF：open {pdf_file}")
    else:
        print("跳過 PDF 轉換（使用 --no-pdf）")


if __name__ == '__main__':
    main()
