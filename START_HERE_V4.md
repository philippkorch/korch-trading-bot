# 🚀 KORCH Trading Bot v4.0 - QUICK START

## Три способа запуска

### ✅ Способ 1: Локально на Linux/Mac (Рекомендуется для тестирования)

```bash
# 1. Перейдите в папку проекта
cd ~/korch-trading-bot

# 2. Установите зависимости
pip install -r requirements_v4.txt

# 3. Установите переменные окружения
export TELEGRAM_BOT_TOKEN="ваш_токен_от_BotFather"
export TELEGRAM_CHAT_ID="ваш_chat_id"

# 4. Запустите бота
python korch_bot_v4_with_charts.py

# В консоли должны увидеть:
# 🚀 Starting KORCH Trading Bot v4.0+ with Charts...
# ✅ Bot is running! Press Ctrl+C to stop.
```

### ✅ Способ 2: Docker (Локально)

```bash
# 1. Постройте образ
docker build -t korch-bot:v4 .

# 2. Запустите контейнер
docker run -e TELEGRAM_BOT_TOKEN="ваш_токен" \
           -e TELEGRAM_CHAT_ID="ваш_chat_id" \
           korch-bot:v4

# 3. В логах должны увидеть:
# 🚀 Starting KORCH Trading Bot v4.0+ with Charts...
```

### ✅ Способ 3: Railway (Облако - Production)

```bash
# 1. Установите Railway CLI
npm install -g @railway/cli

# 2. Логинитесь
railway login

# 3. Инициализируйте проект
cd ~/korch-trading-bot
railway init

# 4. Установите переменные окружения в Railway Dashboard:
# Project → Settings → Variables
# TELEGRAM_BOT_TOKEN = "ваш_токен"
# TELEGRAM_CHAT_ID = "ваш_chat_id"

# 5. Пушьте в GitHub
git add .
git commit -m "Deploy KORCH Bot v4.0"
git push origin main

# Railway автоматически развернет бота!
```

---

## 📱 Использование в Telegram

### Начало работы

```
1. Откройте Telegram
2. Найдите вашего бота (по имени которое вы задали BotFather)
3. Нажмите /start
4. Должны увидеть главное меню
```

### Главное меню

```
🤖 KORCH Trading Bot v4.0+

Анализ в реальном времени: GER40 | BTC | GOLD

[▶️ Анализировать]
[📰 NEWS]     [⚙️ STATUS]
[📍 SIGNALS]  [ℹ️ INFO]
```

### Анализ (главная функция)

```
1. Нажимаете "▶️ Анализировать"
2. Бот показывает: "🔄 Анализирую GER40, BTC, GOLD... ⏳"
3. Для каждого сигнала автоматически отправляется график
4. Финальное сообщение: "✅ Анализ завершен! 3 сигнала"
5. Можно нажать "⏹️ ОТМЕНА" для остановки во время анализа
```

### Экономический календарь (NEWS)

```
📰 ЭКОНОМИЧЕСКИЙ КАЛЕНДАРЬ

🇺🇸 10:30
🔴 HIGH: FOMC Interest Rate Decision

🇪🇺 11:00
🔴 HIGH: ECB Press Conference

...

Фильтры: [🔴 HIGH] [🟡 MEDIUM] [⚪ LOW]
Нажимайте на фильтр для включения/выключения событий
```

### Статус системы (STATUS)

```
⚙️ СТАТУС СИСТЕМЫ

✅ Тренд мониторинг: Активен
✅ Стратегия AMD: Включена
✅ FVG Структура: Включена
✅ INTELLECT_city: Активен

⏱️ Интервал проверки: 5 мин
🕐 Последнее обновление: 22:35
```

### Активные сигналы (SIGNALS)

```
📍 Активные сигналы (3)

🟢 GER40
Entry: 18500.50 | SL: 18450.00 | TP: 18600.50
R:R: 1:2.3 | Conf: 78% | INTELLECT: 72%

🔴 BTC/USD
Entry: 42850.00 | SL: 43200.00 | TP: 42350.00
R:R: 1:1.9 | Conf: 65% | INTELLECT: 58%

...
```

### Информация (INFO)

```
ℹ️ ИНФОРМАЦИЯ О СТРАТЕГИИ

AMD (After Market Delivery)
Анализ трендов с MA9 > MA21 для определения восходящего тренда.

FVG - Fair Value Gap
Выявление структурных пробелов на 5-минутном таймфрейме.

INTELLECT_city Score
Составной индикатор 0-100%. BUY: ≥60% | SELL: ≤40%

Risk:Reward Ratio 1:2
TP = Entry + (Entry - SL) × 2

...
```

---

## 📊 Получение Telegram данных

### Шаг 1: Найдите BotFather

В Telegram поиске введите `BotFather` (без кавычек)

### Шаг 2: Создайте бота

```
/start
/newbot

Bot name: Korch Trading Bot (или ваше имя)
Bot username: korch_trading_bot (уникальный, с англ. букв)

Вы получите токен вида:
8999356089:AAEzV2onmpC6oFe-j9M26UTFLxU14N6fSCs
```

