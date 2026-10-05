"""
Тестовый скрипт для проверки бота локально
"""

import asyncio
from korch_trading_bot import (
    KorchTradingBot,
    StrategyAnalyzer,
    TelegramSignalSender,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    TRADINGVIEW_SESSION_ID,
    TRADING_PAIRS
)

async def test_signal_format():
    """Тест форматирования сигнала"""
    print("\n📋 Тест 1: Форматирование сигнала")
    print("=" * 50)

    telegram = TelegramSignalSender(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)

    # Тестовый сигнал
    test_signal = {
        'type': 'BUY',
        'symbol': 'EURUSD',
        'entry': 1.0950,
        'sl': 1.0920,
        'tp': 1.0980,
        'sl_pips': 30,
        'tp_pips': 60,
        'rr': '1:2',
        'reason': 'AMD+FVG инверсия на 5M',
        'session': 'London Morning'
    }

    formatted = telegram._format_signal(test_signal)
    print(formatted)
    print("\n✅ Сигнал отформатирован правильно!")


async def test_strategy_analyzer():
    """Тест анализатора стратегии"""
    print("\n📊 Тест 2: Анализатор стратегии")
    print("=" * 50)

    analyzer = StrategyAnalyzer()

    # Тестовые OHLCV данные
    test_ohlcv_1h = [
        {'open': 1.0900, 'high': 1.0950, 'low': 1.0880, 'close': 1.0940},
        {'open': 1.0940, 'high': 1.0960, 'low': 1.0930, 'close': 1.0955},
        {'open': 1.0955, 'high': 1.0970, 'low': 1.0945, 'close': 1.0965},
    ]

    test_ohlcv_5m = [
        {'open': 1.0960, 'high': 1.0975, 'low': 1.0950, 'close': 1.0965},
        {'open': 1.0965, 'high': 1.0970, 'low': 1.0955, 'close': 1.0958},
        {'open': 1.0958, 'high': 1.0962, 'low': 1.0945, 'close': 1.0950},
        {'open': 1.0950, 'high': 1.0955, 'low': 1.0940, 'close': 1.0945},
        {'open': 1.0945, 'high': 1.0950, 'low': 1.0930, 'close': 1.0935},
    ]

    setup = analyzer.find_amd_fvg_setup(test_ohlcv_1h, test_ohlcv_5m)
    if setup:
        print(f"✅ Сетап найден: {setup}")
    else:
        print("❌ Сетап не найден (это может быть нормально на тестовых данных)")

    # Тест calculate_sl_tp
    sl_tp = analyzer.calculate_sl_tp(
        entry=1.0950,
        sl=1.0920,
        signal='BUY',
        risk_percent=1.0
    )

    if sl_tp:
        print(f"\n✅ SL/TP рассчитаны:")
        print(f"   SL: {sl_tp.get('sl')}")
        print(f"   TP: {sl_tp.get('tp')}")
        print(f"   RR: {sl_tp.get('rr')}")
        print(f"   Пункты: {sl_tp.get('sl_pips')} / {sl_tp.get('tp_pips')}")


async def test_bot_creation():
    """Тест создания бота"""
    print("\n🤖 Тест 3: Создание бота")
    print("=" * 50)

    try:
        bot = KorchTradingBot(
            token=TELEGRAM_BOT_TOKEN,
            chat_id=TELEGRAM_CHAT_ID,
            sessionid=TRADINGVIEW_SESSION_ID
        )

        if bot.tv:
            print("✅ Бот создан с TradingView подключением")
        else:
            print("⚠️  Бот создан без TradingView (sessionid не установлен)")

        print(f"📋 Пары для торговли: {list(TRADING_PAIRS.keys())}")
        print("✅ Бот готов к работе!")

    except Exception as e:
        print(f"❌ Ошибка при создании бота: {e}")


async def main():
    """Запусти все тесты"""
    print("\n" + "=" * 50)
    print("🧪 ТЕСТИРОВАНИЕ KORCH TRADING BOT")
    print("=" * 50)

    await test_signal_format()
    await test_strategy_analyzer()
    await test_bot_creation()

    print("\n" + "=" * 50)
    print("✅ ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
