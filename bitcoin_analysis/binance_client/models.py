"""
Models for storing Binance market data
"""
from django.db import models
from django.core.validators import MinValueValidator


class Candle(models.Model):
    """
    Armazena dados de candles (velas) da Binance
    """
    INTERVAL_CHOICES = [
        ('1m', '1 Minuto'),
        ('5m', '5 Minutos'),
        ('15m', '15 Minutos'),
        ('1h', '1 Hora'),
        ('4h', '4 Horas'),
        ('1d', '1 Dia'),
    ]

    symbol = models.CharField(max_length=20, default='BTCUSDT')
    interval = models.CharField(max_length=5, choices=INTERVAL_CHOICES)
    open_time = models.DateTimeField(db_index=True)
    close_time = models.DateTimeField()
    open_price = models.DecimalField(max_digits=20, decimal_places=8, validators=[MinValueValidator(0)])
    high_price = models.DecimalField(max_digits=20, decimal_places=8, validators=[MinValueValidator(0)])
    low_price = models.DecimalField(max_digits=20, decimal_places=8, validators=[MinValueValidator(0)])
    close_price = models.DecimalField(max_digits=20, decimal_places=8, validators=[MinValueValidator(0)])
    volume = models.DecimalField(max_digits=30, decimal_places=8, validators=[MinValueValidator(0)])
    quote_volume = models.DecimalField(max_digits=30, decimal_places=8, validators=[MinValueValidator(0)])
    trades_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'candles'
        unique_together = [['symbol', 'interval', 'open_time']]
        indexes = [
            models.Index(fields=['symbol', 'interval', 'open_time']),
            models.Index(fields=['open_time']),
        ]
        ordering = ['-open_time']

    def __str__(self):
        return f"{self.symbol} {self.interval} {self.open_time}"


class CurrentPrice(models.Model):
    """
    Armazena o preço atual do BTC
    """
    symbol = models.CharField(max_length=20, default='BTCUSDT', unique=True)
    price = models.DecimalField(max_digits=20, decimal_places=8, validators=[MinValueValidator(0)])
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'current_prices'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.symbol}: {self.price} @ {self.updated_at}"
