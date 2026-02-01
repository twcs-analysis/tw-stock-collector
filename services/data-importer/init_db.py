"""初始化資料庫 - 建立所有資料表"""

import sys
import os

# 加入專案路徑
sys.path.insert(0, os.path.abspath('.'))

from services.data_importer.app.db import init_database, DatabaseConfig

def main():
    # 從環境變數載入配置
    db_config = DatabaseConfig.from_env()

    print(f"Initializing database: {db_config.get_url()}")

    # 建立所有資料表
    manager = init_database(db_config)

    print("✓ Database tables created successfully!")

    # 測試連線
    if manager.test_connection():
        print("✓ Database connection test passed!")
    else:
        print("✗ Database connection test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
