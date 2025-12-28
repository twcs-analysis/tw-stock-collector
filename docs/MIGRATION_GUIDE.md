# 官方 API 遷移指南

從 FinMind API 遷移至台灣證交所與櫃買中心官方 API 的完整指南。

---

## 📋 快速對照表

### API 使用方式對照

| 項目 | FinMind（舊） | 官方 API（新） |
|------|--------------|---------------|
| **初始化** | `PriceCollector(api_token=token)` | `PriceCollector(timeout=30)` |
| **收集單一股票** | `collect('2025-12-26', '2330')` | `collect('2025-12-26', '2330')` |
| **收集所有股票** | `collect('2025-12-26', None)` | `collect('2025-12-26', None)` |
| **需要 Token** | ✅ 是 | ❌ 否 |
| **需要股票清單** | ✅ 是 | ❌ 否 |
| **API 請求次數** | 1,946 次 | 2 次 |
| **資料延遲** | 30 天 | 即時 |

---

## 🔄 程式碼遷移範例

### 範例 1: 基本使用

#### 舊版（FinMind）
```python
from src.collectors import PriceCollector
import os

# 需要 API Token
api_token = os.getenv('FINMIND_API_TOKEN')
collector = PriceCollector(api_token=api_token)

# 收集資料（逐檔查詢，需要股票清單）
df = collector.collect('2025-12-26', stock_id='2330')
```

#### 新版（官方 API）
```python
from src.collectors import PriceCollector

# 無需 API Token
collector = PriceCollector(timeout=30)

# 收集資料（聚合查詢，無需股票清單）
df = collector.collect('2025-12-26', stock_id='2330')
```

---

### 範例 2: 收集所有股票

#### 舊版（FinMind）
```python
from src.utils import get_stock_list_manager

# 1. 先取得股票清單
stock_manager = get_stock_list_manager()
stocks = stock_manager.get_stock_list()
stock_ids = stocks['stock_id'].tolist()  # 1,946 檔

# 2. 逐一收集（1,946 次 API 請求）
for stock_id in stock_ids:
    df = collector.collect('2025-12-26', stock_id)
    # 處理資料...
```

#### 新版（官方 API）
```python
# 一次取得所有股票（2 次 API 請求）
df = collector.collect('2025-12-26', stock_id=None)

# df 已包含 1,946 檔股票資料
print(f"收集 {len(df)} 檔股票")
```

---

### 範例 3: Docker 使用

#### 舊版（FinMind）
```bash
# 需要設定環境變數
docker run --rm \
  -e FINMIND_API_TOKEN="${FINMIND_API_TOKEN}" \
  -e COLLECTION_DATE="2025-12-26" \
  -v $(pwd)/data:/app/data \
  tw-stock-collector:latest \
  python scripts/run_collection.py
```

#### 新版（官方 API）
```bash
# 無需 API Token
docker run --rm \
  -e COLLECTION_DATE="2025-12-26" \
  -v $(pwd)/data:/app/data \
  tw-stock-collector:refactored \
  python scripts/run_collection.py
```

---

## 📦 環境變數變更

### 移除的環境變數
```bash
# ❌ 不再需要
FINMIND_API_TOKEN=xxx
```

### 新增/保留的環境變數
```bash
# ✅ 使用這些
TZ=Asia/Taipei
COLLECTION_DATE=yesterday
COLLECTION_TYPES=price
```

---

## 🔧 配置檔案變更

### config.yaml

#### 移除的設定
```yaml
# ❌ 刪除此區塊
finmind:
  api_token: ${FINMIND_API_TOKEN:}
  rate_limit: 600
  retry:
    max_attempts: 3
    wait_seconds: 10
    backoff_factor: 2
```

#### 新增的設定
```yaml
# ✅ 新增此區塊
official_api:
  timeout: 30
  retry:
    max_attempts: 3
    wait_seconds: 5
```

---

## 🚀 GitHub Actions 變更

### Secrets 變更

#### 移除的 Secret
```
❌ FINMIND_API_TOKEN（不再需要）
```

#### 保留的 Secret
```
✅ PERSONAL_ACCESS_TOKEN（用於 Docker Registry）
```

### Workflow 變更

#### 舊版
```yaml
- name: Run data collection
  env:
    FINMIND_API_TOKEN: ${{ secrets.FINMIND_API_TOKEN }}  # ❌ 移除
    COLLECTION_DATE: ${{ steps.params.outputs.date }}
```

#### 新版
```yaml
- name: Run data collection
  env:
    COLLECTION_DATE: ${{ steps.params.outputs.date }}  # ✅ 無需 Token
```

---

## 📊 資料結構變更

### 輸出欄位對照

#### 共同欄位（無變更）
```python
{
    'date': '2025-12-26',
    'stock_id': '2330',
    'stock_name': '台積電',
    'open': 1500.0,
    'high': 1520.0,
    'low': 1495.0,
    'close': 1510.0,
    'volume': 20806344.0,
    'amount': 31234567890.0,
    'transaction_count': 12345
}
```

