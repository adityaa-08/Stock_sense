# import torch
# import torch.nn as nn
# import os


# class DQN(nn.Module):
#     def __init__(self, state_dim, action_dim):
#         super(DQN, self).__init__()
#         self.fc1 = nn.Linear(state_dim, 256)
#         self.fc2 = nn.Linear(256, 128)
#         self.fc3 = nn.Linear(128, action_dim)

#     def forward(self, x):
#         x = torch.relu(self.fc1(x))
#         x = torch.relu(self.fc2(x))
#         return self.fc3(x)


# class DQNAgent:
#     def __init__(self, state_dim, action_dim):
#         self.state_dim = state_dim
#         self.action_dim = action_dim
#         self.model = DQN(state_dim, action_dim)

#     def save(self):
#         os.makedirs("app/models_store", exist_ok=True)
#         torch.save(self.model.state_dict(), "app/models_store/dqn.pth")

#     def load(self):
#         path = "app/models_store/dqn.pth"
#         if os.path.exists(path):
#             self.model.load_state_dict(torch.load(path))





import torch
import torch.nn as nn
import torch.optim as optim
import os

MODEL_PATH = "app/models_store/dqn.pth"


class DQNNetwork(nn.Module):

    def __init__(self, state_dim, action_dim):

        super(DQNNetwork, self).__init__()

        self.net = nn.Sequential(

            nn.Linear(state_dim, 128),
            nn.ReLU(),

            nn.Linear(128, 128),
            nn.ReLU(),

            nn.Linear(128, action_dim)
        )

    def forward(self, x):

        return self.net(x)


class DQNAgent:

    def __init__(self, state_dim, action_dim):

        self.state_dim = state_dim
        self.action_dim = action_dim

        self.model = DQNNetwork(state_dim, action_dim)

        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)

        self.criterion = nn.MSELoss()

    def save(self):

        os.makedirs("app/models_store", exist_ok=True)

        torch.save(self.model.state_dict(), MODEL_PATH)

    def load(self):

        if os.path.exists(MODEL_PATH):

            self.model.load_state_dict(torch.load(MODEL_PATH))

            self.model.eval()