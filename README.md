# Korch Trading Bot 🤖

<<<<<<< HEAD
Автоматический торговый бот для анализа стратегии AMD+FVG и отправки сигналов в Telegram.

## Особенности

✅ Анализ стратегии AMD+FVG на TradingView  
✅ Поиск продвинутой структуры (HTF targets)  
✅ Управление риском (1% per trade, 1:2 RR)  
✅ Отправка сигналов в Telegram  
✅ Мониторинг сессий (Frankfurt, London, NY)  
✅ Проверка дневного контекста  

## Установка локально

### 1. Клонируй/скачай проект
```bash
git clone <repo> korch-bot
cd korch-bot
```

### 2. Установи зависимости
```bash
pip install -r requirements.txt
```

### 3. Запусти бота
```bash
python korch_trading_bot.py
```

## Конфигурация

### Основные параметры (в коде)

```python
TELEGRAM_BOT_TOKEN = "твой_токен_здесь"
TELEGRAM_CHAT_ID = 457832510  # Твой ID
TRADINGVIEW_SESSION_ID = "qu1s4tex582n1uzvgl9m35we03cbn6f2"

RISK_PER_TRADE = 0.01  # 1% риска на сделку
MAX_DAILY_LOSS = 0.02  # 2% максимум за день
RISK_REWARD_RATIO = 2  # 1:2
```

### Активы для торговли

```python
TRADING_PAIRS = {
    "GER40": {"timeframe": "1H", "session": "Frankfurt"},
    "EURUSD": {"timeframe": "1H", "session": "London"},
    "BTCUSDT": {"timeframe": "1H", "session": "NY"},
    "XAUUSD": {"timeframe": "1H", "session": "London"},
}
```

## Развертывание на Railway

### 1. Создай аккаунт на Railway
- https://railway.app
- Связи с GitHub (если нужно)

### 2. Создай новый проект
```bash
railway init
```

### 3. Добавь переменные окружения
```
TELEGRAM_BOT_TOKEN=твой_токен
TELEGRAM_CHAT_ID=457832510
TRADINGVIEW_SESSION_ID=qu1s4tex582n1uzvgl9m35we03cbn6f2
```

### 4. Задай команду запуска
```
python korch_trading_bot.py
```

### 5. Задеплой
```bash
railway up
```

## Интеграция с TradingView

### Получить sessionid

1. Зайди на https://www.tradingview.com
2. Открой DevTools (F12)
3. Application → Cookies → tradingview.com
4. Найди `sessionid` - скопируй значение
5. Вставь в `TRADINGVIEW_SESSION_ID`

### Pine Script для сигналов (опционально)

Используй стратегию с webhook'ами для более точных сигналов:

```pinescript
//@version=5
strategy("Korch AMD+FVG", overlay=true)

// Твоя логика здесь
// alert("BUY_SIGNAL") or alert("SELL_SIGNAL")
```

## Мониторинг

Бот проверяет сигналы каждые **5 минут** (300 сек).

Логи будут в консоли:
```
🤖 Бот запущен! Проверка каждые 300 сек...
📊 Проверка сигналов... 14:32:45
```

## Стоп-лосс и Тейк-профит

Бот автоматически считает:
- **SL**: На основе структуры (recent low для BUY)
- **TP**: По правилу 1:2 (RR = 1:2)
- **Пункты**: В пипсах для Forex

Пример сигнала в Telegram:

```
🟢 BUY GER40

📊 Вход: 25350
🛑 SL: 25320 (30 пункты)
🎯 TP: 25380 (60 пункты)

📈 R:R = 1:2
💡 Сигнал: AMD+FVG инверсия на 5M
⏰ Сессия: Frankfurt Morning
🕐 Время: 14:32:45
```

## Проблемы и решения

### sessionid истёк
- Переавторизуйся на TradingView
- Получи новый sessionid
- Обнови переменную

### Нет сигналов
- Проверь, активна ли сессия торговли
- Посмотри логи ошибок
- Убедись, что OHLCV данные получаются

### Ошибка Telegram
- Проверь токен бота
- Проверь chat_id
- Убедись, что бот добавлен в чат

## Безопасность

⚠️ **Никогда не коммитьте**:
- Telegram токены
- TradingView sessionid'ы
- Пароли

Используй `.env` файл (добавь в `.gitignore`):

```bash
# .env
TELEGRAM_BOT_TOKEN=xxx
TRADINGVIEW_SESSION_ID=xxx
```

Загружай переменные:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Дополнительно

- Docs: https://tradingview.com/api/
- Python-Telegram-Bot: https://python-telegram-bot.readthedocs.io/
- Railway CLI: https://docs.railway.app/reference/cli

## Статус

- ✅ Основной функционал (v1.0)
- 🔄 В работе: Интеграция с tvdatafeeds
- 📅 Планы: Бэктестинг, сохранение истории сигналов

---

**Контакт**: @philipp_korch (Telegram)  
**Стратегия**: AMD+FVG + Advanced Structure  
**Версия**: 1.0
=======
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
>>>>>>> origin/main
