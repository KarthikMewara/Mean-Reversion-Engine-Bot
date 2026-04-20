import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_all(df: pd.DataFrame, window: int, entry_z: float):
    """
    Shows Price Bands, Z-Score Oscillator, and Equity Curve in an interactive dashboard.
    """
    # Calculate the upper and lower bands for the visual overlay
    mean = df['price'].rolling(window, min_periods=1).mean()
    std = df['price'].rolling(window, min_periods=1).std(ddof=0)
    upper = mean + (entry_z * std)
    lower = mean - (entry_z * std)

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.05,
                        row_heights=[0.5, 0.25, 0.25],
                        subplot_titles=("Price & Reversion Bands", "Z-Score Oscillator", "Equity Curve"))

    # --- 1. PRICE BANDS ---
    fig.add_trace(go.Scatter(x=df.index, y=df['price'], mode='lines', name='Price', line=dict(color='#00ffe7', width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=mean, mode='lines', name='Mean (Fair Value)', line=dict(color='#ff00ff', width=1, dash='dash')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=upper, mode='lines', name=f'+{entry_z} Std (Overbought)', line=dict(color='#ff073a', width=1, dash='dot')), row=1, col=1)
    # Fill between the upper and lower bands for a clean visual channel
    fig.add_trace(go.Scatter(x=df.index, y=lower, mode='lines', name=f'-{entry_z} Std (Oversold)', line=dict(color='#39ff14', width=1, dash='dot'), fill='tonexty', fillcolor='rgba(255, 255, 255, 0.03)'), row=1, col=1)

    # --- 2. Z-SCORE OSCILLATOR ---
    fig.add_trace(go.Scatter(x=df.index, y=df['z'], mode='lines', name='Z-Score', line=dict(color='#b026ff', width=1.5)), row=2, col=1)
    fig.add_hline(y=entry_z, line_dash="dash", line_color="#ff073a", row=2, col=1)
    fig.add_hline(y=-entry_z, line_dash="dash", line_color="#39ff14", row=2, col=1)
    fig.add_hline(y=0, line_dash="dot", line_color="#ffffff", opacity=0.3, row=2, col=1)
    
    # Buy/Short markers
    buys = df[df['signal'] == 1]
    shorts = df[df['signal'] == -1]
    
    if not buys.empty:
        fig.add_trace(go.Scatter(x=buys.index, y=buys['z'], mode='markers', name='Buy Signal', marker=dict(symbol='triangle-up', color='#39ff14', size=12, line=dict(color='black', width=1))), row=2, col=1)
    if not shorts.empty:
        fig.add_trace(go.Scatter(x=shorts.index, y=shorts['z'], mode='markers', name='Short Signal', marker=dict(symbol='triangle-down', color='#ff073a', size=12, line=dict(color='black', width=1))), row=2, col=1)

    # --- 3. EQUITY CURVE ---
    fig.add_trace(go.Scatter(x=df.index, y=df['equity_curve'], mode='lines', name='Equity Multiplier', line=dict(color='#00ffe7', width=2), fill='tozeroy', fillcolor='rgba(0, 255, 231, 0.1)'), row=3, col=1)

    # --- LAYOUT & STYLING ---
    fig.update_layout(
        height=850, template="plotly_dark", plot_bgcolor='#181a20', paper_bgcolor='#181a20',
        hovermode="x", margin=dict(l=20, r=20, t=40, b=20), showlegend=True
    )
    
    # Synchronized vertical crosshair
    fig.update_xaxes(showgrid=False, showspikes=True, spikemode='across', spikesnap='cursor', spikedash='solid', spikecolor='#ffffff', spikethickness=1)
    fig.update_yaxes(showgrid=False)

    return fig