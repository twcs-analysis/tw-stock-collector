#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
將 Markdown 檔案轉換成 PDF
支援繁體中文及完整 Markdown 格式
"""

import sys
import re
import argparse
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, black
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY


def register_chinese_font():
    """註冊繁體中文字體"""
    font_paths = [
        '/System/Library/Fonts/PingFang.ttc',
        '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
        '/Library/Fonts/Arial Unicode.ttf',
    ]

    for font_path in font_paths:
        if Path(font_path).exists():
            try:
                pdfmetrics.registerFont(TTFont('Chinese', font_path))
                pdfmetrics.registerFont(TTFont('Chinese-Bold', font_path))
                print(f"✓ 已註冊字體: {font_path}")
                return True
            except Exception as e:
                continue

    print("✗ 無法找到合適的中文字體")
    return False


def create_styles(font_name='Chinese'):
    """建立樣式"""
    styles = {}

    # H1 標題
    styles['h1'] = ParagraphStyle(
        'H1',
        fontName=font_name,
        fontSize=18,
        textColor=HexColor('#1a1a1a'),
        spaceAfter=16,
        spaceBefore=20,
        alignment=TA_LEFT,
        leading=24,
    )

    # H2 標題
    styles['h2'] = ParagraphStyle(
        'H2',
        fontName=font_name,
        fontSize=16,
        textColor=HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=16,
        alignment=TA_LEFT,
        leading=20,
    )

    # H3 標題
    styles['h3'] = ParagraphStyle(
        'H3',
        fontName=font_name,
        fontSize=14,
        textColor=HexColor('#34495e'),
        spaceAfter=10,
        spaceBefore=12,
        alignment=TA_LEFT,
        leading=18,
    )

    # H4 標題
    styles['h4'] = ParagraphStyle(
        'H4',
        fontName=font_name,
        fontSize=12,
        textColor=HexColor('#34495e'),
        spaceAfter=8,
        spaceBefore=10,
        alignment=TA_LEFT,
        leading=16,
    )

    # 一般段落
    styles['normal'] = ParagraphStyle(
        'Normal',
        fontName=font_name,
        fontSize=11,
        textColor=black,
        alignment=TA_JUSTIFY,
        leading=16,
        spaceAfter=6,
    )

    # 清單項目
    styles['list'] = ParagraphStyle(
        'List',
        fontName=font_name,
        fontSize=11,
        textColor=black,
        alignment=TA_LEFT,
        leading=16,
        leftIndent=20,
        spaceAfter=4,
    )

    # 程式碼區塊
    styles['code'] = ParagraphStyle(
        'Code',
        fontName='Courier',
        fontSize=9,
        textColor=HexColor('#2c3e50'),
        alignment=TA_LEFT,
        leading=12,
        leftIndent=20,
        spaceAfter=6,
        backColor=HexColor('#f8f9fa'),
    )

    # 引用區塊
    styles['quote'] = ParagraphStyle(
        'Quote',
        fontName=font_name,
        fontSize=11,
        textColor=HexColor('#555555'),
        alignment=TA_JUSTIFY,
        leading=16,
        leftIndent=20,
        spaceAfter=8,
        borderColor=HexColor('#dddddd'),
        borderWidth=2,
        borderPadding=10,
    )

    # 分隔線
    styles['hr'] = ParagraphStyle(
        'HR',
        fontName=font_name,
        fontSize=1,
        textColor=HexColor('#dddddd'),
        alignment=TA_CENTER,
        spaceAfter=12,
        spaceBefore=12,
    )

    return styles


def parse_markdown_line(line, styles):
    """解析單行 Markdown 並返回對應的 Paragraph"""
    line = line.rstrip()

    # 空行
    if not line:
        return Spacer(1, 0.3*cm)

    # H1 標題 (# )
    if line.startswith('# '):
        text = line[2:].strip()
        return Paragraph(text, styles['h1'])

    # H2 標題 (## )
    if line.startswith('## '):
        text = line[3:].strip()
        return Paragraph(text, styles['h2'])

    # H3 標題 (### )
    if line.startswith('### '):
        text = line[4:].strip()
        return Paragraph(text, styles['h3'])

    # H4 標題 (#### )
    if line.startswith('#### '):
        text = line[5:].strip()
        return Paragraph(text, styles['h4'])

    # 分隔線
    if line.strip() in ['---', '***', '___']:
        return Spacer(1, 0.5*cm)

    # 無序列表
    if line.startswith('- ') or line.startswith('* ') or line.startswith('+ '):
        text = '• ' + line[2:].strip()
        text = process_inline_markdown(text)
        return Paragraph(text, styles['list'])

    # 有序列表
    if re.match(r'^\d+\.\s', line):
        text = process_inline_markdown(line)
        return Paragraph(text, styles['list'])

    # 引用
    if line.startswith('> '):
        text = line[2:].strip()
        text = process_inline_markdown(text)
        return Paragraph(text, styles['quote'])

    # 程式碼區塊標記（忽略）
    if line.strip().startswith('```'):
        return None

    # 一般段落
    text = process_inline_markdown(line)
    return Paragraph(text, styles['normal'])


def process_inline_markdown(text):
    """處理行內 Markdown 格式"""
    # 粗體 **text** 或 __text__
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)

    # 斜體 *text* 或 _text_
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    text = re.sub(r'_(.+?)_', r'<i>\1</i>', text)

    # 行內程式碼 `code`
    text = re.sub(r'`(.+?)`', r'<font name="Courier" color="#c7254e">\1</font>', text)

    # 連結 [text](url) - 只顯示文字
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'<u>\1</u>', text)

    return text


def create_pdf_from_markdown(md_file: Path, output_file: Path, title: str = None):
    """
    將 Markdown 檔案轉換成 PDF

    Args:
        md_file: 輸入的 Markdown 檔案路徑
        output_file: 輸出的 PDF 檔案路徑
        title: PDF 標題（預設使用檔案名稱）
    """
    # 註冊中文字體
    if not register_chinese_font():
        print("警告: 使用預設字體，可能無法正確顯示中文")
        font_name = 'Helvetica'
    else:
        font_name = 'Chinese'

    # 讀取 Markdown 檔案
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        print("⚠ UTF-8 解碼失敗，使用錯誤忽略模式重試...")
        with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
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

        # 建立樣式
        styles = create_styles(font_name)

        # 建立內容
        story = []

        # 加入文件標題（如果有）
        if title:
            title_style = ParagraphStyle(
                'Title',
                fontName=font_name,
                fontSize=20,
                textColor=HexColor('#1a1a1a'),
                alignment=TA_CENTER,
                spaceAfter=20,
                leading=24,
            )
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 0.5*cm))

        # 解析 Markdown
        in_code_block = False
        code_lines = []

        for line in lines:
            # 處理程式碼區塊
            if line.strip().startswith('```'):
                if in_code_block:
                    # 結束程式碼區塊
                    if code_lines:
                        code_text = '<br/>'.join(code_lines)
                        story.append(Paragraph(code_text, styles['code']))
                        story.append(Spacer(1, 0.3*cm))
                        code_lines = []
                    in_code_block = False
                else:
                    # 開始程式碼區塊
                    in_code_block = True
                continue

            if in_code_block:
                code_lines.append(line.rstrip())
                continue

            # 解析一般行
            element = parse_markdown_line(line, styles)
            if element is not None:
                story.append(element)

        # 生成 PDF
        doc.build(story)
        print(f"✓ PDF 已生成: {output_file}")
        return True

    except Exception as e:
        print(f"✗ PDF 生成失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description='將 Markdown 檔案轉換成 PDF（支援繁體中文及格式）')
    parser.add_argument('input', type=str, help='輸入的 Markdown 檔案路徑')
    parser.add_argument('-o', '--output', type=str, help='輸出的 PDF 檔案路徑（預設與輸入檔同名）')
    parser.add_argument('-t', '--title', type=str, help='PDF 標題（預設使用檔案名稱）')

    args = parser.parse_args()

    # 處理路徑
    md_file = Path(args.input)
    if not md_file.exists():
        print(f"✗ 檔案不存在: {md_file}")
        sys.exit(1)

    if args.output:
        output_file = Path(args.output)
    else:
        output_file = md_file.with_suffix('.pdf')

    # 轉換
    success = create_pdf_from_markdown(md_file, output_file, args.title)

    if success:
        print(f"\n完成！")
        print(f"輸入: {md_file}")
        print(f"輸出: {output_file}")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
