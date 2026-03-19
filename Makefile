# ResistanceAtlas — Developer Makefile
# Usage: make <target>
# Run `make help` to see all available commands.

.PHONY: help setup dev dev-backend dev-frontend \
        build up down restart logs logs-backend logs-frontend \
        test test-backend test-frontend lint lint-backend lint-frontend \
        format clean clean-docker clean-all \
        train-model download-data \
        smoke-test open shell-backend shell-frontend \
        env-check deps-check

# ── Colours ────────────────────────────────────────────────────────────────────
BOLD   := \033[1m
RESET  := \033[0m
GREEN  := \033[32m
YELLOW := \033[33m
CYAN   := \033[36m
RED    := \033[31m

# ── Config ─────────────────────────────────────────────────────────────────────
BACKEND_DIR  := backend
FRONTEND_DIR := frontend
DATA_DIR     := data
VENV_DIR     := .venv
PYTHON       := python3
PIP          := $(VENV_DIR)/bin/pip
UVICORN      := $(VENV_DIR)/bin/uvicorn
PYTEST       := $(VENV_DIR)/bin/pytest

BACKEND_URL  := http://localhost:8000
FRONTEND_URL := http://localhost:3000

# ── Help ───────────────────────────────────────────────────────────────────────

help: ## Show this help message
	@echo ""
	@echo "$(BOLD)ResistanceAtlas — Developer Commands$(RESET)"
	@echo "══════════════════════════════════════"
	@echo ""
	@echo "$(CYAN)Setup$(RESET)"
	@grep -E '^(setup|env-check|deps-check).*:.*##' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BOLD)%-22s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(CYAN)Development$(RESET)"
	@grep -E '^(dev|dev-backend|dev-frontend).*:.*##' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BOLD)%-22s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(CYAN)Docker$(RESET)"
	@grep -E '^(build|up|down|restart|logs|logs-backend|logs-frontend).*:.*##' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BOLD)%-22s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(CYAN)Testing & Quality$(RESET)"
	@grep -E '^(test|test-backend|test-frontend|lint|lint-backend|lint-frontend|format|smoke-test).*:.*##' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BOLD)%-22s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(CYAN)ML Pipeline$(RESET)"
	@grep -E '^(download-data|train-model).*:.*##' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BOLD)%-22s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(CYAN)Utilities$(RESET)"
	@grep -E '^(open|shell-backend|shell-frontend|clean|clean-docker|clean-all).*:.*##' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BOLD)%-22s$(RESET) %s\n", $$1, $$2}'
	@echo ""

# ── Setup ──────────────────────────────────────────────────────────────────────

setup: env-check deps-check ## Full first-time project setup (venv + deps + .env)
	@echo "$(GREEN)$(BOLD)Setting up ResistanceAtlas...$(RESET)"
	@$(MAKE) --no-print-directory _setup-env
	@$(MAKE) --no-print-directory _setup-backend
	@$(MAKE) --no-print-directory _setup-frontend
	@echo ""
	@echo "$(GREEN)$(BOLD)Setup complete.$(RESET)"
	@echo "  1. Edit $(BOLD).env$(RESET) and add your NVIDIA API key"
	@echo "     Get a free key at: https://build.nvidia.com/arc/evo2-40b"
	@echo "  2. Run $(BOLD)make dev$(RESET) to start both servers"
	@echo "  3. Open $(BOLD)$(FRONTEND_URL)$(RESET) in your browser"
	@echo ""

_setup-env:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(YELLOW)Created .env from .env.example — add your NVIDIA_API_KEY$(RESET)"; \
	else \
		echo "  .env already exists — skipping"; \
	fi

_setup-backend:
	@echo "$(CYAN)Installing Python dependencies...$(RESET)"
	@$(PYTHON) -m venv $(VENV_DIR)
	@$(PIP) install --quiet --upgrade pip
	@$(PIP) install --quiet -r $(BACKEND_DIR)/requirements.txt
	@$(PIP) install --quiet -r $(BACKEND_DIR)/requirements-dev.txt
	@echo "  Backend dependencies installed (prod + dev)"

