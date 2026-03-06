# # backend/app/services/training_service.py

# from .reward_service import risk_reward
# import numpy as np


# def train_agent(agent, states, prices):

#     rewards = []

#     for i in range(len(states) - 1):

#         state = states[i]
#         next_state = states[i + 1]

#         # Calculate profit
#         profit = (prices[i + 1] - prices[i]) / prices[i]

#         # Calculate volatility
#         volatility = np.std(prices[max(0, i-5):i+1])

#         reward = risk_reward(profit, volatility)

#         done = (i == len(states) - 2)

#         action = agent.act(state)
#         agent.remember(state, action, reward, next_state, done)

#         agent.replay()

#         rewards.append(reward)

#     return rewards







# backend/app/services/training_service.py

import numpy as np
from .reward_service import risk_reward


def train_agent(agent, states, prices):

    rewards = []

    if len(states) < 10:
        return rewards

    for i in range(len(states) - 1):

        state = np.array(states[i], dtype=np.float32)
        next_state = np.array(states[i + 1], dtype=np.float32)

        # ---------------------------------------
        # Calculate Daily Return
        # ---------------------------------------
        current_price = prices[i]
        next_price = prices[i + 1]

        if current_price == 0:
            continue

        profit = (next_price - current_price) / current_price

        # ---------------------------------------
        # Volatility (10 day window)
        # ---------------------------------------
        window = prices[max(0, i - 10): i + 1]

        if len(window) > 1:
            volatility = np.std(window) / np.mean(window)
        else:
            volatility = 0

        # ---------------------------------------
        # Risk Adjusted Reward
        # ---------------------------------------
        reward = risk_reward(profit, volatility)

        # ---------------------------------------
        # Done Flag
        # ---------------------------------------
        done = (i == len(states) - 2)

        # ---------------------------------------
        # RL Action
        # ---------------------------------------
        action = agent.act(state)

        # ---------------------------------------
        # Store Experience
        # ---------------------------------------
        agent.remember(
            state,
            action,
            reward,
            next_state,
            done
        )

        # ---------------------------------------
        # Train Network
        # ---------------------------------------
        agent.replay()

        rewards.append(reward)

    return rewards