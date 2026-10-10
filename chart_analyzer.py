#!/usr/bin/env python3
"""
Interactive Chart Analyzer - анализирует скриншоты графиков TradingView
и рисует аннотации (уровни поддержки, входы, stop loss, take profit)
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PriceLevel:
    """Уровень цены на графике"""
    price: float
    level_type: str  # "support", "resistance", "entry", "sl", "tp"
    y_pixel: int  # пиксель на изображении
    label: str
    color: Tuple[int, int, int]  # RGB

@dataclass
class ChartAnalysis:
    """Результат анализа графика"""
    pair: str
    timeframe: str
    trend: str  # "uptrend", "downtrend", "ranging"
    entry_price: Optional[float]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    confidence: float  # 0-100%
    support_levels: List[float]
    resistance_levels: List[float]
    analysis_text: str
    signal_type: Optional[str]  # "BUY", "SELL", None


class ChartImageAnalyzer:
    """Анализирует изображения графиков с помощью Claude Vision"""

    def __init__(self):
        self.img_width = None
        self.img_height = None
        self.y_min_price = None
        self.y_max_price = None
        self.x_min_time = None
        self.x_max_time = None

    async def analyze_image(self, image_path: str) -> ChartAnalysis:
        """
        Анализирует изображение графика с помощью Claude Vision API

        Возвращает: ChartAnalysis с найденными уровнями и сигналами
        """
        from anthropic import Anthropic

        client = Anthropic()

        # Читаем изображение и преобразуем в base64
        with open(image_path, "rb") as img_file:
            image_data = img_file.read()

        import base64
        base64_image = base64.standard_b64encode(image_data).decode("utf-8")

        # Отправляем Vision API запрос
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": base64_image,
                            },
                        },
                        {
                            "type": "text",
                            "text": """Проанализируй этот скриншот TradingView графика по следующей схеме:

1. **Определи тренд:**
   - Восход (uptrend): цена выше MA9 > MA21
   - Спад (downtrend): цена ниже MA9 < MA21
   - Боковой тренд (ranging)

2. **Найди ключевые уровни:**
   - Уровни поддержки (где цена отскакивала вверх)
   - Уровни сопротивления (где цена отскакивала вниз)
   - Приблизительные цены (в виде чисел на правой оси)

3. **Определи точку входа:**
   - Где бы ты вошел в сделку (текущая цена или ожидаемая)
   - Примерная цена

4. **Рассчитай Stop Loss и Take Profit:**
   - SL обычно на уровне поддержки/сопротивления ниже/выше
   - TP с R:R 1:2

5. **Оцени уверенность:**
   - 0-100% на основе четкости сигнала

