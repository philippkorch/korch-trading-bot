# KORCH Trading Bot v4.0 - Deployment Guide

## 📦 Что включено в v4.0

### Две версии бота

#### 1. **korch_bot_v4_minimalist.py** (Рекомендуется для начала)
- Минималистичный интерфейс
- Одна кнопка "Анализировать"
- Секции: NEWS, STATUS, SIGNALS, INFO
- Легче дебаглить
- Меньше зависимостей от графиков

#### 2. **korch_bot_v4_with_charts.py** (Полная версия)
- Все возможности v4.0
- **Автоматическая отправка аннотированных графиков**
- Графики с Entry, SL, TP, MA9, MA21, Support/Resistance
- Требует matplotlib и PIL

---

## 🚀 Развертывание на Railway

### Шаг 1: Подготовка GitHub репозитория

```bash
cd /home/claude/korch-trading-bot

# Убедитесь, что файлы в git
git add korch_bot_v4_minimalist.py korch_bot_v4_with_charts.py requirements_v4.txt
git commit -m "Add KORCH Bot v4.0 - Minimalist Interface with Charts"
git push origin main
```

### Шаг 2: Создание Railway сервиса

#### Опция A: Через Railway Dashboard

1. Перейдите на https://railway.app
2. Нажмите "Create Project"
3. Выберите "Deploy from GitHub"
4. Подключите репозиторий `korch-trading-bot`
5. Выберите branch `main`

#### Опция B: Через Railway CLI

```bash
# Установите Railway CLI
npm install -g @railway/cli

# Логинитесь
railway login

# Инициализируйте проект
railway init

# Выберите проект Korch
# Выберите environment: production
```

### Шаг 3: Конфигурация Railway

#### Создайте `Procfile` (если нет):

```procfile
# Версия с графиками (рекомендуется)
web: python korch_bot_v4_with_charts.py

# Или минималистичная версия
# web: python korch_bot_v4_minimalist.py
```

#### Обновите `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установите системные зависимости для PIL и matplotlib
RUN apt-get update && apt-get install -y \
    libfreetype6-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируйте requirements
COPY requirements_v4.txt .

# Установите Python зависимости
RUN pip install --no-cache-dir -r requirements_v4.txt

# Копируйте код
COPY . .

# Запустите бот
CMD ["python", "korch_bot_v4_with_charts.py"]
```

### Шаг 4: Установите переменные окружения

В Railway Dashboard → Project Settings → Variables:

```
TELEGRAM_BOT_TOKEN = "ваш_токен_бота"
TELEGRAM_CHAT_ID = "ваш_chat_id"
PYTHON_VERSION = "3.11"
```

**Где получить значения:**

- **TELEGRAM_BOT_TOKEN**: Откройте Telegram, найдите BotFather (@BotFather)
  ```
  /start
  /newbot
  Введите имя: Korch Trading Bot
  Получите токен вида: 8999356089:AAEzV2onmpC6oFe-j9M26UTFLxU14N6fSCs
  ```

- **TELEGRAM_CHAT_ID**: Отправьте сообщение боту, затем:
  ```bash
  curl "https://api.telegram.org/bot<TOKEN>/getUpdates"
  # В ответе найдите "id" в chat_id
  ```

### Шаг 5: Развертывание

```bash
# Через Railway CLI
railway deploy

# Или через Dashboard → Deploy
# Railway автоматически depoloyит при push в main
```

---

## ✅ Проверка развертывания

### 1. Проверьте логи

```bash
# Через Railway CLI
railway logs -f

# Должны увидеть:
# 🚀 Starting KORCH Trading Bot v4.0+ with Charts...
# ✅ Bot is running! Press Ctrl+C to stop.
```

### 2. Протестируйте бота

В Telegram:
```
/start
```

Должны увидеть:
```
🤖 KORCH Trading Bot v4.0+

Анализ в реальном времени: GER40 | BTC | GOLD

[▶️ Анализировать]
[📰 NEWS]     [⚙️ STATUS]
[📍 SIGNALS]  [ℹ️ INFO]
```

### 3. Протестируйте анализ

1. Нажмите "▶️ Анализировать"
2. Бот должен показать прогресс: "🔄 Анализирую..."
3. Через 10-15 секунд должны появиться графики сигналов
4. Финальное сообщение: "✅ Анализ завершен! Найдено сигналов: X"

---

## 📊 Что отправляет бот

### При нажатии "▶️ Анализировать":

```
✅ Анализ завершен!
🎯 Найдено сигналов: 3

🟢 GER40: BUY @ 18500.50 (R:R 2.3:1)
🔴 BTC/USD: SELL @ 42850.00 (R:R 1.9:1)
🟢 GOLD: BUY @ 2595.50 (R:R 2.1:1)

[▶️ Анализировать] [📍 SIGNALS] [◀️ МЕНЮ]
```

### Автоматически отправляются графики:

Для каждого сигнала отправляется фото с:
- OHLC свечами (последние 100 свечей)
- MA9 (синяя линия)
- MA21 (оранжевая линия)
- Support уровни (зеленый пунктир)
- Resistance уровни (красный пунктир)
- Entry (синяя линия)
- Stop Loss (красная линия)
- Take Profit (зеленая линия)

Пример подписи под графиком:
```
🟢 GER40 | 1H

