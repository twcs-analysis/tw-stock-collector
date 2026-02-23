# 批次 MP3 轉逐字稿 - 使用範例

## 情境 1：首次使用，轉換所有檔案

```bash
# 使用預設 base 模型
./scripts/media-tools/batch_mp3_to_transcript.sh /Users/jasonhuang/yt-video/yt-moneyline
```

**預期結果：**
- 找到 79 個 mp3 檔案
- 轉換所有檔案（約 2-3 小時）
- 每個 mp3 旁邊產生對應的 .txt 檔案

---

## 情境 2：中斷後續傳

```bash
# 第一次執行（處理到一半按 Ctrl+C 中斷）
./scripts/media-tools/batch_mp3_to_transcript.sh /Users/jasonhuang/yt-video/yt-moneyline

# 再次執行（自動跳過已完成的檔案）
./scripts/media-tools/batch_mp3_to_transcript.sh /Users/jasonhuang/yt-video/yt-moneyline
```

**預期結果：**
- 自動跳過已有逐字稿的檔案
- 只處理未完成的檔案
- 節省時間

---

## 情境 3：使用更高品質的模型

```bash
# 第一次用 base 測試（快速）
./scripts/media-tools/batch_mp3_to_transcript.sh /Users/jasonhuang/yt-video/yt-moneyline

# 確認無誤後，用 small 模型重新轉換（品質更好）
./scripts/media-tools/batch_mp3_to_transcript.sh /Users/jasonhuang/yt-video/yt-moneyline --model small --force
```

**預期結果：**
- 第一次：快速完成，驗證流程正確
- 第二次：品質提升，但時間較長（4-6 小時）

---

## 情境 4：只轉換新增的檔案

```bash
# 第一次轉換（2026-01 到 2026-01-20 的檔案）
./scripts/media-tools/batch_mp3_to_transcript.sh /Users/jasonhuang/yt-video/yt-moneyline

# ... 過幾天後新增了 2026-01-21 到 2026-01-31 的檔案 ...

# 再次執行（只會轉換新增的檔案）
./scripts/media-tools/batch_mp3_to_transcript.sh /Users/jasonhuang/yt-video/yt-moneyline
```

**預期結果：**
- 自動偵測新增的檔案
- 只轉換沒有逐字稿的檔案
- 快速完成增量更新

---

## 情境 5：重新轉換特定檔案

```bash
# 先刪除想重新轉換的逐字稿
rm /Users/jasonhuang/yt-video/yt-moneyline/2026-01-02/*.txt

# 再執行轉換（只會處理剛刪除逐字稿的檔案）
./scripts/media-tools/batch_mp3_to_transcript.sh /Users/jasonhuang/yt-video/yt-moneyline
```

**預期結果：**
- 只轉換已刪除逐字稿的檔案
- 其他檔案會被跳過

---

## 情境 6：測試單一目錄

```bash
# 建立測試目錄
mkdir -p /tmp/test-transcribe/2026-01-02
cp /Users/jasonhuang/yt-video/yt-moneyline/2026-01-02/*.mp3 /tmp/test-transcribe/2026-01-02/

# 測試轉換
./scripts/media-tools/batch_mp3_to_transcript.sh /tmp/test-transcribe
```

**預期結果：**
- 只處理測試目錄的檔案
- 不影響原始檔案
- 適合測試不同模型

---

## 情境 7：背景執行（長時間轉換）

```bash
# 使用 nohup 在背景執行
nohup ./scripts/media-tools/batch_mp3_to_transcript.sh /Users/jasonhuang/yt-video/yt-moneyline --model small > transcript.log 2>&1 &

# 查看進度
tail -f transcript.log

# 查看背景程序
ps aux | grep batch_mp3_to_transcript
```

**預期結果：**
- 程序在背景執行
- 即使關閉終端機也不會中斷
- 輸出記錄到 transcript.log

---

## 情境 8：批次處理多個來源

```bash
# 處理錢線百分百
./scripts/media-tools/batch_mp3_to_transcript.sh /Users/jasonhuang/yt-video/yt-moneyline

# 處理其他節目（如果有的話）
./scripts/media-tools/batch_mp3_to_transcript.sh /Users/jasonhuang/yt-video/another-show
```

**預期結果：**
- 依序處理不同來源
- 逐字稿保存在各自的目錄

---

## 情境 9：只查看狀態（不執行轉換）

