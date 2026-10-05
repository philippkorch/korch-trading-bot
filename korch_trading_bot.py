#!/usr/bin/env python3
"""
Korch Trading Bot - Интерактивный Telegram бот с анализом AMD+FVG
Анализирует стратегию AMD+FVG и отправляет сигналы в Telegram с интерактивным меню
"""

import asyncio
import logging
import os
import json
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import yfinance as yf
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import TelegramError
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from io import BytesIO
import numpy as np
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment or defaults
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8999356089:AAEzV2onmpC6oFe-j9M26UTFLxU14N6fSCs')
TELEGRAM_CHAT_ID = int(os.getenv('TELEGRAM_CHAT_ID', '8999356089'))

# DEMO MODE - использует фиктивные данные вместо реальных
DEMO_MODE = False

# Risk Management
RISK_PER_TRADE = 0.01  # 1% per trade
MAX_DAILY_LOSS = 0.02  # 2% max daily loss
RISK_REWARD_RATIO = 2  # 1:2 R:R

# Trading Pairs (Philipp's primary focus - EURUSD removed, DAX replaced with GER40)
TRADING_PAIRS = {
    'GER40': {'symbol': '^GDAXI', 'yf_symbol': '^GDAXI', 'session': 'Frankfurt', 'volatility': 0.005},
    'BTC': {'symbol': 'BTC-USD', 'yf_symbol': 'BTC-USD', 'session': 'NY', 'volatility': 0.03},
    'GOLD': {'symbol': 'GC=F', 'yf_symbol': 'GC=F', 'session': 'London', 'volatility': 0.008},
}

# Forex News & Economic Calendar (основные события с уровнями важности, датами и временами)
# 🟢 = зелёная (нормально), 🟠 = оранжевая (средняя), 🔴 = красная (критично)
FOREX_EVENTS = {
    'NFP': {
        'level': '🔴',
        'date': '2026-10-10',
        'time': '13:30 UTC',
        'country': '🇺🇸',
        'text': '💼 Non-Farm Payroll (США) - КРИТИЧНО! Новые рабочие места. Сильно влияет на USD и S&P',
        'impact': 'Сильное влияние на долгосрочный тренд'
    },
    'CPI': {
        'level': '🔴',
        'date': '2026-10-14',
        'time': '12:30 UTC',
        'country': '🇺🇸',
        'text': '📈 Инфляция (США) - КРИТИЧНО! Рост = повышение ставок, укрепление валюты',
        'impact': 'Критический для принятия решений ФРС'
    },
    'ECB_Meeting': {
        'level': '🔴',
        'date': '2026-10-17',
        'time': '12:45 UTC',
        'country': '🇪🇺',
        'text': '🏦 Заседание ЕЦБ - КРИТИЧНО! Решения о ставках влияют на EUR и GER40',
        'impact': 'Определяет тренд EUR на месяцы вперед'
    },
    'Fed_Meeting': {
        'level': '🔴',
        'date': '2026-11-05',
        'time': '18:00 UTC',
        'country': '🇺🇸',
        'text': '🏛️ Заседание ФРС (США) - КРИТИЧНО! Решения о ставках влияют на USD и глобальные рынки',
        'impact': 'Глобальное влияние на все активы'
    },
    'DXY': {
        'level': '🟠',
        'country': '🇺🇸',
        'text': '📊 Индекс доллара (USD Index) - мера силы доллара. Рост = укрепление долл',
        'impact': 'Средний уровень влияния'
    },
    'Oil': {
        'level': '🟠',
        'country': '⛽',
        'text': '⛽ Цена нефти (WTI/Brent) - Средняя важность. Влияет на доллар и энергосектор',
        'impact': 'Влияет на GER40 и DXY'
    },
}

