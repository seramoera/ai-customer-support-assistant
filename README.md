# Helpify AI - Customer Support Assistant

A fully functional intelligent customer support chatbot powered by Claude AI with ML visualization, NLP intent classification, and Q-Learning reinforcement learning.

## Project Structure

```
helpify-ai/
├── index.html              # Main entry point (open this in browser)
├── css/
│   └── styles.css         # All styling
├── js/
│   ├── app.js             # Main app initialization
│   ├── state.js           # State management
│   ├── api.js             # API calls & fallback responses
│   ├── ml.js              # Machine learning & RL
│   ├── ui.js              # UI rendering & charts
│   └── chat.js            # Chat message handling
├── config/
│   └── config.json        # Configuration settings
├── data/
│   └── responses.json     # Response templates & features
├── lib/                   # (For future libraries)
├── assets/                # (For future images/icons)
└── .git/                  # Version control
```

## Features

✅ **AI-Powered Chat** - Conversations with Claude AI
✅ **Intent Classification** - 8 customer support intents recognized
✅ **ML Pipeline Visualization** - Watch the processing pipeline animate
✅ **Q-Learning RL** - Reinforcement learning agent optimizes actions
✅ **Real-time Analytics** - Intent distribution, reward curves, Q-table
✅ **Mock Mode** - Works without API key (uses template responses)
✅ **Live API Mode** - Optionally connect to Claude API

## Quick Start

### 1. **Open in Browser**
Simply open `index.html` in any modern web browser. The app works immediately with mock responses.

