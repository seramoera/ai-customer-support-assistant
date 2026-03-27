# API Configuration

## Using Claude API

### Method 1: Browser Console (Development)
```javascript
// Open browser console (F12 → Console)
App.setApiKey('sk-your-api-key-here')
```

### Method 2: LocalStorage (Persistent)
```javascript
// In console, run once:
localStorage.setItem('ANTHROPIC_API_KEY', 'sk-your-api-key-here')

// Next time you load the app, it will use this key
```

### Method 3: Environment File (Backend Setup)
For future backend integration, create a `.env` file:
```
ANTHROPIC_API_KEY=sk-your-api-key-here
CLAUDE_MODEL=claude-sonnet-4-20250514
```

## Getting Your API Key

1. Go to https://console.anthropic.com/account/keys
2. Sign in or create an account
3. Create a new API key
4. Copy the key (starts with `sk-`)
5. Use it in one of the methods above

## Security Notes

⚠️ **DO NOT** commit your API key to git
⚠️ **DO NOT** share your API key publicly
⚠️ For production, use a backend server to handle API calls
⚠️ The `.gitignore` file will protect your `.env` files

## Testing Without API Key

The app works perfectly with mock responses!
- All intents are recognized
- Responses are realistic
- Analytics work fully
- No API key needed

Switch to real API anytime using `App.setApiKey()`

## Monitoring API Usage

1. Visit https://console.anthropic.com/account/usage
2. Check your daily/monthly token usage
3. Set up billing alerts if needed

## Rate Limits

Default Claude API limits (per plan):
- Free tier: Limited requests
- Pro: Higher limits
- Enterprise: Custom limits

Check your plan at: https://console.anthropic.com/account/plans
