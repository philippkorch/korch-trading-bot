"""
Korch Trading Bot - Async Trading Bot with AMD+FVG Strategy
Analyzes multiple timeframes and sends signals via Telegram
"""

import asyncio
import logging
import os
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import aiohttp
from telegram import Bot
from telegram.error import TelegramError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
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


class TelegramSignalSender:
    """Sends signals via Telegram"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot = Bot(token=bot_token)
        self.chat_id = chat_id
        self.daily_signals = {}
    
    async def send_signal(self, signal: Signal) -> bool:
        """Send signal"""
        try:
            today = datetime.now().date()
            if today not in self.daily_signals:
                self.daily_signals[today] = 0
            
            if self.daily_signals[today] >= DAILY_SIGNAL_LIMIT:
                logger.warning("Daily limit reached")
                return False
            
            message = self._format_signal(signal)
            await self.bot.send_message(chat_id=self.chat_id, text=message)
            
            self.daily_signals[today] += 1
            logger.info(f"Signal sent: {signal.pair}")
            return True
            
        except TelegramError as e:
            logger.error(f"Telegram error: {e}")
            return False
    
    def _format_signal(self, signal: Signal) -> str:
        """Format signal message"""
        return f"""
🎯 Trading Signal

📊 Pair: {signal.pair}
📈 Direction: {signal.direction}
⏱️ Timeframe: {signal.timeframe}

💰 Entry: {signal.entry}
🛑 SL: {signal.stop_loss}
🎁 TP: {signal.take_profit}

📌 {signal.reason}
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""


class KorchTradingBot:
    """Main bot"""
    
    def __init__(self, bot_token: str, chat_id: str, session_id: str):
        self.api = TradingViewAPI(session_id)
        self.strategy = StrategyAnalyzer()
        self.telegram = TelegramSignalSender(bot_token, chat_id)
        self.is_running = False
    
    async def run(self):
        """Main loop"""
        self.is_running = True
        logger.info("Korch Bot started")
        
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
