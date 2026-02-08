#!/usr/bin/env python3.11
"""
HTML 轉 PDF 工具

使用方式：
    python3.11 html_to_pdf.py <input.html> <output.pdf>
"""

import sys
import subprocess
from pathlib import Path

def html_to_pdf_macos(html_file: str, pdf_file: str):
    """使用 macOS 的工具將 HTML 轉為 PDF"""

    # 方法 1: 使用 textutil (純文字，格式較差)
    # subprocess.run(['textutil', '-convert', 'pdf', html_file, '-output', pdf_file])

    # 方法 2: 使用 Safari 的 headless 模式（需要 osascript）
    script = f'''
    tell application "Safari"
        set theURL to "file://{Path(html_file).absolute()}"
        open location theURL
        delay 2
        tell application "System Events"
            keystroke "p" using command down
            delay 1
            keystroke return
        end tell
    end tell
    '''

    print(f"✗ 自動轉換需要安裝額外工具")
    print(f"\n請手動轉換：")
    print(f"1. 在瀏覽器中開啟: file://{Path(html_file).absolute()}")
    print(f"2. 使用 Cmd+P 列印")
    print(f"3. 選擇「儲存為 PDF」")
    print(f"4. 儲存到: {Path(pdf_file).absolute()}")

    return False

def main():
    if len(sys.argv) != 3:
        print("使用方式: python3.11 html_to_pdf.py <input.html> <output.pdf>")
        sys.exit(1)

    html_file = sys.argv[1]
    pdf_file = sys.argv[2]

    if not Path(html_file).exists():
        print(f"✗ 找不到檔案: {html_file}")
        sys.exit(1)

    html_to_pdf_macos(html_file, pdf_file)

if __name__ == "__main__":
    main()
