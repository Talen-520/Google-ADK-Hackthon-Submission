from playwright.async_api import async_playwright, Browser, TimeoutError as PlaywrightTimeoutError
import asyncio # Import asyncio for running async functions
from typing import List, Dict,Optional
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd
import ta
import datetime
from zoneinfo import ZoneInfo
import json

def get_current_time(timezone: str = "America/New_York") -> str:
    """
    Gets the current time in a specified timezone and returns it as a formatted string.

    Args:
        timezone (str, optional): The IANA timezone name (e.g., "America/Los_Angeles", 
                                  "Europe/London", "Asia/Tokyo"). 
                                  Defaults to "America/New_York" (Eastern Time).
                                  
    Returns:
        str: The current time formatted as 'Day, Mon Day, Year, HH:MM AM/PM'.
             For example: 'Tue, Jun 10, 2025, 04:52 PM'.
    """
    try:
        # Get the ZoneInfo object for the specified timezone
        tz = ZoneInfo(timezone)
    except Exception:
        tz = ZoneInfo("America/New_York")

    now_with_tz = datetime.datetime.now(tz)


    formatted_time = now_with_tz.strftime("%a, %b %d, %Y, %I:%M %p")

    return formatted_time

# earnings calendar
def get_earnings_calendar(ticker_symbol: str) -> dict:
    """
    Retrieves earnings calendar data from Yahoo Finance.
    Args:
        ticker_symbol (str): The stock ticker symbol (e.g., 'AAPL' for Apple Inc.).
    Returns:
        dict: A dictionary containing earnings calendar data.
    """
    calendar_df = yf.Ticker(ticker_symbol).calendar
    if calendar_df.empty:
        return {}

    # The data is a DataFrame with a single row. Transpose it to work with it easily.
    calendar_series = calendar_df.transpose()[0]
    
    # Convert any timestamp objects to string format
    for idx, value in calendar_series.items():
        if isinstance(value, pd.Timestamp):
            calendar_series[idx] = value.isoformat()

    return calendar_series.to_dict()


if __name__ == "__main__":
    print(get_current_time())

