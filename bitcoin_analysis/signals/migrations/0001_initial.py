# Generated manually
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('binance_client', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TradingSignal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('signal_type', models.CharField(choices=[('BUY', 'Compra'), ('SELL', 'Venda'), ('HOLD', 'Manter')], max_length=4)),
                ('confidence_score', models.DecimalField(decimal_places=2, help_text='Pontuação de confiança (0-100)', max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('reasons', models.JSONField(default=list, help_text='Lista de razões para o sinal')),
                ('indicators_used', models.JSONField(default=list, help_text='Indicadores utilizados')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('candle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='signals', to='binance_client.candle')),
            ],
            options={
                'db_table': 'trading_signals',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='tradingsignal',
            index=models.Index(fields=['candle', 'signal_type', 'created_at'], name='trading_sig_candle__idx'),
        ),
        migrations.AddIndex(
            model_name='tradingsignal',
            index=models.Index(fields=['signal_type', 'confidence_score'], name='trading_sig_signal__idx'),
        ),
    ]
