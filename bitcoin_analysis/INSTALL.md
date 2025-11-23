# Guia de Instalação Rápida

## Pré-requisitos

1. Python 3.10 ou superior
2. PostgreSQL instalado e rodando
3. Redis instalado e rodando

## Passo a Passo

### 1. Instalar Dependências do Sistema

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3-pip python3-venv postgresql postgresql-contrib redis-server
```

**MacOS:**
```bash
brew install postgresql redis
```

**Windows:**
- Instale PostgreSQL: https://www.postgresql.org/download/windows/
- Instale Redis: https://github.com/microsoftarchive/redis/releases

### 2. Configurar PostgreSQL

```bash
sudo -u postgres psql
```

No prompt do PostgreSQL:
```sql
CREATE DATABASE bitcoin_analysis;
CREATE USER bitcoin_user WITH PASSWORD 'sua_senha_segura';
GRANT ALL PRIVILEGES ON DATABASE bitcoin_analysis TO bitcoin_user;
\q
```

### 3. Clonar e Configurar o Projeto

```bash
cd bitcoin_analysis
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate no Windows
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

```bash
cp .env.example .env
nano .env  # ou use seu editor preferido
```

Edite o arquivo `.env` com suas configurações.

### 5. Executar Migrations

```bash
python manage.py migrate
```

### 6. Criar Superusuário (Opcional)

```bash
python manage.py createsuperuser
```

### 7. Iniciar Serviços

**Terminal 1 - Django:**
```bash
python manage.py runserver
```

**Terminal 2 - Celery Worker:**
```bash
celery -A bitcoin_platform worker -l info
```

**Terminal 3 - Celery Beat:**
```bash
celery -A bitcoin_platform beat -l info
```

### 8. Acessar o Sistema

Abra seu navegador em: `http://localhost:8000`

## Coletar Dados Iniciais

Após iniciar o sistema, você pode coletar dados históricos manualmente:

```bash
python manage.py shell
```

```python
from binance_client.services import BinanceDataService
from indicators.services import IndicatorService
from signals.services import SignalService

# Coletar dados
binance_service = BinanceDataService()
binance_service.fetch_and_save_candles('BTCUSDT', '1h', limit=500)
binance_service.fetch_and_save_candles('BTCUSDT', '4h', limit=500)
binance_service.fetch_and_save_candles('BTCUSDT', '1d', limit=500)

# Calcular indicadores
indicator_service = IndicatorService()
indicator_service.compute_all_indicators('BTCUSDT', intervals=['1h', '4h', '1d'])

# Gerar sinais
signal_service = SignalService()
signal_service.generate_all_signals('BTCUSDT', intervals=['1h', '4h', '1d'])
```

## Verificar se Está Funcionando

1. Acesse `http://localhost:8000` - deve mostrar a página inicial
2. Verifique o admin em `http://localhost:8000/admin` - deve mostrar os modelos
3. Verifique os logs do Celery - devem mostrar tarefas sendo executadas

## Problemas Comuns

### Erro: "No module named 'django'"
- Certifique-se de que o ambiente virtual está ativado
- Execute `pip install -r requirements.txt` novamente

### Erro de conexão com PostgreSQL
- Verifique se o PostgreSQL está rodando: `sudo systemctl status postgresql`
- Verifique as credenciais no arquivo `.env`

### Erro de conexão com Redis
- Verifique se o Redis está rodando: `redis-cli ping`
- Deve retornar `PONG`

### Celery não executa tarefas
- Certifique-se de que tanto o worker quanto o beat estão rodando
- Verifique os logs para erros
