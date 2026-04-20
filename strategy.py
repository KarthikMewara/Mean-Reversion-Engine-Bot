import pandas as pd
import numpy as np
from indicators import zscore

class MeanReversionStrategy:
    def __init__(self, window=20, entry_z=2.0, exit_z=0.5):
        self.window = window
        self.entry_z = entry_z
        self.exit_z = exit_z

    def generate_signals(self, prices: pd.Series) -> pd.DataFrame:
        df = pd.DataFrame({'price': prices})
        
        # 1. Calculate the Z-Score
        df['z'] = zscore(df['price'], self.window)
        df['signal'] = 0
        
        # 2. Entry Logic: Rubber band is stretched too far
        df.loc[df['z'] < -self.entry_z, 'signal'] = 1   # Price is too low -> BUY
        df.loc[df['z'] > self.entry_z, 'signal'] = -1   # Price is too high -> SELL (Short)
        
        # Forward fill the signals so we hold the position until an exit triggers
        df['signal'] = df['signal'].replace(0, np.nan).ffill().fillna(0)
        
        # 3. Exit Logic: Rubber band snaps back to the mean
        df.loc[df['z'].abs() < self.exit_z, 'signal'] = 0
        
        # Forward fill again to maintain the neutral (0) state after exiting
        df['signal'] = df['signal'].replace(0, np.nan).ffill().fillna(0)
        
        return df

# --- TEST BLOCK ---
if __name__ == "__main__":
    from data import fetch_data
    
    print("Fetching test data for AAPL...")
    # Get some real data to test our logic
    df = fetch_data('AAPL', start='2023-01-01', end='2024-01-01', interval='1d')
    
    print("Running Mean Reversion Strategy...")
    strategy = MeanReversionStrategy(window=20, entry_z=2.0, exit_z=0.5)
    
    # We only feed the 'Close' prices into the strategy
    signals = strategy.generate_signals(df['Close'])
    
    # Let's see how many times it triggered a trade
    total_buys = (signals['signal'] == 1).sum()
    total_sells = (signals['signal'] == -1).sum()
    
    print(f"\nTotal Buy Days: {total_buys}")
    print(f"Total Short Sell Days: {total_sells}")
    print("\nFirst 5 rows of calculated signals:")
    print(signals.head())