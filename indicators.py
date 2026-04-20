import pandas as pd
import numpy as np

def rolling_mean(series: pd.Series, window: int) -> pd.Series:
    """Calculates the simple moving average."""
    return series.rolling(window=window, min_periods=1).mean()

def rolling_std(series: pd.Series, window: int) -> pd.Series:
    """Calculates the rolling standard deviation."""
    return series.rolling(window=window, min_periods=1).std(ddof=0)

def zscore(series: pd.Series, window: int) -> pd.Series:
    """
    Calculates the Z-Score.
    Z = (Current Price - Mean) / Standard Deviation
    """
    mean = rolling_mean(series, window)
    std = rolling_std(series, window)
    
    # Avoid division by zero if standard deviation is 0
    return (series - mean) / std.replace(0, np.nan)