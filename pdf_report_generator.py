#!/usr/bin/env python3
"""
Gerador de Relatórios PDF para Validação de Dados
Autor: Assistente AI
Data: 2024

Este módulo gera relatórios profissionais em PDF com:
- Resumo executivo
- Detalhamento de problemas
- Visualizações integradas
- Sugestões de correção
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics import renderPDF
import os
import tempfile
from datetime import datetime
import numpy as np

class PDFReportGenerator:
    """
    Gerador de relatórios PDF para validação de dados
    """
    
    def __init__(self, validation_results, output_path=None):
        """
        Inicializa o gerador de relatórios PDF
        
        Args:
            validation_results (dict): Resultados da validação de dados
            output_path (str): Caminho para salvar o arquivo PDF
        """
        self.validation_results = validation_results
        self.output_path = output_path or self._generate_output_path()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        self.chart_files = []
    
    def _generate_output_path(self):
        """
        Gera caminho automático para o arquivo de saída
        
        Returns:
            str: Caminho do arquivo PDF
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dataset_name = self.validation_results.get('dataset_name', 'dataset')
        safe_name = "".join(c for c in dataset_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        
        return f"/workspace/reports/relatorio_validacao_{safe_name}_{timestamp}.pdf"
    
    def _setup_custom_styles(self):
        """
        Configura estilos personalizados para o PDF
        """
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            alignment=TA_LEFT,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        ))
        
        # Cabeçalho de seção
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceAfter=8,
            alignment=TA_LEFT,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        ))
        
        # Texto normal
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Texto pequeno
        self.styles.add(ParagraphStyle(
            name='SmallText',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_LEFT,
            fontName='Helvetica'
        ))
        
        # Informações do relatório
        self.styles.add(ParagraphStyle(
            name='ReportInfo',
            parent=self.styles['Normal'],
            fontSize=9,
            alignment=TA_RIGHT,
            textColor=colors.grey,
            fontName='Helvetica-Oblique'
        ))
    
    def generate_report(self):
        """
        Gera o relatório completo em PDF
        
        Returns:
            bool: True se o relatório foi gerado com sucesso
        """
        try:
            print("📄 Gerando relatório PDF...")
            
            # Criar documento PDF
            doc = SimpleDocTemplate(
                self.output_path,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # Construir conteúdo
            story = []
            self._build_report_content(story)
            
            # Gerar PDF
            doc.build(story)
            
            # Limpar arquivos temporários
            self._cleanup_temp_files()
            
            print(f"✅ Relatório PDF gerado com sucesso: {self.output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao gerar relatório PDF: {e}")
            return False
    
    def _build_report_content(self, story):
        """
        Constrói o conteúdo completo do relatório
        
        Args:
            story (list): Lista de elementos do relatório
        """
        # Página de capa
        self._add_cover_page(story)
        story.append(PageBreak())
        
        # Resumo executivo
        self._add_executive_summary(story)
        story.append(PageBreak())
        
        # Análise de problemas
        self._add_issues_analysis(story)
        story.append(PageBreak())
        
        # Visualizações
        self._add_visualizations(story)
        story.append(PageBreak())
        
        # Sugestões de correção
        self._add_correction_suggestions(story)
        story.append(PageBreak())
        
        # Detalhamento de problemas
        self._add_detailed_issues(story)
    
    def _add_cover_page(self, story):
        """
        Adiciona página de capa ao relatório
        """
        # Título principal
        title = Paragraph("Relatório de Validação e Qualidade de Dados", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 30))
        
        # Nome do dataset
        dataset_name = self.validation_results['dataset_name']
        dataset_para = Paragraph(f"<b>Dataset:</b> {dataset_name}", self.styles['CustomSubtitle'])
        story.append(dataset_para)
        story.append(Spacer(1, 20))
        
        # Informações do relatório
        timestamp = self.validation_results['timestamp'].strftime('%d/%m/%Y às %H:%M:%S')
        info_text = f"""
        <b>Data/Hora de Geração:</b> {timestamp}<br/>
        <b>Total de Registros:</b> {self.validation_results['total_rows']:,}<br/>
        <b>Total de Colunas:</b> {self.validation_results['total_columns']}<br/>
        <b>Problemas Encontrados:</b> {self.validation_results['total_issues']}<br/>
        <b>Pontuação de Qualidade:</b> {self.validation_results['quality_score']:.1f}/100
        """
        
        info_para = Paragraph(info_text, self.styles['CustomNormal'])
        story.append(info_para)
        story.append(Spacer(1, 40))
        
        # Status da qualidade
        quality_score = self.validation_results['quality_score']
        if quality_score >= 90:
            status = "✅ EXCELENTE"
            color = "green"
        elif quality_score >= 70:
            status = "⚠️ BOM"
            color = "orange"
        elif quality_score >= 50:
            status = "🔶 REGULAR"
            color = "red"
        else:
            status = "🚨 CRÍTICO"
            color = "darkred"
        
        status_para = Paragraph(f"<b>Status da Qualidade:</b> <font color='{color}'>{status}</font>", self.styles['CustomSubtitle'])
        story.append(status_para)
    
    def _add_executive_summary(self, story):
        """
        Adiciona resumo executivo ao relatório
        """
        # Título da seção
        title = Paragraph("Resumo Executivo", self.styles['CustomSubtitle'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Resumo dos dados
        summary_text = f"""
        Este relatório apresenta uma análise completa da qualidade dos dados do dataset 
        <b>"{self.validation_results['dataset_name']}"</b>, contendo <b>{self.validation_results['total_rows']:,}</b> 
        registros e <b>{self.validation_results['total_columns']}</b> colunas.
        """
        
        summary_para = Paragraph(summary_text, self.styles['CustomNormal'])
        story.append(summary_para)
        story.append(Spacer(1, 12))
        
        # Métricas principais
        metrics_data = [
            ['Métrica', 'Valor', 'Status'],
            ['Total de Registros', f"{self.validation_results['total_rows']:,}", '✅'],
            ['Total de Colunas', str(self.validation_results['total_columns']), '✅'],
            ['Problemas Encontrados', str(self.validation_results['total_issues']), 
             '✅' if self.validation_results['total_issues'] == 0 else '⚠️'],
            ['Pontuação de Qualidade', f"{self.validation_results['quality_score']:.1f}/100", 
             '✅' if self.validation_results['quality_score'] >= 80 else '⚠️']
        ]
        
        metrics_table = Table(metrics_data, colWidths=[2*inch, 1.5*inch, 0.8*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        
        story.append(metrics_table)
        story.append(Spacer(1, 20))
        
        # Resumo de problemas por categoria
        if self.validation_results['issue_categories']:
            story.append(Paragraph("Problemas por Categoria", self.styles['SectionHeader']))
            story.append(Spacer(1, 8))
            
            category_data = [['Categoria', 'Quantidade', 'Percentual']]
            total_issues = self.validation_results['total_issues']
            
            for category, count in self.validation_results['issue_categories'].items():
                percentage = (count / total_issues * 100) if total_issues > 0 else 0
                category_data.append([category, str(count), f"{percentage:.1f}%"])
            
            category_table = Table(category_data, colWidths=[2*inch, 1*inch, 1*inch])
            category_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            
            story.append(category_table)
    
    def _add_issues_analysis(self, story):
        """
        Adiciona análise de problemas ao relatório
        """
        # Título da seção
        title = Paragraph("Análise Detalhada de Problemas", self.styles['CustomSubtitle'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Análise por severidade
        story.append(Paragraph("Distribuição por Severidade", self.styles['SectionHeader']))
        story.append(Spacer(1, 8))
        
        severity_data = [['Severidade', 'Quantidade', 'Percentual', 'Status']]
        total_issues = self.validation_results['total_issues']
        severity_order = ['Crítico', 'Alto', 'Médio', 'Baixo']
        
        for severity in severity_order:
            count = self.validation_results['issue_severities'].get(severity, 0)
            percentage = (count / total_issues * 100) if total_issues > 0 else 0
            
            if count == 0:
                status = "✅ OK"
            elif count <= total_issues * 0.1:
                status = "⚠️ Atenção"
            elif count <= total_issues * 0.3:
                status = "🔶 Cuidado"
            else:
                status = "🚨 Crítico"
            
            severity_data.append([severity, str(count), f"{percentage:.1f}%", status])
        
        severity_table = Table(severity_data, colWidths=[1.2*inch, 1*inch, 1*inch, 1.2*inch])
        severity_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        
        story.append(severity_table)
        story.append(Spacer(1, 20))
        
        # Resumo dos problemas mais críticos
        critical_issues = [issue for issue in self.validation_results['issues'] if issue['severidade'] == 'Crítico']
        if critical_issues:
            story.append(Paragraph("Problemas Críticos Identificados", self.styles['SectionHeader']))
            story.append(Spacer(1, 8))
            
            for i, issue in enumerate(critical_issues[:5], 1):  # Mostrar apenas os 5 primeiros
                issue_text = f"""
                <b>{i}. {issue['categoria']}</b><br/>
                {issue['descricao']}<br/>
                <i>Linhas afetadas: {issue['linhas_afetadas']} | Colunas: {', '.join(issue['colunas_afetadas'])}</i>
                """
                issue_para = Paragraph(issue_text, self.styles['SmallText'])
                story.append(issue_para)
                story.append(Spacer(1, 8))
    
    def _add_visualizations(self, story):
        """
        Adiciona visualizações ao relatório
        """
        # Título da seção
        title = Paragraph("Visualizações e Gráficos", self.styles['CustomSubtitle'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Criar gráficos
        self._create_issues_pie_chart()
        self._create_severity_bar_chart()
        
        # Adicionar gráficos ao relatório
        for chart_file in self.chart_files:
            try:
                img = Image(chart_file, width=6*inch, height=4*inch)
                story.append(img)
                story.append(Spacer(1, 12))
            except Exception as e:
                print(f"Aviso: Não foi possível adicionar o gráfico {chart_file}: {e}")
    
    def _create_issues_pie_chart(self):
        """
        Cria gráfico de pizza para problemas por categoria
        """
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            categories = list(self.validation_results['issue_categories'].keys())
            counts = list(self.validation_results['issue_categories'].values())
            
            if counts and sum(counts) > 0:
                colors_pie = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
                
                wedges, texts, autotexts = ax.pie(
                    counts, 
                    labels=categories, 
                    autopct='%1.1f%%',
                    colors=colors_pie[:len(categories)],
                    startangle=90
                )
                
                ax.set_title('Distribuição de Problemas por Categoria', fontsize=14, fontweight='bold')
                
                # Melhorar legibilidade
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                
                plt.tight_layout()
                
                # Salvar gráfico
                chart_file = tempfile.mktemp(suffix='.png')
                plt.savefig(chart_file, dpi=300, bbox_inches='tight')
                self.chart_files.append(chart_file)
                plt.close()
            
        except Exception as e:
            print(f"Erro ao criar gráfico de pizza: {e}")
    
    def _create_severity_bar_chart(self):
        """
        Cria gráfico de barras para problemas por severidade
        """
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            severity_order = ['Crítico', 'Alto', 'Médio', 'Baixo']
            counts = [self.validation_results['issue_severities'].get(s, 0) for s in severity_order]
            
            # Cores baseadas na severidade
            colors_bar = ['#C5504B', '#FFC000', '#FFFF00', '#92D050']
            
            bars = ax.bar(severity_order, counts, color=colors_bar)
            ax.set_title('Problemas por Nível de Severidade', fontsize=14, fontweight='bold')
            ax.set_xlabel('Severidade')
            ax.set_ylabel('Quantidade de Problemas')
            
            # Adicionar valores nas barras
            for bar, count in zip(bars, counts):
                if count > 0:
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                           str(count), ha='center', va='bottom', fontweight='bold')
            
            plt.tight_layout()
            
            # Salvar gráfico
            chart_file = tempfile.mktemp(suffix='.png')
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            self.chart_files.append(chart_file)
            plt.close()
            
        except Exception as e:
            print(f"Erro ao criar gráfico de barras: {e}")
    
    def _add_correction_suggestions(self, story):
        """
        Adiciona sugestões de correção ao relatório
        """
        # Título da seção
        title = Paragraph("Sugestões de Correção e Melhorias", self.styles['CustomSubtitle'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Sugestões gerais
        story.append(Paragraph("Sugestões Gerais", self.styles['SectionHeader']))
        story.append(Spacer(1, 8))
        
        general_suggestions = [
            "1. Implementar validação de dados na entrada para prevenir problemas futuros",
            "2. Estabelecer regras de qualidade de dados claras e documentadas",
            "3. Criar processo de limpeza automática de dados rotineira",
            "4. Implementar monitoramento contínuo da qualidade dos dados",
            "5. Treinar a equipe em boas práticas de entrada e manutenção de dados"
        ]
        
        for suggestion in general_suggestions:
            sug_para = Paragraph(suggestion, self.styles['CustomNormal'])
            story.append(sug_para)
            story.append(Spacer(1, 6))
        
        story.append(Spacer(1, 12))
        
        # Sugestões específicas por categoria
        story.append(Paragraph("Sugestões por Categoria de Problema", self.styles['SectionHeader']))
        story.append(Spacer(1, 8))
        
        category_suggestions = {
            "Valores Faltantes": [
                "• Verificar se os valores são realmente faltantes ou se há um padrão sistemático",
                "• Considerar imputação de valores usando média, mediana ou moda",
                "• Implementar validação obrigatória para campos críticos do negócio"
            ],
            "Duplicatas": [
                "• Implementar chaves únicas para identificação de registros",
                "• Criar processo de deduplicação automática baseado em regras de negócio",
                "• Estabelecer critérios claros para duplicatas aceitáveis"
            ],
            "Tipo de Dados": [
                "• Padronizar formatos de entrada de dados",
                "• Implementar conversão automática de tipos quando apropriado",
                "• Criar validação de formato na entrada de dados"
            ],
            "Outliers": [
                "• Investigar se são erros de entrada ou valores legítimos",
                "• Implementar regras de detecção de outliers baseadas no domínio",
                "• Considerar transformações matemáticas para normalizar distribuições"
            ]
        }
        
        for category, suggestions in category_suggestions.items():
            if category in self.validation_results['issue_categories']:
                story.append(Paragraph(f"📋 {category}:", self.styles['SectionHeader']))
                for suggestion in suggestions:
                    sug_para = Paragraph(suggestion, self.styles['CustomNormal'])
                    story.append(sug_para)
                    story.append(Spacer(1, 4))
                story.append(Spacer(1, 8))
    
    def _add_detailed_issues(self, story):
        """
        Adiciona detalhamento completo de todos os problemas
        """
        # Título da seção
        title = Paragraph("Detalhamento Completo de Problemas", self.styles['CustomSubtitle'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Tabela de problemas
        issues_data = [['Tipo', 'Categoria', 'Descrição', 'Severidade', 'Linhas', 'Colunas']]
        
        for issue in self.validation_results['issues']:
            issues_data.append([
                issue['tipo'],
                issue['categoria'],
                issue['descricao'][:50] + "..." if len(issue['descricao']) > 50 else issue['descricao'],
                issue['severidade'],
                str(issue['linhas_afetadas']),
                ', '.join(issue['colunas_afetadas'])[:30] + "..." if len(', '.join(issue['colunas_afetadas'])) > 30 else ', '.join(issue['colunas_afetadas'])
            ])
        
        issues_table = Table(issues_data, colWidths=[1*inch, 1.2*inch, 2*inch, 0.8*inch, 0.6*inch, 1*inch])
        issues_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(issues_table)
    
    def _cleanup_temp_files(self):
        """
        Remove arquivos temporários criados durante a geração do relatório
        """
        for chart_file in self.chart_files:
            try:
                if os.path.exists(chart_file):
                    os.remove(chart_file)
            except Exception as e:
                print(f"Aviso: Não foi possível remover arquivo temporário {chart_file}: {e}")
        
        self.chart_files.clear()