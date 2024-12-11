# CryptoPrice Live Tracker

A real-time cryptocurrency price tracking application that displays live BTC/USDT price data with technical indicators in an interactive chart.

## Features

- Live BTC/USDT price tracking with candlestick chart
- Technical indicators:
  - MACD (Moving Average Convergence Divergence)
  - RSI (Relative Strength Index)
- Auto-resizing chart that adapts to your screen size
- Real-time data fetching from Binance API
- Clean and responsive visualization

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Internet connection for live data fetching

## Installation

1. Clone the repository:
   ```bash
   git clone [your-repository-url]
   cd cryotoprice
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application using:
```bash
python main.py
```

The application will open a window displaying the live BTC/USDT chart with technical indicators.

## Dependencies

- requests>=2.31.0: For API calls to Binance
- pandas>=2.1.0: For data manipulation
- numpy>=1.24.0: For numerical computations
- matplotlib>=3.8.0: For chart visualization
- ta>=0.10.0: For technical analysis indicators

## Notes

- The chart automatically adjusts to your screen size for optimal viewing
- Data is fetched in real-time from the Binance API
- Default timeframe is set to 1-minute candles
