from fastapi import APIRouter
from sqlalchemy import text
from ..database import SessionLocal
import yfinance as yf  # type: ignore

router = APIRouter()

# ----------------------------------------
# Add Stock
# ----------------------------------------
@router.post("/portfolio/add")
def add_stock(symbol: str, quantity: int, avg_price: float):

    db = SessionLocal()

    db.execute(
        text("""
            INSERT INTO portfolio (symbol, quantity, avg_price)
            VALUES (:symbol, :quantity, :avg_price)
        """),
        {
            "symbol": symbol.upper(),
            "quantity": quantity,
            "avg_price": avg_price
        }
    )

    db.commit()
    db.close()

    return {"message": "Stock added successfully"}


# ----------------------------------------
# Get Portfolio
# ----------------------------------------
@router.get("/portfolio")
def get_portfolio():

    db = SessionLocal()

    rows = db.execute(
        text("SELECT id, symbol, quantity, avg_price FROM portfolio")
    ).fetchall()

    db.close()

    portfolio_data = []

    for row in rows:

        stock = yf.Ticker(row.symbol)
        hist = stock.history(period="1d")

        if hist.empty:
            current_price = row.avg_price
        else:
            current_price = float(hist["Close"].iloc[-1])

        pnl = (current_price - row.avg_price) * row.quantity

        portfolio_data.append({
            "id": row.id,
            "symbol": row.symbol,
            "quantity": row.quantity,
            "avg_price": row.avg_price,
            "current_price": round(current_price, 2),
            "pnl": round(pnl, 2)
        })

    return portfolio_data