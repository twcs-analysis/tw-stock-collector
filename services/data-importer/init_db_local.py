"""初始化資料庫"""
from app.db import init_database, DatabaseConfig

db_config = DatabaseConfig.from_env()
print(f"Initializing: {db_config.get_url()}")

manager = init_database(db_config)
print("✓ Tables created!")

if manager.test_connection():
    print("✓ Connection OK!")
