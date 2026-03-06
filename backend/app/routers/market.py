from fastapi import APIRouter
from ..services.market_service import get_stock_history

router = APIRouter()

@router.get("/stock-history/{symbol}")
def stock_history(symbol: str):

    prices = get_stock_history(symbol)

    if not prices:
        return {"error": "Invalid symbol"}

    return {
        "symbol": symbol.upper(),
        "prices": prices
    }