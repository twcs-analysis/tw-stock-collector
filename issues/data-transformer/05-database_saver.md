# Issues: database_saver.py (資料庫儲存模組)

## 问题 1: 缺少数据库连接复用 [MEDIUM]

**文件**: `services/data-transformer/app/database_saver.py` (Line 59-75)

**问题描述**:
在 `save_to_database()` 中，每次调用都创建新的数据库连接，处理完后立即关闭：

```python
def save_to_database(self, df, table_name='stock_analysis_daily', if_exists='append'):
    try:
        from sqlalchemy import create_engine
        
        # ❌ 每次都创建新连接
        engine = create_engine(self.database_url)
        
        df_to_save.to_sql(...)
        
        engine.dispose()  # ❌ 立即关闭
        return True
```

**影响范围**:
- 性能低下：每次保存都需要建立 TCP 连接
- 如果批量保存 1000 次数据，会创建 1000 个连接
- 数据库连接池资源浪费

**修復方案**:
```python
class DatabaseSaver:
    """資料庫儲存器"""
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or self._get_default_db_url()
        self.logger = get_logger(__name__)
        self._engine = None  # ✓ 缓存引擎
    
    def _get_engine(self):
        """✓ 获取或创建引擎（连接池）"""
        if self._engine is None:
            from sqlalchemy import create_engine
            self._engine = create_engine(
                self.database_url,
                pool_size=10,           # 连接池大小
                max_overflow=20,        # 超出池大小时的额外连接
                pool_recycle=3600,      # 1小时回收连接
                echo=False              # 不输出 SQL（性能）
            )
        return self._engine
    
    def save_to_database(self, df, table_name='stock_analysis_daily', if_exists='append'):
        """✓ 使用连接池"""
        try:
            engine = self._get_engine()  # ✓ 复用连接
            
            df_to_save = self._prepare_dataframe(df)
            
            df_to_save.to_sql(
                name=table_name,
                con=engine,
                if_exists=if_exists,
                index=False,
                method='multi',
                chunksize=1000
            )
            
            self.logger.info(f"成功儲存 {len(df_to_save)} 筆資料到 {table_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"儲存到資料庫失敗: {e}", exc_info=True)
            return False
    
    def close(self):
        """✓ 显式关闭连接"""
        if self._engine:
            self._engine.dispose()
            self._engine = None
    
    def __del__(self):
        """✓ 对象销毁时关闭连接"""
        self.close()
```

**优先级**: ⭐⭐⭐ 中等，但影响性能

---

## 问题 2: 批量插入配置不optimal [MEDIUM]

**文件**: `services/data-transformer/app/database_saver.py` (Line 67-72)

**问题描述**:
批量插入配置使用 `method='multi'` 和 `chunksize=1000`，但没有根据实际情况优化：

```python
df_to_save.to_sql(
    name=table_name,
    con=engine,
    if_exists=if_exists,
    index=False,
    method='multi',   # ✓ 这是对的
    chunksize=1000    # ❌ 固定值，没有考虑数据量大小
)
```

**问题**:
- `chunksize=1000` 对小数据量和大数据量都不是最优的
- 对于超大数据量（百万级），可能导致 OOM
- 没有处理插入冲突或更新场景

**修復方案**:
```python
def save_to_database(self, df, table_name='stock_analysis_daily', 
                    if_exists='append', on_duplicate='skip'):
    """✓ 可配置的批量插入"""
    try:
        engine = self._get_engine()
        df_to_save = self._prepare_dataframe(df)
        
        # ✓ 根据数据量调整 chunksize
        row_count = len(df_to_save)
        if row_count > 100000:
            chunksize = 5000  # 大数据量用更大的 chunk
        elif row_count > 10000:
            chunksize = 2000
        else:
            chunksize = 1000  # 小数据量用小 chunk
        
        self.logger.info(
            f"開始儲存 {row_count} 筆資料 (chunksize={chunksize})"
        )
        
        # ✓ 处理重复键冲突
        try:
            df_to_save.to_sql(
                name=table_name,
                con=engine,
                if_exists=if_exists,
                index=False,
                method='multi',
                chunksize=chunksize
            )
        except Exception as e:
            if 'duplicate' in str(e).lower() and on_duplicate == 'update':
                # ✓ 尝试 upsert
                self._upsert_data(df_to_save, table_name, engine)
            else:
                raise
        
        self.logger.info(f"成功儲存 {row_count} 筆資料到 {table_name}")
        return True
        
    except Exception as e:
        self.logger.error(f"儲存到資料庫失敗: {e}", exc_info=True)
        return False

def _upsert_data(self, df, table_name, engine):
    """✓ Upsert 数据（insert or update）"""
    # 具体实现取决于数据库
    # PostgreSQL: ON CONFLICT DO UPDATE
    # MySQL: ON DUPLICATE KEY UPDATE
    # SQLite: INSERT OR REPLACE
    pass
```

**优先级**: ⭐⭐⭐ 中等

---

## 问题 3: 缺少数据验证 [MEDIUM]

**文件**: `services/data-transformer/app/database_saver.py` (Line 78-100)

**问题描述**:
`_prepare_dataframe()` 只是重命名列，没有进行数据验证或类型转换：

```python
def _prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
    """
    準備 DataFrame 以符合資料庫 schema
    
    Args:
        df: 原始 DataFrame
    """
    # ❌ 当前代码不完整，无法查看完整逻辑
    # 但从文件名和方法名推测，应该进行数据清理
```

**影响范围**:
- 无法捕获数据类型不匹配的问题
- 插入数据库时可能失败
- 数据库中可能存储不正确的数据类型

