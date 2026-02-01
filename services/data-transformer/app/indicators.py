"""
技術指標計算模組

使用純 pandas/numpy 實作常用技術指標
不依賴 pandas-ta 或 ta-lib，適用於任何 Python 版本
"""

import pandas as pd
import numpy as np


def sma(series: pd.Series, period: int) -> pd.Series:
    """
    Simple Moving Average (簡單移動平均)

    Args:
        series: 價格序列
        period: 週期

    Returns:
        pd.Series: SMA 值
    """
    return series.rolling(window=period, min_periods=period).mean()


def ema(series: pd.Series, period: int) -> pd.Series:
    """
    Exponential Moving Average (指數移動平均)

    Args:
        series: 價格序列
        period: 週期

    Returns:
        pd.Series: EMA 值
    """
    return series.ewm(span=period, adjust=False, min_periods=period).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Relative Strength Index (相對強弱指標)

    Args:
        series: 價格序列
        period: 週期 (預設 14)

    Returns:
        pd.Series: RSI 值 (0-100)

    Note:
        當股票持續上漲 (avg_loss = 0) 時，RSI 設為 100
        當股票持續下跌 (avg_gain = 0) 時，RSI 設為 0
        其他無法計算的情況設為 50 (中性)
    """
    delta = series.diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    # 處理除以零的情況
    with np.errstate(divide='ignore', invalid='ignore'):
        # 將 avg_loss 為 0 的情況替換為 NaN，避免除以零
        rs = avg_gain / avg_loss.replace(0, np.nan)

    rsi_val = 100 - (100 / (1 + rs))

    # 處理特殊情況：
    # - 當 avg_loss = 0 (持續上漲)，RSI 應該是 100
    # - 當 avg_gain = 0 (持續下跌)，RSI 應該是 0
    # - 其他無法計算的情況設為 50 (中性)
    rsi_val = rsi_val.mask((avg_gain > 0) & (avg_loss == 0), 100)
    rsi_val = rsi_val.mask((avg_gain == 0) & (avg_loss > 0), 0)
    rsi_val = rsi_val.fillna(50)

    return rsi_val


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """
    MACD (指數平滑異同移動平均線)

    Args:
        series: 價格序列
        fast: 快線週期 (預設 12)
        slow: 慢線週期 (預設 26)
        signal: 訊號線週期 (預設 9)

    Returns:
        pd.DataFrame: 包含 DIF, DEA, Histogram
    """
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)

    dif = ema_fast - ema_slow  # DIF (快線)
    dea = ema(dif, signal)      # DEA (慢線/訊號線)
    histogram = dif - dea       # Histogram (柱狀體)

    return pd.DataFrame({
        'DIF': dif,
        'DEA': dea,
        'Histogram': histogram
    })


def bollinger_bands(series: pd.Series, period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
    """
    Bollinger Bands (布林通道)

    Args:
        series: 價格序列
        period: 週期 (預設 20)
        std_dev: 標準差倍數 (預設 2)

    Returns:
        pd.DataFrame: 包含 upper, middle, lower
    """
    middle = sma(series, period)
    std = series.rolling(window=period, min_periods=period).std()

    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)

    return pd.DataFrame({
        'upper': upper,
        'middle': middle,
        'lower': lower
    })


def vwap(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series) -> pd.Series:
    """
    Volume Weighted Average Price (成交量加權平均價)

    Args:
        high: 最高價序列
        low: 最低價序列
        close: 收盤價序列
        volume: 成交量序列

    Returns:
        pd.Series: VWAP 值
    """
    typical_price = (high + low + close) / 3
    return (typical_price * volume).cumsum() / volume.cumsum()


def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """
    Average True Range (真實波動幅度均值)

    Args:
        high: 最高價序列
        low: 最低價序列
        close: 收盤價序列
        period: 週期 (預設 14)

    Returns:
        pd.Series: ATR 值
    """
    high_low = high - low
    high_close = (high - close.shift()).abs()
    low_close = (low - close.shift()).abs()

    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr_val = true_range.rolling(window=period, min_periods=period).mean()

    return atr_val


def adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.DataFrame:
    """
    Average Directional Index (平均趨向指標)

    Args:
        high: 最高價序列
        low: 最低價序列
        close: 收盤價序列
        period: 週期 (預設 14)

    Returns:
        pd.DataFrame: 包含 PDI, MDI, ADX
    """
    # 計算 +DM 和 -DM
    high_diff = high.diff()
    low_diff = -low.diff()

    plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
    minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)

    # 直接計算 True Range (而不是調用 atr() 函數)
    high_low = high - low
    high_close = (high - close.shift()).abs()
    low_close = (low - close.shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

    # 計算平滑後的 +DM, -DM, TR
    atr_val = tr.rolling(window=period, min_periods=period).mean()
    plus_dm_smooth = plus_dm.rolling(window=period, min_periods=period).mean()
    minus_dm_smooth = minus_dm.rolling(window=period, min_periods=period).mean()

    # 計算 +DI 和 -DI (避免除以零)
    with np.errstate(divide='ignore', invalid='ignore'):
        pdi = 100 * (plus_dm_smooth / atr_val.replace(0, np.nan))
        mdi = 100 * (minus_dm_smooth / atr_val.replace(0, np.nan))

    # 計算 DX 和 ADX (避免除以零)
    with np.errstate(divide='ignore', invalid='ignore'):
        dx = 100 * ((pdi - mdi).abs() / (pdi + mdi).replace(0, np.nan))

    adx_val = dx.rolling(window=period, min_periods=period).mean()

    return pd.DataFrame({
        'PDI': pdi,
        'MDI': mdi,
        'ADX': adx_val
    })