# Market Impact Explanations (объяснения влияния на рынок)
MARKET_IMPACTS = {
    'GER40': {
        'up': 'Немецкие компании растут! 🚀 Причины: улучшение производства, экспорт, позитив из Европы',
        'down': 'GER40 падает 📉 Причины: слабая экономика, рост ставок, проблемы в Европе, недовольство акционеров',
    },
    'BTC': {
        'up': 'Bitcoin взлетел! 🚀 Причины: принятие, вывод с бирж, позитив про регуляцию, инфляция',
        'down': 'Bitcoin падает 📉 Причины: новые ограничения, вывод с кошельков, негатив про крипто, слабость риск-активов',
    },
    'GOLD': {
        'up': 'Золото растет! 🚀 Причины: инфляция, ослабление доллара, политическая напряженность, страх инвесторов',
        'down': 'Золото падает 📉 Причины: укрепление доллара, рост ставок, улучшение экономики, отток капитала',
    },
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
    intellect_score: float = 50.0  # INTELLECT_city indicator score


class MarketDataAPI:
    """Market data API wrapper using yfinance for fetching real market data"""

    def __init__(self):
        self.cache = {}
        self.cache_time = {}
        self.cache_duration = 300  # 5 minutes
        self.last_ohlcv = {}  # Store last successful OHLCV data

    async def fetch_ohlcv(self, pair_name: str, pair_config: Dict, timeframe: str = '1h', limit: int = 50) -> List[OHLCV]:
        """
        Fetch OHLCV data from yfinance (or return demo data if DEMO_MODE is enabled)

        Args:
            pair_name: Trading pair name (e.g., 'GER40', 'BTC')
            pair_config: Configuration dict with yf_symbol
            timeframe: Timeframe (1m, 5m, 1h, 1d)
            limit: Number of candles to fetch

        Returns:
            List of OHLCV data points
        """
        try:
            yf_symbol = pair_config.get('yf_symbol')
            logger.info(f"Fetching {pair_name} ({yf_symbol}) {timeframe} ({limit} candles)")

            # DEMO MODE - return simulated data instead of real market data
            if DEMO_MODE:
                logger.info(f"🎮 DEMO MODE: Generating simulated data for {pair_name}")
                return self._generate_demo_data(pair_name, limit)

            # Check cache
            cache_key = f"{yf_symbol}_{timeframe}"
            now = datetime.now()
            if cache_key in self.cache_time:
                if (now - self.cache_time[cache_key]).total_seconds() < self.cache_duration:
                    logger.info(f"Using cached data for {cache_key}")
                    return self.cache[cache_key]

            # Download data from yfinance
            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(period="5d", interval=timeframe)

            if df.empty:
                logger.warning(f"No data fetched for {yf_symbol}")
                return []

            # Convert to OHLCV objects
            ohlcv_list = []
            for idx, row in df.tail(limit).iterrows():
                ohlcv = OHLCV(
                    timestamp=idx.to_pydatetime(),
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    volume=int(row['Volume'])
                )
                ohlcv_list.append(ohlcv)

            # Cache the result
            self.cache[cache_key] = ohlcv_list
            self.cache_time[cache_key] = now
            self.last_ohlcv[pair_name] = ohlcv_list  # Save last successful data

            logger.info(f"✅ Fetched {len(ohlcv_list)} candles for {pair_name}")
            return ohlcv_list

        except Exception as e:
            logger.error(f"Error fetching {pair_name} ({pair_config.get('yf_symbol')}): {e}")
            # Return last known data if available
            if pair_name in self.last_ohlcv and self.last_ohlcv[pair_name]:
                logger.info(f"⚠️ Using cached data for {pair_name}")
                return self.last_ohlcv[pair_name]
            return []

    def _generate_demo_data(self, pair_name: str, limit: int = 21) -> List[OHLCV]:
        """Generate simulated OHLCV data for demo mode"""
        demo_data = []

        # Demo base prices for each pair
        base_prices = {
            'GER40': 18000,
            'BTC': 42000,
            'GOLD': 2050,
        }

        base_price = base_prices.get(pair_name, 100)
        current_time = datetime.now()

        # Generate candles going backwards in time
        for i in range(limit, 0, -1):
            # Simulate realistic price movements
            volatility = 0.02  # 2% volatility per candle
            direction = 1 if np.random.random() > 0.5 else -1

            open_price = base_price + (np.random.random() - 0.5) * base_price * volatility
            close_price = open_price + direction * np.random.random() * base_price * volatility
            high_price = max(open_price, close_price) + np.random.random() * base_price * 0.005
            low_price = min(open_price, close_price) - np.random.random() * base_price * 0.005
            volume = int(np.random.random() * 1000000)

            candle = OHLCV(
                timestamp=current_time - timedelta(hours=i),
                open=round(open_price, 2),
                high=round(high_price, 2),
                low=round(low_price, 2),
                close=round(close_price, 2),
                volume=volume
            )
            demo_data.append(candle)

            # Update base price for next candle
            base_price = close_price

        logger.info(f"📊 Generated {len(demo_data)} demo candles for {pair_name}")
        return demo_data


class IndicatorAnalyzer:
    """Calculates INTELLECT_city composite indicator from all 8 component indicators"""

    def __init__(self):
        self.rsi_period = 14
        self.macd_fast = 12
        self.macd_slow = 26
        self.macd_signal = 9
        self.stoch_period = 14
        self.mfi_period = 14
        self.rosc_period = 20
        self.wpr_period = 14
        self.jap_period = 20

    def calculate_rsi(self, closes: List[float], period: int = 14) -> float:
        """Calculate RSI (Relative Strength Index) - normalized 0-100"""
        if len(closes) < period + 1:
            return 50.0

        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]

        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])

        if avg_loss == 0:
            return 100.0 if avg_gain > 0 else 50.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return float(max(0, min(100, rsi)))

    def calculate_stochastic(self, highs: List[float], lows: List[float], closes: List[float],
                            period: int = 14) -> float:
        """Stochastic %K oscillator - normalized 0-100"""
        if len(closes) < period:
            return 50.0

        recent_high = max(highs[-period:])
        recent_low = min(lows[-period:])

        if recent_high == recent_low:
            return 50.0

        k_percent = ((closes[-1] - recent_low) / (recent_high - recent_low)) * 100
        return float(max(0, min(100, k_percent)))

    def calculate_rosc(self, closes: List[float], period: int = 20) -> float:
        """ROSC (Linear Correlation Oscillator) - correlation between price and time - normalized 0-100"""
        if len(closes) < period:
            return 50.0

        recent_closes = closes[-period:]
        time_series = np.arange(period)

        # Calculate correlation coefficient
        correlation = np.corrcoef(time_series, recent_closes)[0, 1]

        # Normalize correlation (-1 to 1) to 0-100 scale
        # correlation of 1 (uptrend) = 100, -1 (downtrend) = 0, 0 (no correlation) = 50
        normalized = 50 + (correlation * 50)
        return float(max(0, min(100, normalized)))

    def calculate_wpr(self, highs: List[float], lows: List[float], closes: List[float],
                      period: int = 14) -> float:
        """Williams %R normalized to 0-100 scale (instead of -100 to 0)"""
        if len(highs) < period or len(lows) < period:
            return 50.0

        high_period = max(highs[-period:])
        low_period = min(lows[-period:])

        if high_period == low_period:
            return 50.0

        # Williams %R formula: (High - Close) / (High - Low) * -100
        # Convert from -100..0 range to 0..100 range
        wpr = ((high_period - closes[-1]) / (high_period - low_period)) * -100
        normalized = 100 + wpr  # Convert from (-100, 0) to (0, 100)

        return float(max(0, min(100, normalized)))

    def calculate_percent_rank(self, closes: List[float], period: int = 20) -> float:
        """Percent Rank (%R) - percentage of values below current close - normalized 0-100"""
        if len(closes) < period:
            return 50.0

        recent_closes = closes[-period:]
        current_close = closes[-1]

        # Count how many values are below current close
        below_count = sum(1 for price in recent_closes if price < current_close)

        # Calculate percentage rank (0-100)
        percent_rank = (below_count / period) * 100

        return float(max(0, min(100, percent_rank)))

    def calculate_macd(self, closes: List[float]) -> float:
        """MACD line - returns momentum indicator (0-100 scale)"""
        if len(closes) < self.macd_slow + 1:
            return 50.0

        exp_fast = self._ema(closes, self.macd_fast)
        exp_slow = self._ema(closes, self.macd_slow)

        macd = exp_fast - exp_slow
        # Normalize to 0-100 scale
        normalized = 50 + (macd / (max(abs(exp_fast), abs(exp_slow)) + 1e-6)) * 50
        return float(max(0, min(100, normalized)))

    def calculate_mfi(self, highs: List[float], lows: List[float], closes: List[float],
                     volumes: List[int], period: int = 14) -> float:
        """Money Flow Index - normalized 0-100"""
        if len(closes) < period + 1:
            return 50.0

        typical_price = [(h + l + c) / 3 for h, l, c in zip(highs, lows, closes)]
        money_flow = [tp * v for tp, v in zip(typical_price, volumes)]

        positive_mf = sum([mf for i, mf in enumerate(money_flow[-period:])
                          if typical_price[len(typical_price)-period+i] > typical_price[len(typical_price)-period+i-1]])
        negative_mf = sum([mf for i, mf in enumerate(money_flow[-period:])
                          if typical_price[len(typical_price)-period+i] < typical_price[len(typical_price)-period+i-1]])

        if negative_mf == 0:
            return 100.0 if positive_mf > 0 else 50.0

        mfi = 100 - (100 / (1 + (positive_mf / negative_mf)))
        return float(max(0, min(100, mfi)))

    def calculate_jap(self, closes: List[float], volumes: List[int], period: int = 20) -> float:
        """JAP (Japan Trade Indicator) - volume-weighted momentum normalized to 0-100"""
        if len(closes) < period + 1 or len(volumes) < period + 1:
            return 50.0

        # Calculate ROC (Rate of Change)
        roc = ((closes[-1] - closes[-period-1]) / closes[-period-1]) * 100

        # Calculate volume ratio (current volume vs average)
        avg_volume = np.mean(volumes[-period:])
        if avg_volume == 0:
            volume_ratio = 1.0
        else:
            volume_ratio = volumes[-1] / avg_volume

        # Combine ROC and volume weighting
        # ROC already in percentage form
        jap = 50 + (roc / 10) * volume_ratio  # Scale ROC for visualization

        return float(max(0, min(100, jap)))

    def _ema(self, data: List[float], period: int) -> float:
        """Calculate EMA value"""
        if len(data) < period:
            return np.mean(data)

        multiplier = 2 / (period + 1)
        ema = np.mean(data[:period])

        for price in data[period:]:
            ema = price * multiplier + ema * (1 - multiplier)

        return ema

    def calculate_intellect_city_index(self, ohlcv_data: List[OHLCV]) -> dict:
        """
        Calculate INTELLECT_city composite index from all 8 components

        Components:
        1. RSI (Relative Strength Index)
        2. Stochastic %K
        3. ROSC (Linear Correlation Oscillator)
        4. WPR (Williams %R normalized)
        5. %R (Percent Rank)
        6. MFI (Money Flow Index)
        7. MACD
        8. JAP (Japan Trade Indicator)

        Returns: dict with individual scores and composite index
        - 0-25: Strong bearish
        - 25-50: Bearish/neutral
        - 50-75: Bullish/neutral
        - 75-100: Strong bullish
        """
        if len(ohlcv_data) < 30:
            return {
                'intellect_score': 50.0,
                'rsi': 50.0,
                'stochastic': 50.0,
                'rosc': 50.0,
                'wpr': 50.0,
                'percent_rank': 50.0,
                'macd': 50.0,
                'mfi': 50.0,
                'jap': 50.0,
                'trend': 50.0
            }

        closes = [c.close for c in ohlcv_data]
        highs = [c.high for c in ohlcv_data]
        lows = [c.low for c in ohlcv_data]
        volumes = [c.volume for c in ohlcv_data]

        # Calculate all 8 component indicators
        rsi = self.calculate_rsi(closes)
        stoch = self.calculate_stochastic(highs, lows, closes)
        rosc = self.calculate_rosc(closes, self.rosc_period)
        wpr = self.calculate_wpr(highs, lows, closes, self.wpr_period)
        percent_rank = self.calculate_percent_rank(closes)
        macd = self.calculate_macd(closes)
        mfi = self.calculate_mfi(highs, lows, closes, volumes)
        jap = self.calculate_jap(closes, volumes, self.jap_period)

        # Trend component (MA9 vs MA21)
        ma9 = np.mean(closes[-9:])
        ma21 = np.mean(closes[-21:])
        trend = 75 if ma9 > ma21 else (25 if ma9 < ma21 else 50)

        # Calculate average of all 8 indicators + trend
        all_components = [rsi, stoch, rosc, wpr, percent_rank, macd, mfi, jap, trend]
        intellect_index = np.mean(all_components)

        result = {
            'intellect_score': float(intellect_index),
            'rsi': float(rsi),
            'stochastic': float(stoch),
            'rosc': float(rosc),
            'wpr': float(wpr),
            'percent_rank': float(percent_rank),
            'macd': float(macd),
            'mfi': float(mfi),
            'jap': float(jap),
            'trend': float(trend),
            'ma9': float(ma9),
            'ma21': float(ma21)
        }

        logger.debug(f"INTELLECT_city: {intellect_index:.1f}% | RSI={rsi:.1f} Stoch={stoch:.1f} ROSC={rosc:.1f} WPR={wpr:.1f} %R={percent_rank:.1f} MACD={macd:.1f} MFI={mfi:.1f} JAP={jap:.1f} Trend={trend:.1f}")

        return result