**修復方案**:
```python
def _prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
    """✓ 完整的数据准备和验证"""
    
    # 复制以避免修改原始数据
    df = df.copy()
    
    # ✓ 列名映射（如果需要）
    column_mapping = {
        'trade_date': 'trade_date',
        'stock_id': 'stock_id',
        'open': 'open_price',
        'high': 'high_price',
        'low': 'low_price',
        'close': 'close_price',
        # ... 其他映射
    }
    df = df.rename(columns=column_mapping)
    
    # ✓ 数据类型转换
    type_mapping = {
        'trade_date': 'datetime64[ns]',
        'stock_id': 'object',  # 字符串
        'open_price': 'float64',
        'high_price': 'float64',
        'low_price': 'float64',
        'close_price': 'float64',
        'volume': 'int64',
        'ma_5': 'float64',
        'ma_10': 'float64',
        # ... 其他字段
    }
    
    for col, dtype in type_mapping.items():
        if col in df.columns:
            try:
                if dtype == 'datetime64[ns]':
                    df[col] = pd.to_datetime(df[col])
                else:
                    df[col] = df[col].astype(dtype)
            except Exception as e:
                self.logger.warning(f"無法轉換列 {col} 為 {dtype}: {e}")
    
    # ✓ 验证必要列
    required_columns = ['trade_date', 'stock_id', 'close_price']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"缺少必要列: {missing_columns}")
    
    # ✓ 检查 NULL 值
    null_counts = df.isnull().sum()
    if null_counts.any():
        self.logger.warning(f"發現 NULL 值:\n{null_counts[null_counts > 0]}")
        # 可选：填充或删除
    
    # ✓ 检查重复值
    duplicates = df[['trade_date', 'stock_id']].duplicated().sum()
    if duplicates > 0:
        self.logger.warning(f"發現 {duplicates} 個重複記錄")
        # 可选：删除重复值
        df = df.drop_duplicates(subset=['trade_date', 'stock_id'], keep='last')
    
    return df
```

**优先级**: ⭐⭐⭐ 中等

---

## 问题 4: 缺少事务管理 [MEDIUM]

**文件**: `services/data-transformer/app/database_saver.py` (Line 59-75)

**问题描述**:
没有使用数据库事务，如果中途出错，可能导致部分数据被保存：

```python
def save_to_database(self, df, table_name='stock_analysis_daily', if_exists='append'):
    try:
        engine = create_engine(self.database_url)
        
        # ❌ 没有事务管理
        df_to_save.to_sql(...)
        
        engine.dispose()
        return True
    except Exception as e:
        # ❌ 失败时无法回滚
        return False
```

**影响范围**:
- 数据一致性问题
- 如果批量插入到一半失败，前面的数据已被保存

**修復方案**:
```python
def save_to_database(self, df, table_name='stock_analysis_daily', if_exists='append'):
    """✓ 使用事务管理"""
    engine = self._get_engine()
    
    try:
        with engine.begin() as connection:  # ✓ 自动事务管理
            df_to_save = self._prepare_dataframe(df)
            
            # 在事务中执行
            df_to_save.to_sql(
                name=table_name,
                con=connection,
                if_exists=if_exists,
                index=False,
                method='multi',
                chunksize=1000
            )
            
            # ✓ 成功时自动提交
            self.logger.info(f"成功儲存 {len(df_to_save)} 筆資料到 {table_name}")
            return True
            
    except Exception as e:
        # ✓ 失败时自动回滚
        self.logger.error(f"儲存失敗，已回滾: {e}")
        return False
```

**优先级**: ⭐⭐⭐ 中等

---

## 问题 5: 缺少错误恢复机制 [LOW]

**文件**: `services/data-transformer/app/database_saver.py` (Line 59-100)

**问题描述**:
当保存失败时，没有重试机制或错误日志保存：

```python
except Exception as e:
    self.logger.error(f"儲存到資料庫失敗: {e}", exc_info=True)
    return False  # ❌ 直接返回 False，数据丢失
```

**修復方案**:
```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
    """✓ 重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"第 {attempt + 1} 次嘗試失敗，"
                            f"{delay} 秒後重試: {e}"
                        )
                        time.sleep(delay * (2 ** attempt))  # 指数退避
                    else:
                        logger.error(f"所有 {max_retries} 次嘗試都失敗: {e}")
            raise last_exception
        return wrapper
    return decorator

class DatabaseSaver:
    @retry_on_failure(max_retries=3, delay=1)
    def save_to_database(self, df, table_name='stock_analysis_daily', if_exists='append'):
        """✓ 自动重试"""
        engine = self._get_engine()
        
        with engine.begin() as connection:
            df_to_save = self._prepare_dataframe(df)
            
            df_to_save.to_sql(
                name=table_name,
                con=connection,
                if_exists=if_exists,
                index=False,
                method='multi',
                chunksize=1000
            )
            
            self.logger.info(f"成功儲存 {len(df_to_save)} 筆資料到 {table_name}")
            return True
```

**优先级**: ⭐⭐ 低到中等

---

## 问题总结

| 问题 | 严重程度 | 类型 | 修复时间 |
|------|---------|------|---------|
| 缺少连接复用 | MEDIUM | 性能 | 25 分钟 |
| 批量插入不优化 | MEDIUM | 性能/稳定性 | 20 分钟 |
| 缺少数据验证 | MEDIUM | 数据质量 | 30 分钟 |
| 缺少事务管理 | MEDIUM | 数据一致性 | 15 分钟 |
| 缺少重试机制 | LOW | 鲁棒性 | 20 分钟 |

