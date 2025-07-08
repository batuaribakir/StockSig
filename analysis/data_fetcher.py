import yfinance as yf
import pandas as pd
from typing import Dict, Optional

class DataFetcher:
    def __init__(self, ticker: str, period: str = '1y'):
        self.ticker = ticker
        self.period = period
        self.raw_data = None
        
    def fetch(self) -> pd.DataFrame:
        """Fetch stock data from Yahoo Finance"""
        try:
            self.raw_data = yf.download(
                self.ticker,
                period=self.period,
                auto_adjust=True,
                progress=False,
                threads=True
            )
            
            if self.raw_data.empty:
                raise ValueError("No data received - empty DataFrame")
                
            # standardize columns and clean data
            self.raw_data = self.raw_data[['Open', 'High', 'Low', 'Close', 'Volume']]
            self.raw_data.columns = ['open', 'high', 'low', 'close', 'volume']
            self.raw_data = self.raw_data.dropna()
            
            if not isinstance(self.raw_data.index, pd.DatetimeIndex):
                self.raw_data.index = pd.to_datetime(self.raw_data.index)
                
            return self.raw_data
            
        except Exception as e:
            raise Exception(f"Data fetching error: {str(e)}")
    
    def get_stock_info(self) -> Dict:
        """Get fundamental information about the stock"""
        try:
            stock = yf.Ticker(self.ticker)
            info = stock.info
            
            return {
                'company': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'country': info.get('country', 'N/A'),
                'market_cap': info.get('marketCap'),
                'current_price': info.get('currentPrice', info.get('regularMarketPrice')),
                'fifty_two_week_range': f"{info.get('fiftyTwoWeekLow', 'N/A')} - {info.get('fiftyTwoWeekHigh', 'N/A')}",
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'dividend_yield': info.get('dividendYield', 'N/A')
            }
        except Exception as e:
            raise Exception(f"Failed to get stock info: {str(e)}")