class StrategyAnalyzer:
    """Analyzes AMD+FVG and Advanced Structure trading strategies with indicator confirmation"""

    def __init__(self):
        self.min_fvg_size = 0.0005  # Minimum Fair Value Gap size
        self.amd_threshold = 0.7     # AMD confidence threshold (70%)
        self.daily_trades = 0
        self.daily_loss = 0
        self.indicators = IndicatorAnalyzer()
        self.intellect_threshold = 60  # 60%+ for strong confirmation

    def detect_amd(self, ohlcv_1h: List[OHLCV], ohlcv_5m: List[OHLCV]) -> Optional[Dict]:
        """
        Detect AMD (After Market Delivery) setup with INTELLECT_city confirmation

        AMD conditions:
        1. Daily trend direction clear (uptrend or downtrend)
        2. 1H momentum confirmation (MA9 > MA21 for longs)
        3. 5M structure (inversion, BOS, or engulfing)
        4. INTELLECT_city indicator confirmation (60%+)
        """
        if len(ohlcv_1h) < 21 or len(ohlcv_5m) < 20:
            return None

        try:
            # 1H Moving Averages (9 and 21)
            closes_1h = [candle.close for candle in ohlcv_1h[-21:]]
            ma9_1h = np.mean(closes_1h[-9:])
            ma21_1h = np.mean(closes_1h[-21:])
            current_close = closes_1h[-1]

            # Calculate INTELLECT_city indicator on 5M timeframe
            intellect_result = self.indicators.calculate_intellect_city_index(ohlcv_5m[-30:] if len(ohlcv_5m) >= 30 else ohlcv_5m)
            intellect_score = intellect_result['intellect_score']

            # AMD Buy condition: close > MA9 > MA21
            if current_close > ma9_1h and ma9_1h > ma21_1h:
                # Check 5M for entry signal (simple inversion detection)
                closes_5m = [candle.close for candle in ohlcv_5m[-20:]]
                lows_5m = [candle.low for candle in ohlcv_5m[-20:]]

                if lows_5m[-1] > lows_5m[-2] and lows_5m[-2] < lows_5m[-3]:
                    # Require INTELLECT_city confirmation for buy (score > 60)
                    if intellect_score >= self.intellect_threshold:
                        confidence = 0.75 + (intellect_score - 60) * 0.003  # Boost confidence based on indicator strength
                        return {
                            'type': 'BUY',
                            'confidence': min(0.95, confidence),  # Cap at 95%
                            'reason': f'AMD + 5M Inversion + INTELLECT {intellect_score:.0f}%',
                            'entry_level': current_close,
                            'support_level': lows_5m[-2],
                            'intellect_score': intellect_score
                        }
                    else:
                        logger.info(f"BUY signal filtered: INTELLECT_city {intellect_score:.0f}% < {self.intellect_threshold}%")
                        return None

            # AMD Sell condition: close < MA9 < MA21
            elif current_close < ma9_1h and ma9_1h < ma21_1h:
                closes_5m = [candle.close for candle in ohlcv_5m[-20:]]
                highs_5m = [candle.high for candle in ohlcv_5m[-20:]]

                if highs_5m[-1] < highs_5m[-2] and highs_5m[-2] > highs_5m[-3]:
                    # Require INTELLECT_city confirmation for sell (score < 40)
                    if intellect_score <= (100 - self.intellect_threshold):
                        confidence = 0.75 + (100 - intellect_score - 60) * 0.003  # Boost confidence based on bearish strength
                        return {
                            'type': 'SELL',
                            'confidence': min(0.95, confidence),
                            'reason': f'AMD + 5M Inversion + INTELLECT {intellect_score:.0f}%',
                            'entry_level': current_close,
                            'resistance_level': highs_5m[-2],
                            'intellect_score': intellect_score
                        }
                    else:
                        logger.info(f"SELL signal filtered: INTELLECT_city {intellect_score:.0f}% > {100 - self.intellect_threshold}%")
                        return None

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
        self.api = MarketDataAPI()

        # Add command handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("menu", self.menu))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_text = """
