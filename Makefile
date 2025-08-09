# MS11 Project Makefile
# Provides convenient shortcuts for common development tasks

.PHONY: help setup test lint format clean install run dev docs quick-test

# Default Python - adjust if needed
PYTHON := python

# Virtual environment paths
VENV_PATH := venv
ifeq ($(OS),Windows_NT)
	VENV_PYTHON := $(VENV_PATH)/Scripts/python.exe
	VENV_PIP := $(VENV_PATH)/Scripts/pip.exe
else
	VENV_PYTHON := $(VENV_PATH)/bin/python
	VENV_PIP := $(VENV_PATH)/bin/pip
endif

help: ## Show this help message
	@echo "🛠️  MS11 Development Commands"
	@echo "================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "📋 Common workflows:"
	@echo "  make setup      # First-time setup"
	@echo "  make dev        # Start development environment"
	@echo "  make test       # Run tests"
	@echo "  make clean      # Clean temporary files"

setup: ## Set up development environment
	@echo "🔧 Setting up development environment..."
	$(PYTHON) scripts/dev_setup.py

venv: ## Create virtual environment if it doesn't exist
	@if [ ! -d "$(VENV_PATH)" ]; then \
		echo "📦 Creating virtual environment..."; \
		$(PYTHON) -m venv $(VENV_PATH); \
	fi

install: venv ## Install dependencies
	@echo "📦 Installing dependencies..."
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r requirements.txt
	@if [ -f "requirements-dev.txt" ]; then \
		$(VENV_PIP) install -r requirements-dev.txt; \
	fi

test: ## Run tests
	@echo "🧪 Running tests..."
	$(VENV_PYTHON) -m pytest tests/ -v

test-cov: ## Run tests with coverage
	@echo "🧪 Running tests with coverage..."
	$(VENV_PYTHON) -m pytest tests/ --cov=src --cov-report=html --cov-report=term

quick-test: ## Run quick system test
	@echo "⚡ Running quick system test..."
	$(VENV_PYTHON) scripts/quick_test_ms11.py

lint: ## Run code quality checks
	@echo "🔍 Running code quality checks..."
	$(VENV_PYTHON) -m flake8 src/ scripts/ tests/ --max-line-length=100 --ignore=E501,W503
	$(VENV_PYTHON) -m bandit -r src/ -f json || true

format: ## Format code with black
	@echo "✨ Formatting code..."
	$(VENV_PYTHON) -m black src/ scripts/ tests/ --line-length=100

format-check: ## Check code formatting
	@echo "✨ Checking code formatting..."
	$(VENV_PYTHON) -m black src/ scripts/ tests/ --line-length=100 --check --diff

mypy: ## Run type checking
	@echo "🔍 Running type checking..."
	$(VENV_PYTHON) -m mypy src/

clean: ## Clean temporary files
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ *.egg-info/ .coverage htmlcov/ .mypy_cache/

run: ## Start MS11 interface
	@echo "🚀 Starting MS11 interface..."
	$(VENV_PYTHON) scripts/ms11_interface.py

gui: ## Start MS11 GUI interface
	@echo "🖥️ Starting MS11 GUI..."
	$(VENV_PYTHON) scripts/ms11_gui.py

dashboard: ## Start web dashboard
	@echo "🌐 Starting web dashboard..."
	@echo "Dashboard will be available at: http://localhost:5000/ms11"
	$(VENV_PYTHON) dashboard/app.py

dev: install ## Set up development environment and start interface
	@echo "🚀 Starting development environment..."
	$(VENV_PYTHON) scripts/ms11_interface.py

build: ## Build the project
	@echo "🏗️ Building project..."
	$(VENV_PYTHON) -m pip install -e .

docs: ## Generate documentation
	@echo "📚 Generating documentation..."
	@echo "Available documentation files:"
	@find docs/ -name "*.md" -type f | sort

security: ## Run security scans
	@echo "🔒 Running security scans..."
	$(VENV_PYTHON) -m bandit -r src/ -f json -o bandit-report.json
	@echo "Security report saved to: bandit-report.json"

profile: ## Profile MS11 performance
	@echo "📊 Profiling MS11 performance..."
	$(VENV_PYTHON) scripts/dev_tools.py profile

ci-test: ## Run CI-style tests
	@echo "⚙️ Running CI-style tests..."
	$(VENV_PYTHON) -m pytest tests/test_ci_sanity.py -v --tb=short

all: clean install test lint ## Run complete check (clean, install, test, lint)

version: ## Show version information
	@echo "📋 MS11 Version Information"
	@echo "=========================="
	@echo "Python: $$($(VENV_PYTHON) --version)"
	@echo "Pip: $$($(VENV_PIP) --version)"
	@echo "Project: MS11 (Project MorningStar)"
	@echo "Location: $$(pwd)"

status: ## Show project status
	@echo "📊 MS11 Project Status"
	@echo "====================="
	@echo "Virtual Environment: $$(if [ -d '$(VENV_PATH)' ]; then echo '✅ Present'; else echo '❌ Missing'; fi)"
	@echo "Dependencies: $$(if [ -f 'requirements.txt' ]; then echo '✅ Found'; else echo '❌ Missing'; fi)"
	@echo "Tests: $$(if [ -d 'tests' ]; then echo '✅ Present'; else echo '❌ Missing'; fi)"
	@echo "Git: $$(if [ -d '.git' ]; then echo '✅ Repository'; else echo '❌ Not a git repo'; fi)"

# Docker commands
docker-build: ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker-compose build

docker-up: ## Start Docker services
	@echo "🐳 Starting Docker services..."
	docker-compose up -d

docker-down: ## Stop Docker services
	@echo "🐳 Stopping Docker services..."
	docker-compose down

docker-logs: ## Show Docker logs
	@echo "🐳 Showing Docker logs..."
	docker-compose logs -f

# Git helpers
git-status: ## Show git status with enhancements
	@echo "📋 Git Status"
	@echo "============"
	@git status --porcelain | head -20
	@echo ""
	@git log --oneline -5

commit: ## Quick commit with message (usage: make commit MSG="your message")
	@if [ -z "$(MSG)" ]; then \
		echo "❌ Usage: make commit MSG=\"your commit message\""; \
		exit 1; \
	fi
	git add -A
	git commit -m "$(MSG)"
	@echo "✅ Committed: $(MSG)"

# Development workflow shortcuts
fresh-start: clean setup quick-test ## Complete fresh start (clean, setup, test)

hotfix: format lint test ## Quick hotfix workflow (format, lint, test)

release-check: clean install test lint security ## Pre-release checks

# Platform-specific commands
ifeq ($(OS),Windows_NT)
activate: ## Show activation command for Windows
	@echo "To activate virtual environment on Windows:"
	@echo "$(VENV_PATH)\\Scripts\\activate"
else
activate: ## Show activation command for Unix-like systems
	@echo "To activate virtual environment:"
	@echo "source $(VENV_PATH)/bin/activate"
endif