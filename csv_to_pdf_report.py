#!/usr/bin/env python3
"""
Script para ler um arquivo CSV e gerar um relatório em PDF
Autor: Assistente AI
Data: 2024
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os
import sys
from datetime import datetime
import numpy as np

class CSVToPDFReporter:
    def __init__(self, csv_file_path, output_pdf_path=None):
        """
        Inicializa o gerador de relatórios
        
        Args:
            csv_file_path (str): Caminho para o arquivo CSV
            output_pdf_path (str): Caminho para o arquivo PDF de saída
        """
        self.csv_file_path = csv_file_path
        self.output_pdf_path = output_pdf_path or f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        self.df = None
        self.styles = getSampleStyleSheet()
        
    def load_csv(self):
        """Carrega o arquivo CSV"""
        try:
            self.df = pd.read_csv(self.csv_file_path)
            print(f"✅ Arquivo CSV carregado com sucesso: {len(self.df)} linhas e {len(self.df.columns)} colunas")
            return True
        except FileNotFoundError:
            print(f"❌ Erro: Arquivo '{self.csv_file_path}' não encontrado")
            return False
        except Exception as e:
            print(f"❌ Erro ao carregar CSV: {e}")
            return False
    
    def create_summary_statistics(self):
        """Cria estatísticas resumidas dos dados"""
        if self.df is None:
            return None
            
        summary = {
            'total_registros': len(self.df),
            'total_colunas': len(self.df.columns),
            'colunas_numericas': len(self.df.select_dtypes(include=[np.number]).columns),
            'colunas_categoricas': len(self.df.select_dtypes(include=['object']).columns),
            'valores_faltantes': self.df.isnull().sum().sum(),
            'colunas': list(self.df.columns)
        }
        
        # Estatísticas para colunas numéricas
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            summary['estatisticas_numericas'] = self.df[numeric_cols].describe()
            
        return summary
    
    def create_charts(self, output_dir="temp_charts"):
        """Cria gráficos para o relatório"""
        if self.df is None:
            return []
            
        # Criar diretório temporário para os gráficos
        os.makedirs(output_dir, exist_ok=True)
        chart_files = []
        
        # Configurar estilo dos gráficos
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # 1. Gráfico de distribuição de tipos de dados
        fig, ax = plt.subplots(figsize=(10, 6))
        data_types = self.df.dtypes.value_counts()
        data_types.plot(kind='bar', ax=ax, color='skyblue')
        ax.set_title('Distribuição de Tipos de Dados', fontsize=14, fontweight='bold')
        ax.set_xlabel('Tipo de Dado')
        ax.set_ylabel('Quantidade de Colunas')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        chart_path = os.path.join(output_dir, 'tipos_dados.png')
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        chart_files.append(chart_path)
        plt.close()
        
        # 2. Gráfico de valores faltantes
        missing_data = self.df.isnull().sum()
        if missing_data.sum() > 0:
            fig, ax = plt.subplots(figsize=(10, 6))
            missing_data[missing_data > 0].plot(kind='bar', ax=ax, color='coral')
            ax.set_title('Valores Faltantes por Coluna', fontsize=14, fontweight='bold')
            ax.set_xlabel('Coluna')
            ax.set_ylabel('Quantidade de Valores Faltantes')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            chart_path = os.path.join(output_dir, 'valores_faltantes.png')
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            chart_files.append(chart_path)
            plt.close()
        
        # 3. Histograma para colunas numéricas (primeira coluna numérica)
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            col = numeric_cols[0]
            fig, ax = plt.subplots(figsize=(10, 6))
            self.df[col].hist(ax=ax, bins=20, color='lightgreen', alpha=0.7)
            ax.set_title(f'Distribuição de {col}', fontsize=14, fontweight='bold')
            ax.set_xlabel(col)
            ax.set_ylabel('Frequência')
            plt.tight_layout()
            
            chart_path = os.path.join(output_dir, f'histograma_{col}.png')
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            chart_files.append(chart_path)
            plt.close()
        
        return chart_files
    
    def generate_pdf_report(self):
        """Gera o relatório em PDF"""
        if self.df is None:
            print("❌ Nenhum dado carregado. Execute load_csv() primeiro.")
            return False
            
        try:
            # Criar documento PDF
            doc = SimpleDocTemplate(self.output_pdf_path, pagesize=A4)
            story = []
            
            # Título principal
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.darkblue
            )
            title = Paragraph("Relatório de Análise de Dados CSV", title_style)
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Informações do relatório
            info_style = ParagraphStyle(
                'Info',
                parent=self.styles['Normal'],
                fontSize=10,
                textColor=colors.grey
            )
            info_text = f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}<br/>"
            info_text += f"Arquivo fonte: {os.path.basename(self.csv_file_path)}<br/>"
            info_text += f"Total de registros: {len(self.df):,}"
            
            info_paragraph = Paragraph(info_text, info_style)
            story.append(info_paragraph)
            story.append(Spacer(1, 30))
            
            # Resumo estatístico
            summary = self.create_summary_statistics()
            
            # Seção de resumo
            subtitle_style = ParagraphStyle(
                'Subtitle',
                parent=self.styles['Heading2'],
                fontSize=16,
                spaceAfter=12,
                textColor=colors.darkblue
            )
            
            subtitle = Paragraph("Resumo dos Dados", subtitle_style)
            story.append(subtitle)
            story.append(Spacer(1, 12))
            
            # Tabela de resumo
            summary_data = [
                ['Métrica', 'Valor'],
                ['Total de Registros', f"{summary['total_registros']:,}"],
                ['Total de Colunas', summary['total_colunas']],
                ['Colunas Numéricas', summary['colunas_numericas']],
                ['Colunas Categóricas', summary['colunas_categoricas']],
                ['Valores Faltantes', summary['valores_faltantes']]
            ]
            
            summary_table = Table(summary_data, colWidths=[2*inch, 1.5*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 20))
            
            # Lista de colunas
            subtitle = Paragraph("Colunas do Dataset", subtitle_style)
            story.append(subtitle)
            story.append(Spacer(1, 12))
            
            columns_text = "<br/>".join([f"• {col}" for col in summary['colunas']])
            columns_paragraph = Paragraph(columns_text, self.styles['Normal'])
            story.append(columns_paragraph)
            story.append(Spacer(1, 20))
            
            # Estatísticas numéricas
            if 'estatisticas_numericas' in summary:
                subtitle = Paragraph("Estatísticas Descritivas", subtitle_style)
                story.append(subtitle)
                story.append(Spacer(1, 12))
                
                # Converter DataFrame de estatísticas para tabela
                stats_df = summary['estatisticas_numericas']
                stats_data = [['Coluna'] + list(stats_df.index)]
                
                for col in stats_df.columns:
                    row = [col] + [f"{stats_df.loc[index, col]:.2f}" for index in stats_df.index]
                    stats_data.append(row)
                
                stats_table = Table(stats_data, colWidths=[1.2*inch] + [0.8*inch] * (len(stats_data[0]) - 1))
                stats_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]))
                
                story.append(stats_table)
                story.append(Spacer(1, 20))
            
            # Criar e adicionar gráficos
            chart_files = self.create_charts()
            if chart_files:
                subtitle = Paragraph("Visualizações", subtitle_style)
                story.append(subtitle)
                story.append(Spacer(1, 12))
                
                for chart_file in chart_files:
                    try:
                        img = Image(chart_file, width=6*inch, height=4*inch)
                        story.append(img)
                        story.append(Spacer(1, 12))
                    except Exception as e:
                        print(f"Aviso: Não foi possível adicionar o gráfico {chart_file}: {e}")
            
            # Amostra dos dados
            subtitle = Paragraph("Amostra dos Dados (Primeiras 10 linhas)", subtitle_style)
            story.append(subtitle)
            story.append(Spacer(1, 12))
            
            # Preparar dados para tabela
            sample_data = [list(self.df.columns)]  # Cabeçalho
            for _, row in self.df.head(10).iterrows():
                sample_data.append([str(val)[:20] + "..." if len(str(val)) > 20 else str(val) for val in row])
            
            # Calcular larguras das colunas
            col_widths = [1.5*inch] * len(self.df.columns)
            
            sample_table = Table(sample_data, colWidths=col_widths)
            sample_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 6),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            
            story.append(sample_table)
            
            # Gerar PDF
            doc.build(story)
            
            # Limpar arquivos temporários
            for chart_file in chart_files:
                try:
                    os.remove(chart_file)
                except:
                    pass
            try:
                os.rmdir("temp_charts")
            except:
                pass
            
            print(f"✅ Relatório PDF gerado com sucesso: {self.output_pdf_path}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao gerar PDF: {e}")
            return False

def main():
    """Função principal"""
    print("=" * 60)
    print("📊 GERADOR DE RELATÓRIOS CSV PARA PDF")
    print("=" * 60)
    
    # Verificar argumentos da linha de comando
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
    else:
        # Usar arquivo de exemplo se não fornecido
        csv_file = "dados_exemplo.csv"
        output_file = None
    
    # Criar instância do gerador
    reporter = CSVToPDFReporter(csv_file, output_file)
    
    # Carregar dados
    if not reporter.load_csv():
        return
    
    # Gerar relatório
    if reporter.generate_pdf_report():
        print(f"\n🎉 Relatório gerado com sucesso!")
        print(f"📁 Arquivo: {reporter.output_pdf_path}")
        print(f"📊 Total de registros processados: {len(reporter.df):,}")
    else:
        print("\n❌ Falha ao gerar relatório")

if __name__ == "__main__":
    main()