#!/usr/bin/env python3
"""
技術分析資料匯入腳本 - 將 CSV 格式的技術指標匯入資料庫

用法:
    # 匯入單一日期的技術分析資料
    python scripts/data-importer/import_technical_analysis.py --date 2026-02-03

    # 匯入日期區間
    python scripts/data-importer/import_technical_analysis.py --start 2026-01-02 --end 2026-02-03

    # 使用自訂資料目錄
    python scripts/data-importer/import_technical_analysis.py --date 2026-02-03 --data-dir data/transformed/technical
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
import argparse
import logging

# 添加專案根目錄到 Python 路徑
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
services_path = project_root / 'services'
data_importer_path = services_path / 'data-importer'

sys.path.insert(0, str(data_importer_path))
sys.path.insert(0, str(project_root))

# 導入必要的模組
from app.db import get_db_manager, DatabaseConfig
from app.importers import AnalysisImporter

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


class TechnicalAnalysisImportService:
    """技術分析資料匯入服務"""

    def __init__(self, db_config: DatabaseConfig = None, data_dir: str = "data/transformed/technical"):
        """
        Args:
            db_config: 資料庫配置
            data_dir: 技術分析資料目錄路徑
        """
        self.db_manager = get_db_manager(db_config)
        self.data_dir = Path(data_dir)

    def get_csv_file_path(self, date: datetime) -> Path:
        """
        獲取 CSV 檔案路徑

        Args:
            date: 日期

        Returns:
            檔案路徑 (data/transformed/technical/YYYY-MM-DD_all.csv)
        """
        filename = date.strftime("%Y-%m-%d_all.csv")
        return self.data_dir / filename

    def csv_to_records(self, csv_path: Path) -> List[Dict[str, Any]]:
        """
        將 CSV 檔案轉換為記錄列表

        Args:
            csv_path: CSV 檔案路徑

        Returns:
            記錄列表
        """
        logger.info(f"Reading CSV file: {csv_path}")

        # 讀取 CSV（處理 BOM）
        df = pd.read_csv(csv_path, encoding='utf-8-sig')

        logger.info(f"Loaded {len(df)} records from CSV")

        # 轉換為字典列表
        records = df.to_dict('records')

        # 確保 stock_id 為字串格式（補零到4位數）
        for record in records:
            if 'stock_id' in record:
                stock_id = record['stock_id']
                # 轉換為整數再轉為字串並補零
                record['stock_id'] = str(int(stock_id)).zfill(4)

        return records

    def import_single_date(self, import_date: datetime) -> Dict[str, Any]:
        """
        匯入單一日期的技術分析資料

        Args:
            import_date: 匯入日期

        Returns:
            匯入結果統計
        """
        date_str = import_date.strftime("%Y-%m-%d")
        logger.info(f"Starting import for date: {date_str}")

        result = {
            'date': date_str,
            'total_records': 0,
            'success': False,
            'error': None
        }

        try:
            # 獲取 CSV 檔案路徑
            csv_path = self.get_csv_file_path(import_date)

            # 檢查檔案是否存在
            if not csv_path.exists():
                error_msg = f"CSV file not found: {csv_path}"
                logger.warning(error_msg)
                result['error'] = error_msg
                return result

            # 讀取 CSV 並轉換為記錄
            records = self.csv_to_records(csv_path)

            if not records:
                logger.warning(f"No records found in {csv_path}")
                result['error'] = 'No records in CSV file'
                return result

            # 執行匯入
            logger.info(f"Importing {len(records)} records to database...")
            with self.db_manager.get_session() as session:
                importer = AnalysisImporter(session)

                # 建立匯入記錄
                importer.create_import_log(import_date.date(), str(csv_path))

                # 確保股票存在
                importer.ensure_stocks(records)

                # 轉換資料
                transformed_records = [
                    importer.transform_record(record, import_date.date())
                    for record in records
                ]

                # 批次匯入（使用 UPSERT）
                unique_keys = importer.get_unique_keys()
                count = importer.upsert_records(transformed_records, unique_keys)

                # 提交
                session.commit()

                # 更新記錄
                importer.update_import_log('completed', count)

                result['total_records'] = count
                result['success'] = True

            logger.info(f"✓ Successfully imported {count} records for {date_str}")

        except Exception as e:
            logger.error(f"✗ Import failed: {str(e)}", exc_info=True)
            result['error'] = str(e)

        return result

    def import_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        匯入日期範圍的技術分析資料

        Args:
            start_date: 開始日期
            end_date: 結束日期

        Returns:
            匯入結果列表
        """
        logger.info(f"Importing data from {start_date.date()} to {end_date.date()}")

        results = []
        current_date = start_date

        while current_date <= end_date:
            result = self.import_single_date(current_date)
            results.append(result)
            current_date += timedelta(days=1)

        # 總結
        total_records = sum(r['total_records'] for r in results)
        total_success = sum(1 for r in results if r['success'])
        total_failed = sum(1 for r in results if not r['success'])

        logger.info(f"\n{'=' * 80}")
        logger.info(f"Overall Summary")
        logger.info(f"{'=' * 80}")
        logger.info(f"Date range: {start_date.date()} to {end_date.date()}")
        logger.info(f"Total dates processed: {len(results)}")
        logger.info(f"Total records imported: {total_records}")
        logger.info(f"Successful imports: {total_success}")
        logger.info(f"Failed imports: {total_failed}")
        logger.info(f"{'=' * 80}\n")

        return results


