.DEFAULT_GOAL := help
PY ?= python3
VENV ?= .venv
BIN := $(VENV)/bin

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

$(BIN)/activate:
	$(PY) -m venv $(VENV)

.PHONY: dev
dev: $(BIN)/activate ## Create venv, install deps, generate protos, install git hooks
	$(BIN)/pip install -U pip
	$(BIN)/pip install -e ".[dev]"
	$(MAKE) proto
	$(BIN)/pre-commit install

.PHONY: proto
proto: ## Generate Python code from proto/
	$(BIN)/python -m grpc_tools.protoc -I proto \
		--python_out=src --pyi_out=src --grpc_python_out=src \
		proto/cellpulse/v1/telemetry.proto

.PHONY: lint
lint: ## Ruff lint + format check + mypy
	$(BIN)/ruff check .
	$(BIN)/ruff format --check .
	$(BIN)/mypy src

.PHONY: fmt
fmt: ## Auto-format code
	$(BIN)/ruff check --fix .
	$(BIN)/ruff format .

.PHONY: test
test: ## Run tests with coverage
	$(BIN)/pytest

.PHONY: up
up: ## Start the full stack with docker compose
	docker compose -f deploy/docker-compose.yml up --build -d

.PHONY: down
down: ## Stop the stack
	docker compose -f deploy/docker-compose.yml down -v

.PHONY: logs
logs: ## Tail stack logs
	docker compose -f deploy/docker-compose.yml logs -f
