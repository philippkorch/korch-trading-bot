"""
<<<<<<< HEAD
Korch Trading Bot - Telegram Signals
Анализирует стратегию AMD+FVG и отправляет сигналы в Telegram
"""

import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import asyncio
from telegram import Bot
import numpy as np

# ===== КОНФИГ =====
TELEGRAM_BOT_TOKEN = "8999356089:AAEzV2onmpC6oFe-j19M26UTFLxU14N6fSCs"
TELEGRAM_CHAT_ID = 457832510  # Твой ID

# TradingView данные
TRADINGVIEW_SESSION_ID = "qu1s4tex582n1uzvgl9m35we03cbn6f2"
TRADINGVIEW_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
}

# Твоя стратегия параметры
RISK_PER_TRADE = 0.01  # 1% риска на сделку
MAX_DAILY_LOSS = 0.02  # 2% максимум за день
RISK_REWARD_RATIO = 2  # 1:2

# Активы для торговли
TRADING_PAIRS = {
    "GER40": {"timeframe": "1H", "session": "Frankfurt"},
    "EURUSD": {"timeframe": "1H", "session": "London"},
    "BTCUSDT": {"timeframe": "1H", "session": "NY"},
    "XAUUSD": {"timeframe": "1H", "session": "London"},
}

# Сессии торговли (UTC+3 Haifa time)
TRADING_SESSIONS = {
    "Frankfurt": {"start": 6, "end": 8},  # 9-11 Frankfurt = 6-8 UTC+3
    "London": {"start": 7, "end": 10},     # 10-13 London = 7-10 UTC+3
    "NY": {"start": 12, "end": 16},        # 15:30-19:30 NY = 12-16 UTC+3 (ЛЕТО)
}


