"""
Быстрый тест инициализации бота
"""
import asyncio
import logging
from korch_trading_bot import KorchTradingBot, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_bot_init():
    """Тест создания и инициализации бота"""
    print("\n🤖 Тест инициализации бота")
    print("=" * 50)
    
    try:
        print(f"📡 Token: {TELEGRAM_BOT_TOKEN[:20]}...")
        print(f"💬 Chat ID: {TELEGRAM_CHAT_ID}")
        
        bot = KorchTradingBot()
        print("✅ Бот инициализирован успешно!")
        print(f"   - API: {type(bot.api).__name__}")
        print(f"   - Strategy: {type(bot.strategy).__name__}")
        print(f"   - Telegram: {type(bot.telegram).__name__}")
        print(f"   - Application: {type(bot.telegram.application).__name__}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_bot_init())
    exit(0 if success else 1)
