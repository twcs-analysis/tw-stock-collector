# 快速开始 - 数据导入

## 一、启动数据库

```bash
# 启动本地 PostgreSQL
cd deployment/database/postgresql
docker-compose up -d

# 验证数据库运行状态
docker ps | grep postgres
```

## 二、导入数据

### 方式 1: 使用 Python 脚本（推荐）

```bash
# 设置数据库密码
export DB_PASSWORD=tw_stock_dev_password_2024

# 导入单日数据（所有类型）
python scripts/data-importer/import_data.py --date 2026-01-02

# 只导入 price 数据
python scripts/data-importer/import_data.py --date 2026-01-02 --types price

# 导入日期区间
python scripts/data-importer/import_data.py --start 2026-01-01 --end 2026-01-31

# 导入多种类型
python scripts/data-importer/import_data.py --date 2026-01-02 --types price institutional margin
```

### 方式 2: 使用 Shell 脚本（更简单）

```bash
# 导入单日（自动使用默认密码）
scripts/data-importer/import_single_date.sh 2026-01-02

# 只导入 price
scripts/data-importer/import_single_date.sh 2026-01-02 price

# 导入日期区间
scripts/data-importer/import_date_range.sh 2026-01-01 2026-01-31
```

## 三、验证数据

```bash
# 查看导入记录数
docker exec tw-stock-postgres psql -U postgres -d tw_stock -c \
  "SELECT COUNT(*) FROM stock_prices WHERE trade_date = '2026-01-02';"

# 查看成交量前 5 名
docker exec tw-stock-postgres psql -U postgres -d tw_stock -c \
  "SELECT stock_id, close_price, volume
   FROM stock_prices
   WHERE trade_date = '2026-01-02'
   ORDER BY volume DESC LIMIT 5;"

# 查看特定股票（台积电 2330）
docker exec tw-stock-postgres psql -U postgres -d tw_stock -c \
  "SELECT * FROM stock_prices
   WHERE trade_date = '2026-01-02' AND stock_id = '2330';"
```

## 四、常见问题

### Q: 为什么有些股票的价格是 NULL？

A: 这些是原始数据中的 NaN 值，通常表示：
- 股票当天停牌（暂停交易）
- 新上市股票还没有数据
- 数据源本身缺失

这是正常现象，系统已正确将 NaN 转换为数据库 NULL。

```sql
-- 查看有多少股票价格为 NULL
SELECT COUNT(*)
FROM stock_prices
WHERE trade_date = '2026-01-02'
  AND close_price IS NULL;

-- 查看这些股票
SELECT stock_id, volume
FROM stock_prices
WHERE trade_date = '2026-01-02'
  AND close_price IS NULL
LIMIT 10;
```

### Q: 连线失败 "no password supplied"

A: 设置环境变量：
```bash
export DB_PASSWORD=tw_stock_dev_password_2024
```

或者直接在命令前加上：
```bash
DB_PASSWORD=tw_stock_dev_password_2024 python scripts/data-importer/import_data.py --date 2026-01-02
```

### Q: 如何删除已导入的数据？

A: 使用 SQL 删除：
```bash
docker exec tw-stock-postgres psql -U postgres -d tw_stock -c \
  "DELETE FROM stock_prices WHERE trade_date = '2026-01-02';"
```

## 五、数据统计

导入 2026-01-02 的结果：
- 总记录数：1954 笔
- 正常股票：约 1939 笔（有完整价格数据）
- NULL 股票：约 15 笔（停牌或无数据）

## 六、下一步

- [完整文档](README.md) - 详细使用说明
- [数据库 Schema](../../database/schemas/README.md) - 资料表结构
- [API 查询](../../services/api-service/README.md) - 通过 API 查询数据
