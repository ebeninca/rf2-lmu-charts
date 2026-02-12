# Makefile - Setup virtual environment e tarefas comuns
.PHONY: help install dev test run desktop prod clean venv

PYTHON := python
VENV_DIR := venv
VENV_PYTHON := $(VENV_DIR)/bin/python
VENV_PIP := $(VENV_DIR)/bin/pip

help:
	@echo "🐍 rFactor2-lmu-graphs - Makefile Commands"
	@echo "=========================================="
	@echo ""
	@echo "Setup:"
	@echo "  make install     - Criar venv e instalar dependências"
	@echo "  make dev         - Instalar dependências de desenvolvimento"
	@echo ""
	@echo "Execução:"
	@echo "  make run         - Rodar aplicação em desenvolvimento (DEBUG=True)"
	@echo "  make desktop     - Rodar em modo desktop com waitress"
	@echo "  make prod        - Rodar em produção com gunicorn"
	@echo ""
	@echo "Testes:"
	@echo "  make test        - Rodar pytest com cobertura"
	@echo ""
	@echo "Limpeza:"
	@echo "  make clean       - Remover venv e arquivos temporários"
	@echo ""

# Criar venv se não existir
$(VENV_DIR):
	@echo "📦 Criando virtual environment..."
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "✅ venv criado"

# Install: criar venv + instalar requirements
install: $(VENV_DIR)
	@echo "📦 Instalando dependências..."
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r requirements.txt
	@echo "✅ Dependências instaladas"

# Dev: instalar dependências de desenvolvimento
dev: $(VENV_DIR)
	@echo "📦 Instalando dependências de desenvolvimento..."
	$(VENV_PIP) install -r requirements.txt -r requirements-dev.txt
	@echo "✅ Dependências de dev instaladas"

# Test: rodar testes com pytest
test: $(VENV_DIR)
	@echo "🧪 Rodando testes..."
	$(VENV_PYTHON) -m pytest --cov

# Run: rodar aplicação em desenvolvimento
run: $(VENV_DIR)
	@echo "🚀 Iniciando aplicação..."
	$(VENV_PYTHON) -c "import os; os.environ['DEBUG']='True'" && \
	DEBUG=True $(VENV_PYTHON) app.py

# Desktop: rodar em modo desktop com waitress
desktop: $(VENV_DIR)
	@echo "🖥️  Iniciando em modo desktop com waitress..."
	$(VENV_PYTHON) -c "from waitress import serve; from app import app; serve(app.server, host='0.0.0.0', port=7860, threads=4, channel_timeout=120)"

# Prod: rodar com gunicorn
prod: $(VENV_DIR)
	@echo "🚀 Iniciando em modo produção..."
	$(VENV_PYTHON) -m gunicorn -c gunicorn.conf.py server:server

# Clean: remover venv e arquivos temporários
clean:
	@echo "🧹 Limpando..."
	rm -rf $(VENV_DIR)
	rm -rf htmlcov .pytest_cache .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Limpeza completa"