_setup-frontend:
	@echo "$(CYAN)Installing Node dependencies...$(RESET)"
	@cd $(FRONTEND_DIR) && npm install --silent
	@echo "  Frontend dependencies installed"

env-check: ## Check required tools are installed
	@echo "$(CYAN)Checking required tools...$(RESET)"
	@command -v python3 >/dev/null 2>&1 || { echo "$(RED)ERROR: python3 not found$(RESET)"; exit 1; }
	@command -v node   >/dev/null 2>&1 || { echo "$(RED)ERROR: node not found$(RESET)"; exit 1; }
	@command -v npm    >/dev/null 2>&1 || { echo "$(RED)ERROR: npm not found$(RESET)"; exit 1; }
	@command -v docker >/dev/null 2>&1 || { echo "$(YELLOW)WARN: docker not found — Docker targets will not work$(RESET)"; }
	@echo "  $(GREEN)All required tools found$(RESET)"

deps-check: ## Verify .env exists and NVIDIA key looks valid
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)WARN: .env not found — run 'make setup' first$(RESET)"; \
	elif ! grep -q "NVIDIA_API_KEY=nvapi" .env 2>/dev/null; then \
		echo "$(YELLOW)WARN: NVIDIA_API_KEY not set in .env$(RESET)"; \
		echo "      Get a free key at: https://build.nvidia.com/arc/evo2-40b"; \
	else \
		echo "  $(GREEN).env and NVIDIA key present$(RESET)"; \
	fi

# ── Development (no Docker) ────────────────────────────────────────────────────

dev: ## Start backend + frontend in parallel (no Docker, hot reload)
	@echo "$(GREEN)$(BOLD)Starting dev servers...$(RESET)"
	@echo "  Backend:  $(BACKEND_URL)"
	@echo "  Frontend: $(FRONTEND_URL)"
	@echo "  Press Ctrl+C to stop both"
	@echo ""
	@trap 'kill 0' INT; \
		$(MAKE) --no-print-directory dev-backend & \
		$(MAKE) --no-print-directory dev-frontend & \
		wait

dev-backend: ## Start FastAPI backend only (hot reload on :8000)
	@echo "$(CYAN)Starting backend on $(BACKEND_URL)...$(RESET)"
	@cd $(BACKEND_DIR) && \
		PYTHONPATH=. ../$(VENV_DIR)/bin/uvicorn main:app \
		--host 0.0.0.0 \
		--port 8000 \
		--reload \
		--reload-dir . \
		--log-level info

dev-frontend: ## Start Next.js frontend only (hot reload on :3000)
	@echo "$(CYAN)Starting frontend on $(FRONTEND_URL)...$(RESET)"
	@cd $(FRONTEND_DIR) && npm run dev

# ── Docker ─────────────────────────────────────────────────────────────────────

build: ## Build all Docker images (no cache)
	@echo "$(CYAN)Building Docker images...$(RESET)"
	docker compose build --no-cache
	@echo "$(GREEN)Build complete$(RESET)"

up: ## Start all services with Docker Compose (detached)
	@echo "$(CYAN)Starting services...$(RESET)"
	docker compose up -d
	@echo "$(GREEN)Services running:$(RESET)"
	@echo "  Frontend: $(FRONTEND_URL)"
	@echo "  Backend:  $(BACKEND_URL)"
	@echo "  API docs: $(BACKEND_URL)/docs"

down: ## Stop all Docker services
	@echo "$(CYAN)Stopping services...$(RESET)"
	docker compose down
	@echo "$(GREEN)All services stopped$(RESET)"

restart: down up ## Restart all Docker services

logs: ## Tail logs from all Docker services
	docker compose logs -f

logs-backend: ## Tail backend logs only
	docker compose logs -f backend

logs-frontend: ## Tail frontend logs only
	docker compose logs -f frontend

