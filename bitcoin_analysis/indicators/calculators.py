"""
Calculadores de indicadores técnicos
"""
import logging
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from django.utils import timezone

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """
    Classe para calcular indicadores técnicos
    """
    
    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Calcula RSI (Relative Strength Index)
        """
        delta = df['close_price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        df['rsi'] = rsi
        return df
    
    @staticmethod
    def calculate_sma(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """
        Calcula Média Móvel Simples (SMA)
        """
        df[f'sma_{period}'] = df['close_price'].rolling(window=period).mean()
        return df
    
    @staticmethod
    def calculate_ema(df: pd.DataFrame, period: int = 50) -> pd.DataFrame:
        """
        Calcula Média Móvel Exponencial (EMA)
        """
        df[f'ema_{period}'] = df['close_price'].ewm(span=period, adjust=False).mean()
        return df
    
    @staticmethod
    def calculate_macd(
        df: pd.DataFrame,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> pd.DataFrame:
        """
        Calcula MACD (Moving Average Convergence Divergence)
        """
        ema_fast = df['close_price'].ewm(span=fast_period, adjust=False).mean()
        ema_slow = df['close_price'].ewm(span=slow_period, adjust=False).mean()
        
        df['macd'] = ema_fast - ema_slow
        df['macd_signal'] = df['macd'].ewm(span=signal_period, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        return df
    
    @staticmethod
    def calculate_bollinger_bands(
        df: pd.DataFrame,
        period: int = 20,
        std_dev: float = 2.0
    ) -> pd.DataFrame:
        """
        Calcula Bollinger Bands
        """
        sma = df['close_price'].rolling(window=period).mean()
        std = df['close_price'].rolling(window=period).std()
        
        df['bb_upper'] = sma + (std * std_dev)
        df['bb_middle'] = sma
        df['bb_lower'] = sma - (std * std_dev)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        
        return df
    
    @staticmethod
    def calculate_vwap(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula VWAP (Volume Weighted Average Price)
        """
        typical_price = (df['high_price'] + df['low_price'] + df['close_price']) / 3
        df['vwap'] = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
        return df
    
    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Calcula ATR (Average True Range)
        """
        high_low = df['high_price'] - df['low_price']
        high_close = np.abs(df['high_price'] - df['close_price'].shift())
        low_close = np.abs(df['low_price'] - df['close_price'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = true_range.rolling(window=period).mean()
        
        return df
    
    @staticmethod
    def calculate_mean_reversion_zscore(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """
        Calcula Z-Score para Reversão à Média
        Z = (Preço Fechamento – SMA(20)) / desvio padrão
        """
        sma = df['close_price'].rolling(window=period).mean()
        std = df['close_price'].rolling(window=period).std()
        
        df['zscore'] = (df['close_price'] - sma) / std
        df['zscore_sma'] = sma  # Guardar SMA também
        
        return df
    
    @staticmethod
    def identify_swing_points(df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
        """
        Identifica swing highs e swing lows (pivôs locais)
        """
        df['swing_high'] = False
        df['swing_low'] = False
        
        for i in range(window, len(df) - window):
            # Swing High
            if df.iloc[i]['high_price'] == df.iloc[i-window:i+window+1]['high_price'].max():
                df.loc[df.index[i], 'swing_high'] = True
            
            # Swing Low
            if df.iloc[i]['low_price'] == df.iloc[i-window:i+window+1]['low_price'].min():
                df.loc[df.index[i], 'swing_low'] = True
        
        return df
    
    @staticmethod
    def calculate_fibonacci_levels(
        df: pd.DataFrame,
        swing_high: float,
        swing_low: float
    ) -> Dict[str, float]:
        """
        Calcula níveis de Fibonacci baseado em swing high e swing low
        """
        diff = swing_high - swing_low
        
        fib_levels = {
            '0.0': swing_high,
            '23.6': swing_high - (diff * 0.236),
            '38.2': swing_high - (diff * 0.382),
            '50.0': swing_high - (diff * 0.5),
            '61.8': swing_high - (diff * 0.618),
            '78.6': swing_high - (diff * 0.786),
            '100.0': swing_low,
        }
        
        return fib_levels
    
    @staticmethod
    def identify_support_resistance(
        df: pd.DataFrame,
        window: int = 20,
        min_touches: int = 2
    ) -> Tuple[pd.DataFrame, list]:
        """
        Identifica níveis de suporte e resistência baseado em pivôs
        """
        df = TechnicalIndicators.identify_swing_points(df, window=window//2)
        
        swing_highs = df[df['swing_high']]['high_price'].tolist()
        swing_lows = df[df['swing_low']]['low_price'].tolist()
        
        # Agrupar preços próximos
        tolerance = df['close_price'].std() * 0.02  # 2% de tolerância
        
        support_levels = []
        resistance_levels = []
        
        # Processar swing lows (suportes)
        for low in swing_lows:
            nearby = [l for l in swing_lows if abs(l - low) <= tolerance]
            if len(nearby) >= min_touches:
                avg_price = np.mean(nearby)
                strength = len(nearby) * 10  # Score baseado em número de toques
                if avg_price not in [s['price'] for s in support_levels]:
                    support_levels.append({
                        'price': avg_price,
                        'strength': min(strength, 100)
                    })
        
        # Processar swing highs (resistências)
        for high in swing_highs:
            nearby = [h for h in swing_highs if abs(h - high) <= tolerance]
            if len(nearby) >= min_touches:
                avg_price = np.mean(nearby)
                strength = len(nearby) * 10
                if avg_price not in [r['price'] for r in resistance_levels]:
                    resistance_levels.append({
                        'price': avg_price,
                        'strength': min(strength, 100)
                    })
        
        return df, support_levels + resistance_levels
    
    @staticmethod
    def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula todos os indicadores de uma vez
        """
        # Indicadores básicos
        df = TechnicalIndicators.calculate_rsi(df, period=14)
        df = TechnicalIndicators.calculate_sma(df, period=20)
        df = TechnicalIndicators.calculate_ema(df, period=50)
        df = TechnicalIndicators.calculate_ema(df, period=200)
        df = TechnicalIndicators.calculate_macd(df)
        df = TechnicalIndicators.calculate_bollinger_bands(df, period=20)
        df = TechnicalIndicators.calculate_vwap(df)
        df = TechnicalIndicators.calculate_atr(df, period=14)
        df = TechnicalIndicators.calculate_mean_reversion_zscore(df, period=20)
        
        return df
