"""
Tarefas Celery para binance_client
"""
import logging
from celery import shared_task
from django.conf import settings
from .services import BinanceDataService

logger = logging.getLogger(__name__)


@shared_task(name='binance_client.tasks.fetch_new_candles')
def fetch_new_candles(symbol: str = 'BTCUSDT'):
    """
    Tarefa Celery para buscar novos candles
    """
    try:
        service = BinanceDataService()
        
        # Atualizar preço atual
        service.update_current_price(symbol)
        
        # Buscar novos candles
        intervals = ['1m', '5m', '15m', '1h', '4h', '1d']
        results = service.fetch_new_candles(symbol=symbol, intervals=intervals)
        
        logger.info(f"Tarefa fetch_new_candles concluída: {results}")
        return results
        
    except Exception as e:
        logger.error(f"Erro na tarefa fetch_new_candles: {e}")
        raise


@shared_task(name='binance_client.tasks.cleanup_old_data')
def cleanup_old_data(days_to_keep: int = 90):
    """
    Tarefa Celery para limpar dados antigos
    """
    try:
        service = BinanceDataService()
        deleted_count = service.cleanup_old_data(days_to_keep=days_to_keep)
        
        logger.info(f"Tarefa cleanup_old_data concluída: {deleted_count} registros deletados")
        return deleted_count
        
    except Exception as e:
        logger.error(f"Erro na tarefa cleanup_old_data: {e}")
        raise
