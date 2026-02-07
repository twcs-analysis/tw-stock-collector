"""
Taiwan Stock Data Importer - Main Entry Point

將 JSON 格式的原始資料匯入到資料庫（PostgreSQL/SQLite）
"""

import argparse
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from .db import get_db_manager, DatabaseConfig
from .importers import (
    PriceImporter,
    InstitutionalImporter,
    MarginImporter,
    LendingImporter,
    Top20VolumeImporter,
    RevenueImporter,
    AnalysisImporter,
)


# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


# 匯入器對應表
IMPORTERS = {
    'price': PriceImporter,
    'institutional': InstitutionalImporter,
    'margin': MarginImporter,
    'lending': LendingImporter,
    'top20_volume': Top20VolumeImporter,
    'revenue': RevenueImporter,
    'analysis': AnalysisImporter,
}


class DataImportService:
    """資料匯入服務"""

    def __init__(self, db_config: Optional[DatabaseConfig] = None, data_root: str = "data/raw"):
        """
        Args:
            db_config: 資料庫配置
            data_root: 資料根目錄路徑
        """
        self.db_manager = get_db_manager(db_config)
        self.data_root = Path(data_root)

    def get_data_file_path(self, data_type: str, date: datetime) -> Path:
        """
        獲取資料檔案路徑

        Args:
            data_type: 資料類型
            date: 日期

        Returns:
            檔案路徑 (data/raw/{type}/YYYY/MM/YYYY-MM-DD.json 或其他格式)
        """
        year = date.strftime("%Y")
        month = date.strftime("%m")
        year_month = date.strftime("%Y-%m")
        filename = date.strftime("%Y-%m-%d.json")

        # analysis 資料在 transformed 目錄，需要特殊處理
        if data_type == 'analysis':
            # 從 data/raw 找到 data/transformed/technical_analysis
            base_path = self.data_root.parent / 'transformed' / 'technical_analysis'
            file_path = base_path / year / month / filename
        # revenue 資料按月存檔（優先使用 revenue-monthly，若不存在則使用 revenue-daily）
        elif data_type == 'revenue':
            # 先嘗試 revenue-monthly
            monthly_path = self.data_root / 'revenue-monthly' / year / f"{year_month}.json"
            if monthly_path.exists():
                file_path = monthly_path
            else:
                # 若不存在，則使用 revenue-daily
                file_path = self.data_root / 'revenue-daily' / year / f"{year_month}.json"
        else:
            file_path = self.data_root / data_type / year / month / filename

        return file_path

    def import_single_date(
        self,
        import_date: datetime,
        data_types: List[str]
    ) -> dict:
        """
        匯入單一日期的資料

        Args:
            import_date: 匯入日期
            data_types: 資料類型列表

        Returns:
            匯入結果統計
        """
        date_str = import_date.strftime("%Y-%m-%d")
        logger.info(f"Starting import for date: {date_str}")
        logger.info(f"Data types: {', '.join(data_types)}")

        results = {
            'date': date_str,
            'total_records': 0,
            'success': [],
            'failed': [],
            'skipped': []
        }

        for data_type in data_types:
            try:
                # 獲取檔案路徑
                file_path = self.get_data_file_path(data_type, import_date)

                # 檢查檔案是否存在
                if not file_path.exists():
                    logger.warning(f"File not found: {file_path}")
                    results['skipped'].append({
                        'type': data_type,
                        'reason': 'file_not_found',
                        'path': str(file_path)
                    })
                    continue

                # 獲取對應的匯入器
                importer_class = IMPORTERS.get(data_type)
                if not importer_class:
                    logger.error(f"Unknown data type: {data_type}")
                    results['failed'].append({
                        'type': data_type,
                        'error': f'Unknown data type: {data_type}'
                    })
                    continue

                # 執行匯入
                with self.db_manager.get_session() as session:
                    importer = importer_class(session)
                    count = importer.import_from_file(file_path, import_date.date())

                    results['success'].append({
                        'type': data_type,
                        'records': count,
                        'file': str(file_path)
                    })
                    results['total_records'] += count

                logger.info(f"✓ {data_type}: {count} records imported")

            except Exception as e:
                logger.error(f"✗ {data_type}: {str(e)}", exc_info=True)
                results['failed'].append({
                    'type': data_type,
                    'error': str(e)
                })

        # 輸出結果摘要
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Import Summary for {date_str}")
        logger.info(f"{'=' * 60}")
        logger.info(f"Total records imported: {results['total_records']}")
        logger.info(f"Successful: {len(results['success'])}")
        logger.info(f"Failed: {len(results['failed'])}")
        logger.info(f"Skipped: {len(results['skipped'])}")
        logger.info(f"{'=' * 60}\n")

        return results

    def import_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        data_types: List[str]
    ) -> List[dict]:
        """
        匯入日期範圍的資料

        Args:
            start_date: 開始日期
            end_date: 結束日期
            data_types: 資料類型列表

        Returns:
            匯入結果列表
        """
        logger.info(f"Importing data from {start_date.date()} to {end_date.date()}")

        results = []
        current_date = start_date

        while current_date <= end_date:
            result = self.import_single_date(current_date, data_types)
            results.append(result)
            current_date += timedelta(days=1)

        # 總結
        total_records = sum(r['total_records'] for r in results)
        total_success = sum(len(r['success']) for r in results)
        total_failed = sum(len(r['failed']) for r in results)

        logger.info(f"\n{'=' * 60}")
        logger.info(f"Overall Summary")
        logger.info(f"{'=' * 60}")
        logger.info(f"Date range: {start_date.date()} to {end_date.date()}")
        logger.info(f"Total dates processed: {len(results)}")
        logger.info(f"Total records imported: {total_records}")
        logger.info(f"Total successful imports: {total_success}")
        logger.info(f"Total failed imports: {total_failed}")
        logger.info(f"{'=' * 60}\n")

        return results


def parse_args():
    """解析命令列參數"""
    parser = argparse.ArgumentParser(
        description="Taiwan Stock Data Importer - Import JSON data to database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import all types for a specific date
  python -m app.main --date 2024-12-27

  # Import specific types
  python -m app.main --date 2024-12-27 --types price institutional

  # Import date range
  python -m app.main --start 2024-12-01 --end 2024-12-31

  # Use custom data directory
  python -m app.main --date 2024-12-27 --data-root /path/to/data/raw

  # Use SQLite instead of PostgreSQL
  python -m app.main --date 2024-12-27 --db-type sqlite --sqlite-path db/tw_stock.db
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

    # 資料類型
    parser.add_argument(
        '--types',
        nargs='+',
        choices=list(IMPORTERS.keys()),
        default=list(IMPORTERS.keys()),
        help='Data types to import (default: all types)'
    )

    # 資料目錄
    parser.add_argument(
        '--data-root',
        type=str,
        default='data/raw',
        help='Data root directory (default: data/raw)'
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
        service = DataImportService(
            db_config=db_config,
            data_root=args.data_root
        )

        # 執行匯入
        if args.date:
            service.import_single_date(import_date, args.types)
        else:
            service.import_date_range(start_date, end_date, args.types)

        logger.info("Import completed successfully!")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Import failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
