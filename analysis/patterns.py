import numpy as np
import pandas as pd
from typing import Literal

class PatternDetector:
    @staticmethod
    def detect_all_patterns(df: pd.DataFrame) -> pd.DataFrame:
        """Detect all chart patterns"""
        df = df.copy()
        
        # Head and Shoulders
        df['hs_pattern'] = PatternDetector.detect_head_shoulders(df)
        
        # Double Top/Bottom
        df['double_top'] = PatternDetector.detect_double_top_bottom(df, pattern_type='top')
        df['double_bottom'] = PatternDetector.detect_double_top_bottom(df, pattern_type='bottom')
        
        # Triangle Patterns
        df['triangle_asc'] = PatternDetector.detect_triangle_patterns(df, pattern_type='ascending')
        df['triangle_desc'] = PatternDetector.detect_triangle_patterns(df, pattern_type='descending')
        df['triangle_sym'] = PatternDetector.detect_triangle_patterns(df, pattern_type='symmetrical')
        
        # Support/Resistance
        df = PatternDetector.identify_support_resistance(df)
        
        return df
    
    @staticmethod
    def detect_head_shoulders(df: pd.DataFrame, window: int = 30) -> np.ndarray:
        """Detect head and shoulders pattern (1 for HS Top, -1 for inverse HS)"""
        patterns = np.zeros(len(df))
        high = df['high'].values
        low = df['low'].values
        
        for i in range(window, len(df)-window):
            # Left shoulder
            left_high = high[i-window:i].max()
            left_idx = i - window + np.argmax(high[i-window:i])
            
            # Head
            head_high = high[i-window:i+window].max()
            head_idx = i - window + np.argmax(high[i-window:i+window])
            
            # Right shoulder
            right_high = high[i:i+window].max()
            right_idx = i + np.argmax(high[i:i+window])
            
            # Neckline (lowest between left shoulder and head)
            neckline_low = low[left_idx:head_idx].min()
            
            # Pattern conditions
            if (left_high < head_high and right_high < head_high and 
                left_high > neckline_low and right_high > neckline_low and
                abs(left_high - right_high) < 0.02 * head_high and
                left_idx < head_idx < right_idx):
                patterns[right_idx] = -1  # Bearish pattern
                
        return patterns
    
    @staticmethod
    def detect_double_top_bottom(df: pd.DataFrame, 
                               pattern_type: Literal['top', 'bottom'], 
                               window: int = 30) -> np.ndarray:
        """Detect double top (1) or double bottom (-1) patterns"""
        patterns = np.zeros(len(df))
        high = df['high'].values
        low = df['low'].values
        
        for i in range(window, len(df)-window):
            if pattern_type == 'top':
                peak1 = high[i-window:i].max()
                peak1_idx = i - window + np.argmax(high[i-window:i])
                peak2 = high[i:i+window].max()
                peak2_idx = i + np.argmax(high[i:i+window])
                trough = low[peak1_idx:peak2_idx].min()
                
                if (abs(peak1 - peak2) < 0.02 * peak1 and 
                    trough < peak1 and 
                    (peak2_idx - peak1_idx) >= window//2):
                    patterns[peak2_idx] = -1
                    
            elif pattern_type == 'bottom':
                trough1 = low[i-window:i].min()
                trough1_idx = i - window + np.argmin(low[i-window:i])
                trough2 = low[i:i+window].min()
                trough2_idx = i + np.argmin(low[i:i+window])
                peak = high[trough1_idx:trough2_idx].max()
                
                if (abs(trough1 - trough2) < 0.02 * trough1 and 
                    peak > trough1 and 
                    (trough2_idx - trough1_idx) >= window//2):
                    patterns[trough2_idx] = 1
                    
        return patterns
    
    @staticmethod
    def detect_triangle_patterns(df: pd.DataFrame, 
                                pattern_type: Literal['ascending', 'descending', 'symmetrical'], 
                                window: int = 30) -> np.ndarray:
        """Detect triangle patterns (1 for bullish, -1 for bearish)"""
        patterns = np.zeros(len(df))
        high = df['high'].values
        low = df['low'].values
        
        for i in range(window, len(df)-window):
            highs = high[i-window:i+window]
            lows = low[i-window:i+window]
            
            if pattern_type == 'ascending':
                top = highs.max()
                bottom_slope = np.polyfit(range(len(lows)), lows, 1)[0]
                if (abs(highs[-5:].max() - highs[:5].max()) < 0.01 * top and bottom_slope > 0):
                    patterns[i+window] = 1
                    
            elif pattern_type == 'descending':
                bottom = lows.min()
                top_slope = np.polyfit(range(len(highs)), highs, 1)[0]
                if (abs(lows[-5:].min() - lows[:5].min()) < 0.01 * bottom and top_slope < 0):
                    patterns[i+window] = -1
                    
            elif pattern_type == 'symmetrical':
                high_slope = np.polyfit(range(len(highs)), highs, 1)[0]
                low_slope = np.polyfit(range(len(lows)), lows, 1)[0]
                if (high_slope < 0 and low_slope > 0 and 
                    abs(highs[-1] - lows[-1]) < 0.7 * abs(highs[0] - lows[0])):
                    patterns[i+window] = 1 if df['close'].iloc[i+window] > (highs[-1] + lows[-1])/2 else -1
                    
        return patterns
    
    @staticmethod
    def identify_support_resistance(df: pd.DataFrame, window: int = 20, threshold: float = 0.02) -> pd.DataFrame:
        """Identify support and resistance levels"""
        df = df.copy()
        
        # find pivot points
        df['pivot_high'] = df['high'].rolling(window, center=True).max()
        df['pivot_low'] = df['low'].rolling(window, center=True).min()
        
        # resistance levels
        resistance = df[df['high'] == df['pivot_high']]['high'].drop_duplicates()
        resistance = resistance[resistance.diff() > resistance * threshold]
        
        # support levels
        support = df[df['low'] == df['pivot_low']]['low'].drop_duplicates()
        support = support[support.diff() < -support * threshold]
        
        # add levels to DataFrame
        df['resistance'] = np.nan
        df['support'] = np.nan
        
        for level in resistance:
            df.loc[df['high'] == level, 'resistance'] = level
            
        for level in support:
            df.loc[df['low'] == level, 'support'] = level
            
        return df.drop(['pivot_high', 'pivot_low'], axis=1)