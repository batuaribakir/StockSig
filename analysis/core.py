import pandas as pd
from typing import Optional
from analysis.data_fetcher import DataFetcher
from analysis.indicators import IndicatorCalculator
from analysis.patterns import PatternDetector
from analysis.signals import SignalGenerator
from analysis.backtest import Backtester
from utils.plotting import plot_technical_analysis, plot_candlestick

class TechnicalAnalysis:
    def __init__(self, ticker: str, period: str = '1y'):
        self.ticker = ticker
        self.period = period
        self.raw_data = None
        self.processed_data = None
        self.signals = None
        self.performance = None

    def fetch_data(self) -> pd.DataFrame:
        """Fetch raw stock data"""
        fetcher = DataFetcher(self.ticker, self.period)
        self.raw_data = fetcher.fetch()
        return self.raw_data

    def add_technical_indicators(self) -> pd.DataFrame:
        """Calculate all technical indicators"""
        if self.raw_data is None:
            self.fetch_data()
            
        self.processed_data = IndicatorCalculator.calculate_all_indicators(self.raw_data)
        return self.processed_data

    def detect_chart_patterns(self) -> pd.DataFrame:
        """Detect all chart patterns"""
        if self.processed_data is None:
            self.add_technical_indicators()
            
        self.processed_data = PatternDetector.detect_all_patterns(self.processed_data)
        return self.processed_data

    def generate_signals(self) -> pd.DataFrame:
        """Generate trading signals"""
        if self.processed_data is None:
            self.detect_chart_patterns()
            
        signal_gen = SignalGenerator(self.processed_data)
        self.signals = signal_gen.generate_signals()
        return self.signals

    def backtest(self, initial_capital: float = 10000.0) -> dict:
        """Run backtesting simulation"""
        if self.signals is None:
            self.generate_signals()
            
        backtester = Backtester(self.processed_data, self.signals)
        self.performance = backtester.run_backtest(initial_capital)
        return self.performance

    def plot_analysis(self, chart_type: str = 'technical', **kwargs):
        """Visualize analysis results with error handling"""
        try:
            if self.processed_data is None:
                raise ValueError("No data available. Run analysis first.")
                
            if chart_type == 'technical':
                if self.signals is None:
                    self.generate_signals()
                fig = plot_technical_analysis(
                    data=self.processed_data,
                    signals=self.signals,
                    ticker=self.ticker,
                    period=self.period,
                    **kwargs
                )
            elif chart_type == 'candlestick':
                fig = plot_candlestick(
                    data=self.processed_data,
                    ticker=self.ticker,
                    period=self.period,
                    **kwargs
                )
            else:
                raise ValueError("chart_type must be 'technical' or 'candlestick'")
                
            return fig
        except Exception as e:
            print(f"❌ Plotting error: {str(e)}")
            return None

    def run_full_analysis(self):
        """Run complete analysis pipeline and return summary"""
        self.fetch_data()
        self.add_technical_indicators() 
        self.detect_chart_patterns()
        self.generate_signals()
        self.backtest()
        
        # create summary dictionary
        summary = {
            'indicators': self.processed_data[['close', 'sma_20', 'rsi_14', 'bb_upper', 'bb_middle', 'bb_lower']].tail(),
            'performance': {
                'initial_capital': self.performance['initial_capital'],
                'final_value': self.performance['final_value'],
                'return_pct': self.performance['total_return_pct'],
                'max_drawdown': self.performance['max_drawdown_pct']
            },
            'signal': self.signals.iloc[-1]['signal'],
            'signal_score': self.signals.iloc[-1]['composite_score']
        }
        
        return self, summary