#### 新增欄位
```python
{
    'type': 'twse'  # ✅ 新增：'twse'（上市）或 'tpex'（上櫃）
}
```

#### TWSE 獨有欄位
```python
{
    'change_price': 15.0  # ✅ TWSE 提供，TPEx 為 NaN
}
```

---

## ⚠️ Breaking Changes 清單

### 1. BaseCollector

#### 移除的方法
```python
# ❌ 不再可用
collector.fetch_with_retry(func, *args, **kwargs)
```

#### 移除的屬性
```python
# ❌ 不再可用
collector.dl  # FinMind DataLoader
```

#### 移除的參數
```python
# ❌ 舊版
BaseCollector(config=config, api_token=token)

# ✅ 新版
BaseCollector(config=config)
```

---

### 2. PriceCollector

#### 移除的參數
```python
# ❌ 舊版
PriceCollector(api_token=token)

# ✅ 新版
PriceCollector(timeout=30)
```

#### 行為變更
```python
# 舊版：逐檔查詢
df = collector.collect('2025-12-26', None)  # 需要先取得股票清單

# 新版：聚合查詢
df = collector.collect('2025-12-26', None)  # 直接取得所有股票
```

---

### 3. StockListManager

```python
# ❌ 已完全移除
from src.utils import StockListManager  # ImportError

# ✅ 不再需要股票清單
# 官方 API 一次回傳所有股票
```

---

## 🧪 測試遷移

### 舊版測試
```python
# test_finmind.py
def test_collection():
    api_token = os.getenv('FINMIND_API_TOKEN')
    collector = PriceCollector(api_token=api_token)
    df = collector.collect('2025-12-26', '2330')
    assert not df.empty
```

### 新版測試
```python
# test_official_api.py
def test_collection():
    collector = PriceCollector(timeout=30)
    df = collector.collect('2025-12-26', '2330')
    assert not df.empty
    assert 'type' in df.columns  # 新增欄位
```

---

## 📝 常見問題

### Q1: 我的舊程式碼會壞掉嗎？

**A**: 如果你的程式碼只使用 `collect()` 方法，**大部分可以繼續運作**。只需：
1. 移除 `api_token` 參數
2. 移除股票清單相關邏輯

---

### Q2: 如何處理 NaN 值？

**A**: 新版會有合法的 NaN 值：
- `change_price`: TPEx 不提供（871 筆）
- OHLC: 無交易股票（少數）

```python
# 過濾掉 NaN
df_clean = df.dropna(subset=['close'])

# 或填補 NaN
df['change_price'] = df['change_price'].fillna(0)
```

---

### Q3: 可以同時支援兩種 API 嗎？

**A**: 不建議。官方 API 在所有方面都優於 FinMind：
- ✅ 更快（973 倍）
- ✅ 即時資料
- ✅ 完全免費
- ✅ 無需 Token

---

### Q4: 其他資料類型（法人、融資融券）呢？

**A**: 目前只重構了價格資料。其他資料類型：
- **選項 1**: 保持使用 FinMind（需要 Token）
- **選項 2**: 研究官方 API 是否有對應端點（推薦）

---

## 🎯 遷移檢查清單

完成遷移前，請確認：

### 程式碼
- [ ] 移除 `api_token` 參數
- [ ] 移除 StockListManager 相關程式碼
- [ ] 更新測試案例
- [ ] 處理新增的 `type` 欄位
- [ ] 處理 NaN 值（如需要）

### 環境
- [ ] 移除 `FINMIND_API_TOKEN` 環境變數
- [ ] 更新 `.env` 檔案
- [ ] 更新 `docker-compose.yml`
- [ ] 更新 GitHub Actions Secrets

### 測試
- [ ] 本地測試通過
- [ ] Docker 測試通過
- [ ] GitHub Actions 測試通過

---

## 📚 相關資源

- [重構完成報告](REFACTOR_SUMMARY.md)
- [快速開始範例](../scripts/quickstart.py)
- [官方 API 測試](../scripts/test_official_api.py)
- [Phase 1 規格書](specifications/PHASE1_DATA_COLLECTION.md)

---

## 💡 最佳實踐

### 1. 快取使用
```python
# 官方 API 很快，但仍建議快取
import pickle

# 收集一次，快取結果
df = collector.collect('2025-12-26')
with open('cache.pkl', 'wb') as f:
    pickle.dump(df, f)
```

### 2. 錯誤處理
```python
try:
    df = collector.collect('2025-12-26')
    if df.empty:
        print("可能是非交易日")
except Exception as e:
    print(f"收集失敗: {e}")
```

### 3. 資料驗證
```python
# 檢查資料完整性
assert len(df) >= 1900, "資料筆數異常"
assert 'type' in df.columns, "缺少 type 欄位"
assert set(df['type'].unique()) == {'twse', 'tpex'}, "type 欄位異常"
```

---

**遷移愉快！如有問題請參考 [REFACTOR_SUMMARY.md](REFACTOR_SUMMARY.md)** 🚀
