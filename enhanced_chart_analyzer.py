#!/usr/bin/env python3
"""
Enhanced Chart Analyzer - детальный анализ графиков с аннотациями
Включает: уровни, entry, SL, TP, вероятность выигрыша, альтернативные входы
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
class TradeSetup:
    """Полный торговый сетап с расширенной информацией"""
    pair: str
    timeframe: str
    trend: str
    signal_type: Optional[str]
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float
    win_probability: float
    support_levels: List[float]
    resistance_levels: List[float]
    alternative_entries: List[Dict[str, str]]  # [{"price": 25150, "description": "Better R:R"}, ...]
    price_action_notes: str
    intellect_score: float
    price_high: float
    price_low: float


class EnhancedChartAnalyzer:
    """Создает детальные аннотированные графики с полной информацией о сделке"""

    def __init__(self):
        self.img_width = None
        self.img_height = None
        self.y_min_price = None
        self.y_max_price = None

    def create_annotated_chart(self, image_path: str, setup: TradeSetup, output_path: str):
        """
        Создает аннотированный график со всеми деталями торговой сделки
        """
        # Открываем изображение
        img = Image.open(image_path)
        self.img_width, self.img_height = img.size

        draw = ImageDraw.Draw(img, 'RGBA')

        # Загружаем шрифты
        try:
            font_xlarge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
            font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except:
            font_xlarge = font_large = font_medium = font_small = ImageFont.load_default()

        def price_to_pixel(price: float) -> int:
            """Преобразует цену в Y координату (инвертировано)"""
            if self.y_min_price is None or self.y_max_price is None:
                return int(self.img_height * 0.5)
            ratio = (price - self.y_min_price) / (self.y_max_price - self.y_min_price)
            return int(self.img_height * (1 - ratio))

        self.y_min_price = setup.price_low
        self.y_max_price = setup.price_high

        # ===== УРОВНИ ПОДДЕРЖКИ (Зеленый) =====
        for i, support in enumerate(setup.support_levels):
            y = price_to_pixel(support)
            if 0 < y < self.img_height:
                draw.line([(0, y), (self.img_width, y)], fill=(0, 200, 100, 120), width=2)
                # Левая сторона
                draw.text((5, y - 12), f"{support:.0f}", fill=(0, 200, 100, 255), font=font_small)
                # Правая сторона
                bbox = draw.textbbox((0, y - 12), f"{support:.0f}", font=font_small)
                draw.text((self.img_width - (bbox[2] - bbox[0]) - 5, y - 12), f"{support:.0f}",
                         fill=(0, 200, 100, 255), font=font_small)

        # ===== УРОВНИ СОПРОТИВЛЕНИЯ (Красный) =====
        for i, resistance in enumerate(setup.resistance_levels):
            y = price_to_pixel(resistance)
            if 0 < y < self.img_height:
                draw.line([(0, y), (self.img_width, y)], fill=(220, 50, 50, 120), width=2)
                # Левая сторона
                draw.text((5, y + 3), f"{resistance:.0f}", fill=(220, 50, 50, 255), font=font_small)
                # Правая сторона
                bbox = draw.textbbox((0, y + 3), f"{resistance:.0f}", font=font_small)
                draw.text((self.img_width - (bbox[2] - bbox[0]) - 5, y + 3), f"{resistance:.0f}",
                         fill=(220, 50, 50, 255), font=font_small)

        # ===== ENTRY (Синий) =====
        if setup.entry_price:
            y = price_to_pixel(setup.entry_price)
            if 0 < y < self.img_height:
                draw.line([(0, y), (self.img_width, y)], fill=(50, 150, 255, 180), width=4)
                text = f"ENTRY: {setup.entry_price:.2f}"
                bbox = draw.textbbox((15, y - 28), text, font=font_large)
                draw.rectangle([(12, y - 30), (bbox[2] + 18, bbox[3] + 5)],
                             fill=(50, 150, 255, 220), outline=(255, 255, 255, 255), width=2)
                draw.text((15, y - 28), text, fill=(255, 255, 255, 255), font=font_large)

        # ===== STOP LOSS (Оранжевый) =====
        if setup.stop_loss:
            y = price_to_pixel(setup.stop_loss)
            if 0 < y < self.img_height:
                draw.line([(0, y), (self.img_width, y)], fill=(255, 140, 0, 150), width=2)
                risk_pips = abs(setup.entry_price - setup.stop_loss) * 100
                text_sl = f"SL: {setup.stop_loss:.2f} ({risk_pips:.0f}p)"
                draw.text((5, y - 15), text_sl, fill=(255, 140, 0, 255), font=font_small)

        # ===== TAKE PROFIT (Светло-зеленый) =====
        if setup.take_profit:
            y = price_to_pixel(setup.take_profit)
            if 0 < y < self.img_height:
                draw.line([(0, y), (self.img_width, y)], fill=(100, 255, 100, 150), width=2)
                profit_pips = abs(setup.take_profit - setup.entry_price) * 100
                text_tp = f"TP: {setup.take_profit:.2f} ({profit_pips:.0f}p)"
                draw.text((5, y + 3), text_tp, fill=(100, 255, 100, 255), font=font_small)

        # ===== АЛЬТЕРНАТИВНЫЕ ВХОДЫ (Серый пунктир) =====
        for alt in setup.alternative_entries:
            alt_price = float(alt.get("price", 0))
            if alt_price > 0:
                y = price_to_pixel(alt_price)
                if 0 < y < self.img_height:
                    # Пунктирная линия
                    for x in range(0, self.img_width, 8):
                        draw.line([(x, y), (x + 4, y)], fill=(150, 150, 150, 100), width=1)
                    draw.text((5, y - 28), alt.get("description", f"Alt: {alt_price:.0f}"),
                             fill=(150, 150, 150, 200), font=font_small)

        # ===== ГЛАВНЫЙ ИНФО БОX (Верхний левый угол) =====
        info_lines = [
            f"═══════════════════════════",
            f"  {setup.pair} | {setup.timeframe}",
            f"═══════════════════════════",
            f"  Тренд: {setup.trend.upper()}",
            f"  Сигнал: {setup.signal_type or 'НЕТ'}",
            f"  Уверенность: {setup.confidence:.0f}%",
            f"  INTELLECT_city: {setup.intellect_score:.0f}%",
            f"═══════════════════════════",
        ]

        y_offset = 15
        for line in info_lines:
            bbox = draw.textbbox((18, y_offset), line, font=font_medium)
            draw.rectangle([(10, y_offset - 3), (bbox[2] + 15, bbox[3] + 3)],
                         fill=(0, 0, 0, 180), outline=(100, 100, 100, 200), width=1)
            draw.text((18, y_offset), line, fill=(255, 255, 255, 255), font=font_medium)
            y_offset += 24

        # ===== ТОРГОВЫЕ ПАРАМЕТРЫ (Нижний левый угол) =====
        risk_pips = abs(setup.entry_price - setup.stop_loss) * 100
        profit_pips = abs(setup.take_profit - setup.entry_price) * 100
        rr_ratio = profit_pips / risk_pips if risk_pips > 0 else 0

        trade_lines = [
            f"═══ ТОРГОВАЯ СДЕЛКА ═══",
            f"Entry: {setup.entry_price:.2f}",
            f"SL: {setup.stop_loss:.2f} ({risk_pips:.0f}p риск)",
            f"TP: {setup.take_profit:.2f} ({profit_pips:.0f}p прибыль)",
            f"R:R: 1:{rr_ratio:.1f}",
            f"Вероятность TP: {setup.win_probability:.0f}%",
            f"═══════════════════════",
        ]

        y_offset = self.img_height - 190
        for line in trade_lines:
            bbox = draw.textbbox((18, y_offset), line, font=font_medium)
            draw.rectangle([(10, y_offset - 3), (bbox[2] + 15, bbox[3] + 3)],
                         fill=(0, 0, 0, 180), outline=(100, 100, 100, 200), width=1)
            draw.text((18, y_offset), line, fill=(200, 200, 100, 255), font=font_medium)
            y_offset += 20

        # ===== ОЖИДАНИЕ ЦЕНЫ (Нижний правый угол) =====
        action_lines = [
            f"РЕАКЦИЯ НА УРОВНЯХ:",
            f"• Поддержка - отскок вверх",
            f"• Сопротивление - отскок вниз",
            f"• Entry - пробой вверх",
            f"• Take Profit - целевая зона",
        ]

        y_offset = self.img_height - 130
        x_right_start = self.img_width - 280
        for line in action_lines:
            bbox = draw.textbbox((x_right_start + 10, y_offset), line, font=font_small)
            draw.rectangle([(x_right_start, y_offset - 3), (self.img_width - 5, bbox[3] + 3)],
                         fill=(0, 0, 0, 180), outline=(100, 100, 100, 200), width=1)
            draw.text((x_right_start + 10, y_offset), line, fill=(150, 200, 255, 255), font=font_small)
            y_offset += 18

        # Сохраняем результат
        img.save(output_path)
        logger.info(f"✅ Аннотированный график сохранен: {output_path}")
        print(f"\n📊 График сохранен: {output_path}")


def create_demo_analysis() -> TradeSetup:
    """
    Создает демо торговый сетап для примера GER40
    """
    return TradeSetup(
        pair="GER40",
        timeframe="1H",
        trend="uptrend",
        signal_type="BUY",
        entry_price=25172.5,
        stop_loss=25100.0,
        take_profit=25317.5,  # Правильный расчет: Entry + (Entry - SL) * 2
        confidence=78.0,
        win_probability=78.0,
        support_levels=[25000.0, 25040.0, 25080.0],
        resistance_levels=[25100.0, 25140.0, 25160.0],
        alternative_entries=[
            {"price": "25150", "description": "Alt Entry: Лучший R:R (27:2)"},
            {"price": "25120", "description": "Alt Entry: Больше прибыли (+52p)"},
            {"price": "25080", "description": "Alt Entry: Макс прибыль (+237p)"},
        ],
        price_action_notes="Ожидаем пробой выше сопротивления 25160 с целью TP",
        intellect_score=68.5,
        price_high=25200.0,
        price_low=24950.0,
    )


if __name__ == "__main__":
    import sys

    print("\n" + "=" * 60)
    print("🎯 ENHANCED CHART ANALYZER v2.0")
    print("=" * 60)

    # Если передана путь к изображению
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        output_path = image_path.replace(".png", "_enhanced.png")

        # Создаем демо сетап
        setup = create_demo_analysis()

        print(f"\n📊 Анализирую: {image_path}")
        print(f"Пара: {setup.pair} | Таймфрейм: {setup.timeframe}")
        print(f"Сигнал: {setup.signal_type} @ {setup.entry_price:.2f}")
        print(f"SL: {setup.stop_loss:.2f} | TP: {setup.take_profit:.2f}")
        print(f"Уверенность: {setup.confidence:.0f}% | INTELLECT_city: {setup.intellect_score:.0f}%")

        # Анализируем
        analyzer = EnhancedChartAnalyzer()
        analyzer.create_annotated_chart(image_path, setup, output_path)

        print(f"\n✅ Результат сохранен: {output_path}")
    else:
        print("Использование: python enhanced_chart_analyzer.py <путь_к_изображению>")
        print("\nПример с демо данными:")
        setup = create_demo_analysis()
        print(f"  Пара: {setup.pair}")
        print(f"  Тренд: {setup.trend}")
        print(f"  Сигнал: {setup.signal_type}")
        print(f"  Entry: {setup.entry_price:.2f}")
        print(f"  SL: {setup.stop_loss:.2f}")
        print(f"  TP: {setup.take_profit:.2f} (правильный R:R 1:2)")
        print(f"  R:R ratio: 1:{(setup.take_profit - setup.entry_price) / (setup.entry_price - setup.stop_loss):.1f}")
