import yfinance as yf # type: ignore

def get_stock_history(symbol: str):
    """
    Fetch last 6 months of stock closing prices from Yahoo Finance.
    Returns list of closing prices.
    Returns None if symbol is invalid.
    """

    try:
        symbol = symbol.upper().strip()

        stock = yf.Ticker(symbol)

        hist = stock.history(period="2y")

        if hist.empty:
            return None

        closes = hist["Close"].dropna().tolist()

        return closes

    except Exception:
        return None


def get_current_price(symbol: str):
    """
    Fetch latest current price.
    """

    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1d")

        if hist.empty:
            return None

        return float(hist["Close"].iloc[-1])

    except Exception:
        return None
    
def get_company_stats(symbol: str):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info

        return {
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "52_week_high": info.get("fiftyTwoWeekHigh"),
            "52_week_low": info.get("fiftyTwoWeekLow"),
            "sector": info.get("sector"),
            "industry": info.get("industry")
        }
    except:
        return {}