def parse_args():
    """解析命令列參數"""
    parser = argparse.ArgumentParser(
        description="Taiwan Stock Technical Analysis Importer - Import CSV data to database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import for a specific date
  python scripts/data-importer/import_technical_analysis.py --date 2026-02-03

  # Import date range
  python scripts/data-importer/import_technical_analysis.py --start 2026-01-02 --end 2026-02-03

  # Use custom data directory
  python scripts/data-importer/import_technical_analysis.py --date 2026-02-03 --data-dir data/transformed/technical
        """
    )

    # 日期參數
    date_group = parser.add_mutually_exclusive_group(required=True)
    date_group.add_argument(
        '--date',
        type=str,
        help='Import date (YYYY-MM-DD)'
    )
    date_group.add_argument(
        '--start',
        type=str,
        help='Start date for range import (YYYY-MM-DD)'
    )

    parser.add_argument(
        '--end',
        type=str,
        help='End date for range import (YYYY-MM-DD), required when --start is used'
    )

    # 資料目錄
    parser.add_argument(
        '--data-dir',
        type=str,
        default='data/transformed/technical',
        help='Technical analysis data directory (default: data/transformed/technical)'
    )

    # 資料庫配置
    parser.add_argument(
        '--db-type',
        type=str,
        choices=['postgresql', 'sqlite', 'mysql'],
        help='Database type (default: from env DB_TYPE or postgresql)'
    )
    parser.add_argument(
        '--db-host',
        type=str,
        help='Database host (default: from env DB_HOST or localhost)'
    )
    parser.add_argument(
        '--db-port',
        type=int,
        help='Database port (default: from env DB_PORT or 5432)'
    )
    parser.add_argument(
        '--db-name',
        type=str,
        help='Database name (default: from env DB_NAME or tw_stock)'
    )
    parser.add_argument(
        '--db-user',
        type=str,
        help='Database user (default: from env DB_USER or postgres)'
    )
    parser.add_argument(
        '--db-password',
        type=str,
        help='Database password (default: from env DB_PASSWORD)'
    )
    parser.add_argument(
        '--sqlite-path',
        type=str,
        help='SQLite database file path (default: database/sqlite/tw_stock.db)'
    )

    # 日誌等級
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Log level (default: INFO)'
    )

    return parser.parse_args()


def main():
    """主程式入口"""
    args = parse_args()

    # 設定日誌等級
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    try:
        # 解析日期
        if args.date:
            import_date = datetime.strptime(args.date, "%Y-%m-%d")
            start_date = end_date = import_date
        else:
            if not args.end:
                logger.error("--end is required when using --start")
                sys.exit(1)
            start_date = datetime.strptime(args.start, "%Y-%m-%d")
            end_date = datetime.strptime(args.end, "%Y-%m-%d")

        # 建立資料庫配置
        if args.db_type or args.db_host or args.db_name:
            # 使用命令列參數
            import os
            db_config = DatabaseConfig(
                db_type=args.db_type or os.getenv('DB_TYPE', 'postgresql'),
                host=args.db_host or os.getenv('DB_HOST', 'localhost'),
                port=args.db_port or int(os.getenv('DB_PORT', '5432')),
                database=args.db_name or os.getenv('DB_NAME', 'tw_stock'),
                user=args.db_user or os.getenv('DB_USER', 'postgres'),
                password=args.db_password or os.getenv('DB_PASSWORD', ''),
                sqlite_path=args.sqlite_path
            )
        else:
            # 從環境變數載入
            db_config = None

        # 建立匯入服務
        service = TechnicalAnalysisImportService(
            db_config=db_config,
            data_dir=args.data_dir
        )

        # 執行匯入
        if args.date:
            result = service.import_single_date(import_date)
            if not result['success']:
                logger.error(f"Import failed: {result['error']}")
                sys.exit(1)
        else:
            service.import_date_range(start_date, end_date)

        logger.info("Import completed successfully!")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Import failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
