<<<<<<< HEAD
# Развертывание на Railway 🚀

Полное руководство по развертыванию Korch Trading Bot на Railway.

## Что такое Railway?

Railway - это платформа для хостинга приложений. Это похоже на Heroku, но дешевле и проще.

**Плюсы:**
- Бесплатный trial (до $5/месяц)
- Простой интерфейс
- Не нужна карта кредитной для начала
- Поддержка Python, Docker
- 24/7 работа

## Шаг 1: Подготовка локально

### Убедись что у тебя есть:
```
korch_trading_bot.py   ✓
requirements.txt       ✓
Dockerfile            ✓
railway.yaml          ✓
README.md             ✓
```

### Проверь что всё работает локально:
```bash
# 1. Установи зависимости
pip install -r requirements.txt

# 2. Запусти тест
python test_bot.py

# Если вижу ✅ - отлично! Готово к развертыванию
```

## Шаг 2: Создание GitHub репо (опционально, но рекомендуется)

### Если хочешь хранить код на GitHub:
```bash
# 1. Инит git
git init
git add .
git commit -m "Initial commit: Korch Trading Bot"

# 2. Создай репо на https://github.com/new
# Назови его "korch-trading-bot"

# 3. Push на GitHub
git remote add origin https://github.com/твой-юзер/korch-trading-bot.git
git branch -M main
git push -u origin main
```

## Шаг 3: Развертывание на Railway

### Способ 1: Через Railway CLI (рекомендуется)

#### 1. Установи Railway CLI
```bash
# macOS
brew install railway

# Windows (через npm)
npm install -g @railway/cli

# Linux
curl -fsSL https://railway.app/install.sh | bash
```

#### 2. Авторизуйся
```bash
railway login
```
Откроется браузер - авторизуйся через GitHub или почту.

#### 3. Создай проект
```bash
railway init

# Тебе предложат:
# - Project name: korch-trading-bot
# - Select a template: None (я свой файл использую)
```

#### 4. Добавь переменные окружения
```bash
railway variable set TELEGRAM_BOT_TOKEN "8999356089:AAEzV2onmpC6oFe-j19M26UTFLxU14N6fSCs"
railway variable set TELEGRAM_CHAT_ID "457832510"
railway variable set TRADINGVIEW_SESSION_ID "qu1s4tex582n1uzvgl9m35we03cbn6f2"
```

#### 5. Задеплой
```bash
railway up
```

Бот начнет работать! 🎉

---

### Способ 2: Через веб-интерфейс Railway

#### 1. Зайди на https://railway.app

#### 2. Нажми "+ New Project"

#### 3. Выбери "GitHub Repo"
- Выбери свой репо (если он на GitHub)
- Или "Deploy from Dockerfile"

#### 4. Выбери переменные окружения
Нажми "Add Variable":
```
TELEGRAM_BOT_TOKEN = 8999356089:AAEzV2onmpC6oFe-j19M26UTFLxU14N6fSCs
TELEGRAM_CHAT_ID = 457832510
TRADINGVIEW_SESSION_ID = qu1s4tex582n1uzvgl9m35we03cbn6f2
```

#### 5. Нажми "Deploy"

Railway автоматически:
- Найдет Dockerfile
- Установит зависимости
- Запустит `python korch_trading_bot.py`
- Будет держать бота работающим 24/7

---

## Шаг 4: Проверка что всё работает

### Смотри логи в Railway:
1. Зайди в Dashboard: https://railway.app/dashboard
2. Откой проект "korch-trading-bot"
3. Нажми на "Logs"

Ты должен увидеть:
```
🤖 Korch Trading Bot v1.0
🤖 Бот запущен! Проверка каждые 300 сек...
📊 Проверка сигналов... HH:MM:SS
```

### Получи сигнал в Telegram
- Бот проверяет пары каждые 5 минут
- При нахождении сетапа отправит сигнал тебе в Telegram
- Проверь чат @philipp_korch или с ботом

---

## Стоимость

**Railway Pricing:**
- Первый месяц: бесплатный trial
- Потом: оплата по использованию
- Примерная стоимость бота: **$0.20-1.00/месяц** (очень дешево!)

Это намного дешевле чем Heroku ($7-50/месяц).

---

## Обновление бота

### После изменений в коде:

#### Способ 1 (если на GitHub):
```bash
git add .
git commit -m "Update bot logic"
git push origin main

# Railway автоматически перезагрузит бота
```

#### Способ 2 (локально через CLI):
```bash
railway up
```

#### Способ 3 (через веб):
1. Зайди в Dashboard
2. Нажми Redeploy
3. Выбери ветку/commit

---

## Проблемы при развертывании

### "Module not found: tvdatafeeds"
**Решение**: Убедись что requirements.txt установлен
```bash
railway variable set PYTHON_VERSION 3.11
```

### "sessionid not found"
**Решение**: Переавторизуйся на TradingView и обнови sessionid
```bash
railway variable set TRADINGVIEW_SESSION_ID "новый_sessionid"
```

### "Telegram bot token invalid"
**Решение**: Проверь токен у BotFather:
1. Напиши @BotFather в Telegram
2. /mybotslist
3. Скопируй правильный токен
4. Обнови переменную

### Бот не отправляет сигналы
**Проверь:**
1. Логи в Railway (`railway logs` или Dashboard)
2. Активны ли сессии торговли в твой час
3. Есть ли данные с TradingView (может быть API проблема)

---

## Мониторинг

### Смотри логи:
```bash
railway logs -f  # Реал-тайм логи
```

### Перезагрузи если нужно:
```bash
railway redeploy
```

### Проверь статус:
=======
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

>>>>>>> origin/main
```bash
railway status
```

<<<<<<< HEAD
---

## Удаление с Railway

Если хочешь удалить:
```bash
railway down
```

Или через Dashboard → Delete Project

---

## Полезные команды Railway CLI

```bash
railway login              # Авторизация
railway init               # Создать проект
railway variable set KEY VALUE  # Добавить переменную
railway variable get KEY        # Посмотреть переменную
railway up                 # Развернуть приложение
railway redeploy           # Перезагрузить
railway logs              # Смотреть логи
railway logs -f           # Логи в реал-тайме
railway open              # Открыть dashboard
railway down              # Остановить
```

---

## Дальнейшие улучшения

После развертывания можешь:

1. **Настроить бэктестинг** для проверки стратегии
2. **Добавить пауз-логику** (не торговать в определенные часы)
3. **Сохранять историю сигналов** в базе данных
4. **Добавить webhook от TradingView** для более точных сигналов
5. **Интегрировать с брокером** (API для реальной торговли - будь осторожен!)

---

## Контакты и поддержка

- **Railway Docs**: https://docs.railway.app
- **Telegram**: @philipp_korch
- **Errors**: Смотри логи в Railway Dashboard

**Успешного развертывания! 🚀**
=======
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
>>>>>>> origin/main
