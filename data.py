import pandas as pd
import yfinance as yf
import streamlit as st

@st.cache_data(ttl=3600)
def fetch_data(symbol: str, start: str, end: str, interval: str = '1d') -> pd.DataFrame:
    """
    Fetches historical market data.
    """
    df = yf.download(symbol, start=start, end=end, interval=interval)
    
    if df.empty:
        raise ValueError(f"No data fetched for {symbol}.")
        
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    return df[['Open', 'High', 'Low', 'Close', 'Volume']]