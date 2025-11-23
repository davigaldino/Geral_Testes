"""
Testes para signals
"""
from django.test import TestCase
from binance_client.models import Candle
from indicators.models import IndicatorValue
from signals.generators import SignalGenerator
from django.utils import timezone
from datetime import timedelta


class SignalGeneratorTestCase(TestCase):
    """Testes para SignalGenerator"""
    
    def setUp(self):
        self.generator = SignalGenerator()
        
        # Criar candle de teste
        self.candle = Candle.objects.create(
            symbol='BTCUSDT',
            interval='1h',
            open_time=timezone.now() - timedelta(hours=1),
            close_time=timezone.now(),
            open_price=50000,
            high_price=51000,
            low_price=49000,
            close_price=50500,
            volume=1000,
            quote_volume=50500000,
            trades_count=100
        )
    
    def test_check_rsi_signals_buy(self):
        """Testa sinal de compra baseado em RSI baixo"""
        IndicatorValue.objects.create(
            candle=self.candle,
            indicator_name='RSI',
            value=25.0
        )
        
        signal_type, confidence = self.generator.check_rsi_signals(self.candle)
        self.assertEqual(signal_type, 'BUY')
        self.assertGreater(confidence, 0)
    
    def test_check_rsi_signals_sell(self):
        """Testa sinal de venda baseado em RSI alto"""
        IndicatorValue.objects.create(
            candle=self.candle,
            indicator_name='RSI',
            value=75.0
        )
        
        signal_type, confidence = self.generator.check_rsi_signals(self.candle)
        self.assertEqual(signal_type, 'SELL')
        self.assertGreater(confidence, 0)
    
    def test_check_zscore_signals_buy(self):
        """Testa sinal de compra baseado em Z-Score baixo"""
        IndicatorValue.objects.create(
            candle=self.candle,
            indicator_name='ZSCORE',
            value=-2.5
        )
        
        signal_type, confidence = self.generator.check_zscore_signals(self.candle)
        self.assertEqual(signal_type, 'BUY')
        self.assertGreater(confidence, 0)
    
    def test_generate_signal(self):
        """Testa geração completa de sinal"""
        # Criar indicadores necessários
        IndicatorValue.objects.create(
            candle=self.candle,
            indicator_name='RSI',
            value=25.0
        )
        IndicatorValue.objects.create(
            candle=self.candle,
            indicator_name='EMA_50',
            value=50000
        )
        IndicatorValue.objects.create(
            candle=self.candle,
            indicator_name='EMA_200',
            value=49000
        )
        
        signal_data = self.generator.generate_signal(self.candle)
        self.assertIn('signal_type', signal_data)
        self.assertIn('confidence_score', signal_data)
        self.assertIn('reasons', signal_data)
