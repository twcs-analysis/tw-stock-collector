#!/usr/bin/env python3
"""
資料庫初始化腳本

功能：
- 建立所有資料表
- 建立索引
- 建立約束條件

使用方式：
    python services/common/database/init_db.py
"""

import sys
from pathlib import Path

# 加入專案路徑
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / 'services'))

from common.database import Base, DatabaseManager, get_db_manager
from common.utils import get_logger

logger = get_logger(__name__)


def init_database():
    """初始化資料庫"""

    logger.info("="*70)
    logger.info("開始初始化資料庫")
    logger.info("="*70)

    try:
        # 取得資料庫管理器
        db_manager = get_db_manager()

        # 建立所有表格
        logger.info("建立資料表...")
        Base.metadata.create_all(db_manager.engine)

        # 驗證表格是否建立成功
        from sqlalchemy import inspect
        inspector = inspect(db_manager.engine)
        tables = inspector.get_table_names()

        logger.info(f"\n✅ 成功建立 {len(tables)} 個資料表:")
        for table_name in sorted(tables):
            logger.info(f"  - {table_name}")

        # 顯示各表的索引
        logger.info("\n索引資訊:")
        for table_name in sorted(tables):
            indexes = inspector.get_indexes(table_name)
            if indexes:
                logger.info(f"\n  {table_name}:")
                for idx in indexes:
                    logger.info(f"    - {idx['name']}: {idx['column_names']}")

        logger.info("\n" + "="*70)
        logger.info("✅ 資料庫初始化完成")
        logger.info("="*70)

        return 0

    except Exception as e:
        logger.error(f"❌ 資料庫初始化失敗: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(init_database())
