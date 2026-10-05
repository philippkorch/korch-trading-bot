# Korch Trading Bot 🤖

Async trading bot with AMD+FVG strategy detection. Analyzes multiple timeframes and sends signals via Telegram.

## Features

- **Multi-timeframe Analysis**: 1H and 5M chart analysis
- **AMD+FVG Strategy**: Advanced price action analysis
- **Risk Management**: 1:2 reward-risk ratio, 1% per trade
- **Telegram Integration**: Real-time signal delivery
- **Docker Support**: Easy cloud deployment
- **Async Processing**: Non-blocking concurrent operations

## Architecture

### Core Components

- `TradingViewAPI`: Fetches OHLCV data from TradingView
- `StrategyAnalyzer`: AMD+FVG pattern detection
  - Fair Value Gap (FVG) detection on 1H
  - Auraprice Movement Direction (AMD) on 5M
  - Signal confirmation with both timeframes
- `TelegramSignalSender`: Sends formatted signals
- `KorchTradingBot`: Main orchestrator

### Trading Pairs

- EURUSD
- GBPUSD
- USDJPY
- AUDUSD

## Requirements

```
python-telegram-bot==20.3
requests==2.31.0
numpy==1.24.3
python-dateutil==2.8.2
aiohttp==3.8.7
```

## Environment Variables

```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
TRADINGVIEW_SESSION_ID=your_session_id_here
```

## Installation

### Local Setup

```bash
# Clone repository
git clone https://github.com/philippkorch/korch-trading-bot.git
cd korch-trading-bot

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_BOT_TOKEN=your_token
export TELEGRAM_CHAT_ID=your_chat_id
export TRADINGVIEW_SESSION_ID=your_session_id

# Run bot
python korch_trading_bot.py
```

### Docker Setup

```bash
# Build image
docker build -t korch-bot .

# Run container
docker run -e TELEGRAM_BOT_TOKEN=your_token \
           -e TELEGRAM_CHAT_ID=your_chat_id \
           -e TRADINGVIEW_SESSION_ID=your_session_id \
           korch-bot
```

## Configuration

- **SIGNAL_CHECK_INTERVAL**: 300 seconds (5 minutes)
- **DAILY_SIGNAL_LIMIT**: 5 signals per day
- **TRADING_PAIRS**: EURUSD, GBPUSD, USDJPY, AUDUSD
- **TIMEFRAMES**: 1H, 5M

## How It Works

1. **Data Fetching**: Continuously fetches OHLCV data from TradingView
2. **Pattern Detection**:
   - Identifies FVG (Fair Value Gap) on 1H timeframe
   - Detects AMD (Auraprice Movement Direction) on 5M
3. **Signal Generation**: Creates signals when both conditions align
4. **Risk Management**: Calculates SL and TP with 1:2 ratio
5. **Notification**: Sends formatted signal to Telegram

## Testing

```bash
python -m pytest test_bot.py
```

## Deployment

See `DEPLOYMENT.md` for Railway deployment instructions.

## Quick Start

See `QUICKSTART.md` for 5-minute setup guide.

## License

MIT

## Author

Philipp Korchmar (@philippkorch)
