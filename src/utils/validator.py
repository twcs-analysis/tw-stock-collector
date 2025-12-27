"""
資料驗證模組

提供各類資料的驗證功能：
- 價格資料驗證
- 法人資料驗證
- 融資融券資料驗證
- 資料完整性檢查
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import pandas as pd

from .logger import get_logger
from .config import get_global_config

logger = get_logger(__name__)


class ValidationError(Exception):
    """驗證錯誤異常"""
    pass


class DataValidator:
    """資料驗證器"""

    def __init__(self, config: Optional[Any] = None):
        """
        Args:
            config: 配置實例，預設使用全域配置
        """
        if config is None:
            config = get_global_config()
        self.config = config
        self.validation_rules = config.validation.rules.to_dict()
        self.on_error = config.validation.on_validation_error

    def validate(
        self,
        df: pd.DataFrame,
        data_type: str,
        raise_on_error: bool = False
    ) -> bool:
        """
        驗證 DataFrame

        Args:
            df: 待驗證的 DataFrame
            data_type: 資料類型 (price, institutional, margin 等)
            raise_on_error: 是否在驗證失敗時拋出異常

        Returns:
            bool: 是否通過驗證

        Raises:
            ValidationError: 驗證失敗且 raise_on_error=True
        """
        if df is None or df.empty:
            msg = f"資料為空: {data_type}"
            logger.warning(msg)
            if raise_on_error or self.on_error == 'raise':
                raise ValidationError(msg)
            return False

        # 根據資料類型選擇驗證方法
        validator_map = {
            'price': self._validate_price_data,
            'institutional': self._validate_institutional_data,
            'margin': self._validate_margin_data,
            'lending': self._validate_lending_data,
            'foreign_holding': self._validate_foreign_holding_data,
            'shareholding': self._validate_shareholding_data,
            'director': self._validate_director_data,
        }

        validator_func = validator_map.get(data_type)
        if validator_func is None:
            logger.warning(f"未知的資料類型: {data_type}")
            return True  # 未知類型預設通過

        try:
            validator_func(df)
            logger.debug(f"驗證通過: {data_type} ({len(df)} rows)")
            return True

        except ValidationError as e:
            logger.error(f"驗證失敗: {data_type} - {e}")
            if raise_on_error or self.on_error == 'raise':
                raise
            return False

    def _validate_price_data(self, df: pd.DataFrame) -> None:
        """驗證價格資料"""
        rules = self.validation_rules.get('price', {})

        # 檢查必要欄位
        required_cols = rules.get('required_columns', ['stock_id', 'date', 'close'])
        self._check_required_columns(df, required_cols, 'price')

        # 檢查數值範圍
        if 'close' in df.columns:
            if (df['close'] <= 0).any():
                raise ValidationError("收盤價必須大於 0")

        if 'volume' in df.columns:
            min_volume = rules.get('min_volume', 0)
            if (df['volume'] < min_volume).any():
                raise ValidationError(f"成交量不能小於 {min_volume}")

        # 檢查漲跌幅
        if 'change_rate' in df.columns:
            max_change = rules.get('max_change_rate', 0.15)
            if (df['change_rate'].abs() > max_change).any():
                raise ValidationError(f"漲跌幅超過限制: {max_change * 100}%")

        # 檢查 OHLC 邏輯
        if all(col in df.columns for col in ['open', 'high', 'low', 'close']):
            invalid = (
                (df['high'] < df['low']) |
                (df['high'] < df['open']) |
                (df['high'] < df['close']) |
                (df['low'] > df['open']) |
                (df['low'] > df['close'])
            )
            if invalid.any():
                raise ValidationError("OHLC 資料邏輯錯誤")

    def _validate_institutional_data(self, df: pd.DataFrame) -> None:
        """驗證法人資料"""
        rules = self.validation_rules.get('institutional', {})

        required_cols = rules.get('required_columns', [
            'stock_id', 'date', 'foreign_net', 'trust_net', 'dealer_net'
        ])
        self._check_required_columns(df, required_cols, 'institutional')

        # 檢查買賣超數值 (可以是負數)
        numeric_cols = ['foreign_net', 'trust_net', 'dealer_net']
        for col in numeric_cols:
            if col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    raise ValidationError(f"欄位 {col} 必須是數值類型")

    def _validate_margin_data(self, df: pd.DataFrame) -> None:
        """驗證融資融券資料"""
        rules = self.validation_rules.get('margin', {})

        required_cols = rules.get('required_columns', [
            'stock_id', 'date', 'margin_purchase', 'margin_sale'
        ])
        self._check_required_columns(df, required_cols, 'margin')

        # 檢查非負數
        numeric_cols = ['margin_purchase', 'margin_sale', 'short_sale', 'short_covering']
        for col in numeric_cols:
            if col in df.columns:
                if (df[col] < 0).any():
                    raise ValidationError(f"欄位 {col} 不能為負數")

    def _validate_lending_data(self, df: pd.DataFrame) -> None:
        """驗證借券賣出資料"""
        required_cols = ['stock_id', 'date', 'lending_balance']
        self._check_required_columns(df, required_cols, 'lending')

    def _validate_foreign_holding_data(self, df: pd.DataFrame) -> None:
        """驗證外資持股資料"""
        required_cols = ['stock_id', 'date', 'foreign_holding_ratio']
        self._check_required_columns(df, required_cols, 'foreign_holding')

        # 檢查持股比例範圍
        if 'foreign_holding_ratio' in df.columns:
            if ((df['foreign_holding_ratio'] < 0) | (df['foreign_holding_ratio'] > 100)).any():
                raise ValidationError("外資持股比例必須在 0-100 之間")

    def _validate_shareholding_data(self, df: pd.DataFrame) -> None:
        """驗證股權分散表資料"""
        required_cols = ['stock_id', 'date']
        self._check_required_columns(df, required_cols, 'shareholding')

    def _validate_director_data(self, df: pd.DataFrame) -> None:
        """驗證董監持股資料"""
        required_cols = ['stock_id', 'date']
        self._check_required_columns(df, required_cols, 'director')

    def _check_required_columns(
        self,
        df: pd.DataFrame,
        required_cols: List[str],
        data_type: str
    ) -> None:
        """
        檢查必要欄位

        Args:
            df: DataFrame
            required_cols: 必要欄位清單
            data_type: 資料類型

        Raises:
            ValidationError: 缺少必要欄位
        """
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            raise ValidationError(
                f"{data_type} 缺少必要欄位: {', '.join(missing_cols)}"
            )

    def validate_date_format(self, date_str: str) -> bool:
        """
        驗證日期格式

        Args:
            date_str: 日期字串

        Returns:
            bool: 是否有效

        Examples:
            >>> validator = DataValidator()
            >>> validator.validate_date_format('2025-01-28')  # True
            >>> validator.validate_date_format('2025/01/28')  # False
        """
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def validate_stock_id(self, stock_id: str) -> bool:
        """
        驗證股票代碼格式

        Args:
            stock_id: 股票代碼

        Returns:
            bool: 是否有效

        Examples:
            >>> validator = DataValidator()
            >>> validator.validate_stock_id('2330')  # True
            >>> validator.validate_stock_id('00XX')  # False
        """
        import re

        # 4 位數字股票代碼，或 ETF (00XX, 00XXX)
        pattern = r'^(\d{4}|00\d{2,3})$'
        return bool(re.match(pattern, stock_id))


def check_data_completeness(
    df: pd.DataFrame,
    expected_count: Optional[int] = None,
    date_column: str = 'date',
    stock_id_column: str = 'stock_id'
) -> Dict[str, Any]:
    """
    檢查資料完整性

    Args:
        df: DataFrame
        expected_count: 預期筆數
        date_column: 日期欄位名稱
        stock_id_column: 股票代碼欄位名稱

    Returns:
        完整性報告 dict

    Examples:
        >>> report = check_data_completeness(df, expected_count=1500)
        >>> print(f"完整率: {report['completeness_rate']:.2%}")
    """
    total_rows = len(df)
    unique_stocks = df[stock_id_column].nunique() if stock_id_column in df.columns else 0
    unique_dates = df[date_column].nunique() if date_column in df.columns else 0

    # 缺失值統計
    missing_stats = {}
    for col in df.columns:
        missing_count = df[col].isna().sum()
        if missing_count > 0:
            missing_stats[col] = {
                'count': int(missing_count),
                'ratio': float(missing_count / total_rows)
            }

    # 重複資料
    if stock_id_column in df.columns and date_column in df.columns:
        duplicates = df.duplicated(subset=[stock_id_column, date_column], keep=False).sum()
    else:
        duplicates = 0

    report = {
        'total_rows': total_rows,
        'unique_stocks': unique_stocks,
        'unique_dates': unique_dates,
        'missing_values': missing_stats,
        'duplicate_rows': int(duplicates),
        'completeness_rate': 1.0 if expected_count is None else min(total_rows / expected_count, 1.0)
    }

    return report


def quick_validate(df: pd.DataFrame, data_type: str) -> bool:
    """
    快速驗證（便利函數）

    Args:
        df: DataFrame
        data_type: 資料類型

    Returns:
        bool: 是否通過驗證

    Examples:
        >>> if quick_validate(df, 'price'):
        ...     save_to_file(df)
    """
    try:
        validator = DataValidator()
        return validator.validate(df, data_type, raise_on_error=False)
    except Exception as e:
        logger.error(f"驗證失敗: {e}")
        return False
