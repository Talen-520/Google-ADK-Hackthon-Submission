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
# In your test.py, only this function needs to be updated.

async def get_yahoo_article_content(browser: Browser, url: str) -> Dict[str, str]:
    """
    Extracts the main article content from a given Yahoo Finance URL.
    This final version uses highly specific locators to avoid strict mode violations.
    """
    page = await browser.new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # Handle consent dialog (this logic is good)
        try:
            consent_frame_locator = page.frame_locator('iframe[title="Consent Management Z Dialog"]')
            await consent_frame_locator.locator('button:has-text("Accept all")').click(timeout=7000)
        except Exception:
            pass # Ignore if not found

        # Wait for the main content area to ensure the page is ready
        await page.wait_for_selector("main", timeout=15000)
        
        # Click "Continue Reading" if it exists (this logic is good)
        try:
            continue_btn = page.locator("button:has-text('Continue Reading')")
            if await continue_btn.is_visible(timeout=5000):
                await continue_btn.click()
                await page.wait_for_load_state('networkidle', timeout=20000)
        except Exception:
            pass

        # --- FINAL FIX ---
        # 🎯 Use specific locators for title and time to get exactly one element.
        # The error log showed 'h1.cover-title' is the correct title.
        title_locator = page.locator("h1.cover-title")
        
        # We'll use a similarly specific locator for the timestamp.
        time_locator = page.locator("time.byline-attr-meta-time")

        # The fallback logic for the article body is working well, so we keep it.
        article_locator = page.locator('div.caas-body')
        try:
            await article_locator.first.wait_for(timeout=10000)
        except PlaywrightTimeoutError:
            # This fallback is a good robust feature.
            # print(f"Warning: Could not find 'div.caas-body' on {url}. Falling back to the main <article> tag.")
            article_locator = page.locator('article').first
            await article_locator.wait_for(timeout=5000)

        # Now we extract the text using our specific locators.
        title_text = await title_locator.inner_text()
        time_text = await time_locator.inner_text()
        full_text = await article_locator.inner_text()
        
        return {
            "title": title_text.strip(),
            "date": time_text.strip(),
            "content": full_text.strip()
        }
    except Exception as e:
        return {
            "url": url,
            "error": f"Error extracting content: {type(e).__name__}: {e}"
        }
    finally:
        await page.close()

async def scrape_news(ticker: str, num_url: int = 5) -> List[Dict[str, str]]:
    """
    为给定的股票代码从雅虎财经抓取新闻文章。
    """
    print(f"Starting to scrape Yahoo Finance news for {ticker}")
    news_page_url = f"https://finance.yahoo.com/quote/{ticker}/news/"
    
    unique_article_urls = []
    async with async_playwright() as p:
        # 优化4: 调试时使用 headless=False，完成时改回 True
        browser = await p.chromium.launch(headless=True) 
        page = await browser.new_page()
        
        try:
            # ... (这部分逻辑保持不变，它工作得很好) ...
            await page.goto(news_page_url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_selector('li.stream-item', timeout=20000)
            
            links_locators = await page.query_selector_all('li.stream-item a[href]')
            
            seen_urls = set()
            for link_loc in links_locators:
                href = await link_loc.get_attribute('href')
                if href:
                    if href.startswith('/'):
                        href = f"https://finance.yahoo.com{href}"
                    
                    if "/news/" in href and ".html" in href:
                        clean_url = href.split('?')[0]
                        if clean_url not in seen_urls:
                           seen_urls.add(clean_url)
                           unique_article_urls.append(clean_url)
        except Exception as e:
            print(f"Error while scraping article links: {e}")
        finally:
            await page.close()

        if not unique_article_urls:
            print("Could not find any unique article URLs.")
            await browser.close()
            return []

        print(f"Found {len(unique_article_urls)} unique article links. Fetching content for the first {num_url}...")
        
        urls_to_fetch = unique_article_urls[:num_url]
        tasks = [get_yahoo_article_content(browser, url) for url in urls_to_fetch]
        articles = await asyncio.gather(*tasks)
        
        await browser.close()
    
    print("--------  Finished scraping Yahoo Finance news --------")
    return articles

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

# basic company info
def get_company_profile(ticker_symbol: str) -> dict:
    """
    Retrieves basic company profile information from Yahoo Finance.
    Args:
        ticker_symbol (str): The stock ticker symbol (e.g., 'AAPL' for Apple Inc.).
    Returns:
        dict: A dictionary containing company profile information, including name, sector, industry, and summary.
    """
    ticker = yf.Ticker(ticker_symbol)
    info = ticker.info
    return {
        "name": info.get("longName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "summary": info.get("longBusinessSummary")
    }




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



# dividend info
def get_dividend_info(ticker_symbol: str) -> dict:
    """
    Retrieves dividend information from Yahoo Finance.
    Args:
        ticker_symbol (str): The stock ticker symbol (e.g., 'AAPL' for Apple Inc.).
    Returns:
        dict: A dictionary containing dividend information.
    """
    info = yf.Ticker(ticker_symbol).info
    return {
        "dividendRate": info.get("dividendRate"),
        "dividendYield": info.get("dividendYield"),
        "exDividendDate": info.get("exDividendDate")
    }


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

async def main():
    import json

    results = await scrape_news(ticker="NVDA", num_url=3)
    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())