class TradingViewAPI:
    """Подключение к TradingView"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.headers = TRADINGVIEW_HEADERS.copy()
        self.headers['Cookie'] = f'sessionid={session_id}'

    def get_ohlcv(self, symbol: str, timeframe: str = "1H", limit: int = 100) -> List[Dict]:
        """
        Получить OHLCV данные (Open, High, Low, Close, Volume)

        Args:
            symbol: Пара (GER40, EURUSD, etc)
            timeframe: Таймфрейм (1M, 5M, 1H, 4H, D)
            limit: Количество свечей

        Returns:
            Список свечей с OHLCV
        """
        try:
            # TradingView WebSocket API для получения исторических данных
            # Здесь упрощённая версия - в реальности нужен tvdatafeeds или подобное

            # Для демо - возвращаем пустой список
            # В production: использовать tvdatafeeds.Fetcher или REST API
            # pip install tvdatafeeds

            return []
        except Exception as e:
            print(f"❌ Ошибка при получении OHLCV для {symbol}: {e}")
            return []

    def check_trend(self, symbol: str) -> Dict:
        """Проверить тренд на дневном таймфрейме"""
        # D: вверх (+1), вниз (-1), боком (0)
        try:
            ohlcv = self.get_ohlcv(symbol, timeframe="D", limit=20)
            if not ohlcv or len(ohlcv) < 3:
                return {"trend": 0, "strength": 0}

            closes = [candle.get('close', 0) for candle in ohlcv]
            highs = [candle.get('high', 0) for candle in ohlcv]
            lows = [candle.get('low', 0) for candle in ohlcv]

            # Простой анализ тренда по последним 5 свечам
            trend_direction = 1 if closes[-1] > closes[-5] else (-1 if closes[-1] < closes[-5] else 0)

            # Сила тренда (как далеко от moving average)
            ma20 = sum(closes[-20:]) / min(len(closes), 20)
            strength = abs(closes[-1] - ma20) / ma20 if ma20 > 0 else 0

            return {
                "trend": trend_direction,  # +1: вверх, -1: вниз, 0: боком
                "strength": strength,      # 0-1
                "close": closes[-1]
            }
        except Exception as e:
            print(f"❌ Ошибка при проверке тренда {symbol}: {e}")
            return {"trend": 0, "strength": 0}


class StrategyAnalyzer:
    """Анализ твоей стратегии AMD+FVG"""

    def __init__(self):
        self.broken_trades = 0
        self.daily_loss = 0

    def check_skip_day(self, market_context: Dict) -> bool:
        """
        Проверить, нужно ли пропустить день

        Пропускаем если:
        - Контекст непонятен
        - Красные новости
        - На дневке боковая тенденция
        """
        # Реализация проверки
        return False

    def find_amd_fvg_setup(self, ohlcv_1h: List, ohlcv_5m: List) -> Optional[Dict]:
        """
        Найти сетап AMD + FVG на графике

        Условия:
        1. Только по тренду (D ↑ + 1H моментум)
        2. Снятие ликвидности
        3. Входы: инверсия / BOS / поглощение на 5М
        """
        if not ohlcv_1h or not ohlcv_5m:
            return None

        try:
            # Анализ структуры и моделей входа

            # 1. Проверить моментум на 1H (простой MA)
            closes_1h = [c.get('close', 0) for c in ohlcv_1h[-10:]]
            if len(closes_1h) < 3:
                return None

            ma9_1h = sum(closes_1h[-9:]) / 9
            ma21_1h = sum(closes_1h[-10:]) / 10

            # Условие: close > MA9 > MA21 (восходящий тренд)
            if closes_1h[-1] <= ma9_1h or ma9_1h <= ma21_1h:
                return None  # Нет тренда

            # 2. Анализ 5M для входа (инверсия/BOS)
            closes_5m = [c.get('close', 0) for c in ohlcv_5m[-20:]]
            highs_5m = [c.get('high', 0) for c in ohlcv_5m[-20:]]
            lows_5m = [c.get('low', 0) for c in ohlcv_5m[-20:]]

            if len(closes_5m) < 5:
                return None

            # Простой анализ: ищем отскоки (pull-back перед входом)
            # Пример: ищем два последовательных lower low (инверсия)
            if lows_5m[-1] > lows_5m[-2] and lows_5m[-2] < lows_5m[-3]:
                # Это может быть инверсия
                entry_price = highs_5m[-1]
                sl = lows_5m[-2] * 0.99

                if entry_price > sl:
                    return {
                        'type': 'BUY',
                        'entry': round(entry_price, 5),
                        'sl': round(sl, 5),
                        'reason': 'AMD+FVG инверсия на 5M',
                        'confidence': 0.7
                    }

            return None
        except Exception as e:
            print(f"❌ Ошибка при поиске AMD+FVG: {e}")
            return None

    def find_advanced_structure_setup(self, ohlcv: List) -> Optional[Dict]:
        """
        Найти продвинутую структуру

        Условия:
        1. HTF таргет (пул ликвидности)
        2. 5М инверсия / поглощение
        """
        if not ohlcv or len(ohlcv) < 10:
            return None

        try:
            closes = [c.get('close', 0) for c in ohlcv[-30:]]
            highs = [c.get('high', 0) for c in ohlcv[-30:]]
            lows = [c.get('low', 0) for c in ohlcv[-30:]]

            # Поиск уровней поддержки/сопротивления (HTF таргеты)
            # Используем простой метод: ищем clustering highs/lows

            # Ищем структурный уровень (область с несколькими касаниями)
            recent_low = min(lows[-10:])
            recent_high = max(highs[-10:])

            # Проверяем, есть ли pullback к этому уровню
            if abs(closes[-1] - recent_high) < abs(recent_high - recent_low) * 0.1:
                # Цена близко к recent_high - возможен отскок вверх
                return {
                    'type': 'SELL',
                    'entry': round(recent_high, 5),
                    'sl': round(recent_high * 1.005, 5),
                    'reason': 'Advanced Structure - HTF resistance',
                    'confidence': 0.6
                }

            return None
        except Exception as e:
            print(f"❌ Ошибка при поиске Advanced Structure: {e}")
            return None

    def calculate_sl_tp(self, entry: float, sl: float, signal: str, risk_percent: float = 1.0) -> Dict:
        """
        Считать SL и TP по правилу 1:2

        Args:
            entry: Цена входа
            sl: Цена стоп-лосса
            signal: BUY или SELL
            risk_percent: % риска от счёта (по умолчанию 1%)

        Returns:
            {sl: цена, tp: цена, pips: пункты, rr: risk/reward ratio}
        """
        try:
            if signal == 'BUY':
                risk_points = entry - sl
                tp = entry + (risk_points * RISK_REWARD_RATIO)  # 1:2 RR

                # Для Forex/CFD пункты - это обычно 0.0001
                pips = round(risk_points * 10000, 1)

            elif signal == 'SELL':
                risk_points = sl - entry
                tp = entry - (risk_points * RISK_REWARD_RATIO)  # 1:2 RR
                pips = round(risk_points * 10000, 1)
            else:
                return {}

            return {
                'sl': round(sl, 5),
                'tp': round(tp, 5),
                'sl_pips': abs(pips),
                'tp_pips': abs(pips * RISK_REWARD_RATIO),
                'rr': f'1:{RISK_REWARD_RATIO}'
            }
        except Exception as e:
            print(f"❌ Ошибка при расчете SL/TP: {e}")
            return {}


class TelegramSignalSender:
    """Отправка сигналов в Telegram"""

    def __init__(self, token: str, chat_id: int):
        self.bot = Bot(token=token)
        self.chat_id = chat_id

    async def send_signal(self, signal: Dict):
        """
        Отправить сигнал в Telegram

        signal должен содержать:
        {
            'type': 'BUY' | 'SELL',
            'symbol': 'GER40',
            'entry': 25350,
            'sl': 25320,
            'tp': 25410,
            'rr': '1:2',
            'reason': 'AMD+FVG инверсия на 5M',
            'session': 'Frankfurt Morning'
        }
        """
        message = self._format_signal(signal)
        await self.bot.send_message(
            chat_id=self.chat_id,
            text=message,
            parse_mode='Markdown'
        )

    async def send_confirmation(self, signal_id: str, confirmed: bool, reason: str = ""):
        """Отправить подтверждение/отклонение сигнала"""
        if confirmed:
            emoji = "✅"
            text = f"{emoji} ПОДТВЕРЖДАЮ сигнал #{signal_id}"
        else:
            emoji = "⚠️"
            text = f"{emoji} ОТКЛОНЯЮ сигнал #{signal_id}\n\nПричина: {reason}"

        await self.bot.send_message(
            chat_id=self.chat_id,
            text=text,
            parse_mode='Markdown'
        )

    def _format_signal(self, signal: Dict) -> str:
        """Форматировать сигнал для отправки"""
        emoji = "🟢" if signal['type'] == 'BUY' else "🔴"

        message = f"""
{emoji} **{signal['type']} {signal['symbol']}**

