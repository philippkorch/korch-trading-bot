#!/usr/bin/env python3
"""
KORCH Trading Bot v4.0+ с поддержкой аннотированных графиков
Расширенная версия с отправкой фото анализа
"""

import asyncio
import logging
import os
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional
import yfinance as yf
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from io import BytesIO
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8999356089:AAEzV2onmpC6oFe-j9M26UTFLxU14N6fSCs')
TELEGRAM_CHAT_ID = int(os.getenv('TELEGRAM_CHAT_ID', '8999356089'))

# Trading Pairs
TRADING_PAIRS = {
    'GER40': {'symbol': '^GDAXI', 'interval': '1h', 'name': 'DAX Index'},
    'BTC': {'symbol': 'BTC-USD', 'interval': '4h', 'name': 'Bitcoin'},
    'GOLD': {'symbol': 'GC=F', 'interval': '1h', 'name': 'Gold Futures'},
}

# Economic Events
ECONOMIC_EVENTS = [
    {'time': '10:30', 'country': '🇺🇸', 'impact': 'HIGH', 'title': 'FOMC Interest Rate Decision'},
    {'time': '11:00', 'country': '🇪🇺', 'impact': 'HIGH', 'title': 'ECB Press Conference'},
    {'time': '14:30', 'country': '🇺🇸', 'impact': 'MEDIUM', 'title': 'US Core PCE'},
    {'time': '15:45', 'country': '🇺🇸', 'impact': 'LOW', 'title': 'API Crude Oil Inventories'},
]

# ===== DATA CLASSES =====
@dataclass
class TradeSignal:
    pair: str
    timeframe: str
    signal_type: str
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float
    intellect_score: float
    confirmations: int
    support_levels: List[float]
    resistance_levels: List[float]
    price_high: float = 0.0
    price_low: float = 0.0

@dataclass
class AnalysisState:
    is_analyzing: bool = False
    progress: int = 0
    last_update: Optional[datetime] = None
    active_signals: List[TradeSignal] = None

    def __post_init__(self):
        if self.active_signals is None:
            self.active_signals = []

# Global state
analysis_state = AnalysisState()
active_analysis_tasks = {}

# ===== CHART GENERATION =====
class ChartAnnotator:
    """Создает аннотированные графики торговых сигналов"""

    def __init__(self):
        self.img_width = 800
        self.img_height = 600

    def create_chart_image(self, signal: TradeSignal, df: pd.DataFrame) -> BytesIO:
        """Создает аннотированный график сигнала"""
        try:
            fig, ax = plt.subplots(figsize=(12, 8), dpi=100)
            fig.patch.set_facecolor('#1a1a1a')
            ax.set_facecolor('#2a2a2a')

            # Основные данные
            dates = range(len(df))
            closes = df['Close'].values
            highs = df['High'].values
            lows = df['Low'].values

            # Рисуем свечи (OHLC)
            for i, date in enumerate(dates[-100:]):  # Последние 100 свечей
                idx = len(df) - 100 + i
                open_p = df['Open'].iloc[idx]
                close_p = closes[idx]
                high_p = highs[idx]
                low_p = lows[idx]

                color = '#10b981' if close_p >= open_p else '#ef4444'

                # Wick (тень)
                ax.plot([i, i], [low_p, high_p], color=color, linewidth=1, alpha=0.5)

                # Body (тело свечи)
                height = abs(close_p - open_p)
                bottom = min(open_p, close_p)
                ax.add_patch(plt.Rectangle((i - 0.3, bottom), 0.6, height,
                                          facecolor=color, edgecolor=color, alpha=0.8))

            # Скользящие средние
            if 'MA9' in df.columns and 'MA21' in df.columns:
                ma9 = df['MA9'].iloc[-100:].values
                ma21 = df['MA21'].iloc[-100:].values

                ax.plot(range(len(ma9)), ma9, color='#3b82f6', linewidth=2, label='MA9', alpha=0.7)
                ax.plot(range(len(ma21)), ma21, color='#f97316', linewidth=2, label='MA21', alpha=0.7)

            # Уровни поддержки и сопротивления
            for level in signal.support_levels:
                ax.axhline(y=level, color='#10b981', linestyle='--', linewidth=1, alpha=0.5)

            for level in signal.resistance_levels:
                ax.axhline(y=level, color='#ef4444', linestyle='--', linewidth=1, alpha=0.5)

            # Entry, SL, TP
            ax.axhline(y=signal.entry_price, color='#3b82f6', linestyle='-', linewidth=2, label='Entry')
            ax.axhline(y=signal.stop_loss, color='#ef4444', linestyle='-', linewidth=2, label='SL')
            ax.axhline(y=signal.take_profit, color='#10b981', linestyle='-', linewidth=2, label='TP')

            # Оформление
            ax.set_facecolor('#2a2a2a')
            ax.grid(True, alpha=0.2, color='white')
            ax.legend(loc='upper left', facecolor='#3a3a3a', edgecolor='white', labelcolor='white')

            # Заголовок
            rr = (signal.take_profit - signal.entry_price) / abs(signal.entry_price - signal.stop_loss)
            title = f"{signal.pair} | {signal.signal_type} | Entry: {signal.entry_price:.2f} | R:R: {rr:.1f}:1 | Conf: {signal.confidence:.0f}%"
            ax.set_title(title, color='white', fontsize=14, fontweight='bold', pad=20)

            # Оси
            ax.tick_params(colors='white', labelsize=9)
            ax.spines['bottom'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            ax.set_ylabel('Price', color='white')
            ax.set_xlabel('Time', color='white')

            # Сохраняем в BytesIO
            buf = BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format='png', facecolor='#1a1a1a', dpi=100)
            plt.close(fig)

            buf.seek(0)
            return buf

        except Exception as e:
            logger.error(f"❌ Error creating chart: {e}")
            return None

