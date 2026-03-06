# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from .database import Base, engine
# from .routers import predict, portfolio, backtest
# from .services.dqn_agent import DQNAgent
# from .services.market_service import get_stock_history
# from .services.lstm_model import train_lstm, load_lstm, save_lstm
# from .import models

# # FastAPI App
# # ----------------------------------------
# app = FastAPI()

# # CORS (for React frontend)
# # ----------------------------------------
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Create DB Tables
# # ----------------------------------------
# Base.metadata.create_all(bind=engine)

# # Model Configuration
# # ----------------------------------------
# MAX_ASSETS = 10
# FEATURES_PER_ASSET = 4

# STATE_DIM = MAX_ASSETS * FEATURES_PER_ASSET
# ACTION_DIM = MAX_ASSETS

# agent = DQNAgent(state_dim=STATE_DIM, action_dim=ACTION_DIM)

# # Startup Event
# # ----------------------------------------
# @app.on_event("startup")
# def startup_event():

#     print("Starting TradeMind Backend...")

#     # Load or Train LSTM
#     lstm_model = load_lstm()

#     if lstm_model is None:
#         print("No saved LSTM found. Training...")
#         prices = get_stock_history("AAPL")

#         if prices and len(prices) > 20:
#             lstm_model = train_lstm(prices, epochs=100)
#             save_lstm(lstm_model)
#             print("LSTM trained & saved")
#         else:
#             print("Not enough data to train LSTM")
#             lstm_model = None
#     else:
#         print("LSTM loaded")

#     # Load DQN
#     agent.load()
#     print("DQN loaded")

#     app.state.agent = agent
#     app.state.lstm_model = lstm_model

#     print("Backend Ready")

# # Include Routers
# # ----------------------------------------
# app.include_router(predict.router)
# app.include_router(portfolio.router)
# app.include_router(backtest.router)









from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import predict, portfolio, backtest
from .services.dqn_agent import DQNAgent
from .services.market_service import get_stock_history
from .services.lstm_model import train_lstm, load_lstm, save_lstm
from .routers import search
from .routers import news
from . import models

# ----------------------------------------
# FastAPI App
# ----------------------------------------
app = FastAPI()

# ----------------------------------------
# CORS (React Frontend)
# ----------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------
# Create Database Tables
# ----------------------------------------
Base.metadata.create_all(bind=engine)

# ----------------------------------------
# Model Configuration
# ----------------------------------------
MAX_ASSETS = 10
FEATURES_PER_ASSET = 4

STATE_DIM = MAX_ASSETS * FEATURES_PER_ASSET
ACTION_DIM = MAX_ASSETS

# Initialize RL Agent
agent = DQNAgent(STATE_DIM, ACTION_DIM)

# ----------------------------------------
# Startup Event
# ----------------------------------------
@app.on_event("startup")
def startup_event():

    print("Starting TradeMind Backend...")

    # ----------------------------------------
    # Load or Train LSTM
    # ----------------------------------------
    lstm_model = load_lstm()

    if lstm_model is None:

        print("No saved LSTM found. Training...")

        # Train on multiple stocks
        symbols = ["AAPL", "TSLA", "MSFT", "NVDA", "AMZN"]

        all_prices = []

        for symbol in symbols:

            prices = get_stock_history(symbol)

            if prices and len(prices) > 50:
                all_prices.extend(prices)

        if len(all_prices) > 200:

            lstm_model = train_lstm(all_prices, epochs=100)

            save_lstm(lstm_model)

            print("LSTM trained with multi-stock data & saved")

        else:

            print("Not enough data to train LSTM")
            lstm_model = None

    else:
        print("LSTM loaded")

    # ----------------------------------------
    # Load DQN Model
    # ----------------------------------------
    try:
        agent.load()
        print("DQN loaded")
    except:
        print("No trained DQN found. Using random initialized agent")

    # ----------------------------------------
    # Store Models in App State
    # ----------------------------------------
    app.state.agent = agent
    app.state.lstm_model = lstm_model

    print("Backend Ready")

# ----------------------------------------
# Include Routers
# ----------------------------------------
app.include_router(predict.router)
app.include_router(portfolio.router)
app.include_router(backtest.router)
app.include_router(search.router)
app.include_router(news.router)