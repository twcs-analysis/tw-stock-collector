#!/usr/bin/env python3.11
"""
錢線百分百逐字稿 AI 分析腳本

功能：
- 讀取逐字稿檔案
- 使用 Claude API 進行深度分析
- 產生結構化的 Markdown 報告
- 支援產生每日整合摘要

使用方式：
    # 分析單一集數
    python3.11 analyze_transcript.py <transcript_file> <output_file> --part <1|2|3>

    # 產生每日整合摘要
    python3.11 analyze_transcript.py --generate-summary \
        --analysis-files <file1> <file2> <file3> \
        --output <summary_file>

範例：
    python3.11 analyze_transcript.py \
        data/transcripts/yt-moneyline/2026-02-07/moneyline_20260207_part1.txt \
        data/transcripts/yt-moneyline/2026-02-07/moneyline_20260207_part1_analysis.md \
        --part 1
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Anthropic API 設定
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

PART_NAMES = {
    "1": "上集",
    "2": "中集",
    "3": "下集"
}

def read_transcript(file_path: str) -> str:
    """讀取逐字稿檔案"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"✗ 讀取逐字稿失敗: {e}")
        sys.exit(1)

def analyze_with_claude(transcript: str, part: str = "1") -> str:
    """使用 Claude Code 分析逐字稿"""

    # 檢查是否在 Claude Code 環境中執行
    # Claude Code 會設定特定的環境變數或可透過其他方式偵測

    # 目前實作：產生待分析標記，讓 execute.sh 知道需要人工分析
    # 未來可改為直接呼叫 Claude Code 或使用其他互動方式

    print("⚠️  需要使用 Claude Code 進行深度分析")
    print("   當前模式：待 Claude Code 互動式分析")
    return generate_placeholder_analysis(transcript, part)

def generate_placeholder_analysis(transcript: str, part: str = "1") -> str:
    """產生占位分析報告（需要 Claude Code 深度分析）"""

    # 提取基本資訊
    lines = transcript.split('\n')

    # 嘗試從前幾行提取標題和日期
    title = ""
    date = ""

    for line in lines[:10]:
        if line.startswith("# 逐字稿"):
            title = line.replace("# 逐字稿 - ", "").strip()
        if line.startswith("# 轉換日期"):
            date = line.replace("# 轉換日期: ", "").strip()[:10]

    # 計算字數
    content_start = False
    content_lines = []
    for line in lines:
        if "=" * 50 in line:
            content_start = True
            continue
        if content_start:
            content_lines.append(line)

    content = '\n'.join(content_lines)
    word_count = len(content)

    part_name = PART_NAMES.get(part, f"第 {part} 集")

    # 產生占位報告
    report = f"""# 錢線百分百分析報告 - {date}（{part_name}）

## 📺 節目資訊
- 播出日期：{date}
- 集數：{part_name}
- 檔案名稱：{title}
- 逐字稿字數：{word_count:,} 字

---

## ⚠️ 分析模式說明

本報告為**占位檔案**，等待 Claude Code 進行深度分析。

### 使用 Claude Code 分析

請在 Claude Code 中執行：

```
請分析逐字稿檔案並產生深度報告：
- 檔案：{title}.txt
- 集數：{part_name}

分析內容應包含：
1. 市場總體觀察（台股、美股、國際市場）
2. 產業分析與投資建議（含個股、目標價、停損點）
3. 技術面分析與操作策略
4. 投資策略總結
5. 來賓金句整理
6. 名詞解釋
```

---

## 📄 逐字稿內容預覽

以下為逐字稿原始內容（前 2000 字）：

```
{content[:2000]}
...
```

---

**報告產生時間**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**分析模式**：占位模式（等待 Claude Code 分析）
**集數**：{part_name}
"""

    return report

def generate_simple_analysis(transcript: str, part: str = "1") -> str:
    """產生簡易分析報告（不使用 API）"""

    # 提取基本資訊
    lines = transcript.split('\n')

    # 嘗試從前幾行提取標題和日期
    title = ""
    date = ""

    for line in lines[:10]:
        if line.startswith("# 逐字稿"):
            title = line.replace("# 逐字稿 - ", "").strip()
        if line.startswith("# 轉換日期"):
            date = line.replace("# 轉換日期: ", "").strip()[:10]

    # 計算字數
    content_start = False
    content_lines = []
    for line in lines:
        if "=" * 50 in line:
            content_start = True
            continue
        if content_start:
            content_lines.append(line)

    content = '\n'.join(content_lines)
    word_count = len(content)

    part_name = PART_NAMES.get(part, f"第 {part} 集")

    # 產生報告
    report = f"""# 錢線百分百分析報告 - {date}（{part_name}）

## 📺 節目資訊
- 播出日期：{date}
- 集數：{part_name}
- 檔案名稱：{title}
- 逐字稿字數：{word_count:,} 字

---

## ⚠️ 分析模式說明

本報告使用**簡易分析模式**產生。

原因：未偵測到 `ANTHROPIC_API_KEY` 環境變數，無法呼叫 Claude API 進行深度分析。

### 如何啟用完整分析

設定環境變數後重新執行：

```bash
export ANTHROPIC_API_KEY="your-api-key"
./cron-automation/yt-moneyline/execute.sh
```

---

## 📄 逐字稿內容

以下為逐字稿原始內容（前 2000 字）：

```
{content[:2000]}
...
```

---

## 💡 建議

1. **設定 API Key**：取得 Claude API Key 以啟用完整分析功能
2. **手動分析**：閱讀完整逐字稿進行人工分析
3. **使用 Claude CLI**：使用 `/yt-moneyline` skill 進行互動式分析

---

**報告產生時間**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**分析模式**：簡易模式（無 API）
**集數**：{part_name}
"""

    return report

