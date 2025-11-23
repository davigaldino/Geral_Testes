"""
Tarefas Celery para indicators
"""
import logging
from celery import shared_task
from .services import IndicatorService

logger = logging.getLogger(__name__)


@shared_task(name='indicators.tasks.compute_indicators')
def compute_indicators(symbol: str = 'BTCUSDT'):
    """
    Tarefa Celery para calcular indicadores técnicos
    """
    try:
        service = IndicatorService()
        intervals = ['1h', '4h', '1d']
        results = service.compute_all_indicators(symbol=symbol, intervals=intervals)
        
        logger.info(f"Tarefa compute_indicators concluída: {results}")
        return results
        
    except Exception as e:
        logger.error(f"Erro na tarefa compute_indicators: {e}")
        raise
