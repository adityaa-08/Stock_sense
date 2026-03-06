import numpy as np
import torch

from .lstm_model import predict_lstm
from .sentiment_service import get_multi_source_sentiment
from .trends_service import get_trend_score


MAX_ASSETS = 10
FEATURES_PER_ASSET = 4

def calculate_sharpe_ratio(returns, risk_free_rate=0.01):
    returns = np.array(returns)
    if len(returns) < 2:
        return 0

    excess_returns = returns - (risk_free_rate / 252)
    std = np.std(excess_returns)

    if std == 0:
        return 0

    return float((np.mean(excess_returns) / std) * np.sqrt(252))


def calculate_max_drawdown(equity_curve):
    peak = equity_curve[0]
    max_dd = 0

    for value in equity_curve:
        if value > peak:
            peak = value
        dd = (peak - value) / peak
        max_dd = max(max_dd, dd)

    return float(max_dd)


def backtest_multi_asset(agent, lstm_model, assets_data):

    if agent is None or lstm_model is None:
        return {"error": "Model not initialized"}

    asset_list = list(assets_data.keys())

    if len(asset_list) > MAX_ASSETS:
        return {"error": f"Maximum {MAX_ASSETS} assets supported"}

    initial_capital = 10000
    capital = initial_capital

    equity_curve = []
    daily_returns = []

    min_length = min(len(data) for data in assets_data.values())

    if min_length < 10:
        return {"error": "Not enough historical data"}

    for i in range(5, min_length - 1):

        state = []

        # -----------------------------
        # Build State For Real Assets
        # -----------------------------
        for asset in asset_list:
            prices = assets_data[asset]
            history = prices[:i]

            predicted_price = predict_lstm(lstm_model, history)
            news_avg, news_vol = get_multi_source_sentiment(asset)
            trend_score = get_trend_score(asset)

            state.extend([
                predicted_price / 1000,
                news_avg,
                news_vol,
                trend_score
            ])

        # -----------------------------
        # Pad Remaining Slots
        # -----------------------------
        remaining = MAX_ASSETS - len(asset_list)
        for _ in range(remaining):
            state.extend([0, 0, 0, 0])

        state_tensor = torch.FloatTensor(state).unsqueeze(0)

        # -----------------------------
        # Portfolio Allocation
        # -----------------------------
        with torch.no_grad():
            logits = agent.model(state_tensor)
            weights = torch.softmax(logits, dim=-1)[0].detach().cpu().numpy()

        # Use only real assets
        weights = weights[:len(asset_list)]

        if np.sum(weights) > 0:
            weights = weights / np.sum(weights)
        else:
            weights = np.ones(len(asset_list)) / len(asset_list)

        # -----------------------------
        # Compute Portfolio Return
        # -----------------------------
        daily_return = 0

        for idx, asset in enumerate(asset_list):
            prices = assets_data[asset]
            r = (prices[i + 1] - prices[i]) / prices[i]
            daily_return += weights[idx] * r

        capital *= (1 + daily_return)

        equity_curve.append(capital)
        daily_returns.append(daily_return)

    total_return = (capital - initial_capital) / initial_capital
    sharpe = calculate_sharpe_ratio(daily_returns)
    max_dd = calculate_max_drawdown(equity_curve)
    
    return {
        "initial_capital": initial_capital,
        "final_portfolio_value": round(capital, 2),
        "total_return": round(total_return, 4),
        "sharpe_ratio": round(sharpe, 4),
        "max_drawdown": round(max_dd, 4),
        "equity_curve": [round(v, 2) for v in equity_curve]
    }