def generate_daily_summary(analysis_files: list) -> str:
    """產生每日整合摘要"""

    # 讀取所有分析報告
    analyses = []
    for file_path in analysis_files:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                analyses.append({
                    "file": file_path,
                    "content": f.read()
                })

    if not analyses:
        return "# 錢線百分百每日總覽\n\n⚠️ 找不到任何分析報告"

    # 提取日期（從第一份報告）
    date = ""
    for line in analyses[0]["content"].split('\n'):
        if "播出日期" in line:
            date = line.split("：")[1].strip()
            break

    # 產生整合摘要
    summary = f"""# 錢線百分百每日總覽 - {date}

## 📺 節目資訊
- 播出日期：{date}
- 集數：共 {len(analyses)} 集

---

## ⚠️ 分析模式說明

本總覽使用**簡易整合模式**產生，僅整合各集的基本資訊。

若需完整的深度分析整合，請設定 `ANTHROPIC_API_KEY` 並重新執行。

---

## 📊 各集概覽

"""

    # 列出各集資訊
    for i, analysis in enumerate(analyses, 1):
        filename = os.path.basename(analysis["file"])
        summary += f"### 第 {i} 集\n"
        summary += f"- 檔案：{filename}\n"
        summary += f"- 狀態：已完成分析\n"
        summary += f"\n"

    summary += f"""
---

## 💡 建議

1. **設定 API Key**：取得 Claude API Key 以啟用完整整合分析功能
2. **查看各集報告**：分別閱讀各集的詳細分析報告
3. **使用 Claude CLI**：使用 `/yt-moneyline` skill 進行互動式整合分析

---

**報告產生時間**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**分析模式**：簡易整合模式（無 API）
"""

    return summary

def save_analysis(content: str, output_file: str):
    """儲存分析報告"""
    try:
        # 確保目錄存在
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✓ 分析報告已儲存: {output_file}")

    except Exception as e:
        print(f"✗ 儲存報告失敗: {e}")
        sys.exit(1)

def main():
    """主程式"""

    parser = argparse.ArgumentParser(description="錢線百分百逐字稿 AI 分析")
    parser.add_argument("transcript_file", nargs="?", help="逐字稿檔案路徑")
    parser.add_argument("output_file", nargs="?", help="輸出報告路徑")
    parser.add_argument("--part", default="1", help="集數（1=上, 2=中, 3=下）")
    parser.add_argument("--generate-summary", action="store_true", help="產生每日整合摘要")
    parser.add_argument("--analysis-files", nargs="+", help="分析報告檔案列表（用於整合摘要）")
    parser.add_argument("--output", help="摘要輸出檔案（用於整合摘要）")

    args = parser.parse_args()

    # 模式一：產生每日整合摘要
    if args.generate_summary:
        if not args.analysis_files or not args.output:
            print("✗ 產生摘要需要 --analysis-files 和 --output 參數")
            sys.exit(1)

        print(f"📊 產生每日整合摘要...")
        print(f"   整合 {len(args.analysis_files)} 份報告")

        summary = generate_daily_summary(args.analysis_files)
        save_analysis(summary, args.output)

        print("✓ 完成")
        return

    # 模式二：分析單一集數
    if not args.transcript_file or not args.output_file:
        print("✗ 使用方式: python3.11 analyze_transcript.py <transcript_file> <output_file> --part <1|2|3>")
        sys.exit(1)

    # 檢查檔案是否存在
    if not os.path.exists(args.transcript_file):
        print(f"✗ 找不到逐字稿檔案: {args.transcript_file}")
        sys.exit(1)

    print(f"📄 讀取逐字稿: {args.transcript_file}")
    transcript = read_transcript(args.transcript_file)

    print(f"🤖 AI 分析中（{PART_NAMES.get(args.part, f'第 {args.part} 集')}）...")
    analysis = analyze_with_claude(transcript, args.part)

    print(f"💾 儲存報告: {args.output_file}")
    save_analysis(analysis, args.output_file)

    print("✓ 完成")

if __name__ == "__main__":
    main()