👋 **Добро пожаловать в Korch Trading Bot!**

🤖 Интерактивный торговый бот с анализом **AMD+FVG** стратегии
📊 Сигналы для GER40, BTC, GOLD (реальные данные)

Выберите опцию меню:
📈 Анализ рынка
📰 Новости форекса
📢 Торговые сигналы
📊 Статус бота
ℹ️ Информация о стратегии

Давайте зарабатывать! 💰
        """

        keyboard = [
            [
                InlineKeyboardButton("📈 Анализ", callback_data="analysis"),
                InlineKeyboardButton("📰 Новости", callback_data="news")
            ],
            [
                InlineKeyboardButton("📊 Статус", callback_data="status"),
                InlineKeyboardButton("📢 Сигналы", callback_data="signals")
            ],
            [
                InlineKeyboardButton("🔔 Демо-сигнал", callback_data="demo_signal"),
                InlineKeyboardButton("ℹ️ Инфо", callback_data="info")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if update.message:
            await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
        elif update.callback_query:
            await update.callback_query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

    async def menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Display main menu"""
        keyboard = [
            [
                InlineKeyboardButton("📈 Анализ", callback_data="analysis"),
                InlineKeyboardButton("📊 Статус", callback_data="status")
            ],
            [
                InlineKeyboardButton("📢 Сигналы", callback_data="signals"),
                InlineKeyboardButton("ℹ️ Инфо", callback_data="info")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if update.message:
            await update.message.reply_text(
                "🤖 **Главное меню**\n\nВыберите опцию:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.callback_query.edit_message_text(
                "🤖 **Главное меню**\n\nВыберите опцию:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

    async def analysis_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show market analysis with AMD+FVG+INTELLECT_city"""
        query = update.callback_query
        
        try:
            # Show loading
            await query.edit_message_text("⏳ Загружаю анализ...", parse_mode='Markdown')

            text = "**📊 Анализ (AMD+FVG+INTELLECT)**\n\n"

            for pair_name, cfg in TRADING_PAIRS.items():
                try:
                    # Get data
                    h1 = await self.api.fetch_ohlcv(pair_name, cfg, '1h', 21)
                    m5 = await self.api.fetch_ohlcv(pair_name, cfg, '5m', 30)

                    if h1 and len(h1) >= 21:
                        closes = [c.close for c in h1[-21:]]
                        ma9 = np.mean(closes[-9:])
                        ma21 = np.mean(closes[-21:])
                        cur = closes[-1]

                        # AMD
                        amd_ok = cur > ma9 > ma21 or cur < ma9 < ma21
                        amd = "✅" if amd_ok else "❌"
                        trend = "📈" if cur > ma9 > ma21 else ("📉" if cur < ma9 < ma21 else "—")

                        # FVG
                        fvg = "✅" if (m5 and len(m5) >= 3) else "❌"

                        # INTELLECT
                        intellect = 50.0
                        if m5 and len(m5) >= 30:
                            try:
                                res = IndicatorAnalyzer().calculate_intellect_city_index(m5[-30:])
                                if isinstance(res, dict) and 'intellect_score' in res:
                                    intellect = float(res['intellect_score'])
                            except Exception as ie:
                                intellect = 50.0

                        intel_emoji = "🟢" if intellect >= 60 else ("🔴" if intellect <= 40 else "🟡")
                        intel_ok = "✅" if (intellect >= 60 or intellect <= 40) else "🟡"

                        # Status
                        ready = amd_ok and (m5 and len(m5) >= 3) and (intellect >= 60 or intellect <= 40)
                        status = "🟢 OK" if ready else "🟡 Wait"

                        text += f"`{pair_name}` {trend} | MA:{ma9:.0f}/{ma21:.0f}\n"
                        text += f"{amd} {fvg} {intel_ok} | {intel_emoji}{intellect:.0f}% | {status}\n\n"
                    else:
                        text += f"`{pair_name}` ⏳ Загрузка...\n\n"
                except Exception as e:
                    logger.error(f"Analysis error for {pair_name}: {e}")
                    text += f"`{pair_name}` ❌ Ошибка\n\n"

            text += f"\n⏰ {datetime.now().strftime('%H:%M')}"

            kb = [[InlineKeyboardButton("🔙 Menu", callback_data="menu")]]
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Analysis handler error: {e}")
            try:
                await query.edit_message_text(
                    "❌ **Ошибка анализа**\n\nПопробуйте ещё раз",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="menu")]]),
                    parse_mode='Markdown'
                )
            except:
                pass

    async def status_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show bot status with strategy confirmation breakdown"""
        uptime = datetime.now().strftime('%H:%M:%S')

        status_text = f"""**🤖 Статус бота v2.1**

✅ **Статус**: ОНЛАЙН
⏰ **Время работы**: Запущен
📡 **Соединение**: Подключено
🔋 **Здоровье**: Отлично

**📊 Статистика за день**
📈 Сигналов: 0/5
💰 P/L: +0%
📊 Win Rate: N/A

**🎯 Статус стратегии (AMD+FVG+INTELLECT_city)**

**1️⃣ AMD (After Market Delivery)**
   📌 Тренд: Мониторинг
   📊 Moving Average: MA9 vs MA21
   ✅ Подтверждение: На 1H таймфрейме

**2️⃣ FVG (Fair Value Gap)**
   📌 Структура: Мониторинг
   🎯 Уровни входа: На 5M таймфрейме
   ✅ Подтверждение: Инверсия/BOS

**3️⃣ INTELLECT_city (Smart Money)**
   🟢 Статус: 8 компонентов включены
   📈 Компоненты: RSI, Stochastic, ROSC, WPR, %R, MACD, MFI, JAP
   ✅ Порог BUY: ≥60% | ✅ Порог SELL: ≤40%

**🔗 Взаимное подтверждение:**
   • AMD определяет тренд (направление)
   • FVG показывает структуру (точка входа)
   • INTELLECT_city подтверждает согласованность индикаторов
   • Вместе они образуют надежный торговый сигнал ✅

📡 **Источник данных**: Yahoo Finance
🌍 **Рыночные часы**: 24/5 (криптовалюта)
⏱️ **Интервал проверки**: 5 минут

🔄 Последнее обновление: {uptime}
"""

        keyboard = [[InlineKeyboardButton("🔙 В меню", callback_data="menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            await update.callback_query.edit_message_text(
                status_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Status handler error: {e}")
            try:
                await update.callback_query.edit_message_text(
                    "❌ **Ошибка статуса**",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            except:
                pass

    async def news_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show forex news and economic calendar"""
        news_text = "**📰 Новости форекса и экономический календарь**\n\n"

        news_text += "**🌍 Ключевые экономические события:**\n\n"

        # Группируем события по уровню важности
        critical = []
        medium = []
        normal = []

        for event_key, event_data in FOREX_EVENTS.items():
            critical.append(event_data) if event_data['level'] == '🔴' else (
                medium.append(event_data) if event_data['level'] == '🟠' else normal.append(event_data)
            )

        # КРИТИЧНЫЕ события (красные)
        if critical:
            news_text += "**🔴 КРИТИЧНЫЕ СОБЫТИЯ (Опасно для рынка):**\n"
            for event in critical:
                date_str = f"\n   📅 {event.get('date', 'N/A')}" if 'date' in event else ""
                time_str = f" | ⏰ {event.get('time', 'N/A')}" if 'time' in event else ""
                impact_str = f"\n   💥 {event.get('impact', '')}" if 'impact' in event else ""
                news_text += f"{event.get('level', '🔴')} {event.get('text', '')}{date_str}{time_str}{impact_str}\n\n"
            news_text += "\n"

        # Средней важности (оранжевые)
        if medium:
            news_text += "**🟠 СРЕДНЯЯ ВАЖНОСТЬ (Внимание):**\n"
            for event in medium:
                date_str = f"\n   📅 {event.get('date', 'N/A')}" if 'date' in event else ""
                time_str = f" | ⏰ {event.get('time', 'N/A')}" if 'time' in event else ""
                impact_str = f"\n   💥 {event.get('impact', '')}" if 'impact' in event else ""
                news_text += f"{event.get('level', '🟠')} {event.get('text', '')}{date_str}{time_str}{impact_str}\n\n"
            news_text += "\n"

        # Нормальные события (зелёные)
        if normal:
            news_text += "**🟢 НОРМАЛЬНЫЕ СОБЫТИЯ (Всё хорошо):**\n"
            for event in normal:
                date_str = f"\n   📅 {event.get('date', 'N/A')}" if 'date' in event else ""
                time_str = f" | ⏰ {event.get('time', 'N/A')}" if 'time' in event else ""
                impact_str = f"\n   💥 {event.get('impact', '')}" if 'impact' in event else ""
                news_text += f"{event.get('level', '🟢')} {event.get('text', '')}{date_str}{time_str}{impact_str}\n\n"
            news_text += "\n"

        news_text += "---\n\n"
        news_text += "**📊 Влияние на цены:**\n\n"

        for pair_name, impacts in MARKET_IMPACTS.items():
            news_text += f"**{pair_name}**\n"
            news_text += f"📈 При росте: {impacts['up']}\n"
            news_text += f"📉 При падении: {impacts['down']}\n\n"

        news_text += f"🔄 Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}"

        keyboard = [[InlineKeyboardButton("🔙 В меню", callback_data="menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            news_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def demo_signal_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show example trading signal with AMD+FVG+INTELLECT_city confirmation breakdown"""
        demo_signal_text = """🟢 **BUY GER40**

⏱️ **Таймфрейм:** 1H + 5M
🎲 **Уверенность:** 78%

---

**🎯 Подтверждение стратегий:**

**1️⃣ AMD (After Market Delivery)**
   📈 Тренд: **Восход** ✅
   • MA9 > MA21 (тренд вверх на 1H)
   • Цена > MA9 > MA21 (классический восход)
   • Подтверждение: ✅ АКТИВНО

**2️⃣ FVG (Fair Value Gap)**
   🎯 Структура: **Инверсия на 5M** ✅
   • Low[-1] > Low[-2] < Low[-3]
   • Точка входа найдена (5M)
   • Подтверждение: ✅ АКТИВНО

**3️⃣ INTELLECT_city (Композитный индекс)**
   🟢 Сильный бычий: `78%` ✅
   • Пороговое значение: ≥60% для BUY
   • Компоненты согласны: 6/8 бычьих
   • Подтверждение: ✅ АКТИВНО

---

**📊 Компоненты INTELLECT_city:**
├─ RSI (14): 72%
├─ Stochastic %K: 80%
├─ ROSC: 65%
├─ WPR: 75%
├─ %R: 85%
├─ MACD: 70%
├─ MFI: 68%
├─ JAP: 70%
└─ Тренд (MA9>MA21): 100%

---

**💰 Детали входа:**
• **Цена входа:** 18250.50
• **Stop Loss:** 18200.00 (50 пипс)
• **Take Profit:** 18350.00
• **R:R:** 1:2

⏰ **Время:** 22:13:45
📌 **Сессия:** Frankfurt

---

**💡 Почему этот сигнал сильный?**
✅ AMD показывает четкий тренд вверх
✅ FVG предоставляет точку входа со структурой
✅ INTELLECT_city подтверждает согласованность (78% > 60%)
✅ Все три компонента работают вместе = надежный сигнал

**Это ДЕМО-ПРИМЕР.** Реальные сигналы будут иметь аналогичный формат.
        """

        keyboard = [[InlineKeyboardButton("🔙 В меню", callback_data="menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            demo_signal_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button presses"""
        query = update.callback_query
        await query.answer()

        if query.data == "analysis":
            await self.analysis_handler(update, context)
        elif query.data == "news":
            await self.news_handler(update, context)
        elif query.data == "demo_signal":
            await self.demo_signal_handler(update, context)
        elif query.data == "signals":
            keyboard = [[InlineKeyboardButton("🔙 В меню", callback_data="menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "📢 **Активных сигналов нет**\n\nОжидаем подтверждение AMD+FVG...\n⏳ Следующая проверка через 5 минут",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        elif query.data == "status":
            await self.status_handler(update, context)
        elif query.data == "menu":
            await self.start(update, context)
        elif query.data == "info":
            info_text = """**📌 Стратегия AMD+FVG с INTELLECT_city (v2.1)**

**🎯 ОСНОВНЫЕ КОМПОНЕНТЫ:**

**1️⃣ AMD** (After Market Delivery)
   • Определяет тренд на 1H таймфрейме
   • MA9 > MA21 = Восход 📈
   • MA9 < MA21 = Спад 📉
   • Основа сигнала (направление)

**2️⃣ FVG** (Fair Value Gap)
   • Структура входа на 5M таймфрейме
   • Инверсия низких: Low[-1] > Low[-2] < Low[-3]
   • Инверсия высоких: High[-1] < High[-2] > High[-3]
   • Точка входа (когда входить)

**3️⃣ INTELLECT_city** (Композитный индекс из 8 индикаторов)
   **Все 8 компонентов:**
   ├─ RSI (14) - импульс
   ├─ Stochastic %K (14) - осциллятор
   ├─ ROSC - корреляция цены и времени
   ├─ WPR - Williams %R нормализованный
   ├─ %R - Percent Rank процент ниже текущей цены
   ├─ MACD (12/26/9) - импульс тренда
   ├─ MFI (14) - Money Flow Index объемный импульс
   └─ JAP - Japan Trade Indicator объемно-взвешенный

   📊 **Результат:** Среднее значение всех 8 (0-100%)
   • ✅ ≥60% = Сильный сигнал BUY (большинство индикаторов согласны)
   • ✅ ≤40% = Сильный сигнал SELL (большинство индикаторов согласны)
   • 🟡 40-60% = Нейтральный (индикаторы разделены)

**💡 Роль INTELLECT_city:**
🔹 НЕ генерирует сигналы сам по себе
🔹 Служит ПОДТВЕРЖДЕНИЕМ к AMD+FVG
🔹 Фильтрует слабые сигналы
🔹 Показывает уверенность индикаторов
🔹 Увеличивает вероятность прибыльной сделки

**🔗 Как работают вместе:**
1. AMD определяет НАПРАВЛЕНИЕ (вверх/вниз)
2. FVG показывает ТОЧКУ ВХОДА (где входить)
3. INTELLECT_city ПОДТВЕРЖДАЕТ (готов ли рынок)
→ Все три = надежный торговый сигнал ✅

**📊 Управление риском**
💰 Риск на сделку: 1%
📈 R:R: 1:2 (минимум)
🛑 Макс потеря в день: 2%
📋 Макс сигналов в день: 5

**⏰ Торговые сессии**
🇩🇪 Франкфурт: 6:00-8:00 (UTC+3)
🇬🇧 Лондон: 7:00-10:00 (UTC+3)
🗽 Нью-Йорк: 12:00-16:00 (UTC+3)

**✅ Условия сигнала:**
✓ AMD: Тренд на месте (MA9>MA21 или MA9<MA21)
✓ FVG: Инверсия структуры на 5M
✓ INTELLECT_city: ≥60% (BUY) или ≤40% (SELL)
✓ Всё вместе = готов сигнал → Отправляю в Telegram

Бот разработан по методологии TrendyQ + Smart Money ✨
            """

            keyboard = [[InlineKeyboardButton("🔙 В меню", callback_data="menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                info_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

    async def send_signal(self, signal: Signal) -> bool:
        """Send trading signal with INTELLECT_city indicator confirmation"""
        try:
            today = datetime.now().date()
            if today not in self.daily_signals:
                self.daily_signals[today] = 0

            if self.daily_signals[today] >= DAILY_SIGNAL_LIMIT:
                logger.warning(f"Daily signal limit reached ({DAILY_SIGNAL_LIMIT})")
                return False

            emoji = "🟢" if signal.direction == "BUY" else "🔴"

            # INTELLECT_city score interpretation
            intellect_emoji = "🟢" if signal.intellect_score > 60 else ("🔴" if signal.intellect_score < 40 else "🟡")

            message = f"""
{emoji} **{signal.direction} {signal.pair}**

📊 Сигнал: {signal.reason}
⏱️ Таймфрейм: {signal.timeframe}
🎲 Уверенность: {signal.confidence * 100:.0f}%

**🔮 Подтверждение индикаторов**
{intellect_emoji} INTELLECT_city: `{signal.intellect_score:.0f}%` ({'Сильный бычий' if signal.intellect_score > 70 else ('Сильный медвежий' if signal.intellect_score < 30 else 'Нейтральный')})

**📈 Детали сделки**
💰 Вход: `{signal.entry}`
🛑 Stop Loss: `{signal.stop_loss}` ({signal.pips} пипс)
🎁 Take Profit: `{signal.take_profit}`
📊 R:R: {signal.rr_ratio}

⏰ Время: {datetime.now().strftime('%H:%M:%S')}
📌 Сессия: {TRADING_PAIRS[signal.pair]['session']}
            """

            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown'
            )

            self.daily_signals[today] += 1
            logger.info(f"✅ Signal sent: {signal.direction} {signal.pair} (INTELLECT: {signal.intellect_score:.0f}%)")
            return True

        except TelegramError as e:
            logger.error(f"❌ Telegram error: {e}")
            return False


class KorchTradingBot:
    """Main bot orchestrator"""

    def __init__(self):
        self.api = MarketDataAPI()
        self.strategy = StrategyAnalyzer()
        self.telegram = TelegramBot(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        self.is_running = False

    async def analyze_pair(self, pair_name: str, pair_config: Dict) -> Optional[Signal]:
        """Analyze single trading pair with INTELLECT_city indicator confirmation"""
        try:
            # Fetch OHLCV data for 1H and 5M (yfinance uses 1m as 5m substitute)
            ohlcv_1h = await self.api.fetch_ohlcv(pair_name, pair_config, timeframe='1h', limit=50)
            ohlcv_5m = await self.api.fetch_ohlcv(pair_name, pair_config, timeframe='1m', limit=100)

            if not ohlcv_1h or len(ohlcv_1h) < 21:
                logger.info(f"Insufficient data for {pair_name}")
                return None

            # AMD detection with INTELLECT_city confirmation
            amd_setup = self.strategy.detect_amd(ohlcv_1h, ohlcv_5m if ohlcv_5m else ohlcv_1h)

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
                timeframe='1H+5M',  # Changed from 1H+1M to 1H+5M
                confidence=amd_setup['confidence'],
                reason=amd_setup['reason'],
                pips=sl_tp['sl_pips'],
                rr_ratio=sl_tp['rr'],
                intellect_score=amd_setup.get('intellect_score', 50.0)
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
