# Revenue Pipeline - 更新日誌

## [2026-02-07] 新增 monthly 資料智慧檢查機制

### 🎯 新增功能

**Step 3: 檢查 monthly 完整資料**（新增步驟）

在收集目標月份資料前，先自動檢查是否有新的 monthly 完整資料可用。

### 🔄 執行邏輯

```
1. 嘗試收集 monthly 模式資料
   └─ python3.11 scripts/data-collector/collect_revenue.py --mode monthly

2. 解析 API 返回的年月
   └─ 從日誌或 metadata 中取得實際年月

3. 比對本地檔案
   ├─ 檢查: data/raw/revenue-monthly/YYYY/YYYY-MM.json
   └─ 比對 metadata.year_month

4. 決策
   ├─ 本地無此檔案 → ✓ 保存
   ├─ 本地檔案年月不同 → ✓ 保存（發現新資料）
   └─ 本地檔案年月相同 → ⏭️ 跳過儲存（避免重複下載）
```

### 📊 使用情境

#### 情境 A：API 返回新月份資料

```
日期: 2026-02-11（10號後）
本地檔案: data/raw/revenue-monthly/2025/2025-12.json

執行流程:
[2/5] 檢查 monthly 完整資料...
  ⚡ 嘗試取得最新完整月份資料
  ✓ API 返回: 2026-01
  ✓ 本地僅有 2025-12，發現新月份！
  ✓ 儲存至: data/raw/revenue-monthly/2026/2026-01.json (1,940 檔)
```

#### 情境 B：API 返回相同月份資料

```
日期: 2026-02-07（7號）
本地檔案: data/raw/revenue-monthly/2025/2025-12.json

執行流程:
[2/5] 檢查 monthly 完整資料...
  ⚡ 嘗試取得最新完整月份資料
  ✓ API 返回: 2025-12
  ⚠️  本地已有 2025-12 資料（1,940 檔），跳過儲存
  ℹ️  繼續收集目標月份 2026-01（daily 模式）
```

### ✨ 優點

1. **自動偵測新資料**：每次執行都會檢查是否有新的完整月份
2. **避免重複下載**：相同年月不會重複保存，節省空間和時間
3. **無需手動干預**：完全自動化，無需人工判斷
4. **保持資料最新**：確保 revenue-monthly 目錄永遠有最新完整資料

### 🔧 實作方式

修改檔案：
- `.claude/skills/revenue-pipeline/instructions.md`
  - 新增 Step 3：檢查 monthly 完整資料
  - 原 Step 3-5 順延為 Step 4-6
  - 更新完整輸出範例

- `.claude/skills/revenue-pipeline/SKILL.md`
  - 更新功能說明
  - 更新執行流程圖

### 📝 技術細節

**檢查邏輯偽代碼**：

```python
# Step 1: 收集 monthly 資料
result = collect_revenue(mode="monthly")
api_year_month = result["metadata"]["year_month"]  # 例如 "2025-12"

# Step 2: 檢查本地檔案
local_file = f"data/raw/revenue-monthly/{api_year_month[:4]}/{api_year_month}.json"

if os.path.exists(local_file):
    with open(local_file) as f:
        local_data = json.load(f)
        local_year_month = local_data["metadata"]["year_month"]

    if local_year_month == api_year_month:
        print("⚠️  本地已有相同年月資料，跳過儲存")
        # 刪除暫存檔案（如果有的話）
        return "skip"
    else:
        print("✓ 發現新的年月資料，保存檔案")
        return "save"
else:
    print("✓ 本地無此年月資料，保存檔案")
    return "save"
```

### ⚠️ 注意事項

1. **不影響 daily 模式收集**：此步驟不會干擾 daily 模式的增量更新
2. **僅檢查 revenue-monthly**：不會檢查或影響 revenue-daily 目錄
3. **保留舊檔案**：跳過儲存時，本地舊檔案保持不變
4. **API 呼叫成本**：每次執行都會呼叫一次 monthly API（約 2-3 秒）

### 🎯 預期效果

- **減少重複下載**：相同月份不會每天重複下載
- **自動發現新資料**：10 號後新月份完整資料自動保存
- **保持檔案最小化**：避免同一月份多個版本的檔案

---

**更新者**: Claude Sonnet 4.5
**更新日期**: 2026-02-07
