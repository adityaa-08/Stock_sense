
from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import List

from ..services.market_service import get_stock_history
from ..services.backtest_service import backtest_multi_asset

router = APIRouter()


class AssetRequest(BaseModel):
    symbols: List[str]


# @router.post("/multi-backtest")
# def multi_asset_backtest(request: Request, data: AssetRequest):

#     agent = request.app.state.agent
#     lstm_model = request.app.state.lstm_model

#     assets_data = {}

#     for symbol in data.symbols:
#         prices = get_stock_history(symbol)

#         if not prices or len(prices) < 10:
#             return {"error": f"Invalid or insufficient data for {symbol}"}

#         assets_data[symbol] = prices

#     return backtest_multi_asset(agent, lstm_model, assets_data)

@router.post("/multi-backtest")
def multi_asset_backtest(request: Request, data: AssetRequest):

    agent = request.app.state.agent
    lstm_model = request.app.state.lstm_model

    if agent is None or lstm_model is None:
        return {"error": "Model not initialized"}

    assets_data = {}

    for symbol in data.symbols:
        prices = get_stock_history(symbol)

        if not prices or len(prices) < 10:
            return {"error": f"Invalid or insufficient data for {symbol}"}

        assets_data[symbol] = prices

    return backtest_multi_asset(agent, lstm_model, assets_data)