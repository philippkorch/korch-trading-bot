# Quick Start Guide (5 Minutes)

Get Korch Trading Bot running in 5 minutes.

## What You Need

- Telegram account
- TradingView account
- GitHub account
- 5 minutes

## Step 1: Telegram Setup (2 min)

### Create Bot Token

1. Open Telegram
2. Search → @BotFather
3. Send `/newbot`
4. Name: "Korch Trading Bot"
5. Username: "korch_trading_bot_yourname"
6. **Copy the token** ← Save this

### Get Chat ID

1. Search → @userinfobot
2. Send any message
3. **Copy User ID** ← Save this

## Step 2: TradingView Session (1 min)

1. Open https://tradingview.com
2. Press F12 (DevTools)
3. Application → Cookies → tradingview.com
4. Find "sessionid" cookie
5. **Copy the value** ← Save this

## Step 3: Deploy to Railway (2 min)

1. Go https://railway.app
2. Sign up with GitHub
3. Click "New Project"
4. "Deploy from GitHub repo"
5. Select `philippkorch/korch-trading-bot`
6. Wait for build... ✓

## Step 4: Add Environment Variables

In Railway Dashboard:

1. Select project
2. "Variables" tab
3. Click "New Variable"
4. Add three:
   ```
   TELEGRAM_BOT_TOKEN = your_token_from_step1
   TELEGRAM_CHAT_ID = your_id_from_step1
   TRADINGVIEW_SESSION_ID = your_sessionid_from_step2
   ```

## Done! ✓

Bot is now running! 

- Check Telegram for signals
- View logs: Railway → Logs tab
- Bot runs 24/7 automatically

## Testing Locally (Optional)

```bash
# Clone repo
git clone https://github.com/philippkorch/korch-trading-bot
cd korch-trading-bot

# Install
pip install -r requirements.txt

# Run (Ctrl+C to stop)
TELEGRAM_BOT_TOKEN=your_token \
TELEGRAM_CHAT_ID=your_id \
TRADINGVIEW_SESSION_ID=your_session \
python korch_trading_bot.py
```

## Troubleshooting

**No signals after 1 hour?**
- Check TradingView session is still valid
- Check logs in Railway dashboard
- Verify TRADINGVIEW_SESSION_ID is correct

**Telegram not receiving messages?**
- Verify TELEGRAM_BOT_TOKEN is correct
- Verify TELEGRAM_CHAT_ID is correct
- Check Railway logs for errors

**Bot not starting?**
- Check all 3 environment variables are set
- Check variable values have no spaces
- View deployment logs for errors

## Next: Full Documentation

See:
- `README.md` - Full documentation
- `DEPLOYMENT.md` - Detailed deployment guide
- `test_bot.py` - View how bot works

Done! Your bot is live! 🚀
