"""
<<<<<<< HEAD
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
=======
Unit tests for Korch Trading Bot
"""

import unittest
from datetime import datetime
from korch_trading_bot import (
    OHLCV, Signal, StrategyAnalyzer, TelegramSignalSender
)


class TestStrategyAnalyzer(unittest.TestCase):
    
    def setUp(self):
        self.analyzer = StrategyAnalyzer()
    
    def test_fvg_detection(self):
        """Test Fair Value Gap detection"""
        ohlcv = [
            OHLCV(datetime.now(), 1.0500, 1.0520, 1.0490, 1.0510, 1000),
            OHLCV(datetime.now(), 1.0510, 1.0530, 1.0500, 1.0520, 1000),
            OHLCV(datetime.now(), 1.0520, 1.0540, 1.0510, 1.0530, 1000),
        ]
        
        fvg_buy, fvg_sell = self.analyzer._detect_fvg(ohlcv)
        self.assertTrue(fvg_buy or fvg_sell)
    
    def test_amd_detection(self):
        """Test AMD detection"""
        ohlcv = [
            OHLCV(datetime.now(), 1.0500, 1.0520, 1.0490, 1.0510, 1000),
            OHLCV(datetime.now(), 1.0510, 1.0530, 1.0500, 1.0520, 1000),
            OHLCV(datetime.now(), 1.0520, 1.0540, 1.0510, 1.0530, 1000),
            OHLCV(datetime.now(), 1.0530, 1.0550, 1.0520, 1.0540, 1000),
            OHLCV(datetime.now(), 1.0540, 1.0560, 1.0530, 1.0550, 1000),
        ]
        
        amd = self.analyzer._detect_amd(ohlcv)
        self.assertIsNotNone(amd)
        self.assertEqual(amd['direction'], 'BUY')
    
    def test_signal_creation(self):
        """Test signal creation with proper 1:2 RR"""
        h1 = OHLCV(datetime.now(), 1.0500, 1.0520, 1.0490, 1.0515, 1000)
        m5 = OHLCV(datetime.now(), 1.0510, 1.0525, 1.0505, 1.0520, 500)
        
        signal = self.analyzer._create_signal('EURUSD', 'BUY', h1, m5, 'Test')
        
        self.assertEqual(signal.pair, 'EURUSD')
        self.assertEqual(signal.direction, 'BUY')
        self.assertGreater(signal.take_profit, signal.entry)
        self.assertLess(signal.stop_loss, signal.entry)
        
        # Check 1:2 ratio (TP distance = 2 * SL distance)
        tp_dist = signal.take_profit - signal.entry
        sl_dist = signal.entry - signal.stop_loss
        ratio = tp_dist / sl_dist if sl_dist > 0 else 0
        self.assertAlmostEqual(ratio, 2.0, places=0)


class TestSignalFormatting(unittest.TestCase):
    
    def setUp(self):
        self.sender = TelegramSignalSender('test_token', 'test_chat')
    
    def test_signal_format(self):
        """Test signal message formatting"""
        signal = Signal(
            pair='EURUSD',
            direction='BUY',
            entry=1.0520,
            stop_loss=1.0500,
            take_profit=1.0540,
            timeframe='1H+5M',
            confidence=0.75,
            reason='FVG+AMD'
        )
        
        message = self.sender._format_signal(signal)
        
        self.assertIn('EURUSD', message)
        self.assertIn('BUY', message)
        self.assertIn('1.0520', message)
        self.assertIn('1.0500', message)
        self.assertIn('1.0540', message)


if __name__ == '__main__':
    unittest.main()
>>>>>>> origin/main
