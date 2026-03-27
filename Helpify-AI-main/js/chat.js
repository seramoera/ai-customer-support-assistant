// Chat Handler - manages message flow and interactions
const Chat = {
  async send() {
    const inputEl = document.getElementById('user-input');
    const text = inputEl.value.trim();

    if (!text || State.busy) return;

    State.busy = true;
    document.getElementById('send-btn').disabled = true;
    inputEl.value = '';
    inputEl.style.height = 'auto';

    // Add user message to UI and state
    UI.addUserMessage(text);
    State.addMessage('user', text);

    // Animate pipeline and show typing
    UI.animatePipeline();
    UI.addTyping();

    try {
      // Get AI response
      const history = State.msgs.slice(0, -1);
      const response = await API.callClaude(text, history);

      // Select action with RL
      response.rl_action = ML.selectAction(response.intent, response.rl_action);

      // Update Q-table
      ML.updateQ(response.intent, response.rl_action, response.rl_reward);

      // Update state
      State.incrementIntentCount(response.intent);
      State.addReward(response.rl_reward);
      State.recordIntent(response.intent);
      State.addMessage('assistant', response.response);

      // Update UI
      document.querySelectorAll('.intent-row').forEach(c => c.classList.remove('active'));
      document.querySelector(`[data-intent="${response.intent}"]`)?.classList.add('active');

      const countEl = document.getElementById(`cnt-${response.intent}`);
      if (countEl) countEl.textContent = State.intentCounts[response.intent];

      // Update model metrics
      if (response.model_metrics) {
        document.getElementById('macc').textContent = (response.model_metrics.accuracy * 100).toFixed(1) + '%';
        document.getElementById('mf1').textContent = response.model_metrics.macro_f1.toFixed(3);
      }

      // Render response and update charts
      UI.addAIMessage(response);
      UI.addActionLog(response);
      UI.drawIntentBars();
      UI.drawChart();
      UI.drawQTable();
      UI.updateStats();
    } catch (error) {
      console.error('Error:', error);
      document.getElementById('typing')?.remove();
      const div = document.createElement('div');
      div.className = 'msg ai';
      div.innerHTML = `
        <div class="msg-av"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg></div>
        <div class="msg-body"><div class="bubble" style="border-color:rgba(244,63,94,0.3);color:#fca5a5">Connection error: ${UI.escape(error.message)}</div></div>
      `;
      document.getElementById('messages').appendChild(div);
      UI.scrollDown();
    }

    State.busy = false;
    document.getElementById('send-btn').disabled = false;
    inputEl.focus();
  },

  fillInput(text) {
    const inputEl = document.getElementById('user-input');
    inputEl.value = text;
    this.resize(inputEl);
    inputEl.focus();
  },

  resize(el) {
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 120) + 'px';
  },

  handleKeydown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.send();
    }
  },

  clearAll() {
    State.reset();
    UI.reset();
  }
};
