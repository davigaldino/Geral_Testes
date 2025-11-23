# Bitcoin Analysis Platform

Plataforma web completa para análise de Bitcoin usando dados da API da Binance, cálculos de indicadores técnicos, geração de sinais de compra/venda e visualização de informações históricas.

## 🚀 Características

- **Coleta Automática de Dados**: Integração com API da Binance para coleta automática de candles e preços
- **Indicadores Técnicos Avançados**: RSI, SMA, EMA, MACD, Bollinger Bands, VWAP, ATR, Z-Score, Fibonacci, Suporte/Resistência
- **Geração de Sinais**: Sistema inteligente de geração de sinais de compra/venda com pontuação de confiança
- **Dashboard Interativo**: Visualizações com gráficos Plotly, tabelas de indicadores e painel de sinais
- **Tarefas Automáticas**: Celery para atualização automática de dados e cálculos

## 📋 Requisitos

- Python 3.10+
- PostgreSQL
- Redis
- Conta Binance (opcional, para API keys)

## 🛠 Instalação

### 1. Clone o repositório

```bash
cd bitcoin_analysis
```

### 2. Crie e ative um ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

**Nota**: Se encontrar problemas com `ta-lib`, você pode precisar instalar a biblioteca TA-Lib separadamente:

```bash
# Ubuntu/Debian
sudo apt-get install ta-lib

# MacOS
brew install ta-lib

# Windows: Baixe os binários de https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
```

### 4. Configure o banco de dados PostgreSQL

Crie um banco de dados PostgreSQL:

```sql
CREATE DATABASE bitcoin_analysis;
CREATE USER bitcoin_user WITH PASSWORD 'sua_senha';
GRANT ALL PRIVILEGES ON DATABASE bitcoin_analysis TO bitcoin_user;
```

### 5. Configure as variáveis de ambiente

Copie o arquivo `.env.example` para `.env`:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
# Django Settings
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=bitcoin_analysis
DB_USER=bitcoin_user
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=5432

# Binance API (opcional - pode deixar vazio para modo somente leitura)
BINANCE_API_KEY=sua-api-key-aqui
BINANCE_API_SECRET=sua-api-secret-aqui
BINANCE_TESTNET=False

# Celery & Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Security
API_READ_ONLY_MODE=False
```

### 6. Execute as migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Crie um superusuário (opcional)

```bash
python manage.py createsuperuser
```

## 🚀 Como Rodar

### 1. Inicie o servidor Redis

```bash
redis-server
```

### 2. Inicie o servidor Django

Em um terminal:

```bash
python manage.py runserver
```

### 3. Inicie o worker Celery

Em outro terminal:

```bash
celery -A bitcoin_platform worker -l info
```

### 4. Inicie o Celery Beat (agendador de tarefas)

Em outro terminal:

```bash
celery -A bitcoin_platform beat -l info
```

## 📊 Uso

### Acessar o Dashboard

Abra seu navegador e acesse: `http://localhost:8000`

### Páginas Disponíveis

- **Home** (`/`): Preço atual do BTC e últimos sinais
- **Gráficos** (`/chart/<interval>/`): Visualização de gráficos candlestick com indicadores
- **Indicadores** (`/indicators/`): Tabela com todos os indicadores calculados
- **Sinais** (`/signals/`): Painel de sinais de compra/venda com pontuação de confiança
- **Backtesting** (`/backtesting/`): Estrutura para backtesting (em desenvolvimento)
- **Configurações** (`/settings/`): Configurações da plataforma

### Coletar Dados Iniciais

Para coletar dados históricos iniciais, você pode usar o shell do Django:

```bash
python manage.py shell
```

```python
from binance_client.services import BinanceDataService

service = BinanceDataService()
# Coletar últimos 500 candles para cada intervalo
service.fetch_and_save_candles('BTCUSDT', '1h', limit=500)
service.fetch_and_save_candles('BTCUSDT', '4h', limit=500)
service.fetch_and_save_candles('BTCUSDT', '1d', limit=500)
```

### Calcular Indicadores

```python
from indicators.services import IndicatorService

service = IndicatorService()
service.compute_all_indicators('BTCUSDT', intervals=['1h', '4h', '1d'])
```

### Gerar Sinais

