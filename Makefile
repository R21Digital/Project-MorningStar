.PHONY: install test validate validate-batch-044 validate-batch-045 validate-batch-046 validate-batch-047 validate-048 validate-049 validate-batch-051

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

validate-batch-046:
	python codex_validation_batch_046.py

validate-batch-047:
	python codex_validation_batch_047.py

validate-048:
	python scripts/codex_validation_batch_048.py

validate-049:
        python scripts/codex_validation_batch_049.py

validate-batch-051:
        python scripts/codex_validation_batch_051.py
