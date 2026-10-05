# Korch Trading Bot 🤖

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