Ответь JSON'ом ТОЛЬКО (без других текстов):
{
    "pair": "GER40 или BTC или GOLD",
    "timeframe": "1H или 5M или 4H",
    "trend": "uptrend или downtrend или ranging",
    "signal_type": "BUY или SELL или null",
    "entry_price": число или null,
    "stop_loss": число или null,
    "take_profit": число или null,
    "confidence": число 0-100,
    "support_levels": [числа в порядке возрастания],
    "resistance_levels": [числа в порядке возрастания],
    "analysis": "Описание 2-3 предложениями почему это сильный/слабый сигнал",
    "price_high": число на верхнем краю экрана,
    "price_low": число на нижнем краю экрана
}"""
                        }
                    ],
                }
            ],
        )

        # Парсим ответ
        response_text = message.content[0].text
        logger.info(f"Vision API ответ:\n{response_text}")

        # Извлекаем JSON
        try:
            # Пытаемся найти JSON в ответе
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                analysis_json = json.loads(json_match.group())
            else:
                analysis_json = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            logger.error(f"Текст ответа: {response_text}")
            return None

        # Создаем объект ChartAnalysis
        analysis = ChartAnalysis(
            pair=analysis_json.get("pair", "UNKNOWN"),
            timeframe=analysis_json.get("timeframe", "1H"),
            trend=analysis_json.get("trend", "ranging"),
            entry_price=analysis_json.get("entry_price"),
            stop_loss=analysis_json.get("stop_loss"),
            take_profit=analysis_json.get("take_profit"),
            confidence=float(analysis_json.get("confidence", 50)),
            support_levels=analysis_json.get("support_levels", []),
            resistance_levels=analysis_json.get("resistance_levels", []),
            analysis_text=analysis_json.get("analysis", ""),
            signal_type=analysis_json.get("signal_type")
        )

        # Сохраняем границы цены для рисования
        self.y_min_price = analysis_json.get("price_low", 0)
        self.y_max_price = analysis_json.get("price_high", 100)

        logger.info(f"✅ Анализ завершен: {analysis.pair} {analysis.signal_type}")
        return analysis

    def draw_annotations(self, image_path: str, analysis: ChartAnalysis, output_path: str):
        """
        Рисует аннотации на изображение графика
        """
        # Открываем изображение
        img = Image.open(image_path)
        self.img_width, self.img_height = img.size

        draw = ImageDraw.Draw(img, 'RGBA')

        # Попробуем загрузить шрифт, если нет - используем дефолт
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # Функция для конвертации цены в пиксель
        def price_to_pixel(price: float) -> int:
            """Преобразует цену в Y координату на изображении"""
            if self.y_min_price is None or self.y_max_price is None:
                return int(self.img_height * 0.5)

            # Инвертируем: высокие цены вверху, низкие внизу
            ratio = (price - self.y_min_price) / (self.y_max_price - self.y_min_price)
            return int(self.img_height * (1 - ratio))

        # Рисуем уровни поддержки (зеленый)
        for support in analysis.support_levels:
            y = price_to_pixel(support)
            if 0 < y < self.img_height:
                # Горизонтальная линия
                draw.line([(0, y), (self.img_width, y)], fill=(0, 255, 0, 100), width=2)
                # Лейбл
                draw.text((10, y - 20), f"Support: {support:.2f}", fill=(0, 255, 0, 255), font=font_small)

        # Рисуем уровни сопротивления (красный)
        for resistance in analysis.resistance_levels:
            y = price_to_pixel(resistance)
            if 0 < y < self.img_height:
                # Горизонтальная линия
                draw.line([(0, y), (self.img_width, y)], fill=(255, 0, 0, 100), width=2)
                # Лейбл
                draw.text((10, y + 5), f"Resistance: {resistance:.2f}", fill=(255, 0, 0, 255), font=font_small)

        # Рисуем Entry
        if analysis.entry_price:
            y = price_to_pixel(analysis.entry_price)
            if 0 < y < self.img_height:
                # Толстая синяя линия
                draw.line([(0, y), (self.img_width, y)], fill=(0, 100, 255, 150), width=3)
                # Лейбл с фоном
                text = f"ENTRY: {analysis.entry_price:.2f}"
                bbox = draw.textbbox((20, y - 30), text, font=font_large)
                draw.rectangle(bbox, fill=(0, 100, 255, 200))
                draw.text((20, y - 30), text, fill=(255, 255, 255, 255), font=font_large)

        # Рисуем Stop Loss (оранжевый)
        if analysis.stop_loss:
            y = price_to_pixel(analysis.stop_loss)
            if 0 < y < self.img_height:
                draw.line([(0, y), (self.img_width, y)], fill=(255, 165, 0, 120), width=2)
                draw.text((10, y - 20), f"SL: {analysis.stop_loss:.2f}", fill=(255, 165, 0, 255), font=font_small)

        # Рисуем Take Profit (светло-зеленый)
        if analysis.take_profit:
            y = price_to_pixel(analysis.take_profit)
            if 0 < y < self.img_height:
                draw.line([(0, y), (self.img_width, y)], fill=(144, 238, 144, 120), width=2)
                draw.text((10, y + 5), f"TP: {analysis.take_profit:.2f}", fill=(144, 238, 144, 255), font=font_small)

        # Рисуем инфо-бокс в левом верхнем углу
        info_lines = [
            f"{analysis.pair} | {analysis.timeframe}",
            f"Trend: {analysis.trend.upper()}",
            f"Signal: {analysis.signal_type or 'NONE'}",
            f"Confidence: {analysis.confidence:.0f}%",
        ]

        y_offset = 10
        for line in info_lines:
            bbox = draw.textbbox((10, y_offset), line, font=font_small)
            draw.rectangle([(5, y_offset - 2), (bbox[2] + 5, bbox[3] + 2)], fill=(0, 0, 0, 150))
            draw.text((10, y_offset), line, fill=(255, 255, 255, 255), font=font_small)
            y_offset += 25

        # Сохраняем результат
        img.save(output_path)
        logger.info(f"✅ Аннотированное изображение сохранено: {output_path}")


async def analyze_chart(image_path: str, output_path: str) -> ChartAnalysis:
    """
    Главная функция: анализирует график и рисует на нем аннотации
    """
    logger.info(f"📊 Начинаю анализ: {image_path}")

    analyzer = ChartImageAnalyzer()

    # Анализируем
    analysis = await analyzer.analyze_image(image_path)
    if not analysis:
        logger.error("❌ Ошибка анализа")
        return None

    # Рисуем аннотации
    analyzer.draw_annotations(image_path, analysis, output_path)

    # Выводим результаты
    print("\n" + "="*60)
    print(f"📊 РЕЗУЛЬТАТ АНАЛИЗА: {analysis.pair}")
    print("="*60)
    print(f"🔹 Пара: {analysis.pair}")
    print(f"🔹 Таймфрейм: {analysis.timeframe}")
    print(f"🔹 Тренд: {analysis.trend.upper()}")
    print(f"🔹 Сигнал: {analysis.signal_type or 'НЕТ'}")
    print(f"🔹 Уверенность: {analysis.confidence:.0f}%")
    if analysis.entry_price:
        print(f"🔹 Вход: {analysis.entry_price:.5f}")
    if analysis.stop_loss:
        print(f"🔹 SL: {analysis.stop_loss:.5f}")
    if analysis.take_profit:
        print(f"🔹 TP: {analysis.take_profit:.5f}")
    print(f"\n💡 Анализ: {analysis.analysis_text}")
    print(f"\n✅ Аннотированное фото: {output_path}")
    print("="*60 + "\n")

    return analysis


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Использование: python chart_analyzer.py <путь_к_фото>")
        sys.exit(1)

    image_path = sys.argv[1]
    output_path = image_path.replace(".png", "_analyzed.png")

    asyncio.run(analyze_chart(image_path, output_path))
