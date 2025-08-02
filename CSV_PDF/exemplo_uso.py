#!/usr/bin/env python3
"""
Exemplo de uso programático do gerador de relatórios CSV para PDF
"""

from csv_to_pdf_report import CSVToPDFReporter
import pandas as pd
import numpy as np

def criar_dados_exemplo():
    """Cria dados de exemplo para demonstrar o uso"""
    
    # Criar dados de vendas
    np.random.seed(42)  # Para reprodutibilidade
    
    dados = {
        'Produto': ['Laptop', 'Mouse', 'Teclado', 'Monitor', 'Headset'] * 20,
        'Vendedor': ['João', 'Maria', 'Pedro', 'Ana', 'Carlos'] * 20,
        'Quantidade': np.random.randint(1, 50, 100),
        'Preco_Unitario': np.random.uniform(50, 2000, 100),
        'Data_Venda': pd.date_range('2024-01-01', periods=100, freq='D'),
        'Regiao': np.random.choice(['Norte', 'Sul', 'Leste', 'Oeste'], 100),
        'Categoria': np.random.choice(['Eletrônicos', 'Acessórios', 'Periféricos'], 100)
    }
    
    df = pd.DataFrame(dados)
    df['Valor_Total'] = df['Quantidade'] * df['Preco_Unitario']
    
    return df

def exemplo_basico():
    """Exemplo básico de uso"""
    print("=" * 50)
    print("📊 EXEMPLO BÁSICO")
    print("=" * 50)
    
    # Criar dados de exemplo
    df = criar_dados_exemplo()
    df.to_csv('vendas_exemplo.csv', index=False)
    
    # Criar relatório
    reporter = CSVToPDFReporter('vendas_exemplo.csv', 'relatorio_vendas.pdf')
    
    if reporter.load_csv():
        if reporter.generate_pdf_report():
            print("✅ Relatório de vendas gerado com sucesso!")
        else:
            print("❌ Erro ao gerar relatório")
    else:
        print("❌ Erro ao carregar dados")

def exemplo_personalizado():
    """Exemplo com personalização"""
    print("\n" + "=" * 50)
    print("🎨 EXEMPLO PERSONALIZADO")
    print("=" * 50)
    
    # Criar dados financeiros
    dados_financeiros = {
        'Mes': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
        'Receita': [150000, 180000, 220000, 190000, 250000, 280000],
        'Despesas': [120000, 140000, 160000, 150000, 180000, 200000],
        'Lucro': [30000, 40000, 60000, 40000, 70000, 80000],
        'Investimento': [50000, 60000, 80000, 70000, 90000, 100000]
    }
    
    df_financeiro = pd.DataFrame(dados_financeiros)
    df_financeiro.to_csv('dados_financeiros.csv', index=False)
    
    # Gerar relatório com nome personalizado
    reporter = CSVToPDFReporter('dados_financeiros.csv', 'relatorio_financeiro_2024.pdf')
    
    if reporter.load_csv():
        if reporter.generate_pdf_report():
            print("✅ Relatório financeiro gerado com sucesso!")
        else:
            print("❌ Erro ao gerar relatório")
    else:
        print("❌ Erro ao carregar dados")

def exemplo_multiplos_arquivos():
    """Exemplo processando múltiplos arquivos"""
    print("\n" + "=" * 50)
    print("📁 EXEMPLO MÚLTIPLOS ARQUIVOS")
    print("=" * 50)
    
    # Criar diferentes datasets
    datasets = {
        'funcionarios.csv': {
            'Nome': ['Ana', 'João', 'Maria', 'Pedro', 'Lucia'],
            'Idade': [28, 32, 25, 29, 35],
            'Salario': [4500, 5200, 3800, 4100, 5800],
            'Departamento': ['TI', 'RH', 'Vendas', 'Marketing', 'Financeiro']
        },
        'produtos.csv': {
            'Produto': ['Laptop', 'Mouse', 'Teclado', 'Monitor'],
            'Preco': [2500, 50, 150, 800],
            'Estoque': [10, 100, 50, 25],
            'Categoria': ['Eletrônicos', 'Acessórios', 'Acessórios', 'Eletrônicos']
        }
    }
    
    for nome_arquivo, dados in datasets.items():
        df = pd.DataFrame(dados)
        df.to_csv(nome_arquivo, index=False)
        
        # Gerar relatório para cada arquivo
        nome_relatorio = f"relatorio_{nome_arquivo.replace('.csv', '')}.pdf"
        reporter = CSVToPDFReporter(nome_arquivo, nome_relatorio)
        
        if reporter.load_csv():
            if reporter.generate_pdf_report():
                print(f"✅ Relatório gerado: {nome_relatorio}")
            else:
                print(f"❌ Erro ao gerar relatório: {nome_relatorio}")
        else:
            print(f"❌ Erro ao carregar dados: {nome_arquivo}")

def main():
    """Função principal com todos os exemplos"""
    print("🚀 EXEMPLOS DE USO DO GERADOR DE RELATÓRIOS CSV PARA PDF")
    print("=" * 60)
    
    # Executar exemplos
    exemplo_basico()
    exemplo_personalizado()
    exemplo_multiplos_arquivos()
    
    print("\n" + "=" * 60)
    print("🎉 TODOS OS EXEMPLOS CONCLUÍDOS!")
    print("📁 Verifique os arquivos PDF gerados no diretório atual")
    print("=" * 60)

if __name__ == "__main__":
    main()