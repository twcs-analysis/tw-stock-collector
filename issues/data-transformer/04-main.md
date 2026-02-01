# Issues: main.py (主程式入口)

## 问题 1: 配置加载逻辑未实现 [LOW]

**文件**: `services/data-transformer/app/main.py` (Line 195-202)

**问题描述**:
配置加载的分支逻辑只是占位符，未实现从文件加载配置的功能：

```python
def main():
    args = parse_arguments()
    
    try:
        # 載入配置
        if args.config:
            # TODO: 實作從檔案載入配置  # ❌ 仍然是 TODO
            config = get_global_config()
        else:
            config = get_global_config()
```

**影响范围**:
- `--config` 参数被忽视
- 用户无法通过命令行指定自定义配置文件
- 灵活性不足

**修復方案**:
```python
def main():
    args = parse_arguments()
    
    try:
        # ✓ 加载配置
        if args.config:
            config = load_config_from_file(args.config)
            logger.info(f"已加载自定义配置: {args.config}")
        else:
            config = get_global_config()
            logger.info("使用默认配置")
        
        # 验证配置
        if not config:
            raise ValueError("配置加载失败")
        
        # ... 继续处理 ...
```

**优先级**: ⭐ 低，但应该实现

---

## 问题 2: 命令行参数的日期验证缺失 [MEDIUM]

**文件**: `services/data-transformer/app/main.py` (Line 195-232)

**问题描述**:
命令行参数接受字符串日期但没有验证格式或逻辑：

```python
parser.add_argument('--date', type=str, help='指定日期 (YYYY-MM-DD)')
parser.add_argument('--start', type=str, help='起始日期 (YYYY-MM-DD)')
parser.add_argument('--end', type=str, help='結束日期 (YYYY-MM-DD)')

# 后续处理中使用这些日期参数
# ❌ 如果用户输入 '2024-13-45'，不会被捕获
```

**影响范围**:
- 无效日期会导致程序崩溃或行为异常
- 用户体验差
- 错误消息不清楚

**修復方案**:
```python
def parse_arguments():
    """✓ 包含日期验证的参数解析"""
    parser = argparse.ArgumentParser(
        description="資料轉換服務 - 將原始資料轉換為分析資料"
    )
    
    # 自定义日期类型
    def valid_date(date_string):
        try:
            return datetime.strptime(date_string, "%Y-%m-%d")
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"無效日期格式: '{date_string}'. 應使用 YYYY-MM-DD"
            )
    
    parser.add_argument(
        '--date',
        type=valid_date,
        help='指定日期 (YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--start',
        type=valid_date,
        help='起始日期 (YYYY-MM-DD，用於批次轉換)'
    )
    
    parser.add_argument(
        '--end',
        type=valid_date,
        help='結束日期 (YYYY-MM-DD，用於批次轉換)'
    )
    
    args = parser.parse_args()
    
    # ✓ 额外验证
    if args.start and args.end and args.start > args.end:
        parser.error("起始日期不能晚於結束日期")
    
    return args
```

**优先级**: ⭐⭐⭐ 中等

---

## 问题 3: 日期范围检查不足 [MEDIUM]

**文件**: `services/data-transformer/app/main.py` (Line 215-222)

**问题描述**:
在批量转换模式中，没有检查日期范围的合理性：

```python
if args.start and args.end:
    # 批次轉換模式
    stats = transform_date_range(
        transformer=transformer,
        start_date=args.start,
        end_date=args.end,
        stock_id=args.stock_id
    )
    # ❌ 如果用户输入跨越 5 年的日期范围会怎样？
    # ❌ 没有检查是否超过内存限制或时间限制
```

**影响范围**:
- 用户可能输入过大的日期范围导致程序耗尽资源
- 没有进度指示或预估时间
- 可能导致程序崩溃或系统卡顿

**修復方案**:
```python
def transform_date_range(transformer, start_date, end_date, stock_id=None):
    """✓ 包含范围检查的批量转换"""
    
    # 计算日期数量
    if isinstance(start_date, str):
        start = datetime.strptime(start_date, '%Y-%m-%d')
    else:
        start = start_date
        
    if isinstance(end_date, str):
        end = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        end = end_date
    
    date_count = (end - start).days + 1
    
    # ✓ 检查范围合理性
    MAX_DAYS = 365  # 最多一次处理 1 年
    if date_count > MAX_DAYS:
        logger.warning(
            f"日期範圍過大: {date_count} 天 (限制: {MAX_DAYS} 天). "
            f"建議分多次處理."
        )
        # 可选：分割成多个批次
        # 或要求用户确认
    
    logger.info(
        f"開始批次轉換: {start.date()} 到 {end.date()} "
        f"({date_count} 天)"
    )
    
    # ... 继续处理 ...
```

