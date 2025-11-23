"""
Models para armazenar sinais de compra/venda
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from binance_client.models import Candle


class TradingSignal(models.Model):
    """
    Armazena sinais de compra/venda gerados
    """
    SIGNAL_TYPE_CHOICES = [
        ('BUY', 'Compra'),
        ('SELL', 'Venda'),
        ('HOLD', 'Manter'),
    ]
    
    candle = models.ForeignKey(Candle, on_delete=models.CASCADE, related_name='signals')
    signal_type = models.CharField(max_length=4, choices=SIGNAL_TYPE_CHOICES)
    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Pontuação de confiança (0-100)"
    )
    reasons = models.JSONField(default=list, help_text="Lista de razões para o sinal")
    indicators_used = models.JSONField(default=list, help_text="Indicadores utilizados")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'trading_signals'
        indexes = [
            models.Index(fields=['candle', 'signal_type', 'created_at']),
            models.Index(fields=['signal_type', 'confidence_score']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.signal_type} @ {self.candle.open_time} (Confiança: {self.confidence_score}%)"
