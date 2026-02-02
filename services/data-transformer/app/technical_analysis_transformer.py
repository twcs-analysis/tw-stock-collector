"""
技術分析轉換器

將原始價格資料轉換為包含技術指標的分析資料：
- 均線系統 (MA5, MA10, MA20, MA60, MA120, MA240)
- RSI 指標 (RSI6, RSI14)
- MACD 指標 (DIF, DEA, Histogram)
- DMI 指標 (PDI, MDI, ADX, ADXR)
- Bollinger Bands (上軌、中軌、下軌)
- 成交量分析 (Volume MA, Ratio, VWAP)
"""

from typing import Union, Optional
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.base_transformer import BaseTransformer, TransformerError
from common.utils import get_logger
import app.indicators as indicators  # 使用我們自己的指標計算模組

logger = get_logger(__name__)


class TechnicalAnalysisTransformer(BaseTransformer):
    """
    技術分析轉換器

    將原始價格資料轉換為包含技術指標的分析資料
    """

    def __init__(self, config: Optional[any] = None):
        """
        Args:
            config: 配置實例
        """
        super().__init__(config)

        # 計算技術指標所需的最少天數 (最長指標是 MA240)
        self.min_periods = 240

        # 歷史資料回溯天數 (約 1.5 年，確保有足夠的交易日)
        self.lookback_days = 550

    def get_source_data_type(self) -> str:
        """返回來源資料類型"""
        return "price"

    def get_target_data_type(self) -> str:
        """返回目標資料類型"""
        return "technical_analysis"

    def transform(
        self,
        date: Union[str, datetime],
        stock_id: Optional[str] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        轉換價格資料為技術分析資料

        Args:
            date: 轉換日期
            stock_id: 股票代碼 (選用，None 表示處理所有股票)
            **kwargs: 其他參數

        Returns:
            pd.DataFrame: 包含技術指標的資料

        Raises:
            TransformerError: 轉換失敗
        """
        try:
            # 載入歷史資料 (需要足夠的歷史資料來計算指標)
            historical_df = self._load_historical_data(date)

            if historical_df.empty:
                self.logger.warning(f"無歷史資料可供轉換: {date}")
                return pd.DataFrame()

            # 按股票分組計算技術指標
            result_list = []
            skipped_stocks = {
                'insufficient_data': [],
                'calculation_errors': []
            }
            grouped = historical_df.groupby('stock_id')
            total_stocks = len(grouped)

            self.logger.info(f"開始計算技術指標: {total_stocks} 檔股票")

            for idx, (stock_id_val, stock_df) in enumerate(grouped, 1):
                # 只處理有足夠資料的股票
                if len(stock_df) < self.min_periods:
                    skipped_stocks['insufficient_data'].append({
                        'stock_id': stock_id_val,
                        'available_days': len(stock_df),
                        'required_days': self.min_periods
                    })
                    self.logger.debug(
                        f"跳過 {stock_id_val}: 資料不足 "
                        f"({len(stock_df)} < {self.min_periods})"
                    )
                    continue

                # 計算技術指標
                try:
                    stock_df_with_indicators = self._calculate_indicators(stock_df.copy())
                    result_list.append(stock_df_with_indicators)
                except Exception as e:
                    skipped_stocks['calculation_errors'].append({
                        'stock_id': stock_id_val,
                        'error': str(e)
                    })
                    self.logger.error(
                        f"計算指標失敗 {stock_id_val}: {e}"
                    )

                if idx % 100 == 0:
                    self.logger.info(f"已處理 {idx}/{total_stocks} 檔股票")

            # 報告跳過的股票統計
            if skipped_stocks['insufficient_data']:
                self.logger.warning(
                    f"跳過 {len(skipped_stocks['insufficient_data'])} 檔股票 (資料不足): "
                    f"前 5 檔: {[s['stock_id'] for s in skipped_stocks['insufficient_data'][:5]]}"
                )

            if skipped_stocks['calculation_errors']:
                self.logger.error(
                    f"跳過 {len(skipped_stocks['calculation_errors'])} 檔股票 (計算錯誤): "
                    f"前 5 檔: {[s['stock_id'] for s in skipped_stocks['calculation_errors'][:5]]}"
                )

            if not result_list:
                self.logger.warning(
                    f"沒有股票有足夠資料可計算指標。"
                    f"共跳過 {len(skipped_stocks['insufficient_data'])} 檔股票"
                )
                return pd.DataFrame()

            # 合併所有股票
            result_df = pd.concat(result_list, ignore_index=True)

            # 只保留目標日期的資料
            target_date_str = self._format_date(date)
            result_df = result_df[result_df['trade_date'] == target_date_str].copy()

            self.logger.info(
                f"技術指標計算完成: {len(result_df)} 筆記錄 "
                f"({len(result_list)} 檔股票)"
            )

            return result_df

        except Exception as e:
            raise TransformerError(f"技術分析轉換失敗: {e}") from e

    def _load_historical_data(
        self,
        target_date: Union[str, datetime]
    ) -> pd.DataFrame:
        """
        載入歷史資料

        需要載入足夠的歷史資料來計算技術指標：
        - MA240 需要至少 240 天
        - 策略: 載入過去約 1.5 年的資料 (約 240 交易日)

        使用資料庫模式時，直接查詢區間資料，效率更高

        Args:
            target_date: 目標日期

        Returns:
            pd.DataFrame: 歷史資料
        """
        if isinstance(target_date, str):
            target_date = datetime.strptime(target_date, "%Y-%m-%d")

        # 使用資料庫載入 (推薦，效率更高)
        if self.use_database:
            self.logger.info(
                f"使用資料庫載入歷史資料 (回溯 {self.lookback_days} 天)"
            )

            df = self.db_loader.load_historical_data(
                target_date=target_date,
                lookback_days=self.lookback_days,
                stock_id=None
            )

            if df.empty:
                self.logger.warning("無歷史資料")
                return pd.DataFrame()

            self.logger.info(
                f"歷史資料載入完成: {len(df)} 筆記錄, "
                f"{df['stock_id'].nunique()} 檔股票"
            )

            return df

        # 使用檔案系統載入 (舊方法，逐日載入)
        else:
            return self._load_historical_data_from_files(target_date)

    def _load_historical_data_from_files(
        self,
        target_date: datetime
    ) -> pd.DataFrame:
        """
        從檔案系統載入歷史資料 (舊方法)

        逐日載入，跳過周末和假期

        Args:
            target_date: 目標日期

        Returns:
            pd.DataFrame: 歷史資料
        """
        # 計算起始日期 (往前推 lookback_days 天)
        start_date = target_date - timedelta(days=self.lookback_days)

        self.logger.info(
            f"從檔案系統載入歷史資料: {start_date.date()} 到 {target_date.date()}"
        )

        # 收集所有歷史資料
        all_data = []
        current = start_date
        failed_consecutive = 0  # 連續失敗計數
        total_attempts = 0
        successful_loads = 0

        while current <= target_date:
            try:
                # 載入單日資料
                df = self._load_from_file(current, stock_id=None)

                if not df.empty:
                    # 確保有 date 欄位
                    if 'date' in df.columns:
                        df = df.rename(columns={'date': 'trade_date'})
                    elif 'trade_date' not in df.columns:
                        df['trade_date'] = current.strftime('%Y-%m-%d')

                    all_data.append(df)
                    successful_loads += 1
                    failed_consecutive = 0  # 重置連續失敗計數
                else:
                    failed_consecutive += 1

            except Exception as e:
                failed_consecutive += 1
                # 只在 debug 模式記錄失敗（避免過多日誌）
                if failed_consecutive <= 3:
                    self.logger.debug(f"載入 {current.date()} 資料失敗: {e}")

            total_attempts += 1

            # 優化: 連續失敗超過 5 天後，跳過更多天數（可能是長假期）
            if failed_consecutive > 5:
                if failed_consecutive == 6:
                    self.logger.debug(
                        f"檢測到可能的假期區間，從 {current.date()} 開始加速跳過"
                    )
                # 跳過 2 天，加速通過周末和假期
                current += timedelta(days=3)
                failed_consecutive = 0  # 重置計數，避免無限跳躍
            else:
                current += timedelta(days=1)

        if not all_data:
            self.logger.warning("無歷史資料")
            return pd.DataFrame()

        # 合併所有資料
        df = pd.concat(all_data, ignore_index=True)
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df = df.sort_values(['stock_id', 'trade_date'])

        self.logger.info(
            f"檔案載入完成: {len(df)} 筆記錄 "
            f"({len(df['stock_id'].unique())} 檔股票), "
            f"成功載入 {successful_loads}/{total_attempts} 天"
        )

        return df

    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        計算單一股票的所有技術指標

        統一使用 datetime 格式進行所有計算，只在最後轉為字串

        Args:
            df: 股票的歷史價格資料

        Returns:
            pd.DataFrame: 包含技術指標的資料
        """
        # 確保 trade_date 是 datetime 格式（統一數據類型）
        if not pd.api.types.is_datetime64_any_dtype(df['trade_date']):
            df['trade_date'] = pd.to_datetime(df['trade_date'])

        # 設定索引為日期
        df = df.set_index('trade_date').sort_index()

        # ========================================
        # 1. 均線系統 (Moving Averages)
        # ========================================
        df['ma_5'] = indicators.sma(df['close'], 5)
        df['ma_10'] = indicators.sma(df['close'], 10)
        df['ma_20'] = indicators.sma(df['close'], 20)
        df['ma_60'] = indicators.sma(df['close'], 60)
        df['ma_120'] = indicators.sma(df['close'], 120)
        df['ma_240'] = indicators.sma(df['close'], 240)

        # ========================================
        # 2. RSI (相對強弱指標)
        # ========================================
        df['rsi_6'] = indicators.rsi(df['close'], 6)
        df['rsi_14'] = indicators.rsi(df['close'], 14)

        # ========================================
        # 3. MACD (指數平滑異同移動平均線)
        # ========================================
        macd_df = indicators.macd(df['close'], fast=12, slow=26, signal=9)
        df['macd_dif'] = macd_df['DIF']
        df['macd_dea'] = macd_df['DEA']
        df['macd_hist'] = macd_df['Histogram']

        # ========================================
        # 4. DMI/ADX (趨向指標)
        # ========================================
        adx_df = indicators.adx(df['high'], df['low'], df['close'], period=14)
        df['dmi_pdi'] = adx_df['PDI']
        df['dmi_mdi'] = adx_df['MDI']
        df['dmi_adx'] = adx_df['ADX']
        # 注意: 簡化版沒有 ADXR，可設為 None 或移除
        df['dmi_adxr'] = None

        # ========================================
        # 5. Bollinger Bands (布林通道)
        # ========================================
        bb_df = indicators.bollinger_bands(df['close'], period=20, std_dev=2.0)
        df['bb_upper'] = bb_df['upper']
        df['bb_mid'] = bb_df['middle']
        df['bb_lower'] = bb_df['lower']

        # ========================================
        # 6. 成交量分析
        # ========================================
        df['vol_ma5'] = indicators.sma(df['volume'], 5)
        df['vol_ma20'] = indicators.sma(df['volume'], 20)

        # 量比 (當日量 / 5日均量)
        df['vol_ratio'] = df['volume'] / df['vol_ma5']

        # VWAP (成交量加權平均價) = 成交金額 / 成交量
        df['vwap'] = indicators.vwap(df['amount'], df['volume'])

        # ========================================
        # 重置索引，保留原始欄位
        # ========================================
        df = df.reset_index()

        # 定義輸出欄位
        output_columns = [
            # 基礎資料
            'trade_date', 'stock_id',
            'open', 'high', 'low', 'close', 'volume', 'amount',
            # 均線
            'ma_5', 'ma_10', 'ma_20', 'ma_60', 'ma_120', 'ma_240',
            # RSI
            'rsi_6', 'rsi_14',
            # MACD
            'macd_dif', 'macd_dea', 'macd_hist',
            # DMI
            'dmi_pdi', 'dmi_mdi', 'dmi_adx', 'dmi_adxr',
            # Bollinger
            'bb_upper', 'bb_mid', 'bb_lower',
            # Volume
            'vol_ma5', 'vol_ma20', 'vol_ratio', 'vwap'
        ]

        # 只保留存在的欄位，並記錄缺失的欄位
        existing_columns = [col for col in output_columns if col in df.columns]
        missing_columns = [col for col in output_columns if col not in df.columns]

        if missing_columns:
            stock_id = df['stock_id'].iloc[0] if not df.empty and 'stock_id' in df.columns else 'unknown'
            self.logger.warning(
                f"股票 {stock_id} 缺少欄位: {missing_columns}"
            )

        df = df[existing_columns]

        # 只在最後轉為字串格式（統一數據類型轉換時機）
        df['trade_date'] = df['trade_date'].dt.strftime('%Y-%m-%d')

        return df

    def __repr__(self) -> str:
        return (
            f"TechnicalAnalysisTransformer("
            f"min_periods={self.min_periods}, "
            f"lookback_days={self.lookback_days})"
        )
