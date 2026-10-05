<<<<<<< HEAD
# ⚡ Быстрый старт Korch Trading Bot

## За 5 минут

### 1️⃣ Установка локально

```bash
# Скачай все файлы:
# korch_trading_bot.py
# requirements.txt
# test_bot.py

# Установи зависимости:
pip install -r requirements.txt

# Проверь что работает:
python test_bot.py
```

✅ Готово! Если вижу "✅ ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!" - идем дальше.

### 2️⃣ Запуск локально

```bash
python korch_trading_bot.py
```

Ты должен увидеть:
```
==================================================
🤖 Korch Trading Bot v1.0
==================================================
🤖 Бот запущен! Проверка каждые 300 сек...
📊 Проверка сигналов... 14:32:45
```

**Сигналы будут приходить в Telegram!** ✅

### 3️⃣ Развертывание на Railway (облако)

#### Способ быстро (3 клика):

1. Зайди на https://railway.app
2. Нажми "+ New Project" → "Deploy from GitHub"
3. Выбери этот репо (или создай новый репо на GitHub и push туда)
4. Добавь переменные:
   - `TELEGRAM_BOT_TOKEN` = `8999356089:AAEzV2onmpC6oFe-j19M26UTFLxU14N6fSCs`
   - `TELEGRAM_CHAT_ID` = `457832510`
   - `TRADINGVIEW_SESSION_ID` = `qu1s4tex582n1uzvgl9m35we03cbn6f2`
5. Нажми "Deploy"

✅ Бот работает 24/7 на облаке!

---

## Что дальше?

### Получи сигналы в Telegram

Бот будет отправлять сигналы вот так:

```
🟢 BUY EURUSD

📊 Вход: 1.0950
🛑 SL: 1.0920
🎯 TP: 1.0980

📈 R:R = 1:2
💡 Сигнал: AMD+FVG инверсия на 5M
⏰ Сессия: London
🕐 Время: 14:32:45
```

### Настройка сессий торговли

Бот проверяет сигналы только в активные сессии:

| Сессия    | UTC+3 Время | Валютные пары |
|-----------|-------------|---------------|
| Frankfurt | 6-8         | GER40         |
| London    | 7-10        | EURUSD, XAUUSD|
| NY        | 12-16       | BTCUSDT       |

Ты можешь изменить в коде какие пары торговать.

---

## Главные файлы

| Файл | Что это |
|------|---------|
| `korch_trading_bot.py` | 🤖 Основной бот |
| `requirements.txt` | 📦 Зависимости |
| `test_bot.py` | 🧪 Тесты |
| `Dockerfile` | 🐳 Для Railway |
| `railway.yaml` | ⚙️  Конфиг Railway |
| `README.md` | 📖 Полная документация |
| `DEPLOYMENT.md` | 🚀 Подробно про Railroad |

---

## Команды

```bash
# Локальный запуск
python korch_trading_bot.py

# Тестирование
python test_bot.py

# Развертывание на Railway (если CLI установлен)
railway up

# Смотреть логи
railway logs -f
```

---

## Стоимость

- **Локально**: Бесплатно (только интернет)
- **Railway**: $0.20-1.00/месяц (очень дешево!)
- **Telegram**: Бесплатно

---

## Что если что-то не работает?

### Нет сигналов?
- Проверь активна ли сессия в твой час
- Посмотри логи: `railway logs`
- Убедись что OHLCV данные получаются

### Ошибка Telegram?
- Проверь токен и chat_id
- Убедись что бот добавлен в чат

### Sessionid истёк?
- Переавторизуйся на TradingView
- Получи новый sessionid из DevTools
- Обнови переменную

---

## Дальнейшее улучшение

Когда бот работает, можешь:

1. **Добавить Pine Script webhook** для точных сигналов
2. **Интегрировать с брокером** (для реальной торговли)
3. **Сохранять историю** сигналов в базе
4. **Бэктестировать** стратегию

---

## Поддержка

📖 **Docs**: Читай `README.md` и `DEPLOYMENT.md`

🆘 **Проблемы**: Смотри логи в Railway Dashboard

💬 **Вопросы**: @philipp_korch

---

**Ты готов! Запускай бота и ловли сигналы! 🚀📈**
=======
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
>>>>>>> origin/main
