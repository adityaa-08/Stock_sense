# from fastapi import APIRouter, Request
# from pydantic import BaseModel
# from typing import List
# import torch
# import numpy as np
# import yfinance as yf # type: ignore

# from ..services.market_service import (
#     get_stock_history,
#     get_company_stats
# )
# from ..services.lstm_model import predict_lstm
# from ..services.sentiment_service import get_multi_source_sentiment
# from ..services.trends_service import get_trend_score

# router = APIRouter()

# MAX_ASSETS = 10
# FEATURES_PER_ASSET = 4


# # Request Model
# class PortfolioRequest(BaseModel):
#     symbols: List[str]



# # Portfolio Prediction Endpoint
# @router.post("/portfolio-predict")
# def portfolio_predict(request: Request, data: PortfolioRequest):

#     agent = request.app.state.agent
#     lstm_model = request.app.state.lstm_model

#     if agent is None or lstm_model is None:
#         return {"error": "Model not initialized"}

#     symbols = data.symbols

#     if not symbols:
#         return {"error": "No symbols provided"}

#     if len(symbols) > MAX_ASSETS:
#         return {"error": f"Maximum {MAX_ASSETS} assets supported"}

#     state = []
#     asset_outputs = []

# # Build State & Collect Asset Data
#     for symbol in symbols:

#         symbol = symbol.upper().strip()

#         history = get_stock_history(symbol)

#         if not history or len(history) < 6:
#             return {"error": f"Invalid stock symbol or insufficient data: {symbol}"}

#         current_price = history[-1]
#         predicted_price = predict_lstm(lstm_model, history)

#         news_avg, news_vol = get_multi_source_sentiment(symbol)
#         trend_score = get_trend_score(symbol)
#         company_stats = get_company_stats(symbol)

        

#         # BUY / SELL / HOLD Decision Logic
#         change = (predicted_price - current_price) / current_price
#         print("Current:", current_price)
#         print("Predicted:", predicted_price)
#         print("Change:", change)

#         if change > 0.01 and news_avg >0:
#             decision = "BUY"
#         elif change < -0.01 and news_avg < 0:
#             decision = "SELL"
#         else:
#             decision = "HOLD"        

#         # Add to RL State Vector
#         state.extend([
#             predicted_price / 1000,
#             news_avg,
#             news_vol,
#             trend_score
#         ])

#         asset_outputs.append({
#             "symbol": symbol,
#             "current_price": round(current_price, 2),
#             "predicted_price": round(predicted_price, 2),
#             "decision": decision,
#             "news_sentiment_avg": round(news_avg, 4),
#             "news_sentiment_volatility": round(news_vol, 4),
#             "trend_score": round(trend_score, 4),
#             "company_stats": company_stats
#         })

#     # Pad State to Fixed Size
#     remaining = MAX_ASSETS - len(symbols)
#     for _ in range(remaining):
#         state.extend([0, 0, 0, 0])

#     state_tensor = torch.FloatTensor(state).unsqueeze(0)

#     # DRL Allocation
#     try:
#         with torch.no_grad():
#             logits = agent.model(state_tensor)
#             weights = torch.softmax(logits, dim=-1)[0].detach().cpu().numpy()
#     except Exception as e:
#         return {"error": f"DQN inference failed: {str(e)}"}

#     weights = weights[:len(symbols)]

#     if np.sum(weights) > 0:
#         weights = weights / np.sum(weights)
#     else:
#         weights = np.ones(len(symbols)) / len(symbols)

#     # Attach allocation weight
#     for i in range(len(symbols)):
#         asset_outputs[i]["allocation_weight"] = round(float(weights[i]), 4)

#     return {
#         "portfolio_allocation": asset_outputs,
#         "total_assets": len(symbols)
#     }


# # Candlestick Chart Data Endpoint
# @router.get("/stock-history/{symbol}")
# def get_chart_data(symbol: str):

#     symbol = symbol.upper().strip()

#     try:
#         stock = yf.Ticker(symbol)
#         hist = stock.history(period="3mo")

#         if hist.empty:
#             return []

#         data = []

#         for date, row in hist.iterrows():
#             data.append({
#                 "time": date.strftime("%Y-%m-%d"),
#                 "open": float(row["Open"]),
#                 "high": float(row["High"]),
#                 "low": float(row["Low"]),
#                 "close": float(row["Close"])
#             })

#         return data

#     except Exception:
#         return []









from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import List
import torch
import numpy as np
import yfinance as yf

from ..services.market_service import (
    get_stock_history,
    get_company_stats
)

from ..services.lstm_model import predict_lstm
from ..services.sentiment_service import get_multi_source_sentiment
from ..services.trends_service import get_trend_score