**Сохраните этот токен в `TELEGRAM_BOT_TOKEN`**

### Шаг 3: Узнайте ваш Chat ID

```bash
# Способ 1: Через curl (если есть Terminal)
curl "https://api.telegram.org/bot<ВАШЕ_ТОКЕН>/getUpdates"

# Найдите в ответе: "chat":{"id":8999356089}
# Это и есть ваш TELEGRAM_CHAT_ID
```

Или:

```bash
# Способ 2: Через bot webhook (проще)
# Отправьте боту любое сообщение: "hello"
# Затем запустите бота локально (он покажет Chat ID в логах)
# 📱 Chat ID found: 8999356089
```

---

## 📂 Структура проекта v4.0

```
korch-trading-bot/
├── korch_bot_v4_minimalist.py       ← Версия БЕЗ графиков (проще)
├── korch_bot_v4_with_charts.py      ← Версия С графиками (рекомендуется)
├── requirements_v4.txt              ← Зависимости Python
├── Dockerfile                        ← Docker конфигурация (обновлена)
├── Procfile                          ← Railway конфигурация (обновлена)
├── START_HERE_V4.md                 ← Этот файл
├── KORCH_BOT_V4_README.md           ← Подробная документация
└── DEPLOYMENT_V4.md                 ← Гайд по развертыванию

Старые файлы (остаются для совместимости):
├── korch_trading_bot.py
├── chart_analyzer.py
├── enhanced_chart_analyzer.py
└── requirements.txt
```

---

## 🔄 Версии бота

| Версия | Графики | Сложность | Рекомендуется |
|--------|---------|-----------|---------------|
| **korch_bot_v4_minimalist.py** | ❌ Нет | Низкая | Для начала |
| **korch_bot_v4_with_charts.py** | ✅ Да | Средняя | **Production** |

---

## ✅ Проверка после запуска

### 1. Логи показывают успешный старт?

```
✅ Bot is running! Press Ctrl+C to stop.
```

### 2. Бот отвечает на /start?

```
🤖 KORCH Trading Bot v4.0+
[▶️ Анализировать]
```

### 3. Анализ работает?

Нажимаете "▶️ Анализировать" → должны появиться графики сигналов

### 4. Графики отправляются?

Каждый сигнал сопровождается фото графика с:
- OHLC свечами
- MA9 и MA21
- Entry, SL, TP
- Support и Resistance уровни

---

## 🐛 Проблемы и решения

### Проблема: "ModuleNotFoundError: No module named 'telegram'"

```bash
# Решение:
pip install python-telegram-bot==20.3
```

### Проблема: "ModuleNotFoundError: No module named 'matplotlib'"

```bash
# Решение:
pip install -r requirements_v4.txt
```

### Проблема: Бот не отвечает на команды

```bash
# Проверьте токен:
echo $TELEGRAM_BOT_TOKEN

# Перезапустите бота:
Ctrl+C
python korch_bot_v4_with_charts.py
```

### Проблема: Графики не отправляются

```bash
# Убедитесь что используете версию с графиками:
# Должно быть: python korch_bot_v4_with_charts.py

# Проверьте логи:
python korch_bot_v4_with_charts.py 2>&1 | grep -i "chart\|error"
```

### Проблема: "yfinance returned no data"

Это нормально! Бот использует fallback демо-сигналы, если реальные данные недоступны.

---

## 📚 Дополнительная информация

- **Подробная документация**: читайте `KORCH_BOT_V4_README.md`
- **Развертывание на Railway**: читайте `DEPLOYMENT_V4.md`
- **Исходный код бота**: смотрите `korch_bot_v4_with_charts.py`

---

## 🎯 Что дальше?

### Этап 1 (Сейчас) ✅
- [x] Интерфейс v4.0 с одной кнопкой
- [x] NEWS, STATUS, SIGNALS, INFO секции
- [x] Реальные данные через yfinance
- [x] Графики с аннотациями
- [x] Готов к развертыванию на Railway

### Этап 2 (Планируется)
- [ ] История сигналов (сохранение в БД)
- [ ] Уведомления при Entry/SL/TP
- [ ] Интеграция TradingView webhooks
- [ ] Дашборд со статистикой

### Этап 3 (Будущее)
- [ ] Управление позициями из Telegram
- [ ] Full INTELLECT_city (все 8 компонентов)
- [ ] Smart Money confirmations
- [ ] Публичный канал с сигналами

---

## 📞 Контакты

- **GitHub**: https://github.com/philippkorch/korch-trading-bot
- **Email**: philippkorchmar@gmail.com
- **Telegram**: @korch_bot

---

**KORCH Trading Bot v4.0** © 2026

Создано для анализа рынков: GER40 | BTC | GOLD  
Использует стратегию: AMD (After Market Delivery) + FVG  
Интеграция: yfinance + matplotlib + Telegram API

Готово к production! 🚀