Entry: 18500.50
SL: 18450.00
TP: 18600.50

R:R: 1:2.3
Confidence: 78%
INTELLECT: 72%
Confirmations: 5/8
```

---

## 🔧 Структура проекта после развертывания

```
korch-trading-bot/
├── korch_bot_v4_minimalist.py        # Базовая версия
├── korch_bot_v4_with_charts.py       # Версия с графиками
├── requirements_v4.txt               # Python зависимости
├── enhanced_chart_analyzer.py        # Генератор графиков (опционально)
├── chart_analyzer.py                 # Claude Vision интеграция (опционально)
├── Dockerfile                        # Docker конфигурация
├── Procfile                          # Railway конфигурация
├── KORCH_BOT_V4_README.md           # Пользовательская документация
└── DEPLOYMENT_V4.md                  # Этот файл
```

---

## 🐛 Troubleshooting

### Бот не отвечает на /start

```bash
# Проверьте токен
railway vars list | grep TELEGRAM_BOT_TOKEN

# Переустановите бота (может быть webhook старых версий)
# BotFather → /mybots → /setcommands
# Установите webhook: /setwebhook <пустой URL>
```

### "ModuleNotFoundError: No module named 'telegram'"

```bash
# Переустановите зависимости
railway run pip install -r requirements_v4.txt

# Или пересоберите контейнер
railway redeploy
```

### Нет графиков при анализе

```bash
# Проверьте логи на ошибки matplotlib
railway logs -f | grep -i "chart\|matplotlib\|image"

# Убедитесь что используете версию с графиками:
# Procfile должен содержать: korch_bot_v4_with_charts.py
```

### yfinance возвращает пустые данные

```bash
# Проверьте, что интернет доступен
railway run python -c "import yfinance; df = yf.Ticker('^GDAXI').history(period='30d', interval='1h'); print(len(df))"

# Если ошибка — используйте fallback сигналы (задано в коде)
```

---

## 📈 Мониторинг

### Railway Dashboard метрики

- **CPU Usage**: Должен быть < 50% в норме
- **Memory**: Должна быть < 200MB (Python + telegram lib + matplotlib)
- **Disk**: Не требуется (stateless бот)

### Логирование

Все события логируются с timestamp и уровнем (INFO, ERROR, DEBUG):

```
2026-10-10 22:30:45 - korch_bot_v4_with_charts - INFO - 🚀 Starting...
2026-10-10 22:30:46 - korch_bot_v4_with_charts - INFO - 📊 Fetching GER40...
2026-10-10 22:30:48 - korch_bot_v4_with_charts - INFO - ✅ Chart sent for GER40
2026-10-10 22:30:50 - korch_bot_v4_with_charts - INFO - ✅ Анализ завершен! 3 сигнала
```

---

## 🔄 Обновление бота

### Развертывание новой версии

```bash
# Внесите изменения локально
vim korch_bot_v4_with_charts.py

# Закоммитьте
git add korch_bot_v4_with_charts.py
git commit -m "Fix: улучшена генерация графиков"

# Пушьте в main
git push origin main

# Railway автоматически перестроит и переразвернет контейнер
```

### Откат на предыдущую версию

```bash
# Через Railway Dashboard
# Project → Deployments → Выберите предыдущий deployment → Redeploy
```

---

## 🎯 Будущие улучшения (Roadmap)

### V4.1 (Ближайшее)
- [ ] История сигналов (сохранение в JSON/DB)
- [ ] Уведомления при достижении Entry/SL/TP
- [ ] Статистика по сигналам (Win Rate, Profit Factor)

### V4.2 (Планируется)
- [ ] Интеграция TradingView webhooks для инициирования анализа
- [ ] Full FVG анализ на 5M таймфрейме
- [ ] INTELLECT_city интеграция (все 8 компонентов)

### V5.0 (Дорожная карта)
- [ ] Управление позициями (Edit Entry/SL/TP через бота)
- [ ] Database для истории (MongoDB/PostgreSQL)
- [ ] Dashboard для просмотра статистики
- [ ] Telegram Channels для публичных сигналов

---

## 📞 Поддержка

### Лог файлы
```bash
# Вывести последние 100 строк логов
railway logs -n 100 -f

# Сохранить логи в файл
railway logs > bot_logs.txt
```

### Restart бота
```bash
# Мягкий перезапуск (сохраняет состояние)
railway restart

# Жесткий перезапуск (пересоздает контейнер)
railway redeploy
```

### Обратная связь
- **GitHub Issues**: https://github.com/philippkorch/korch-trading-bot/issues
- **Email**: philippkorchmar@gmail.com

---

## 📋 Чек-лист перед production

- [ ] TELEGRAM_BOT_TOKEN установлен и правильный
- [ ] TELEGRAM_CHAT_ID установлен и правильный
- [ ] Dockerfile обновлен с matplotlib зависимостями
- [ ] Procfile указывает на правильный скрипт
- [ ] requirements_v4.txt содержит все зависимости
- [ ] Логи показывают "✅ Bot is running!"
- [ ] /start работает и показывает меню
- [ ] "Анализировать" отправляет графики без ошибок
- [ ] NEWS, STATUS, SIGNALS, INFO работают корректно

---

**KORCH Trading Bot v4.0** © 2026 | Production Deployment Ready

