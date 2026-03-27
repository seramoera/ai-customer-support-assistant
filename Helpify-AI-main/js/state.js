// State Management for Helpify AI
const State = {
  msgs: [],
  intentCounts: {},
  rewards: [],
  totalReward: 0,
  episodes: 0,
  success: 0,
  seen: new Set(),
  busy: false,
  qTable: {},
  epsilon: 0.3,
  config: null,
  responses: null,

  init(config, responses) {
    this.config = config;
    this.responses = responses;
    this.epsilon = config.rl.epsilon;
    
    // Initialize Q-Table
    config.intents.forEach(intent => {
      this.qTable[intent] = {};
      config.actions.forEach(action => {
        this.qTable[intent][action] = Math.random() * config.rl.initialQValue;
      });
    });
  },

  reset() {
    this.msgs = [];
    this.intentCounts = {};
    this.rewards = [];
    this.totalReward = 0;
    this.episodes = 0;
    this.success = 0;
    this.seen = new Set();
    this.epsilon = this.config.rl.epsilon;
    
    this.config.intents.forEach(intent => {
      this.qTable[intent] = {};
      this.config.actions.forEach(action => {
        this.qTable[intent][action] = Math.random() * this.config.rl.initialQValue;
      });
    });
  },

  addMessage(role, content) {
    this.msgs.push({ role, content });
  },

  incrementIntentCount(intent) {
    this.intentCounts[intent] = (this.intentCounts[intent] || 0) + 1;
  },

  addReward(reward) {
    this.rewards.push(reward);
    this.totalReward += reward;
    this.episodes++;
    if (reward > 0) this.success++;
  },

  recordIntent(intent) {
    this.seen.add(intent);
  }
};
