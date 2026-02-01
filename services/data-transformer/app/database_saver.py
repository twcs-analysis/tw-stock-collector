"""
資料庫儲存模組

將轉換後的技術分析資料儲存到資料庫
"""

from pathlib import Path
import pandas as pd
from typing import Optional
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from common.utils import get_logger

logger = get_logger(__name__)


class DatabaseSaver:
    """
    資料庫儲存器

    將技術分析資料儲存到 stock_analysis_daily 資料表
    使用連接池以提升性能
    """

    def __init__(self, database_url: Optional[str] = None):
        """
        Args:
            database_url: 資料庫連線字串 (PostgreSQL 或 SQLite)
        """
        self.database_url = database_url or self._get_default_db_url()
        self.logger = get_logger(__name__)
        self._engine = None  # 緩存引擎實例

    def _get_default_db_url(self) -> str:
        """取得預設資料庫 URL"""
        import os
        return os.getenv(
            'DATABASE_URL',
            'sqlite:///data/tw_stock.db'  # 預設使用 SQLite
        )

    def _get_engine(self):
        """獲取或創建引擎（連接池）"""
        if self._engine is None:
            from sqlalchemy import create_engine
            self._engine = create_engine(
                self.database_url,
                pool_size=10,           # 連接池大小
                max_overflow=20,        # 超出池大小時的額外連接
                pool_recycle=3600,      # 1小時回收連接
                echo=False              # 不輸出 SQL（性能）
            )
        return self._engine

    def close(self):
        """顯式關閉連接"""
        if self._engine:
            self._engine.dispose()
            self._engine = None

    def __del__(self):
        """對象銷毀時關閉連接"""
        self.close()

    def save_to_database(
        self,
        df: pd.DataFrame,
        table_name: str = 'stock_analysis_daily',
        if_exists: str = 'append'
    ) -> bool:
        """
        儲存資料到資料庫（使用連接池和事務管理）

        Args:
            df: 要儲存的 DataFrame
            table_name: 資料表名稱
            if_exists: 'append', 'replace', 或 'fail'

        Returns:
            bool: 是否成功
        """
        try:
            engine = self._get_engine()  # 使用連接池

            # 準備資料
            df_to_save = self._prepare_dataframe(df)

            # 根據數據量調整 chunksize
            row_count = len(df_to_save)
            if row_count > 100000:
                chunksize = 5000  # 大數據量用更大的 chunk
            elif row_count > 10000:
                chunksize = 2000
            else:
                chunksize = 1000  # 小數據量用小 chunk

            self.logger.info(
                f"開始儲存 {row_count} 筆資料到 {table_name} (chunksize={chunksize})"
            )

            # 使用事務管理
            with engine.begin() as connection:
                # 寫入資料庫
                df_to_save.to_sql(
                    name=table_name,
                    con=connection,
                    if_exists=if_exists,
                    index=False,
                    method='multi',  # 批次插入，效能較好
                    chunksize=chunksize
                )

            self.logger.info(
                f"成功儲存 {row_count} 筆資料到 {table_name}"
            )
            return True

        except ImportError:
            self.logger.error(
                "缺少 sqlalchemy 套件，請安裝: pip install sqlalchemy"
            )
            return False

        except Exception as e:
            self.logger.error(f"儲存到資料庫失敗（已回滾）: {e}", exc_info=True)
            return False

    def _prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        準備 DataFrame 以符合資料庫 schema，包含數據驗證

        Args:
            df: 原始 DataFrame

        Returns:
            pd.DataFrame: 處理後的 DataFrame
        """
        df_prep = df.copy()

        # 確保日期格式正確
        if 'trade_date' in df_prep.columns:
            df_prep['trade_date'] = pd.to_datetime(df_prep['trade_date'])

        # 移除不需要的欄位
        columns_to_remove = ['type', 'stock_name', 'transaction_count', 'change_price']
        for col in columns_to_remove:
            if col in df_prep.columns:
                df_prep = df_prep.drop(columns=[col])

        # 定義預期的欄位和類型
        expected_columns = [
            'trade_date', 'stock_id',
            'open', 'high', 'low', 'close', 'volume', 'amount',
            'ma_5', 'ma_10', 'ma_20', 'ma_60', 'ma_120', 'ma_240',
            'rsi_6', 'rsi_14',
            'macd_dif', 'macd_dea', 'macd_hist',
            'dmi_pdi', 'dmi_mdi', 'dmi_adx', 'dmi_adxr',
            'bb_upper', 'bb_mid', 'bb_lower',
            'vol_ma5', 'vol_ma20', 'vol_ratio', 'vwap'
        ]

        type_mapping = {
            'trade_date': 'datetime64[ns]',
            'stock_id': 'object',  # 字符串
            'open': 'float64',
            'high': 'float64',
            'low': 'float64',
            'close': 'float64',
            'volume': 'int64',
            'amount': 'float64',
        }

        # 數據類型轉換
        for col, dtype in type_mapping.items():
            if col in df_prep.columns:
                try:
                    if dtype == 'datetime64[ns]':
                        df_prep[col] = pd.to_datetime(df_prep[col])
                    else:
                        df_prep[col] = df_prep[col].astype(dtype)
                except Exception as e:
                    self.logger.warning(f"無法轉換列 {col} 為 {dtype}: {e}")

        # 驗證必要列
        required_columns = ['trade_date', 'stock_id', 'close']
        missing_columns = [col for col in required_columns if col not in df_prep.columns]
        if missing_columns:
            raise ValueError(f"缺少必要列: {missing_columns}")

        # 檢查 NULL 值
        null_counts = df_prep[required_columns].isnull().sum()
        if null_counts.any():
            self.logger.warning(f"必要列發現 NULL 值:\n{null_counts[null_counts > 0]}")

        # 檢查重複值
        duplicates = df_prep[['trade_date', 'stock_id']].duplicated().sum()
        if duplicates > 0:
            self.logger.warning(f"發現 {duplicates} 個重複記錄，將保留最後一筆")
            df_prep = df_prep.drop_duplicates(subset=['trade_date', 'stock_id'], keep='last')

        # 只保留存在的欄位
        existing_columns = [col for col in expected_columns if col in df_prep.columns]
        df_prep = df_prep[existing_columns]

        return df_prep

    def upsert_to_database(
        self,
        df: pd.DataFrame,
        table_name: str = 'stock_analysis_daily'
    ) -> bool:
        """
        使用 UPSERT 邏輯儲存資料（更新已存在的記錄）

        Args:
            df: 要儲存的 DataFrame
            table_name: 資料表名稱

        Returns:
            bool: 是否成功
        """
        try:
            from sqlalchemy import create_engine, text

            engine = create_engine(self.database_url)
            df_to_save = self._prepare_dataframe(df)

            # 使用 ON CONFLICT 語法 (PostgreSQL 和新版 SQLite 支援)
            with engine.begin() as conn:
                # 先刪除相同日期和股票的舊資料
                for _, row in df_to_save.iterrows():
                    conn.execute(
                        text(f"""
                            DELETE FROM {table_name}
                            WHERE trade_date = :date AND stock_id = :stock_id
                        """),
                        {'date': row['trade_date'], 'stock_id': row['stock_id']}
                    )

                # 插入新資料
                df_to_save.to_sql(
                    name=table_name,
                    con=conn,
                    if_exists='append',
                    index=False,
                    method='multi',
                    chunksize=1000
                )

            self.logger.info(
                f"成功 UPSERT {len(df_to_save)} 筆資料到 {table_name}"
            )

            engine.dispose()
            return True

        except Exception as e:
            self.logger.error(f"UPSERT 到資料庫失敗: {e}", exc_info=True)
            return False


def save_analysis_to_db(
    df: pd.DataFrame,
    database_url: Optional[str] = None,
    upsert: bool = True
) -> bool:
    """
    便利函式：儲存技術分析資料到資料庫

    Args:
        df: 技術分析 DataFrame
        database_url: 資料庫連線字串
        upsert: 是否使用 UPSERT (更新已存在的記錄)

    Returns:
        bool: 是否成功
    """
    saver = DatabaseSaver(database_url)

    if upsert:
        return saver.upsert_to_database(df)
    else:
        return saver.save_to_database(df)