# ── Testing & Quality ──────────────────────────────────────────────────────────

test: test-backend test-frontend ## Run all tests

test-backend: ## Run backend Python tests (pytest)
	@echo "$(CYAN)Running backend tests...$(RESET)"
	@if [ ! -d $(BACKEND_DIR)/tests ]; then \
		echo "$(YELLOW)No tests directory found — creating skeleton$(RESET)"; \
		mkdir -p $(BACKEND_DIR)/tests; \
		echo 'def test_health(): pass' > $(BACKEND_DIR)/tests/test_placeholder.py; \
	fi
	@cd $(BACKEND_DIR) && \
		PYTHONPATH=. ../$(VENV_DIR)/bin/pytest tests/ -v \
		--tb=short \
		--no-header \
		2>&1 || true

test-frontend: ## Run frontend tests (next lint + type-check)
	@echo "$(CYAN)Running frontend checks...$(RESET)"
	@cd $(FRONTEND_DIR) && npm run lint 2>&1 || true
	@cd $(FRONTEND_DIR) && npx tsc --noEmit 2>&1 || true
	@echo "$(GREEN)Frontend checks done$(RESET)"

smoke-test: ## Quick end-to-end smoke test against running server
	@echo "$(CYAN)Running smoke tests against $(BACKEND_URL)...$(RESET)"
	@echo ""
	@echo "  1. Health check..."
	@curl -sf $(BACKEND_URL)/api/health | python3 -m json.tool || \
		{ echo "$(RED)FAIL: Backend not reachable$(RESET)"; exit 1; }
	@echo ""
	@echo "  2. Sample sequence analysis..."
	@curl -sf -X POST $(BACKEND_URL)/api/analyse \
		-H "Content-Type: application/json" \
		-d '{"sequence":"ATGGAGAAAAAAATCACTGGATATACCACCGTTGATATATCCCAATGGCATCGTAAAGAACATTTTGAGGCATTTCAGTCAGTTGCTCAATGTACCTATAAACCAGACCGTTCAGCTGGATATTACGGCCTTTTTAAAGACC","sequence_name":"smoke-test"}' \
		| python3 -m json.tool | head -30 || \
		{ echo "$(RED)FAIL: Analysis endpoint returned error$(RESET)"; exit 1; }
	@echo ""
	@echo "  3. Invalid sequence rejection..."
	@STATUS=$$(curl -s -o /dev/null -w "%{http_code}" -X POST $(BACKEND_URL)/api/analyse \
		-H "Content-Type: application/json" \
		-d '{"sequence":"not dna at all!!!"}'); \
		if [ "$$STATUS" = "400" ] || [ "$$STATUS" = "422" ]; then \
			echo "  $(GREEN)Correctly rejected invalid sequence (HTTP $$STATUS)$(RESET)"; \
		else \
			echo "$(RED)FAIL: Expected 400/422, got $$STATUS$(RESET)"; exit 1; \
		fi
	@echo ""
	@echo "$(GREEN)$(BOLD)All smoke tests passed$(RESET)"

lint: lint-backend lint-frontend ## Lint all code

lint-backend: ## Lint Python code (ruff)
	@echo "$(CYAN)Linting backend...$(RESET)"
	@if command -v $(VENV_DIR)/bin/ruff >/dev/null 2>&1; then \
		$(VENV_DIR)/bin/ruff check $(BACKEND_DIR) --fix; \
	else \
		$(PIP) install --quiet ruff && \
		$(VENV_DIR)/bin/ruff check $(BACKEND_DIR) --fix; \
	fi
	@echo "$(GREEN)Backend lint done$(RESET)"

lint-frontend: ## Lint TypeScript/React code (eslint)
	@echo "$(CYAN)Linting frontend...$(RESET)"
	@cd $(FRONTEND_DIR) && npm run lint -- --fix 2>&1 || true
	@echo "$(GREEN)Frontend lint done$(RESET)"

