import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict

class Backtester:
    def __init__(self, data: pd.DataFrame, signals: pd.DataFrame):
        self.data = data
        self.signals = signals
        self.performance = None
        
    def run_backtest(self, initial_capital: float = 10000.0, commission: float = 0.001) -> Dict:
        """Run backtest simulation with improved numerical stability"""
        signals = self.signals.copy()
        data = self.data.copy()
        
        # shift signals to avoid look-ahead bias
        signals['signal'] = signals['signal'].shift(1)
        
        # initialize positions
        positions = pd.DataFrame(index=signals.index).fillna(0.0)
        positions['position'] = signals['signal'].cumsum()
        
        # calculate portfolio value
        portfolio = pd.DataFrame(index=positions.index)
        portfolio['holdings'] = positions['position'] * data['close']
        portfolio['cash'] = initial_capital - (positions['position'].diff() * data['close'] * (1 + commission)).cumsum()
        portfolio['total'] = portfolio['cash'] + portfolio['holdings']
        portfolio['returns'] = portfolio['total'].pct_change().fillna(0)  # fill NA with 0 returns
        
        # calculate performance metrics with safe division
        total_return = (portfolio['total'].iloc[-1] / initial_capital - 1) * 100
        annualized_return = (portfolio['total'].iloc[-1] / initial_capital) ** (252/max(len(portfolio), 1)) - 1
        
        # max drawdown calculation
        cum_max = portfolio['total'].cummax()
        drawdown = (cum_max - portfolio['total'])/cum_max
        max_drawdown = drawdown.max()
        
        # sharpe ratio with protection against zero std
        returns = portfolio['returns']
        if len(returns) > 1 and returns.std() != 0:
            sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252)
        else:
            sharpe_ratio = 0  # default when insufficient data
        
        # trade statistics
        trades = positions['position'].diff().fillna(0)
        buy_trades = trades[trades > 0]
        sell_trades = trades[trades < 0]
        
        # success rates with protection against empty trades
        buy_success = (data.loc[buy_trades.index, 'close'].shift(-5) > 
                      data.loc[buy_trades.index, 'close']).mean() if len(buy_trades) > 0 else 0
        sell_success = (data.loc[sell_trades.index, 'close'].shift(-5) < 
                       data.loc[sell_trades.index, 'close']).mean() if len(sell_trades) > 0 else 0
        
        self.performance = {
            'initial_capital': initial_capital,
            'final_value': portfolio['total'].iloc[-1],
            'total_return_pct': total_return,
            'annualized_return_pct': annualized_return * 100,
            'max_drawdown_pct': max_drawdown * 100,
            'sharpe_ratio': sharpe_ratio,
            'total_trades': len(buy_trades) + len(sell_trades),
            'buy_trades': len(buy_trades),
            'sell_trades': len(sell_trades),
            'buy_success_rate': buy_success * 100,
            'sell_success_rate': sell_success * 100,
            'portfolio': portfolio,
            'positions': positions
        }
        
        return self.performance