```bash
# 使用 Python 腳本查看狀態
python3.11 -c "
from pathlib import Path

base_dir = Path('/Users/jasonhuang/yt-video/yt-moneyline')
mp3_files = []

for year_dir in sorted(base_dir.glob('2026-*')):
    if year_dir.is_dir():
        for mp3_file in sorted(year_dir.glob('*.mp3')):
            if not mp3_file.name.startswith('._'):
                mp3_files.append(mp3_file)

existing = sum(1 for mp3 in mp3_files if mp3.with_suffix('.txt').exists())
pending = len(mp3_files) - existing

print(f'總檔案數: {len(mp3_files)}')
print(f'已完成: {existing}')
print(f'待處理: {pending}')
print(f'完成度: {existing/len(mp3_files)*100:.1f}%')
"
```

**預期結果：**
- 顯示當前進度
- 不執行任何轉換
- 快速了解狀態

---

## 時間估算

根據不同模型的處理時間（79 個檔案）：

| 模型 | 單檔平均 | 總時間（79 檔） | 適用場景 |
|------|---------|---------------|---------|
| tiny | ~30 秒 | ~40 分鐘 | 快速測試 |
| **base** | ~90 秒 | **~2 小時** | **推薦** |
| small | ~3 分鐘 | ~4 小時 | 高品質 |
| medium | ~6 分鐘 | ~8 小時 | 專業用途 |
| large | ~12 分鐘 | ~16 小時 | 最高品質 |

> 💡 **建議策略**：
> 1. 首次使用 `base` 模型快速完成（2 小時）
> 2. 驗證結果無誤
> 3. 需要更高品質時，用 `small` 模型重新轉換（4 小時）

---

## 檢查點檢查清單

### 執行前

- [ ] 確認 whisper-cpp 已安裝（`brew install whisper-cpp`）
- [ ] 確認 Python 3.11 已安裝（`python3.11 --version`）
- [ ] 確認目錄路徑正確
- [ ] 確認有足夠的磁碟空間（逐字稿約佔 1-2% mp3 大小）

### 執行中

- [ ] 觀察前幾個檔案的轉換結果
- [ ] 確認逐字稿內容品質
- [ ] 注意是否有錯誤訊息

### 執行後

- [ ] 檢查統計結果（成功數、失敗數）
- [ ] 查看失敗檔案列表
- [ ] 隨機抽查逐字稿品質
- [ ] 確認所有檔案都已處理

---

## 常見問題

### Q1: 如何知道目前進度？

A: 腳本會即時顯示進度，格式如 `[10/79] 處理中`。

### Q2: 可以暫停後繼續嗎？

A: 可以，按 `Ctrl+C` 中斷，下次執行會自動跳過已完成的檔案。

### Q3: 如何確認逐字稿品質？

A: 隨機打開幾個 .txt 檔案檢查內容，如果品質不佳，可以用更大的模型重新轉換。

### Q4: 轉換失敗怎麼辦？

A: 檢查失敗檔案列表，確認原因（如：檔案損壞、格式不支援），修正後重新執行即可。

### Q5: 如何批次重新轉換所有檔案？

A: 使用 `--force` 參數：
```bash
./scripts/media-tools/batch_mp3_to_transcript.sh /Users/jasonhuang/yt-video/yt-moneyline --force
```

---

## 效能優化建議

1. **使用 SSD 磁碟**：I/O 效能影響轉換速度
2. **關閉不必要的應用程式**：釋放 CPU 資源
3. **選擇適當的模型**：根據需求平衡速度與品質
4. **分批處理**：如果檔案太多，可以分批執行
5. **背景執行**：使用 `nohup` 或 `screen` 在背景執行

---

## 進階技巧

### 自訂年份範圍

腳本目前只處理 `2026-*` 目錄，如需處理其他年份：

```bash
# 修改腳本中的搜尋模式（第 72 行）
# 將 "2026-*" 改為 "202[56]-*" 可同時處理 2025 和 2026
```

### 並行處理（不建議）

whisper-cpp 已經充分使用 CPU，並行處理可能導致效能下降。

### 整合到自動化流程

```bash
# 建立每日自動轉換腳本
cat > ~/daily-transcribe.sh << 'EOF'
#!/bin/bash
cd /Users/jasonhuang/github/personal/tw-stock-collector
./scripts/media-tools/batch_mp3_to_transcript.sh /Users/jasonhuang/yt-video/yt-moneyline
EOF

chmod +x ~/daily-transcribe.sh

# 加入 crontab（每天凌晨 2 點執行）
# 0 2 * * * ~/daily-transcribe.sh >> ~/transcribe.log 2>&1
```
