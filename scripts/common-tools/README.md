# 通用工具 (Common Tools)

本目錄包含專案中使用的通用工具腳本。

---

## 📄 markdown_to_pdf.py

將 Markdown 檔案轉換為 HTML 和 PDF 格式的工具。

### 功能特色

- ✅ 支援繁體中文
- ✅ 自動生成 HTML 和 PDF
- ✅ 支援表格、程式碼區塊等 Markdown 語法
- ✅ 自動加入目錄 (TOC)
- ✅ 美化的 HTML 樣式

### 系統需求

1. **pandoc** - Markdown 轉 HTML
   ```bash
   brew install pandoc
   ```

2. **Google Chrome** - HTML 轉 PDF
   ```bash
   # macOS 通常已安裝
   # 或從 https://www.google.com/chrome/ 下載
   ```

### 使用方式

#### 基本用法

```bash
# 在相同目錄下生成 HTML 和 PDF
python scripts/common-tools/markdown_to_pdf.py report.md
```

#### 指定輸出目錄

```bash
# 將輸出檔案放到指定目錄
python scripts/common-tools/markdown_to_pdf.py report.md ~/Documents/
```

### 範例

```bash
# 轉換股票推薦報告
python scripts/common-tools/markdown_to_pdf.py \
    ~/Downloads/股票推薦/股票推薦報告_2026-02-02.md

# 輸出到指定目錄
python scripts/common-tools/markdown_to_pdf.py \
    ~/Downloads/股票推薦/股票推薦報告_2026-02-02.md \
    ~/Desktop/Reports/
```

### 輸出結果

執行後會在輸出目錄生成兩個檔案：

1. **{filename}.html** - HTML 格式，可用瀏覽器開啟
2. **{filename}.pdf** - PDF 格式，適合列印和分享

### 技術細節

- 使用 **pandoc** 進行 Markdown → HTML 轉換
- 使用 **Chrome Headless** 進行 HTML → PDF 轉換
- 支援完整的 Markdown 語法（包含表格、程式碼等）
- 自動嵌入資源，生成獨立的 HTML 檔案

### 疑難排解

#### 錯誤: pandoc 未安裝

```bash
brew install pandoc
```

#### 錯誤: Google Chrome 未安裝

從 [https://www.google.com/chrome/](https://www.google.com/chrome/) 下載並安裝。

#### PDF 生成失敗

確認 HTML 檔案已正確生成，然後手動用瀏覽器開啟 HTML 並列印為 PDF。

---

## 未來擴充

未來可能加入的通用工具：

- CSV 處理工具
- 資料驗證工具
- 報表生成工具
- 資料匯出工具

---

**最後更新**: 2026-02-03
**維護者**: Jason Huang
