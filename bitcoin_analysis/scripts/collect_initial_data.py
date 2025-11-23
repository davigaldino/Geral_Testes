#!/usr/bin/env python
"""
Script para coletar dados iniciais da Binance
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bitcoin_platform.settings')
django.setup()

from binance_client.services import BinanceDataService
from indicators.services import IndicatorService
from signals.services import SignalService


def main():
    print("=" * 60)
    print("Coletando dados iniciais da Binance")
    print("=" * 60)
    
    symbol = 'BTCUSDT'
    intervals = ['1h', '4h', '1d']
    
    # 1. Coletar dados da Binance
    print("\n1. Coletando candles da Binance...")
    binance_service = BinanceDataService()
    
    # Atualizar preço atual
    print("   Atualizando preço atual...")
    binance_service.update_current_price(symbol)
    
    # Coletar candles para cada intervalo
    for interval in intervals:
        print(f"   Coletando candles {interval}...")
        count = binance_service.fetch_and_save_candles(symbol, interval, limit=500)
        print(f"   ✓ {count} candles coletados para {interval}")
    
    # 2. Calcular indicadores
    print("\n2. Calculando indicadores técnicos...")
    indicator_service = IndicatorService()
    
    for interval in intervals:
        print(f"   Calculando indicadores para {interval}...")
        results = indicator_service.compute_all_indicators(symbol, intervals=[interval])
        print(f"   ✓ Indicadores calculados para {interval}")
        for key, value in results.items():
            if interval in key:
                print(f"      - {key}: {value} valores")
    
    # 3. Gerar sinais
    print("\n3. Gerando sinais de trading...")
    signal_service = SignalService()
    
    for interval in intervals:
        print(f"   Gerando sinais para {interval}...")
        results = signal_service.generate_all_signals(symbol, intervals=[interval])
        print(f"   ✓ Sinais gerados para {interval}")
        for key, value in results.items():
            if interval in key:
                print(f"      - {key}: {value} sinais")
    
    print("\n" + "=" * 60)
    print("Coleta de dados concluída!")
    print("=" * 60)
    print("\nAcesse http://localhost:8000 para ver o dashboard")


if __name__ == '__main__':
    main()
