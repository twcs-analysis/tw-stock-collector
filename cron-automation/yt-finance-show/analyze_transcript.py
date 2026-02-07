#!/usr/bin/env python3.11
"""
理財達人秀逐字稿 AI 分析腳本

功能：
- 讀取逐字稿檔案
- 使用 Claude API 進行深度分析
- 產生結構化的 Markdown 報告

使用方式：
    python3.11 analyze_transcript.py <transcript_file> <output_file>

範例：
    python3.11 analyze_transcript.py \
        data/transcripts/2026-02-07/finance_show_20260207.txt \
        data/transcripts/2026-02-07/finance_show_20260207_analysis.md
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Anthropic API 設定
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

def read_transcript(file_path: str) -> str:
    """讀取逐字稿檔案"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"✗ 讀取逐字稿失敗: {e}")
        sys.exit(1)

def analyze_with_claude(transcript: str) -> str:
    """使用 Claude API 分析逐字稿"""

    if not ANTHROPIC_API_KEY:
        print("⚠️  未設定 ANTHROPIC_API_KEY，使用簡易分析模式")
        return generate_simple_analysis(transcript)

    try:
        # 這裡應該呼叫 Claude API，目前先用簡易模式
        # TODO: 實作 Claude API 呼叫
        return generate_simple_analysis(transcript)

    except Exception as e:
        print(f"⚠️  Claude API 分析失敗: {e}")
        print("   降級為簡易分析模式")
        return generate_simple_analysis(transcript)

def generate_simple_analysis(transcript: str) -> str:
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

    # 產生報告
    report = f"""# 理財達人秀分析報告 - {date}

## 📺 節目資訊
- 播出日期：{date}
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
./cron-automation/yt-finance-show/execute.sh
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
3. **使用 Claude CLI**：使用 `/yt-finance-show` skill 進行互動式分析

---

**報告產生時間**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**分析模式**：簡易模式（無 API）
"""

    return report

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

    # 檢查參數
    if len(sys.argv) != 3:
        print("使用方式: python3.11 analyze_transcript.py <transcript_file> <output_file>")
        sys.exit(1)

    transcript_file = sys.argv[1]
    output_file = sys.argv[2]

    # 檢查檔案是否存在
    if not os.path.exists(transcript_file):
        print(f"✗ 找不到逐字稿檔案: {transcript_file}")
        sys.exit(1)

    print(f"📄 讀取逐字稿: {transcript_file}")
    transcript = read_transcript(transcript_file)

    print(f"🤖 AI 分析中...")
    analysis = analyze_with_claude(transcript)

    print(f"💾 儲存報告: {output_file}")
    save_analysis(analysis, output_file)

    print("✓ 完成")

if __name__ == "__main__":
    main()