router = APIRouter()

MAX_ASSETS = 10
FEATURES_PER_ASSET = 4


# ---------------------------------------
# Request Model
# ---------------------------------------
class PortfolioRequest(BaseModel):
    symbols: List[str]


# ---------------------------------------
# Portfolio Prediction Endpoint
# ---------------------------------------
@router.post("/portfolio-predict")
def portfolio_predict(request: Request, data: PortfolioRequest):

    agent = request.app.state.agent
    lstm_model = request.app.state.lstm_model

    if agent is None or lstm_model is None:
        return {"error": "Model not initialized"}

    symbols = data.symbols

    if not symbols:
        return {"error": "No symbols provided"}

    if len(symbols) > MAX_ASSETS:
        return {"error": f"Maximum {MAX_ASSETS} assets supported"}

    state = []
    asset_outputs = []

    # ---------------------------------------
    # Build State & Asset Data
    # ---------------------------------------
    for symbol in symbols:

        symbol = symbol.upper().strip()

        history = get_stock_history(symbol)

        if not history or len(history) < 10:
            return {"error": f"Invalid stock symbol or insufficient data: {symbol}"}

        current_price = history[-1]

        predicted_price = predict_lstm(lstm_model, history)

        news_avg, news_vol = get_multi_source_sentiment(symbol)

        trend_score = get_trend_score(symbol)

        company_stats = get_company_stats(symbol)

        # ---------------------------------------
        # Calculate Price Change %
        # ---------------------------------------
        price_change = (predicted_price - current_price) / current_price

        print("------")
        print("Stock:", symbol)
        print("Current:", current_price)
        print("Predicted:", predicted_price)
        print("Change:", price_change)
        print("Sentiment:", news_avg)
        print("Trend:", trend_score)

        # ---------------------------------------
        # Decision Logic
        # ---------------------------------------
        decision = "HOLD"

        if price_change > 0.003 and news_avg > 0:
            decision = "BUY"

        elif price_change < -0.003 and news_avg < 0:
            decision = "SELL"

        elif price_change > 0.001:
            decision = "BUY"

        elif price_change < -0.001:
            decision = "SELL"

        # ---------------------------------------
        # RL State Vector
        # ---------------------------------------
        state.extend([
            predicted_price / 1000,
            news_avg,
            news_vol,
            trend_score
        ])

        # ---------------------------------------
        # Asset Output
        # ---------------------------------------
        asset_outputs.append({
            "symbol": symbol,
            "current_price": round(current_price, 2),
            "predicted_price": round(predicted_price, 2),
            "decision": decision,
            "news_sentiment_avg": round(news_avg, 4),
            "news_sentiment_volatility": round(news_vol, 4),
            "trend_score": round(trend_score, 4),
            "company_stats": company_stats
        })

    # ---------------------------------------
    # Pad State to Fixed Size
    # ---------------------------------------
    remaining = MAX_ASSETS - len(symbols)

    for _ in range(remaining):
        state.extend([0, 0, 0, 0])

    state_tensor = torch.FloatTensor(state).unsqueeze(0)

    # ---------------------------------------
    # DQN Portfolio Allocation
    # ---------------------------------------
    try:
        with torch.no_grad():

            logits = agent.model(state_tensor)

            weights = torch.softmax(logits, dim=-1)[0].detach().cpu().numpy()

    except Exception as e:

        return {"error": f"DQN inference failed: {str(e)}"}

    weights = weights[:len(symbols)]

    if np.sum(weights) > 0:
        weights = weights / np.sum(weights)
    else:
        weights = np.ones(len(symbols)) / len(symbols)

    # ---------------------------------------
    # Attach Allocation Weight
    # ---------------------------------------
    for i in range(len(symbols)):

        asset_outputs[i]["allocation_weight"] = round(float(weights[i]), 4)

    return {
        "portfolio_allocation": asset_outputs,
        "total_assets": len(symbols)
    }

@router.get("/stock-history/{symbol}")
def get_chart_data(symbol: str, period: str = "3mo"):

    symbol = symbol.upper().strip()

    # Validate period
    valid_periods = ["1mo", "3mo", "6mo", "1y", "2y", "5y"]
    if period not in valid_periods:
        period = "3mo"

    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)

        if hist.empty:
            return []

        data = []
        for date, row in hist.iterrows():
            data.append({
                "time":  date.strftime("%Y-%m-%d"),
                "open":  float(row["Open"]),
                "high":  float(row["High"]),
                "low":   float(row["Low"]),
                "close": float(row["Close"])
            })

        return data

    except Exception:
        return []