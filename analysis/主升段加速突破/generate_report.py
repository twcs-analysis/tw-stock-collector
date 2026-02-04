#!/usr/bin/env python3
"""
主升段加速突破選股報告生成器

功能：
1. 執行選股 SQL 查詢
2. 生成 Markdown 格式報告
3. 儲存到 analysis/reports/主升段加速突破/{日期}/
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

MARKDOWN_TEMPLATE = """# 主升段加速突破選股報告

---

**分析日期**: {trade_date}
**報告生成時間**: {report_time}
**選股策略**: 主升段第一波爆發（失控式放量 + 價格加速）
**篩選結果**: {stock_count} 檔

---

## 📊 策略說明

### 核心邏輯

在中期趨勢未死的前提下，股價 **脫離整理成本區**，搭配 **失控式放量與價格加速**，捕捉主升段「最有爆發力的起漲段」。

### 策略定位

- 🔥 專抓「主升段第一波」
- 🔥 不等回檔、不求安全
- 🔥 接受較高波動，換取高單筆報酬

### 五大核心條件

| 條件 | 說明 | 目的 |
|------|------|------|
| A. 中期趨勢不死 | 收盤 > MA20 且 MA20 ≥ MA60 | 排除空頭趨勢 |
| B. 創20日新高 | 收盤 > 近20日最高價 | 脫離整理區 |
| C. 失控式放量 | 量比 ≥ 1.5 | 主升段關鍵 |
| D. 價格加速 | 當日漲幅 ≥ 4% | 排除龜速股 |
| E. 收在高檔 | 收盤位置 ≥ 75% | 追價有底氣 |

### 兩層防護機制

- ✅ 排除末升段過熱股（60日漲幅 ≤ 35%）
- ✅ 嚴格流動性門檻（今日量 ≥ 3,000 張，20日均量 ≥ 1,500 張）

---

## 🎯 推薦標的

{stock_list}

---

## 📈 技術指標詳情

{stock_details}

---

## ⚠️ 風險提示與投資建議

1. **本報告僅供參考，不構成投資建議**
2. **這是追價策略，風險較高，務必嚴格停損**
3. **停損建議**：跌破突破 K 棒低點或跌幅超過 5%
4. **停利建議**：分批停利（一半 +10%，一半 +15%）
5. **持有時間**：1-5 天（短線策略）
6. **資金配置**：單筆 ≤ 總資金 10%
7. **市場環境**：僅在強勢多頭市場使用
8. **交易紀律**：
   - 只買當天，不追隔天開高
   - 盤中接近尾盤再決定
   - 建議分批進場（降低風險）
9. **預期勝率**：40-55%（低於回頭買上漲策略）
10. **單筆報酬**：10-20%（高於回頭買上漲策略）
11. **投資有風險，請謹慎評估自身風險承受能力**

### 停損紀律（一定要執行）

擇一即可：
- ❌ 跌破突破 K 棒低點
- ❌ 或固定 -5% 停損

📌 **錯就走，不凹單**。這套的期望值來自「賺大 + 小賠多次」。

### 不適合使用情境

- ❌ 空頭市場
- ❌ 高檔震盪末升段
- ❌ 無量盤整股
- ❌ 成交量萎縮期
- ❌ 新手或無法承受高波動者

---

*本報告由台股資料收集系統 - 主升段加速突破策略自動生成*
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

    if not stocks:
        return "**本次未篩選出符合條件的股票**\n\n這是正常現象，主升段加速突破策略只在「市場給機會」時出手。"

    lines = ["| 代號 | 名稱 | 市場 | 收盤價 | 漲跌% | 量比 | 收盤位置 | 60日漲幅% |"]
    lines.append("|------|------|------|--------|-------|------|----------|-----------|")

    for stock in stocks:
        close_pos_pct = int(float(stock['收盤位置']) * 100)
        market_zh = '上市' if stock['市場別'] == 'twse' else '上櫃'
        line = f"| {stock['股票代號']} | {stock['股票名稱']} | {market_zh} | {stock['收盤價']} | {stock['日漲跌%']} | {stock['量比']} | {close_pos_pct}% | {stock['60日漲幅%']}% |"
        lines.append(line)

    return '\n'.join(lines)


