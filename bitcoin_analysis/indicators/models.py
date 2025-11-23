"""
Models para armazenar indicadores técnicos calculados
"""
from django.db import models
from django.core.validators import MinValueValidator
from binance_client.models import Candle


class IndicatorValue(models.Model):
    """
    Armazena valores calculados de indicadores técnicos
    """
    candle = models.ForeignKey(Candle, on_delete=models.CASCADE, related_name='indicators')
    indicator_name = models.CharField(max_length=50, db_index=True)
    value = models.DecimalField(max_digits=30, decimal_places=10)
    metadata = models.JSONField(default=dict, blank=True)  # Para valores adicionais (ex: MACD tem signal, histogram)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'indicator_values'
        unique_together = [['candle', 'indicator_name']]
        indexes = [
            models.Index(fields=['candle', 'indicator_name']),
            models.Index(fields=['indicator_name', 'created_at']),
        ]
        ordering = ['-candle__open_time']

    def __str__(self):
        return f"{self.indicator_name} @ {self.candle.open_time}: {self.value}"


class SupportResistanceLevel(models.Model):
    """
    Armazena níveis de suporte e resistência identificados
    """
    symbol = models.CharField(max_length=20, default='BTCUSDT')
    interval = models.CharField(max_length=5)
    level_type = models.CharField(max_length=10, choices=[('support', 'Suporte'), ('resistance', 'Resistência')])
    price = models.DecimalField(max_digits=20, decimal_places=8, validators=[MinValueValidator(0)])
    strength = models.DecimalField(max_digits=5, decimal_places=2)  # Score de força (0-100)
    detected_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'support_resistance_levels'
        indexes = [
            models.Index(fields=['symbol', 'interval', 'detected_at']),
        ]
        ordering = ['-detected_at']

    def __str__(self):
        return f"{self.level_type} {self.symbol} @ {self.price} (strength: {self.strength})"


class FibonacciLevel(models.Model):
    """
    Armazena níveis de Fibonacci calculados
    """
    symbol = models.CharField(max_length=20, default='BTCUSDT')
    interval = models.CharField(max_length=5)
    level_percentage = models.DecimalField(max_digits=5, decimal_places=2)  # Ex: 23.6, 38.2, 61.8
    price = models.DecimalField(max_digits=20, decimal_places=8, validators=[MinValueValidator(0)])
    swing_high = models.DecimalField(max_digits=20, decimal_places=8)
    swing_low = models.DecimalField(max_digits=20, decimal_places=8)
    detected_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fibonacci_levels'
        indexes = [
            models.Index(fields=['symbol', 'interval', 'detected_at']),
        ]
        ordering = ['-detected_at']

    def __str__(self):
        return f"Fib {self.level_percentage}% {self.symbol} @ {self.price}"
