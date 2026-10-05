# 🤖 Korch Trading Bot v2.0

**Интерактивный Telegram бот с AMD+FVG стратегией и INTELLECT_city подтверждением**

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.11-brightgreen)
![Status](https://img.shields.io/badge/status-production--ready-success)

---

## 📊 Что Это

Korch Trading Bot - автоматизированный торговый ассистент, который:

✅ **Анализирует** рынки GER40, BTC, GOLD на 1H+5M таймфреймах  
✅ **Обнаруживает** AMD+FVG торговые сетапы  
✅ **Подтверждает** сигналы через INTELLECT_city индикатор (60%+ порог)  
✅ **Отправляет** торговые сигналы в Telegram с полной информацией  
✅ **Управляет** рисками с 1:2 R:R и 1% риском на сделку  

---

## 🎯 Основные Возможности

### 1. AMD+FVG Стратегия
- After Market Delivery (AMD) - тренд на 1H (MA9 > MA21)
- Fair Value Gap (FVG) - эффективность цены на 1H
- 5M инверсии - точный вход на структуре

### 2. INTELLECT_city Индикатор 🔮
Композитный индекс из 8 ТОП индикаторов:
- RSI (14 период) - перекупленность/перепроданность
- Stochastic %K (14 период) - импульс
- MACD - направление тренда
- MFI (14 период) - объемные потоки
- Тренд - MA9 vs MA21 согласованность

**Результат**: 0-100% шкала рыночного настроения

### 3. Smart Money Методология
- Отслеживание институциональных потоков
- FVG как уровень входа Smart Money
- INTELLECT_city показывает согласованность крупных игроков

---

## 📦 Файлы Проекта

```
├── korch_trading_bot.py          # Основной бот (900+ строк)
├── requirements.txt               # Python зависимости
├── Dockerfile                     # Docker конфигурация
├── test_intellect_city.py        # Тестовый скрипт
├── INTELLECT_CITY_INTEGRATION.md # Техническая документация
├── DEPLOYMENT_CHECKLIST.md       # Чеклист для Railway
└── README.md                      # Этот файл
```

---

## 🚀 Развертывание

**Статус**: ✅ ГОТОВ К РАЗВЕРТЫВАНИЮ

```bash
# 1. Подготовить переменные окружения
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"

# 2. На Railway через CLI
railway up

# 3. Или через Dashboard
# railway.app → Deploy from GitHub
```

**Подробнее**: `DEPLOYMENT_CHECKLIST.md`

---

## 🧪 Локальное Тестирование

```bash
# Установить зависимости
pip install -r requirements.txt

# Протестировать INTELLECT_city
python test_intellect_city.py

# Запустить бот локально
python korch_trading_bot.py
```

---

## 📊 Пример Сигнала

```
🟢 BUY GER40

📊 Сигнал: AMD + 5M Inversion + INTELLECT 78%
⏱️ Таймфрейм: 1H+5M
🎲 Уверенность: 78%

🔮 INTELLECT_city: 78% (Сильный бычий)

💰 Вход: 18250.50
🛑 Stop Loss: 18200.00 (50 пипс)
🎁 Take Profit: 18350.00
📊 R:R: 1:2
```

---

## 📈 Логика Сигналов

**BUY**: AMD восход + 5M инверсия + INTELLECT ≥ 60%  
**SELL**: AMD спад + 5M инверсия + INTELLECT ≤ 40%

---

## 📞 Документация

- **INTELLECT_CITY_INTEGRATION.md** - Полное описание индикатора
- **DEPLOYMENT_CHECKLIST.md** - Инструкции развертывания
- **test_intellect_city.py** - Тестирование индикатора

---

**Версия**: 2.0 с INTELLECT_city и Smart Money  
**Дата**: 2026-10-05 22:27  
**Статус**: 🟢 Готов к боевому использованию

🎯 **Бот готов к развертыванию на Railway!**
