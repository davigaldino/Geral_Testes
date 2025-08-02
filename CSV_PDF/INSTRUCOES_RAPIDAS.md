# 🚀 Instruções Rápidas

## ⚡ Uso Imediato

### 1. Instalar dependências
```bash
pip3 install --break-system-packages pandas matplotlib seaborn reportlab numpy
```

### 2. Executar com arquivo padrão
```bash
python3 csv_to_pdf_report.py
```

### 3. Executar com seu arquivo CSV
```bash
python3 csv_to_pdf_report.py seu_arquivo.csv
```

### 4. Executar com nome personalizado do PDF
```bash
python3 csv_to_pdf_report.py seu_arquivo.csv meu_relatorio.pdf
```

## 📊 Exemplos Práticos

### Exemplo 1: Dados de Funcionários
```csv
Nome,Idade,Salario,Departamento
João,28,4500,Tecnologia
Maria,32,5200,Marketing
Pedro,25,3800,Vendas
```

### Exemplo 2: Dados de Vendas
```csv
Produto,Quantidade,Preco,Data
Laptop,10,2500,2024-01-15
Mouse,50,50,2024-01-16
Teclado,25,150,2024-01-17
```

## 🎯 Funcionalidades do Relatório

✅ **Estatísticas Gerais**
- Total de registros
- Número de colunas
- Tipos de dados
- Valores faltantes

✅ **Análise Numérica**
- Média, mediana, desvio padrão
- Valores mínimo e máximo
- Quartis

✅ **Visualizações**
- Gráfico de tipos de dados
- Gráfico de valores faltantes
- Histograma da primeira coluna numérica

✅ **Amostra dos Dados**
- Primeiras 10 linhas formatadas
- Tabela com cores e bordas

## 🔧 Personalização

### Modificar cores do PDF
```python
# No arquivo csv_to_pdf_report.py, linha ~150
textColor=colors.darkblue  # Mude para outras cores
```

### Adicionar novos gráficos
```python
# No método create_charts(), adicione:
fig, ax = plt.subplots(figsize=(10, 6))
# Seu código de gráfico aqui
```

## 📁 Arquivos Gerados

- `relatorio_YYYYMMDD_HHMMSS.pdf` - Relatório com timestamp
- `relatorio_personalizado.pdf` - Se especificado

## 🆘 Solução de Problemas

**Erro: "Módulo não encontrado"**
```bash
pip3 install --break-system-packages pandas matplotlib seaborn reportlab numpy
```

**Erro: "Arquivo não encontrado"**
- Verifique se o arquivo CSV existe
- Use caminho completo se necessário

**PDF não gerado**
- Verifique permissões de escrita
- Certifique-se de que há espaço em disco

## 📞 Suporte

Para mais detalhes, consulte o `README.md` completo.