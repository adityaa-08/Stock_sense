# import requests
# from textblob import TextBlob # type: ignore

# def get_news_sentiment(symbol):
#     try:
#         url = f"https://news.google.com/rss/search?q={symbol}+stock"
#         response = requests.get(url)

#         if response.status_code != 200:
#             return 0

#         text = response.text

#         # crude headline extraction
#         headlines = text.split("<title>")[1:6]

#         sentiment_scores = []

#         for headline in headlines:
#             clean_text = headline.split("</title>")[0]
#             analysis = TextBlob(clean_text)
#             sentiment_scores.append(analysis.sentiment.polarity)

#         if len(sentiment_scores) == 0:
#             return 0

#         return sum(sentiment_scores) / len(sentiment_scores)

#     except:
#         return 0
    


# import numpy as np
# from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer # type: ignore

# analyzer = SentimentIntensityAnalyzer()

# def analyze_headlines(headlines):

#     scores = []

#     for text in headlines:
#         sentiment = analyzer.polarity_scores(text)
#         scores.append(sentiment["compound"])

#     if not scores:
#         return 0, 0

#     avg_sentiment = float(np.mean(scores))
#     sentiment_volatility = float(np.std(scores))

#     return avg_sentiment, sentiment_volatility    





# from .news_service import fetch_news

# def get_multi_source_sentiment(symbol):

#     headlines = fetch_news(symbol)

#     avg, volatility = analyze_headlines(headlines)

#     return avg, volatility



# import numpy as np
# import time
# from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer # type: ignore

# from .news_service import fetch_news

# analyzer = SentimentIntensityAnalyzer()

# # ------------------------------
# # Simple In-Memory Cache
# # ------------------------------
# CACHE = {}
# CACHE_TTL = 60 * 30  # 30 minutes


# def analyze_headlines(headlines):
#     scores = []

#     for text in headlines:
#         sentiment = analyzer.polarity_scores(text)
#         scores.append(sentiment["compound"])

#     if not scores:
#         return 0.0, 0.0

#     avg_sentiment = float(np.mean(scores))
#     sentiment_volatility = float(np.std(scores))

#     return avg_sentiment, sentiment_volatility


# def get_multi_source_sentiment(symbol):
#     current_time = time.time()

#     # ------------------------------
#     # Check Cache
#     # ------------------------------
#     if symbol in CACHE:
#         cached_data = CACHE[symbol]

#         if current_time - cached_data["timestamp"] < CACHE_TTL:
#             return cached_data["avg"], cached_data["vol"]

#     # ------------------------------
#     # Fetch Fresh Data
#     # ------------------------------
#     headlines = fetch_news(symbol)

#     avg, vol = analyze_headlines(headlines)

#     # ------------------------------
#     # Store In Cache
#     # ------------------------------
#     CACHE[symbol] = {
#         "avg": avg,
#         "vol": vol,
#         "timestamp": current_time
#     }

#     return avg, vol






import numpy as np
import time
import logging
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from .news_service import fetch_news

# -------------------------------------------------
# Initialize Sentiment Analyzer
# -------------------------------------------------
analyzer = SentimentIntensityAnalyzer()

# -------------------------------------------------
# In-Memory Cache Configuration
# -------------------------------------------------
CACHE = {}
CACHE_TTL = 60 * 30  # 30 minutes

# -------------------------------------------------
# Analyze Headlines
# -------------------------------------------------
def analyze_headlines(headlines):
    """
    Analyze a list of headlines using VADER sentiment.
    Returns:
        avg_sentiment (float)
        sentiment_volatility (float)
    """
    scores = []

    for text in headlines:
        try:
            sentiment = analyzer.polarity_scores(text)
            scores.append(sentiment["compound"])
        except Exception as e:
            logging.warning(f"Sentiment analysis error: {e}")

    if not scores:
        return 0.0, 0.0

    avg_sentiment = float(np.mean(scores))
    sentiment_volatility = float(np.std(scores))

    return avg_sentiment, sentiment_volatility


# -------------------------------------------------
# Multi-Source Sentiment with Caching
# -------------------------------------------------
def get_multi_source_sentiment(symbol):

    symbol = symbol.upper().strip()
    current_time = time.time()

    if symbol in CACHE:
        cached_data = CACHE[symbol]
        if current_time - cached_data["timestamp"] < CACHE_TTL:
            return cached_data["avg"], cached_data["vol"]

    try:
        headlines = fetch_news(symbol)
    except Exception as e:
        logging.error(f"News fetch failed for {symbol}: {e}")
        return 0.0, 0.0

    if not headlines:
        return 0.0, 0.0

    avg, vol = analyze_headlines(headlines)

    CACHE[symbol] = {
        "avg": avg,
        "vol": vol,
        "timestamp": current_time
    }

    return avg, vol