**优先级**: ⭐⭐⭐ 中等

---

## 问题 4: 错误处理中缺少恢复机制 [MEDIUM]

**文件**: `services/data-transformer/app/main.py` (Line 237-247)

**问题描述**:
程序在出错时直接调用 `sys.exit()`，没有清理资源或保存中间结果：

```python
except KeyboardInterrupt:
    logger.warning("使用者中斷執行")
    sys.exit(130)

except Exception as e:
    logger.error(f"程式執行失敗: {e}", exc_info=True)
    sys.exit(1)  # ❌ 如果批量处理中断，之前的结果丢失
```

**影响范围**:
- 用户中断或出错时，之前的处理结果没有被保存
- 无法恢复或继续处理
- 大规模批处理时浪费资源

**修復方案**:
```python
def main():
    """✓ 包含恢复机制的主程序"""
    args = parse_arguments()
    
    try:
        # ... 初始化代码 ...
        
        if args.start and args.end:
            # 批次转换模式
            stats = transform_date_range(
                transformer=transformer,
                start_date=args.start,
                end_date=args.end,
                stock_id=args.stock_id
            )
            
            # ✓ 保存中间结果
            save_batch_stats(stats)
            
            exit_code = 0 if stats['failed_count'] == 0 else 1
        
        elif args.date:
            # 单日转换模式
            success = transform_single_date(...)
            exit_code = 0 if success else 1
        
        else:
            # 默认处理
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            success = transform_single_date(...)
            exit_code = 0 if success else 1
        
        sys.exit(exit_code)
    
    except KeyboardInterrupt:
        logger.warning("使用者中斷執行")
        # ✓ 保存当前进度
        save_checkpoint(transformer.get_stats())
        sys.exit(130)
    
    except Exception as e:
        logger.error(f"程式執行失敗: {e}", exc_info=True)
        # ✓ 保存错误日志和统计
        save_error_log(str(e), transformer.get_stats())
        sys.exit(1)

def save_checkpoint(stats: dict):
    """保存检查点，便于恢复"""
    import json
    from datetime import datetime as dt
    
    checkpoint_file = f"logs/checkpoint_{dt.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(checkpoint_file, 'w') as f:
        json.dump(stats, f, indent=2)
    logger.info(f"檢查點已保存: {checkpoint_file}")
```

**优先级**: ⭐⭐⭐ 中等

---

## 问题 5: 日志级别设置不合理 [LOW]

**文件**: `services/data-transformer/app/main.py` (Line 205-210)

**问题描述**:
在 `transform_date_range()` 中，每 100 个股票输出一条 info 日志，但这对于日期级别的批处理可能过于频繁：

```python
# technical_analysis_transformer.py 中
if idx % 100 == 0:
    self.logger.info(f"已處理 {idx}/{total_stocks} 檔股票")
```

**影响范围**:
- 日志输出过多，难以查看重要信息
- 性能影响（频繁的日志输出）

**修復方案**:
```python
# 在配置中设置日志级别或使用不同的日志级别
if idx % 100 == 0:
    self.logger.debug(f"已處理 {idx}/{total_stocks} 檔股票")  # 改用 debug

# 或按百分比输出
progress_pct = (idx / total_stocks) * 100
if progress_pct % 10 == 0:  # 每 10% 输出一次
    self.logger.info(f"進度: {progress_pct:.0f}% ({idx}/{total_stocks})")
```

**优先级**: ⭐ 低，日志优化

---

## 问题总结

| 问题 | 严重程度 | 类型 | 修复时间 |
|------|---------|------|---------|
| 配置加载未实现 | LOW | TODO | 20 分钟 |
| 参数验证缺失 | MEDIUM | 用户体验 | 25 分钟 |
| 日期范围检查 | MEDIUM | 资源管理 | 20 分钟 |
| 错误处理无恢复 | MEDIUM | 鲁棒性 | 30 分钟 |
| 日志级别不合理 | LOW | 优化 | 10 分钟 |

