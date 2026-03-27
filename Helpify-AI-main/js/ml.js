// Machine Learning & Reinforcement Learning Module
const ML = {
  config: null,

  init(config) {
    this.config = config;
  },

  // Epsilon-greedy action selection
  selectAction(intent, suggestedAction) {
    const state = State;
    if (Math.random() < state.epsilon) {
      // Explore: random action
      const randomIdx = Math.floor(Math.random() * this.config.actions.length);
      return this.config.actions[randomIdx];
    } else {
      // Exploit: best action
      return suggestedAction;
    }
  },

  // Q-Learning update
  updateQ(intent, action, reward) {
    const state = State;
    const lr = this.config.rl.learningRate;
    const gamma = this.config.rl.gamma;

    const oldQ = state.qTable[intent][action] || 0;
    const bestNextQ = Math.max(...Object.values(state.qTable[intent]));
    
    state.qTable[intent][action] = oldQ + lr * (reward + gamma * bestNextQ - oldQ);

    // Decay epsilon
    state.epsilon = Math.max(
      this.config.rl.epsilonMin,
      state.epsilon * this.config.rl.epsilonDecay
    );
  },

  // Get best action for intent
  getBestAction(intent) {
    const state = State;
    const qValues = state.qTable[intent];
    let bestAction = this.config.actions[0];
    let bestValue = qValues[bestAction] || 0;

    for (const action of this.config.actions) {
      if ((qValues[action] || 0) > bestValue) {
        bestValue = qValues[action];
        bestAction = action;
      }
    }

    return bestAction;
  },

  // Get Q-table summary
  getQTableSummary() {
    const state = State;
    return Array.from(state.seen).map(intent => {
      const bestAction = this.getBestAction(intent);
      return {
        intent,
        action: bestAction,
        qValue: state.qTable[intent][bestAction] || 0
      };
    }).sort((a, b) => b.qValue - a.qValue);
  },

  // Calculate metrics
  getMetrics() {
    const state = State;
    const userMsgCount = state.msgs.filter(m => m.role === 'user').length;
    
    return {
      totalMessages: userMsgCount,
      avgReward: state.rewards.length ? (state.rewards.reduce((a, b) => a + b) / state.rewards.length).toFixed(1) : 0,
      successRate: userMsgCount ? Math.round((state.success / userMsgCount) * 100) : 0,
      intentsFound: state.seen.size,
      totalReward: state.totalReward,
      episodes: state.episodes,
      epsilon: state.epsilon.toFixed(3)
    };
  }
};
