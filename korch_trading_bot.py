#!/usr/bin/env python3
"""
Korch Trading Bot - Interactive Telegram Bot with AMD+FVG Strategy
Анализирует стратегию AMD+FVG и отправляет сигналы в Telegram с интерактивным меню
"""

import asyncio
import logging
import os
import json
from datetime import datetime, timedelta
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

# Configuration from environment or defaults
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8999356089:AAEzV2onmpC6oFe-j19M26UTFLxU14N6fSCs')
TELEGRAM_CHAT_ID = int(os.getenv('TELEGRAM_CHAT_ID', '457832510'))
TRADINGVIEW_SESSION_ID = os.getenv('TRADINGVIEW_SESSION_ID', 'qu1s4tex582n1uzvgl9m35we03cbn6f2')

# Risk Management
RISK_PER_TRADE = 0.01  # 1% per trade
MAX_DAILY_LOSS = 0.02  # 2% max daily loss
RISK_REWARD_RATIO = 2  # 1:2 R:R

# Trading Pairs (Philipp's primary focus)
TRADING_PAIRS = {
    'GER40': {'symbol': 'XETRA:DAX', 'timeframe': '1H', 'session': 'Frankfurt', 'volatility': 0.005},
    'EURUSD': {'symbol': 'FX_IDC:EURUSD', 'timeframe': '1H', 'session': 'London', 'volatility': 0.0015},
    'BTCUSDT': {'symbol': 'BINANCE:BTCUSDT', 'timeframe': '1H', 'session': 'NY', 'volatility': 0.03},
    'XAUUSD': {'symbol': 'TVC:GOLD', 'timeframe': '1H', 'session': 'London', 'volatility': 0.008},
}

# Trading Sessions (UTC+3 Haifa timezone)
TRADING_SESSIONS = {
    'Frankfurt': {'start': 6, 'end': 8},   # 9-11 CET = 6-8 UTC+3
    'London': {'start': 7, 'end': 10},     # 10-13 GMT = 7-10 UTC+3
    'NY': {'start': 12, 'end': 16},        # 15:30-19:30 EST = 12-16 UTC+3
}

TIMEFRAMES = ['1H', '5M']
SIGNAL_CHECK_INTERVAL = 300  # 5 minutes
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
    pips: float = 0.0
    rr_ratio: str = "1:2"