📊 Вход: `{signal['entry']}`
🛑 SL: `{signal['sl']}` ({signal.get('sl_pips', 0)} пунктов)
🎯 TP: `{signal['tp']}` ({signal.get('tp_pips', 0)} пунктов)

📈 R:R = `{signal['rr']}`
💡 Сигнал: {signal['reason']}
⏰ Сессия: {signal['session']}
🕐 Время: {datetime.now().strftime('%H:%M:%S')}
"""
        return message


class KorchTradingBot:
    """Главный класс бота"""

    def __init__(self, token: str, chat_id: int, sessionid: str = None):
        self.telegram = TelegramSignalSender(token, chat_id)
        self.strategy = StrategyAnalyzer()

        if sessionid:
            self.tv = TradingViewAPI(sessionid)
        else:
            self.tv = None
            print("⚠️ sessionid не установлен - бот работает в режиме демо")

    async def analyze_pair(self, symbol: str, pair_config: Dict):
        """Анализировать одну пару"""
        # Получить данные с TradingView
        ohlcv_1h = self.tv.get_ohlcv(symbol, timeframe="1H") if self.tv else []
        ohlcv_5m = self.tv.get_ohlcv(symbol, timeframe="5M") if self.tv else []

        # Проверить, нужно ли пропустить
        if self.strategy.check_skip_day({}):
            return

        # Искать сетапы
        setup_amd = self.strategy.find_amd_fvg_setup(ohlcv_1h, ohlcv_5m)
        setup_advanced = self.strategy.find_advanced_structure_setup(ohlcv_1h)

        # Если найден сетап - отправить сигнал
        if setup_amd or setup_advanced:
            signal = setup_amd or setup_advanced

            # Добавить SL/TP расчеты
            sl_tp = self.strategy.calculate_sl_tp(
                entry=signal['entry'],
                sl=signal['sl'],
                signal=signal['type'],
                risk_percent=RISK_PER_TRADE * 100
            )

            # Объединить сигнал с SL/TP
            signal.update(sl_tp)
            signal['symbol'] = symbol
            signal['session'] = pair_config.get('session', 'Unknown')

            # Отправить в Telegram
            await self.telegram.send_signal(signal)

    async def run_continuous(self, check_interval: int = 300):
        """
        Запустить бота в режиме проверки каждые N секунд

        Args:
            check_interval: Интервал проверки в секундах (по умолчанию 5 минут)
        """
        print(f"🤖 Бот запущен! Проверка каждые {check_interval} сек...")

        while True:
            try:
                print(f"📊 Проверка сигналов... {datetime.now().strftime('%H:%M:%S')}")

                for symbol, config in TRADING_PAIRS.items():
                    await self.analyze_pair(symbol, config)

                await asyncio.sleep(check_interval)

            except Exception as e:
                print(f"❌ Ошибка: {e}")
                await asyncio.sleep(60)


# ===== PINE SCRIPT ДЛЯ TradingView =====

PINE_SCRIPT_STRATEGY = """
//@version=5
strategy("Korch AMD+FVG Strategy", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=100)