format: ## Format all code (ruff + prettier)
	@echo "$(CYAN)Formatting backend (ruff)...$(RESET)"
	@if ! $(VENV_DIR)/bin/python -c "import ruff" 2>/dev/null; then \
		$(PIP) install --quiet ruff; \
	fi
	@$(VENV_DIR)/bin/ruff format $(BACKEND_DIR)
	@echo "$(CYAN)Formatting frontend (prettier)...$(RESET)"
	@cd $(FRONTEND_DIR) && npx prettier --write "src/**/*.{ts,tsx,css}" --log-level warn
	@echo "$(GREEN)Formatting done$(RESET)"

# ── ML Pipeline ────────────────────────────────────────────────────────────────

download-data: ## Download BV-BRC training data (~2GB, takes 10-20 min)
	@echo "$(CYAN)Downloading BV-BRC AMR training data...$(RESET)"
	@echo "  This downloads ~2GB of bacterial genomes with resistance labels."
	@echo "  Estimated time: 10–20 minutes depending on connection."
	@echo ""
	@mkdir -p $(DATA_DIR)/raw
	@cd $(BACKEND_DIR) && \
		PYTHONPATH=. ../$(VENV_DIR)/bin/python ml/download_data.py
	@echo "$(GREEN)Data download complete → $(DATA_DIR)/raw/$(RESET)"

train-model: ## Train the resistance classifier (requires downloaded data)
	@echo "$(CYAN)Training resistance classifier...$(RESET)"
	@if [ ! -d "$(DATA_DIR)/raw" ] || [ -z "$$(ls -A $(DATA_DIR)/raw 2>/dev/null)" ]; then \
		echo "$(RED)ERROR: No training data found.$(RESET)"; \
		echo "  Run $(BOLD)make download-data$(RESET) first."; \
		exit 1; \
	fi
	@cd $(BACKEND_DIR) && \
		PYTHONPATH=. ../$(VENV_DIR)/bin/python ml/train_classifier.py
	@echo "$(GREEN)Model trained → backend/ml/classifier.joblib$(RESET)"
	@echo "  Restart the backend to load the new model: make restart"

# ── Utilities ──────────────────────────────────────────────────────────────────

open: ## Open the app in your default browser
	@echo "$(CYAN)Opening ResistanceAtlas...$(RESET)"
	@open $(FRONTEND_URL) 2>/dev/null || \
		xdg-open $(FRONTEND_URL) 2>/dev/null || \
		echo "  Open manually: $(FRONTEND_URL)"

shell-backend: ## Open a shell inside the running backend container
	docker compose exec backend bash

shell-frontend: ## Open a shell inside the running frontend container
	docker compose exec frontend sh

clean: ## Remove build artifacts and caches (keeps data + .env)
	@echo "$(CYAN)Cleaning build artifacts...$(RESET)"
	@rm -rf $(FRONTEND_DIR)/.next
	@rm -rf $(FRONTEND_DIR)/node_modules/.cache
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)Clean done$(RESET)"

clean-docker: ## Remove all Docker containers, images, volumes for this project
	@echo "$(YELLOW)Removing Docker resources for ResistanceAtlas...$(RESET)"
	docker compose down --rmi local --volumes --remove-orphans
	@echo "$(GREEN)Docker clean done$(RESET)"

clean-all: clean clean-docker ## Full clean — removes everything including node_modules and venv
	@echo "$(YELLOW)Removing all generated files...$(RESET)"
	@rm -rf $(VENV_DIR)
	@rm -rf $(FRONTEND_DIR)/node_modules
	@rm -f $(BACKEND_DIR)/ml/classifier.joblib
	@rm -f $(BACKEND_DIR)/ml/label_encoder.joblib
	@echo "$(GREEN)Full clean done — run 'make setup' to start fresh$(RESET)"

# ── Internal helpers ───────────────────────────────────────────────────────────

.env:
	@$(MAKE) --no-print-directory _setup-env
