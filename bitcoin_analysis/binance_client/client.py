"""
Cliente para integração com API da Binance
"""
import logging
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import requests
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class BinanceClient:
    """
    Cliente para comunicação com a API da Binance
    """
    
    BASE_URL = "https://api.binance.com/api/v3"
    TESTNET_URL = "https://testnet.binance.vision/api/v3"
    
    def __init__(self):
        self.api_key = settings.BINANCE_API_KEY
        self.api_secret = settings.BINANCE_API_SECRET
        self.testnet = settings.BINANCE_TESTNET
        self.read_only_mode = settings.API_READ_ONLY_MODE
        
        if self.testnet:
            self.base_url = self.TESTNET_URL
        else:
            self.base_url = self.BASE_URL
        
        self.session = requests.Session()
        self.last_request_time = 0
        self.rate_limit_delay = 0.1  # Delay mínimo entre requisições (100ms)
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Faz uma requisição à API da Binance com tratamento de erros e rate limiting
        """
        if self.read_only_mode and endpoint not in ['/klines', '/ticker/price']:
            logger.warning("Modo somente leitura ativado. Operação bloqueada.")
            return {}
        
        # Rate limiting
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last_request)
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            self.last_request_time = time.time()
            
            # Verificar rate limit
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                logger.warning(f"Rate limit atingido. Aguardando {retry_after} segundos...")
                time.sleep(retry_after)
                return self._make_request(endpoint, params)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout ao conectar com Binance: {endpoint}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição à Binance: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            raise
    
    def get_current_price(self, symbol: str = 'BTCUSDT') -> Optional[float]:
        """
        Obtém o preço atual de um símbolo
        """
        try:
            endpoint = "/ticker/price"
            params = {"symbol": symbol}
            data = self._make_request(endpoint, params)
            return float(data.get('price', 0))
        except Exception as e:
            logger.error(f"Erro ao obter preço atual: {e}")
            return None
    
    def get_klines(
        self,
        symbol: str = 'BTCUSDT',
        interval: str = '1h',
        limit: int = 500,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[List]:
        """
        Obtém dados de candles (klines) da Binance
        
        Args:
            symbol: Par de negociação (ex: BTCUSDT)
            interval: Intervalo (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Número máximo de candles (máx 1000)
            start_time: Data/hora inicial
            end_time: Data/hora final
        
        Returns:
            Lista de candles no formato da Binance
        """
        try:
            endpoint = "/klines"
            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": min(limit, 1000)
            }
            
            if start_time:
                params["startTime"] = int(start_time.timestamp() * 1000)
            if end_time:
                params["endTime"] = int(end_time.timestamp() * 1000)
            
            data = self._make_request(endpoint, params)
            return data
            
        except Exception as e:
            logger.error(f"Erro ao obter klines: {e}")
            return []
    
    def get_historical_klines(
        self,
        symbol: str = 'BTCUSDT',
        interval: str = '1h',
        days: int = 30
    ) -> List[List]:
        """
        Obtém dados históricos de candles
        
        Args:
            symbol: Par de negociação
            interval: Intervalo
            days: Número de dias para buscar
        
        Returns:
            Lista de candles
        """
        end_time = timezone.now()
        start_time = end_time - timedelta(days=days)
        
        all_klines = []
        current_start = start_time
        
        while current_start < end_time:
            klines = self.get_klines(
                symbol=symbol,
                interval=interval,
                limit=1000,
                start_time=current_start,
                end_time=end_time
            )
            
            if not klines:
                break
            
            all_klines.extend(klines)
            
            # Próximo batch
            last_time = datetime.fromtimestamp(klines[-1][0] / 1000)
            current_start = last_time + timedelta(seconds=1)
            
            # Evitar rate limit
            time.sleep(0.2)
        
        return all_klines
