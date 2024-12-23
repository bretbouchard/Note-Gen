.PHONY: test clean install

install:
	pip install -e ".[dev]"

test:
	pytest -v

coverage:
	pytest --cov=src --cov-report=term-missing

clean:
	rm -rf .pytest_cache .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +