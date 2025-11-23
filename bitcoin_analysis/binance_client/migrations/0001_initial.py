# Generated manually
from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Candle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(default='BTCUSDT', max_length=20)),
                ('interval', models.CharField(choices=[('1m', '1 Minuto'), ('5m', '5 Minutos'), ('15m', '15 Minutos'), ('1h', '1 Hora'), ('4h', '4 Horas'), ('1d', '1 Dia')], max_length=5)),
                ('open_time', models.DateTimeField(db_index=True)),
                ('close_time', models.DateTimeField()),
                ('open_price', models.DecimalField(decimal_places=8, max_digits=20, validators=[django.core.validators.MinValueValidator(0)])),
                ('high_price', models.DecimalField(decimal_places=8, max_digits=20, validators=[django.core.validators.MinValueValidator(0)])),
                ('low_price', models.DecimalField(decimal_places=8, max_digits=20, validators=[django.core.validators.MinValueValidator(0)])),
                ('close_price', models.DecimalField(decimal_places=8, max_digits=20, validators=[django.core.validators.MinValueValidator(0)])),
                ('volume', models.DecimalField(decimal_places=8, max_digits=30, validators=[django.core.validators.MinValueValidator(0)])),
                ('quote_volume', models.DecimalField(decimal_places=8, max_digits=30, validators=[django.core.validators.MinValueValidator(0)])),
                ('trades_count', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'candles',
                'ordering': ['-open_time'],
            },
        ),
        migrations.CreateModel(
            name='CurrentPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(default='BTCUSDT', max_length=20, unique=True)),
                ('price', models.DecimalField(decimal_places=8, max_digits=20, validators=[django.core.validators.MinValueValidator(0)])),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'current_prices',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.AddIndex(
            model_name='candle',
            index=models.Index(fields=['symbol', 'interval', 'open_time'], name='candles_symbol_interval_idx'),
        ),
        migrations.AddIndex(
            model_name='candle',
            index=models.Index(fields=['open_time'], name='candles_open_time_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='candle',
            unique_together={('symbol', 'interval', 'open_time')},
        ),
    ]
