SHELL := /bin/bash


.PHONY: ruff
ruff: ## Run ruff to check code style
	ruff check .

.PHONY: mypy
mypy: ## Run mypy to check for type errors
	mypy . --config-file pyproject.toml

.PHONY: style
style: ## Run ruff and mypy to check code style
	uv run ruff check . --fix
	uv run mypy . --config-file pyproject.toml

.PHONY: clean
clean: ## Clean up the project
	find . -type f -name "*.DS_Store" -ls -delete || true
	find . | grep -E "(__pycache__|\.pyc|\.pyo)" | xargs rm -rf || true
	find . | grep -E ".pytest_cache" | xargs rm -rf || true
	find . | grep -E ".mypy_cache" | xargs rm -rf || true
	find . | grep -E ".ruff_cache" | xargs rm -rf || true
	find . | grep -E ".ipynb_checkpoints" | xargs rm -rf || true
	find . | grep -E "dist" | xargs rm -rf || true
	rm -rf .coverage || true