// Параметры
fastMA = ta.sma(close, 9)
slowMA = ta.sma(close, 21)
riskPercent = 1.0

// Условие входа: AMD + FVG
buyCondition = close > fastMA and fastMA > slowMA and volume > ta.sma(volume, 20)
sellCondition = close < fastMA and fastMA < slowMA and volume > ta.sma(volume, 20)

// Отправить webhook при сигнале
if buyCondition
    strategy.entry("Buy", strategy.long)
    alert("BUY_SIGNAL")

if sellCondition
    strategy.entry("Sell", strategy.short)
    alert("SELL_SIGNAL")
"""


async def main():
    """Главная функция"""

    print("=" * 50)
    print("🤖 Korch Trading Bot v1.0")
    print("=" * 50)

    # Создать бота
    bot = KorchTradingBot(
        token=TELEGRAM_BOT_TOKEN,
        chat_id=TELEGRAM_CHAT_ID,
        sessionid=TRADINGVIEW_SESSION_ID  # Заполнится после авторизации
    )

    # Запустить в режиме проверки каждые 5 минут
    await bot.run_continuous(check_interval=300)


if __name__ == "__main__":
=======
Korch Trading Bot - Interactive Telegram Bot with Charts
"""

import asyncio
import logging
import os
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import aiohttp
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import TelegramError
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from io import BytesIO
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = int(os.getenv('TELEGRAM_CHAT_ID', '0'))
TRADINGVIEW_SESSION_ID = os.getenv('TRADINGVIEW_SESSION_ID', '')

TRADING_PAIRS = {
    'EURUSD': {'symbol': 'FX_IDC:EURUSD', 'volatility': 0.0015},
    'GBPUSD': {'symbol': 'FX_IDC:GBPUSD', 'volatility': 0.0018},
    'USDJPY': {'symbol': 'FX_IDC:USDJPY', 'volatility': 0.0012},
    'AUDUSD': {'symbol': 'FX_IDC:AUDUSD', 'volatility': 0.0020},
}

TIMEFRAMES = ['1H', '5M']
SIGNAL_CHECK_INTERVAL = 300
DAILY_SIGNAL_LIMIT = 5


