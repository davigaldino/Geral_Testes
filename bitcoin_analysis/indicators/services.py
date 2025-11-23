"""
Serviços para calcular e armazenar indicadores técnicos
"""
import logging
import pandas as pd
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from binance_client.models import Candle
from .models import IndicatorValue, SupportResistanceLevel, FibonacciLevel
from .calculators import TechnicalIndicators

logger = logging.getLogger(__name__)


class IndicatorService:
    """
    Serviço para calcular e armazenar indicadores
    """
    
    def __init__(self):
        self.calculator = TechnicalIndicators()
    
    def candles_to_dataframe(self, candles: list) -> pd.DataFrame:
        """
        Converte queryset de candles para DataFrame
        """
        data = []
        for candle in candles:
            data.append({
                'open_time': candle.open_time,
                'open_price': float(candle.open_price),
                'high_price': float(candle.high_price),
                'low_price': float(candle.low_price),
                'close_price': float(candle.close_price),
                'volume': float(candle.volume),
                'candle_id': candle.id,
            })
        
        df = pd.DataFrame(data)
        if not df.empty:
            df = df.sort_values('open_time')
            df = df.reset_index(drop=True)
        
        return df
    
    def save_indicator_value(
        self,
        candle: Candle,
        indicator_name: str,
        value: float,
        metadata: dict = None
    ) -> IndicatorValue:
        """
        Salva um valor de indicador no banco
        """
        indicator_value, created = IndicatorValue.objects.update_or_create(
            candle=candle,
            indicator_name=indicator_name,
            defaults={
                'value': value,
                'metadata': metadata or {}
            }
        )
        return indicator_value
    
    def compute_indicators_for_interval(
        self,
        symbol: str = 'BTCUSDT',
        interval: str = '1h',
        limit: int = 500
    ) -> int:
        """
        Calcula todos os indicadores para um intervalo específico
        """
        try:
            # Buscar candles
            candles = Candle.objects.filter(
                symbol=symbol,
                interval=interval
            ).order_by('open_time')[:limit]
            
            if not candles.exists():
                logger.warning(f"Nenhum candle encontrado para {symbol} {interval}")
                return 0
            
            # Converter para DataFrame
            df = self.candles_to_dataframe(list(candles))
            
            if df.empty or len(df) < 200:
                logger.warning(f"Dados insuficientes para calcular indicadores: {len(df)} candles")
                return 0
            
            # Calcular indicadores
            df = self.calculator.calculate_all_indicators(df)
            
            # Salvar indicadores no banco
            saved_count = 0
            with transaction.atomic():
                for idx, row in df.iterrows():
                    candle_id = row['candle_id']
                    candle = Candle.objects.get(id=candle_id)
                    
                    # RSI
                    if pd.notna(row.get('rsi')):
                        self.save_indicator_value(candle, 'RSI', float(row['rsi']))
                        saved_count += 1
                    
                    # SMA 20
                    if pd.notna(row.get('sma_20')):
                        self.save_indicator_value(candle, 'SMA_20', float(row['sma_20']))
                        saved_count += 1
                    
                    # EMA 50
                    if pd.notna(row.get('ema_50')):
                        self.save_indicator_value(candle, 'EMA_50', float(row['ema_50']))
                        saved_count += 1
                    
                    # EMA 200
                    if pd.notna(row.get('ema_200')):
                        self.save_indicator_value(candle, 'EMA_200', float(row['ema_200']))
                        saved_count += 1
                    
                    # MACD
                    if pd.notna(row.get('macd')):
                        self.save_indicator_value(
                            candle,
                            'MACD',
                            float(row['macd']),
                            metadata={
                                'signal': float(row.get('macd_signal', 0)),
                                'histogram': float(row.get('macd_histogram', 0))
                            }
                        )
                        saved_count += 1
                    
                    # Bollinger Bands
                    if pd.notna(row.get('bb_upper')):
                        self.save_indicator_value(
                            candle,
                            'BB_UPPER',
                            float(row['bb_upper']),
                            metadata={
                                'middle': float(row.get('bb_middle', 0)),
                                'lower': float(row.get('bb_lower', 0)),
                                'width': float(row.get('bb_width', 0))
                            }
                        )
                        saved_count += 1
                    
                    # VWAP
                    if pd.notna(row.get('vwap')):
                        self.save_indicator_value(candle, 'VWAP', float(row['vwap']))
                        saved_count += 1
                    
                    # ATR
                    if pd.notna(row.get('atr')):
                        self.save_indicator_value(candle, 'ATR', float(row['atr']))
                        saved_count += 1
                    
                    # Z-Score
                    if pd.notna(row.get('zscore')):
                        self.save_indicator_value(
                            candle,
                            'ZSCORE',
                            float(row['zscore']),
                            metadata={'sma': float(row.get('zscore_sma', 0))}
                        )
                        saved_count += 1
            
            logger.info(f"Indicadores calculados para {symbol} {interval}: {saved_count} valores salvos")
            return saved_count
            
        except Exception as e:
            logger.error(f"Erro ao calcular indicadores: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return 0
    
    def compute_support_resistance(
        self,
        symbol: str = 'BTCUSDT',
        interval: str = '1h',
        limit: int = 500
    ) -> int:
        """
        Calcula e salva níveis de suporte e resistência
        """
        try:
            candles = Candle.objects.filter(
                symbol=symbol,
                interval=interval
            ).order_by('open_time')[:limit]
            
            if not candles.exists():
                return 0
            
            df = self.candles_to_dataframe(list(candles))
            
            if df.empty or len(df) < 50:
                return 0
            
            # Identificar suporte e resistência
            df, levels = self.calculator.identify_support_resistance(df)
            
            # Salvar no banco
            saved_count = 0
            with transaction.atomic():
                # Limpar níveis antigos
                SupportResistanceLevel.objects.filter(
                    symbol=symbol,
                    interval=interval
                ).delete()
                
                for level in levels:
                    level_type = 'support' if level['price'] < df['close_price'].iloc[-1] else 'resistance'
                    
                    SupportResistanceLevel.objects.create(
                        symbol=symbol,
                        interval=interval,
                        level_type=level_type,
                        price=level['price'],
                        strength=level['strength'],
                        detected_at=timezone.now()
                    )
                    saved_count += 1
            
            logger.info(f"Suporte/Resistência calculados: {saved_count} níveis")
            return saved_count
            
        except Exception as e:
            logger.error(f"Erro ao calcular suporte/resistência: {e}")
            return 0
    
    def compute_fibonacci_levels(
        self,
        symbol: str = 'BTCUSDT',
        interval: str = '1h',
        limit: int = 500
    ) -> int:
        """
        Calcula e salva níveis de Fibonacci
        """
        try:
            candles = Candle.objects.filter(
                symbol=symbol,
                interval=interval
            ).order_by('open_time')[:limit]
            
            if not candles.exists():
                return 0
            
            df = self.candles_to_dataframe(list(candles))
            
            if df.empty or len(df) < 50:
                return 0
            
            # Identificar swing points
            df = self.calculator.identify_swing_points(df)
            
            swing_highs = df[df['swing_high']]['high_price'].tolist()
            swing_lows = df[df['swing_low']]['low_price'].tolist()
            
            if not swing_highs or not swing_lows:
                return 0
            
            # Usar o swing mais recente
            swing_high = max(swing_highs[-10:]) if len(swing_highs) >= 10 else max(swing_highs)
            swing_low = min(swing_lows[-10:]) if len(swing_lows) >= 10 else min(swing_lows)
            
            # Calcular níveis Fibonacci
            fib_levels = self.calculator.calculate_fibonacci_levels(df, swing_high, swing_low)
            
            # Salvar no banco
            saved_count = 0
            with transaction.atomic():
                # Limpar níveis antigos
                FibonacciLevel.objects.filter(
                    symbol=symbol,
                    interval=interval
                ).delete()
                
                for level_pct, price in fib_levels.items():
                    FibonacciLevel.objects.create(
                        symbol=symbol,
                        interval=interval,
                        level_percentage=float(level_pct),
                        price=price,
                        swing_high=swing_high,
                        swing_low=swing_low,
                        detected_at=timezone.now()
                    )
                    saved_count += 1
            
            logger.info(f"Fibonacci calculado: {saved_count} níveis")
            return saved_count
            
        except Exception as e:
            logger.error(f"Erro ao calcular Fibonacci: {e}")
            return 0
    
    def compute_all_indicators(self, symbol: str = 'BTCUSDT', intervals: list = None) -> dict:
        """
        Calcula todos os indicadores para todos os intervalos
        """
        if intervals is None:
            intervals = ['1h', '4h', '1d']
        
        results = {}
        
        for interval in intervals:
            # Indicadores básicos
            count = self.compute_indicators_for_interval(symbol=symbol, interval=interval)
            results[f'{interval}_indicators'] = count
            
            # Suporte e Resistência
            sr_count = self.compute_support_resistance(symbol=symbol, interval=interval)
            results[f'{interval}_support_resistance'] = sr_count
            
            # Fibonacci
            fib_count = self.compute_fibonacci_levels(symbol=symbol, interval=interval)
            results[f'{interval}_fibonacci'] = fib_count
        
        return results
