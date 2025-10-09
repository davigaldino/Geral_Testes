#!/usr/bin/env python3
"""
Sistema de Validação e Qualidade de Dados
Autor: Assistente AI
Data: 2024

Esta classe realiza análises completas de qualidade de dados incluindo:
- Validação de tipos de dados
- Detecção de valores faltantes
- Identificação de duplicatas
- Análise de outliers
- Verificação de consistência
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class DataValidator:
    """
    Classe principal para validação e análise de qualidade de dados
    """
    
    def __init__(self, data_source, dataset_name="Dataset"):
        """
        Inicializa o validador de dados
        
        Args:
            data_source: DataFrame do pandas, caminho para CSV, ou dados em formato de lista/dict
            dataset_name (str): Nome do dataset para identificação nos relatórios
        """
        self.dataset_name = dataset_name
        self.timestamp = datetime.now()
        self.validation_results = {}
        self.data_quality_issues = []
        
        # Carregar dados
        self.df = self._load_data(data_source)
        
        if self.df is not None:
            self._run_comprehensive_validation()
    
    def _load_data(self, data_source):
        """
        Carrega dados de diferentes fontes (DataFrame, CSV, dict, list)
        
        Args:
            data_source: Fonte dos dados
            
        Returns:
            pandas.DataFrame: DataFrame carregado ou None se houver erro
        """
        try:
            if isinstance(data_source, pd.DataFrame):
                return data_source.copy()
            elif isinstance(data_source, str):
                # Assumir que é um caminho para arquivo CSV
                return pd.read_csv(data_source)
            elif isinstance(data_source, (dict, list)):
                return pd.DataFrame(data_source)
            else:
                print(f"❌ Tipo de dados não suportado: {type(data_source)}")
                return None
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return None
    
    def _run_comprehensive_validation(self):
        """
        Executa todas as validações de qualidade de dados
        """
        if self.df is None:
            return
        
        print(f"🔍 Iniciando validação de dados para: {self.dataset_name}")
        
        # Executar todas as validações
        self._validate_basic_structure()
        self._validate_data_types()
        self._validate_missing_values()
        self._validate_duplicates()
        self._validate_outliers()
        self._validate_consistency()
        self._validate_format()
        
        # Compilar resultados
        self._compile_validation_summary()
        
        print(f"✅ Validação concluída: {len(self.data_quality_issues)} problemas encontrados")
    
    def _validate_basic_structure(self):
        """
        Valida a estrutura básica do dataset
        """
        issues = []
        
        # Verificar se o DataFrame está vazio
        if self.df.empty:
            issues.append({
                'tipo': 'Estrutura',
                'categoria': 'Dataset Vazio',
                'descricao': 'O dataset não contém nenhuma linha de dados',
                'severidade': 'Crítico',
                'linhas_afetadas': 0,
                'colunas_afetadas': list(self.df.columns)
            })
        
        # Verificar se há colunas
        if len(self.df.columns) == 0:
            issues.append({
                'tipo': 'Estrutura',
                'categoria': 'Sem Colunas',
                'descricao': 'O dataset não possui colunas definidas',
                'severidade': 'Crítico',
                'linhas_afetadas': len(self.df),
                'colunas_afetadas': []
            })
        
        # Verificar colunas com nomes duplicados
        duplicate_columns = self.df.columns[self.df.columns.duplicated()].tolist()
        if duplicate_columns:
            issues.append({
                'tipo': 'Estrutura',
                'categoria': 'Colunas Duplicadas',
                'descricao': f'Colunas com nomes duplicados: {duplicate_columns}',
                'severidade': 'Alto',
                'linhas_afetadas': len(self.df),
                'colunas_afetadas': duplicate_columns
            })
        
        self.data_quality_issues.extend(issues)
    
    def _validate_data_types(self):
        """
        Valida tipos de dados e detecta inconsistências
        """
        issues = []
        
        for column in self.df.columns:
            # Verificar se a coluna tem tipo misto
            non_null_values = self.df[column].dropna()
            if len(non_null_values) > 0:
                # Detectar tipos únicos na coluna
                unique_types = set(type(val).__name__ for val in non_null_values)
                if len(unique_types) > 1:
                    issues.append({
                        'tipo': 'Tipo de Dados',
                        'categoria': 'Tipos Mistos',
                        'descricao': f'Coluna "{column}" contém tipos mistos: {list(unique_types)}',
                        'severidade': 'Médio',
                        'linhas_afetadas': len(non_null_values),
                        'colunas_afetadas': [column]
                    })
                
                # Verificar se coluna numérica tem valores não numéricos
                if self.df[column].dtype == 'object':
                    numeric_count = pd.to_numeric(self.df[column], errors='coerce').notna().sum()
                    total_count = len(non_null_values)
                    if numeric_count > 0 and numeric_count < total_count:
                        non_numeric_count = total_count - numeric_count
                        issues.append({
                            'tipo': 'Tipo de Dados',
                            'categoria': 'Valores Não Numéricos',
                            'descricao': f'Coluna "{column}" contém {non_numeric_count} valores não numéricos em coluna de texto',
                            'severidade': 'Médio',
                            'linhas_afetadas': non_numeric_count,
                            'colunas_afetadas': [column]
                        })
        
        self.data_quality_issues.extend(issues)
    
    def _validate_missing_values(self):
        """
        Valida e analisa valores faltantes
        """
        issues = []
        
        missing_data = self.df.isnull().sum()
        total_rows = len(self.df)
        
        for column, missing_count in missing_data.items():
            if missing_count > 0:
                missing_percentage = (missing_count / total_rows) * 100
                
                # Classificar severidade baseada na porcentagem
                if missing_percentage >= 50:
                    severity = 'Crítico'
                elif missing_percentage >= 20:
                    severity = 'Alto'
                elif missing_percentage >= 5:
                    severity = 'Médio'
                else:
                    severity = 'Baixo'
                
                issues.append({
                    'tipo': 'Valores Faltantes',
                    'categoria': 'Valores Nulos',
                    'descricao': f'Coluna "{column}" tem {missing_count} valores faltantes ({missing_percentage:.1f}%)',
                    'severidade': severity,
                    'linhas_afetadas': missing_count,
                    'colunas_afetadas': [column]
                })
        
        # Verificar linhas completamente vazias
        empty_rows = self.df.isnull().all(axis=1).sum()
        if empty_rows > 0:
            issues.append({
                'tipo': 'Valores Faltantes',
                'categoria': 'Linhas Vazias',
                'descricao': f'{empty_rows} linhas completamente vazias encontradas',
                'severidade': 'Alto',
                'linhas_afetadas': empty_rows,
                'colunas_afetadas': list(self.df.columns)
            })
        
        self.data_quality_issues.extend(issues)
    
    def _validate_duplicates(self):
        """
        Detecta registros duplicados
        """
        issues = []
        
        # Verificar duplicatas completas
        duplicate_rows = self.df.duplicated().sum()
        if duplicate_rows > 0:
            issues.append({
                'tipo': 'Duplicatas',
                'categoria': 'Registros Duplicados',
                'descricao': f'{duplicate_rows} registros completamente duplicados encontrados',
                'severidade': 'Médio',
                'linhas_afetadas': duplicate_rows,
                'colunas_afetadas': list(self.df.columns)
            })
        
        # Verificar duplicatas em colunas específicas (assumindo primeira coluna como ID)
        if len(self.df.columns) > 0:
            first_column = self.df.columns[0]
            if self.df[first_column].dtype == 'object' or self.df[first_column].dtype.name.startswith('int'):
                duplicate_ids = self.df[first_column].duplicated().sum()
                if duplicate_ids > 0:
                    issues.append({
                        'tipo': 'Duplicatas',
                        'categoria': 'IDs Duplicados',
                        'descricao': f'Coluna "{first_column}" tem {duplicate_ids} valores duplicados',
                        'severidade': 'Alto',
                        'linhas_afetadas': duplicate_ids,
                        'colunas_afetadas': [first_column]
                    })
        
        self.data_quality_issues.extend(issues)
    
    def _validate_outliers(self):
        """
        Detecta outliers em colunas numéricas
        """
        issues = []
        
        numeric_columns = self.df.select_dtypes(include=[np.number]).columns
        
        for column in numeric_columns:
            if self.df[column].notna().sum() > 0:
                # Usar método IQR para detectar outliers
                Q1 = self.df[column].quantile(0.25)
                Q3 = self.df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = self.df[(self.df[column] < lower_bound) | (self.df[column] > upper_bound)]
                outlier_count = len(outliers)
                
                if outlier_count > 0:
                    outlier_percentage = (outlier_count / len(self.df)) * 100
                    issues.append({
                        'tipo': 'Outliers',
                        'categoria': 'Valores Extremos',
                        'descricao': f'Coluna "{column}" tem {outlier_count} outliers ({outlier_percentage:.1f}%)',
                        'severidade': 'Baixo',
                        'linhas_afetadas': outlier_count,
                        'colunas_afetadas': [column]
                    })
        
        self.data_quality_issues.extend(issues)
    
    def _validate_consistency(self):
        """
        Verifica consistência dos dados
        """
        issues = []
        
        # Verificar valores negativos em colunas que não deveriam ter (ex: idade, preços)
        for column in self.df.select_dtypes(include=[np.number]).columns:
            if 'idade' in column.lower() or 'age' in column.lower():
                negative_values = (self.df[column] < 0).sum()
                if negative_values > 0:
                    issues.append({
                        'tipo': 'Consistência',
                        'categoria': 'Valores Negativos',
                        'descricao': f'Coluna "{column}" tem {negative_values} valores negativos',
                        'severidade': 'Alto',
                        'linhas_afetadas': negative_values,
                        'colunas_afetadas': [column]
                    })
        
        # Verificar strings vazias
        string_columns = self.df.select_dtypes(include=['object']).columns
        for column in string_columns:
            empty_strings = (self.df[column] == '').sum()
            if empty_strings > 0:
                issues.append({
                    'tipo': 'Consistência',
                    'categoria': 'Strings Vazias',
                    'descricao': f'Coluna "{column}" tem {empty_strings} strings vazias',
                    'severidade': 'Médio',
                    'linhas_afetadas': empty_strings,
                    'colunas_afetadas': [column]
                })
        
        self.data_quality_issues.extend(issues)
    
    def _validate_format(self):
        """
        Valida formatos específicos (emails, datas, etc.)
        """
        issues = []
        
        # Verificar formato de email
        email_columns = [col for col in self.df.columns if 'email' in col.lower() or 'mail' in col.lower()]
        for column in email_columns:
            if self.df[column].dtype == 'object':
                # Regex simples para validar email
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                invalid_emails = ~self.df[column].str.match(email_pattern, na=False)
                invalid_count = invalid_emails.sum()
                
                if invalid_count > 0:
                    issues.append({
                        'tipo': 'Formato',
                        'categoria': 'Email Inválido',
                        'descricao': f'Coluna "{column}" tem {invalid_count} emails com formato inválido',
                        'severidade': 'Médio',
                        'linhas_afetadas': invalid_count,
                        'colunas_afetadas': [column]
                    })
        
        self.data_quality_issues.extend(issues)
    
    def _compile_validation_summary(self):
        """
        Compila resumo dos resultados de validação
        """
        if self.df is None:
            return
        
        # Estatísticas básicas
        total_rows = len(self.df)
        total_columns = len(self.df.columns)
        total_issues = len(self.data_quality_issues)
        
        # Contar problemas por categoria
        issue_categories = {}
        issue_severities = {'Crítico': 0, 'Alto': 0, 'Médio': 0, 'Baixo': 0}
        
        for issue in self.data_quality_issues:
            category = issue['categoria']
            severity = issue['severidade']
            
            issue_categories[category] = issue_categories.get(category, 0) + 1
            issue_severities[severity] = issue_severities.get(severity, 0) + 1
        
        # Calcular qualidade geral
        quality_score = max(0, 100 - (total_issues * 2))  # Penalização de 2 pontos por problema
        
        self.validation_results = {
            'dataset_name': self.dataset_name,
            'timestamp': self.timestamp,
            'total_rows': total_rows,
            'total_columns': total_columns,
            'total_issues': total_issues,
            'quality_score': quality_score,
            'issue_categories': issue_categories,
            'issue_severities': issue_severities,
            'issues': self.data_quality_issues
        }
    
    def get_summary(self):
        """
        Retorna resumo dos resultados de validação
        
        Returns:
            dict: Resumo dos resultados
        """
        return self.validation_results
    
    def get_issues_by_category(self, category=None):
        """
        Retorna problemas filtrados por categoria
        
        Args:
            category (str): Categoria específica para filtrar
            
        Returns:
            list: Lista de problemas filtrados
        """
        if category is None:
            return self.data_quality_issues
        
        return [issue for issue in self.data_quality_issues if issue['categoria'] == category]
    
    def get_issues_by_severity(self, severity=None):
        """
        Retorna problemas filtrados por severidade
        
        Args:
            severity (str): Severidade específica para filtrar
            
        Returns:
            list: Lista de problemas filtrados
        """
        if severity is None:
            return self.data_quality_issues
        
        return [issue for issue in self.data_quality_issues if issue['severidade'] == severity]
    
    def print_summary(self):
        """
        Imprime resumo dos resultados de validação
        """
        if not self.validation_results:
            print("❌ Nenhum resultado de validação disponível")
            return
        
        print(f"\n{'='*60}")
        print(f"📊 RELATÓRIO DE VALIDAÇÃO DE DADOS")
        print(f"{'='*60}")
        print(f"📁 Dataset: {self.validation_results['dataset_name']}")
        print(f"🕒 Data/Hora: {self.validation_results['timestamp'].strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"📈 Total de Linhas: {self.validation_results['total_rows']:,}")
        print(f"📋 Total de Colunas: {self.validation_results['total_columns']}")
        print(f"⚠️  Total de Problemas: {self.validation_results['total_issues']}")
        print(f"🎯 Pontuação de Qualidade: {self.validation_results['quality_score']:.1f}/100")
        
        print(f"\n📊 PROBLEMAS POR CATEGORIA:")
        for category, count in self.validation_results['issue_categories'].items():
            print(f"   • {category}: {count}")
        
        print(f"\n🚨 PROBLEMAS POR SEVERIDADE:")
        for severity, count in self.validation_results['issue_severities'].items():
            if count > 0:
                print(f"   • {severity}: {count}")
        
        if self.validation_results['total_issues'] == 0:
            print(f"\n✅ Excelente! Nenhum problema de qualidade encontrado!")
        else:
            print(f"\n⚠️  {self.validation_results['total_issues']} problemas encontrados que precisam de atenção.")