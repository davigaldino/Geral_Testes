"""
Views do Dashboard
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils import timezone
import pandas as pd
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import json

from binance_client.models import Candle, CurrentPrice
from indicators.models import IndicatorValue, SupportResistanceLevel, FibonacciLevel
from signals.models import TradingSignal


def home(request):
    """
    Página inicial com preço atual do BTC
    """
    current_price = CurrentPrice.objects.filter(symbol='BTCUSDT').first()
    
    # Últimos sinais
    recent_signals = TradingSignal.objects.select_related('candle').order_by('-created_at')[:5]
    
    context = {
        'current_price': current_price,
        'recent_signals': recent_signals,
    }
    
    return render(request, 'dashboard/home.html', context)


def chart_view(request, interval='1h'):
    """
    Visualização de gráfico histórico
    """
    intervals = ['15m', '1h', '4h', '1d']
    
    if interval not in intervals:
        interval = '1h'
    
    # Buscar candles
    candles = Candle.objects.filter(
        symbol='BTCUSDT',
        interval=interval
    ).order_by('open_time')[:500]
    
    # Buscar indicadores
    indicators_data = {}
    for candle in candles:
        indicators = IndicatorValue.objects.filter(candle=candle)
        indicators_data[candle.id] = {ind.indicator_name: ind.value for ind in indicators}
    
    # Buscar suporte/resistência
    support_resistance = SupportResistanceLevel.objects.filter(
        symbol='BTCUSDT',
        interval=interval
    ).order_by('-detected_at')[:20]
    
    # Buscar Fibonacci
    fibonacci_levels = FibonacciLevel.objects.filter(
        symbol='BTCUSDT',
        interval=interval
    ).order_by('-detected_at')
    
    context = {
        'interval': interval,
        'intervals': intervals,
        'candles': candles,
        'indicators_data': indicators_data,
        'support_resistance': support_resistance,
        'fibonacci_levels': fibonacci_levels,
    }
    
    return render(request, 'dashboard/chart.html', context)


def indicators_table(request):
    """
    Tabela com todos os indicadores calculados
    """
    interval = request.GET.get('interval', '1h')
    
    # Buscar últimos candles com indicadores
    candles = Candle.objects.filter(
        symbol='BTCUSDT',
        interval=interval
    ).order_by('-open_time')[:100]
    
    # Preparar dados para tabela
    table_data = []
    for candle in candles:
        indicators = IndicatorValue.objects.filter(candle=candle)
        row = {
            'candle': candle,
            'indicators': {ind.indicator_name: ind for ind in indicators}
        }
        table_data.append(row)
    
    context = {
        'interval': interval,
        'table_data': table_data,
    }
    
    return render(request, 'dashboard/indicators_table.html', context)


def signals_panel(request):
    """
    Painel de Sinais com pontuação de confiança
    """
    interval = request.GET.get('interval', '1h')
    
    # Buscar sinais recentes
    signals = TradingSignal.objects.filter(
        candle__symbol='BTCUSDT',
        candle__interval=interval
    ).select_related('candle').order_by('-created_at')[:50]
    
    # Estatísticas
    buy_signals = signals.filter(signal_type='BUY').count()
    sell_signals = signals.filter(signal_type='SELL').count()
    hold_signals = signals.filter(signal_type='HOLD').count()
    
    from django.db.models import Avg
    avg_confidence = signals.aggregate(
        avg_conf=Avg('confidence_score')
    )['avg_conf'] or 0
    
    context = {
        'interval': interval,
        'signals': signals,
        'buy_signals': buy_signals,
        'sell_signals': sell_signals,
        'hold_signals': hold_signals,
        'avg_confidence': avg_confidence,
    }
    
    return render(request, 'dashboard/signals_panel.html', context)


def backtesting(request):
    """
    Página de Backtesting (estrutura criada, implementação adiada)
    """
    context = {
        'message': 'Funcionalidade de backtesting será implementada na próxima etapa.'
    }
    return render(request, 'dashboard/backtesting.html', context)


def settings_page(request):
    """
    Página de configurações
    """
    from django.conf import settings
    
    context = {
        'api_read_only_mode': settings.API_READ_ONLY_MODE,
        'binance_testnet': settings.BINANCE_TESTNET,
    }
    
    return render(request, 'dashboard/settings.html', context)


@require_http_methods(["GET"])
def chart_data_api(request, interval='1h'):
    """
    API endpoint para dados do gráfico (JSON)
    """
    try:
        candles = Candle.objects.filter(
            symbol='BTCUSDT',
            interval=interval
        ).order_by('open_time')[:500]
        
        # Preparar dados para Plotly
        dates = [candle.open_time for candle in candles]
        opens = [float(candle.open_price) for candle in candles]
        highs = [float(candle.high_price) for candle in candles]
        lows = [float(candle.low_price) for candle in candles]
        closes = [float(candle.close_price) for candle in candles]
        volumes = [float(candle.volume) for candle in candles]
        
        # Buscar EMAs
        ema50_values = []
        ema200_values = []
        rsi_values = []
        macd_values = []
        macd_signal_values = []
        bb_upper_values = []
        bb_lower_values = []
        
        for candle in candles:
            ema50 = IndicatorValue.objects.filter(candle=candle, indicator_name='EMA_50').first()
            ema200 = IndicatorValue.objects.filter(candle=candle, indicator_name='EMA_200').first()
            rsi = IndicatorValue.objects.filter(candle=candle, indicator_name='RSI').first()
            macd = IndicatorValue.objects.filter(candle=candle, indicator_name='MACD').first()
            bb = IndicatorValue.objects.filter(candle=candle, indicator_name='BB_UPPER').first()
            
            ema50_values.append(float(ema50.value) if ema50 else None)
            ema200_values.append(float(ema200.value) if ema200 else None)
            rsi_values.append(float(rsi.value) if rsi else None)
            
            if macd:
                macd_values.append(float(macd.value))
                macd_signal_values.append(float(macd.metadata.get('signal', 0)))
            else:
                macd_values.append(None)
                macd_signal_values.append(None)
            
            if bb:
                bb_upper_values.append(float(bb.value))
                bb_lower_values.append(float(bb.metadata.get('lower', 0)))
            else:
                bb_upper_values.append(None)
                bb_lower_values.append(None)
        
        data = {
            'dates': [d.isoformat() for d in dates],
            'opens': opens,
            'highs': highs,
            'lows': lows,
            'closes': closes,
            'volumes': volumes,
            'ema50': ema50_values,
            'ema200': ema200_values,
            'rsi': rsi_values,
            'macd': macd_values,
            'macd_signal': macd_signal_values,
            'bb_upper': bb_upper_values,
            'bb_lower': bb_lower_values,
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
