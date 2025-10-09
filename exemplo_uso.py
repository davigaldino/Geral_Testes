#!/usr/bin/env python3
"""
Exemplo de Uso do Sistema de Relatórios de Validação e Qualidade de Dados
Autor: Assistente AI
Data: 2024

Este arquivo demonstra como usar o sistema para diferentes cenários:
1. Validação de dados de um DataFrame
2. Validação de dados de um arquivo CSV
3. Geração de relatórios específicos
4. Análise customizada
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Importar o sistema
from data_quality_reporter import DataQualityReporter
from data_validator import DataValidator
from excel_report_generator import ExcelReportGenerator
from pdf_report_generator import PDFReportGenerator
from data_visualizer import DataVisualizer

def exemplo_1_dataframe_simples():
    """
    Exemplo 1: Validação de um DataFrame simples
    """
    print("=" * 60)
    print("📊 EXEMPLO 1: Validação de DataFrame Simples")
    print("=" * 60)
    
    # Criar DataFrame com alguns problemas intencionais
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
    
    # Adicionar alguns problemas intencionais
    df.loc[2, 'Email'] = None  # Valor nulo
    df.loc[5, 'Idade'] = -5    # Idade negativa
    df.loc[8, 'Salario'] = 50000  # Outlier
    
    # Usar o sistema
    reporter = DataQualityReporter(df, "Funcionários - Exemplo 1")
    results = reporter.run_complete_analysis()
    
    return results

def exemplo_2_arquivo_csv():
    """
    Exemplo 2: Validação de arquivo CSV
    """
    print("\n" + "=" * 60)
    print("📊 EXEMPLO 2: Validação de Arquivo CSV")
    print("=" * 60)
    
    # Criar arquivo CSV de exemplo
    csv_data = {
        'Produto_ID': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        'Nome_Produto': ['Laptop', 'Mouse', 'Teclado', 'Monitor', 'Cabo USB', 'Fone', 
                        'Webcam', 'Impressora', 'Scanner', 'Tablet', 'Laptop', 'Mouse'],
        'Preco': [2500.00, 50.00, 120.00, 800.00, 15.00, 200.00, 
                 300.00, 400.00, 150.00, 1200.00, 2500.00, 50.00],
        'Categoria': ['Eletrônicos', 'Acessórios', 'Acessórios', 'Eletrônicos', 'Acessórios',
                     'Acessórios', 'Acessórios', 'Eletrônicos', 'Eletrônicos', 'Eletrônicos',
                     'Eletrônicos', 'Acessórios'],
        'Estoque': [10, 50, 30, 15, 100, 25, 20, 8, 12, 5, 10, 50],
        'Data_Cadastro': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19',
                         '2024-01-20', '2024-01-21', '2024-01-22', '2024-01-23', '2024-01-24',
                         '2024-01-15', '2024-01-16'],
        'Ativo': [True, True, True, True, True, True, True, True, True, True, True, True]
    }
    
    df_csv = pd.DataFrame(csv_data)
    
    # Adicionar problemas
    df_csv.loc[3, 'Preco'] = None  # Preço nulo
    df_csv.loc[6, 'Estoque'] = -10  # Estoque negativo
    df_csv.loc[9, 'Data_Cadastro'] = 'data_invalida'  # Data inválida
    
    # Salvar CSV
    csv_file = '/workspace/produtos_exemplo.csv'
    df_csv.to_csv(csv_file, index=False)
    
    # Validar arquivo
    reporter = DataQualityReporter(csv_file, "Produtos - Exemplo 2")
    results = reporter.run_complete_analysis()
    
    return results

def exemplo_3_validacao_personalizada():
    """
    Exemplo 3: Validação personalizada com análise específica
    """
    print("\n" + "=" * 60)
    print("📊 EXEMPLO 3: Validação Personalizada")
    print("=" * 60)
    
    # Criar dados de vendas com problemas específicos
    np.random.seed(42)
    n_records = 100
    
    vendas_data = {
        'Venda_ID': range(1, n_records + 1),
        'Cliente_ID': np.random.randint(1, 51, n_records),
        'Produto': np.random.choice(['Laptop', 'Mouse', 'Teclado', 'Monitor', 'Fone'], n_records),
        'Quantidade': np.random.randint(1, 10, n_records),
        'Preco_Unitario': np.random.uniform(10, 1000, n_records).round(2),
        'Data_Venda': [(datetime.now() - timedelta(days=np.random.randint(0, 365))).strftime('%Y-%m-%d') 
                      for _ in range(n_records)],
        'Vendedor': np.random.choice(['João', 'Maria', 'Pedro', 'Ana', 'Carlos'], n_records),
        'Regiao': np.random.choice(['Norte', 'Sul', 'Leste', 'Oeste', 'Centro'], n_records)
    }
    
    df_vendas = pd.DataFrame(vendas_data)
    
    # Adicionar problemas específicos
    # Valores nulos
    df_vendas.loc[10:15, 'Cliente_ID'] = None
    df_vendas.loc[20:25, 'Preco_Unitario'] = None
    
    # Valores negativos
    df_vendas.loc[30:35, 'Quantidade'] = -1
    
    # Outliers
    df_vendas.loc[40:45, 'Preco_Unitario'] = 10000
    
    # Duplicatas
    df_vendas.loc[50:55] = df_vendas.loc[10:15].values
    
    # Validação personalizada
    print("🔍 Executando validação personalizada...")
    validator = DataValidator(df_vendas, "Vendas - Exemplo 3")
    
    # Análise específica
    print("\n📊 Análise de Duplicatas:")
    duplicates = validator.get_issues_by_category('Registros Duplicados')
    for dup in duplicates:
        print(f"   • {dup['descricao']}")
    
    print("\n📊 Análise de Valores Faltantes:")
    missing = validator.get_issues_by_category('Valores Nulos')
    for miss in missing:
        print(f"   • {miss['descricao']}")
    
    print("\n📊 Análise de Outliers:")
    outliers = validator.get_issues_by_category('Valores Extremos')
    for out in outliers:
        print(f"   • {out['descricao']}")
    
    # Gerar apenas relatório Excel
    print("\n📊 Gerando relatório Excel personalizado...")
    excel_gen = ExcelReportGenerator(validator.get_summary())
    excel_gen.generate_report()
    
    return validator.get_summary()

def exemplo_4_analise_por_severidade():
    """
    Exemplo 4: Análise focada em problemas por severidade
    """
    print("\n" + "=" * 60)
    print("📊 EXEMPLO 4: Análise por Severidade")
    print("=" * 60)
    
    # Criar dados com problemas de diferentes severidades
    data_critica = {
        'ID': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'Nome': ['João', 'Maria', 'Pedro', 'Ana', 'Carlos', 'Lucia', 'Roberto', 'Fernanda', 'Miguel', 'Isabela'],
        'CPF': ['12345678901', '98765432100', '11111111111', '22222222222', '33333333333',
               '44444444444', '55555555555', '66666666666', '77777777777', '88888888888'],
        'Email': ['joao@email.com', 'maria@email.com', 'pedro@email.com', 'ana@email.com', 
                 'carlos@email.com', 'lucia@email.com', 'roberto@email.com', 'fernanda@email.com',
                 'miguel@email.com', 'isabela@email.com'],
        'Telefone': ['11999999999', '11888888888', '11777777777', '11666666666', '11555555555',
                    '11444444444', '11333333333', '11222222222', '11111111111', '11000000000'],
        'Salario': [5000, 6000, 7000, 5500, 8000, 6500, 5800, 6200, 5200, 5900]
    }
    
    df_critica = pd.DataFrame(data_critica)
    
    # Adicionar problemas críticos
    df_critica.loc[2, 'Nome'] = None  # Nome nulo - CRÍTICO
    df_critica.loc[5, 'CPF'] = None   # CPF nulo - CRÍTICO
    df_critica.loc[8, 'Email'] = None # Email nulo - CRÍTICO
    
    # Adicionar problemas de alta severidade
    df_critica.loc[3, 'CPF'] = '123'  # CPF inválido - ALTO
    df_critica.loc[6, 'Email'] = 'email_invalido'  # Email inválido - ALTO
    
    # Adicionar problemas de média severidade
    df_critica.loc[1, 'Telefone'] = '123'  # Telefone inválido - MÉDIO
    df_critica.loc[4, 'Salario'] = -1000   # Salário negativo - MÉDIO
    
    # Adicionar problemas de baixa severidade
    df_critica.loc[7, 'Salario'] = 50000   # Outlier - BAIXO
    
    # Validar
    validator = DataValidator(df_critica, "Dados Críticos - Exemplo 4")
    
    # Análise por severidade
    print("🚨 PROBLEMAS CRÍTICOS:")
    critical = validator.get_issues_by_severity('Crítico')
    for issue in critical:
        print(f"   • {issue['descricao']}")
    
    print("\n⚠️ PROBLEMAS DE ALTA SEVERIDADE:")
    high = validator.get_issues_by_severity('Alto')
    for issue in high:
        print(f"   • {issue['descricao']}")
    
    print("\n🔶 PROBLEMAS DE MÉDIA SEVERIDADE:")
    medium = validator.get_issues_by_severity('Médio')
    for issue in medium:
        print(f"   • {issue['descricao']}")
    
    print("\nℹ️ PROBLEMAS DE BAIXA SEVERIDADE:")
    low = validator.get_issues_by_severity('Baixo')
    for issue in low:
        print(f"   • {issue['descricao']}")
    
    # Gerar relatório PDF focado em severidade
    print("\n📄 Gerando relatório PDF focado em severidade...")
    pdf_gen = PDFReportGenerator(validator.get_summary())
    pdf_gen.generate_report()
    
    return validator.get_summary()

def exemplo_5_visualizacoes_personalizadas():
    """
    Exemplo 5: Criação de visualizações personalizadas
    """
    print("\n" + "=" * 60)
    print("📊 EXEMPLO 5: Visualizações Personalizadas")
    print("=" * 60)
    
    # Criar dados para visualização
    data_viz = {
        'Mes': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
        'Vendas': [100, 120, 90, 110, 130, 140, 160, 150, 170, 180, 200, 220],
        'Problemas_Qualidade': [5, 3, 8, 4, 2, 1, 0, 2, 1, 0, 1, 0],
        'Satisfacao_Cliente': [8.5, 8.8, 8.2, 8.9, 9.1, 9.3, 9.5, 9.4, 9.6, 9.7, 9.8, 9.9]
    }
    
    df_viz = pd.DataFrame(data_viz)
    
    # Adicionar alguns problemas
    df_viz.loc[2, 'Vendas'] = None  # Venda nula
    df_viz.loc[5, 'Satisfacao_Cliente'] = -1  # Satisfação negativa
    
    # Validar
    validator = DataValidator(df_viz, "Dados de Visualização - Exemplo 5")
    
    # Criar visualizações personalizadas
    print("📈 Criando visualizações personalizadas...")
    visualizer = DataVisualizer(validator.get_summary())
    chart_files = visualizer.create_all_visualizations('/workspace/reports')
    
    print(f"✅ {len(chart_files)} visualizações criadas:")
    for chart in chart_files:
        print(f"   • {os.path.basename(chart)}")
    
    return validator.get_summary()

def main():
    """
    Executa todos os exemplos
    """
    print("🚀 SISTEMA DE RELATÓRIOS DE VALIDAÇÃO E QUALIDADE DE DADOS")
    print("📊 Exemplos de Uso")
    print("=" * 60)
    
    try:
        # Executar exemplos
        exemplo_1_dataframe_simples()
        exemplo_2_arquivo_csv()
        exemplo_3_validacao_personalizada()
        exemplo_4_analise_por_severidade()
        exemplo_5_visualizacoes_personalizadas()
        
        print("\n" + "=" * 60)
        print("🎉 TODOS OS EXEMPLOS EXECUTADOS COM SUCESSO!")
        print("📁 Verifique a pasta /workspace/reports/ para ver os relatórios gerados.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Erro durante a execução dos exemplos: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()