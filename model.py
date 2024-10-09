import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os
import numpy

# Device configuration
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class Linear_QNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(Linear_QNet, self).__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x

    def save(self, file_name='model.pth'):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)

class QTrainer:
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_step(self, states, actions, rewards, next_states, dones):
        # Stack tensors for batch processing
        states = torch.stack(states).to(device)           # Shape: [batch_size, state_size]
        actions = torch.stack(actions).to(device)         # Shape: [batch_size, action_size]
        rewards = torch.stack(rewards).to(device)         # Shape: [batch_size, 1]
        next_states = torch.stack(next_states).to(device) # Shape: [batch_size, state_size]
        dones = torch.tensor(dones, dtype=torch.bool).to(device)  # Shape: [batch_size]

        # 1: Predicted Q values with current state
        pred = self.model(states)  # Shape: [batch_size, output_size]

        # 2: Predicted Q values with next state
        with torch.no_grad():
            target_next = self.model(next_states)  # Shape: [batch_size, output_size]

        # 3: Compute target Q values
        target = pred.clone()
        for idx in range(len(dones)):
            Q_new = rewards[idx]
            if not dones[idx]:
                Q_new = rewards[idx] + self.gamma * torch.max(target_next[idx])
            # Update the Q value for the action taken
            action_index = torch.argmax(actions[idx]).item()
            target[idx][action_index] = Q_new

        # 4: Backpropagation
        self.optimizer.zero_grad()
        loss = self.criterion(pred, target)
        loss.backward()
        self.optimizer.step()