@dataclass
class OHLCV:
    """OHLC+Volume data point"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


@dataclass
class Signal:
    """Trading signal"""
    pair: str
    direction: str
    entry: float
    stop_loss: float
    take_profit: float
    timeframe: str
    confidence: float
    reason: str


class TradingViewAPI:
    """TradingView API wrapper"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.headers = {
            'User-Agent': 'Mozilla/5.0',
            'Cookie': f'sessionid={session_id}',
        }
    
    async def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 50) -> List[OHLCV]:
        """Fetch OHLCV data"""
        try:
            logger.info(f"Fetching {symbol} {timeframe}")
            return []
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")
            return []


class StrategyAnalyzer:
    """Analyzes AMD+FVG trading strategy"""
    
    def __init__(self):
        self.min_fvg_size = 0.0005
        self.amd_threshold = 0.7
    
    def analyze(self, ohlcv_data: Dict[str, List[OHLCV]], pair: str) -> Optional[Signal]:
        """Analyze price action"""
        h1_data = ohlcv_data.get('1H', [])
        m5_data = ohlcv_data.get('5M', [])
        
        if len(h1_data) < 3 or len(m5_data) < 5:
            return None
        
        fvg_buy, fvg_sell = self._detect_fvg(h1_data)
        amd_signal = self._detect_amd(m5_data)
        
        if not amd_signal:
            return None
        
        if fvg_buy and amd_signal['direction'] == 'BUY':
            return self._create_signal(pair, 'BUY', h1_data[-1], m5_data[-1], 'FVG+AMD')
        elif fvg_sell and amd_signal['direction'] == 'SELL':
            return self._create_signal(pair, 'SELL', h1_data[-1], m5_data[-1], 'FVG+AMD')
        
        return None
    
    def _detect_fvg(self, ohlcv: List[OHLCV]) -> Tuple[bool, bool]:
        """Detect Fair Value Gap"""
        if len(ohlcv) < 3:
            return False, False
        
        fvg_buy = ohlcv[-3].low < ohlcv[-1].high
        fvg_sell = ohlcv[-3].high > ohlcv[-1].low
        
        return fvg_buy, fvg_sell
    
    def _detect_amd(self, ohlcv: List[OHLCV]) -> Optional[Dict]:
        """Detect movement direction"""
        if len(ohlcv) < 5:
            return None
        
        closes = [candle.close for candle in ohlcv[-5:]]
        up_count = sum(1 for i in range(len(closes)-1) if closes[i+1] > closes[i])
        strength = up_count / (len(closes) - 1)
        
        if strength >= self.amd_threshold:
            return {'direction': 'BUY', 'strength': strength}
        elif strength <= (1 - self.amd_threshold):
            return {'direction': 'SELL', 'strength': 1 - strength}
        
        return None
    
    def _create_signal(self, pair: str, direction: str, h1_candle: OHLCV, 
                      m5_candle: OHLCV, reason: str) -> Signal:
        """Create trading signal"""
        entry = m5_candle.close
        
        if direction == 'BUY':
            stop_loss = m5_candle.low * 0.9999
            pip_size = (entry - stop_loss) * 10000
            take_profit = entry + (pip_size * 2 / 10000)
        else:
            stop_loss = m5_candle.high * 1.0001
            pip_loss = (stop_loss - entry) * 10000
            take_profit = entry - (pip_loss * 2 / 10000)
        
        return Signal(
            pair=pair,
            direction=direction,
            entry=round(entry, 5),
            stop_loss=round(stop_loss, 5),
            take_profit=round(take_profit, 5),
            timeframe='1H+5M',
            confidence=0.75,
            reason=reason
        )


