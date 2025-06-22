import yfinance as yf
from typing import List,Optional
import ta

# stock price history (1 year)
def get_historical_prices(ticker_symbol: str, period: str = "1y") -> dict:
    """
    Retrieves historical stock price data for a given ticker symbol.
    Args:
        ticker_symbol (str): The stock ticker symbol (e.g., 'AAPL' for Apple Inc.).
        period (str, optional): The period for which to retrieve data (e.g., '1y' for 1 year). Defaults to '1y'.
    Returns:
        dict: A dictionary containing historical price data.
    """
    hist = yf.Ticker(ticker_symbol).history(period=period)
    return hist.reset_index().to_dict(orient="records")

def calculate_technical_indicators(ticker_symbol: str, indicators: Optional[List[str]] = None) -> dict:
    """
    Calculates technical indicators for a given ticker symbol.
    Args:
        ticker_symbol (str): The stock ticker symbol (e.g., 'AAPL' for Apple Inc.).
        indicators (list, optional): A list of indicators to calculate. 
                                     Defaults to ['SMA', 'RSI', 'MACD'].
    Returns:
        dict: A dictionary containing the calculated indicators.
    """
    # Set the default list inside the function if none is provided
    if indicators is None:
        indicators = ['SMA', 'RSI', 'MACD']

    df = yf.Ticker(ticker_symbol).history(period="6mo")

    result = {}
    if df.empty:
        return {"error": "No historical data found for ticker"}

    # Helper function to format the series correctly
    def format_indicator_series(series, name):
        series = series.dropna().tail(5)
        series.index = series.index.strftime('%Y-%m-%d') # Convert Timestamp index to string
        return series.to_dict()


    if 'SMA' in indicators:
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        result['SMA20'] = format_indicator_series(df['SMA20'], 'SMA20')

    if 'RSI' in indicators:
        rsi_series = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()
        result['RSI'] = format_indicator_series(rsi_series, 'RSI')

    if 'MACD' in indicators:
        macd = ta.trend.MACD(close=df['Close'])
        result['MACD'] = {
            'macd': format_indicator_series(macd.macd(), 'MACD'),
            'signal': format_indicator_series(macd.macd_signal(), 'MACD_Signal')
        }

    return result

if __name__ == "__main__":
    # test result 
    print(calculate_technical_indicators("AAPL"))
    print(get_historical_prices("AAPL"))