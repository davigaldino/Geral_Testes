#!/usr/bin/env python3
"""
Módulo de Visualização de Dados para Relatórios de Validação
Autor: Assistente AI
Data: 2024

Este módulo cria visualizações profissionais para relatórios de validação de dados:
- Gráficos de distribuição de problemas
- Análise de severidade
- Tendências de qualidade
- Heatmaps de problemas por coluna
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
import os
import tempfile

class DataVisualizer:
    """
    Classe para criação de visualizações de dados de validação
    """
    
    def __init__(self, validation_results):
        """
        Inicializa o visualizador de dados
        
        Args:
            validation_results (dict): Resultados da validação de dados
        """
        self.validation_results = validation_results
        self.chart_files = []
        self._setup_plot_style()
    
    def _setup_plot_style(self):
        """
        Configura o estilo dos gráficos
        """
        # Configurar estilo do matplotlib
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Configurações globais
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['xtick.labelsize'] = 10
        plt.rcParams['ytick.labelsize'] = 10
        plt.rcParams['legend.fontsize'] = 10
        plt.rcParams['figure.titlesize'] = 16
        
        # Cores personalizadas
        self.colors = {
            'critical': '#C5504B',      # Vermelho
            'high': '#FFC000',          # Laranja
            'medium': '#FFFF00',        # Amarelo
            'low': '#92D050',           # Verde claro
            'success': '#70AD47',       # Verde
            'info': '#4F81BD',          # Azul
            'primary': '#366092',       # Azul escuro
            'light_gray': '#F2F2F2',    # Cinza claro
            'dark_gray': '#808080'      # Cinza escuro
        }
    
    def create_all_visualizations(self, output_dir="/workspace/reports"):
        """
        Cria todas as visualizações disponíveis
        
        Args:
            output_dir (str): Diretório para salvar os gráficos
            
        Returns:
            list: Lista de caminhos dos arquivos de gráficos criados
        """
        print("📊 Criando visualizações de dados...")
        
        # Criar diretório se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        # Criar diferentes tipos de visualizações
        self._create_issues_distribution_chart(output_dir)
        self._create_severity_analysis_chart(output_dir)
        self._create_quality_score_gauge(output_dir)
        self._create_issues_timeline_chart(output_dir)
        self._create_column_issues_heatmap(output_dir)
        self._create_problems_summary_chart(output_dir)
        
        print(f"✅ {len(self.chart_files)} visualizações criadas com sucesso!")
        return self.chart_files
    
    def _create_issues_distribution_chart(self, output_dir):
        """
        Cria gráfico de distribuição de problemas por categoria
        """
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            
            # Dados
            categories = list(self.validation_results['issue_categories'].keys())
            counts = list(self.validation_results['issue_categories'].values())
            
            if not counts or sum(counts) == 0:
                # Se não há problemas, criar gráfico vazio
                ax1.text(0.5, 0.5, '✅ Nenhum problema encontrado!', 
                        ha='center', va='center', fontsize=16, color=self.colors['success'])
                ax1.set_title('Distribuição de Problemas por Categoria', fontweight='bold')
                ax1.axis('off')
            else:
                # Gráfico de pizza
                colors_pie = [self.colors['critical'], self.colors['high'], 
                            self.colors['medium'], self.colors['low'], 
                            self.colors['info'], self.colors['primary']]
                
                wedges, texts, autotexts = ax1.pie(
                    counts, 
                    labels=categories, 
                    autopct='%1.1f%%',
                    colors=colors_pie[:len(categories)],
                    startangle=90,
                    explode=[0.05] * len(categories)
                )
                
                # Melhorar legibilidade
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                    autotext.set_fontsize(10)
                
                ax1.set_title('Distribuição de Problemas por Categoria', fontweight='bold')
            
            # Gráfico de barras horizontal
            if counts and sum(counts) > 0:
                y_pos = np.arange(len(categories))
                bars = ax2.barh(y_pos, counts, color=colors_pie[:len(categories)])
                
                # Adicionar valores nas barras
                for i, (bar, count) in enumerate(zip(bars, counts)):
                    ax2.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, 
                            str(count), ha='left', va='center', fontweight='bold')
                
                ax2.set_yticks(y_pos)
                ax2.set_yticklabels(categories)
                ax2.set_xlabel('Quantidade de Problemas')
                ax2.set_title('Problemas por Categoria (Barras)', fontweight='bold')
                ax2.grid(axis='x', alpha=0.3)
            else:
                ax2.text(0.5, 0.5, '✅ Nenhum problema encontrado!', 
                        ha='center', va='center', fontsize=16, color=self.colors['success'])
                ax2.set_title('Problemas por Categoria (Barras)', fontweight='bold')
                ax2.axis('off')
            
            plt.tight_layout()
            
            # Salvar gráfico
            chart_path = os.path.join(output_dir, 'distribuicao_problemas.png')
            plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
            self.chart_files.append(chart_path)
            plt.close()
            
        except Exception as e:
            print(f"Erro ao criar gráfico de distribuição: {e}")
    
    def _create_severity_analysis_chart(self, output_dir):
        """
        Cria gráfico de análise de severidade dos problemas
        """
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            
            # Dados de severidade
            severity_order = ['Crítico', 'Alto', 'Médio', 'Baixo']
            counts = [self.validation_results['issue_severities'].get(s, 0) for s in severity_order]
            colors_severity = [self.colors['critical'], self.colors['high'], 
                             self.colors['medium'], self.colors['low']]
            
            # Gráfico de barras verticais
            bars = ax1.bar(severity_order, counts, color=colors_severity)
            ax1.set_title('Problemas por Nível de Severidade', fontweight='bold')
            ax1.set_xlabel('Severidade')
            ax1.set_ylabel('Quantidade de Problemas')
            
            # Adicionar valores nas barras
            for bar, count in zip(bars, counts):
                if count > 0:
                    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                            str(count), ha='center', va='bottom', fontweight='bold')
            
            # Adicionar grid
            ax1.grid(axis='y', alpha=0.3)
            
            # Gráfico de donut
            if sum(counts) > 0:
                # Filtrar apenas severidades com problemas
                non_zero_counts = [c for c in counts if c > 0]
                non_zero_severities = [s for s, c in zip(severity_order, counts) if c > 0]
                non_zero_colors = [c for c, count in zip(colors_severity, counts) if count > 0]
                
                wedges, texts, autotexts = ax2.pie(
                    non_zero_counts,
                    labels=non_zero_severities,
                    autopct='%1.1f%%',
                    colors=non_zero_colors,
                    startangle=90,
                    pctdistance=0.85
                )
                
                # Criar efeito de donut
                centre_circle = plt.Circle((0,0), 0.70, fc='white')
                ax2.add_artist(centre_circle)
                
                # Adicionar texto no centro
                total_issues = sum(counts)
                ax2.text(0, 0, f'Total\n{total_issues}', ha='center', va='center', 
                        fontsize=12, fontweight='bold')
                
                ax2.set_title('Distribuição de Severidade (Donut)', fontweight='bold')
            else:
                ax2.text(0.5, 0.5, '✅ Nenhum problema encontrado!', 
                        ha='center', va='center', fontsize=16, color=self.colors['success'])
                ax2.set_title('Distribuição de Severidade (Donut)', fontweight='bold')
                ax2.axis('off')
            
            plt.tight_layout()
            
            # Salvar gráfico
            chart_path = os.path.join(output_dir, 'analise_severidade.png')
            plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
            self.chart_files.append(chart_path)
            plt.close()
            
        except Exception as e:
            print(f"Erro ao criar gráfico de severidade: {e}")
    
    def _create_quality_score_gauge(self, output_dir):
        """
        Cria medidor de qualidade (gauge chart)
        """
        try:
            fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(projection='polar'))
            
            # Dados
            quality_score = self.validation_results['quality_score']
            
            # Configurar o gauge
            theta = np.linspace(0, np.pi, 100)
            r = np.ones_like(theta)
            
            # Cores baseadas na pontuação
            if quality_score >= 90:
                color = self.colors['success']
                status = 'EXCELENTE'
            elif quality_score >= 70:
                color = self.colors['info']
                status = 'BOM'
            elif quality_score >= 50:
                color = self.colors['medium']
                status = 'REGULAR'
            else:
                color = self.colors['critical']
                status = 'CRÍTICO'
            
            # Desenhar o gauge
            ax.fill_between(theta, 0, r, alpha=0.3, color=color)
            ax.plot(theta, r, color=color, linewidth=3)
            
            # Adicionar ponteiro
            pointer_angle = np.pi * (1 - quality_score / 100)
            ax.plot([pointer_angle, pointer_angle], [0, 0.8], color='black', linewidth=4)
            ax.plot(pointer_angle, 0.8, 'o', color='black', markersize=8)
            
            # Configurar eixos
            ax.set_ylim(0, 1)
            ax.set_xticks(np.linspace(0, np.pi, 6))
            ax.set_xticklabels(['0', '20', '40', '60', '80', '100'])
            ax.set_yticks([])
            ax.set_title(f'Pontuação de Qualidade: {quality_score:.1f}/100\nStatus: {status}', 
                        fontsize=16, fontweight='bold', pad=20)
            
            # Adicionar texto da pontuação
            ax.text(0, 0, f'{quality_score:.1f}', ha='center', va='center', 
                   fontsize=24, fontweight='bold', color=color)
            
            plt.tight_layout()
            
            # Salvar gráfico
            chart_path = os.path.join(output_dir, 'medidor_qualidade.png')
            plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
            self.chart_files.append(chart_path)
            plt.close()
            
        except Exception as e:
            print(f"Erro ao criar medidor de qualidade: {e}")
    
    def _create_issues_timeline_chart(self, output_dir):
        """
        Cria gráfico de timeline dos problemas (simulado)
        """
        try:
            fig, ax = plt.subplots(figsize=(14, 8))
            
            # Simular timeline baseado nos problemas encontrados
            total_issues = self.validation_results['total_issues']
            
            if total_issues == 0:
                ax.text(0.5, 0.5, '✅ Nenhum problema encontrado!\nTimeline limpa', 
                        ha='center', va='center', fontsize=16, color=self.colors['success'])
                ax.set_title('Timeline de Problemas de Qualidade', fontweight='bold')
                ax.axis('off')
            else:
                # Simular distribuição temporal dos problemas
                np.random.seed(42)  # Para reprodutibilidade
                days = 30
                dates = pd.date_range(start='2024-01-01', periods=days, freq='D')
                
                # Distribuir problemas ao longo do tempo
                issues_per_day = np.random.poisson(total_issues / days, days)
                
                # Criar gráfico de linha
                ax.plot(dates, issues_per_day, marker='o', linewidth=2, 
                       markersize=6, color=self.colors['primary'])
                ax.fill_between(dates, issues_per_day, alpha=0.3, color=self.colors['info'])
                
                # Adicionar linha de média
                avg_issues = np.mean(issues_per_day)
                ax.axhline(y=avg_issues, color=self.colors['critical'], 
                          linestyle='--', linewidth=2, label=f'Média: {avg_issues:.1f}')
                
                ax.set_title('Timeline de Problemas de Qualidade (Simulado)', fontweight='bold')
                ax.set_xlabel('Data')
                ax.set_ylabel('Problemas por Dia')
                ax.legend()
                ax.grid(True, alpha=0.3)
                
                # Rotacionar labels do eixo x
                plt.xticks(rotation=45)
            
            plt.tight_layout()
            
            # Salvar gráfico
            chart_path = os.path.join(output_dir, 'timeline_problemas.png')
            plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
            self.chart_files.append(chart_path)
            plt.close()
            
        except Exception as e:
            print(f"Erro ao criar timeline: {e}")
    
    def _create_column_issues_heatmap(self, output_dir):
        """
        Cria heatmap de problemas por coluna
        """
        try:
            # Preparar dados para o heatmap
            issues = self.validation_results['issues']
            
            if not issues:
                fig, ax = plt.subplots(figsize=(12, 8))
                ax.text(0.5, 0.5, '✅ Nenhum problema encontrado!\nHeatmap limpo', 
                        ha='center', va='center', fontsize=16, color=self.colors['success'])
                ax.set_title('Heatmap de Problemas por Coluna', fontweight='bold')
                ax.axis('off')
            else:
                # Criar DataFrame para o heatmap
                columns = set()
                for issue in issues:
                    columns.update(issue['colunas_afetadas'])
                
                columns = sorted(list(columns))
                categories = ['Valores Faltantes', 'Duplicatas', 'Tipo de Dados', 
                            'Outliers', 'Consistência', 'Formato']
                
                # Criar matriz de problemas
                heatmap_data = np.zeros((len(categories), len(columns)))
                
                for issue in issues:
                    category = issue['categoria']
                    if category in categories:
                        cat_idx = categories.index(category)
                        for col in issue['colunas_afetadas']:
                            if col in columns:
                                col_idx = columns.index(col)
                                heatmap_data[cat_idx, col_idx] += 1
                
                # Criar heatmap
                fig, ax = plt.subplots(figsize=(max(12, len(columns) * 1.5), 8))
                
                im = ax.imshow(heatmap_data, cmap='Reds', aspect='auto')
                
                # Configurar eixos
                ax.set_xticks(range(len(columns)))
                ax.set_xticklabels(columns, rotation=45, ha='right')
                ax.set_yticks(range(len(categories)))
                ax.set_yticklabels(categories)
                
                # Adicionar valores nas células
                for i in range(len(categories)):
                    for j in range(len(columns)):
                        value = heatmap_data[i, j]
                        if value > 0:
                            ax.text(j, i, str(int(value)), ha='center', va='center', 
                                   fontweight='bold', color='white' if value > heatmap_data.max()/2 else 'black')
                
                # Adicionar barra de cores
                cbar = plt.colorbar(im, ax=ax)
                cbar.set_label('Quantidade de Problemas', rotation=270, labelpad=20)
                
                ax.set_title('Heatmap de Problemas por Coluna e Categoria', fontweight='bold')
                ax.set_xlabel('Colunas')
                ax.set_ylabel('Categorias de Problemas')
            
            plt.tight_layout()
            
            # Salvar gráfico
            chart_path = os.path.join(output_dir, 'heatmap_colunas.png')
            plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
            self.chart_files.append(chart_path)
            plt.close()
            
        except Exception as e:
            print(f"Erro ao criar heatmap: {e}")
    
    def _create_problems_summary_chart(self, output_dir):
        """
        Cria gráfico de resumo geral dos problemas
        """
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            
            # 1. Gráfico de pizza - Distribuição geral
            categories = list(self.validation_results['issue_categories'].keys())
            counts = list(self.validation_results['issue_categories'].values())
            
            if counts and sum(counts) > 0:
                ax1.pie(counts, labels=categories, autopct='%1.1f%%', startangle=90)
                ax1.set_title('Distribuição de Problemas', fontweight='bold')
            else:
                ax1.text(0.5, 0.5, '✅ Nenhum problema!', ha='center', va='center', 
                        fontsize=14, color=self.colors['success'])
                ax1.set_title('Distribuição de Problemas', fontweight='bold')
                ax1.axis('off')
            
            # 2. Gráfico de barras - Severidade
            severity_order = ['Crítico', 'Alto', 'Médio', 'Baixo']
            severity_counts = [self.validation_results['issue_severities'].get(s, 0) for s in severity_order]
            colors_severity = [self.colors['critical'], self.colors['high'], 
                             self.colors['medium'], self.colors['low']]
            
            bars = ax2.bar(severity_order, severity_counts, color=colors_severity)
            ax2.set_title('Problemas por Severidade', fontweight='bold')
            ax2.set_ylabel('Quantidade')
            
            # Adicionar valores nas barras
            for bar, count in zip(bars, severity_counts):
                if count > 0:
                    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                            str(count), ha='center', va='bottom', fontweight='bold')
            
            # 3. Medidor de qualidade
            quality_score = self.validation_results['quality_score']
            ax3.text(0.5, 0.5, f'{quality_score:.1f}/100', ha='center', va='center', 
                    fontsize=24, fontweight='bold', 
                    color=self.colors['success'] if quality_score >= 80 else self.colors['critical'])
            ax3.set_title('Pontuação de Qualidade', fontweight='bold')
            ax3.axis('off')
            
            # 4. Resumo estatístico
            stats_text = f"""
            📊 RESUMO ESTATÍSTICO
            
            • Total de Registros: {self.validation_results['total_rows']:,}
            • Total de Colunas: {self.validation_results['total_columns']}
            • Problemas Encontrados: {self.validation_results['total_issues']}
            • Pontuação de Qualidade: {self.validation_results['quality_score']:.1f}/100
            
            🎯 STATUS: {'✅ EXCELENTE' if quality_score >= 90 else '⚠️ ATENÇÃO' if quality_score >= 70 else '🚨 CRÍTICO'}
            """
            
            ax4.text(0.1, 0.5, stats_text, ha='left', va='center', fontsize=12, 
                    transform=ax4.transAxes, bbox=dict(boxstyle="round,pad=0.3", 
                    facecolor=self.colors['light_gray'], alpha=0.8))
            ax4.set_title('Resumo Estatístico', fontweight='bold')
            ax4.axis('off')
            
            plt.suptitle(f'Relatório de Qualidade - {self.validation_results["dataset_name"]}', 
                        fontsize=16, fontweight='bold', y=0.98)
            plt.tight_layout()
            
            # Salvar gráfico
            chart_path = os.path.join(output_dir, 'resumo_problemas.png')
            plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
            self.chart_files.append(chart_path)
            plt.close()
            
        except Exception as e:
            print(f"Erro ao criar resumo de problemas: {e}")
    
    def cleanup_charts(self):
        """
        Remove todos os arquivos de gráficos criados
        """
        for chart_file in self.chart_files:
            try:
                if os.path.exists(chart_file):
                    os.remove(chart_file)
            except Exception as e:
                print(f"Aviso: Não foi possível remover {chart_file}: {e}")
        
        self.chart_files.clear()
        print("🧹 Arquivos de gráficos removidos com sucesso!")