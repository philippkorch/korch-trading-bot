"""
Финальная валидация всех компонентов бота
"""
import asyncio
import sys
from datetime import datetime

# Тесты
async def validate_imports():
    """Проверка всех импортов"""
    print("\n✓ Проверка импортов...")
    try:
        from korch_trading_bot import (
            OHLCV, Signal, MarketDataAPI, IndicatorAnalyzer,
            StrategyAnalyzer, TelegramBot, KorchTradingBot,
            TRADING_PAIRS, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
        )
        print("  ✅ Все импорты OK")
        return True
    except Exception as e:
        print(f"  ❌ Ошибка импорта: {e}")
        return False

async def validate_bot_classes():
    """Проверка классов"""
    print("\n✓ Проверка классов...")
    try:
        from korch_trading_bot import (
            MarketDataAPI, IndicatorAnalyzer, StrategyAnalyzer,
            TelegramBot, KorchTradingBot
        )
        
        # Инициализация
        api = MarketDataAPI()
        indicators = IndicatorAnalyzer()
        strategy = StrategyAnalyzer()
        bot = KorchTradingBot()
        
        print("  ✅ MarketDataAPI OK")
        print("  ✅ IndicatorAnalyzer OK")
        print("  ✅ StrategyAnalyzer OK")
        print("  ✅ TelegramBot OK")
        print("  ✅ KorchTradingBot OK")
        return True
    except Exception as e:
        print(f"  ❌ Ошибка инициализации: {e}")
        return False

async def validate_data_fetching():
    """Проверка загрузки данных"""
    print("\n✓ Проверка загрузки данных...")
    try:
        from korch_trading_bot import MarketDataAPI, TRADING_PAIRS
        
        api = MarketDataAPI()
        success_count = 0
        
        for pair_name, config in TRADING_PAIRS.items():
            try:
                ohlcv = await api.fetch_ohlcv(pair_name, config, '1h', 5)
                if ohlcv and len(ohlcv) > 0:
                    print(f"  ✅ {pair_name}: {len(ohlcv)} свечей загружено")
                    success_count += 1
                else:
                    print(f"  ⚠️  {pair_name}: данные пусты")
            except Exception as e:
                print(f"  ❌ {pair_name}: {e}")
        
        return success_count == len(TRADING_PAIRS)
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        return False

async def validate_indicators():
    """Проверка индикаторов"""
    print("\n✓ Проверка INTELLECT_city индикаторов...")
    try:
        from korch_trading_bot import OHLCV, IndicatorAnalyzer
        from datetime import datetime
        
        analyzer = IndicatorAnalyzer()
        
        # Генерируем данные
        ohlcv = [
            OHLCV(datetime.now(), 100+i, 101+i, 99+i, 100+i, 1000000)
            for i in range(30)
        ]
        
        result = analyzer.calculate_intellect_city_index(ohlcv)
        
        if result and 'intellect_score' in result:
            score = result['intellect_score']
            print(f"  ✅ INTELLECT_city: {score:.1f}%")
            print(f"     - RSI: {result['rsi']:.1f}%")
            print(f"     - Stochastic: {result['stochastic']:.1f}%")
            print(f"     - ROSC: {result['rosc']:.1f}%")
            return True
        else:
            print("  ❌ Invalid indicator result")
            return False
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        return False

async def validate_signal_generation():
    """Проверка генерации сигналов"""
    print("\n✓ Проверка генерации сигналов...")
    try:
        from korch_trading_bot import StrategyAnalyzer
        
        strategy = StrategyAnalyzer()
        
        # Тест SL/TP
        result = strategy.calculate_sl_tp(18250.50, 'BUY', 50)
        
        if result and all(k in result for k in ['sl', 'tp', 'sl_pips', 'tp_pips', 'rr']):
            print(f"  ✅ SL/TP расчеты OK")
            print(f"     - SL: {result['sl']}")
            print(f"     - TP: {result['tp']}")
            print(f"     - R:R: {result['rr']}")
            return True
        else:
            print("  ❌ Invalid SL/TP result")
            return False
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        return False

async def main():
    """Запуск всех проверок"""
    print("\n" + "=" * 60)
    print("🔍 ФИНАЛЬНАЯ ВАЛИДАЦИЯ KORCH TRADING BOT v2.2")
    print("=" * 60)
    
    results = []
    
    results.append(("Импорты", await validate_imports()))
    results.append(("Классы", await validate_bot_classes()))
    results.append(("Загрузка данных", await validate_data_fetching()))
    results.append(("INTELLECT_city", await validate_indicators()))
    results.append(("Генерация сигналов", await validate_signal_generation()))
    
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ВАЛИДАЦИИ:")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:10} | {name}")
    
    all_passed = all(r[1] for r in results)
    
    print("=" * 60)
    if all_passed:
        print("🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ! БОТ ГОТОВ К РАЗВЁРТЫВАНИЮ!")
        print("=" * 60)
        return 0
    else:
        print("⚠️  НЕКОТОРЫЕ ПРОВЕРКИ НЕ ПРОЙДЕНЫ!")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
