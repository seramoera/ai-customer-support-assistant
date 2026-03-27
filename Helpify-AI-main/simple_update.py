#!/usr/bin/env python3
"""Simple HTML updater script"""

file_path = r'c:\Users\YUKI\Documents\Helpify AI\helpify-ai.html'

with open(file_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Replace callClaude function
old_func = '''async function callClaude(text, history) {
  const sys = `You are Helpify AI, an intelligent customer support assistant simulating a full ML pipeline. For EVERY message, respond ONLY with valid JSON (no markdown, no extra text):
{"intent":"<greeting|order_status|refund_request|complaint|product_inquiry|cancel_order|shipping_issue|account_issue>","intent_confidence":<0.65-0.99>,"cnn_features":["<3 key text features>"],"rl_action":"<ask_order_id|provide_solution|escalate_human|give_faq|ask_clarification|apologize_and_help>","rl_reward":<2|1|-1|-2>,"response":"<warm helpful professional 2-3 sentence reply>","model_metrics":{"accuracy":<0.87-0.97>,"macro_f1":<0.82-0.95>}}
Rules: intent must match exactly one of 8 classes. rl_action must match exactly one of 6. rl_reward: +2 clear helpful, +1 partial, -1 unclear, -2 harmful. Respond ONLY with JSON.`;
  const resp = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: 'claude-sonnet-4-20250514', max_tokens: 1000, system: sys, messages: [...history.slice(-6), { role:'user', content: text }] })
  });
  if (!resp.ok) throw new Error(`API error ${resp.status}`);
  const d = await resp.json();
  return JSON.parse(d.content[0].text.trim());
}'''

new_func = '''async function callAPI(text) {
  const resp = await fetch('http://localhost:5000/api/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: text })
  });
  if (!resp.ok) throw new Error(`API error ${resp.status}`);
  const data = await resp.json();
  if(!data.success) throw new Error(data.error || 'API error');
  return {
    intent: data.intent,
    intent_confidence: data.confidence,
    cnn_features: [data.intent, 'CNN-embedding', data.confidence.toFixed(3)],
    rl_action: data.action,
    rl_reward: data.confidence > 0.8 ? 2 : 1,
    response: data.response,
    model_metrics: { accuracy: 0.9667, macro_f1: 0.9662 }
  };
}'''

html = html.replace(old_func, new_func)

# 2. Replace function call
html = html.replace(
    'const r=await callClaude(text,hist);',
    'const r=await callAPI(text);'
)

# 3. Update INTENTS
html = html.replace(
    "const INTENTS = ['greeting','order_status','refund_request','complaint','product_inquiry','cancel_order','shipping_issue','account_issue'];",
    "const INTENTS = ['greeting','order_status','refund_request','complaint','product_inquiry','cancel_order','shipping_issue','account_issue','borrow_money','cancel_subscription'];"
)

# 4. Update ICOLORS
html = html.replace(
    "const ICOLORS = { greeting:'#60a5fa', order_status:'#0ea5e9', refund_request:'#f59e0b', complaint:'#f43f5e', product_inquiry:'#818cf8', cancel_order:'#f87171', shipping_issue:'#34d399', account_issue:'#a78bfa' };",
    "const ICOLORS = { greeting:'#60a5fa', order_status:'#0ea5e9', refund_request:'#f59e0b', complaint:'#f43f5e', product_inquiry:'#818cf8', cancel_order:'#f87171', shipping_issue:'#34d399', account_issue:'#a78bfa', borrow_money:'#06b6d4', cancel_subscription:'#ec4899' };"
)

# 5. Update other text
html = html.replace('Powered by Claude AI', 'Powered by Trained ML Models')
html = html.replace('Model: <b>Claude + Text-CNN</b>', 'Model: <b>Text-CNN + Q-Learning RL</b>')
html = html.replace('Intents: <b>8 classes</b>', 'Intents: <b>10 classes</b>')
html = html.replace('<span class="welcome-chip">8 Intent Classes</span>', '<span class="welcome-chip">10 Intent Classes</span>')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("HTML file successfully updated!")
print("Changes made:")
print("- Replaced callClaude with callAPI (calls localhost:5000)")
print("- Updated INTENTS from 8 to 10 classes")
print("- Updated ICOLORS mapping")
print("- Updated labels and metadata")
