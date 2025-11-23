"""
Testes para binance_client
"""
from django.test import TestCase
from unittest.mock import Mock, patch
from datetime import datetime
from django.utils import timezone
from .client import BinanceClient
from .services import BinanceDataService
from .models import Candle, CurrentPrice


class BinanceClientTestCase(TestCase):
    """Testes para BinanceClient"""
    
    def setUp(self):
        self.client = BinanceClient()
    
    @patch('binance_client.client.requests.Session.get')
    def test_get_current_price(self, mock_get):
        """Testa obtenção de preço atual"""
        mock_response = Mock()
        mock_response.json.return_value = {'price': '50000.00'}
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        price = self.client.get_current_price('BTCUSDT')
        self.assertEqual(price, 50000.00)
    
    @patch('binance_client.client.requests.Session.get')
    def test_get_klines(self, mock_get):
        """Testa obtenção de klines"""
        mock_response = Mock()
        mock_response.json.return_value = [
            [1609459200000, '29000', '30000', '28000', '29500', '1000', 1609545600000, '29500000', 100, '500', '500', '0']
        ]
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        klines = self.client.get_klines('BTCUSDT', '1h', limit=1)
        self.assertEqual(len(klines), 1)
        self.assertEqual(klines[0][0], 1609459200000)


class BinanceDataServiceTestCase(TestCase):
    """Testes para BinanceDataService"""
    
    def setUp(self):
        self.service = BinanceDataService()
    
    def test_save_candle(self):
        """Testa salvamento de candle"""
        kline_data = [
            1609459200000,  # open_time
            '29000',  # open
            '30000',  # high
            '28000',  # low
            '29500',  # close
            '1000',  # volume
            1609545600000,  # close_time
            '29500000',  # quote_volume
            100,  # trades
        ]
        
        candle = self.service.save_candle(kline_data, 'BTCUSDT', '1h')
        self.assertIsNotNone(candle)
        self.assertEqual(float(candle.open_price), 29000)
        self.assertEqual(float(candle.close_price), 29500)
    
    def test_update_current_price(self):
        """Testa atualização de preço atual"""
        with patch.object(self.service.client, 'get_current_price', return_value=50000.0):
            result = self.service.update_current_price('BTCUSDT')
            self.assertTrue(result)
            
            current_price = CurrentPrice.objects.filter(symbol='BTCUSDT').first()
            self.assertIsNotNone(current_price)
            self.assertEqual(float(current_price.price), 50000.0)
