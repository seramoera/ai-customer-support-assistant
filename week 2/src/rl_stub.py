import random

class RLEnvironment:
    def __init__(self):
        self.states = ["message_1", "message_2"]
        self.actions = ["reply_good", "reply_bad"]

    def step(self, action):
        reward = 1 if action == "reply_good" else -1
        next_state = random.choice(self.states)
        done = False
        return next_state, reward, done

# Simulate a few episodes
env = RLEnvironment()
state = random.choice(env.states)
for episode in range(3):
    action = random.choice(env.actions)
    next_state, reward, done = env.step(action)
    print(f"Episode {episode+1} | State: {state}, Action: {action}, Reward: {reward}")
    state = next_state