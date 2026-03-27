# Helpify AI - Quick Setup Guide



### Directory Structure
```
├── index.html                   ← OPEN THIS FILE IN YOUR BROWSER
├── README.md                    ← Full documentation
├── css/
│   └── styles.css              ← All styling (separated from HTML)
├── js/
│   ├── app.js                  ← Main app entry point
│   ├── state.js                ← State management
│   ├── api.js                  ← API integration with fallback
│   ├── ml.js                   ← Machine learning & Q-Learning
│   ├── ui.js                   ← UI rendering & visualization
│   └── chat.js                 ← Chat handler
├── config/
│   └── config.json             ← Settings (intents, RL params)
├── data/
│   └── responses.json          ← Response templates & features
└── lib/, assets/               ← (For future use)
```

## Getting Started (3 Steps!)

### Step 1: Open in Browser
- Open `index.html` directly in your browser (Chrome, Firefox, Safari, Edge)
- You should see the Helpify AI interface load immediately

### Step 2: Test It Out
- Click any "Quick Prompt" button (e.g., "Say hello")
- Type your own message
- Watch the ML Pipeline animate
- See your intent get classified

### Step 3: (Optional) Add Your Claude API Key
To use real AI responses instead of templates:
1. Get API key from https://console.anthropic.com
2. Open browser console (F12 → Console tab)
3. Paste this (replace with your actual key):
   ```javascript
   App.setApiKey('sk-your-anthropic-api-key-here')
   ```
4. Press Enter and start chatting!

## File Organization Breakdown

### Frontend Files (Working Code)
- **index.html** - Main UI structure
- **js/app.js** - Initializes everything
- **js/state.js** - Manages conversation data
- **js/chat.js** - Handles messages
- **js/api.js** - Calls Claude AI or uses mock responses
- **js/ml.js** - Q-Learning algorithm
- **js/ui.js** - Charts, animations, rendering

### Configuration Files
- **config/config.json** - All settings (customize here!)
- **data/responses.json** - Response templates & NLP features

### Styling
- **css/styles.css** - Complete theme (dark mode theme)

## Key Features

✅ **Works immediately** - No npm install, no build step
✅ **Mock responses** - Fully functional without API key
✅ **Real AI** - Optional Claude integration
✅ **ML Visualization** - See the pipeline animate
✅ **Analytics** - Reward curves, intent distribution
✅ **Q-Learning** - Reinforcement learning agent learns

## What's Different From Original

| Before | Now |
|--------|-----|
| 1 giant HTML file | 7 focused JS modules |
| CSS embedded in HTML | Separate css/styles.css |
| Hard to modify | Easy config via JSON |
| Limited functionality | Full mock mode support |
| No fallback | Graceful API failures |

## Customization Quick Tips

### Add More Intents
Edit `config/config.json`:
```json
"intents": [
  "booking_request",
  "technical_support",
  "billing_issue"
]
```

Add responses in `data/responses.json`:
```json
"booking_request": {
  "templates": ["I can help with bookings..."],
  "actions": ["ask_clarification", "provide_solution"],
  "reward": 2
}
```

### Adjust Learning Rate
In `config/config.json`:
```json
"rl": {
  "learningRate": 0.15,    ← Lower = more conservative learning
  "gamma": 0.85,           ← Lower = more focus on immediate reward
  "epsilon": 0.2           ← Lower = more exploitation vs exploration
}
```

## Testing Different Scenarios

Try these inputs to test different intents:
- "Hello!" → greeting
- "Where's my order?" → order_status
- "I want a refund" → refund_request
- "Your service sucks!" → complaint
- "How much does X cost?" → product_inquiry
- "Cancel my order" → cancel_order
- "My package hasn't arrived" → shipping_issue
- "I can't log in" → account_issue

## Troubleshooting

**Problem**: Page is blank
- **Solution**: Make sure you opened index.html (not helpify-ai.html)

**Problem**: Messages don't send
- **Solution**: Check browser console (F12) for JavaScript errors

**Problem**: Charts don't appear
- **Solution**: Try refreshing the page

**Problem**: Want to use real API but getting errors
- **Solution**: Verify API key is valid and hasn't expired

## Project is Now:

✅ **Modular** - Easy to understand and modify
✅ **Maintainable** - Clear separation of concerns
✅ **Scalable** - Can add more features without chaos
✅ **Professional** - Proper project structure
✅ **Documented** - Code is organized and readable

## Next Steps You Could Do

1. Add a backend server for persistence
2. Connect to real NLP models (tensorflow.js)
3. Add user authentication
4. Build admin dashboard
5. Deploy to web hosting
6. Add more intents/responses
7. Implement actual knowledge base
8. Add voice chat support

## Need Help?

1. Check README.md for full documentation
2. Look at config examples in config/config.json
3. Check browser console (F12) for error messages
4. All JS modules have clear comments

**You're all set!** Open index.html and enjoy your fully functional Helpify AI! 🚀
