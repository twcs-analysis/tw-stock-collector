"""
Database Connection Manager

支援 PostgreSQL 和 SQLite 的連線管理
"""

import os
from typing import Optional
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool, QueuePool

from .models import Base


class DatabaseConfig:
    """資料庫配置"""

    def __init__(
        self,
        db_type: str = "postgresql",
        host: str = "localhost",
        port: int = 5432,
        database: str = "tw_stock",
        user: str = "postgres",
        password: str = "",
        sqlite_path: Optional[str] = None
    ):
        self.db_type = db_type.lower()
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.sqlite_path = sqlite_path or "database/sqlite/tw_stock.db"

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """從環境變數載入配置"""
        db_type = os.getenv("DB_TYPE", "postgresql")

        if db_type == "sqlite":
            return cls(
                db_type="sqlite",
                sqlite_path=os.getenv("SQLITE_PATH", "database/sqlite/tw_stock.db")
            )
        else:
            return cls(
                db_type=db_type,
                host=os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("DB_PORT", "5432")),
                database=os.getenv("DB_NAME", "tw_stock"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", "")
            )

    @classmethod
    def from_url(cls, database_url: str) -> "DatabaseConfig":
        """從 DATABASE_URL 字串解析配置"""
        # 簡化版本，實際可用 sqlalchemy.engine.url.make_url
        if database_url.startswith("sqlite"):
            return cls(
                db_type="sqlite",
                sqlite_path=database_url.replace("sqlite:///", "")
            )
        # PostgreSQL URL 解析留給 SQLAlchemy
        config = cls()
        config._url = database_url
        return config

    def get_url(self) -> str:
        """獲取資料庫連線 URL"""
        if hasattr(self, '_url'):
            return self._url

        if self.db_type == "sqlite":
            # SQLite
            return f"sqlite:///{self.sqlite_path}"
        elif self.db_type == "postgresql":
            # PostgreSQL
            return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.db_type == "mysql":
            # MySQL (選用)
            return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")


class DatabaseManager:
    """資料庫管理器"""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None

    def init_engine(self, **kwargs):
        """初始化資料庫引擎"""
        url = self.config.get_url()

        # 根據資料庫類型設定連線池
        if self.config.db_type == "sqlite":
            # SQLite: 不使用連線池，啟用 foreign keys
            engine_kwargs = {
                "poolclass": NullPool,
                "connect_args": {"check_same_thread": False},
                **kwargs
            }

            # SQLite 啟用外鍵約束
            @event.listens_for(Engine, "connect")
            def set_sqlite_pragma(dbapi_conn, connection_record):
                if 'sqlite' in str(dbapi_conn):
                    cursor = dbapi_conn.cursor()
                    cursor.execute("PRAGMA foreign_keys=ON")
                    cursor.close()

        else:
            # PostgreSQL/MySQL: 使用連線池
            engine_kwargs = {
                "poolclass": QueuePool,
                "pool_size": kwargs.get("pool_size", 5),
                "max_overflow": kwargs.get("max_overflow", 10),
                "pool_pre_ping": True,  # 連線前先 ping，確保連線有效
                **kwargs
            }

        self.engine = create_engine(url, **engine_kwargs)
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def create_tables(self):
        """建立所有資料表"""
        if not self.engine:
            raise RuntimeError("Engine not initialized. Call init_engine() first.")
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        """刪除所有資料表 (慎用!)"""
        if not self.engine:
            raise RuntimeError("Engine not initialized. Call init_engine() first.")
        Base.metadata.drop_all(bind=self.engine)

    @contextmanager
    def get_session(self) -> Session:
        """獲取資料庫 Session (Context Manager)"""
        if not self.SessionLocal:
            raise RuntimeError("SessionLocal not initialized. Call init_engine() first.")

        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def test_connection(self) -> bool:
        """測試資料庫連線"""
        try:
            from sqlalchemy import text
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False

    def close(self):
        """關閉資料庫連線"""
        if self.engine:
            self.engine.dispose()


# 全域資料庫管理器實例 (單例模式)
_db_manager: Optional[DatabaseManager] = None


def get_db_manager(config: Optional[DatabaseConfig] = None) -> DatabaseManager:
    """獲取全域資料庫管理器"""
    global _db_manager

    if _db_manager is None:
        if config is None:
            # 從環境變數或 DATABASE_URL 載入配置
            database_url = os.getenv("DATABASE_URL")
            if database_url:
                config = DatabaseConfig.from_url(database_url)
            else:
                config = DatabaseConfig.from_env()

        _db_manager = DatabaseManager(config)
        _db_manager.init_engine()

    return _db_manager


def init_database(config: Optional[DatabaseConfig] = None):
    """初始化資料庫 (建立所有資料表)"""
    manager = get_db_manager(config)
    manager.create_tables()
    return manager


def get_connection_string() -> str:
    """
    取得資料庫連線字串

    優先級:
    1. 環境變數 DATABASE_URL
    2. 環境變數 DB_* 設定
    3. 預設值（PostgreSQL localhost）

    Returns:
        資料庫連線字串
    """
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    # 從環境變數或使用預設值
    config = DatabaseConfig.from_env()

    # 如果沒有設定密碼，使用預設密碼
    if not config.password and config.db_type == "postgresql":
        config.password = os.getenv("DB_PASSWORD", "tw_stock_dev_password_2024")

    return config.get_url()
