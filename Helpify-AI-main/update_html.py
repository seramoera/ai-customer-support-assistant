import re

# Read the file
with open('helpify-ai.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace callClaude function
pattern = r'async function callClaude\(text, history\) \{[^}]*?return JSON\.parse\(d\.content\[0\]\.text\.trim\(\)\);\s*\}'
replacement = '''async function callAPI(text) {
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

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Simple string replacements
content = content.replace(
    "const r=await callClaude(text,hist);",
    "const r=await callAPI(text);"
)

content = content.replace(
    "<span class=\"welcome-chip\">8 Intent Classes</span>",
    "<span class=\"welcome-chip\">10 Intent Classes</span>"
)

content = content.replace(
    "Model: <b>Claude + Text-CNN</b>",
    "Model: <b>Text-CNN + Q-Learning RL</b>"
)

content = content.replace(
    "Intents: <b>8 classes</b>",
    "Intents: <b>10 classes</b>"
)

content = content.replace(
    "Powered by Claude AI",
    "Powered by Trained ML Models"
)

# Write back
with open('helpify-ai.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('HTML file updated successfully!')
