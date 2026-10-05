# Railway Deployment Guide

Complete guide to deploy Korch Trading Bot on Railway.

## Prerequisites

- GitHub account with this repository pushed
- Railway account (free tier available)
- Telegram bot token and chat ID
- TradingView session ID

## Step 1: Prepare Your TradingView Session ID

1. Open TradingView.com
2. Open browser DevTools (F12)
3. Go to Application/Storage → Cookies → tradingview.com
4. Find cookie named "sessionid"
5. Copy the value - this is your `TRADINGVIEW_SESSION_ID`

## Step 2: Create Telegram Bot

1. Open Telegram, search for @BotFather
2. Send `/newbot`
3. Follow instructions:
   - Bot name: "Korch Trading Bot"
   - Bot username: "korch_trading_bot_[yourname]"
4. Copy the token (HTTP API)
5. Send `/mybots` → select bot → "My HTTP API" to verify

## Step 3: Get Telegram Chat ID

1. Search for @userinfobot in Telegram
2. Send any message
3. Get your User ID (this is your `TELEGRAM_CHAT_ID`)

## Step 4: Deploy to Railway

### Method 1: Web Dashboard (Recommended for Beginners)

1. Go to https://railway.app
2. Sign up/login with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Authorize Railway to access your GitHub
6. Select `philippkorch/korch-trading-bot` repository
7. Click "Deploy"

### Method 2: Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Link project to current directory
railway link

# Add environment variables
railway variables set TELEGRAM_BOT_TOKEN=your_token
railway variables set TELEGRAM_CHAT_ID=your_chat_id
railway variables set TRADINGVIEW_SESSION_ID=your_session_id

# Deploy
railway deploy
```

## Step 5: Add Environment Variables

In Railway Dashboard:

1. Go to your project
2. Select "Variables" tab
3. Add three variables:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
   - `TELEGRAM_CHAT_ID`: Your Telegram chat ID
   - `TRADINGVIEW_SESSION_ID`: Your TradingView session ID

## Step 6: Configure Deployment Settings

1. Go to "Deployments" tab
2. Select "Deploy on Push" option
3. This auto-deploys when you push to GitHub

## Monitoring

### View Logs

```bash
railway logs
```

Or in dashboard: Project → Logs tab

### Check Status

```bash
railway status
```

Or in dashboard: Project → Deployments tab

## Troubleshooting

### Bot not sending signals

1. **Check environment variables**: Verify all 3 variables are set correctly
2. **Check logs**: Look for error messages in Railway logs
3. **Verify token**: Ensure Telegram bot token is valid
4. **Test connection**: Manually check TradingView session still valid

### Deployment failed

1. **Check requirements.txt**: Ensure all dependencies are listed
2. **Check Dockerfile**: Verify syntax and image availability
3. **View build logs**: Railway shows detailed error messages
4. **Check Python version**: Should be 3.11

### No signals received

1. Verify TRADINGVIEW_SESSION_ID is still valid (expires after time)
2. Check if market is open (bot analyzes when market active)
3. Check daily signal limit (max 5/day)
4. Review logs for API errors

## Updating Bot

To update the bot:

1. Make changes locally
2. Push to GitHub:
   ```bash
   git add .
   git commit -m "Update bot logic"
   git push origin main
   ```
3. Railway auto-deploys (if Deploy on Push enabled)
4. Monitor deployment in Railway dashboard

## Costs

- **Free Tier**: Sufficient for 24/7 bot operation
- No monthly charges
- Included: 500 hours of running time per month

## Best Practices

1. **Session ID Refresh**: Refresh TradingView session every 30 days
2. **Monitor Signals**: Check first few signals for accuracy
3. **Adjust Pairs**: Remove trading pairs not needed (edit TRADING_PAIRS)
4. **Review Logs**: Check logs daily for any errors
5. **Backup Tokens**: Keep bot token and chat ID in safe place

## Need Help?

- Railway Docs: https://docs.railway.app
- Telegram Bot Docs: https://core.telegram.org/bots
- GitHub Issues: Create issue on repository

## Next Steps

1. Deploy on Railway using guide above
2. Verify bot is running with `railway status`
3. Check logs with `railway logs`
4. Wait for first signal (may take hours depending on market conditions)
5. Verify signal arrives in Telegram
