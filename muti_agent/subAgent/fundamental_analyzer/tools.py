import yfinance as yf

# financial statements
def get_financial_statements(ticker_symbol: str) -> dict:
    """
    Retrieves financial statements from Yahoo Finance in a JSON-friendly format.
    Args:
        ticker_symbol (str): The stock ticker symbol (e.g., 'AAPL' for Apple Inc.).
    Returns:
        dict: A dictionary containing income statement, balance sheet, and cash flow data.
    """
    ticker = yf.Ticker(ticker_symbol)

    def format_statement(statement_df):
        if statement_df.empty:
            return []
        # The financial statement columns are Timestamps. We need to transpose,
        # reset index, and format the new 'index' column (which contains the dates).
        df = statement_df.transpose()
        df.reset_index(inplace=True)
        # The column with dates is now named 'index'. Convert it to string.
        df['index'] = df['index'].astype(str)
        return df.to_dict(orient='records')

    return {
        "incomeStatement": format_statement(ticker.financials),
        "balanceSheet": format_statement(ticker.balance_sheet),
        "cashFlow": format_statement(ticker.cashflow)
    }
# financial ratios
def get_key_ratios(ticker_symbol: str) -> dict:
    """
    Retrieves key financial ratios from Yahoo Finance.
    Args:
        ticker_symbol (str): The stock ticker symbol (e.g., 'AAPL' for Apple Inc.).
    Returns:
        dict: A dictionary containing key financial ratios, including market cap, P/E ratio, ROE, and gross margin.
    """
    info = yf.Ticker(ticker_symbol).info
    return {
        "marketCap": info.get("marketCap"),
        "peRatio": info.get("trailingPE"),
        "roe": info.get("returnOnEquity"),
        "grossMargin": info.get("grossMargins")
    }

# analyst recommendations
def get_analyst_ratings(ticker_symbol: str) -> dict:
    """
    Retrieves analyst recommendations from Yahoo Finance.
    Args:
        ticker_symbol (str): The stock ticker symbol (e.g., 'AAPL' for Apple Inc.).
    Returns:
        dict: A dictionary containing analyst recommendations.
    """
    info = yf.Ticker(ticker_symbol).info
    return {
        "recommendation": info.get("recommendationKey"),
        "targetMeanPrice": info.get("targetMeanPrice"),
        "targetHighPrice": info.get("targetHighPrice"),
        "targetLowPrice": info.get("targetLowPrice")
    }