# 📊 Gerador de Relatórios CSV para PDF

Este script Python lê um arquivo CSV e gera um relatório profissional em PDF com análises estatísticas, gráficos e visualizações dos dados.

## 🚀 Funcionalidades

- ✅ Leitura de arquivos CSV
- 📊 Análise estatística automática
- 📈 Geração de gráficos e visualizações
- 📄 Relatório PDF profissional
- 🎨 Formatação elegante com cores e estilos
- 📋 Tabelas organizadas e legíveis
- 📊 Estatísticas descritivas
- 🔍 Amostra dos dados

## 📋 Pré-requisitos

- Python 3.7 ou superior
- Bibliotecas listadas no `requirements.txt`

## 🛠️ Instalação

1. Clone ou baixe os arquivos
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

## 📖 Como Usar

### Uso Básico

```bash
python csv_to_pdf_report.py
```

O script usará automaticamente o arquivo `dados_exemplo.csv` e gerará um PDF com timestamp.

### Uso Personalizado

```bash
python csv_to_pdf_report.py seu_arquivo.csv
```

### Especificando arquivo de saída

```bash
python csv_to_pdf_report.py seu_arquivo.csv relatorio_saida.pdf
```

### Uso Programático

```python
from csv_to_pdf_report import CSVToPDFReporter

# Criar instância
reporter = CSVToPDFReporter('dados.csv', 'relatorio.pdf')

# Carregar dados
if reporter.load_csv():
    # Gerar relatório
    reporter.generate_pdf_report()
```

## 📊 Estrutura do Relatório

O PDF gerado inclui:

1. **Cabeçalho** - Título e informações do relatório
2. **Resumo dos Dados** - Estatísticas gerais
3. **Lista de Colunas** - Todas as colunas do dataset
4. **Estatísticas Descritivas** - Para colunas numéricas
5. **Visualizações** - Gráficos automáticos
6. **Amostra dos Dados** - Primeiras 10 linhas

## 📈 Gráficos Gerados

- Distribuição de tipos de dados
- Valores faltantes por coluna
- Histograma da primeira coluna numérica

## 🎨 Personalização

O script é altamente customizável:

- Cores e estilos podem ser modificados na classe `CSVToPDFReporter`
- Gráficos podem ser personalizados no método `create_charts()`
- Layout do PDF pode ser ajustado no método `generate_pdf_report()`

## 📁 Arquivos Incluídos

- `csv_to_pdf_report.py` - Script principal
- `dados_exemplo.csv` - Arquivo CSV de exemplo
- `requirements.txt` - Dependências Python
- `README.md` - Este arquivo

## 🔧 Solução de Problemas

### Erro: "Arquivo não encontrado"
- Verifique se o arquivo CSV existe no caminho especificado
- Use caminhos absolutos se necessário

### Erro: "Módulo não encontrado"
- Instale as dependências: `pip install -r requirements.txt`

### PDF não gerado
- Verifique permissões de escrita no diretório
- Certifique-se de que há espaço em disco suficiente

## 📝 Exemplo de Saída

O relatório gerado incluirá:
- Tabelas formatadas com cores
- Gráficos profissionais
- Estatísticas detalhadas
- Layout responsivo

## 🤝 Contribuições

Sinta-se à vontade para contribuir com melhorias:
- Adicionar novos tipos de gráficos
- Melhorar a formatação
- Adicionar novas funcionalidades

## 📄 Licença

Este projeto está sob licença MIT. Use livremente para seus projetos.
