import requests
import pandas as pd
import ta
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.gridspec import GridSpec
# New imports for buttons
from matplotlib.widgets import Button  # For interactive buttons

BASE_URL = 'https://api.binance.com/api/v3'


def fetch_klines(symbol, interval='1m', limit=100, start_time=None):
    """
    Fetch historical candlestick (kline) data from the Binance API.

    Parameters:
        symbol (str): The trading pair symbol (e.g., 'BTCUSDT').
        interval (str): The interval for the klines (e.g., '1m', '5m', '1h').
        limit (int): Number of data points to retrieve (default is 100).
        start_time (datetime or None): Start time for fetching klines (optional).

    Returns:
        pd.DataFrame: A DataFrame containing the kline data with columns:
            ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    """
    BASE_URL = 'https://api.binance.com/api/v3'
    url = f'{BASE_URL}/klines'

    # Build the query parameters
    params = {
        'symbol': symbol,
        'interval': interval,
        'limit': limit
    }

    # Add the start time if provided
    if start_time:
        params['startTime'] = int(start_time.timestamp() * 1000)  # Convert datetime to milliseconds

    try:
        print(f"Fetching data for {symbol} with interval {interval}...")
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()  # Raise an exception for bad HTTP status codes

        # Parse the response JSON
        data = response.json()
        print(f"Received {len(data)} klines from Binance")

        # Create a DataFrame
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close',
            'volume', 'close_time', 'quote_volume', 'trades',
            'taker_buy_base', 'taker_buy_quote', 'ignore'
        ])

        # Convert numeric columns to appropriate types
        df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)

        # Convert timestamp to a pandas datetime and set as index
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        print(df.tail())  # Add this to verify the last rows of the fetched data
        return df
    except requests.exceptions.RequestException as req_err:
        print(f"Request error: {req_err}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def calculate_indicators(df):
    try:
        print("Calculating indicators...")
        # Calculate MACD
        macd = ta.trend.MACD(df['close'])
        df['MACD'] = macd.macd()
        df['MACD_signal'] = macd.macd_signal()
        df['MACD_hist'] = macd.macd_diff()

        # Calculate RSI
        df['RSI'] = ta.momentum.RSIIndicator(df['close']).rsi()

        # Calculate Bollinger Bands
        bollinger = ta.volatility.BollingerBands(df['close'])
        df['BBU'] = bollinger.bollinger_hband()
        df['BBL'] = bollinger.bollinger_lband()

        print("Indicators calculated successfully")
        return df
    except Exception as e:
        print(f"Error calculating indicators: {e}")
        return None


class CryptoChart:
    def __init__(self, symbols=None, interval='1m'):
        print("Initializing CryptoChart...")

        # Initialize available symbols and interval
        self.symbols = symbols if symbols else ['BTCUSDT', 'PEPEUSDT']
        self.current_symbol = self.symbols[0]  # Start with the first symbol
        self.interval = interval
        self.df = None

        # Create figure and subplots
        fig_width, fig_height = 16, 9
        self.fig = plt.figure(figsize=(fig_width, fig_height))
        self.gs = GridSpec(3, 1, height_ratios=[2, 1, 1], hspace=0.4, top=0.85, bottom=0.2)
        self.ax_candle = self.fig.add_subplot(self.gs[0])
        self.ax_macd = self.fig.add_subplot(self.gs[1])
        self.ax_rsi = self.fig.add_subplot(self.gs[2])

        # Create buttons
        self.create_buttons()

        # Set chart title
        self.fig.suptitle(f'{self.current_symbol} Live Chart', fontsize=16, y=0.95)

        # Initial plot
        self.first_update()

    def create_buttons(self):
        """Create buttons for symbol switching"""
        # Adjust button positions
        button_width = 0.1
        button_height = 0.05
        spacing = 0.05
        start_x = 0.1

        # Create a button for each symbol
        self.buttons = []
        for i, symbol in enumerate(self.symbols):
            ax_button = self.fig.add_axes([start_x + i * (button_width + spacing), 0.05, button_width, button_height])
            button = Button(ax_button, symbol)
            button.on_clicked(lambda event, sym=symbol: self.switch_symbol(sym))
            self.buttons.append(button)

    def switch_symbol(self, new_symbol):
        """Switch the chart to a new symbol"""
        print(f"Switching symbol to: {new_symbol}")
        self.current_symbol = new_symbol
        self.first_update()

    def first_update(self):
        """Initial update to ensure the chart is displayed"""
        print(f"Fetching data for {self.current_symbol}...")
        self.df = fetch_klines(symbol=self.current_symbol, interval=self.interval)
        if self.df is not None:
            self.df = calculate_indicators(self.df)
            self.plot_data(self.df)

    def plot_data(self, df):
        """Plot the data on the chart"""
        print(f"Last close price in DataFrame: {df['close'].iloc[-1]}")  # Debugging the last price

        # Clear previous plots
        self.ax_candle.clear()
        self.ax_macd.clear()
        self.ax_rsi.clear()

        # Candlestick plot
        width = (df.index[1] - df.index[0]).total_seconds() / (60 * 60 * 24) * 0.8
        up = df[df.close >= df.open]
        down = df[df.close < df.open]

        if not up.empty:
            self.ax_candle.bar(up.index, up.close - up.open, width, bottom=up.open, color='green')
            self.ax_candle.vlines(up.index, up.low, up.high, color='green', linewidth=1)
        if not down.empty:
            self.ax_candle.bar(down.index, down.close - down.open, width, bottom=down.open, color='red')
            self.ax_candle.vlines(down.index, down.low, down.high, color='red', linewidth=1)

        # Add the last price as a live annotation
        last_price = df['close'].iloc[-1]
        self.ax_candle.annotate(
            f'Last Price: {last_price:.8f}',  # Show the price with 8 decimal places
            xy=(df.index[-1], last_price),
            xytext=(df.index[-1], last_price * 1.0005),  # Slightly above the price
            arrowprops=dict(facecolor='black', arrowstyle='->'),
            fontsize=10,
            color='blue'
        )

        # Bollinger Bands
        self.ax_candle.plot(df.index, df['BBU'], 'b--', alpha=0.5, label='Upper BB')
        self.ax_candle.plot(df.index, df['BBL'], 'b--', alpha=0.5, label='Lower BB')

        # MACD and RSI plotting (no changes)
        colors = ['green' if val >= 0 else 'red' for val in df['MACD_hist']]
        self.ax_macd.bar(df.index, df['MACD_hist'], width, color=colors, alpha=0.3)
        self.ax_macd.plot(df.index, df['MACD'], label='MACD', color='blue', linewidth=1.5)
        self.ax_macd.plot(df.index, df['MACD_signal'], label='Signal', color='orange', linewidth=1.5)
        self.ax_macd.axhline(y=0, color='gray', linestyle='--', alpha=0.3)

        self.ax_rsi.plot(df.index, df['RSI'], label='RSI', color='purple')
        self.ax_rsi.axhline(y=70, color='r', linestyle='--', alpha=0.5)
        self.ax_rsi.axhline(y=30, color='g', linestyle='--', alpha=0.5)
        self.ax_rsi.set_ylim(0, 100)

        # Labels and grid
        self.ax_candle.set_ylabel('Price (USDT)')
        self.ax_macd.set_ylabel('MACD')
        self.ax_rsi.set_ylabel('RSI')

        for ax in [self.ax_candle, self.ax_macd, self.ax_rsi]:
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=10)

        # Update chart title
        self.fig.suptitle(f'{self.current_symbol} Live Chart', fontsize=16, y=0.95)

        plt.draw()

    def start_animation(self):
        """Start the animation"""
        print("Starting animation...")
        self.ani = FuncAnimation(
            self.fig,
            self.update,
            interval=1000,
            blit=False
        )
        return self.ani

    def update(self, frame):
        """Fetch and update data during the animation"""
        print(f"Updating data for {self.current_symbol}...")
        df_new = fetch_klines(symbol=self.current_symbol, interval=self.interval)
        if df_new is not None:
            self.df = calculate_indicators(df_new)
            self.plot_data(self.df)


def main():
    try:
        chart = CryptoChart(symbols=['BTCUSDT', 'PEPEUSDT'], interval='1m')
        chart.start_animation()
        plt.show()
    except Exception as e:
        print(f"Error in main: {e}")
    finally:
        plt.close('all')


if __name__ == "__main__":
    animation = main()  # Store the returned animation
