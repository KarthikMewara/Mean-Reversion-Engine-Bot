import pandas as pd

class Backtest:
    def __init__(self, signals: pd.DataFrame):
        self.signals = signals.copy()
        self.results = None

    def run(self):
        df = self.signals.copy()
        
        # Shift position by 1 day to prevent lookahead bias (you trade AT the close)
        df['position'] = df['signal'].shift(1).fillna(0)
        
        # Calculate daily percentage returns of the underlying asset
        df['returns'] = df['price'].pct_change().fillna(0)
        
        # If we are long (1), we get the returns. If short (-1), we get the inverse returns.
        df['strategy_returns'] = df['position'] * df['returns']
        
        # Compounding the returns starting from an initial value of 1.0 (100%)
        df['equity_curve'] = (1 + df['strategy_returns']).cumprod()
        self.results = df
        
        return df

    def performance_metrics(self):
        df = self.results if self.results is not None else self.run()
        
        total_return = df['equity_curve'].iloc[-1] - 1
        
        # Count how many times the position changed (divided by 2 for round trips)
        trades = df['signal'].diff().abs().sum() / 2
        
        # Count winning days while in a trade
        wins = ((df['strategy_returns'] > 0) & (df['position'] != 0)).sum()
        win_rate = wins / trades if trades > 0 else 0
        
        # Max Drawdown calculation
        drawdown = (df['equity_curve'] / df['equity_curve'].cummax() - 1).min()
        
        return {
            'Total Return': total_return,
            'Win Rate': win_rate,
            'Drawdown': drawdown,
            'Trades': trades
        }