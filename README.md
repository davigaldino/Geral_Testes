# 📊 Sistema de Relatórios de Validação e Qualidade de Dados

Um sistema completo e profissional para validação de dados e geração de relatórios em Excel e PDF com visualizações integradas.

## 🚀 Características Principais

- **Validação Abrangente**: Detecta valores faltantes, duplicatas, outliers, inconsistências de tipo e problemas de formato
- **Relatórios Profissionais**: Gera relatórios Excel (.xlsx) e PDF com formatação profissional
- **Visualizações Integradas**: Cria gráficos e charts para análise visual dos problemas
- **Análise por Severidade**: Classifica problemas em níveis de criticidade (Crítico, Alto, Médio, Baixo)
- **Sugestões de Correção**: Fornece recomendações específicas para cada tipo de problema
- **Interface Simples**: Fácil de usar via linha de comando ou programaticamente

## 📋 Funcionalidades

### Validação de Dados
- ✅ Detecção de valores faltantes (nulos)
- ✅ Identificação de duplicatas
- ✅ Análise de outliers
- ✅ Validação de tipos de dados
- ✅ Verificação de consistência
- ✅ Validação de formatos (emails, datas, etc.)
- ✅ Análise de strings vazias
- ✅ Detecção de valores negativos em campos que não deveriam ter

### Relatórios Excel
- 📊 Planilha de visão geral com métricas principais
- 📋 Resumo de problemas por categoria e severidade
- 📝 Detalhamento completo de todos os problemas
- 💡 Sugestões de correção organizadas
- 🎨 Formatação profissional com cores e estilos

### Relatórios PDF
- 📄 Página de capa com resumo executivo
- 📈 Visualizações integradas (gráficos de pizza, barras, medidores)
- 📊 Análise detalhada de problemas
- 💡 Sugestões de correção e melhorias
- 🎯 Foco em problemas críticos e de alta prioridade

### Visualizações
- 🥧 Gráficos de distribuição de problemas
- 📊 Análise de severidade
- 🎯 Medidor de qualidade (gauge chart)
- 📈 Timeline de problemas
- 🔥 Heatmap de problemas por coluna
- 📋 Resumo estatístico visual

## 🛠️ Instalação

### Pré-requisitos
- Python 3.7 ou superior
- pip (gerenciador de pacotes Python)

### Instalação das Dependências

```bash
pip install -r requirements.txt
```

### Dependências Principais
- `pandas>=1.5.0` - Manipulação de dados
- `matplotlib>=3.5.0` - Visualizações
- `seaborn>=0.11.0` - Estilos de gráficos
- `openpyxl>=3.0.0` - Geração de relatórios Excel
- `reportlab>=3.6.0` - Geração de relatórios PDF
- `numpy>=1.21.0` - Computação numérica

## 📖 Como Usar

### 1. Uso Básico via Linha de Comando

```bash
# Análise completa de um arquivo CSV
python data_quality_reporter.py dados.csv "Nome do Dataset"

# Apenas validação rápida
python data_quality_reporter.py dados.csv "Dataset" --quick-validation

# Gerar apenas relatório Excel
python data_quality_reporter.py dados.csv "Dataset" --excel-only

# Gerar apenas relatório PDF
python data_quality_reporter.py dados.csv "Dataset" --pdf-only

# Sem visualizações
python data_quality_reporter.py dados.csv "Dataset" --no-visualizations
```

### 2. Uso Programático

```python
from data_quality_reporter import DataQualityReporter
import pandas as pd

# Criar DataFrame
df = pd.DataFrame({
    'ID': [1, 2, 3, 4, 5],
    'Nome': ['João', 'Maria', 'Pedro', 'Ana', 'Carlos'],
    'Idade': [25, 30, 35, 28, 42],
    'Email': ['joao@email.com', 'maria@email.com', 'pedro@email.com', 'ana@email.com', 'carlos@email.com']
})

# Executar análise completa
reporter = DataQualityReporter(df, "Funcionários")
results = reporter.run_complete_analysis()

# Ou apenas validação
results = reporter.run_quick_validation()
```

### 3. Uso Avançado com Módulos Específicos

```python
from data_validator import DataValidator
from excel_report_generator import ExcelReportGenerator
from pdf_report_generator import PDFReportGenerator
from data_visualizer import DataVisualizer

# Validar dados
validator = DataValidator(df, "Meu Dataset")
validation_results = validator.get_summary()

# Gerar relatório Excel
excel_gen = ExcelReportGenerator(validation_results)
excel_gen.generate_report()

# Gerar relatório PDF
pdf_gen = PDFReportGenerator(validation_results)
pdf_gen.generate_report()

# Criar visualizações
visualizer = DataVisualizer(validation_results)
charts = visualizer.create_all_visualizations('/caminho/para/salvar')
```

## 📁 Estrutura do Projeto

```
/workspace/
├── data_quality_reporter.py    # Script principal
├── data_validator.py           # Classe de validação de dados
├── excel_report_generator.py   # Gerador de relatórios Excel
├── pdf_report_generator.py     # Gerador de relatórios PDF
├── data_visualizer.py          # Criador de visualizações
├── exemplo_uso.py              # Exemplos de uso
├── requirements.txt            # Dependências
├── README.md                   # Esta documentação
└── reports/                    # Pasta de relatórios gerados
    ├── relatorio_validacao_*.xlsx
    ├── relatorio_validacao_*.pdf
    └── *.png                   # Gráficos e visualizações
```

