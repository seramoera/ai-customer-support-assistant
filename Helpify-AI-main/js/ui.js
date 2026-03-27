// UI Rendering & Interaction Module
const UI = {
  config: null,
  intentColors: {
    'greeting': '#60a5fa',
    'order_status': '#0ea5e9',
    'refund_request': '#f59e0b',
    'complaint': '#f43f5e',
    'product_inquiry': '#818cf8',
    'cancel_order': '#f87171',
    'shipping_issue': '#34d399',
    'account_issue': '#a78bfa'
  },

  init(config) {
    this.config = config;
  },

  // Escape HTML
  escape(text) {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\n/g, '<br>');
  },

  // Wait helper
  wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  },

  // Scroll to bottom
  scrollDown() {
    const messagesDiv = document.getElementById('messages');
    if (messagesDiv) {
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
  },

  // Add user message
  addUserMessage(text) {
    document.getElementById('welcome')?.remove();
    const div = document.createElement('div');
    div.className = 'msg user';
    div.innerHTML = `
      <div class="msg-av"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg></div>
      <div class="msg-body"><div class="bubble">${this.escape(text)}</div></div>
    `;
    document.getElementById('messages').appendChild(div);
    this.scrollDown();
  },

  // Add typing indicator
  addTyping() {
    const div = document.createElement('div');
    div.className = 'msg ai typing';
    div.id = 'typing';
    div.innerHTML = `
      <div class="msg-av"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3z"/><path d="M3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"/></svg></div>
      <div class="msg-body"><div class="bubble"><div class="d"></div><div class="d"></div><div class="d"></div></div></div>
    `;
    document.getElementById('messages').appendChild(div);
    this.scrollDown();
  },

  // Add AI response message
  addAIMessage(response) {
    document.getElementById('typing')?.remove();
    const div = document.createElement('div');
    div.className = 'msg ai';
    const sign = response.rl_reward >= 0 ? '+' : '';
    const conf = ((response.intent_confidence || 0.9) * 100).toFixed(0);

    div.innerHTML = `
      <div class="msg-av"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3z"/><path d="M3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"/></svg></div>
      <div class="msg-body">
        <div class="bubble">${this.escape(response.response)}</div>
        <div class="msg-tags">
          <span class="tag intent"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M2 12h3m14 0h3M12 2v3m0 14v3"/></svg>${response.intent}</span>
          <span class="tag action"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>${response.rl_action}</span>
          <span class="tag reward"><svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>${sign}${response.rl_reward}</span>
          <span class="tag conf">${conf}% conf</span>
        </div>
        ${response.cnn_features ? `<div class="msg-cnn">CNN features: ${response.cnn_features.join(' · ')}</div>` : ''}
      </div>
    `;
    document.getElementById('messages').appendChild(div);
    this.scrollDown();
  },

  // Update stats
  updateStats() {
    const metrics = ML.getMetrics();
    document.getElementById('total-msgs').textContent = metrics.totalMessages;
    document.getElementById('avg-reward').textContent = metrics.avgReward;
    document.getElementById('success-rate').textContent = metrics.successRate + '%';
    document.getElementById('intents-found').textContent = metrics.intentsFound;
    document.getElementById('total-rwd').textContent = metrics.totalReward;
    document.getElementById('episodes').textContent = metrics.episodes;
  },

  // Animate pipeline
  async animatePipeline() {
    for (let i = 0; i <= 5; i++) {
      document.querySelectorAll('.pipe-node').forEach(n => n.classList.remove('active'));
      document.getElementById(`pn${i}`).classList.add('active');
      await this.wait(this.config.ui.animationDuration);
    }
    await this.wait(this.config.ui.pipelineDelay);
    document.querySelectorAll('.pipe-node').forEach(n => n.classList.remove('active'));
  },

  // Draw reward chart
  drawChart() {
    const canvas = document.getElementById('rwd-canvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const W = canvas.offsetWidth || 268;
    const H = 90;

    canvas.width = W;
    canvas.height = H;
    ctx.clearRect(0, 0, W, H);

    const data = State.rewards;

    if (data.length < 2) {
      ctx.fillStyle = 'rgba(255,255,255,0.03)';
      ctx.fillRect(0, 0, W, H);
      ctx.fillStyle = 'rgba(255,255,255,0.15)';
      ctx.font = '10px JetBrains Mono';
      ctx.textAlign = 'center';
      ctx.fillText('Send messages to see reward curve', W / 2, H / 2);
      return;
    }

    const mn = Math.min(...data) - 0.5;
    const mx = Math.max(...data) + 0.5;
    const sy = v => H - 6 - ((v - mn) / (mx - mn)) * (H - 12);
    const sx = i => (i / (data.length - 1)) * W;

    // Grid
    ctx.strokeStyle = 'rgba(99,130,183,0.06)';
    ctx.lineWidth = 1;
    for (let y = 0; y <= 4; y++) {
      ctx.beginPath();
      ctx.moveTo(0, (y / 4) * H);
      ctx.lineTo(W, (y / 4) * H);
      ctx.stroke();
    }

    // Zero line
    if (mn < 0 && mx > 0) {
      const zy = sy(0);
      ctx.strokeStyle = 'rgba(99,130,183,0.15)';
      ctx.setLineDash([3, 3]);
      ctx.beginPath();
      ctx.moveTo(0, zy);
      ctx.lineTo(W, zy);
      ctx.stroke();
      ctx.setLineDash([]);
    }

    // Gradient fill
    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, 'rgba(14,165,233,0.25)');
    g.addColorStop(1, 'rgba(14,165,233,0)');

    ctx.beginPath();
    ctx.moveTo(sx(0), H);
    data.forEach((v, i) => ctx.lineTo(sx(i), sy(v)));
    ctx.lineTo(sx(data.length - 1), H);
    ctx.closePath();
    ctx.fillStyle = g;
    ctx.fill();

    // Line
    ctx.beginPath();
    ctx.strokeStyle = '#38bdf8';
    ctx.lineWidth = 2;
    ctx.lineJoin = 'round';
    data.forEach((v, i) => {
      if (i === 0) ctx.moveTo(sx(i), sy(v));
      else ctx.lineTo(sx(i), sy(v));
    });
    ctx.stroke();

    // Points
    data.forEach((v, i) => {
      ctx.beginPath();
      ctx.arc(sx(i), sy(v), 3, 0, Math.PI * 2);
      ctx.fillStyle = v >= 2 ? '#10d9a8' : v >= 1 ? '#f59e0b' : '#f43f5e';
      ctx.fill();
    });
  },

  // Draw intent bars
  drawIntentBars() {
    const total = Object.values(State.intentCounts).reduce((a, b) => a + b, 0);
    const container = document.getElementById('intent-bars');
    
    if (!total) {
      container.innerHTML = '<div class="empty-state">No data yet</div>';
      return;
    }

    const sorted = Object.entries(State.intentCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 6);

    container.innerHTML = sorted.map(([intent, count]) => `
      <div class="ibar-row">
        <div class="ibar-hd">${intent}<span>${((count / total) * 100).toFixed(0)}%</span></div>
        <div class="ibar-track"><div class="ibar-fill" style="width:${(count / total) * 100}%;background:${this.intentColors[intent] || '#60a5fa'}"></div></div>
      </div>
    `).join('');
  },

  // Draw Q-Table
  drawQTable() {
    const tbody = document.getElementById('qtbody');
    const rows = ML.getQTableSummary();

    if (!rows.length) {
      tbody.innerHTML = '<tr><td colspan="3" class="empty-state">Waiting for interactions…</td></tr>';
      return;
    }

    tbody.innerHTML = rows.map(r => `
      <tr>
        <td style="color:${this.intentColors[r.intent] || '#60a5fa'}">${r.intent}</td>
        <td>${r.action}</td>
        <td class="qv top">${r.qValue.toFixed(3)}</td>
      </tr>
    `).join('');
  },

  // Add action log entry
  addActionLog(response) {
    const log = document.getElementById('alog');
    log.querySelector('.empty-state')?.remove();

    const div = document.createElement('div');
    div.className = 'alog-entry';
    const isPositive = response.rl_reward > 0;

    div.innerHTML = `
      <div class="alog-hd">
        <span class="alog-intent">${response.intent}</span>
        <span class="alog-time">${new Date().toLocaleTimeString()}</span>
      </div>
      <div class="alog-action">
        ${response.rl_action}
        <span class="rpill ${isPositive ? 'pos' : 'neg'}">${isPositive ? '+' : ''}${response.rl_reward}</span>
      </div>
    `;

    log.insertBefore(div, log.firstChild);
    while (log.children.length > this.config.ui.maxActionLogs) {
      log.lastChild.remove();
    }
  },

  // Reset UI
  reset() {
    document.getElementById('messages').innerHTML = `
      <div class="welcome" id="welcome">
        <div class="welcome-icon">
          <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3z"/><path d="M3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"/>
          </svg>
        </div>
        <h1>Welcome to Helpify AI</h1>
        <p>An intelligent customer support assistant powered by deep learning intent classification and reinforcement learning. How can I help you today?</p>
        <div class="welcome-chips">
          <span class="welcome-chip">NLP Classification</span>
          <span class="welcome-chip">Text-CNN Model</span>
          <span class="welcome-chip">Q-Learning RL</span>
          <span class="welcome-chip">8 Intent Classes</span>
        </div>
      </div>
    `;

    document.querySelectorAll('.intent-row').forEach(c => c.classList.remove('active'));
    document.querySelector('[data-intent="greeting"]')?.classList.add('active');
    document.querySelectorAll('[id^="cnt-"]').forEach(e => e.textContent = '0');
    document.getElementById('alog').innerHTML = '<div class="empty-state">No actions yet</div>';
    document.getElementById('intent-bars').innerHTML = '<div class="empty-state">No data yet</div>';
    document.getElementById('qtbody').innerHTML = '<tr><td colspan="3" class="empty-state">Waiting for interactions…</td></tr>';
    document.getElementById('macc').textContent = '—';
    document.getElementById('mf1').textContent = '—';

    this.drawChart();
    this.updateStats();
  }
};
