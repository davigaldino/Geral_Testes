#!/usr/bin/env python3
"""
Demonstração Rápida do Sistema de Relatórios de Validação e Qualidade de Dados
Autor: Assistente AI
Data: 2024

Este script demonstra rapidamente as principais funcionalidades do sistema.
"""

import pandas as pd
import numpy as np
from data_quality_reporter import DataQualityReporter

def demo_rapido():
    """
    Demonstração rápida das funcionalidades principais
    """
    print("🚀 DEMONSTRAÇÃO RÁPIDA - SISTEMA DE VALIDAÇÃO DE DADOS")
    print("=" * 60)
    
    # 1. Criar dados com problemas intencionais
    print("📊 1. Criando dados de exemplo com problemas...")
    
    data = {
        'ID': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'Nome': ['João', 'Maria', 'Pedro', 'Ana', 'Carlos', 'Lucia', 'Roberto', 'Fernanda', 'Miguel', 'Isabela'],
        'Idade': [25, 30, 35, 28, 42, 33, 29, 31, 27, 26],
        'Email': ['joao@email.com', 'maria@email.com', 'pedro@email.com', 'ana@email.com', 
                 'carlos@email.com', 'lucia@email.com', 'roberto@email.com', 'fernanda@email.com',
                 'miguel@email.com', 'isabela@email.com'],
        'Salario': [5000, 6000, 7000, 5500, 8000, 6500, 5800, 6200, 5200, 5900],
        'Departamento': ['TI', 'RH', 'Vendas', 'TI', 'Financeiro', 'RH', 'Vendas', 'TI', 'Financeiro', 'RH']
    }
    
    df = pd.DataFrame(data)
    
    # Adicionar problemas intencionais
    df.loc[2, 'Email'] = None  # Email nulo
    df.loc[5, 'Idade'] = -5    # Idade negativa
    df.loc[8, 'Salario'] = 50000  # Outlier
    df.loc[1, 'Email'] = 'email_invalido'  # Email inválido
    
    print(f"✅ Dataset criado: {len(df)} registros, {len(df.columns)} colunas")
    print("   Problemas adicionados: Email nulo, Idade negativa, Salário outlier, Email inválido")
    
    # 2. Validação rápida
    print("\n🔍 2. Executando validação rápida...")
    reporter = DataQualityReporter(df, "Demo Rápido - Funcionários")
    results = reporter.run_quick_validation()
    
    # 3. Análise completa
    print("\n📊 3. Executando análise completa...")
    results = reporter.run_complete_analysis()
    
    if results:
        print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print("📁 Relatórios gerados em: /workspace/reports/")
        print("📊 Arquivos criados:")
        print("   • Relatório Excel (.xlsx)")
        print("   • Relatório PDF (.pdf)")
        print("   • Visualizações (.png)")
        print("\n💡 DICAS DE USO:")
        print("   • Use 'python3 data_quality_reporter.py arquivo.csv' para validar arquivos")
        print("   • Use '--quick-validation' para validação rápida")
        print("   • Use '--excel-only' ou '--pdf-only' para relatórios específicos")
        print("   • Consulte exemplo_uso.py para mais exemplos")
    else:
        print("\n❌ Falha na demonstração")

if __name__ == "__main__":
    demo_rapido()