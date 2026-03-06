from fastapi import APIRouter
import requests

router = APIRouter()

NEWS_API_KEY = "ce19dd41f65c4ad49127b257ce528281"

@router.get("/stock-news/{symbol}")
def get_stock_news(symbol: str):

    url = "https://newsapi.org/v2/everything"

    params = {
        "q": symbol,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 5,
        "apiKey": NEWS_API_KEY
    }

    response = requests.get(url, params=params)

    data = response.json()

    articles = []

    for item in data.get("articles", []):

        articles.append({
            "title": item["title"],
            "url": item["url"],
            "source": item["source"]["name"]
        })

    return articles