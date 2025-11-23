#!/usr/bin/env python
"""
Script para verificar se o sistema está configurado corretamente
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bitcoin_platform.settings')
django.setup()

from django.conf import settings
from django.db import connection
import redis


def check_database():
    """Verifica conexão com banco de dados"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✓ Conexão com PostgreSQL: OK")
        return True
    except Exception as e:
        print(f"✗ Erro na conexão com PostgreSQL: {e}")
        return False


def check_redis():
    """Verifica conexão com Redis"""
    try:
        r = redis.from_url(settings.CELERY_BROKER_URL)
        r.ping()
        print("✓ Conexão com Redis: OK")
        return True
    except Exception as e:
        print(f"✗ Erro na conexão com Redis: {e}")
        return False


def check_binance_api():
    """Verifica configuração da API Binance"""
    if settings.API_READ_ONLY_MODE:
        print("⚠ Modo somente leitura ativado (sem API keys necessárias)")
        return True
    
    if not settings.BINANCE_API_KEY or not settings.BINANCE_API_SECRET:
        print("⚠ API keys da Binance não configuradas (modo somente leitura)")
        return True
    
    print("✓ API keys da Binance configuradas")
    return True


def check_models():
    """Verifica se os modelos estão criados"""
    try:
        from binance_client.models import Candle, CurrentPrice
        from indicators.models import IndicatorValue
        from signals.models import TradingSignal
        
        print("✓ Modelos do banco de dados: OK")
        return True
    except Exception as e:
        print(f"✗ Erro ao importar modelos: {e}")
        return False


def main():
    print("=" * 60)
    print("Verificação do Sistema")
    print("=" * 60)
    print()
    
    results = []
    results.append(("Banco de Dados", check_database()))
    results.append(("Redis", check_redis()))
    results.append(("API Binance", check_binance_api()))
    results.append(("Modelos", check_models()))
    
    print()
    print("=" * 60)
    
    if all(r[1] for r in results):
        print("✓ Sistema configurado corretamente!")
    else:
        print("✗ Alguns problemas foram encontrados. Verifique acima.")
    
    print("=" * 60)


if __name__ == '__main__':
    main()
