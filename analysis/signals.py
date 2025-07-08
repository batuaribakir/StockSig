import pandas as pd
from typing import Dict

class SignalGenerator:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.signals = None
        
    def generate_signals(self) -> pd.DataFrame:
        """Generate trading signals based on technical indicators"""
        signals = pd.DataFrame(index=self.data.index)
        signals['signal'] = 0  # Default: Hold
        
        # 1. Moving Average Signals
        signals['ma_signal'] = 0
        signals.loc[(self.data['ema_12'] > self.data['ema_26']) & 
                  (self.data['sma_20'] > self.data['sma_50']), 'ma_signal'] = 1
        signals.loc[(self.data['ema_12'] < self.data['ema_26']) & 
                  (self.data['sma_20'] < self.data['sma_50']), 'ma_signal'] = -1
        
        # 2. MACD Signals
        signals['macd_signal'] = 0
        signals.loc[self.data['macd'] > self.data['macd_signal'], 'macd_signal'] = 1
        signals.loc[self.data['macd'] < self.data['macd_signal'], 'macd_signal'] = -1
        
        # 3. RSI Signals
        signals['rsi_signal'] = 0
        signals.loc[self.data['rsi_14'] < 30, 'rsi_signal'] = 1  # Oversold
        signals.loc[self.data['rsi_14'] > 70, 'rsi_signal'] = -1  # Overbought
        
        # 4. Bollinger Bands Signals
        signals['bb_signal'] = 0
        signals.loc[self.data['close'] < self.data['bb_lower'], 'bb_signal'] = 1
        signals.loc[self.data['close'] > self.data['bb_upper'], 'bb_signal'] = -1
        
        # 5. Pattern Signals
        signals['pattern_signal'] = 0
        bullish_patterns = ['double_bottom', 'triangle_asc', 'triangle_sym']
        bearish_patterns = ['double_top', 'hs_pattern', 'triangle_desc']
        
        for pattern in bullish_patterns:
            if pattern in self.data.columns:
                signals.loc[self.data[pattern] == 1, 'pattern_signal'] += 1
                
        for pattern in bearish_patterns:
            if pattern in self.data.columns:
                signals.loc[self.data[pattern] == -1, 'pattern_signal'] -= 1
        
        # 6. Support/Resistance Signals
        signals['sr_signal'] = 0
        signals.loc[self.data['close'] <= self.data['support'], 'sr_signal'] = 1
        signals.loc[self.data['close'] >= self.data['resistance'], 'sr_signal'] = -1
        
        # Composite Score
        signal_weights = {
            'ma_signal': 2.0,
            'macd_signal': 1.5,
            'rsi_signal': 1.0,
            'bb_signal': 1.0,
            'pattern_signal': 2.0,
            'sr_signal': 1.5
        }
        
        weighted_signals = signals[list(signal_weights.keys())].mul(list(signal_weights.values()))
        signals['composite_score'] = weighted_signals.sum(axis=1)
        
        # Generate final signals
        signals['signal'] = 0
        signals.loc[signals['composite_score'] >= 3, 'signal'] = 1  # Strong buy
        signals.loc[signals['composite_score'] <= -3, 'signal'] = -1  # Strong sell
        
        self.signals = signals
        return signals
        
    def explain_signal(self, date: str = None) -> Dict:
        """Explain the signal for a specific date"""
        if self.signals is None:
            self.generate_signals()
            
        if date is None:
            date = self.signals.index[-1].strftime('%Y-%m-%d')
            
        signal_date = pd.to_datetime(date)
        if signal_date not in self.signals.index:
            raise ValueError(f"No data available for {date}")
            
        signal_row = self.signals.loc[signal_date]
        explanation = {
            'date': date,
            'final_signal': 'Buy' if signal_row['signal'] == 1 else 'Sell' if signal_row['signal'] == -1 else 'Hold',
            'composite_score': round(signal_row['composite_score'], 2),
            'indicators': {
                'moving_averages': self._get_ma_status(signal_row),
                'macd': self._get_macd_status(signal_row),
                'rsi': self._get_rsi_status(signal_row),
                'bollinger_bands': self._get_bb_status(signal_row),
                'chart_patterns': self._get_pattern_status(signal_row),
                'support_resistance': self._get_sr_status(signal_row)
            }
        }
        return explanation
        
    def _get_ma_status(self, signal_row) -> Dict:
        """Get moving average status"""
        status = []
        if signal_row['ma_signal'] == 1:
            status.append("Bullish crossover (EMA12 > EMA26 and SMA20 > SMA50)")
        elif signal_row['ma_signal'] == -1:
            status.append("Bearish crossover (EMA12 < EMA26 and SMA20 < SMA50)")
        else:
            status.append("No clear MA crossover")
        return {'value': signal_row['ma_signal'], 'status': status}
    
    def _get_macd_status(self, signal_row) -> Dict:
        """Get MACD indicator status"""
        status = []
        if signal_row['macd_signal'] == 1:
            status.append("Bullish crossover (MACD > Signal Line)")
        elif signal_row['macd_signal'] == -1:
            status.append("Bearish crossover (MACD < Signal Line)")
        else:
            status.append("No MACD crossover")
        
        # Add histogram status
        if 'macd_hist' in self.data.columns:
            hist_value = self.data.loc[signal_row.name, 'macd_hist']
            if hist_value > 0:
                status.append("MACD histogram above zero (bullish momentum)")
            else:
                status.append("MACD histogram below zero (bearish momentum)")
                
        return {'value': signal_row['macd_signal'], 'status': status}

    def _get_rsi_status(self, signal_row) -> Dict:
        """Get RSI indicator status"""
        status = []
        rsi_value = self.data.loc[signal_row.name, 'rsi_14']
        
        if signal_row['rsi_signal'] == 1:
            status.append(f"Oversold (RSI: {rsi_value:.1f} < 30)")
        elif signal_row['rsi_signal'] == -1:
            status.append(f"Overbought (RSI: {rsi_value:.1f} > 70)")
        else:
            status.append(f"Neutral (RSI: {rsi_value:.1f})")
            
        return {'value': signal_row['rsi_signal'], 'status': status}

    def _get_bb_status(self, signal_row) -> Dict:
        """Get Bollinger Bands status"""
        status = []
        close = self.data.loc[signal_row.name, 'close']
        bb_upper = self.data.loc[signal_row.name, 'bb_upper']
        bb_lower = self.data.loc[signal_row.name, 'bb_lower']
        
        if signal_row['bb_signal'] == 1:
            status.append(f"Price below lower band ({close:.2f} < {bb_lower:.2f})")
        elif signal_row['bb_signal'] == -1:
            status.append(f"Price above upper band ({close:.2f} > {bb_upper:.2f})")
        else:
            status.append(f"Price within bands ({bb_lower:.2f} < {close:.2f} < {bb_upper:.2f})")
            
        # Add bandwidth info
        bandwidth = (bb_upper - bb_lower) / self.data.loc[signal_row.name, 'bb_middle']
        if bandwidth > 0.1:
            status.append("High volatility (wide bands)")
        else:
            status.append("Low volatility (narrow bands)")
            
        return {'value': signal_row['bb_signal'], 'status': status}

    def _get_pattern_status(self, signal_row) -> Dict:
        """Get chart pattern status"""
        status = []
        patterns = {
            'hs_pattern': 'Head and Shoulders',
            'double_top': 'Double Top',
            'double_bottom': 'Double Bottom',
            'triangle_asc': 'Ascending Triangle',
            'triangle_desc': 'Descending Triangle',
            'triangle_sym': 'Symmetrical Triangle'
        }
        
        active_patterns = []
        for pattern, name in patterns.items():
            if pattern in self.data.columns and abs(self.data.loc[signal_row.name, pattern]) == 1:
                direction = "bearish" if self.data.loc[signal_row.name, pattern] == -1 else "bullish"
                active_patterns.append(f"{direction} {name}")
                
        if active_patterns:
            status.extend(active_patterns)
        else:
            status.append("No significant patterns detected")
            
        return {'value': signal_row['pattern_signal'], 'status': status}

    def _get_sr_status(self, signal_row) -> Dict:
        """Get support/resistance status"""
        status = []
        close = self.data.loc[signal_row.name, 'close']
        support = self.data.loc[signal_row.name, 'support']
        resistance = self.data.loc[signal_row.name, 'resistance']
        
        if signal_row['sr_signal'] == 1:
            status.append(f"Near support level ({close:.2f} ≈ {support:.2f})")
        elif signal_row['sr_signal'] == -1:
            status.append(f"Near resistance level ({close:.2f} ≈ {resistance:.2f})")
        else:
            status.append("Between significant support/resistance levels")
            
        return {'value': signal_row['sr_signal'], 'status': status}