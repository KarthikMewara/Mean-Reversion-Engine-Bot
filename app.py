import streamlit as st
import datetime
import pandas as pd
import requests
import io # --- ADD THIS NEW IMPORT ---
from data import fetch_data
from strategy import MeanReversionStrategy
from backtest import Backtest
from visualization import plot_all

st.set_page_config(layout="wide", page_title="Mean Reversion Engine")

# --- DYNAMIC ASSET DICTIONARY ---
@st.cache_data(ttl=86400)
def fetch_live_tickers():
    """Dynamically scrapes the S&P 500 and Nifty 50 constituents."""
    tickers_dict = {}
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    with st.spinner("Fetching live market indices (S&P 500 & Nifty 50)..."):
        try:
            # 1. Fetch S&P 500 (US Market)
            sp500_url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            sp500_html = requests.get(sp500_url, headers=headers).text
            sp500_tables = pd.read_html(io.StringIO(sp500_html))
            
            # Smart Search: Loop through all tables to find the right one
            for table in sp500_tables:
                if 'Symbol' in table.columns and 'Security' in table.columns:
                    us_dict = dict(zip(table['Symbol'], table['Security']))
                    tickers_dict.update(us_dict)
                    break # Stop looking once we found it
            
            # 2. Fetch Nifty 50 (Indian Market)
            nifty_url = 'https://en.wikipedia.org/wiki/NIFTY_50'
            nifty_html = requests.get(nifty_url, headers=headers).text
            nifty_tables = pd.read_html(io.StringIO(nifty_html))
            
            # Smart Search: Loop through all tables to find the right one
            for table in nifty_tables:
                if 'Symbol' in table.columns and 'Company Name' in table.columns:
                    for _, row in table.iterrows():
                        symbol = f"{row['Symbol']}.NS"
                        tickers_dict[symbol] = row['Company Name']
                    break # Stop looking once we found it
                
            return tickers_dict
            
        except Exception as e:
            st.warning(f"Failed to fetch live tickers: {e}")
            return {
                "RELIANCE.NS": "Reliance Industries",
                "TCS.NS": "Tata Consultancy Services",
                "HDFCBANK.NS": "HDFC Bank",
                "AAPL": "Apple Inc.", 
                "TSLA": "Tesla Inc.",
                "BTC-USD": "Bitcoin"
            }
# Execute the function to generate the dictionary dynamically
AVAILABLE_ASSETS = fetch_live_tickers()
AVAILABLE_ASSETS.update({
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
    "GC=F": "Gold Futures (XAU/USD)",
    "SI=F": "Silver Futures",
    "CL=F": "Crude Oil (WTI)",
    "NG=F": "Natural Gas"
})

# Create a list of formatted strings for the UI dropdown
display_options = [f"{ticker} ({name})" for ticker, name in AVAILABLE_ASSETS.items()]

# Find Apple to set as the default, or just use the first item if Apple isn't found
try:
    default_index = [i for i, opt in enumerate(display_options) if "AAPL" in opt][0]
except IndexError:
    default_index = 0

# --- UI CONTROLS (Sidebar) ---
st.sidebar.header("Strategy Parameters")

# Use the dynamic options list and default index
selected_option = st.sidebar.selectbox("Select Asset", display_options, index=default_index)
symbol = selected_option.split(" ")[0]

interval = st.sidebar.selectbox("Timeframe", ["1d", "1wk", "1h", "15m", "5m"])

st.sidebar.markdown("---")
st.sidebar.subheader("Z-Score Settings")
window = st.sidebar.slider("Rolling Window (Periods)", min_value=10, max_value=200, value=20)
entry_z = st.sidebar.slider("Entry Z-Score (Overbought/Oversold)", min_value=1.0, max_value=4.0, value=2.0, step=0.1)
exit_z = st.sidebar.slider("Exit Z-Score (Take Profit)", min_value=0.0, max_value=1.5, value=0.5, step=0.1)

# --- DYNAMIC DATE LOGIC ---
end_date = datetime.date.today()

if interval in ["1h", "15m", "5m"]:
    start_date = end_date - datetime.timedelta(days=59)
elif interval == "1wk":
    start_date = end_date - datetime.timedelta(days=365 * 3)
else:
    start_date = end_date - datetime.timedelta(days=365 * 2)

start_str = start_date.strftime('%Y-%m-%d')
end_str = end_date.strftime('%Y-%m-%d')

# --- EXECUTION ---
with st.spinner(f"Crunching {interval} data for {symbol}..."):
    df = fetch_data(symbol, start=start_str, end=end_str, interval=interval)
    
    # 1. Run the Strategy Logic
    strategy = MeanReversionStrategy(window=window, entry_z=entry_z, exit_z=exit_z)
    signals = strategy.generate_signals(df['Close'])
    
    # 2. Run the Backtest Simulator
    bt = Backtest(signals)
    results = bt.run()
    metrics = bt.performance_metrics()

# --- UI RENDERING (Main Page) ---
st.title(f"Mean Reversion: {symbol} ({interval})")

# Render the Metric Scoreboard
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Return", f"{metrics['Total Return']*100:.2f}%")
col2.metric("Win Rate", f"{metrics['Win Rate']*100:.2f}%")
col3.metric("Max Drawdown", f"{metrics['Drawdown']*100:.2f}%")
col4.metric("Total Trades", int(metrics['Trades']))

# Render the Plotly Charts
fig = plot_all(results, window=window, entry_z=entry_z)
st.plotly_chart(fig, use_container_width=True)