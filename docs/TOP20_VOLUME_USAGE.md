# 成交量前 20 名資料收集器使用說明

## 📊 功能說明

成交量前 20 名資料收集器 (`Top20VolumeCollector`) 用於收集台灣證交所每日成交量排名前 20 名的股票資訊。

## 🎯 資料來源

- **API**: TWSE OpenAPI `/exchangeReport/MI_INDEX20`
- **完整 URL**: https://openapi.twse.com.tw/v1/exchangeReport/MI_INDEX20
- **更新時間**: 每日盤後
- **資料範圍**: 上市股票（不含上櫃）

## 📁 資料儲存位置

```
data/raw/top20_volume/
└── YYYY/
    └── MM/
        └── YYYY-MM-DD.json
```

**範例**: `data/raw/top20_volume/2026/01/2026-01-27.json`

## 📋 資料欄位

### Metadata

```json
{
  "metadata": {
    "date": "2026-01-27",
    "collected_at": "2026-01-27T23:35:29.444423",
    "total_count": 20,
    "source": "TWSE OpenAPI MI_INDEX20"
  }
}
```

### Data

每筆資料包含以下欄位：

| 欄位名稱 | 資料型態 | 說明 | 範例 |
|---------|---------|------|------|
| `rank` | integer | 成交量排名 (1-20) | 1 |
| `date` | string | 交易日期 | "2026-01-27" |
| `stock_id` | string | 股票代號 | "3481" |
| `stock_name` | string | 股票名稱 | "群創" |
| `volume` | float | 成交量（股） | 451933019.0 |
| `amount` | float | 成交金額（元） | 0.0 |
| `transaction_count` | float | 成交筆數 | 149032.0 |
| `open` | float | 開盤價 | 24.55 |
| `high` | float | 最高價 | 25.35 |
| `low` | float | 最低價 | 24.05 |
| `close` | float | 收盤價 | 24.55 |
| `change` | float | 漲跌價差 | 0.55 |
| `type` | string | 市場類型 | "twse" |

## 💻 使用方式

### 方法一：使用測試腳本

```bash
# 收集今日資料
python scripts/test_top20_volume.py

# 收集指定日期
python scripts/test_top20_volume.py --date 2026-01-27

# 不執行驗證
python scripts/test_top20_volume.py --date 2026-01-27 --no-validation
```

### 方法二：Python 程式碼

```python
from src.collectors import Top20VolumeCollector

# 建立收集器
collector = Top20VolumeCollector(date='2026-01-27')

# 執行收集（包含驗證）
result = collector.run(enable_validation=True)

# 檢查結果
if result['status'] == 'success':
    print(f"成功收集 {result['records']} 筆資料")
    print(f"檔案路徑: {result['file']}")
else:
    print(f"收集失敗: {result.get('error', '未知錯誤')}")
```

### 方法三：直接收集資料

```python
from src.collectors import Top20VolumeCollector

collector = Top20VolumeCollector(date='2026-01-27')
data = collector.collect()

# 查看資料
print(f"總筆數: {data['metadata']['total_count']}")
for item in data['data']:
    print(f"{item['rank']}. {item['stock_name']} ({item['stock_id']}): {item['volume']:,} 股")
```

## 📊 資料分析範例

### 範例 1: 顯示前 20 名

```python
import json

with open('data/raw/top20_volume/2026/01/2026-01-27.json', 'r') as f:
    data = json.load(f)

print("成交量前 20 名:")
for item in data['data']:
    volume_lots = int(item['volume'] / 1000)  # 轉換為張數
    print(f"{item['rank']:2}. {item['stock_name']:8} "
          f"{volume_lots:>10,} 張  "
          f"收盤價 {item['close']:>7.2f}  "
          f"漲跌 {item['change']:>6.2f}")
```

### 範例 2: 找出漲幅最大的股票

```python
import json

with open('data/raw/top20_volume/2026/01/2026-01-27.json', 'r') as f:
    data = json.load(f)

# 依漲跌幅排序
sorted_data = sorted(data['data'], key=lambda x: x['change'], reverse=True)

print("成交量前 20 名中漲幅最大:")
for item in sorted_data[:5]:
    print(f"{item['stock_name']:8} ({item['stock_id']}) "
          f"漲 {item['change']:>6.2f}  "
          f"成交量 {int(item['volume']/1000):>10,} 張")
```

### 範例 3: 計算總成交量

```python
import json

with open('data/raw/top20_volume/2026/01/2026-01-27.json', 'r') as f:
    data = json.load(f)

total_volume = sum(item['volume'] for item in data['data'])
total_lots = int(total_volume / 1000)

print(f"前 20 名總成交量: {total_lots:,} 張")
```

## 🔧 進階功能

### 與其他資料類型結合

```python
import json

# 讀取成交量前 20 名
with open('data/raw/top20_volume/2026/01/2026-01-27.json', 'r') as f:
    top20 = json.load(f)

# 讀取三大法人資料
with open('data/raw/institutional/2026/01/2026-01-27.json', 'r') as f:
    institutional = json.load(f)

# 建立股票代號對應的三大法人資料
inst_dict = {item['stock_id']: item for item in institutional['data']}

# 找出成交量前 20 名中，外資買超最多的股票
print("成交量前 20 名 + 外資買超:")
for item in top20['data']:
    stock_id = item['stock_id']
    if stock_id in inst_dict:
        foreign_net = inst_dict[stock_id]['foreign_net'] / 1000  # 轉張數
        if foreign_net > 0:
            print(f"{item['stock_name']:8} "
                  f"成交量 {int(item['volume']/1000):>8,} 張  "
                  f"外資買超 {int(foreign_net):>6,} 張")
```

## ⚠️ 注意事項

1. **資料更新時間**: API 資料在每日盤後更新，盤中查詢可能無資料
2. **僅上市股票**: 此 API 只包含上市股票，不含上櫃
3. **排名固定 20 名**: API 固定回傳前 20 名，無法調整數量
4. **成交金額欄位**: API 回傳的 `amount` 欄位可能為 0，需另行計算
5. **歷史資料**: API 回傳的是最新資料，歷史資料需從檔案讀取

## 📖 相關文件

- [TWSE API 參考文件](TWSE_API_REFERENCE.md)
- [資料目錄說明](../data/README.md)
- [專案 README](../README.md)

---

**最後更新**: 2026-01-27
**維護者**: tw-stock-collector 專案團隊
