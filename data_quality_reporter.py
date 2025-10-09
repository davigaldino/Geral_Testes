#!/usr/bin/env python3
"""
Sistema Principal de Relatórios de Validação e Qualidade de Dados
Autor: Assistente AI
Data: 2024

Este é o script principal que integra todas as funcionalidades:
- Validação de dados
- Geração de relatórios Excel
- Geração de relatórios PDF
- Criação de visualizações
- Análise completa de qualidade

Uso:
    python data_quality_reporter.py <fonte_dados> [nome_dataset]
    
Exemplos:
    python data_quality_reporter.py dados.csv "Vendas 2024"
    python data_quality_reporter.py dados.xlsx "Funcionários"
    python data_quality_reporter.py "caminho/para/arquivo.csv"
"""

import sys
import os
import pandas as pd
from datetime import datetime
import argparse

# Importar módulos do sistema
from data_validator import DataValidator
from excel_report_generator import ExcelReportGenerator
from pdf_report_generator import PDFReportGenerator
from data_visualizer import DataVisualizer

class DataQualityReporter:
    """
    Classe principal que orquestra todo o processo de validação e geração de relatórios
    """
    
    def __init__(self, data_source, dataset_name="Dataset", output_dir="/workspace/reports"):
        """
        Inicializa o sistema de relatórios de qualidade
        
        Args:
            data_source: Fonte dos dados (DataFrame, caminho para arquivo, etc.)
            dataset_name (str): Nome do dataset para identificação
            output_dir (str): Diretório para salvar os relatórios
        """
        self.data_source = data_source
        self.dataset_name = dataset_name
        self.output_dir = output_dir
        self.validator = None
        self.validation_results = None
        
        # Criar diretório de saída se não existir
        os.makedirs(output_dir, exist_ok=True)
    
    def run_complete_analysis(self, generate_excel=True, generate_pdf=True, create_visualizations=True):
        """
        Executa análise completa de qualidade de dados e gera todos os relatórios
        
        Args:
            generate_excel (bool): Se deve gerar relatório Excel
            generate_pdf (bool): Se deve gerar relatório PDF
            create_visualizations (bool): Se deve criar visualizações
            
        Returns:
            dict: Resultados da análise
        """
        print("🚀 Iniciando análise completa de qualidade de dados...")
        print("=" * 60)
        
        # 1. Validar dados
        print("📊 Etapa 1: Validando dados...")
        self.validator = DataValidator(self.data_source, self.dataset_name)
        
        if self.validator.df is None:
            print("❌ Falha ao carregar dados. Análise interrompida.")
            return None
        
        self.validation_results = self.validator.get_summary()
        
        # Imprimir resumo da validação
        self.validator.print_summary()
        print()
        
        # 2. Criar visualizações
        if create_visualizations:
            print("📈 Etapa 2: Criando visualizações...")
            visualizer = DataVisualizer(self.validation_results)
            chart_files = visualizer.create_all_visualizations(self.output_dir)
            print(f"✅ {len(chart_files)} visualizações criadas")
            print()
        
        # 3. Gerar relatório Excel
        if generate_excel:
            print("📊 Etapa 3: Gerando relatório Excel...")
            excel_generator = ExcelReportGenerator(self.validation_results)
            excel_success = excel_generator.generate_report()
            
            if excel_success:
                print(f"✅ Relatório Excel gerado: {excel_generator.output_path}")
            else:
                print("❌ Falha ao gerar relatório Excel")
            print()
        
        # 4. Gerar relatório PDF
        if generate_pdf:
            print("📄 Etapa 4: Gerando relatório PDF...")
            pdf_generator = PDFReportGenerator(self.validation_results)
            pdf_success = pdf_generator.generate_report()
            
            if pdf_success:
                print(f"✅ Relatório PDF gerado: {pdf_generator.output_path}")
            else:
                print("❌ Falha ao gerar relatório PDF")
            print()
        
        # 5. Resumo final
        print("🎉 Análise concluída com sucesso!")
        print("=" * 60)
        print(f"📁 Relatórios salvos em: {self.output_dir}")
        print(f"📊 Dataset: {self.dataset_name}")
        print(f"📈 Registros analisados: {self.validation_results['total_rows']:,}")
        print(f"⚠️  Problemas encontrados: {self.validation_results['total_issues']}")
        print(f"🎯 Pontuação de qualidade: {self.validation_results['quality_score']:.1f}/100")
        
        return {
            'validation_results': self.validation_results,
            'excel_generated': generate_excel and excel_success,
            'pdf_generated': generate_pdf and pdf_success,
            'visualizations_created': create_visualizations,
            'output_directory': self.output_dir
        }
    
    def run_quick_validation(self):
        """
        Executa apenas validação rápida sem gerar relatórios
        
        Returns:
            dict: Resultados da validação
        """
        print("⚡ Executando validação rápida...")
        
        self.validator = DataValidator(self.data_source, self.dataset_name)
        
        if self.validator.df is None:
            print("❌ Falha ao carregar dados.")
            return None
        
        self.validation_results = self.validator.get_summary()
        self.validator.print_summary()
        
        return self.validation_results
    
    def generate_excel_only(self):
        """
        Gera apenas o relatório Excel
        
        Returns:
            bool: True se gerado com sucesso
        """
        if not self.validation_results:
            print("❌ Execute a validação primeiro!")
            return False
        
        print("📊 Gerando relatório Excel...")
        excel_generator = ExcelReportGenerator(self.validation_results)
        return excel_generator.generate_report()
    
    def generate_pdf_only(self):
        """
        Gera apenas o relatório PDF
        
        Returns:
            bool: True se gerado com sucesso
        """
        if not self.validation_results:
            print("❌ Execute a validação primeiro!")
            return False
        
        print("📄 Gerando relatório PDF...")
        pdf_generator = PDFReportGenerator(self.validation_results)
        return pdf_generator.generate_report()
    
    def create_visualizations_only(self):
        """
        Cria apenas as visualizações
        
        Returns:
            list: Lista de arquivos de gráficos criados
        """
        if not self.validation_results:
            print("❌ Execute a validação primeiro!")
            return []
        
        print("📈 Criando visualizações...")
        visualizer = DataVisualizer(self.validation_results)
        return visualizer.create_all_visualizations(self.output_dir)

