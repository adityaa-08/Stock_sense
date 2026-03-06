import requests
import os
import logging

NEWS_API_KEY = "ce19dd41f65c4ad49127b257ce528281"


def fetch_news(symbol):

    if not NEWS_API_KEY:
        logging.warning("NEWS_API_KEY not set")
        return []

    try:
        url = (
            f"https://newsapi.org/v2/everything?"
            f"q={symbol}&pageSize=10&apiKey={NEWS_API_KEY}"
        )

        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            logging.warning(
                f"News API failed: {response.status_code}"
            )
            return []

        data = response.json()

        articles = data.get("articles", [])
        headlines = [
            a.get("title") for a in articles
            if a.get("title")
        ]

        return headlines

    except Exception as e:
        logging.error(f"News fetch error: {e}")
        return []