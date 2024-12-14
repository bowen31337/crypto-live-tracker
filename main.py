import requests
import pandas as pd
import ta
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.gridspec import GridSpec

BASE_URL = 'https://api.binance.com/api/v3'

def fetch_klines(symbol='BTCUSDT', interval='1m', limit=100):
    url = f'{BASE_URL}/klines'
    params = {
        'symbol': symbol,
        'interval': interval,
        'limit': limit
    }
    
    try:
        print("Fetching data from Binance...")
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"Received {len(data)} klines from Binance")
        
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 
                                       'volume', 'close_time', 'quote_volume', 'trades',
                                       'taker_buy_base', 'taker_buy_quote', 'ignore'])
        
        # Convert numeric columns
        df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        print("Sample of data:")
        print(df.head())
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
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
    def __init__(self):
        print("Initializing CryptoChart...")
        
        # Get screen size
        try:
            manager = plt.get_current_fig_manager()
            if hasattr(manager, 'window'):
                # Get screen width and height
                screen_width = manager.window.winfo_screenwidth()
                screen_height = manager.window.winfo_screenheight()
                
                # Calculate figure size based on screen size (80% of screen)
                fig_width = screen_width * 0.8 / 100  # Convert pixels to inches
                fig_height = screen_height * 0.8 / 100
                
                print(f"Screen size detected: {screen_width}x{screen_height}")
                print(f"Figure size set to: {fig_width:.1f}x{fig_height:.1f} inches")
            else:
                # Default size if can't detect screen
                fig_width, fig_height = 20, 12
        except Exception as e:
            print(f"Could not detect screen size: {e}")
            fig_width, fig_height = 20, 12
        
        # Create figure with adaptive size
        self.fig = plt.figure(figsize=(fig_width, fig_height))
        
        # Calculate font sizes based on figure width
        self.title_size = max(16, int(fig_width * 0.8))
        self.label_size = max(12, int(fig_width * 0.6))
        self.tick_size = max(10, int(fig_width * 0.5))
        self.legend_size = max(10, int(fig_width * 0.5))
        
        # Store animation object
        self.ani = None
        
        # Adjust GridSpec with proper spacing
        self.gs = GridSpec(3, 1, 
                         height_ratios=[2, 1, 1], 
                         hspace=0.4,
                         top=0.95,
                         bottom=0.05,
                         left=0.05,
                         right=0.95,
                         figure=self.fig)
        
        # Create subplots
        self.ax_candle = self.fig.add_subplot(self.gs[0])
        self.ax_macd = self.fig.add_subplot(self.gs[1])
        self.ax_rsi = self.fig.add_subplot(self.gs[2])
        
        # Set title with adaptive font size
        self.fig.suptitle('BTC/USDT Live Chart', 
                         fontsize=self.title_size,
                         y=0.98)
        
        # Try to maximize window
        try:
            manager = plt.get_current_fig_manager()
            if hasattr(manager, 'window'):
                # For TkAgg backend
                manager.resize(*manager.window.maxsize())
            elif hasattr(manager, 'full_screen_toggle'):
                # For Qt backend
                manager.full_screen_toggle()
            elif hasattr(manager, 'frame'):
                # For WX backend
                manager.frame.Maximize(True)
        except Exception as e:
            print(f"Could not maximize window: {e}")
        
        # Connect the close event
        self.fig.canvas.mpl_connect('close_event', self._on_close)
        
        print("Chart initialized")
        self.first_update()
    
    def _on_close(self, event):
        """Handle figure close event"""
        print("Closing chart...")
        if self.ani is not None:
            self.ani.event_source.stop()
        plt.close('all')
    
    def first_update(self):
        """Initial update to ensure data is displayed"""
        print("Performing initial update...")
        df = fetch_klines()
        if df is not None:
            df = calculate_indicators(df)
            if df is not None:
                self.plot_data(df)
                print("Initial plot completed")
    
    def update(self, frame):
        """Update the chart with new data"""
        print(f"Update frame {frame}")
        try:
            df = fetch_klines()
            if df is not None:
                df = calculate_indicators(df)
                if df is not None:
                    self.plot_data(df)
        except Exception as e:
            print(f"Error in update: {e}")
    
    def plot_data(self, df):
        print("Plotting data...")
        # Clear all axes
        self.ax_candle.clear()
        self.ax_macd.clear()
        self.ax_rsi.clear()
        
        # Plot candlesticks
        width = 0.0008
        up = df[df.close >= df.open]
        down = df[df.close < df.open]
        
        # Plot up candlesticks
        if not up.empty:
            self.ax_candle.bar(up.index, up.close-up.open, width, bottom=up.open, color='green')
            self.ax_candle.vlines(up.index, up.low, up.high, color='green', linewidth=1)
        
        # Plot down candlesticks
        if not down.empty:
            self.ax_candle.bar(down.index, down.close-down.open, width, bottom=down.open, color='red')
            self.ax_candle.vlines(down.index, down.low, down.high, color='red', linewidth=1)
        
        # Plot Bollinger Bands
        self.ax_candle.plot(df.index, df['BBU'], 'b--', alpha=0.5, label='Upper BB')
        self.ax_candle.plot(df.index, df['BBL'], 'b--', alpha=0.5, label='Lower BB')
        
        # MACD Plot
        colors = ['green' if val >= 0 else 'red' for val in df['MACD_hist']]
        self.ax_macd.bar(df.index, df['MACD_hist'], width, color=colors, alpha=0.3, label='Histogram')
        self.ax_macd.plot(df.index, df['MACD'], label='MACD', color='blue', linewidth=1.5)
        self.ax_macd.plot(df.index, df['MACD_signal'], label='Signal', color='orange', linewidth=1.5)
        self.ax_macd.axhline(y=0, color='gray', linestyle='--', alpha=0.3)
        
        # RSI
        self.ax_rsi.plot(df.index, df['RSI'], label='RSI', color='purple')
        self.ax_rsi.axhline(y=70, color='r', linestyle='--', alpha=0.5)
        self.ax_rsi.axhline(y=30, color='g', linestyle='--', alpha=0.5)
        self.ax_rsi.set_ylim(0, 100)
        
        # Set labels and grid with adaptive font sizes
        for ax in [self.ax_candle, self.ax_macd, self.ax_rsi]:
            ax.tick_params(axis='both', labelsize=self.tick_size)
            ax.yaxis.label.set_size(self.label_size)
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=self.legend_size)
        
        # Set specific labels
        self.ax_candle.set_ylabel('Price (USDT)')
        self.ax_macd.set_ylabel('MACD')
        self.ax_rsi.set_ylabel('RSI')
        
        # Align labels and adjust layout
        self.fig.align_labels()
    
    def start_animation(self):
        """Start the animation"""
        print("Starting animation...")
        try:
            self.ani = FuncAnimation(
                self.fig,
                self.update,
                interval=1000,
                blit=False
            )
            print("Animation started")
            return self.ani
        except Exception as e:
            print(f"Error starting animation: {e}")
            return None

def main():
    try:
        print("Starting application...")
        chart = CryptoChart()
        # Create the animation and store it in a local variable
        anim = chart.start_animation()
        print("Starting plot display...")
        plt.show()
        return anim  # Return animation to prevent garbage collection
    except Exception as e:
        print(f"Error in main: {e}")
    finally:
        plt.close('all')

if __name__ == "__main__":
    animation = main()  # Store the returned animation