def main():
    """
    Função principal para execução via linha de comando
    """
    parser = argparse.ArgumentParser(
        description='Sistema de Relatórios de Validação e Qualidade de Dados',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python data_quality_reporter.py dados.csv "Vendas 2024"
  python data_quality_reporter.py dados.xlsx "Funcionários" --excel-only
  python data_quality_reporter.py dados.csv --pdf-only
  python data_quality_reporter.py dados.csv --quick-validation
        """
    )
    
    parser.add_argument('data_source', help='Fonte dos dados (arquivo CSV, Excel, ou DataFrame)')
    parser.add_argument('dataset_name', nargs='?', default='Dataset', 
                       help='Nome do dataset para identificação nos relatórios')
    parser.add_argument('--output-dir', default='/workspace/reports',
                       help='Diretório para salvar os relatórios (padrão: /workspace/reports)')
    parser.add_argument('--excel-only', action='store_true',
                       help='Gerar apenas relatório Excel')
    parser.add_argument('--pdf-only', action='store_true',
                       help='Gerar apenas relatório PDF')
    parser.add_argument('--quick-validation', action='store_true',
                       help='Executar apenas validação rápida sem gerar relatórios')
    parser.add_argument('--no-visualizations', action='store_true',
                       help='Não criar visualizações')
    
    args = parser.parse_args()
    
    # Verificar se o arquivo existe (se for um caminho)
    if isinstance(args.data_source, str) and not os.path.exists(args.data_source):
        print(f"❌ Arquivo não encontrado: {args.data_source}")
        return 1
    
    # Criar instância do reporter
    reporter = DataQualityReporter(args.data_source, args.dataset_name, args.output_dir)
    
    try:
        if args.quick_validation:
            # Apenas validação rápida
            results = reporter.run_quick_validation()
            return 0 if results else 1
        
        elif args.excel_only:
            # Apenas Excel
            reporter.run_quick_validation()
            success = reporter.generate_excel_only()
            return 0 if success else 1
        
        elif args.pdf_only:
            # Apenas PDF
            reporter.run_quick_validation()
            success = reporter.generate_pdf_only()
            return 0 if success else 1
        
        else:
            # Análise completa
            results = reporter.run_complete_analysis(
                generate_excel=True,
                generate_pdf=True,
                create_visualizations=not args.no_visualizations
            )
            return 0 if results else 1
    
    except KeyboardInterrupt:
        print("\n⚠️ Operação interrompida pelo usuário")
        return 1
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return 1

def create_sample_data():
    """
    Cria dados de exemplo para demonstração
    """
    print("📊 Criando dados de exemplo...")
    
    # Dados com problemas intencionais para demonstração
    data = {
        'ID': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        'Nome': ['João', 'Maria', 'Pedro', 'Ana', 'Carlos', 'Lucia', 'Roberto', 'Fernanda', 
                'Miguel', 'Isabela', 'João', 'Maria', 'Pedro', 'Ana', 'Carlos'],  # Duplicatas
        'Idade': [25, 30, 35, 28, 42, 33, 29, 31, 27, 26, 25, 30, 35, 28, 42],  # Duplicatas
        'Email': ['joao@email.com', 'maria@email.com', 'pedro@email.com', 'ana@email.com', 
                 'carlos@email.com', 'lucia@email.com', 'roberto@email.com', 'fernanda@email.com',
                 'miguel@email.com', 'isabela@email.com', 'joao@email.com', 'maria@email.com',
                 'pedro@email.com', 'ana@email.com', 'carlos@email.com'],  # Duplicatas
        'Salario': [5000, 6000, 7000, 5500, 8000, 6500, 5800, 6200, 5200, 5900, 
                   5000, 6000, 7000, 5500, 8000],  # Duplicatas
        'Departamento': ['TI', 'RH', 'Vendas', 'TI', 'Financeiro', 'RH', 'Vendas', 'TI', 
                        'Financeiro', 'RH', 'TI', 'RH', 'Vendas', 'TI', 'Financeiro'],
        'Data_Admissao': ['2020-01-15', '2019-03-20', '2021-06-10', '2020-08-05', '2018-12-01',
                         '2022-02-14', '2021-09-30', '2020-11-12', '2023-01-08', '2022-07-22',
                         '2020-01-15', '2019-03-20', '2021-06-10', '2020-08-05', '2018-12-01'],
        'Ativo': [True, True, False, True, True, True, False, True, True, True, 
                 True, True, False, True, True],
        'Notas': [8.5, 9.0, 7.5, 8.8, 9.2, 8.0, 7.8, 8.9, 8.3, 9.1, 
                 8.5, 9.0, 7.5, 8.8, 9.2]
    }
    
    # Adicionar alguns problemas intencionais
    df = pd.DataFrame(data)
    
    # Adicionar valores nulos
    df.loc[2, 'Email'] = None
    df.loc[5, 'Salario'] = None
    df.loc[8, 'Idade'] = None
    
    # Adicionar valores inválidos
    df.loc[12, 'Email'] = 'email_invalido'  # Email sem formato correto
    df.loc[13, 'Idade'] = -5  # Idade negativa
    
    # Adicionar outliers
    df.loc[14, 'Salario'] = 50000  # Salário muito alto
    
    # Salvar dados de exemplo
    sample_file = '/workspace/dados_exemplo_validacao.csv'
    df.to_csv(sample_file, index=False)
    
    print(f"✅ Dados de exemplo criados: {sample_file}")
    return sample_file

if __name__ == "__main__":
    # Se executado sem argumentos, criar dados de exemplo e executar análise
    if len(sys.argv) == 1:
        print("🚀 Executando demonstração com dados de exemplo...")
        sample_file = create_sample_data()
        
        # Executar análise completa
        reporter = DataQualityReporter(sample_file, "Dados de Exemplo - Funcionários")
        results = reporter.run_complete_analysis()
        
        if results:
            print("\n🎉 Demonstração concluída com sucesso!")
            print("📁 Verifique a pasta /workspace/reports/ para ver os relatórios gerados.")
        else:
            print("\n❌ Falha na demonstração.")
            sys.exit(1)
    else:
        # Executar com argumentos da linha de comando
        sys.exit(main())