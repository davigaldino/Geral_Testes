#!/usr/bin/env python3
"""
Gerador de Relatórios Excel para Validação de Dados
Autor: Assistente AI
Data: 2024

Este módulo gera relatórios profissionais em Excel (.xlsx) com:
- Resumo executivo
- Detalhamento de problemas por categoria
- Sugestões de correção
- Visualizações integradas
"""

import pandas as pd
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.worksheet.table import Table, TableStyleInfo
from datetime import datetime
import os

class ExcelReportGenerator:
    """
    Gerador de relatórios Excel para validação de dados
    """
    
    def __init__(self, validation_results, output_path=None):
        """
        Inicializa o gerador de relatórios Excel
        
        Args:
            validation_results (dict): Resultados da validação de dados
            output_path (str): Caminho para salvar o arquivo Excel
        """
        self.validation_results = validation_results
        self.output_path = output_path or self._generate_output_path()
        self.workbook = Workbook()
        self._setup_styles()
    
    def _generate_output_path(self):
        """
        Gera caminho automático para o arquivo de saída
        
        Returns:
            str: Caminho do arquivo Excel
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dataset_name = self.validation_results.get('dataset_name', 'dataset')
        safe_name = "".join(c for c in dataset_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        
        return f"/workspace/reports/relatorio_validacao_{safe_name}_{timestamp}.xlsx"
    
    def _setup_styles(self):
        """
        Configura estilos para o relatório Excel
        """
        # Cores personalizadas
        self.colors = {
            'header': '366092',      # Azul escuro
            'subheader': '4F81BD',   # Azul médio
            'critical': 'C5504B',    # Vermelho
            'high': 'FFC000',        # Laranja
            'medium': 'FFFF00',      # Amarelo
            'low': '92D050',         # Verde claro
            'success': '70AD47',     # Verde
            'light_gray': 'F2F2F2',  # Cinza claro
            'white': 'FFFFFF'        # Branco
        }
        
        # Fontes
        self.fonts = {
            'title': Font(name='Arial', size=16, bold=True, color='FFFFFF'),
            'subtitle': Font(name='Arial', size=14, bold=True, color='FFFFFF'),
            'header': Font(name='Arial', size=12, bold=True, color='FFFFFF'),
            'normal': Font(name='Arial', size=11),
            'small': Font(name='Arial', size=10)
        }
        
        # Preenchimentos
        self.fills = {
            'header': PatternFill(start_color=self.colors['header'], end_color=self.colors['header'], fill_type='solid'),
            'subheader': PatternFill(start_color=self.colors['subheader'], end_color=self.colors['subheader'], fill_type='solid'),
            'critical': PatternFill(start_color=self.colors['critical'], end_color=self.colors['critical'], fill_type='solid'),
            'high': PatternFill(start_color=self.colors['high'], end_color=self.colors['high'], fill_type='solid'),
            'medium': PatternFill(start_color=self.colors['medium'], end_color=self.colors['medium'], fill_type='solid'),
            'low': PatternFill(start_color=self.colors['low'], end_color=self.colors['low'], fill_type='solid'),
            'success': PatternFill(start_color=self.colors['success'], end_color=self.colors['success'], fill_type='solid'),
            'light_gray': PatternFill(start_color=self.colors['light_gray'], end_color=self.colors['light_gray'], fill_type='solid')
        }
        
        # Alinhamentos
        self.alignments = {
            'center': Alignment(horizontal='center', vertical='center'),
            'left': Alignment(horizontal='left', vertical='center'),
            'right': Alignment(horizontal='right', vertical='center')
        }
        
        # Bordas
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        self.borders = {'thin': thin_border}
    
    def generate_report(self):
        """
        Gera o relatório completo em Excel
        
        Returns:
            bool: True se o relatório foi gerado com sucesso
        """
        try:
            print("📊 Gerando relatório Excel...")
            
            # Remover planilha padrão
            if 'Sheet' in self.workbook.sheetnames:
                self.workbook.remove(self.workbook['Sheet'])
            
            # Criar planilhas do relatório
            self._create_overview_sheet()
            self._create_issues_summary_sheet()
            self._create_detailed_issues_sheet()
            self._create_suggestions_sheet()
            self._create_data_sample_sheet()
            
            # Salvar arquivo
            self.workbook.save(self.output_path)
            print(f"✅ Relatório Excel gerado com sucesso: {self.output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao gerar relatório Excel: {e}")
            return False
    
    def _create_overview_sheet(self):
        """
        Cria planilha de visão geral
        """
        ws = self.workbook.create_sheet("Visão Geral")
        
        # Título principal
        ws['A1'] = f"Relatório de Validação de Dados - {self.validation_results['dataset_name']}"
        ws['A1'].font = self.fonts['title']
        ws['A1'].fill = self.fills['header']
        ws['A1'].alignment = self.alignments['center']
        ws.merge_cells('A1:F1')
        
        # Informações do relatório
        row = 3
        ws[f'A{row}'] = "Informações do Relatório"
        ws[f'A{row}'].font = self.fonts['subtitle']
        ws[f'A{row}'].fill = self.fills['subheader']
        ws[f'A{row}'].alignment = self.alignments['left']
        ws.merge_cells(f'A{row}:F{row}')
        
        row += 2
        info_data = [
            ["Dataset:", self.validation_results['dataset_name']],
            ["Data/Hora:", self.validation_results['timestamp'].strftime('%d/%m/%Y %H:%M:%S')],
            ["Total de Linhas:", f"{self.validation_results['total_rows']:,}"],
            ["Total de Colunas:", self.validation_results['total_columns']],
            ["Total de Problemas:", self.validation_results['total_issues']],
            ["Pontuação de Qualidade:", f"{self.validation_results['quality_score']:.1f}/100"]
        ]
        
        for label, value in info_data:
            ws[f'A{row}'] = label
            ws[f'A{row}'].font = self.fonts['header']
            ws[f'B{row}'] = value
            ws[f'B{row}'].font = self.fonts['normal']
            row += 1
        
        # Resumo de problemas por categoria
        row += 2
        ws[f'A{row}'] = "Problemas por Categoria"
        ws[f'A{row}'].font = self.fonts['subtitle']
        ws[f'A{row}'].fill = self.fills['subheader']
        ws[f'A{row}'].alignment = self.alignments['left']
        ws.merge_cells(f'A{row}:F{row}')
        
        row += 2
        ws[f'A{row}'] = "Categoria"
        ws[f'B{row}'] = "Quantidade"
        ws[f'C{row}'] = "Percentual"
        
        for cell in [f'A{row}', f'B{row}', f'C{row}']:
            ws[cell].font = self.fonts['header']
            ws[cell].fill = self.fills['header']
            ws[cell].alignment = self.alignments['center']
            ws[cell].border = self.borders['thin']
        
        row += 1
        total_issues = self.validation_results['total_issues']
        
        for category, count in self.validation_results['issue_categories'].items():
            percentage = (count / total_issues * 100) if total_issues > 0 else 0
            
            ws[f'A{row}'] = category
            ws[f'B{row}'] = count
            ws[f'C{row}'] = f"{percentage:.1f}%"
            
            for cell in [f'A{row}', f'B{row}', f'C{row}']:
                ws[cell].font = self.fonts['normal']
                ws[cell].alignment = self.alignments['center']
                ws[cell].border = self.borders['thin']
            
            # Colorir baseado na severidade
            if count > 0:
                if 'Crítico' in category or 'Crítico' in str(count):
                    ws[f'A{row}'].fill = self.fills['critical']
                elif 'Alto' in category or count > total_issues * 0.3:
                    ws[f'A{row}'].fill = self.fills['high']
                elif 'Médio' in category or count > total_issues * 0.1:
                    ws[f'A{row}'].fill = self.fills['medium']
                else:
                    ws[f'A{row}'].fill = self.fills['low']
            
            row += 1
        
        # Ajustar larguras das colunas
        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 15
        ws.column_dimensions['C'].width = 15
    
    def _create_issues_summary_sheet(self):
        """
        Cria planilha de resumo de problemas
        """
        ws = self.workbook.create_sheet("Resumo de Problemas")
        
        # Título
        ws['A1'] = "Resumo de Problemas por Severidade"
        ws['A1'].font = self.fonts['title']
        ws['A1'].fill = self.fills['header']
        ws['A1'].alignment = self.alignments['center']
        ws.merge_cells('A1:D1')
        
        # Cabeçalho da tabela
        row = 3
        headers = ["Severidade", "Quantidade", "Percentual", "Status"]
        for i, header in enumerate(headers, 1):
            cell = ws.cell(row=row, column=i, value=header)
            cell.font = self.fonts['header']
            cell.fill = self.fills['header']
            cell.alignment = self.alignments['center']
            cell.border = self.borders['thin']
        
        # Dados de severidade
        row += 1
        total_issues = self.validation_results['total_issues']
        severity_order = ['Crítico', 'Alto', 'Médio', 'Baixo']
        
        for severity in severity_order:
            count = self.validation_results['issue_severities'].get(severity, 0)
            percentage = (count / total_issues * 100) if total_issues > 0 else 0
            
            # Determinar status
            if count == 0:
                status = "✅ OK"
            elif count <= total_issues * 0.1:
                status = "⚠️ Atenção"
            elif count <= total_issues * 0.3:
                status = "🔶 Cuidado"
            else:
                status = "🚨 Crítico"
            
            # Aplicar cores baseadas na severidade
            fill_color = self.fills['success'] if count == 0 else {
                'Crítico': self.fills['critical'],
                'Alto': self.fills['high'],
                'Médio': self.fills['medium'],
                'Baixo': self.fills['low']
            }.get(severity, self.fills['light_gray'])
            
            data = [severity, count, f"{percentage:.1f}%", status]
            for i, value in enumerate(data, 1):
                cell = ws.cell(row=row, column=i, value=value)
                cell.font = self.fonts['normal']
                cell.fill = fill_color
                cell.alignment = self.alignments['center']
                cell.border = self.borders['thin']
            
            row += 1
        
        # Ajustar larguras
        ws.column_dimensions['A'].width = 15
        ws.column_dimensions['B'].width = 15
        ws.column_dimensions['C'].width = 15
        ws.column_dimensions['D'].width = 20
    
    def _create_detailed_issues_sheet(self):
        """
        Cria planilha com detalhamento de todos os problemas
        """
        ws = self.workbook.create_sheet("Problemas Detalhados")
        
        # Título
        ws['A1'] = "Detalhamento de Problemas Encontrados"
        ws['A1'].font = self.fonts['title']
        ws['A1'].fill = self.fills['header']
        ws['A1'].alignment = self.alignments['center']
        ws.merge_cells('A1:G1')
        
        # Cabeçalho da tabela
        row = 3
        headers = ["Tipo", "Categoria", "Descrição", "Severidade", "Linhas Afetadas", "Colunas Afetadas", "Sugestão"]
        
        for i, header in enumerate(headers, 1):
            cell = ws.cell(row=row, column=i, value=header)
            cell.font = self.fonts['header']
            cell.fill = self.fills['header']
            cell.alignment = self.alignments['center']
            cell.border = self.borders['thin']
        
        # Dados dos problemas
        row += 1
        for issue in self.validation_results['issues']:
            # Gerar sugestão baseada no tipo de problema
            suggestion = self._generate_suggestion(issue)
            
            data = [
                issue['tipo'],
                issue['categoria'],
                issue['descricao'],
                issue['severidade'],
                issue['linhas_afetadas'],
                ', '.join(issue['colunas_afetadas']),
                suggestion
            ]
            
            for i, value in enumerate(data, 1):
                cell = ws.cell(row=row, column=i, value=value)
                cell.font = self.fonts['normal']
                cell.alignment = self.alignments['left']
                cell.border = self.borders['thin']
                
                # Colorir baseado na severidade
                if issue['severidade'] == 'Crítico':
                    cell.fill = self.fills['critical']
                elif issue['severidade'] == 'Alto':
                    cell.fill = self.fills['high']
                elif issue['severidade'] == 'Médio':
                    cell.fill = self.fills['medium']
                elif issue['severidade'] == 'Baixo':
                    cell.fill = self.fills['low']
            
            row += 1
        
        # Ajustar larguras
        column_widths = [15, 20, 40, 12, 15, 20, 30]
        for i, width in enumerate(column_widths, 1):
            ws.column_dimensions[chr(64 + i)].width = width
    
    def _create_suggestions_sheet(self):
        """
        Cria planilha com sugestões de correção
        """
        ws = self.workbook.create_sheet("Sugestões de Correção")
        
        # Título
        ws['A1'] = "Sugestões de Correção e Melhorias"
        ws['A1'].font = self.fonts['title']
        ws['A1'].fill = self.fills['header']
        ws['A1'].alignment = self.alignments['center']
        ws.merge_cells('A1:D1')
        
        # Sugestões gerais
        row = 3
        ws[f'A{row}'] = "Sugestões Gerais"
        ws[f'A{row}'].font = self.fonts['subtitle']
        ws[f'A{row}'].fill = self.fills['subheader']
        ws[f'A{row}'].alignment = self.alignments['left']
        ws.merge_cells(f'A{row}:D{row}')
        
        general_suggestions = [
            "1. Implementar validação de dados na entrada",
            "2. Estabelecer regras de qualidade de dados",
            "3. Criar processo de limpeza automática",
            "4. Implementar monitoramento contínuo",
            "5. Treinar equipe em boas práticas de dados"
        ]
        
        row += 2
        for suggestion in general_suggestions:
            ws[f'A{row}'] = suggestion
            ws[f'A{row}'].font = self.fonts['normal']
            ws[f'A{row}'].alignment = self.alignments['left']
            row += 1
        
        # Sugestões específicas por categoria
        row += 2
        ws[f'A{row}'] = "Sugestões por Categoria de Problema"
        ws[f'A{row}'].font = self.fonts['subtitle']
        ws[f'A{row}'].fill = self.fills['subheader']
        ws[f'A{row}'].alignment = self.alignments['left']
        ws.merge_cells(f'A{row}:D{row}')
        
        category_suggestions = {
            "Valores Faltantes": [
                "• Verificar se os valores são realmente faltantes ou se há padrão",
                "• Considerar imputação de valores (média, mediana, moda)",
                "• Implementar validação obrigatória para campos críticos"
            ],
            "Duplicatas": [
                "• Implementar chaves únicas para identificação",
                "• Criar processo de deduplicação automática",
                "• Estabelecer regras de negócio para duplicatas aceitáveis"
            ],
            "Tipo de Dados": [
                "• Padronizar formatos de entrada",
                "• Implementar conversão automática de tipos",
                "• Criar validação de formato na entrada"
            ],
            "Outliers": [
                "• Investigar se são erros ou valores legítimos",
                "• Implementar regras de detecção de outliers",
                "• Considerar transformações matemáticas"
            ]
        }
        
        row += 2
        for category, suggestions in category_suggestions.items():
            ws[f'A{row}'] = f"📋 {category}:"
            ws[f'A{row}'].font = self.fonts['header']
            ws[f'A{row}'].fill = self.fills['light_gray']
            ws.merge_cells(f'A{row}:D{row}')
            row += 1
            
            for suggestion in suggestions:
                ws[f'A{row}'] = suggestion
                ws[f'A{row}'].font = self.fonts['normal']
                ws[f'A{row}'].alignment = self.alignments['left']
                row += 1
            
            row += 1
        
        # Ajustar larguras
        ws.column_dimensions['A'].width = 50
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 20
        ws.column_dimensions['D'].width = 20
    
    def _create_data_sample_sheet(self):
        """
        Cria planilha com amostra dos dados originais
        """
        ws = self.workbook.create_sheet("Amostra dos Dados")
        
        # Título
        ws['A1'] = f"Amostra dos Dados - {self.validation_results['dataset_name']}"
        ws['A1'].font = self.fonts['title']
        ws['A1'].fill = self.fills['header']
        ws['A1'].alignment = self.alignments['center']
        
        # Nota explicativa
        ws['A2'] = "Esta planilha contém uma amostra dos dados originais para referência"
        ws['A2'].font = self.fonts['small']
        ws['A2'].fill = self.fills['light_gray']
        
        # Aqui você poderia adicionar uma amostra dos dados originais
        # Por enquanto, apenas uma mensagem informativa
        ws['A4'] = "Nota: Para visualizar os dados originais, consulte o arquivo fonte do dataset."
        ws['A4'].font = self.fonts['normal']
        ws['A4'].fill = self.fills['light_gray']
    
    def _generate_suggestion(self, issue):
        """
        Gera sugestão específica baseada no tipo de problema
        
        Args:
            issue (dict): Dicionário com informações do problema
            
        Returns:
            str: Sugestão de correção
        """
        category = issue['categoria']
        severity = issue['severidade']
        
        suggestions = {
            'Valores Nulos': 'Verificar origem dos dados e implementar validação obrigatória',
            'Linhas Vazias': 'Remover linhas vazias ou investigar causa da ausência de dados',
            'Registros Duplicados': 'Implementar chave única ou processo de deduplicação',
            'IDs Duplicados': 'Verificar processo de geração de IDs e implementar validação',
            'Tipos Mistos': 'Padronizar tipos de dados e implementar conversão automática',
            'Valores Não Numéricos': 'Converter para tipo numérico ou remover valores inválidos',
            'Valores Extremos': 'Investigar se são erros ou valores legítimos',
            'Valores Negativos': 'Verificar regras de negócio e implementar validação de range',
            'Strings Vazias': 'Tratar como valores nulos ou implementar validação de conteúdo',
            'Email Inválido': 'Implementar validação de formato de email na entrada'
        }
        
        base_suggestion = suggestions.get(category, 'Revisar dados e implementar validação apropriada')
        
        if severity == 'Crítico':
            return f"🚨 URGENTE: {base_suggestion}"
        elif severity == 'Alto':
            return f"⚠️ ALTA PRIORIDADE: {base_suggestion}"
        elif severity == 'Médio':
            return f"🔶 MÉDIA PRIORIDADE: {base_suggestion}"
        else:
            return f"ℹ️ BAIXA PRIORIDADE: {base_suggestion}"