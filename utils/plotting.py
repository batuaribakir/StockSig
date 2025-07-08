import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib import gridspec
import mplfinance as mpf

def set_plot_style():
    """Set a clean plotting style"""
    plt.style.use('default')
    plt.rcParams.update({
        'figure.facecolor': 'white',
        'axes.grid': True,
        'grid.linestyle': '--',
        'grid.alpha': 0.3,
        'axes.edgecolor': '0.8',
        'axes.linewidth': 0.5,
        'font.size': 10
    })

def plot_technical_analysis(data: pd.DataFrame, signals: pd.DataFrame, 
                          ticker: str, period: str = '1y', 
                          figsize: tuple = (16, 12)):
    """Plot comprehensive technical analysis with indicators and signals"""
    set_plot_style()
    fig = plt.figure(figsize=figsize)
    gs = gridspec.GridSpec(4, 1, height_ratios=[3, 1, 1, 1])
    
    # 1. Price and Indicators
    ax1 = plt.subplot(gs[0])
    ax1.set_title(f'{ticker} Technical Analysis ({period})', fontsize=14, pad=20)
    
    # Price and Moving Averages
    ax1.plot(data['close'], label='Price', color='#1f77b4', linewidth=2)
    ax1.plot(data['sma_20'], label='20 SMA', color='orange', linestyle='--', alpha=0.7)
    ax1.plot(data['sma_50'], label='50 SMA', color='green', linestyle='--', alpha=0.7)
    
    # Bollinger Bands
    ax1.fill_between(data.index, data['bb_upper'], data['bb_lower'], 
                    color='gray', alpha=0.2, label='Bollinger Bands')
    
    # Signals
    buy_signals = signals[signals['signal'] == 1]
    sell_signals = signals[signals['signal'] == -1]
    
    ax1.scatter(buy_signals.index, data.loc[buy_signals.index, 'close'], 
               color='green', marker='^', s=100, label='Buy Signal')
    ax1.scatter(sell_signals.index, data.loc[sell_signals.index, 'close'], 
               color='red', marker='v', s=100, label='Sell Signal')
    
    ax1.set_ylabel('Price', fontsize=12)
    ax1.legend(loc='upper left')
    
    # 2. Volume
    ax2 = plt.subplot(gs[1], sharex=ax1)
    ax2.bar(data.index, data['volume'], color='#17becf', alpha=0.3, label='Volume')
    ax2.plot(data['volume'].rolling(20).mean(), color='blue', label='20-day Avg')
    ax2.set_ylabel('Volume', fontsize=12)
    ax2.legend(loc='upper left')
    
    # 3. RSI
    ax3 = plt.subplot(gs[2], sharex=ax1)
    ax3.plot(data['rsi_14'], color='purple', label='RSI (14)')
    ax3.axhline(70, color='red', linestyle='--', alpha=0.3)
    ax3.axhline(30, color='green', linestyle='--', alpha=0.3)
    ax3.fill_between(data.index, 70, 30, color='yellow', alpha=0.1)
    ax3.set_ylim(0, 100)
    ax3.set_ylabel('RSI', fontsize=12)
    ax3.legend(loc='upper left')
    
    # 4. MACD
    ax4 = plt.subplot(gs[3], sharex=ax1)
    ax4.plot(data['macd'], color='blue', label='MACD')
    ax4.plot(data['macd_signal'], color='orange', label='Signal')
    ax4.bar(data.index, data['macd_hist'], 
           color=np.where(data['macd_hist'] > 0, 'g', 'r'), alpha=0.3, label='Histogram')
    ax4.axhline(0, color='gray', linestyle='--', alpha=0.5)
    ax4.set_ylabel('MACD', fontsize=12)
    ax4.legend(loc='upper left')
    
    plt.tight_layout()
    return fig

def plot_candlestick(data: pd.DataFrame, ticker: str, period: str = '1y', 
                    figsize: tuple = (12, 6), pattern_annotations: bool = True):
    """Plot candlestick chart with detected patterns"""
    # prepare DataFrame for mplfinance
    plot_data = data[['open', 'high', 'low', 'close', 'volume']].copy()
    plot_data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    
    # initialize add_plots as empty list
    add_plots = []
    
    if pattern_annotations:
        patterns = {
            'hs_pattern': ('v', 'red', 'Head & Shoulders'),
            'double_top': ('v', 'darkred', 'Double Top'),
            'double_bottom': ('^', 'darkgreen', 'Double Bottom')
        }
        
        for pattern, (marker, color, label) in patterns.items():
            if pattern in data.columns:
                pattern_dates = data[data[pattern] != 0].index
                if not pattern_dates.empty:
                    add_plots.append(
                        mpf.make_addplot(data.loc[pattern_dates, 'high'],
                                       type='scatter', 
                                       marker=marker,
                                       color=color, 
                                       markersize=100,
                                       label=label)
                    )
    
    # create plot style
    style = mpf.make_mpf_style(
        base_mpf_style='default',
        marketcolors=mpf.make_marketcolors(
            up='g',
            down='r',
            edge='inherit',
            wick='inherit',
            volume='in'
        )
    )
    
    # handle empty add_plots
    plot_kwargs = {
        'type': 'candle',
        'style': style,
        'title': f'{ticker} Candlestick Chart ({period})',
        'ylabel': 'Price',
        'volume': True,
        'figsize': figsize,
        'returnfig': True
    }
    
    if add_plots:  # only add if we have plots to show
        plot_kwargs['addplot'] = add_plots
    
    fig, axes = mpf.plot(plot_data, **plot_kwargs)
    
    if add_plots:
        axes[0].legend(loc='upper left')
    
    return fig