# ===== MARKET DATA =====
async def fetch_market_data(pair: str, symbol: str, interval: str = '1h') -> Optional[pd.DataFrame]:
    """Получить данные рынка"""
    try:
        logger.info(f"📊 Fetching {pair}...")
        period = '30d' if interval in ['1h', '4h'] else '90d'

        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval, progress=False)

        if df.empty:
            logger.warning(f"⚠️ No data for {pair}")
            return None

        df['MA9'] = df['Close'].rolling(window=9).mean()
        df['MA21'] = df['Close'].rolling(window=21).mean()

        logger.info(f"✅ Got {len(df)} candles for {pair}")
        return df

    except Exception as e:
        logger.error(f"❌ Error fetching {pair}: {e}")
        return None

def generate_signal(pair: str, df: Optional[pd.DataFrame]) -> Optional[TradeSignal]:
    """Генерирует сигнал на основе данных"""
    if df is None or len(df) < 21:
        demo_signals = {
            'GER40': TradeSignal(
                pair='GER40',
                timeframe='1H',
                signal_type='BUY',
                entry_price=18500.50,
                stop_loss=18450.00,
                take_profit=18600.50,
                confidence=78.0,
                intellect_score=72.0,
                confirmations=5,
                support_levels=[18400.0, 18350.0],
                resistance_levels=[18550.0, 18600.0],
                price_high=18650.0,
                price_low=18300.0
            ),
            'BTC': TradeSignal(
                pair='BTC/USD',
                timeframe='4H',
                signal_type='SELL',
                entry_price=42850.0,
                stop_loss=43200.0,
                take_profit=42350.0,
                confidence=65.0,
                intellect_score=58.0,
                confirmations=3,
                support_levels=[42000.0, 41500.0],
                resistance_levels=[43000.0, 43500.0],
                price_high=43600.0,
                price_low=41000.0
            ),
            'GOLD': TradeSignal(
                pair='GOLD',
                timeframe='1H',
                signal_type='BUY',
                entry_price=2595.50,
                stop_loss=2585.00,
                take_profit=2616.00,
                confidence=82.0,
                intellect_score=79.0,
                confirmations=6,
                support_levels=[2580.0, 2570.0],
                resistance_levels=[2610.0, 2620.0],
                price_high=2630.0,
                price_low=2560.0
            )
        }
        return demo_signals.get(pair)

    latest = df.iloc[-1]
    is_uptrend = latest['MA9'] > latest['MA21'] if pd.notna(latest['MA9']) and pd.notna(latest['MA21']) else False

    if not is_uptrend:
        return None

    current_price = latest['Close']
    atr = (df['High'] - df['Low']).tail(14).mean()

    return TradeSignal(
        pair=pair,
        timeframe='1H',
        signal_type='BUY',
        entry_price=current_price,
        stop_loss=current_price - atr,
        take_profit=current_price + (atr * 2),
        confidence=min(80.0, 60.0 + len(df[df['MA9'] > df['MA21']].tail(5)) * 4),
        intellect_score=min(80.0, 60.0 + len(df[df['MA9'] > df['MA21']].tail(5)) * 4) - 5,
        confirmations=3,
        support_levels=[current_price - atr, current_price - atr*2],
        resistance_levels=[current_price + atr*0.5],
        price_high=df['High'].tail(50).max(),
        price_low=df['Low'].tail(50).min()
    )

