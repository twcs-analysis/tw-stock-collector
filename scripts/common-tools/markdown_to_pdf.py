#!/usr/bin/env python3
"""
Markdown 轉 PDF 工具
將 Markdown 檔案轉換為 HTML 和 PDF 格式

使用方式:
    python markdown_to_pdf.py <markdown_file> [output_dir]

範例:
    python markdown_to_pdf.py report.md
    python markdown_to_pdf.py report.md ~/Documents/

需求:
    - pandoc (用於 Markdown 轉 HTML)
    - Google Chrome (用於 HTML 轉 PDF)
"""

import sys
import subprocess
from pathlib import Path


def check_dependencies():
    """檢查必要的依賴工具"""
    errors = []

    # 檢查 pandoc
    try:
        result = subprocess.run(['which', 'pandoc'], capture_output=True, text=True)
        if result.returncode != 0:
            errors.append("❌ pandoc 未安裝。請執行: brew install pandoc")
    except Exception as e:
        errors.append(f"❌ 無法檢查 pandoc: {e}")

    # 檢查 Chrome
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if not Path(chrome_path).exists():
        errors.append("❌ Google Chrome 未安裝")

    return errors


def convert_markdown_to_html(md_file: Path, html_file: Path) -> bool:
    """
    將 Markdown 轉換為 HTML

    Args:
        md_file: Markdown 檔案路徑
        html_file: 輸出 HTML 檔案路徑

    Returns:
        轉換是否成功
    """
    try:
        print(f"📄 正在轉換 Markdown 為 HTML...")

        # 使用 pandoc 轉換
        result = subprocess.run(
            [
                'pandoc',
                str(md_file),
                '-o', str(html_file),
                '--embed-resources',
                '--standalone',
                '--metadata', f'title={md_file.stem}',
                '--toc',  # 加入目錄
            ],
            capture_output=True,
            text=True,
            cwd=md_file.parent
        )

        if result.returncode != 0:
            print(f"❌ Pandoc 轉換失敗: {result.stderr}")
            return False

        print(f"✓ HTML 已生成: {html_file}")
        return True

    except Exception as e:
        print(f"❌ 轉換過程發生錯誤: {e}")
        return False


def convert_html_to_pdf(html_file: Path, pdf_file: Path) -> bool:
    """
    將 HTML 轉換為 PDF

    Args:
        html_file: HTML 檔案路徑
        pdf_file: 輸出 PDF 檔案路徑

    Returns:
        轉換是否成功
    """
    try:
        print(f"📄 正在轉換 HTML 為 PDF...")

        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

        # 使用 Chrome headless 模式轉換
        result = subprocess.run(
            [
                chrome_path,
                '--headless',
                '--disable-gpu',
                '--no-sandbox',
                f'--print-to-pdf={pdf_file}',
                f'file://{html_file.absolute()}'
            ],
            capture_output=True,
            text=True
        )

        # Chrome 的錯誤訊息可能在 stderr，但不一定是真的錯誤
        if not pdf_file.exists():
            print(f"❌ PDF 生成失敗")
            if result.stderr:
                print(f"錯誤訊息: {result.stderr}")
            return False

        # 取得檔案大小
        file_size = pdf_file.stat().st_size
        file_size_kb = file_size / 1024

        print(f"✓ PDF 已生成: {pdf_file} ({file_size_kb:.1f} KB)")
        return True

    except Exception as e:
        print(f"❌ 轉換過程發生錯誤: {e}")
        return False


def main():
    """主程式"""
    # 顯示標題
    print("=" * 80)
    print("Markdown 轉 PDF 工具")
    print("=" * 80)
    print()

    # 檢查參數
    if len(sys.argv) < 2:
        print("使用方式: python markdown_to_pdf.py <markdown_file> [output_dir]")
        print()
        print("範例:")
        print("  python markdown_to_pdf.py report.md")
        print("  python markdown_to_pdf.py report.md ~/Documents/")
        sys.exit(1)

    # 檢查依賴
    errors = check_dependencies()
    if errors:
        print("❌ 缺少必要的依賴工具:\n")
        for error in errors:
            print(f"  {error}")
        print()
        sys.exit(1)

    # 取得檔案路徑
    md_file = Path(sys.argv[1]).resolve()

    # 檢查檔案是否存在
    if not md_file.exists():
        print(f"❌ 檔案不存在: {md_file}")
        sys.exit(1)

    if not md_file.suffix.lower() in ['.md', '.markdown']:
        print(f"❌ 檔案不是 Markdown 格式: {md_file}")
        sys.exit(1)

    # 決定輸出目錄
    if len(sys.argv) >= 3:
        output_dir = Path(sys.argv[2]).resolve()
    else:
        output_dir = md_file.parent

    # 確保輸出目錄存在
    output_dir.mkdir(parents=True, exist_ok=True)

    # 設定輸出檔案路徑
    html_file = output_dir / f"{md_file.stem}.html"
    pdf_file = output_dir / f"{md_file.stem}.pdf"

    print(f"📁 輸入檔案: {md_file}")
    print(f"📁 輸出目錄: {output_dir}")
    print()

    # 轉換為 HTML
    if not convert_markdown_to_html(md_file, html_file):
        sys.exit(1)

    print()

    # 轉換為 PDF
    if not convert_html_to_pdf(html_file, pdf_file):
        sys.exit(1)

    print()
    print("=" * 80)
    print("✅ 轉換完成！")
    print("=" * 80)
    print()
    print(f"生成的檔案:")
    print(f"  • HTML: {html_file.name}")
    print(f"  • PDF:  {pdf_file.name}")
    print()
    print(f"檔案位置: {output_dir}")
    print()

    # 詢問是否開啟 PDF（僅在互動模式下）
    if sys.stdin.isatty():
        try:
            response = input("是否開啟 PDF 檔案？[Y/n] ").strip().lower()
            if response in ['', 'y', 'yes']:
                subprocess.run(['open', str(pdf_file)])
        except (KeyboardInterrupt, EOFError):
            print("\n")
            pass


if __name__ == "__main__":
    main()
