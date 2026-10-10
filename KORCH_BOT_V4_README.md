# KORCH Trading Bot v4.0 - Minimalist Interface

## 📋 Что нового в v4.0?

### ✨ Интерфейс
- **Одна кнопка "Анализировать"** — анализирует все пары (GER40, BTC, GOLD) одновременно
- **Кнопка "ОТМЕНА"** — появляется во время анализа для остановки процесса
- **Минималистичный дизайн** — только необходимые функции, без клаттера

### 📊 Основные секции
1. **АНАЛИЗ** — главная кнопка с прогресс-баром
2. **NEWS** — Экономический календарь с фильтрацией по уровню важности (HIGH/MEDIUM/LOW)
3. **STATUS** — Панель статуса (Тренд мониторинг, Интервал проверки, Стратегии, Время обновления)
4. **SIGNALS** — Активные торговые сигналы с Entry, SL, TP, R:R, Confidence
5. **INFO** — Информация о стратегии AMD+FVG, INTELLECT_city, Risk:Reward

### 🔄 Реальные данные
- Интеграция с **yfinance** для получения реальных котировок
- Поддержка пар: GER40 (^GDAXI), BTC-USD, GOLD (GC=F)
- Анализ по MA9/MA21 (AMD стратегия)
- Exponential backoff при ошибках сети

## 🚀 Установка и запуск

### 1. Установите зависимости
```bash
pip install -r requirements_v4.txt
```

### 2. Установите переменные окружения
```bash
export TELEGRAM_BOT_TOKEN="ваш_токен_бота"
export TELEGRAM_CHAT_ID="ваш_chat_id"
```

### 3. Запустите бота
```bash
python korch_bot_v4_minimalist.py
```

## 📱 Использование в Telegram

### Главное меню
```
🤖 KORCH Trading Bot v4.0

Анализ в реальном времени: GER40 | BTC | GOLD

[▶️ Анализировать]
[📰 NEWS]     [⚙️ STATUS]
[📍 SIGNALS]  [ℹ️ INFO]
```

### Процесс анализа
1. Нажимаете "▶️ Анализировать"
2. Бот анализирует все 3 пары одновременно (прогресс-бар: 0-100%)
3. Показывает найденные сигналы или сообщение об отсутствии сигналов
4. Вы можете отменить анализ кнопкой "⏹️ ОТМЕНА"

### Экономический календарь (NEWS)
- Все события отсортированы по уровню важности
- Фильтры: 🔴 HIGH | 🟡 MEDIUM | ⚪ LOW
- Нажимаете на фильтр для включения/выключения событий этого уровня

### Статус системы (STATUS)
Показывает:
- ✅ Тренд мониторинг: Активен
- ⏱️ Интервал проверки: 5 мин
- ✅ Стратегия AMD: Включена
- ✅ FVG Структура: Включена
- 🕐 Последнее обновление: [время]

### Активные сигналы (SIGNALS)
Каждый сигнал показывает:
- Пара и таймфрейм
- Тип сигнала (🟢 BUY / 🔴 SELL)
- Entry, Stop Loss, Take Profit
- R:R Ratio (Risk:Reward)
- Confidence (%)
- INTELLECT_city Score (%)
- Количество подтверждений (из 8)

## 🔧 Архитектура кода

### Основные классы
```python
@dataclass
class TradeSignal:
    pair: str
    timeframe: str
    signal_type: str  # BUY or SELL
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float
    intellect_score: float
    confirmations: int
    support_levels: List[float]
    resistance_levels: List[float]

@dataclass
class AnalysisState:
    is_analyzing: bool
    progress: int  # 0-100
    last_update: Optional[datetime]
    active_signals: List[TradeSignal]
```

### Основные функции

#### `fetch_market_data(pair: str, symbol: str) -> DataFrame`
Получает реальные данные рынка через yfinance
- Вычисляет MA9 и MA21 для AMD стратегии
- Возвращает DataFrame с OHLCV данными

