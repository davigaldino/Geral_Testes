"""
Serviços para geração de sinais
"""
import logging
from django.db import transaction
from binance_client.models import Candle
from .models import TradingSignal
from .generators import SignalGenerator

logger = logging.getLogger(__name__)


class SignalService:
    """
    Serviço para gerenciar geração de sinais
    """
    
    def __init__(self):
        self.generator = SignalGenerator()
    
    def generate_signals_for_interval(
        self,
        symbol: str = 'BTCUSDT',
        interval: str = '1h',
        limit: int = 10
    ) -> int:
        """
        Gera sinais para os últimos candles de um intervalo
        """
        try:
            # Buscar últimos candles com indicadores calculados
            candles = Candle.objects.filter(
                symbol=symbol,
                interval=interval
            ).order_by('-open_time')[:limit]
            
            if not candles.exists():
                logger.warning(f"Nenhum candle encontrado para {symbol} {interval}")
                return 0
            
            saved_count = 0
            
            with transaction.atomic():
                for candle in candles:
                    # Verificar se já existe sinal para este candle
                    existing_signal = TradingSignal.objects.filter(candle=candle).first()
                    if existing_signal:
                        continue
                    
                    # Gerar sinal
                    signal_data = self.generator.generate_signal(candle)
                    
                    # Salvar sinal
                    signal = TradingSignal.objects.create(
                        candle=candle,
                        signal_type=signal_data['signal_type'],
                        confidence_score=signal_data['confidence_score'],
                        reasons=signal_data['reasons'],
                        indicators_used=signal_data['indicators_used']
                    )
                    
                    saved_count += 1
                    logger.debug(f"Sinal gerado: {signal}")
            
            logger.info(f"Sinais gerados para {symbol} {interval}: {saved_count}")
            return saved_count
            
        except Exception as e:
            logger.error(f"Erro ao gerar sinais: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return 0
    
    def generate_all_signals(self, symbol: str = 'BTCUSDT', intervals: list = None) -> dict:
        """
        Gera sinais para todos os intervalos
        """
        if intervals is None:
            intervals = ['1h', '4h', '1d']
        
        results = {}
        
        for interval in intervals:
            count = self.generate_signals_for_interval(symbol=symbol, interval=interval, limit=5)
            results[f'{interval}_signals'] = count
        
        return results
