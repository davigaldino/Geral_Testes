.PHONY: help install migrate runserver worker beat shell test collect-data check clean

help:
	@echo "Comandos disponíveis:"
	@echo "  make install       - Instala dependências"
	@echo "  make migrate       - Executa migrations"
	@echo "  make runserver      - Inicia servidor Django"
	@echo "  make worker        - Inicia Celery worker"
	@echo "  make beat          - Inicia Celery beat"
	@echo "  make shell         - Abre shell Django"
	@echo "  make test          - Executa testes"
	@echo "  make collect-data  - Coleta dados iniciais"
	@echo "  make check         - Verifica configuração do sistema"
	@echo "  make clean         - Limpa arquivos temporários"

install:
	pip install -r requirements.txt

migrate:
	python manage.py makemigrations
	python manage.py migrate

runserver:
	python manage.py runserver

worker:
	celery -A bitcoin_platform worker -l info

beat:
	celery -A bitcoin_platform beat -l info

shell:
	python manage.py shell

test:
	python manage.py test

collect-data:
	python scripts/collect_initial_data.py

check:
	python scripts/check_system.py

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
