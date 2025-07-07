.PHONY: install test validate validate-batch-044 validate-batch-045

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

validate-batch-044:
	python codex_validation_batch_044.py

validate-batch-045:
	python codex_validation_batch_045.py
