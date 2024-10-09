import torch
import random
import numpy as np
from PongGame import Pong, MAX_SPEED
from collections import deque
from model import Linear_QNet, QTrainer, device  # Updated import
from helper import plot
import sys

MAX_MEMORY = 200_000
BATCH_SIZE = 1000
LR = 0.0001

class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 1  # random
        self.gamma = 0.99  # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)  # will pop when len exceeded
        self.model = Linear_QNet(5, 256, 2).to(device)  # Move model to device
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game):
        # Extract positions and speeds
        ball_x, ball_y = game.xy
        paddle_x, paddle_y = game.sideOne  # AI paddle position
        ball_x_speed = game.xSpeed
        ball_y_speed = game.ySpeed

        # Calculate relative positions
        distance_x = ball_x - paddle_x
        offset_y = ball_y - paddle_y

        # Normalize values
        distance_x_normalized = distance_x / game.w  # Normalize by game width
        offset_y_normalized = offset_y / game.h      # Normalize by game height
        ball_x_speed_normalized = ball_x_speed / MAX_SPEED
        ball_y_speed_normalized = ball_y_speed / MAX_SPEED

        # Optional: Include direction flags
        ball_moving_towards_paddle = 1 if ball_x_speed < 0 else 0

        state = torch.tensor([
            distance_x_normalized,
            offset_y_normalized,
            ball_x_speed_normalized,
            ball_y_speed_normalized,
            ball_moving_towards_paddle,
        ], dtype=torch.float).to(device)
        return state


    def remember(self, state, action, reward, next_state, game_done):
        action_tensor = torch.tensor(action, dtype=torch.float).to(device)
        reward_tensor = torch.tensor([reward], dtype=torch.float).to(device)
        self.memory.append((state, action_tensor, reward_tensor, next_state, game_done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, game_dones = zip(*mini_sample)

        self.trainer.train_step(states, actions, rewards, next_states, game_dones)

    def train_short_memory(self, state, action, reward, next_state, game_done):
        # Convert action and reward to tensors
        action_tensor = torch.tensor(action, dtype=torch.float).to(device)
        reward_tensor = torch.tensor([reward], dtype=torch.float).to(device)
        self.trainer.train_step([state], [action_tensor], [reward_tensor], [next_state], [game_done])


    def get_action(self, state, game):
        # Exploration vs Exploitation
        self.epsilon = max(0.01, self.epsilon * 0.995)  # Exponential decay
        final_move = [0, 0]

        if 2 < self.epsilon:
            # Exploration: Random move
            move = random.randint(0, 1)
            final_move[move] = 1
        else:
            # Fallback to model prediction if no action found
            prediction = self.model(state)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move

def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = Pong(visualize=True)
    try:
        while True:
            # Get the old state
            state_old = agent.get_state(game)

            # Get the move
            final_move = agent.get_action(state_old, game)

            # Perform the move and get new state
            reward, is_game_over, score = game.run_one_frame(final_move)
            state_new = agent.get_state(game)
            # Train short memory
            agent.train_short_memory(state_old, final_move, reward, state_new, is_game_over)

            # Remember
            agent.remember(state_old, final_move, reward, state_new, is_game_over)

            if is_game_over:
                # Train long memory (replay memory), plot result
                game.reset()
                agent.n_games += 1
                agent.train_long_memory()

                if score > record:
                    record = score
                    print("Saving AI Model")
                    agent.model.save()
                    print("Model Saved")

                print('Game', agent.n_games, 'Score', score, 'Record', record)

                plot_scores.append(score)
                total_score += score
                mean_score = total_score / agent.n_games
                plot_mean_scores.append(mean_score)
                plot(plot_scores, plot_mean_scores)
    except KeyboardInterrupt or SystemExit:
        print("Training interrupted by user.")
        agent.model.save('model_final.pth')
        print("Model saved before exiting.")
        sys.exit()

if __name__ == '__main__':
    train()