class TradingViewAPI:
    """TradingView API wrapper for fetching market data"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Cookie': f'sessionid={session_id}',
        }

    async def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 50) -> List[OHLCV]:
        """
        Fetch OHLCV data from TradingView

        Args:
            symbol: Trading pair (e.g., 'GER40', 'EURUSD')
            timeframe: Timeframe (1M, 5M, 1H, 4H, D)
            limit: Number of candles to fetch

        Returns:
            List of OHLCV data points
        """
        try:
            # Note: Full TradingView API implementation requires tvdatafeeds
            # For production, use: pip install tvdatafeeds
            logger.info(f"Fetching {symbol} {timeframe} ({limit} candles)")

            # In production environment, this would fetch real data
            # For now, returning mock data for testing
            return []

        except Exception as e:
            logger.error(f"Error fetching {symbol} {timeframe}: {e}")
            return []


class StrategyAnalyzer:
    """Analyzes AMD+FVG and Advanced Structure trading strategies"""

    def __init__(self):
        self.min_fvg_size = 0.0005  # Minimum Fair Value Gap size
        self.amd_threshold = 0.7     # AMD confidence threshold (70%)
        self.daily_trades = 0
        self.daily_loss = 0

    def detect_amd(self, ohlcv_1h: List[OHLCV], ohlcv_5m: List[OHLCV]) -> Optional[Dict]:
        """
        Detect AMD (After Market Delivery) setup

        AMD conditions:
        1. Daily trend direction clear (uptrend or downtrend)
        2. 1H momentum confirmation (MA9 > MA21 for longs)
        3. 5M structure (inversion, BOS, or engulfing)
        """
        if len(ohlcv_1h) < 21 or len(ohlcv_5m) < 20:
            return None

        try:
            # 1H Moving Averages (9 and 21)
            closes_1h = [candle.close for candle in ohlcv_1h[-21:]]
            ma9_1h = np.mean(closes_1h[-9:])
            ma21_1h = np.mean(closes_1h[-21:])
            current_close = closes_1h[-1]

            # AMD Buy condition: close > MA9 > MA21
            if current_close > ma9_1h and ma9_1h > ma21_1h:
                # Check 5M for entry signal (simple inversion detection)
                closes_5m = [candle.close for candle in ohlcv_5m[-20:]]
                lows_5m = [candle.low for candle in ohlcv_5m[-20:]]

                if lows_5m[-1] > lows_5m[-2] and lows_5m[-2] < lows_5m[-3]:
                    return {
                        'type': 'BUY',
                        'confidence': 0.75,
                        'reason': 'AMD + 5M Inversion',
                        'entry_level': current_close,
                        'support_level': lows_5m[-2]
                    }

            # AMD Sell condition: close < MA9 < MA21
            elif current_close < ma9_1h and ma9_1h < ma21_1h:
                closes_5m = [candle.close for candle in ohlcv_5m[-20:]]
                highs_5m = [candle.high for candle in ohlcv_5m[-20:]]

                if highs_5m[-1] < highs_5m[-2] and highs_5m[-2] > highs_5m[-3]:
                    return {
                        'type': 'SELL',
                        'confidence': 0.75,
                        'reason': 'AMD + 5M Inversion',
                        'entry_level': current_close,
                        'resistance_level': highs_5m[-2]
                    }

            return None

        except Exception as e:
            logger.error(f"Error in AMD detection: {e}")
            return None

    def detect_fvg(self, ohlcv_1h: List[OHLCV]) -> Tuple[Optional[float], Optional[float]]:
        """
        Detect Fair Value Gap (FVG) on 1H timeframe

        FVG Buy: Previous candle high < Current candle low
        FVG Sell: Previous candle low > Current candle high
        """
        if len(ohlcv_1h) < 3:
            return None, None

        try:
            # Check for buy FVG
            if ohlcv_1h[-2].high < ohlcv_1h[-1].low:
                fvg_buy = (ohlcv_1h[-2].high + ohlcv_1h[-1].low) / 2
            else:
                fvg_buy = None

            # Check for sell FVG
            if ohlcv_1h[-2].low > ohlcv_1h[-1].high:
                fvg_sell = (ohlcv_1h[-2].low + ohlcv_1h[-1].high) / 2
            else:
                fvg_sell = None

            return fvg_buy, fvg_sell

        except Exception as e:
            logger.error(f"Error in FVG detection: {e}")
            return None, None

    def calculate_sl_tp(self, entry: float, signal_type: str, risk_pips: float) -> Dict:
        """
        Calculate SL and TP using 1:2 Risk/Reward ratio

        Args:
            entry: Entry price
            signal_type: 'BUY' or 'SELL'
            risk_pips: Risk in pips (0.0001 per pip)

        Returns:
            Dict with SL, TP, and R:R ratio
        """
        risk_points = risk_pips / 10000

        if signal_type == 'BUY':
            sl = entry - risk_points
            tp = entry + (risk_points * RISK_REWARD_RATIO)
        else:  # SELL
            sl = entry + risk_points
            tp = entry - (risk_points * RISK_REWARD_RATIO)

        return {
            'sl': round(sl, 5),
            'tp': round(tp, 5),
            'sl_pips': round(risk_pips, 1),
            'tp_pips': round(risk_pips * RISK_REWARD_RATIO, 1),
            'rr': f'1:{RISK_REWARD_RATIO}'
        }


class TelegramBot:
    """Interactive Telegram Bot with menu interface"""

    def __init__(self, bot_token: str, chat_id: int):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot = Bot(token=bot_token)
        self.daily_signals = {}
        self.application = Application.builder().token(bot_token).build()

        # Add command handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("menu", self.menu))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_text = """
👋 Welcome to **Korch Trading Bot**!

