// Main Application Entry Point
const App = {
  config: null,
  responses: null,

  async init() {
    try {
      // Load configuration
      const configResp = await fetch('./config/config.json');
      this.config = await configResp.json();

      // Load response templates
      const responsesResp = await fetch('./data/responses.json');
      this.responses = await responsesResp.json();

      // Initialize all modules
      State.init(this.config, this.responses);
      API.init(this.config, this.responses);
      ML.init(this.config);
      UI.init(this.config);

      // Setup event listeners
      this.setupEventListeners();

      // Initial render
      UI.drawChart();
      UI.updateStats();
      document.getElementById('user-input').focus();

      console.log('✓ Helpify AI initialized successfully');
    } catch (error) {
      console.error('Failed to initialize app:', error);
      alert('Failed to initialize Helpify AI. Please check the console.');
    }
  },

  setupEventListeners() {
    // Chat input
    const inputEl = document.getElementById('user-input');
    if (inputEl) {
      inputEl.addEventListener('keydown', (e) => Chat.handleKeydown(e));
      inputEl.addEventListener('input', (e) => Chat.resize(e.target));
    }

    // Send button
    const sendBtn = document.getElementById('send-btn');
    if (sendBtn) {
      sendBtn.addEventListener('click', () => Chat.send());
    }

    // Intent rows
    document.querySelectorAll('.intent-row').forEach(row => {
      row.addEventListener('click', () => {
        const intent = row.dataset.intent;
        if (intent) {
          const messages = State.msgs.filter((m, i) => {
            if (m.role === 'assistant') {
              // Find corresponding user message before this
              for (let j = i - 1; j >= 0; j--) {
                if (State.msgs[j].role === 'user') return false;
              }
              return true;
            }
            return false;
          });
        }
      });
    });

    // Clear button
    const clearBtn = document.querySelector('.clear-btn');
    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        if (confirm('Clear all messages and reset state?')) {
          Chat.clearAll();
        }
      });
    }

    // Quick prompts
    document.querySelectorAll('.qprompt').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const text = e.target.textContent.trim().split('\n')[0];
        const prompts = {
          'Say hello': 'Hello, I need some help!',
          'Track an order': 'Where is my order #12345?',
          'Request a refund': 'I would like a refund for my order',
          'Cancel an order': 'I want to cancel my order immediately',
          'Shipping problem': 'My package has not arrived after 3 weeks',
          'Product inquiry': 'Can you tell me about your enterprise pricing?',
          'Account issue': 'I am unable to log into my account'
        };
        const text_to_send = prompts[btn.textContent.trim()] || text;
        Chat.fillInput(text_to_send);
      });
    });

    // Window resize
    window.addEventListener('resize', () => UI.drawChart());
  },

  // Set API key
  setApiKey(key) {
    API.setApiKey(key);
    console.log('✓ API key set. Now using live Claude API');
  },

  // Check if using mock
  isUsingMock() {
    return API.useMock;
  }
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  App.init();
});