## 🎯 Tipos de Problemas Detectados

### Estrutura
- **Dataset Vazio**: Nenhuma linha de dados
- **Sem Colunas**: Nenhuma coluna definida
- **Colunas Duplicadas**: Nomes de colunas repetidos

### Valores Faltantes
- **Valores Nulos**: Valores None/NaN
- **Linhas Vazias**: Linhas completamente vazias
- **Strings Vazias**: Strings vazias em campos de texto

### Duplicatas
- **Registros Duplicados**: Linhas completamente idênticas
- **IDs Duplicados**: Valores duplicados em coluna de identificação

### Tipo de Dados
- **Tipos Mistos**: Diferentes tipos na mesma coluna
- **Valores Não Numéricos**: Texto em colunas numéricas

### Outliers
- **Valores Extremos**: Valores muito distantes da média (método IQR)

### Consistência
- **Valores Negativos**: Números negativos em campos que não deveriam ter
- **Strings Vazias**: Campos de texto vazios

### Formato
- **Email Inválido**: Emails com formato incorreto
- **Data Inválida**: Datas em formato incorreto

## 📊 Exemplo de Saída

### Resumo no Terminal
```
============================================================
📊 RELATÓRIO DE VALIDAÇÃO DE DADOS
============================================================
📁 Dataset: Funcionários
🕒 Data/Hora: 15/01/2024 14:30:25
📈 Total de Linhas: 1,000
📋 Total de Colunas: 8
⚠️  Total de Problemas: 15
🎯 Pontuação de Qualidade: 85.0/100

📊 PROBLEMAS POR CATEGORIA:
   • Valores Faltantes: 8
   • Duplicatas: 3
   • Tipo de Dados: 2
   • Outliers: 2

🚨 PROBLEMAS POR SEVERIDADE:
   • Crítico: 2
   • Alto: 5
   • Médio: 6
   • Baixo: 2

⚠️  15 problemas encontrados que precisam de atenção.
```

### Arquivos Gerados
- `relatorio_validacao_Funcionarios_20240115_143025.xlsx` - Relatório Excel
- `relatorio_validacao_Funcionarios_20240115_143025.pdf` - Relatório PDF
- `distribuicao_problemas.png` - Gráfico de distribuição
- `analise_severidade.png` - Gráfico de severidade
- `medidor_qualidade.png` - Medidor de qualidade
- E outros gráficos...

## 🔧 Configurações Avançadas

### Personalização de Cores
As cores dos relatórios podem ser personalizadas editando os dicionários `colors` nos geradores.

### Filtros de Problemas
```python
# Obter problemas por categoria
critical_issues = validator.get_issues_by_category('Valores Faltantes')

# Obter problemas por severidade
high_severity = validator.get_issues_by_severity('Alto')
```

### Validação Customizada
```python
# Adicionar validação personalizada
def custom_validation(self):
    # Sua lógica de validação aqui
    pass
```

## 🚀 Exemplos Práticos

### Exemplo 1: Validação de Dados de Funcionários
```python
# Dados com problemas intencionais
data = {
    'ID': [1, 2, 3, 4, 5],
    'Nome': ['João', 'Maria', None, 'Ana', 'Carlos'],  # Nome nulo
    'Idade': [25, 30, 35, -5, 42],  # Idade negativa
    'Email': ['joao@email.com', 'maria@email.com', 'pedro@email.com', 
              'email_invalido', 'carlos@email.com']  # Email inválido
}

df = pd.DataFrame(data)
reporter = DataQualityReporter(df, "Funcionários")
results = reporter.run_complete_analysis()
```

### Exemplo 2: Validação de Dados de Vendas
```python
# Arquivo CSV de vendas
reporter = DataQualityReporter('vendas.csv', 'Vendas 2024')
results = reporter.run_complete_analysis()
```

## 🐛 Solução de Problemas

### Erro: "Arquivo não encontrado"
- Verifique se o caminho do arquivo está correto
- Use caminhos absolutos se necessário

### Erro: "Falha ao carregar dados"
- Verifique se o arquivo está em formato suportado (CSV, Excel)
- Verifique se o arquivo não está corrompido

### Erro: "Falha ao gerar relatório"
- Verifique se a pasta de destino existe
- Verifique permissões de escrita
- Verifique se todas as dependências estão instaladas

## 📝 Logs e Debugging

O sistema gera logs detalhados durante a execução:
- ✅ Sucessos são marcados com ✅
- ❌ Erros são marcados com ❌
- ⚠️ Avisos são marcados com ⚠️
- 📊 Informações são marcadas com 📊

## 🤝 Contribuição

Para contribuir com o projeto:
1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Implemente suas melhorias
4. Adicione testes se necessário
5. Envie um pull request

## 📄 Licença

Este projeto está sob licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 👥 Suporte

Para suporte e dúvidas:
- Abra uma issue no repositório
- Consulte a documentação
- Execute os exemplos em `exemplo_uso.py`

---

**Desenvolvido com ❤️ para melhorar a qualidade dos dados**