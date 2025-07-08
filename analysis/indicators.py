import numpy as np
import pandas as pd
from typing import Tuple

class IndicatorCalculator:
    @staticmethod
    def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators"""
        df = IndicatorCalculator.add_moving_averages(df)
        df = IndicatorCalculator.add_rsi(df)
        df = IndicatorCalculator.add_bollinger_bands(df)
        df = IndicatorCalculator.add_macd(df)
        return df
        
    @staticmethod
    def add_moving_averages(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate various moving averages"""
        close = df['close'].astype('float64')
        df['sma_20'] = close.rolling(window=20, min_periods=1).mean()
        df['sma_50'] = close.rolling(window=50, min_periods=1).mean()
        df['ema_12'] = close.ewm(span=12, adjust=False).mean()
        df['ema_26'] = close.ewm(span=26, adjust=False).mean()
        return df
        
    @staticmethod
    def add_rsi(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
        """Calculate Relative Strength Index"""
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=window, min_periods=1).mean()
        avg_loss = loss.rolling(window=window, min_periods=1).mean()
        rs = avg_gain / (avg_loss + 1e-10)  # Avoid division by zero
        df[f'rsi_{window}'] = 100 - (100 / (1 + rs))
        return df
        
    @staticmethod
    def add_bollinger_bands(df: pd.DataFrame, window: int = 20, std_dev: int = 2) -> pd.DataFrame:
        """Calculate Bollinger Bands"""
        df['bb_middle'] = df['close'].rolling(window=window, min_periods=1).mean()
        std = df['close'].rolling(window=window, min_periods=1).std()
        df['bb_upper'] = df['bb_middle'] + (std * std_dev)
        df['bb_lower'] = df['bb_middle'] - (std * std_dev)
        return df
        
    @staticmethod
    def add_macd(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate MACD indicator"""
        if 'ema_12' not in df or 'ema_26' not in df:
            df = IndicatorCalculator.add_moving_averages(df)
            
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        return df
        
    @staticmethod
    def add_fibonacci_levels(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """Add Fibonacci retracement levels"""
        df = df.copy()
        df['rolling_high'] = df['high'].rolling(window).max()
        df['rolling_low'] = df['low'].rolling(window).min()
        
        diff = df['rolling_high'] - df['rolling_low']
        
        df['fib_0'] = df['rolling_high']
        df['fib_0.236'] = df['rolling_high'] - 0.236 * diff
        df['fib_0.382'] = df['rolling_high'] - 0.382 * diff
        df['fib_0.5'] = df['rolling_high'] - 0.5 * diff
        df['fib_0.618'] = df['rolling_high'] - 0.618 * diff
        df['fib_1'] = df['rolling_low']
        
        return df.drop(['rolling_high', 'rolling_low'], axis=1)