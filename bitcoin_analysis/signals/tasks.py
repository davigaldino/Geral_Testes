"""
Tarefas Celery para signals
"""
import logging
from celery import shared_task
from .services import SignalService

logger = logging.getLogger(__name__)


@shared_task(name='signals.tasks.generate_signals')
def generate_signals(symbol: str = 'BTCUSDT'):
    """
    Tarefa Celery para gerar sinais de trading
    """
    try:
        service = SignalService()
        intervals = ['1h', '4h', '1d']
        results = service.generate_all_signals(symbol=symbol, intervals=intervals)
        
        logger.info(f"Tarefa generate_signals concluída: {results}")
        return results
        
    except Exception as e:
        logger.error(f"Erro na tarefa generate_signals: {e}")
        raise
