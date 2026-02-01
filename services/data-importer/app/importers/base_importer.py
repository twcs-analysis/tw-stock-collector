"""
Base Importer - 所有資料匯入器的基礎類別
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Any, Optional

from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import insert

from ..db.models import Stock, DataImportLog


logger = logging.getLogger(__name__)


class BaseImporter(ABC):
    """資料匯入器基礎類別"""

    def __init__(self, session: Session, data_type: str):
        """
        Args:
            session: SQLAlchemy Session
            data_type: 資料類型 (price, institutional, margin, lending, top20_volume)
        """
        self.session = session
        self.data_type = data_type
        self.import_log_id: Optional[int] = None

    @abstractmethod
    def get_model_class(self):
        """返回對應的 ORM Model 類別"""
        pass

    @abstractmethod
    def transform_record(self, record: Dict[str, Any], import_date: date) -> Dict[str, Any]:
        """
        將 JSON 記錄轉換為資料庫欄位

        Args:
            record: JSON 資料記錄
            import_date: 匯入日期

        Returns:
            轉換後的資料字典
        """
        pass

    def load_json_file(self, file_path: Path) -> Dict[str, Any]:
        """
        載入 JSON 檔案

        Args:
            file_path: JSON 檔案路徑

        Returns:
            JSON 資料

        Raises:
            FileNotFoundError: 檔案不存在
            json.JSONDecodeError: JSON 格式錯誤
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data

    def ensure_stocks(self, records: List[Dict[str, Any]]):
        """
        確保所有股票都已在 stocks 表中

        Args:
            records: 資料記錄列表
        """
        # 提取所有股票代碼
        stock_ids = set()
        for record in records:
            if 'stock_id' in record:
                stock_ids.add(record['stock_id'])

        if not stock_ids:
            return

        # 查詢已存在的股票
        existing_stocks = self.session.query(Stock.stock_id).filter(
            Stock.stock_id.in_(stock_ids)
        ).all()
        existing_ids = {s.stock_id for s in existing_stocks}

        # 新增不存在的股票
        new_stocks = []
        for record in records:
            stock_id = record.get('stock_id')
            if stock_id and stock_id not in existing_ids:
                stock_data = {
                    'stock_id': stock_id,
                    'stock_name': record.get('stock_name', ''),
                    'market_type': record.get('type', record.get('market_type', 'twse')),
                    'is_active': 1
                }
                new_stocks.append(stock_data)
                existing_ids.add(stock_id)  # 避免重複

        if new_stocks:
            self.session.bulk_insert_mappings(Stock, new_stocks)
            self.session.flush()
            logger.info(f"Inserted {len(new_stocks)} new stocks")

    def upsert_records(self, records: List[Dict[str, Any]], unique_keys: List[str]):
        """
        使用 UPSERT 批次匯入資料 (PostgreSQL) 或 INSERT OR REPLACE (SQLite)

        Args:
            records: 要匯入的資料列表
            unique_keys: 唯一鍵欄位列表

        Returns:
            匯入的記錄數
        """
        if not records:
            return 0

        model_class = self.get_model_class()
        db_type = self.session.bind.dialect.name

        if db_type == "postgresql":
            # PostgreSQL: 使用 INSERT ... ON CONFLICT DO UPDATE
            stmt = pg_insert(model_class).values(records)

            # 建立更新字典 (排除主鍵欄位)
            update_dict = {
                c.name: c
                for c in stmt.excluded
                if c.name not in unique_keys
            }

            stmt = stmt.on_conflict_do_update(
                index_elements=unique_keys,
                set_=update_dict
            )

            self.session.execute(stmt)

        elif db_type == "sqlite":
            # SQLite: 使用 INSERT OR REPLACE
            # 注意: REPLACE 會刪除舊記錄再插入新記錄，可能影響關聯
            for record in records:
                stmt = insert(model_class).values(record)
                stmt = stmt.prefix_with('OR REPLACE')
                self.session.execute(stmt)

        else:
            # 其他資料庫: 逐筆檢查並更新或插入
            for record in records:
                # 查詢是否已存在
                filter_conditions = {k: record[k] for k in unique_keys}
                existing = self.session.query(model_class).filter_by(**filter_conditions).first()

                if existing:
                    # 更新
                    for key, value in record.items():
                        if key not in unique_keys:
                            setattr(existing, key, value)
                else:
                    # 插入
                    self.session.add(model_class(**record))

        self.session.flush()
        return len(records)

    def create_import_log(self, import_date: date, source_file: str) -> int:
        """
        建立匯入記錄

        Args:
            import_date: 匯入日期
            source_file: 來源檔案路徑

        Returns:
            Log ID
        """
        log = DataImportLog(
            import_date=import_date,
            data_type=self.data_type,
            status='running',
            start_time=datetime.now()
        )
        self.session.add(log)
        self.session.flush()
        self.import_log_id = log.id
        return log.id

    def update_import_log(self, status: str, record_count: int = 0, error_message: str = None):
        """
        更新匯入記錄

        Args:
            status: 狀態 (completed/failed)
            record_count: 匯入筆數
            error_message: 錯誤訊息
        """
        if self.import_log_id:
            log = self.session.query(DataImportLog).get(self.import_log_id)
            if log:
                log.status = status
                log.records_count = record_count
                log.error_message = error_message
                log.end_time = datetime.now()
                self.session.flush()

    def import_from_file(self, file_path: Path, import_date: date) -> int:
        """
        從 JSON 檔案匯入資料

        Args:
            file_path: JSON 檔案路徑
            import_date: 匯入日期

        Returns:
            匯入的記錄數

        Raises:
            Exception: 匯入失敗
        """
        try:
            # 建立匯入記錄
            self.create_import_log(import_date, str(file_path))

            # 載入 JSON
            logger.info(f"Loading JSON file: {file_path}")
            data = self.load_json_file(file_path)

            # 取得資料記錄 (支援兩種格式: {metadata, data} 或直接 array)
            if isinstance(data, list):
                records = data
            else:
                records = data.get('data', [])

            if not records:
                logger.warning(f"No data records found in {file_path}")
                self.update_import_log('completed', 0)
                return 0

            logger.info(f"Found {len(records)} records")

            # 確保股票存在
            self.ensure_stocks(records)

            # 轉換資料
            transformed_records = [
                self.transform_record(record, import_date)
                for record in records
            ]

            # 批次匯入
            unique_keys = self.get_unique_keys()
            count = self.upsert_records(transformed_records, unique_keys)

            # 提交
            self.session.commit()

            # 更新記錄
            self.update_import_log('completed', count)

            logger.info(f"Successfully imported {count} records from {file_path}")
            return count

        except Exception as e:
            self.session.rollback()
            error_msg = str(e)
            logger.error(f"Failed to import {file_path}: {error_msg}")
            self.update_import_log('failed', 0, error_msg)
            raise

    @abstractmethod
    def get_unique_keys(self) -> List[str]:
        """返回唯一鍵欄位列表"""
        pass
