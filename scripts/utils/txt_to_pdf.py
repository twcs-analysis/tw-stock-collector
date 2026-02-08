#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
將文字檔轉換成 PDF
支援繁體中文
"""

import sys
import argparse
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER


def register_chinese_font():
    """註冊繁體中文字體"""
    # macOS 系統字體
    font_paths = [
        '/System/Library/Fonts/PingFang.ttc',  # PingFang TC
        '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',  # Arial Unicode MS
        '/Library/Fonts/Arial Unicode.ttf',
    ]

    for font_path in font_paths:
        if Path(font_path).exists():
            try:
                pdfmetrics.registerFont(TTFont('Chinese', font_path))
                print(f"✓ 已註冊字體: {font_path}")
                return True
            except Exception as e:
                print(f"✗ 字體註冊失敗 {font_path}: {e}")
                continue

    print("✗ 無法找到合適的中文字體")
    return False


def create_pdf(txt_file: Path, output_file: Path, title: str = None):
    """
    將文字檔轉換成 PDF

    Args:
        txt_file: 輸入的文字檔路徑
        output_file: 輸出的 PDF 檔案路徑
        title: PDF 標題（預設使用檔案名稱）
    """
    # 註冊中文字體
    if not register_chinese_font():
        print("警告: 使用預設字體，可能無法正確顯示中文")
        font_name = 'Helvetica'
    else:
        font_name = 'Chinese'

    # 讀取文字檔（處理編碼錯誤）
    try:
        # 首先嘗試 UTF-8
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            # 如果失敗，使用 UTF-8 並忽略錯誤字元
            print("⚠ UTF-8 解碼失敗，使用錯誤忽略模式重試...")
            with open(txt_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
    except Exception as e:
        print(f"✗ 讀取檔案失敗: {e}")
        return False

    # 建立 PDF
    try:
        doc = SimpleDocTemplate(
            str(output_file),
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm,
        )

        # 定義樣式
        styles = getSampleStyleSheet()

        # 標題樣式
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName=font_name,
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=20,
        )

        # 內文樣式
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=11,
            alignment=TA_LEFT,
            leading=16,  # 行距
        )

        # 建立內容
        story = []

        # 加入標題
        if title is None:
            title = txt_file.stem
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 0.5*cm))

        # 加入內文
        for line in lines:
            line = line.strip()
            if line:
                # 移除行號（如果有的話）
                if '→' in line:
                    line = line.split('→', 1)[1] if len(line.split('→', 1)) > 1 else line

                # 將文字轉換為 Paragraph
                para = Paragraph(line, body_style)
                story.append(para)
                story.append(Spacer(1, 0.2*cm))

        # 生成 PDF
        doc.build(story)
        print(f"✓ PDF 已生成: {output_file}")
        return True

    except Exception as e:
        print(f"✗ PDF 生成失敗: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='將文字檔轉換成 PDF（支援繁體中文）')
    parser.add_argument('input', type=str, help='輸入的文字檔路徑')
    parser.add_argument('-o', '--output', type=str, help='輸出的 PDF 檔案路徑（預設與輸入檔同名）')
    parser.add_argument('-t', '--title', type=str, help='PDF 標題（預設使用檔案名稱）')

    args = parser.parse_args()

    # 處理路徑
    txt_file = Path(args.input)
    if not txt_file.exists():
        print(f"✗ 檔案不存在: {txt_file}")
        sys.exit(1)

    if args.output:
        output_file = Path(args.output)
    else:
        output_file = txt_file.with_suffix('.pdf')

    # 轉換
    success = create_pdf(txt_file, output_file, args.title)

    if success:
        print(f"\n完成！")
        print(f"輸入: {txt_file}")
        print(f"輸出: {output_file}")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