class ChartGenerator:
    """Generates trading charts with SL/TP visualization"""
    
    @staticmethod
    def create_signal_chart(signal: Signal) -> BytesIO:
        """Create chart with signal visualization"""
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor('#1a1a1a')
        ax.set_facecolor('#2a2a2a')
        
        # Price points
        prices = np.array([signal.stop_loss, signal.entry, signal.take_profit])
        labels = ['SL', 'Entry', 'TP']
        colors = ['#ff4444', '#00ff00', '#4444ff']
        
        # Plot
        ax.scatter(range(len(prices)), prices, s=300, c=colors, zorder=3)
        ax.plot(range(len(prices)), prices, 'w--', alpha=0.3, linewidth=2)
        
        # Add price labels
        for i, (price, label) in enumerate(zip(prices, labels)):
            ax.text(i, price, f'  {price:.5f}\n{label}', 
                   color=colors[i], fontsize=10, va='center')
        
        # Zones
        ax.axhspan(signal.stop_loss - 0.0001, signal.entry, alpha=0.1, color='red', label='Risk Zone')
        ax.axhspan(signal.entry, signal.take_profit + 0.0001, alpha=0.1, color='green', label='Profit Zone')
        
        # Styling
        ax.set_title(f'{signal.pair} - {signal.direction} Signal', 
                    color='white', fontsize=14, fontweight='bold')
        ax.set_ylabel('Price', color='white', fontsize=12)
        ax.set_xticks([0, 1, 2])
        ax.tick_params(colors='white')
        
        # Grid
        ax.grid(True, alpha=0.2, color='white')
        ax.legend(loc='upper left', facecolor='#2a2a2a', edgecolor='white')
        
        # Info text
        info_text = f"""
Pair: {signal.pair}
Direction: {signal.direction}
Entry: {signal.entry}
SL: {signal.stop_loss}
TP: {signal.take_profit}
Ratio: 1:2 Risk/Reward
Confidence: {signal.confidence*100:.0f}%
        """
        ax.text(0.98, 0.02, info_text, transform=ax.transAxes,
               color='white', fontsize=9, verticalalignment='bottom',
               horizontalalignment='right', bbox=dict(boxstyle='round', 
               facecolor='#1a1a1a', alpha=0.8))
        
        # Save to BytesIO
        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', facecolor='#1a1a1a', dpi=100)
        buf.seek(0)
        plt.close()
        
        return buf


