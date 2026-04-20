import pandas as pd
import yfinance as yf
import streamlit as st

# ttl=3600 means it will keep the data in memory for 1 hour before forcing a fresh download
@st.cache_data(ttl=3600)
def fetch_data(symbol: str, start: str, end: str, interval: str = '1d') -> pd.DataFrame:
    """
    Fetches historical price and volume data using yfinance.
    """
    print(f"Fetching {interval} data for {symbol} from {start} to {end}...")
    
    # --- THE FIX: Let yfinance handle the browser spoofing internally ---
    df = yf.download(symbol, start=start, end=end, interval=interval)
    
    if df.empty:
        raise ValueError(f"No data fetched for {symbol}. Check the ticker or dates.")
        
    # yfinance now returns MultiIndex columns. We flatten them here so pandas can do the math.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    return df[['Open', 'High', 'Low', 'Close', 'Volume']]

# --- TEST BLOCK ---
if __name__ == "__main__":
    test_symbol = 'RELIANCE.NS' 
    test_start = '2025-01-01'
    test_end = '2026-01-01'
    
    historical_data = fetch_data(test_symbol, test_start, test_end)
    print("\n--- First 5 rows of data ---")
    print(historical_data.head())