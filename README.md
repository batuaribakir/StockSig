# Stock Analysis AI 📈🤖

A comprehensive technical analysis tool that automates market analysis using AI-driven indicators and pattern recognition.

## Features ✨

- **Data Pipeline**
  - Real-time Yahoo Finance integration
  - Customizable timeframes (1d to max)
  - Automated data cleaning

- **Technical Indicators**
  - Moving Averages (SMA, EMA)
  - Oscillators (RSI, MACD)
  - Volatility (Bollinger Bands)
  - Volume analysis

- **Pattern Recognition**
  - Head & Shoulders
  - Double Tops/Bottoms 
  - Triangle Patterns
  - Support/Resistance Levels

- **Smart Signals**
  - Weighted composite scoring
  - Trend confirmation
  - Volume validation

- **Backtesting**
  - Portfolio simulation
  - Sharpe ratio calculation
  - Win rate analysis

## Installation ⚙️

```bash
git clone https://github.com/batuaribakir/StockSig.git
cd StockSig
pip install -r requirements.txt
```
## Usage 🖥️
**CLI Interface**

python -m interface.cli

**Jupyter Interface**

from interface.widgets import InteractiveAnalysis
analyzer = InteractiveAnalysis()
analyzer.display()

## Tech Stack 🛠️

**Core:** Python 3.9+

**Data:** yFinance, Pandas, NumPy

**TA:** TA-Lib, custom pattern detection

**Visualization:** Matplotlib, mplfinance

**UI:** IPython Widgets, Click
