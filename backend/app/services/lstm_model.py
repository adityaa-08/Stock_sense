# import torch
# import torch.nn as nn
# import torch.optim as optim
# import numpy as np
# import os


# class LSTMModel(nn.Module):
#     def __init__(self, input_size=1, hidden_size=64, num_layers=2):
#         super(LSTMModel, self).__init__()
#         self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
#         self.fc = nn.Linear(hidden_size, 1)

#     def forward(self, x):
#         out, _ = self.lstm(x)
#         out = self.fc(out[:, -1, :])
#         return out


# def prepare_data(prices, seq_length=5):
#     X, y = [], []
#     for i in range(len(prices) - seq_length):
#         X.append(prices[i:i+seq_length])
#         y.append(prices[i+seq_length])
#     return np.array(X), np.array(y)


# def train_lstm(prices, epochs=20):
#     model = LSTMModel()
#     criterion = nn.MSELoss()
#     optimizer = optim.Adam(model.parameters(), lr=0.001)

#     X, y = prepare_data(prices)

#     if len(X) == 0:
#         return model

#     X = torch.tensor(X, dtype=torch.float32).unsqueeze(-1)
#     y = torch.tensor(y, dtype=torch.float32)

#     for epoch in range(epochs):
#         optimizer.zero_grad()
#         output = model(X)
#         loss = criterion(output.squeeze(), y)
#         loss.backward()
#         optimizer.step()

#     model.eval()
#     return model


# def predict_lstm(model, history):
#     if len(history) < 5:
#         return history[-1]

#     data = torch.tensor(history[-5:], dtype=torch.float32)\
#                 .unsqueeze(0)\
#                 .unsqueeze(-1)

#     model.eval()
#     with torch.no_grad():
#         prediction = model(data)

#     return float(prediction.item())


# MODEL_PATH = "app/models_store/lstm.pth"


# def save_lstm(model):
#     os.makedirs("app/models_store", exist_ok=True)
#     torch.save(model.state_dict(), MODEL_PATH)


# def load_lstm():
#     model = LSTMModel()
#     if os.path.exists(MODEL_PATH):
#         model.load_state_dict(torch.load(MODEL_PATH))
#         model.eval()
#         return model
#     return None





import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import os


# ----------------------------------------
# LSTM Model Architecture
# ----------------------------------------
class LSTMModel(nn.Module):

    def __init__(self, input_size=1, hidden_size=64, num_layers=2):
        super(LSTMModel, self).__init__()

        self.lstm = nn.LSTM(
            input_size,
            hidden_size,
            num_layers,
            batch_first=True
        )

        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):

        out, _ = self.lstm(x)

        out = self.fc(out[:, -1, :])

        return out


# ----------------------------------------
# Prepare Training Data
# ----------------------------------------
def prepare_data(prices, seq_length=5):

    prices = np.array(prices)

    min_price = prices.min()
    max_price = prices.max()

    # Min-Max Normalization
    scaled = (prices - min_price) / (max_price - min_price)

    X = []
    y = []

    for i in range(len(scaled) - seq_length):

        X.append(scaled[i:i + seq_length])
        y.append(scaled[i + seq_length])

    return np.array(X), np.array(y), min_price, max_price


# ----------------------------------------
# Train LSTM Model
# ----------------------------------------
def train_lstm(prices, epochs=100):

    model = LSTMModel()

    criterion = nn.MSELoss()

    optimizer = optim.Adam(model.parameters(), lr=0.001)

    X, y, min_price, max_price = prepare_data(prices)

    X = torch.tensor(X, dtype=torch.float32).unsqueeze(-1)

    y = torch.tensor(y, dtype=torch.float32)

    for epoch in range(epochs):

        optimizer.zero_grad()

        output = model(X)

        loss = criterion(output.squeeze(), y)

        loss.backward()

        optimizer.step()

    # Save normalization values
    model.min_price = min_price
    model.max_price = max_price

    return model


# ----------------------------------------
# Predict Future Price
# ----------------------------------------
def predict_lstm(model, history):

    seq = np.array(history[-5:])

    min_price = model.min_price
    max_price = model.max_price

    # Normalize input
    scaled = (seq - min_price) / (max_price - min_price)

    data = torch.tensor(scaled, dtype=torch.float32).unsqueeze(0).unsqueeze(-1)

    with torch.no_grad():

        prediction = model(data).item()

    # Reverse normalization
    predicted_price = prediction * (max_price - min_price) + min_price

    return float(predicted_price)


# ----------------------------------------
# Model Storage Path
# ----------------------------------------
MODEL_PATH = "app/models_store/lstm.pth"


# ----------------------------------------
# Save Model
# ----------------------------------------
def save_lstm(model):

    os.makedirs("app/models_store", exist_ok=True)

    torch.save({
        "model_state": model.state_dict(),
        "min_price": model.min_price,
        "max_price": model.max_price
    }, MODEL_PATH)


# ----------------------------------------
# Load Model
# ----------------------------------------
def load_lstm():

    if not os.path.exists(MODEL_PATH):
        return None

    checkpoint = torch.load(MODEL_PATH)

    model = LSTMModel()

    model.load_state_dict(checkpoint["model_state"])

    model.min_price = checkpoint["min_price"]
    model.max_price = checkpoint["max_price"]

    model.eval()

    return model