### 2. **Enable Live Claude API (Optional)**
To use actual Claude AI responses:
1. Get an API key from [console.anthropic.com](https://console.anthropic.com)
2. In the browser console, run:
   ```javascript
   App.setApiKey('sk-your-api-key-here')
   ```
3. Start chatting - responses now come from Claude

### 3. **Test It Out**
- Click "Say hello" or any quick prompt
- Watch the ML Pipeline animate
- See intents get classified
- Track rewards in the curve
- Clear and start over with the "Clear Conversation" button

4. Alternative Local Browser Server
If you prefer running a local HTTP server:

• cd Helpify-AI-main
•  python -m http.server 8000 --bind 127.0.0.1
•	Open http://localhost:8000 in a browser



## Configuration

Edit `config/config.json` to customize:
- **Intents**: Add/remove customer support intents
- **Actions**: Add/remove RL agent actions
- **RL Settings**: Adjust epsilon, learning rate, gamma
- **UI Settings**: Animation durations, log sizes

## Response Templates

Edit `data/responses.json` to:
- Add response templates for each intent
- Define keyword features for intent detection
- Set reward values for actions
- Configure which actions work best for each intent

## Module Architecture

### `state.js`
- Centralized state management
- Tracks messages, rewards, Q-table
- Methods: `init()`, `reset()`, `addMessage()`, `addReward()`

### `api.js`
- Handles Claude API calls with fallback to mocks
- Intent detection from user text
- API key management
- Methods: `callClaude()`, `getMockResponse()`, `setApiKey()`

### `ml.js`
- Q-Learning implementation
- Epsilon-greedy action selection
- Q-value updates with learning rate & discount
- Methods: `selectAction()`, `updateQ()`, `getBestAction()`

### `ui.js`
- All DOM rendering & charts
- Canvas-based reward curve
- Message formatting with tags
- Methods: `addUserMessage()`, `addAIMessage()`, `drawChart()`, `updateStats()`

### `chat.js`
- Chat message flow
- Event handlers
- Input management
- Methods: `send()`, `fillInput()`, `handleKeydown()`

### `app.js`
- Application initialization
- Module coordination
- Event listener setup
- Methods: `init()`, `setApiKey()`, `isUsingMock()`

## How It Works

1. **User Input** → Chat box
2. **Pipeline Animates** → Shows processing steps
3. **API Call** → Claude or mock response
4. **Intent Detection** → Classifies user intent
5. **RL Action Selection** → Agent chooses best action
6. **Q-Learning Update** → Network learns from reward
7. **Response Rendered** → Shows text + metadata tags
8. **Analytics Update** → Charts and stats refresh

## Intent Classes

1. **greeting** - Hello, introductions
2. **order_status** - Where's my order?
3. **refund_request** - I want a refund
4. **complaint** - I have an issue
5. **product_inquiry** - Tell me about products
6. **cancel_order** - Cancel my order
7. **shipping_issue** - Package didn't arrive
8. **account_issue** - Account problems

## RL Agent Actions

1. `ask_order_id` - Request order identifier
2. `provide_solution` - Give direct answer
3. `escalate_human` - Transfer to human
4. `give_faq` - Provide FAQ response
5. `ask_clarification` - Ask for more details
6. `apologize_and_help` - Empathize and assist

## Reward System

| Scenario | Reward |
|----------|--------|
| Clear, helpful response | +2 |
| Partial/partial clarity | +1 |
| Unclear response | -1 |
| Harmful response | -2 |

## Keyboard Shortcuts

- **Enter** - Send message
- **Shift + Enter** - New line in textarea
- **Click quick prompts** - Fill input with template

## Troubleshooting

**Q: App doesn't respond when I click send**
- A: Check browser console for errors. Ensure config/config.json and data/responses.json load properly.

**Q: I want to use real Claude API but get errors**
- A: Make sure your API key is valid and check the network tab in devtools for HTTP errors.

**Q: Charts aren't showing**
- A: Refresh the page. The canvas needs to render after DOM is ready.

**Q: How do I train the RL agent?**
- A: Just keep chatting! The Q-table updates automatically after each message.

## Future Enhancements

- [ ] Database backend for persistence
- [ ] Multi-user support with sessions
- [ ] Custom intent/action training interface
- [ ] Export analytics as CSV/PDF
- [ ] Dark/light theme toggle
- [ ] Multi-language support
- [ ] Voice chat integration
- [ ] Real ML model integration (TensorFlow.js)


---

# **AUTHORS & CONTRIBUTIONS**

This project was collaboratively developed by the research team, with clearly defined roles across system components. Contributions are outlined below, with emphasis on primary responsibilities.

---

### **Masato Martin – Lead Developer (Modeling & Reinforcement Learning)**

* Led the **overall system development**, including core architecture design
* Designed and implemented the **Text-CNN model** for intent classification
* Developed the **Q-Learning reinforcement learning agent** for action selection
* Performed **hyperparameter tuning, training optimization, and performance improvements**
* Conducted **evaluation, ablation studies, and model analysis**
* Played the primary role in ensuring **system functionality and technical robustness**

---

### **Marielle L. Datu – NLP Pipeline & System Integration**

* Developed the **NLP preprocessing pipeline**:

  * Text cleaning, tokenization, and lemmatization
  * Feature engineering (sentiment analysis, token-based features)
* Managed **dataset preparation and validation**
* Integrated the **CNN and RL components into a unified system workflow**
* Contributed to **evaluation, documentation, and report writing**

---

### **Jasmine Magtanong – Data Preprocessing & Exploratory Analysis**

* Assisted in **data cleaning and preprocessing tasks**
* Conducted **Exploratory Data Analysis (EDA)**:

  * Intent distribution and balance checking
  * Data quality inspection
* Supported **dataset preparation for training and validation**

---

### **Ivan Louis Salamat – Testing & Reinforcement Learning Support**

* Assisted in **testing and validation of the RL component**
* Helped analyze **reward structure behavior and action outcomes**
* Contributed to **debugging and system verification**
* Supported **documentation and testing workflows**

---

# **COLLABORATIVE CONTRIBUTIONS**

All members contributed to:

* System design discussions
* Testing and validation processes
* Preparation of presentation and demonstration materials

-
## License


## Support

For issues or questions, check the browser console for detailed error messages.
