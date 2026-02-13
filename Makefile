# Makefile - Setup virtual environment e tarefas comuns
.PHONY: help install install-dev dev test run desktop prod audit dist-lnx dist-win clean

PYTHON := python
VENV_DIR := venv
VENV_PYTHON := $(VENV_DIR)/bin/python
VENV_PIP := $(VENV_DIR)/bin/pip

help:
	@echo "🐍 rFactor2-lmu-graphs - Makefile Commands"
	@echo "=========================================="
	@echo ""
	@echo "Setup:"
	@echo "  make install      - Create venv and install dependencies"
	@echo "  make install-dev  - Install development dependencies"
	@echo ""
	@echo "Execution:"
	@echo "  make run         - Run application in development (DEBUG=True)"
	@echo "  make desktop     - Run in desktop mode with waitress"
	@echo "  make prod        - Run in production with gunicorn"
	@echo ""
	@echo "Tests:"
	@echo "  make test        - Run pytest with coverage"
	@echo ""
	@echo "Security:"
	@echo "  make audit       - Audit dependencies for vulnerabilities"
	@echo ""
	@echo "Build Distributable:"
	@echo "  make dist-lnx     - Build Linux distributable"
	@echo "  make dist-win     - Build Windows distributable"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean       - Remove venv and temporary files"
	@echo ""

# Create venv if not exists
$(VENV_DIR):
	@echo "📦 Creating virtual environment..."
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "✅ venv created"

# Install: create venv + install requirements
install: $(VENV_DIR)
	@echo "📦 Installing dependencies..."
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r requirements.txt
	@echo "✅ Dependencies installed"

# Dev: install development dependencies
install-dev: $(VENV_DIR)
	@echo "📦 Installing development dependencies..."
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r requirements.txt -r requirements-dev.txt
	@echo "✅ Development dependencies installed"

# Test: run tests with pytest
test: install-dev
	@echo "🧪 Running tests..."
	$(VENV_PYTHON) -m pytest --cov

# Audit: audit dependencies for vulnerabilities
audit: install-dev
	@echo "🔒 Auditing dependencies for vulnerabilities..."
	$(VENV_DIR)/bin/pip-audit -r requirements.txt --desc --strict

# Run: run application in development
run: install
	@echo "🚀 Starting application..."
	$(VENV_PYTHON) -c "import os; os.environ['DEBUG']='True'" && \
	DEBUG=True $(VENV_PYTHON) app.py

# Desktop: run in desktop mode with waitress
desktop: install
	@echo "🖥️  Starting in desktop mode with waitress..."
	$(VENV_PYTHON) -c "from waitress import serve; from app import app; serve(app.server, host='0.0.0.0', port=7860, threads=4, channel_timeout=120)"

# Prod: run with gunicorn
prod: install
	@echo "🚀 Starting in production mode..."
	$(VENV_PYTHON) -m gunicorn -c gunicorn.conf.py server:server

# Dist-Linux: build distributable for Linux
dist-lnx: install
	@echo "🏗️ Building Linux distributable..."
	$(VENV_PIP) install pyinstaller
	$(VENV_PYTHON) -c "import shutil, os, glob; [shutil.rmtree(d) for d in ['build', 'dist'] if os.path.exists(d)]; [os.remove(f) for f in glob.glob('*.spec')]"
	$(VENV_PYTHON) -m PyInstaller --onefile --name rf2-lmu-charts --icon=assets/finish-flag.png --add-data "assets:assets" --add-data "samples:samples" --hidden-import=waitress app.py
	@echo "✅ Linux build complete: dist/rf2-lmu-charts"

# Dist-Windows: build distributable for Windows
dist-win: install
	@echo "🏗️ Building Windows distributable..."
	$(VENV_PIP) install pyinstaller
	$(VENV_PYTHON) -c "import shutil, os, glob; [shutil.rmtree(d) for d in ['build', 'dist'] if os.path.exists(d)]; [os.remove(f) for f in glob.glob('*.spec')]"
	$(VENV_PYTHON) -m PyInstaller --onefile --name rf2-lmu-charts-windows.exe --icon=assets/finish-flag.ico --add-data "assets;assets" --add-data "samples;samples" --hidden-import=waitress app.py
	@echo "✅ Windows build complete: dist/rf2-lmu-charts-windows.exe"

# Clean: remove venv and temporary files
clean:
	@echo "🧹 Cleaning..."
	rm -rf $(VENV_DIR)
	rm -rf htmlcov .pytest_cache .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete"