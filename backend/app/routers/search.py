from fastapi import APIRouter
import requests

router = APIRouter()

@router.get("/search-stock")
def search_stock(q: str):

    url = "https://query1.finance.yahoo.com/v1/finance/search"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    params = {
        "q": q,
        "quotesCount": 10,
        "newsCount": 0
    }

    try:
        response = requests.get(url, headers=headers, params=params)

        data = response.json()

        results = []

        for item in data.get("quotes", []):
            symbol = item.get("symbol")
            name = item.get("shortname") or item.get("longname")

            if symbol and name:
                results.append({
                    "symbol": symbol,
                    "name": name
                })

        return results

    except Exception as e:
        print("Search API error:", e)
        return []