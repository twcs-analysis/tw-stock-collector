"""
JSON 檔案儲存模組

將轉換後的技術分析資料儲存為 JSON 檔案
"""

from pathlib import Path
import pandas as pd
import json
from datetime import datetime
from typing import Dict, Any
import logging

# 簡單的 logger 設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class JSONSaver:
    """
    JSON 檔案儲存器

    將技術分析資料儲存為 JSON 檔案
    """

    def __init__(self, base_path: str = 'data/transformed'):
        """
        Args:
            base_path: 基礎儲存路徑
        """
        self.base_path = Path(base_path)
        self.logger = logger

    def save_to_json(
        self,
        df: pd.DataFrame,
        date: str,
        data_type: str = 'technical_analysis'
    ) -> bool:
        """
        儲存 DataFrame 為 JSON 檔案

        Args:
            df: 要儲存的 DataFrame
            date: 日期 (YYYY-MM-DD)
            data_type: 資料類型

        Returns:
            bool: 是否成功
        """
        try:
            # 建立檔案路徑
            file_path = self._build_file_path(date, data_type)

            # 準備資料
            json_data = self._prepare_json_data(df, date, data_type)

            # 確保目錄存在
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # 寫入檔案
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)

            self.logger.info(
                f"成功儲存 {len(df)} 筆資料到 {file_path}"
            )

            return True

        except Exception as e:
            self.logger.error(f"儲存 JSON 失敗: {e}", exc_info=True)
            return False

    def _build_file_path(self, date: str, data_type: str) -> Path:
        """
        建立檔案路徑

        Args:
            date: 日期 (YYYY-MM-DD)
            data_type: 資料類型

        Returns:
            Path: 檔案路徑
        """
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        year = date_obj.year
        month = f'{date_obj.month:02d}'

        # data/transformed/technical_analysis/2026/01/2026-01-30.json
        file_path = self.base_path / data_type / str(year) / month / f'{date}.json'

        return file_path

    def _prepare_json_data(
        self,
        df: pd.DataFrame,
        date: str,
        data_type: str
    ) -> Dict[str, Any]:
        """
        準備 JSON 資料結構

        Args:
            df: DataFrame
            date: 日期
            data_type: 資料類型

        Returns:
            Dict: JSON 資料
        """
        # 處理 DataFrame
        df_clean = df.copy()

        # 將 datetime 轉為字串
        if 'trade_date' in df_clean.columns:
            df_clean['trade_date'] = df_clean['trade_date'].astype(str)

        # 將 NaN 轉為 None (在 JSON 中會變成 null)
        df_clean = df_clean.where(pd.notnull(df_clean), None)

        # 轉為 dict list
        data_list = df_clean.to_dict(orient='records')

        # 建立完整 JSON 結構
        json_data = {
            'metadata': {
                'date': date,
                'transformed_at': datetime.now().isoformat(),
                'total_count': len(data_list),
                'data_type': data_type,
                'transformer': 'TechnicalAnalysisTransformer',
                'version': '1.0.0'
            },
            'data': data_list
        }

        return json_data

    def load_from_json(self, date: str, data_type: str = 'technical_analysis') -> pd.DataFrame:
        """
        從 JSON 檔案載入資料

        Args:
            date: 日期 (YYYY-MM-DD)
            data_type: 資料類型

        Returns:
            pd.DataFrame: 載入的資料
        """
        try:
            file_path = self._build_file_path(date, data_type)

            if not file_path.exists():
                self.logger.warning(f"檔案不存在: {file_path}")
                return pd.DataFrame()

            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)

            df = pd.DataFrame(json_data['data'])

            # 轉換日期欄位
            if 'trade_date' in df.columns:
                df['trade_date'] = pd.to_datetime(df['trade_date'])

            self.logger.info(f"成功載入 {len(df)} 筆資料從 {file_path}")

            return df

        except Exception as e:
            self.logger.error(f"載入 JSON 失敗: {e}", exc_info=True)
            return pd.DataFrame()


def save_analysis_to_json(
    df: pd.DataFrame,
    date: str,
    base_path: str = 'data/transformed'
) -> bool:
    """
    便利函式：儲存技術分析資料為 JSON

    Args:
        df: 技術分析 DataFrame
        date: 日期 (YYYY-MM-DD)
        base_path: 基礎路徑

    Returns:
        bool: 是否成功
    """
    saver = JSONSaver(base_path)
    return saver.save_to_json(df, date)
