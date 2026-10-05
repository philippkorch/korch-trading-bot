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
```bash
railway status
```

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
