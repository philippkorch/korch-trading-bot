"""
Тестовый скрипт для проверки бота локально
"""

import asyncio
from datetime import datetime
from korch_trading_bot import (
    OHLCV,
    Signal,
    StrategyAnalyzer,
    IndicatorAnalyzer,
    MarketDataAPI,
    TRADING_PAIRS
)


async def test_indicators():
    """Тест INTELLECT_city индикаторов"""
    print("\n📊 Тест 1: INTELLECT_city индикаторы")
    print("=" * 50)

    analyzer = IndicatorAnalyzer()

    # Генерируем тестовые данные
    closes = [100 + i*0.5 for i in range(30)]
    highs = [100.5 + i*0.5 for i in range(30)]
    lows = [99.5 + i*0.5 for i in range(30)]
    volumes = [1000000] * 30

    ohlcv = [
        OHLCV(datetime.now(), closes[i], highs[i], lows[i], closes[i], volumes[i])
        for i in range(30)
    ]

    result = analyzer.calculate_intellect_city_index(ohlcv)
    print(f"✅ INTELLECT_city score: {result['intellect_score']:.1f}%")
    print(f"   RSI: {result['rsi']:.1f}%")
    print(f"   Stochastic: {result['stochastic']:.1f}%")
    print(f"   ROSC: {result['rosc']:.1f}%")
    print(f"   Trend (MA9>MA21): {result['trend']:.1f}%")


async def test_strategy():
    """Тест AMD+FVG стратегии"""
    print("\n🎯 Тест 2: AMD+FVG обнаружение")
    print("=" * 50)

    strategy = StrategyAnalyzer()

    # Генерируем восходящий тренд
    ohlcv_1h = []
    price = 18000
    for i in range(25):
        ohlcv_1h.append(OHLCV(
            datetime.now(),
            price,
            price + 50,
            price - 30,
            price + 30,
            1000000
        ))
        price += 20  # Восходящий тренд

    # Генерируем 5M данные с инверсией
    ohlcv_5m = []
    price = 18500
    for i in range(25):
        ohlcv_5m.append(OHLCV(
            datetime.now(),
            price,
            price + 10,
            price - 5,
            price + 5,
            100000
        ))
        if i >= 20:
            price += 2
        else:
            price -= 2

    amd = strategy.detect_amd(ohlcv_1h, ohlcv_5m)

    if amd:
        print(f"✅ AMD сигнал найден!")
        print(f"   Тип: {amd['type']}")
        print(f"   Уверенность: {amd['confidence']:.0%}")
        print(f"   INTELLECT_city: {amd['intellect_score']:.1f}%")
    else:
        print("⏳ AMD сигнал не найден (может быть нормально для тестовых данных)")


async def test_sl_tp_calculation():
    """Тест расчета SL и TP"""
    print("\n💰 Тест 3: Расчет SL/TP (1:2 R:R)")
    print("=" * 50)

    strategy = StrategyAnalyzer()

    result = strategy.calculate_sl_tp(
        entry=18250.50,
        signal_type='BUY',
        risk_pips=50
    )

    print(f"✅ SL/TP рассчитаны:")
    print(f"   Вход: 18250.50")
    print(f"   SL: {result['sl']} ({result['sl_pips']} пипс)")
    print(f"   TP: {result['tp']} ({result['tp_pips']} пипс)")
    print(f"   R:R: {result['rr']}")


async def test_market_api():
    """Тест Market Data API"""
    print("\n📡 Тест 4: Market Data API")
    print("=" * 50)

    api = MarketDataAPI()

    # Пытаемся загрузить реальные данные
    try:
        for pair_name, config in TRADING_PAIRS.items():
            ohlcv = await api.fetch_ohlcv(pair_name, config, '1h', 10)
            if ohlcv:
                print(f"✅ {pair_name}: загружено {len(ohlcv)} свечей")
                if ohlcv:
                    last = ohlcv[-1]
                    print(f"   Последняя цена: O={last.open:.2f} H={last.high:.2f} L={last.low:.2f} C={last.close:.2f}")
            else:
                print(f"⚠️  {pair_name}: данные не загружены")
    except Exception as e:
        print(f"⚠️  Ошибка при загрузке данных: {e}")


async def main():
    """Запусти все тесты"""
    print("\n" + "=" * 60)
    print("🧪 ТЕСТИРОВАНИЕ KORCH TRADING BOT v2.2")
    print("=" * 60)

    await test_indicators()
    await test_strategy()
    await test_sl_tp_calculation()
    await test_market_api()

    print("\n" + "=" * 60)
    print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