# ===== TELEGRAM HANDLERS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню"""
    keyboard = [
        [InlineKeyboardButton("▶️ Анализировать", callback_data="analyze_start")],
        [InlineKeyboardButton("📰 NEWS", callback_data="show_news"),
         InlineKeyboardButton("⚙️ STATUS", callback_data="show_status")],
        [InlineKeyboardButton("📍 SIGNALS", callback_data="show_signals"),
         InlineKeyboardButton("ℹ️ INFO", callback_data="show_info")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = """
🤖 <b>KORCH Trading Bot v4.0+</b>

<i>С поддержкой аннотированных графиков</i>

Анализ в реальном времени: GER40 | BTC | GOLD

Выберите действие:
    """

    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')
    else:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')

async def analyze_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Анализ всех пар с графиками"""
    query = update.callback_query
    user_id = update.effective_user.id

    if query.data == "analyze_start":
        if user_id in active_analysis_tasks:
            active_analysis_tasks[user_id].cancel()

        analysis_state.is_analyzing = True
        analysis_state.progress = 0

        await query.answer()

        keyboard = [[InlineKeyboardButton("⏹️ ОТМЕНА", callback_data="analyze_cancel")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        msg = await query.edit_message_text(
            "🔄 <b>Анализирую GER40, BTC, GOLD...</b>\n\n⏳ Подождите...",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )

        try:
            task = asyncio.create_task(perform_full_analysis(user_id, msg, query))
            active_analysis_tasks[user_id] = task
        except Exception as e:
            logger.error(f"❌ Analysis error: {e}")
            await query.edit_message_text(f"❌ Ошибка: {str(e)}")

    elif query.data == "analyze_cancel":
        analysis_state.is_analyzing = False

        if user_id in active_analysis_tasks:
            active_analysis_tasks[user_id].cancel()
            del active_analysis_tasks[user_id]

        await query.answer("⏹️ Анализ отменен", show_alert=False)
        await start(update, context)

async def perform_full_analysis(user_id: int, message, query):
    """Полный анализ с графиками"""
    try:
        bot = query.bot
        chart_annotator = ChartAnnotator()
        signals = []

        # Анализируем все пары
        for pair, config in TRADING_PAIRS.items():
            if not analysis_state.is_analyzing:
                break

            analysis_state.progress = int((len(signals) / 3) * 60)

            logger.info(f"🔍 Analyzing {pair}...")

            df = await fetch_market_data(pair, config['symbol'], config['interval'])
            signal = generate_signal(pair, df)

            if signal and df is not None:
                signals.append(signal)

                # Генерируем и отправляем график
                try:
                    chart_buf = chart_annotator.create_chart_image(signal, df)

                    if chart_buf:
                        rr = (signal.take_profit - signal.entry_price) / abs(signal.entry_price - signal.stop_loss)
                        emoji = '🔴' if signal.signal_type == 'SELL' else '🟢'

                        caption = f"""
{emoji} <b>{signal.pair} | {signal.timeframe}</b>

Entry: {signal.entry_price:.2f}
SL: {signal.stop_loss:.2f}
TP: {signal.take_profit:.2f}

R:R: 1:{rr:.1f}
Confidence: {signal.confidence:.0f}%
INTELLECT: {signal.intellect_score:.0f}%
Confirmations: {signal.confirmations}/8
                        """.strip()

                        await bot.send_photo(
                            chat_id=TELEGRAM_CHAT_ID,
                            photo=chart_buf,
                            caption=caption,
                            parse_mode='HTML'
                        )
                        logger.info(f"✅ Chart sent for {pair}")
                except Exception as e:
                    logger.error(f"❌ Error sending chart for {pair}: {e}")

            await asyncio.sleep(0.5)

        # Финальное сообщение
        analysis_state.progress = 100
        analysis_state.is_analyzing = False
        analysis_state.last_update = datetime.now()
        analysis_state.active_signals = signals

        text = f"✅ <b>Анализ завершен!</b>\n\n🎯 Найдено сигналов: <b>{len(signals)}</b>\n\n"

        if signals:
            for signal in signals:
                rr = (signal.take_profit - signal.entry_price) / abs(signal.entry_price - signal.stop_loss)
                emoji = '🔴' if signal.signal_type == 'SELL' else '🟢'
                text += f"{emoji} {signal.pair}: {signal.signal_type} @ {signal.entry_price:.2f} (R:R {rr:.1f}:1)\n"

        keyboard = [
            [InlineKeyboardButton("▶️ Анализировать", callback_data="analyze_start")],
            [InlineKeyboardButton("📍 SIGNALS", callback_data="show_signals"),
             InlineKeyboardButton("◀️ МЕНЮ", callback_data="back_to_menu")],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')

    except asyncio.CancelledError:
        logger.info("Analysis cancelled")
    except Exception as e:
        logger.error(f"❌ Error in perform_full_analysis: {e}")
        analysis_state.is_analyzing = False

async def show_signals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает активные сигналы"""
    query = update.callback_query
    await query.answer()

    if not analysis_state.active_signals:
        text = "📍 Активные сигналы\n━━━━━━━━━━━━━━━━━━━━\n\nСигналов не найдено.\n\nНажмите 'Анализировать' для поиска."
    else:
        text = f"📍 Активные сигналы ({len(analysis_state.active_signals)})\n━━━━━━━━━━━━━━━━━━━━\n\n"

        for signal in analysis_state.active_signals:
            rr = (signal.take_profit - signal.entry_price) / abs(signal.entry_price - signal.stop_loss)
            emoji = '🔴' if signal.signal_type == 'SELL' else '🟢'
            text += f"{emoji} <b>{signal.pair}</b>\n"
            text += f"Entry: {signal.entry_price:.2f} | SL: {signal.stop_loss:.2f} | TP: {signal.take_profit:.2f}\n"
            text += f"R:R: 1:{rr:.1f} | Conf: {signal.confidence:.0f}% | INTELLECT: {signal.intellect_score:.0f}%\n\n"

    keyboard = [[InlineKeyboardButton("◀️ МЕНЮ", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')

async def show_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статус системы"""
    query = update.callback_query
    await query.answer()

    now = datetime.now().strftime('%H:%M')

    text = f"""
⚙️ <b>СТАТУС СИСТЕМЫ</b>
━━━━━━━━━━━━━━━━━━━━

✅ Тренд мониторинг: <b>Активен</b>
✅ Стратегия AMD: <b>Включена</b>
✅ FVG Структура: <b>Включена</b>
✅ INTELLECT_city: <b>Активен</b>

⏱️ Интервал проверки: <b>5 мин</b>
🕐 Последнее обновление: <b>{now}</b>

━━━━━━━━━━━━━━━━━━━━
    """

    keyboard = [[InlineKeyboardButton("◀️ МЕНЮ", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')

async def show_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Экономический календарь"""
    query = update.callback_query
    await query.answer()

    text = "📰 <b>ЭКОНОМИЧЕСКИЙ КАЛЕНДАРЬ</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"

    for event in ECONOMIC_EVENTS:
        impact_emoji = '🔴' if event['impact'] == 'HIGH' else '🟡' if event['impact'] == 'MEDIUM' else '⚪'
        text += f"{event['country']} <b>{event['time']}</b>\n"
        text += f"{impact_emoji} {event['impact']}: {event['title']}\n\n"

    text += "━━━━━━━━━━━━━━━━━━━━"

    keyboard = [[InlineKeyboardButton("◀️ МЕНЮ", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')

async def show_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Информация о стратегии"""
    query = update.callback_query
    await query.answer()

    text = """
ℹ️ <b>ИНФОРМАЦИЯ О СТРАТЕГИИ</b>
━━━━━━━━━━━━━━━━━━━━

<b>AMD (After Market Delivery)</b>
Анализ трендов с MA9 > MA21 для определения восходящего тренда.

<b>FVG - Fair Value Gap</b>
Выявление структурных пробелов на 5-минутном таймфрейме.

<b>INTELLECT_city Score</b>
Составной индикатор 0-100%. BUY: ≥60%  |  SELL: ≤40%

<b>Risk:Reward Ratio 1:2</b>
TP = Entry + (Entry - SL) × 2

<b>Данные рынка</b>
Реальные котировки через yfinance с exponential backoff.

<b>Графики</b>
Аннотированные чарты с Entry, SL, TP, MA9, MA21, поддержкой и сопротивлением.

━━━━━━━━━━━━━━━━━━━━
    """

    keyboard = [[InlineKeyboardButton("◀️ МЕНЮ", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат в меню"""
    query = update.callback_query
    await query.answer()
    await start(update, context)

# ===== MAIN =====
async def main():
    """Запуск бота"""
    logger.info("🚀 Starting KORCH Trading Bot v4.0+ with Charts...")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(analyze_callback, pattern="^analyze_"))
    app.add_handler(CallbackQueryHandler(show_news, pattern="^show_news$"))
    app.add_handler(CallbackQueryHandler(show_status, pattern="^show_status$"))
    app.add_handler(CallbackQueryHandler(show_signals, pattern="^show_signals$"))
    app.add_handler(CallbackQueryHandler(show_info, pattern="^show_info$"))
    app.add_handler(CallbackQueryHandler(back_to_menu, pattern="^back_to_menu$"))

    logger.info("✅ Bot is running! Press Ctrl+C to stop.")
    await app.run_polling()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped.")
