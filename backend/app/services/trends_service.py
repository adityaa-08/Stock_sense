from pytrends.request import TrendReq # type: ignore
import time
import logging

# -----------------------------
# Simple In-Memory Cache
# -----------------------------
CACHE = {}
CACHE_TTL = 60 * 60  # 1 hour


def get_trend_score(symbol):

    symbol = symbol.upper().strip()
    current_time = time.time()

    # -----------------------------
    # Check Cache
    # -----------------------------
    if symbol in CACHE:
        cached = CACHE[symbol]
        if current_time - cached["timestamp"] < CACHE_TTL:
            return cached["value"]

    # -----------------------------
    # Fetch From Google Trends
    # -----------------------------
    try:
        pytrends = TrendReq()

        pytrends.build_payload([symbol], timeframe="now 7-d")
        data = pytrends.interest_over_time()

        if not data.empty and symbol in data.columns:
            value = float(data[symbol].iloc[-1]) / 100
        else:
            value = 0.5

        CACHE[symbol] = {
            "value": value,
            "timestamp": current_time
        }

        return value

    except Exception as e:
        logging.warning(f"Trend fetch failed for {symbol}: {e}")
        return 0.5