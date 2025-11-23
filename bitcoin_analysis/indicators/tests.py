"""
Testes para indicators
"""
from django.test import TestCase
import pandas as pd
import numpy as np
from .calculators import TechnicalIndicators
from binance_client.models import Candle
from django.utils import timezone
from datetime import timedelta


class TechnicalIndicatorsTestCase(TestCase):
    """Testes para TechnicalIndicators"""
    
    def setUp(self):
        self.calculator = TechnicalIndicators()
        # Criar DataFrame de teste
        dates = pd.date_range(start='2024-01-01', periods=100, freq='1H')
        np.random.seed(42)
        prices = 50000 + np.cumsum(np.random.randn(100) * 100)
        
        self.df = pd.DataFrame({
            'open_price': prices,
            'high_price': prices + np.random.rand(100) * 200,
            'low_price': prices - np.random.rand(100) * 200,
            'close_price': prices + np.random.randn(100) * 50,
            'volume': np.random.rand(100) * 1000,
        })
    
    def test_calculate_rsi(self):
        """Testa cálculo de RSI"""
        df = self.calculator.calculate_rsi(self.df.copy(), period=14)
        self.assertIn('rsi', df.columns)
        self.assertFalse(df['rsi'].isna().all())
    
    def test_calculate_sma(self):
        """Testa cálculo de SMA"""
        df = self.calculator.calculate_sma(self.df.copy(), period=20)
        self.assertIn('sma_20', df.columns)
        self.assertFalse(df['sma_20'].isna().all())
    
    def test_calculate_ema(self):
        """Testa cálculo de EMA"""
        df = self.calculator.calculate_ema(self.df.copy(), period=50)
        self.assertIn('ema_50', df.columns)
        self.assertFalse(df['ema_50'].isna().all())
    
    def test_calculate_macd(self):
        """Testa cálculo de MACD"""
        df = self.calculator.calculate_macd(self.df.copy())
        self.assertIn('macd', df.columns)
        self.assertIn('macd_signal', df.columns)
        self.assertIn('macd_histogram', df.columns)
    
    def test_calculate_bollinger_bands(self):
        """Testa cálculo de Bollinger Bands"""
        df = self.calculator.calculate_bollinger_bands(self.df.copy())
        self.assertIn('bb_upper', df.columns)
        self.assertIn('bb_middle', df.columns)
        self.assertIn('bb_lower', df.columns)
    
    def test_calculate_mean_reversion_zscore(self):
        """Testa cálculo de Z-Score"""
        df = self.calculator.calculate_mean_reversion_zscore(self.df.copy())
        self.assertIn('zscore', df.columns)
        self.assertFalse(df['zscore'].isna().all())
