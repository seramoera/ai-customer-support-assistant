// API Handler for Claude AI and Fallback
const API = {
  config: null,
  responses: null,
  useMock: false,

  init(config, responses) {
    this.config = config;
    this.responses = responses;
    
    // Check if API key is available
    const apiKey = localStorage.getItem('ANTHROPIC_API_KEY');
    this.useMock = !apiKey;
  },

  async callClaude(text, history) {
    if (this.useMock) {
      return this.getMockResponse(text);
    }

    const apiKey = localStorage.getItem('ANTHROPIC_API_KEY');
    const sys = `You are Helpify AI, an intelligent customer support assistant. For EVERY message, respond ONLY with valid JSON:
{"intent":"<one of 8 intent classes>","intent_confidence":<0.65-0.99>,"cnn_features":["<3 key features>"],"rl_action":"<one of 6 actions>","rl_reward":<2|1|-1|-2>,"response":"<warm helpful reply>","model_metrics":{"accuracy":<0.87-0.97>,"macro_f1":<0.82-0.95>}}`;

    try {
      const resp = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': apiKey
        },
        body: JSON.stringify({
          model: this.config.api.model,
          max_tokens: this.config.api.maxTokens,
          system: sys,
          messages: [...history.slice(-6), { role: 'user', content: text }]
        })
      });

      if (!resp.ok) {
        throw new Error(`API error ${resp.status}: ${resp.statusText}`);
      }

      const data = await resp.json();
      return JSON.parse(data.content[0].text.trim());
    } catch (error) {
      console.error('API Error:', error);
      return this.getMockResponse(text);
    }
  },

  getMockResponse(text) {
    const intent = this.detectIntent(text);
    const intentData = this.responses.responses[intent];
    const action = intentData.actions[Math.floor(Math.random() * intentData.actions.length)];
    
    return {
      intent,
      intent_confidence: 0.85 + Math.random() * 0.14,
      cnn_features: intentData.features || ["feature1", "feature2", "feature3"],
      rl_action: action,
      rl_reward: intentData.reward || 1,
      response: intentData.templates[Math.floor(Math.random() * intentData.templates.length)],
      model_metrics: {
        accuracy: 0.87 + Math.random() * 0.1,
        macro_f1: 0.82 + Math.random() * 0.13
      }
    };
  },

  detectIntent(text) {
    const lowerText = text.toLowerCase();
    const intents = this.config.intents;
    const features = this.responses.features;

    for (const intent of intents) {
      const keywords = features[intent] || [];
      if (keywords.some(keyword => lowerText.includes(keyword))) {
        return intent;
      }
    }

    // Default to most common
    return 'greeting';
  },

  setApiKey(key) {
    localStorage.setItem('ANTHROPIC_API_KEY', key);
    this.useMock = false;
  },

  clearApiKey() {
    localStorage.removeItem('ANTHROPIC_API_KEY');
    this.useMock = true;
  }
};
