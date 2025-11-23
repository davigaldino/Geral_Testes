"""
Geradores de sinais de compra/venda
"""
import logging
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from django.db.models import Q
from binance_client.models import Candle, CurrentPrice
from indicators.models import IndicatorValue, SupportResistanceLevel, FibonacciLevel

logger = logging.getLogger(__name__)


class SignalGenerator:
    """
    Classe para gerar sinais de trading baseado em indicadores técnicos
    """
    
    def __init__(self):
        self.buy_signals = []
        self.sell_signals = []
    
    def get_latest_indicator_value(
        self,
        candle: Candle,
        indicator_name: str
    ) -> Optional[Decimal]:
        """
        Obtém o valor mais recente de um indicador para um candle
        """
        try:
            indicator = IndicatorValue.objects.filter(
                candle=candle,
                indicator_name=indicator_name
            ).first()
            
            if indicator:
                return indicator.value
            return None
        except Exception as e:
            logger.error(f"Erro ao obter indicador {indicator_name}: {e}")
            return None
    
    def get_indicator_metadata(
        self,
        candle: Candle,
        indicator_name: str
    ) -> Optional[Dict]:
        """
        Obtém metadata de um indicador (ex: MACD tem signal e histogram)
        """
        try:
            indicator = IndicatorValue.objects.filter(
                candle=candle,
                indicator_name=indicator_name
            ).first()
            
            if indicator and indicator.metadata:
                return indicator.metadata
            return {}
        except Exception as e:
            logger.error(f"Erro ao obter metadata do indicador {indicator_name}: {e}")
            return {}
    
    def check_ema_cross(self, candle: Candle) -> Tuple[Optional[str], float]:
        """
        Verifica cruzamento EMA50 x EMA200 (Golden Cross / Death Cross)
        """
        try:
            ema50 = self.get_latest_indicator_value(candle, 'EMA_50')
            ema200 = self.get_latest_indicator_value(candle, 'EMA_200')
            
            if not ema50 or not ema200:
                return None, 0.0
            
            # Buscar candle anterior para comparar
            prev_candle = Candle.objects.filter(
                symbol=candle.symbol,
                interval=candle.interval,
                open_time__lt=candle.open_time
            ).order_by('-open_time').first()
            
            if not prev_candle:
                return None, 0.0
            
            prev_ema50 = self.get_latest_indicator_value(prev_candle, 'EMA_50')
            prev_ema200 = self.get_latest_indicator_value(prev_candle, 'EMA_200')
            
            if not prev_ema50 or not prev_ema200:
                return None, 0.0
            
            # Golden Cross: EMA50 cruza acima de EMA200
            if prev_ema50 <= prev_ema200 and ema50 > ema200:
                return 'BUY', 25.0  # Confiança média
            
            # Death Cross: EMA50 cruza abaixo de EMA200
            if prev_ema50 >= prev_ema200 and ema50 < ema200:
                return 'SELL', 25.0
            
            return None, 0.0
            
        except Exception as e:
            logger.error(f"Erro ao verificar cruzamento EMA: {e}")
            return None, 0.0
    
    def check_rsi_signals(self, candle: Candle) -> Tuple[Optional[str], float]:
        """
        Verifica sinais baseados em RSI
        RSI < 30 = potencial compra
        RSI > 70 = potencial venda
        """
        try:
            rsi = self.get_latest_indicator_value(candle, 'RSI')
            
            if not rsi:
                return None, 0.0
            
            rsi_value = float(rsi)
            
            if rsi_value < 30:
                # RSI muito baixo - possível compra
                confidence = 30.0 - rsi_value  # Quanto menor o RSI, maior a confiança
                return 'BUY', min(confidence, 30.0)
            
            if rsi_value > 70:
                # RSI muito alto - possível venda
                confidence = rsi_value - 70.0
                return 'SELL', min(confidence, 30.0)
            
            return None, 0.0
            
        except Exception as e:
            logger.error(f"Erro ao verificar RSI: {e}")
            return None, 0.0
    
    def check_bollinger_bands(self, candle: Candle) -> Tuple[Optional[str], float]:
        """
        Verifica sinais baseados em Bollinger Bands
        Preço tocando banda inferior → possível compra
        """
        try:
            # Buscar metadata para obter lower e upper
            bb_metadata = self.get_indicator_metadata(candle, 'BB_UPPER')
            
            if not bb_metadata:
                return None, 0.0
            
            bb_lower_value = bb_metadata.get('lower')
            bb_upper_value = bb_metadata.get('middle')  # Usar middle como referência
            current_price = float(candle.close_price)
            
            if bb_lower_value:
                # Preço próximo ou abaixo da banda inferior
                distance = (current_price - bb_lower_value) / bb_lower_value
                if distance <= 0.01:  # Dentro de 1% da banda inferior
                    confidence = abs(distance) * 100 * 2  # Ajustar confiança
                    return 'BUY', min(confidence, 20.0)
            
            if bb_upper_value:
                # Preço próximo ou acima da banda superior
                bb_upper_actual = self.get_latest_indicator_value(candle, 'BB_UPPER')
                if bb_upper_actual:
                    distance = (bb_upper_actual - current_price) / current_price
                    if distance <= 0.01:  # Dentro de 1% da banda superior
                        confidence = abs(distance) * 100 * 2
                        return 'SELL', min(confidence, 20.0)
            
            return None, 0.0
            
        except Exception as e:
            logger.error(f"Erro ao verificar Bollinger Bands: {e}")
            return None, 0.0
    
    def check_zscore_signals(self, candle: Candle) -> Tuple[Optional[str], float]:
        """
        Verifica sinais baseados em Z-Score
        Z-Score < -2 → compra
        Z-Score > +2 → venda
        """
        try:
            zscore = self.get_latest_indicator_value(candle, 'ZSCORE')
            
            if not zscore:
                return None, 0.0
            
            zscore_value = float(zscore)
            
            if zscore_value < -2:
                # Muito abaixo da média - possível compra
                confidence = abs(zscore_value - (-2)) * 10
                return 'BUY', min(confidence, 25.0)
            
            if zscore_value > 2:
                # Muito acima da média - possível venda
                confidence = abs(zscore_value - 2) * 10
                return 'SELL', min(confidence, 25.0)
            
            return None, 0.0
            
        except Exception as e:
            logger.error(f"Erro ao verificar Z-Score: {e}")
            return None, 0.0
    
    def check_fibonacci_levels(self, candle: Candle) -> Tuple[Optional[str], float]:
        """
        Verifica se o preço está próximo de níveis de Fibonacci
        """
        try:
            fib_levels = FibonacciLevel.objects.filter(
                symbol=candle.symbol,
                interval=candle.interval
            ).order_by('-detected_at')[:10]
            
            if not fib_levels.exists():
                return None, 0.0
            
            current_price = float(candle.close_price)
            tolerance = current_price * 0.01  # 1% de tolerância
            
            for fib_level in fib_levels:
                distance = abs(current_price - float(fib_level.price))
                
                if distance <= tolerance:
                    # Preço próximo a nível Fibonacci
                    # Se abaixo do preço atual, pode ser suporte (compra)
                    # Se acima, pode ser resistência (venda)
                    if fib_level.price < current_price:
                        confidence = (1 - distance / tolerance) * 10
                        return 'BUY', min(confidence, 15.0)
                    else:
                        confidence = (1 - distance / tolerance) * 10
                        return 'SELL', min(confidence, 15.0)
            
            return None, 0.0
            
        except Exception as e:
            logger.error(f"Erro ao verificar Fibonacci: {e}")
            return None, 0.0
    
    def generate_signal(self, candle: Candle) -> Dict:
        """
        Gera sinal completo para um candle baseado em todos os indicadores
        """
        try:
            signals = []
            total_confidence = 0.0
            reasons = []
            indicators_used = []
            
            # 1. Cruzamento EMA
            signal_type, confidence = self.check_ema_cross(candle)
            if signal_type:
                signals.append((signal_type, confidence))
                reasons.append(f"Cruzamento EMA50/EMA200: {signal_type}")
                indicators_used.append('EMA_50')
                indicators_used.append('EMA_200')
            
            # 2. RSI
            signal_type, confidence = self.check_rsi_signals(candle)
            if signal_type:
                signals.append((signal_type, confidence))
                rsi = self.get_latest_indicator_value(candle, 'RSI')
                reasons.append(f"RSI em {rsi:.2f}: {signal_type}")
                indicators_used.append('RSI')
            
            # 3. Bollinger Bands
            signal_type, confidence = self.check_bollinger_bands(candle)
            if signal_type:
                signals.append((signal_type, confidence))
                reasons.append(f"Preço próximo à banda de Bollinger: {signal_type}")
                indicators_used.append('BB_UPPER')
            
            # 4. Z-Score
            signal_type, confidence = self.check_zscore_signals(candle)
            if signal_type:
                signals.append((signal_type, confidence))
                zscore = self.get_latest_indicator_value(candle, 'ZSCORE')
                reasons.append(f"Z-Score em {zscore:.2f}: {signal_type}")
                indicators_used.append('ZSCORE')
            
            # 5. Fibonacci
            signal_type, confidence = self.check_fibonacci_levels(candle)
            if signal_type:
                signals.append((signal_type, confidence))
                reasons.append(f"Preço próximo a nível Fibonacci: {signal_type}")
                indicators_used.append('FIBONACCI')
            
            # Agregar sinais
            buy_confidence = sum([c for s, c in signals if s == 'BUY'])
            sell_confidence = sum([c for s, c in signals if s == 'SELL'])
            
            # Determinar sinal final
            if buy_confidence > sell_confidence and buy_confidence > 20:
                final_signal = 'BUY'
                final_confidence = min(buy_confidence, 100)
            elif sell_confidence > buy_confidence and sell_confidence > 20:
                final_signal = 'SELL'
                final_confidence = min(sell_confidence, 100)
            else:
                final_signal = 'HOLD'
                final_confidence = max(buy_confidence, sell_confidence)
            
            return {
                'signal_type': final_signal,
                'confidence_score': final_confidence,
                'reasons': reasons,
                'indicators_used': list(set(indicators_used))
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar sinal: {e}")
            return {
                'signal_type': 'HOLD',
                'confidence_score': 0.0,
                'reasons': [],
                'indicators_used': []
            }
