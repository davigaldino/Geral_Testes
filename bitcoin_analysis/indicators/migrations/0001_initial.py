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
            name='FibonacciLevel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(default='BTCUSDT', max_length=20)),
                ('interval', models.CharField(max_length=5)),
                ('level_percentage', models.DecimalField(decimal_places=2, max_digits=5)),
                ('price', models.DecimalField(decimal_places=8, max_digits=20, validators=[django.core.validators.MinValueValidator(0)])),
                ('swing_high', models.DecimalField(decimal_places=8, max_digits=20)),
                ('swing_low', models.DecimalField(decimal_places=8, max_digits=20)),
                ('detected_at', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'fibonacci_levels',
                'ordering': ['-detected_at'],
            },
        ),
        migrations.CreateModel(
            name='IndicatorValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('indicator_name', models.CharField(db_index=True, max_length=50)),
                ('value', models.DecimalField(decimal_places=10, max_digits=30)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('candle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='indicators', to='binance_client.candle')),
            ],
            options={
                'db_table': 'indicator_values',
                'ordering': ['-candle__open_time'],
            },
        ),
        migrations.CreateModel(
            name='SupportResistanceLevel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(default='BTCUSDT', max_length=20)),
                ('interval', models.CharField(max_length=5)),
                ('level_type', models.CharField(choices=[('support', 'Suporte'), ('resistance', 'Resistência')], max_length=10)),
                ('price', models.DecimalField(decimal_places=8, max_digits=20, validators=[django.core.validators.MinValueValidator(0)])),
                ('strength', models.DecimalField(decimal_places=2, max_digits=5)),
                ('detected_at', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'support_resistance_levels',
                'ordering': ['-detected_at'],
            },
        ),
        migrations.AddIndex(
            model_name='indicatorvalue',
            index=models.Index(fields=['candle', 'indicator_name'], name='indicator_v_candle__idx'),
        ),
        migrations.AddIndex(
            model_name='indicatorvalue',
            index=models.Index(fields=['indicator_name', 'created_at'], name='indicator_v_indicator_idx'),
        ),
        migrations.AddIndex(
            model_name='supportresistancelevel',
            index=models.Index(fields=['symbol', 'interval', 'detected_at'], name='support_res_symbol_interval_idx'),
        ),
        migrations.AddIndex(
            model_name='fibonaccilevel',
            index=models.Index(fields=['symbol', 'interval', 'detected_at'], name='fibonacci_l_symbol_interval_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='indicatorvalue',
            unique_together={('candle', 'indicator_name')},
        ),
    ]
