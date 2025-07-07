.PHONY: install test validate

install:
	pip install -r requirements.txt
	pip install -r requirements-test.txt

test:
	pytest -q --tb=short

validate:
	@echo "\n🔍 Running QA validation script..."
	@python codex_validation_check.py
	@echo "\n🧪 Running full test suite..."
	@pytest -q --tb=short
