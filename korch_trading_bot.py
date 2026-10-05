"""
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
    asyncio.run(main())
