"""初始化資料庫"""
from app.db import DatabaseManager, DatabaseConfig

db_config = DatabaseConfig.from_env()
print(f"Initializing: {db_config.get_url()}")

manager = DatabaseManager(db_config)
manager.init_engine()
manager.create_tables()

print("✓ Tables created!")

if manager.test_connection():
    print("✓ Connection OK!")
