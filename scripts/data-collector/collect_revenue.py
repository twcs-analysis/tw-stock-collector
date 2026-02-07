#!/usr/bin/env python3
"""
月營收資料收集腳本

收集台股上市櫃公司月營收資料
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
import json

# 加入專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from services.common.collectors.revenue_collector import RevenueCollector
from services.common.utils.logger import setup_logger


def main():
    """主程式"""
    parser = argparse.ArgumentParser(
        description='收集台股月營收資料（智慧模式：自動判斷 daily/monthly）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
智慧模式（推薦）:
  # 自動判斷模式（10號前=daily，10號後=monthly，API不符自動切換）
  python scripts/data-collector/collect_revenue.py

  # 指定日期，自動判斷模式
  python scripts/data-collector/collect_revenue.py --date 2026-02-15

手動指定模式:
  # 每日收集模式（1-10 日使用，漸進式累積）
  python scripts/data-collector/collect_revenue.py --mode daily

  # 月度收集模式（10 日後使用，完整資料）
  python scripts/data-collector/collect_revenue.py --mode monthly

其他參數:
  # 指定年月
  python scripts/data-collector/collect_revenue.py --year-month 2026-01

  # 強制重新收集（即使檔案已存在）
  python scripts/data-collector/collect_revenue.py --force

  # 顯示詳細日誌
  python scripts/data-collector/collect_revenue.py --verbose

  # 測試模式（不儲存）
  python scripts/data-collector/collect_revenue.py --dry-run
        """
    )

    parser.add_argument(
        '--mode',
        type=str,
        choices=['daily', 'monthly'],
        default=None,
        help='收集模式：daily (每日漸進) 或 monthly (月度完整)。不指定則智慧判斷（10號前=daily，10號後=monthly）'
    )

    parser.add_argument(
        '--year-month',
        type=str,
        help='指定年月 (YYYY-MM)，若不指定則收集最新資料'
    )

    parser.add_argument(
        '--date',
        type=str,
        help='指定收集日期 (YYYY-MM-DD)，僅用於 daily 模式'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='顯示詳細日誌'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='僅測試不儲存'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='強制重新收集（即使本地檔案已存在）'
    )

    args = parser.parse_args()

    # 設定日誌
    log_level = 'DEBUG' if args.verbose else 'INFO'
    logger = setup_logger('collect_revenue', level=log_level)

    try:
        # 智慧判斷收集模式
        collection_mode = args.mode
        collection_date = args.date or datetime.now().strftime('%Y-%m-%d')

        # 解析日期
        try:
            date_obj = datetime.strptime(collection_date, '%Y-%m-%d')
            day_of_month = date_obj.day
        except ValueError:
            logger.error(f"無效的日期格式: {collection_date}")
            return 1

        # 智慧模式選擇邏輯
        auto_mode_selected = False
        if not args.mode:
            # 未指定模式：智慧判斷
            if day_of_month <= 10:
                # 10號之前：使用 daily 模式
                collection_mode = 'daily'
                auto_mode_selected = True
                logger.info(f"⚡ 智慧判斷: 當前為 {day_of_month} 號（≤10號），自動使用 daily 模式")
            else:
                # 10號之後：使用 monthly 模式（但會檢查 API 返回）
                collection_mode = 'monthly'
                auto_mode_selected = True
                logger.info(f"⚡ 智慧判斷: 當前為 {day_of_month} 號（>10號），自動使用 monthly 模式")
        else:
            # 已指定模式：使用指定的模式
            collection_mode = args.mode
            logger.info(f"使用指定模式: {collection_mode}")

        # 顯示執行資訊
        year_month_str = args.year_month or "最新"
        mode_str = "每日收集" if collection_mode == "daily" else "月度收集"
        logger.info(f"{'='*60}")
        logger.info(f"月營收資料收集")
        logger.info(f"模式: {mode_str} ({collection_mode})")
        logger.info(f"年月: {year_month_str}")
        if args.date:
            logger.info(f"日期: {args.date}")
        logger.info(f"{'='*60}")

        # 初始化收集器
        collector = RevenueCollector(
            year_month=args.year_month,
            mode=collection_mode,
            collection_date=collection_date
        )

        # Monthly 模式：檢查本地檔案是否已存在
        if collection_mode == 'monthly' and not args.force:
            # 預估儲存路徑（使用可能的年月）
            estimated_year_month = args.year_month
            if not estimated_year_month:
                # 計算預期年月（當月的上個月）
                year = date_obj.year
                month = date_obj.month
                if month == 1:
                    estimated_year = year - 1
                    estimated_month = 12
                else:
                    estimated_year = year
                    estimated_month = month - 1
                estimated_year_month = f"{estimated_year}-{estimated_month:02d}"

            # 檢查檔案是否存在
            estimated_path = collector.get_save_path(estimated_year_month)
            if Path(estimated_path).exists():
                logger.info(f"⚠️  本地檔案已存在: {estimated_path}")

                # 載入現有檔案
                try:
                    with open(estimated_path, 'r', encoding='utf-8') as f:
                        result = json.load(f)

                    metadata = result.get('metadata', {})
                    logger.info(f"✓ 載入現有資料:")
                    logger.info(f"  年月: {metadata.get('year_month')}")
                    logger.info(f"  總計: {metadata.get('total_count')} 檔")
                    logger.info(f"  收集日期: {metadata.get('collection_date')}")
                    logger.info(f"\n提示: 如需重新收集，請使用 --force 參數")

                    # 跳過收集，直接使用現有資料
                    skip_collection = True
                except Exception as e:
                    logger.warning(f"載入現有檔案失敗: {e}，將重新收集")
                    skip_collection = False
            else:
                skip_collection = False
        else:
            skip_collection = False

        # 收集資料（如果需要）
        if not skip_collection:
            logger.info("開始收集資料...")
            result = collector.collect()
        else:
            logger.info("使用現有資料，跳過收集")

        # 檢查 monthly 模式是否返回預期的年月
        if auto_mode_selected and collection_mode == 'monthly' and result and result.get('metadata'):
            actual_year_month = result['metadata'].get('year_month')
            expected_year_month = args.year_month

            # 如果未指定 year_month，計算預期值（當月的上個月）
            if not expected_year_month:
                year = date_obj.year
                month = date_obj.month
                if month == 1:
                    expected_year = year - 1
                    expected_month = 12
                else:
                    expected_year = year
                    expected_month = month - 1
                expected_year_month = f"{expected_year}-{expected_month:02d}"

            # 比對實際年月與預期年月
            if actual_year_month != expected_year_month:
                logger.warning(f"⚠️  monthly 模式返回 {actual_year_month}，但預期為 {expected_year_month}")
                logger.warning(f"⚡ 自動切換為 daily 模式重新收集...")

                # 重新初始化為 daily 模式
                collector = RevenueCollector(
                    year_month=expected_year_month,
                    mode='daily',
                    collection_date=collection_date
                )

                # 重新收集
                result = collector.collect()

        if not result or not result.get('data'):
            logger.error("收集失敗：無資料")
            return 1

        # 顯示結果
        metadata = result.get('metadata', {})
        logger.info(f"\n收集結果:")
        logger.info(f"  模式: {metadata.get('mode')}")
        logger.info(f"  實際年月: {metadata.get('year_month')}")
        if metadata.get('collection_date'):
            logger.info(f"  收集日期: {metadata.get('collection_date')}")
        logger.info(f"  總計: {metadata.get('total_count')} 檔")
        logger.info(f"  上市 (TWSE): {metadata.get('twse_count')} 檔")
        logger.info(f"  上櫃 (TPEx): {metadata.get('tpex_count')} 檔")

        # 顯示範例資料
        if args.verbose and result.get('data'):
            logger.debug(f"\n範例資料（前 3 筆）:")
            for i, item in enumerate(result['data'][:3], 1):
                logger.debug(f"\n  [{i}] {item.get('stock_id')} {item.get('stock_name')}")
                logger.debug(f"      當月營收: {item.get('current_month_revenue'):,} 千元")
                logger.debug(f"      月增率: {item.get('mom_change_pct'):.2f}%")
                logger.debug(f"      年增率: {item.get('yoy_change_pct'):.2f}%")

        # 儲存資料
        if not args.dry_run:
            logger.info("\n儲存資料...")

            # 使用實際年月作為檔案名稱（monthly 模式）
            actual_year_month = metadata.get('year_month')
            save_path = collector.get_save_path(actual_year_month)

            # 確保目錄存在
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)

            # 寫入檔案
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            logger.info(f"✓ 已儲存至: {save_path}")

            # 檔案大小
            file_size = Path(save_path).stat().st_size
            logger.info(f"  檔案大小: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        else:
            logger.info("\n[DRY RUN] 跳過儲存")

        logger.info(f"\n{'='*60}")
        logger.info("✓ 收集完成")
        logger.info(f"{'='*60}")

        return 0

    except KeyboardInterrupt:
        logger.warning("\n使用者中斷")
        return 130
    except Exception as e:
        logger.error(f"\n執行失敗: {e}", exc_info=args.verbose)
        return 1


if __name__ == '__main__':
    sys.exit(main())
