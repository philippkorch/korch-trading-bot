"""
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
