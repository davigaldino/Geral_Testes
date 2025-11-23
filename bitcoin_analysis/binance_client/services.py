"""
Serviços para processamento de dados da Binance
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from django.utils import timezone
from django.db import transaction
from .client import BinanceClient
from .models import Candle, CurrentPrice

logger = logging.getLogger(__name__)


class BinanceDataService:
    """
    Serviço para gerenciar dados da Binance
    """
    
    def __init__(self):
        self.client = BinanceClient()
    
    def update_current_price(self, symbol: str = 'BTCUSDT') -> bool:
        """
        Atualiza o preço atual do símbolo
        """
        try:
            price = self.client.get_current_price(symbol)
            if price:
                current_price, created = CurrentPrice.objects.update_or_create(
                    symbol=symbol,
                    defaults={'price': price}
                )
                logger.info(f"Preço atualizado: {symbol} = {price}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao atualizar preço atual: {e}")
            return False
    
    def save_candle(self, kline_data: List, symbol: str = 'BTCUSDT', interval: str = '1h') -> Optional[Candle]:
        """
        Salva um candle no banco de dados
        
        Formato kline_data da Binance:
        [open_time, open, high, low, close, volume, close_time, quote_volume, trades, ...]
        """
        try:
            open_time = datetime.fromtimestamp(kline_data[0] / 1000, tz=timezone.utc)
            close_time = datetime.fromtimestamp(kline_data[6] / 1000, tz=timezone.utc)
            
            candle, created = Candle.objects.update_or_create(
                symbol=symbol,
                interval=interval,
                open_time=open_time,
                defaults={
                    'close_time': close_time,
                    'open_price': float(kline_data[1]),
                    'high_price': float(kline_data[2]),
                    'low_price': float(kline_data[3]),
                    'close_price': float(kline_data[4]),
                    'volume': float(kline_data[5]),
                    'quote_volume': float(kline_data[7]),
                    'trades_count': int(kline_data[8]),
                }
            )
            
            if created:
                logger.debug(f"Candle criado: {symbol} {interval} {open_time}")
            else:
                logger.debug(f"Candle atualizado: {symbol} {interval} {open_time}")
            
            return candle
            
        except Exception as e:
            logger.error(f"Erro ao salvar candle: {e}")
            return None
    
    def fetch_and_save_candles(
        self,
        symbol: str = 'BTCUSDT',
        interval: str = '1h',
        limit: int = 500
    ) -> int:
        """
        Busca e salva candles da Binance
        
        Returns:
            Número de candles salvos
        """
        try:
            klines = self.client.get_klines(symbol=symbol, interval=interval, limit=limit)
            
            saved_count = 0
            with transaction.atomic():
                for kline in klines:
                    candle = self.save_candle(kline, symbol=symbol, interval=interval)
                    if candle:
                        saved_count += 1
            
            logger.info(f"Salvos {saved_count} candles para {symbol} {interval}")
            return saved_count
            
        except Exception as e:
            logger.error(f"Erro ao buscar e salvar candles: {e}")
            return 0
    
    def fetch_new_candles(self, symbol: str = 'BTCUSDT', intervals: List[str] = None) -> Dict[str, int]:
        """
        Busca apenas candles novos (não existentes no banco)
        
        Args:
            symbol: Par de negociação
            intervals: Lista de intervalos para buscar
        
        Returns:
            Dicionário com contagem de candles salvos por intervalo
        """
        if intervals is None:
            intervals = ['1m', '5m', '15m', '1h', '4h', '1d']
        
        results = {}
        
        for interval in intervals:
            try:
                # Buscar último candle no banco
                last_candle = Candle.objects.filter(
                    symbol=symbol,
                    interval=interval
                ).order_by('-open_time').first()
                
                if last_candle:
                    # Buscar candles desde o último
                    start_time = last_candle.open_time
                    limit = 500
                else:
                    # Primeira vez: buscar últimos 500 candles
                    start_time = None
                    limit = 500
                
                klines = self.client.get_klines(
                    symbol=symbol,
                    interval=interval,
                    limit=limit,
                    start_time=start_time
                )
                
                saved_count = 0
                with transaction.atomic():
                    for kline in klines:
                        candle = self.save_candle(kline, symbol=symbol, interval=interval)
                        if candle:
                            saved_count += 1
                
                results[interval] = saved_count
                logger.info(f"Novos candles para {symbol} {interval}: {saved_count}")
                
            except Exception as e:
                logger.error(f"Erro ao buscar novos candles para {interval}: {e}")
                results[interval] = 0
        
        return results
    
    def cleanup_old_data(self, days_to_keep: int = 90) -> int:
        """
        Remove dados antigos do banco
        
        Args:
            days_to_keep: Número de dias para manter
        
        Returns:
            Número de registros deletados
        """
        try:
            cutoff_date = timezone.now() - timedelta(days=days_to_keep)
            
            deleted_count, _ = Candle.objects.filter(
                open_time__lt=cutoff_date
            ).delete()
            
            logger.info(f"Limpeza: {deleted_count} candles antigos removidos")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Erro na limpeza de dados: {e}")
            return 0
