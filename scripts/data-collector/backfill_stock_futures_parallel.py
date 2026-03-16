#!/usr/bin/env python3
"""
平行化回補個股期貨歷史資料

功能：
- 自動抓取指定日期範圍的個股期貨資料
- 使用交易日曆服務自動跳過非交易日
- 平行化處理加快收集速度
- 支援中斷續傳（跳過已存在的檔案）

使用範例：
    # 收集 2026 年全年資料
    python3.11 scripts/data-collector/backfill_stock_futures_parallel.py --year 2026

    # 收集指定日期範圍
    python3.11 scripts/data-collector/backfill_stock_futures_parallel.py \\
        --start 2026-01-01 --end 2026-12-31

    # 指定平行數量
    python3.11 scripts/data-collector/backfill_stock_futures_parallel.py \\
        --year 2026 --workers 5

    # 強制重新收集（覆蓋已存在檔案）
    python3.11 scripts/data-collector/backfill_stock_futures_parallel.py \\
        --year 2026 --force

作者：Claude Sonnet 4.5
日期：2026-03-15
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
import time

# 加入專案根目錄到 Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from services.common.collectors import StockFuturesCollector
from services.common.calendar import TradingCalendarService
from services.common.utils import setup_logger


class StockFuturesBackfiller:
    """個股期貨歷史資料回補器"""

    def __init__(self, max_workers: int = 3, force: bool = False):
        """
        初始化回補器

        Args:
            max_workers: 最大平行執行緒數（預設 3）
            force: 是否強制重新收集（覆蓋已存在檔案）
        """
        self.max_workers = max_workers
        self.force = force
        self.logger = setup_logger('StockFuturesBackfiller')
        self.calendar = TradingCalendarService()

    def get_trading_days(self, start_date: str, end_date: str) -> List[str]:
        """
        取得日期範圍內的所有交易日

        Args:
            start_date: 起始日期 (YYYY-MM-DD)
            end_date: 結束日期 (YYYY-MM-DD)

        Returns:
            交易日列表
        """
        self.logger.info(f"查詢交易日: {start_date} ~ {end_date}")

        # 產生日期範圍
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')

        dates = []
        current = start
        while current <= end:
            dates.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)

        self.logger.info(f"日期範圍: {len(dates)} 天")

        # 過濾出交易日
        trading_days = []
        for date in dates:
            if self.calendar.is_trading_day(date):
                trading_days.append(date)

        self.logger.info(f"交易日: {len(trading_days)} 天")

        return trading_days

    def check_file_exists(self, date: str) -> bool:
        """
        檢查資料檔案是否已存在

        Args:
            date: 日期 (YYYY-MM-DD)

        Returns:
            檔案是否存在
        """
        year, month, _ = date.split('-')
        file_path = project_root / f"data/raw/stock_futures/{year}/{month}/{date}.json"
        return file_path.exists()

    def collect_single_day(self, date: str) -> Dict:
        """
        收集單一日期的資料

        Args:
            date: 日期 (YYYY-MM-DD)

        Returns:
            收集結果
        """
        result = {
            'date': date,
            'status': 'unknown',
            'message': ''
        }

        try:
            # 檢查檔案是否已存在
            if not self.force and self.check_file_exists(date):
                result['status'] = 'skipped'
                result['message'] = '檔案已存在'
                self.logger.info(f"⏭️  {date}: 跳過（檔案已存在）")
                return result

            # 建立收集器
            collector = StockFuturesCollector(date=date)

            # 執行收集（不執行驗證以加快速度）
            collect_result = collector.run(enable_validation=False)

            if collect_result['status'] == 'success':
                result['status'] = 'success'
                result['records'] = collect_result['records']
                result['message'] = f"成功收集 {collect_result['records']} 筆"
                self.logger.info(f"✅ {date}: {result['message']}")

            elif collect_result['status'] == 'no_data':
                result['status'] = 'no_data'
                result['message'] = '無資料（非交易日或 API 無資料）'
                self.logger.warning(f"⚠️  {date}: {result['message']}")

            else:  # error
                result['status'] = 'error'
                result['message'] = collect_result.get('error', '未知錯誤')
                self.logger.error(f"❌ {date}: {result['message']}")

        except Exception as e:
            result['status'] = 'error'
            result['message'] = str(e)
            self.logger.error(f"❌ {date}: {e}")

        return result

    def backfill(self, start_date: str, end_date: str) -> Dict:
        """
        平行化回補資料

        Args:
            start_date: 起始日期 (YYYY-MM-DD)
            end_date: 結束日期 (YYYY-MM-DD)

        Returns:
            回補統計結果
        """
        self.logger.info("="*60)
        self.logger.info("開始平行化回補個股期貨資料")
        self.logger.info("="*60)
        self.logger.info(f"日期範圍: {start_date} ~ {end_date}")
        self.logger.info(f"平行數量: {self.max_workers} 個執行緒")
        self.logger.info(f"強制重新收集: {'是' if self.force else '否'}")
        self.logger.info("")

        # 取得交易日列表
        trading_days = self.get_trading_days(start_date, end_date)

        if not trading_days:
            self.logger.warning("沒有交易日需要處理")
            return {
                'total': 0,
                'success': 0,
                'skipped': 0,
                'no_data': 0,
                'error': 0
            }

        self.logger.info(f"準備處理 {len(trading_days)} 個交易日")
        self.logger.info("")

        # 統計資料
        stats = {
            'total': len(trading_days),
            'success': 0,
            'skipped': 0,
            'no_data': 0,
            'error': 0,
            'results': []
        }

        # 平行處理
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任務
            future_to_date = {
                executor.submit(self.collect_single_day, date): date
                for date in trading_days
            }

            # 收集結果
            completed = 0
            for future in as_completed(future_to_date):
                result = future.result()
                stats['results'].append(result)
                stats[result['status']] += 1

                completed += 1

                # 顯示進度
                progress = completed / len(trading_days) * 100
                self.logger.info(
                    f"進度: {completed}/{len(trading_days)} ({progress:.1f}%) - "
                    f"成功: {stats['success']}, "
                    f"跳過: {stats['skipped']}, "
                    f"無資料: {stats['no_data']}, "
                    f"錯誤: {stats['error']}"
                )

        elapsed_time = time.time() - start_time

        # 顯示最終統計
        self.logger.info("")
        self.logger.info("="*60)
        self.logger.info("回補完成")
        self.logger.info("="*60)
        self.logger.info(f"總交易日: {stats['total']} 天")
        self.logger.info(f"✅ 成功: {stats['success']} 天")
        self.logger.info(f"⏭️  跳過: {stats['skipped']} 天")
        self.logger.info(f"⚠️  無資料: {stats['no_data']} 天")
        self.logger.info(f"❌ 錯誤: {stats['error']} 天")
        self.logger.info(f"⏱️  耗時: {elapsed_time:.1f} 秒")
        self.logger.info(f"⚡ 平均: {elapsed_time / len(trading_days):.2f} 秒/天")

        return stats


def main():
    """主程式"""
    parser = argparse.ArgumentParser(
        description='平行化回補個股期貨歷史資料',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  # 收集 2026 年全年資料
  %(prog)s --year 2026

  # 收集指定日期範圍
  %(prog)s --start 2026-01-01 --end 2026-03-31

  # 使用 5 個平行執行緒
  %(prog)s --year 2026 --workers 5

  # 強制重新收集（覆蓋已存在檔案）
  %(prog)s --year 2026 --force
        """
    )

    # 日期參數（擇一）
    date_group = parser.add_mutually_exclusive_group(required=True)
    date_group.add_argument(
        '--year',
        type=int,
        help='收集整年資料（例如：2026）'
    )
    date_group.add_argument(
        '--start',
        type=str,
        help='起始日期 (YYYY-MM-DD)，需搭配 --end'
    )

    parser.add_argument(
        '--end',
        type=str,
        help='結束日期 (YYYY-MM-DD)，需搭配 --start'
    )

    # 其他參數
    parser.add_argument(
        '--workers',
        type=int,
        default=3,
        help='平行執行緒數量（預設 3）'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='強制重新收集（覆蓋已存在檔案）'
    )

    args = parser.parse_args()

    # 決定日期範圍
    if args.year:
        start_date = f"{args.year}-01-01"
        end_date = f"{args.year}-12-31"
    else:
        if not args.end:
            parser.error("使用 --start 時必須同時指定 --end")
        start_date = args.start
        end_date = args.end

    # 驗證日期格式
    try:
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        print("❌ 日期格式錯誤，請使用 YYYY-MM-DD 格式")
        sys.exit(1)

    # 執行回補
    try:
        backfiller = StockFuturesBackfiller(
            max_workers=args.workers,
            force=args.force
        )

        stats = backfiller.backfill(start_date, end_date)

        # 根據結果決定退出碼
        if stats['error'] > 0:
            sys.exit(1)  # 有錯誤
        else:
            sys.exit(0)  # 成功

    except KeyboardInterrupt:
        print("\n⚠️  使用者中斷")
        sys.exit(130)

    except Exception as e:
        print(f"❌ 執行失敗: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