class TelegramBot:
    """Interactive Telegram Bot"""
    
    def __init__(self, bot_token: str, chat_id: int):
        self.chat_id = chat_id
        self.bot_token = bot_token
        self.application = Application.builder().token(bot_token).build()
        self.daily_signals = {}
        self.strategy = StrategyAnalyzer()
        self.chart_gen = ChartGenerator()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start_handler))
        self.application.add_handler(CommandHandler("status", self.status_handler))
        self.application.add_handler(CommandHandler("analysis", self.analysis_handler))
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
    
    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
        keyboard = [
            [InlineKeyboardButton("📊 Market Analysis", callback_data='analysis')],
            [InlineKeyboardButton("📈 Current Signals", callback_data='signals')],
            [InlineKeyboardButton("⚙️ Status", callback_data='status')],
            [InlineKeyboardButton("💡 Strategy Info", callback_data='info')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🤖 **Korch Trading Bot**\n\n"
            "AMD+FVG Strategy Analyzer\n\n"
            "Select an option:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def analysis_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Market analysis handler"""
        pairs_status = "\n".join([
            f"• {pair}: Monitoring 1H + 5M"
            for pair in TRADING_PAIRS.keys()
        ])
        
        await update.message.reply_text(
            f"📊 **Market Analysis**\n\n"
            f"Active Pairs:\n{pairs_status}\n\n"
            f"Strategy: AMD + FVG\n"
            f"Risk/Reward: 1:2\n"
            f"Daily Limit: {DAILY_SIGNAL_LIMIT} signals",
            parse_mode='Markdown'
        )
    
    async def status_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Status handler"""
        today = datetime.now().date()
        signals_sent = self.daily_signals.get(today, 0)
        
        status_text = f"""
🟢 **Bot Status: ACTIVE**

📊 Session: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🎯 Signals Today: {signals_sent}/{DAILY_SIGNAL_LIMIT}
⏱️ Check Interval: {SIGNAL_CHECK_INTERVAL}s
🔄 Status: Monitoring markets...

**Pairs:**
• EURUSD - Active
• GBPUSD - Active  
• USDJPY - Active
• AUDUSD - Active
        """
        
        await update.message.reply_text(status_text, parse_mode='Markdown')
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Button callback handler"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'analysis':
            await self.analysis_handler(update, context)
        elif query.data == 'signals':
            await query.edit_message_text("📈 No active signals at the moment.\nWaiting for setup...")
        elif query.data == 'status':
            await self.status_handler(update, context)
        elif query.data == 'info':
            info_text = """
**AMD+FVG Strategy**

📌 **AMD** (Auraprice Movement Direction):
- Detects trend direction on 5M
- Threshold: 70% confidence

📌 **FVG** (Fair Value Gap):
- Identifies price inefficiencies on 1H
- Entry opportunity signal

✅ **Confirmation**: Both conditions aligned
💰 **Risk**: 1% per trade
📊 **Ratio**: 1:2 Reward/Risk

Daily Limit: 5 signals max
            """
            await query.edit_message_text(info_text, parse_mode='Markdown')
    
    async def send_signal(self, signal: Signal) -> bool:
        """Send signal with chart"""
        try:
            today = datetime.now().date()
            if today not in self.daily_signals:
                self.daily_signals[today] = 0
            
            if self.daily_signals[today] >= DAILY_SIGNAL_LIMIT:
                logger.warning("Daily limit reached")
                return False
            
            # Create chart
            chart = self.chart_gen.create_signal_chart(signal)
            
            # Message
            message = f"""
🎯 **TRADING SIGNAL**

📊 **{signal.pair}**
📈 Direction: **{signal.direction}**
⏱️ Timeframe: {signal.timeframe}
🎲 Confidence: {signal.confidence*100:.0f}%

💰 **Entry**: {signal.entry}
🛑 **Stop Loss**: {signal.stop_loss}
🎁 **Take Profit**: {signal.take_profit}

📌 Strategy: {signal.reason}
⏰ Time: {datetime.now().strftime('%H:%M:%S')}
            """
            
            # Send photo with caption
            async with aiohttp.ClientSession() as session:
                bot = Bot(token=TELEGRAM_BOT_TOKEN)
                await bot.send_photo(
                    chat_id=self.chat_id,
                    photo=chart,
                    caption=message,
                    parse_mode='Markdown'
                )
            
            self.daily_signals[today] += 1
            logger.info(f"Signal sent: {signal.pair}")
            return True
            
        except TelegramError as e:
            logger.error(f"Telegram error: {e}")
            return False
    
    async def start(self):
        """Start bot"""
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()


class KorchTradingBot:
    """Main bot orchestrator"""
    
    def __init__(self, bot_token: str, chat_id: int, session_id: str):
        self.api = TradingViewAPI(session_id)
        self.strategy = StrategyAnalyzer()
        self.telegram = TelegramBot(bot_token, chat_id)
        self.is_running = False
    
    async def run(self):
        """Main loop"""
        self.is_running = True
        logger.info("Korch Bot started with interactive features")
        
        # Start Telegram bot
        await self.telegram.start()
        
        while self.is_running:
            try:
                await self._analyze_markets()
                await asyncio.sleep(SIGNAL_CHECK_INTERVAL)
            except Exception as e:
                logger.error(f"Error: {e}")
                await asyncio.sleep(SIGNAL_CHECK_INTERVAL)
    
    async def _analyze_markets(self):
        """Analyze markets"""
        for pair_name, pair_config in TRADING_PAIRS.items():
            try:
                ohlcv_data = {}
                for tf in TIMEFRAMES:
                    data = await self.api.fetch_ohlcv(pair_config['symbol'], tf)
                    ohlcv_data[tf] = data
                
                signal = self.strategy.analyze(ohlcv_data, pair_name)
                
                if signal:
                    await self.telegram.send_signal(signal)
                    
            except Exception as e:
                logger.error(f"Error: {e}")
    
    def stop(self):
        """Stop bot"""
        self.is_running = False
        logger.info("Korch Bot stopped")


async def main():
    """Entry point"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID or not TRADINGVIEW_SESSION_ID:
        logger.error("Missing env vars")
        return
    
    bot = KorchTradingBot(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TRADINGVIEW_SESSION_ID)
    
    try:
        await bot.run()
    except KeyboardInterrupt:
        bot.stop()


if __name__ == '__main__':
>>>>>>> origin/main
    asyncio.run(main())
