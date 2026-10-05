#!/usr/bin/env python3
"""
Test script for INTELLECT_city indicator calculation
Проверяет правильность расчета INTELLECT_city индикатора
"""

import asyncio
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List
import numpy as np
import yfinance as yf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class OHLCV:
    """OHLC+Volume data point"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class IndicatorAnalyzer:
    """Test version of INTELLECT_city calculator"""

    def __init__(self):
        self.rsi_period = 14
        self.macd_fast = 12
        self.macd_slow = 26
        self.macd_signal = 9
        self.stoch_period = 14
        self.mfi_period = 14

    def calculate_rsi(self, closes: List[float], period: int = 14) -> float:
        """Calculate RSI"""
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
        return float(rsi)

    def calculate_stochastic(self, highs: List[float], lows: List[float], closes: List[float],
                            period: int = 14) -> float:
        """%K (Stochastic)"""
        if len(closes) < period:
            return 50.0

        recent_high = max(highs[-period:])
        recent_low = min(lows[-period:])

        if recent_high == recent_low:
            return 50.0

        k_percent = ((closes[-1] - recent_low) / (recent_high - recent_low)) * 100
        return float(k_percent)

    def calculate_macd(self, closes: List[float]) -> float:
        """MACD line"""
        if len(closes) < self.macd_slow + 1:
            return 50.0

        exp_fast = self._ema(closes, self.macd_fast)
        exp_slow = self._ema(closes, self.macd_slow)

        macd = exp_fast - exp_slow
        normalized = 50 + (macd / (max(abs(exp_fast), abs(exp_slow)) + 1e-6)) * 50
        return float(max(0, min(100, normalized)))

    def calculate_mfi(self, highs: List[float], lows: List[float], closes: List[float],
                     volumes: List[int], period: int = 14) -> float:
        """Money Flow Index"""
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
        return float(mfi)

    def _ema(self, data: List[float], period: int) -> float:
        """EMA calculation"""
        if len(data) < period:
            return np.mean(data)

        multiplier = 2 / (period + 1)
        ema = np.mean(data[:period])

        for price in data[period:]:
            ema = price * multiplier + ema * (1 - multiplier)

        return ema

    def calculate_rosc(self, closes: List[float], period: int = 20) -> float:
        """ROSC (Linear Correlation Oscillator)"""
        if len(closes) < period:
            return 50.0
        recent_closes = closes[-period:]
        time_series = np.arange(period)
        correlation = np.corrcoef(time_series, recent_closes)[0, 1]
        normalized = 50 + (correlation * 50)
        return float(max(0, min(100, normalized)))

    def calculate_wpr(self, highs: List[float], lows: List[float], closes: List[float],
                      period: int = 14) -> float:
        """Williams %R normalized to 0-100"""
        if len(highs) < period or len(lows) < period:
            return 50.0
        high_period = max(highs[-period:])
        low_period = min(lows[-period:])
        if high_period == low_period:
            return 50.0
        wpr = ((high_period - closes[-1]) / (high_period - low_period)) * -100
        normalized = 100 + wpr
        return float(max(0, min(100, normalized)))

    def calculate_percent_rank(self, closes: List[float], period: int = 20) -> float:
        """Percent Rank (%R)"""
        if len(closes) < period:
            return 50.0
        recent_closes = closes[-period:]
        current_close = closes[-1]
        below_count = sum(1 for price in recent_closes if price < current_close)
        percent_rank = (below_count / period) * 100
        return float(max(0, min(100, percent_rank)))

    def calculate_jap(self, closes: List[float], volumes: List[int], period: int = 20) -> float:
        """JAP (Japan Trade Indicator)"""
        if len(closes) < period + 1 or len(volumes) < period + 1:
            return 50.0
        roc = ((closes[-1] - closes[-period-1]) / closes[-period-1]) * 100
        avg_volume = np.mean(volumes[-period:])
        if avg_volume == 0:
            volume_ratio = 1.0
        else:
            volume_ratio = volumes[-1] / avg_volume
        jap = 50 + (roc / 10) * volume_ratio
        return float(max(0, min(100, jap)))

    def calculate_intellect_city_index(self, ohlcv_data: List[OHLCV]) -> dict:
        """Calculate all 8 INTELLECT_city components"""
        if len(ohlcv_data) < 30:
            return {'error': 'Not enough data'}

        closes = [c.close for c in ohlcv_data]
        highs = [c.high for c in ohlcv_data]
        lows = [c.low for c in ohlcv_data]
        volumes = [c.volume for c in ohlcv_data]

        rsi = self.calculate_rsi(closes)
        stoch = self.calculate_stochastic(highs, lows, closes)
        rosc = self.calculate_rosc(closes, 20)
        wpr = self.calculate_wpr(highs, lows, closes, 14)
        percent_rank = self.calculate_percent_rank(closes, 20)
        macd = self.calculate_macd(closes)
        mfi = self.calculate_mfi(highs, lows, closes, volumes)
        jap = self.calculate_jap(closes, volumes, 20)

        ma9 = np.mean(closes[-9:])
        ma21 = np.mean(closes[-21:])
        trend = 75 if ma9 > ma21 else (25 if ma9 < ma21 else 50)

        all_components = [rsi, stoch, rosc, wpr, percent_rank, macd, mfi, jap, trend]
        intellect_index = np.mean(all_components)

        return {
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
            'ma21': float(ma21),
        }


async def test_intellect_city():
    """Test INTELLECT_city calculation on real data"""
    analyzer = IndicatorAnalyzer()

    print("=" * 70)
    print("🧪 ТЕСТИРОВАНИЕ INTELLECT_city ИНДИКАТОРА")
    print("=" * 70)

    # Fetch real data
    print("\n📊 Загружаю реальные данные GER40...")
    try:
        ticker = yf.Ticker('^GDAXI')
        df = ticker.history(period="5d", interval="1m")

        if df.empty:
            print("❌ Не удалось загрузить данные")
            return

        print(f"✅ Загружено {len(df)} минутных свечей")

        # Convert to OHLCV
        ohlcv_list = []
        for idx, row in df.tail(100).iterrows():
            ohlcv = OHLCV(
                timestamp=idx.to_pydatetime(),
                open=float(row['Open']),
                high=float(row['High']),
                low=float(row['Low']),
                close=float(row['Close']),
                volume=int(row['Volume'])
            )
            ohlcv_list.append(ohlcv)

        # Calculate INTELLECT_city
        print("\n🔮 Вычисляю INTELLECT_city компоненты...")
        result = analyzer.calculate_intellect_city_index(ohlcv_list[-30:])

        if 'error' in result:
            print(f"❌ Ошибка: {result['error']}")
            return

        # Display results
        print("\n" + "=" * 70)
        print("📈 РЕЗУЛЬТАТЫ РАСЧЕТА INTELLECT_city (ВСЕ 8 КОМПОНЕНТОВ):")
        print("=" * 70)

        print(f"\n🟢 INTELLECT_city ИТОГОВЫЙ ИНДЕКС: {result['intellect_score']:.1f}%")

        print("\n📊 ВСЕ 8 КОМПОНЕНТОВ:")
        print(f"  1. RSI (14):              {result['rsi']:.1f}%")
        print(f"  2. Stochastic %K (14):    {result['stochastic']:.1f}%")
        print(f"  3. ROSC (корреляция):     {result['rosc']:.1f}%")
        print(f"  4. WPR (Williams):        {result['wpr']:.1f}%")
        print(f"  5. %R (Percent Rank):     {result['percent_rank']:.1f}%")
        print(f"  6. MACD:                  {result['macd']:.1f}%")
        print(f"  7. MFI (14):              {result['mfi']:.1f}%")
        print(f"  8. JAP (Japan Trade):     {result['jap']:.1f}%")
        print(f"  9. Тренд (MA9>MA21):      {result['trend']:.1f}%")

        print(f"\n📍 MOVING AVERAGES:")
        print(f"  • MA9:  {result['ma9']:.2f}")
        print(f"  • MA21: {result['ma21']:.2f}")

        # Interpretation
        print("\n" + "=" * 70)
        print("💡 ИНТЕРПРЕТАЦИЯ:")
        print("=" * 70)

        if result['intellect_score'] >= 70:
            sentiment = "🟢 СИЛЬНЫЙ БЫЧИЙ - Отличное условие для BUY (все 8 индикаторов согласны)"
        elif result['intellect_score'] >= 60:
            sentiment = "🟢 БЫЧИЙ - Хорошее условие для BUY (большинство индикаторов бычьи)"
        elif result['intellect_score'] >= 50:
            sentiment = "🟡 НЕЙТРАЛЬНЫЙ - Ожидаем подтверждения (индикаторы разделены)"
        elif result['intellect_score'] >= 40:
            sentiment = "🔴 МЕДВЕЖИЙ - Хорошее условие для SELL (большинство индикаторов медвежьи)"
        else:
            sentiment = "🔴 СИЛЬНЫЙ МЕДВЕЖИЙ - Отличное условие для SELL (все 8 индикаторов согласны)"

        print(f"\n{sentiment}")

        print(f"\n📌 ПОРОГИ ДЛЯ СИГНАЛОВ (AMD+FVG+INTELLECT):")
        print(f"  • BUY если INTELLECT ≥ 60%:  {'✅ ГОТОВО' if result['intellect_score'] >= 60 else '❌ НЕТ'}")
        print(f"  • SELL если INTELLECT ≤ 40%: {'✅ ГОТОВО' if result['intellect_score'] <= 40 else '❌ НЕТ'}")

        print(f"\n📈 СТАТИСТИКА КОМПОНЕНТОВ:")
        bullish_count = sum(1 for v in [result['rsi'], result['stochastic'], result['rosc'], result['wpr'],
                                         result['percent_rank'], result['macd'], result['mfi'], result['jap']] if v > 50)
        print(f"  • Бычьих индикаторов (>50%): {bullish_count}/8")
        print(f"  • Медвежьих индикаторов (<50%): {8-bullish_count}/8")

        print("\n" + "=" * 70)

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_intellect_city())