#### `generate_mock_signal(pair: str, df: DataFrame) -> TradeSignal`
Генерирует сигнал на основе реальных данных
- Проверяет AMD условие (MA9 > MA21)
- Вычисляет Entry, SL, TP с 1:2 R:R
- В режиме fallback возвращает демо-сигналы

#### `analyze_all_pairs(context) -> List[TradeSignal]`
Анализирует все пары одновременно
- Получает данные для GER40, BTC, GOLD
- Генерирует сигналы для каждой пары
- Возвращает список активных сигналов

#### `perform_analysis(user_id, message, query)`
Асинхронно выполняет анализ
- Обновляет прогресс-бар
- Собирает результаты
- Обновляет сообщение с результатами

## 🎯 Callback handlers

| Callback | Функция |
|----------|---------|
| `analyze_start` | Начинает анализ |
| `analyze_cancel` | Отменяет анализ |
| `show_news` | Показывает календарь событий |
| `show_status` | Показывает статус системы |
| `show_signals` | Показывает активные сигналы |
| `show_info` | Показывает информацию о стратегии |
| `back_to_menu` | Возвращается в главное меню |

## 📊 Данные с реальных рынков

### Интеграция yfinance
```python
# GER40 (DAX Index)
symbol = '^GDAXI'
interval = '1h'

# BTC/USD
symbol = 'BTC-USD'
interval = '4h'

# Gold
symbol = 'GC=F'
interval = '1h'
```

### Обработка ошибок
- Таймауты и сетевые ошибки → Fallback на демо-данные
- Отсутствие данных → Пропускает пару, продолжает анализ
- Упал бот → Сохраняет состояние, возможна переподключение

## 🔮 Будущие улучшения

### Уровень 1 (Готовы к реализации)
- [ ] Интеграция `enhanced_chart_analyzer.py` для генерации аннотированных графиков
- [ ] Отправка фото графиков в Telegram при каждом сигнале
- [ ] Сохранение истории сигналов в базе данных

### Уровень 2 (Средний приоритет)
- [ ] Полный анализ FVG структуры на 5M таймфрейме
- [ ] Интеграция TrendyQ INTELLECT_city индикатора
- [ ] Smart Money confirmations из платформы

### Уровень 3 (Продвинутые функции)
- [ ] Webhook от TradingView для инициирования анализа
- [ ] Управление позициями (Edit Entry/SL/TP)
- [ ] Уведомления при достижении уровней (Entry/SL/TP)
- [ ] Статистика по сигналам (Win Rate, Profit Factor)

## 📝 Логирование

Все события логируются в console с информацией:
```
2026-10-10 22:30:45 - korch_bot_v4_minimalist - INFO - 🚀 Starting KORCH Trading Bot v4.0...
2026-10-10 22:30:46 - korch_bot_v4_minimalist - INFO - 📊 Fetching data for GER40...
2026-10-10 22:30:48 - korch_bot_v4_minimalist - INFO - ✅ Got 720 candles for GER40
2026-10-10 22:30:48 - korch_bot_v4_minimalist - INFO - ✅ Signal found for GER40: BUY @ 18500.50
```

## 🐛 Troubleshooting

### Бот не запускается
```bash
# Проверьте токен
echo $TELEGRAM_BOT_TOKEN

# Проверьте зависимости
pip install -r requirements_v4.txt

# Запустите с verbose логированием
LOGGING_LEVEL=DEBUG python korch_bot_v4_minimalist.py
```

### Нет данных с yfinance
```python
# Проверьте доступность символов
import yfinance as yf
df = yf.Ticker('^GDAXI').history(period='30d', interval='1h')
print(df)
```

### Сигналы не генерируются
- Проверьте, что MA21 < MA9 для восходящего тренда (BUY сигнал)
- Убедитесь, что данных достаточно (минимум 21 свеч)
- Проверьте логи на ошибки при получении данных

## 📞 Контакты для поддержки

- **Telegram**: @korch_bot
- **GitHub**: https://github.com/philippkorch/korch-trading-bot
- **Email**: philippkorchmar@gmail.com

---

**KORCH Trading Bot v4.0** © 2026 | Minimalist Interface Edition