```python
from signals.services import SignalService

service = SignalService()
service.generate_all_signals('BTCUSDT', intervals=['1h', '4h', '1d'])
```

## 🔄 Tarefas Automáticas (Celery)

O sistema possui as seguintes tarefas agendadas:

- **fetch_new_candles**: Executa a cada 1 minuto para buscar novos candles
- **compute_indicators**: Executa após fetch_new_candles para calcular indicadores
- **generate_signals**: Executa após compute_indicators para gerar sinais
- **cleanup_old_data**: Executa diariamente para limpar dados antigos (mantém últimos 90 dias)

## 🧪 Testes

Execute os testes com:

```bash
python manage.py test
```

Ou testes específicos:

```bash
python manage.py test binance_client
python manage.py test indicators
python manage.py test signals
```

## 📁 Estrutura do Projeto

```
bitcoin_analysis/
├── bitcoin_platform/          # Configurações do projeto Django
│   ├── settings.py            # Configurações principais
│   ├── urls.py                # URLs principais
│   ├── celery.py              # Configuração Celery
│   └── wsgi.py                # WSGI config
├── binance_client/            # App para integração Binance
│   ├── client.py             # Cliente API Binance
│   ├── services.py            # Serviços de dados
│   ├── models.py              # Modelos de dados
│   ├── tasks.py               # Tarefas Celery
│   └── tests.py               # Testes
├── indicators/                # App de indicadores técnicos
│   ├── calculators.py        # Cálculos de indicadores
│   ├── services.py            # Serviços de indicadores
│   ├── models.py              # Modelos
│   └── tests.py               # Testes
├── signals/                   # App de sinais de trading
│   ├── generators.py         # Geradores de sinais
│   ├── services.py            # Serviços de sinais
│   ├── models.py              # Modelos
│   └── tests.py               # Testes
├── dashboard/                 # App do dashboard web
│   ├── views.py               # Views
│   ├── urls.py                # URLs
│   └── templates/             # Templates HTML
├── templates/                 # Templates base
├── static/                    # Arquivos estáticos
├── manage.py                  # Script de gerenciamento Django
├── requirements.txt          # Dependências Python
├── .env.example              # Exemplo de variáveis de ambiente
└── README.md                 # Este arquivo
```

## 🔒 Segurança

- **Nunca** commite suas API keys no código
- Use sempre o arquivo `.env` para configurações sensíveis
- O arquivo `.env` está no `.gitignore` por padrão
- Ative `API_READ_ONLY_MODE=True` se não quiser usar API keys

## 📝 Indicadores Implementados

### Indicadores Essenciais
- ✅ RSI (14 períodos)
- ✅ SMA (Média Móvel Simples)
- ✅ EMA 50 e EMA 200
- ✅ MACD + Linha de Sinal
- ✅ Bollinger Bands (20 períodos)
- ✅ VWAP
- ✅ ATR

### Indicadores Avançados
- ✅ Reversão à Média (Z-Score)
- ✅ Fibonacci Automático
- ✅ Suporte e Resistência Automáticos

## 🎯 Sinais Implementados

- ✅ Cruzamento EMA50 x EMA200 (Golden Cross / Death Cross)
- ✅ RSI < 30 = potencial compra
- ✅ RSI > 70 = potencial venda
- ✅ Preço tocando Banda Inferior de Bollinger → possível compra
- ✅ Z-Score < -2 → compra
- ✅ Z-Score > +2 → venda
- ✅ Preço próximo a níveis de Fibonacci

## 🐛 Troubleshooting

### Erro de conexão com PostgreSQL

Verifique se o PostgreSQL está rodando e se as credenciais no `.env` estão corretas.

### Erro de conexão com Redis

Certifique-se de que o Redis está rodando:

```bash
redis-cli ping
```

Deve retornar `PONG`.

### Erro ao instalar ta-lib

Veja a seção de instalação acima sobre como instalar TA-Lib para seu sistema operacional.

### Celery não está executando tarefas

Verifique se tanto o worker quanto o beat estão rodando. Certifique-se de que o Redis está acessível.

## 📄 Licença

Este projeto é fornecido como está, para fins educacionais e de análise.

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## ⚠️ Aviso Legal

Este software é fornecido apenas para fins educacionais e de análise. Não constitui aconselhamento financeiro. Trading de criptomoedas envolve risco significativo. Use por sua conta e risco.
