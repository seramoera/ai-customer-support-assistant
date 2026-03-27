"""
Q-Learning Reinforcement Learning Agent
Learns to select best response actions based on predicted intents
"""

import numpy as np
import json
import logging
from typing import Dict, Tuple, List
from pathlib import Path

logger = logging.getLogger(__name__)


class QLearningAgent:
    """
    Q-Learning Agent for Response Selection
    
    State: Intent predicted by NLP model
    Actions: 6 possible response types
    Reward: +2 (good) to -2 (bad) based on user feedback
    Goal: Learn optimal action for each intent
    """
    
    ACTIONS = [
        "ask_order_id",          # Request order information
        "provide_solution",      # Provide direct solution
        "escalate_human",        # Transfer to human agent
        "give_faq",              # Provide FAQ
        "ask_clarification",     # Ask for more details
        "apologize_and_help"     # Show empathy
    ]
    
    def __init__(
        self,
        num_states: int = 8,  # 8 intents
        learning_rate: float = 0.1,
        discount_factor: float = 0.9,
        exploration_rate: float = 0.3,
        exploration_decay: float = 0.995
    ):
        """
        Initialize Q-Learning Agent
        
        Args:
            num_states: Number of intent states
            learning_rate: Alpha parameter
            discount_factor: Gamma parameter
            exploration_rate: Epsilon for epsilon-greedy
            exploration_decay: Decay rate for exploration
        """
        self.num_states = num_states
        self.num_actions = len(self.ACTIONS)
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        
        # Initialize Q-table: (states, actions)
        self.q_table = np.random.normal(0, 0.1, (num_states, self.num_actions))
        
        # Statistics
        self.episode_count = 0
        self.total_reward = 0
        self.episode_rewards = []
        self.success_count = 0
    
    def select_action(self, state: int, training: bool = True) -> int:
        """
        Select action using epsilon-greedy strategy
        
        Args:
            state: Current state (intent index)
            training: If True, use exploration; if False, use greedy
        
        Returns:
            action_index: Selected action index
        """
        if training and np.random.rand() < self.exploration_rate:
            # Exploration: random action
            action = np.random.randint(0, self.num_actions)
        else:
            # Exploitation: best action from Q-table
            action = np.argmax(self.q_table[state])
        
        return action
    
    def update_quality(self, state: int, action: int, reward: float, next_state: int = None):
        """
        Update Q-value using Q-Learning formula:
        Q(s,a) = Q(s,a) + α * [r + γ * max Q(s',a') - Q(s,a)]
        
        Args:
            state: Current state
            action: Taken action
            reward: Reward received
            next_state: Next state (optional)
        """
        if next_state is None:
            next_state = state
        
        # Current Q-value
        current_q = self.q_table[state, action]
        
        # Maximum Q-value in next state
        max_next_q = np.max(self.q_table[next_state])
        
        # Q-Learning update
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        
        self.q_table[state, action] = new_q
        
        # Update statistics
        self.total_reward += reward
        if reward > 0:
            self.success_count += 1
    
    def step(self, state: int, reward: float) -> int:
        """
        One step of training
        
        Args:
            state: Intent state
            reward: Reward from environment
        
        Returns:
            action: Action taken
        """
        # Select and store action
        action = self.select_action(state, training=True)
        
        # Update Q-value
        self.update_quality(state, action, reward)
        
        # Decay exploration rate
        self.exploration_rate *= self.exploration_decay
        self.exploration_rate = max(0.05, self.exploration_rate)
        
        return action
    
    def train(self, episodes: int = 1000, intents: List[int] = None) -> Dict:
        """
        Train the agent
        
        Args:
            episodes: Number of training episodes
            intents: List of intent states to sample from
        
        Returns:
            training_history: Dictionary with metrics
        """
        if intents is None:
            intents = list(range(self.num_states))
        
        history = {
            "episode_rewards": [],
            "average_reward": [],
            "success_rate": []
        }
        
        for episode in range(episodes):
            # Sample random state
            state = np.random.choice(intents)
            
            # Simulate reward (in production, would be from user feedback)
            # Reward probability: 70% positive, 20% neutral, 10% negative
            rand = np.random.rand()
            if rand < 0.7:
                reward = np.random.choice([1, 2])
            elif rand < 0.9:
                reward = 0
            else:
                reward = np.random.choice([-1, -2])
            
            # Train step
            self.step(state, reward)
            
            self.episode_rewards.append(reward)
            
            # Log progress
            if (episode + 1) % 100 == 0:
                avg_reward = np.mean(self.episode_rewards[-100:])
                success_rate = np.sum(np.array(self.episode_rewards[-100:]) > 0) / 100
                
                history["episode_rewards"].append(reward)
                history["average_reward"].append(avg_reward)
                history["success_rate"].append(success_rate)
                
                logger.info(
                    f"Episode {episode+1}/{episodes} | "
                    f"Avg Reward: {avg_reward:.3f} | "
                    f"Success Rate: {success_rate:.1%} | "
                    f"Epsilon: {self.exploration_rate:.3f}"
                )
        
        self.episode_count = episodes
        logger.info("Training complete!")
        
        return history
    
    def get_best_actions(self) -> Dict[int, str]:
        """Get best action for each state"""
        best_actions = {}
        for state in range(self.num_states):
            best_action = np.argmax(self.q_table[state])
            best_actions[state] = self.ACTIONS[best_action]
        return best_actions
    
    def get_q_values(self, state: int) -> Dict[str, float]:
        """Get all Q-values for a state"""
        q_values = {}
        for action_id, action_name in enumerate(self.ACTIONS):
            q_values[action_name] = float(self.q_table[state, action_id])
        return q_values
    
    def get_statistics(self) -> Dict:
        """Get training statistics"""
        if len(self.episode_rewards) == 0:
            return {}
        
        return {
            "total_episodes": self.episode_count,
            "total_reward": float(self.total_reward),
            "average_reward": float(self.total_reward / max(1, self.episode_count)),
            "success_count": self.success_count,
            "success_rate": float(self.success_count / max(1, self.episode_count)),
            "exploration_rate": float(self.exploration_rate),
            "recent_avg_reward": float(np.mean(self.episode_rewards[-100:]))
        }
    
    def save(self, filepath: str):
        """Save agent to file"""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "q_table": self.q_table.tolist(),
            "episode_count": self.episode_count,
            "total_reward": float(self.total_reward),
            "success_count": self.success_count,
            "exploration_rate": float(self.exploration_rate),
            "learning_rate": float(self.learning_rate),
            "discount_factor": float(self.discount_factor),
            "episode_rewards": [float(x) for x in self.episode_rewards[-1000:]]  # Convert numpy types
        }
        
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Agent saved to {filepath}")
    
    def load(self, filepath: str):
        """Load agent from file"""
        filepath = Path(filepath)
        
        with open(filepath, "r") as f:
            data = json.load(f)
        
        self.q_table = np.array(data["q_table"])
        self.episode_count = data["episode_count"]
        self.total_reward = data["total_reward"]
        self.success_count = data["success_count"]
        self.exploration_rate = data["exploration_rate"]
        self.episode_rewards = data["episode_rewards"]
        
        logger.info(f"Agent loaded from {filepath}")


if __name__ == "__main__":
    # Test Q-Learning Agent
    logging.basicConfig(level=logging.INFO)
    
    agent = QLearningAgent(
        num_states=8,
        learning_rate=0.1,
        discount_factor=0.9,
        exploration_rate=0.3
    )
    
    # Train
    history = agent.train(episodes=1000)
    
    # Get statistics
    stats = agent.get_statistics()
    print("\nTraining Statistics:")
    print(json.dumps(stats, indent=2))
    
    # Get best actions
    print("\nBest Action for Each Intent:")
    best_actions = agent.get_best_actions()
    intents = ["greeting", "order_status", "refund_request", "complaint",
               "product_inquiry", "cancel_order", "shipping_issue", "account_issue"]
    for state, intent in enumerate(intents):
        print(f"  {intent}: {best_actions[state]}")