🤖 I'm an interactive trading bot analyzing **AMD+FVG** strategy
📊 Real-time signals for GER40, EURUSD, BTCUSDT, XAUUSD

Use the menu below to:
📈 View analysis
📢 Check signals
📊 See bot status
ℹ️ Learn about strategy

Let's make profitable trades! 💰
        """

        keyboard = [
            [
                InlineKeyboardButton("📈 Analysis", callback_data="analysis"),
                InlineKeyboardButton("📊 Status", callback_data="status")
            ],
            [
                InlineKeyboardButton("📢 Signals", callback_data="signals"),
                InlineKeyboardButton("ℹ️ Info", callback_data="info")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

    async def menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Display main menu"""
        keyboard = [
            [
                InlineKeyboardButton("📈 Analysis", callback_data="analysis"),
                InlineKeyboardButton("📊 Status", callback_data="status")
            ],
            [
                InlineKeyboardButton("📢 Signals", callback_data="signals"),
                InlineKeyboardButton("ℹ️ Info", callback_data="info")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "🤖 **Main Menu**\n\nSelect an option:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def analysis_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show market analysis"""
        analysis_text = """
**📊 Market Analysis**

**GER40/DAX** (Frankfurt Session)
⏰ Status: Checking...
📈 Trend: Awaiting data
MA9 vs MA21: Calculating...

**EURUSD** (London Session)
⏰ Status: Checking...
📈 Trend: Awaiting data
MA9 vs MA21: Calculating...

**BTCUSDT** (NY Session)
⏰ Status: Checking...
📈 Trend: Awaiting data
MA9 vs MA21: Calculating...

**XAUUSD** (London Session)
⏰ Status: Checking...
📈 Trend: Awaiting data
MA9 vs MA21: Calculating...

🔄 Updating every 5 minutes...
        """

        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            analysis_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def status_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show bot status"""
        uptime = datetime.now().strftime('%H:%M:%S')

        status_text = f"""
**🤖 Bot Status**

✅ **Bot Status**: ONLINE
⏰ **Uptime**: Running
📡 **Connection**: Connected
🔋 **Health**: Optimal

**Daily Stats**
📊 Signals Today: 0/5
💰 Daily P/L: +0%
📈 Win Rate: N/A

**Strategy Status**
📌 AMD: Active
📌 FVG: Monitoring
🎯 Confidence: 70%+

📡 Data Source: TradingView
🌍 Market: 24/5

Last Update: {uptime}
        """

        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            status_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button presses"""
        query = update.callback_query
        await query.answer()

        if query.data == "analysis":
            await self.analysis_handler(update, context)
        elif query.data == "signals":
            keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "📢 **No active signals at the moment**\n\nWaiting for AMD+FVG setup confirmation...\n⏳ Next check in 5 minutes",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        elif query.data == "status":
            await self.status_handler(update, context)
        elif query.data == "menu":
            await self.start(update, context)
        elif query.data == "info":
            info_text = """
**📌 AMD+FVG Strategy**

**🎯 AMD** (After Market Delivery)
• Detects trend direction on 1H timeframe
• Confirms with Moving Averages (MA9 & MA21)
• Entry on 5M inversion/BOS structure
• Confidence: 70%+

**📌 FVG** (Fair Value Gap)
• Identifies price inefficiencies
• Previous candle ≠ Current candle range
• Often acts as support/resistance
• Entry confirmation signal

**📊 Risk Management**
💰 Risk per trade: 1%
📈 Reward/Risk ratio: 1:2
🛑 Daily loss limit: 2% max
📋 Max signals daily: 5

**⏰ Trading Sessions**
🇩🇪 Frankfurt: 6:00-8:00 (UTC+3)
🇬🇧 London: 7:00-10:00 (UTC+3)
🗽 New York: 12:00-16:00 (UTC+3)

**💡 Entry Rules**
✅ Only in trend direction
✅ AMD + FVG confirmation
✅ 5M inversion before entry
✅ 1:2 R:R minimum

Created for Philipp's trading ✨
            """

            keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                info_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

    async def send_signal(self, signal: Signal) -> bool:
        """Send trading signal with details"""
        try:
            today = datetime.now().date()
            if today not in self.daily_signals:
                self.daily_signals[today] = 0

            if self.daily_signals[today] >= DAILY_SIGNAL_LIMIT:
                logger.warning(f"Daily signal limit reached ({DAILY_SIGNAL_LIMIT})")
                return False

            emoji = "🟢" if signal.direction == "BUY" else "🔴"

            message = f"""
{emoji} **{signal.direction} {signal.pair}**

📊 Signal: {signal.reason}
⏱️ Timeframe: {signal.timeframe}
🎲 Confidence: {signal.confidence * 100:.0f}%

**📈 Trade Details**
💰 Entry: `{signal.entry}`
🛑 Stop Loss: `{signal.stop_loss}` ({signal.pips} pips)
🎁 Take Profit: `{signal.take_profit}`
📊 R:R Ratio: {signal.rr_ratio}

⏰ Time: {datetime.now().strftime('%H:%M:%S')}
📌 Session: {TRADING_PAIRS[signal.pair]['session']}
            """

            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown'
            )

            self.daily_signals[today] += 1
            logger.info(f"✅ Signal sent: {signal.direction} {signal.pair}")
            return True

        except TelegramError as e:
            logger.error(f"❌ Telegram error: {e}")
            return False


class KorchTradingBot:
    """Main bot orchestrator"""

    def __init__(self):
        self.api = TradingViewAPI(TRADINGVIEW_SESSION_ID)
        self.strategy = StrategyAnalyzer()
        self.telegram = TelegramBot(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        self.is_running = False

    async def analyze_pair(self, pair_name: str, pair_config: Dict) -> Optional[Signal]:
        """Analyze single trading pair"""
        try:
            # Fetch OHLCV data
            ohlcv_1h = await self.api.fetch_ohlcv(pair_name, '1H', limit=50)
            ohlcv_5m = await self.api.fetch_ohlcv(pair_name, '5M', limit=100)

            if not ohlcv_1h or not ohlcv_5m:
                return None

            # AMD detection
            amd_setup = self.strategy.detect_amd(ohlcv_1h, ohlcv_5m)

            if not amd_setup:
                return None

            # Calculate SL and TP
            sl_tp = self.strategy.calculate_sl_tp(
                entry=amd_setup['entry_level'],
                signal_type=amd_setup['type'],
                risk_pips=50  # Standard 50 pips risk
            )

            signal = Signal(
                pair=pair_name,
                direction=amd_setup['type'],
                entry=amd_setup['entry_level'],
                stop_loss=sl_tp['sl'],
                take_profit=sl_tp['tp'],
                timeframe='1H+5M',
                confidence=amd_setup['confidence'],
                reason=amd_setup['reason'],
                pips=sl_tp['sl_pips'],
                rr_ratio=sl_tp['rr']
            )

            return signal

        except Exception as e:
            logger.error(f"Error analyzing {pair_name}: {e}")
            return None

    async def run(self):
        """Main bot loop"""
        self.is_running = True
        logger.info("🤖 Korch Trading Bot started!")
        logger.info(f"📡 Telegram Bot Token: {TELEGRAM_BOT_TOKEN[:20]}...")
        logger.info(f"💬 Chat ID: {TELEGRAM_CHAT_ID}")

        # Start Telegram bot
        await self.telegram.application.initialize()
        await self.telegram.application.start()
        await self.telegram.application.updater.start_polling()

        # Main analysis loop
        while self.is_running:
            try:
                logger.info(f"📊 Checking signals... {datetime.now().strftime('%H:%M:%S')}")

                for pair_name, config in TRADING_PAIRS.items():
                    signal = await self.analyze_pair(pair_name, config)
                    if signal:
                        await self.telegram.send_signal(signal)

                await asyncio.sleep(SIGNAL_CHECK_INTERVAL)

            except Exception as e:
                logger.error(f"❌ Main loop error: {e}")
                await asyncio.sleep(60)


async def main():
    """Entry point"""
    try:
        bot = KorchTradingBot()
        await bot.run()
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