def format_stock_detail(stock: dict, index: int) -> str:
    """格式化單一股票詳細資訊"""

    close_pos_pct = int(float(stock['收盤位置']) * 100)
    volume_k = int(float(stock['成交量(張)']))
    market_zh = '上市' if stock['市場別'] == 'twse' else '上櫃'

    detail = f"""### {index}. {stock['股票代號']} - {stock['股票名稱']}

**市場別**: {market_zh}
**收盤價**: {stock['收盤價']} 元
**日漲跌**: {stock['日漲跌%']}%
**成交量**: {volume_k:,} 張
**量比**: {stock['量比']} 倍
**收盤位置**: {close_pos_pct}%

#### 技術指標

| 指標 | 數值 | 說明 |
|------|------|------|
| 距MA20 | {stock['距MA20%']}% | 月線支撐 |
| 距MA60 | {stock['距MA60%']}% | 季線支撐 |
| 量比 | {stock['量比']} | 失控式放量 |
| 收盤位置 | {close_pos_pct}% | 日內強度 |
| 60日漲幅 | {stock['60日漲幅%']}% | 非過熱股 |

#### 條件檢查

- {stock['A_趨勢不死']} 中期趨勢不死（收盤 > MA20 且 MA20 ≥ MA60）
- {stock['B_創20日高']} 收盤創 20 日新高
- {stock['C_爆量≥1.5']} 失控式放量（量比 ≥ 1.5）
- {stock['D_漲幅≥4%']} 價格加速（漲幅 ≥ 4%）
- {stock['E_收高檔']} 收在日內高檔（≥ 75%）
- {stock['防護1_非過熱']} 排除末升段過熱股（60日漲幅 ≤ 35%）
- {stock['防護2_流動性']} 流動性充足（今日量 ≥ 3,000 張）

#### 進場建議

- **進場時機**: 當日尾盤（收盤前 30 分鐘確認）
- **停損點**: 跌破突破 K 棒低點或 -5%
- **停利點**: 第一批 +10%，第二批 +15%
- **建議部位**: 總資金 5-10%

---
"""

    return detail


def generate_markdown_report(trade_date: str, output_dir: Path) -> Path:
    """生成 Markdown 報告"""

    print(f"📊 開始生成 {trade_date} 的主升段加速突破選股報告...")

    # 執行 SQL 查詢
    stocks = run_sql_query(trade_date)

    stock_count = len(stocks) if stocks else 0
    print(f"✅ 找到 {stock_count} 支符合條件的股票")

    # 生成摘要表格
    stock_list = format_stock_summary(stocks)

    # 生成詳細資訊
    if stocks:
        stock_details = '\n'.join([
            format_stock_detail(stock, i+1)
            for i, stock in enumerate(stocks)
        ])
    else:
        stock_details = "**本次未篩選出符合條件的股票**\n\n這是正常現象，主升段加速突破策略採用嚴格篩選，只在市場給予明確訊號時出手。"

    # 生成完整 Markdown
    markdown = MARKDOWN_TEMPLATE.format(
        trade_date=trade_date,
        report_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        stock_count=stock_count,
        stock_list=stock_list,
        stock_details=stock_details
    )

    # 建立輸出目錄
    output_dir.mkdir(parents=True, exist_ok=True)

    # 儲存 Markdown
    md_file = output_dir / f'主升段加速突破選股報告_{trade_date}.md'
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

    parser = argparse.ArgumentParser(description='生成主升段加速突破選股報告')
    parser.add_argument('--date', type=str, help='查詢日期 (YYYY-MM-DD)，預設為今天')
    parser.add_argument('--no-pdf', action='store_true', help='只生成 Markdown，不轉 PDF')
    args = parser.parse_args()

    # 決定查詢日期
    trade_date = args.date or datetime.now().strftime('%Y-%m-%d')

    # 輸出目錄（絕對路徑）
    project_root = Path(__file__).resolve().parent.parent.parent
    output_dir = project_root / 'analysis' / 'reports' / '主升段加速突破' / trade_date

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
