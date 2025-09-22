# ScottLMS - Simplified Makefile
# Essential commands for development, testing, and deployment

.PHONY: help install dev test clean format lint build deploy

# Default target
.DEFAULT_GOAL := help

# Variables
PROJECT_NAME := scottlms
PYTHON := python3
PIP := pip3

# Colors for output
RED := \033[0;31m
YELLOW := \033[1;33m
GREEN := \033[0;32m
BLUE := \033[0;34m
NC := \033[0m # No Color

##@ Help
help: ## Display this help message
	@echo "$(BLUE)ScottLMS - Simplified Learning Management System$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make $(BLUE)<target>$(NC)\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development Setup
install: ## Install Python dependencies
	@echo "$(GREEN)Installing dependencies...$(NC)"
	$(PYTHON) -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r backend/requirements.txt
	. venv/bin/activate && pip install -r frontend/requirements.txt
	@echo "$(GREEN)Dependencies installed!$(NC)"

setup: ## Complete development setup
	@echo "$(GREEN)Setting up development environment...$(NC)"
	@if [ ! -f .env ]; then \
		if [ -f env.example ]; then \
			cp env.example .env; \
			echo "$(YELLOW)Created .env file from env.example$(NC)"; \
		fi; \
	fi
	@echo "$(GREEN)Setup complete!$(NC)"

##@ Development
build: ## Build development environment with Docker
	@echo "$(GREEN)Building development environment...$(NC)"
	docker-compose build --parallel --no-cache
	@echo "$(GREEN)Development environment built!$(NC)"

start: ## Start development environment with Docker
	@echo "$(GREEN)Starting development environment...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)Development environment started!$(NC)"
	@echo "$(BLUE)Access URLs:$(NC)"
	@echo "  • Frontend: http://localhost"
	@echo "  • API: http://localhost:8000"
	@echo "  • API Docs: http://localhost:8000/docs"
	@echo "  • MongoDB Express: http://localhost:8081 (admin/admin)"

logs: ## View development logs
	docker-compose logs -f

stop: ## Stop development environment
	@echo "$(GREEN)Stopping development environment...$(NC)"
	docker-compose down

restart: stop build start ## Restart development environment

destroy: ## Destroy all development resources (containers, volumes, networks)
	@echo "$(GREEN)Cleaning up everything...$(NC)"
	docker-compose down -v --remove-orphans
	docker rmi -f $(shell docker images -q)
	docker system prune -af
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache/ htmlcov/ .coverage
	@echo "$(GREEN)All development resources destroyed!$(NC)"

push: build ## Push Docker images to Docker Hub
	@echo "$(GREEN)Pushing Docker images to Docker Hub...$(NC)"
	docker-compose push --parallel
	@echo "$(GREEN)Docker images pushed to Docker Hub!$(NC)"

##@ Terraform Commands
infra-init: ## Initialize Terraform
	@echo "$(GREEN)Initializing Terraform...$(NC)"
	terraform -chdir=terraform init
	@echo "$(GREEN)Terraform initialized!$(NC)"

infra-validate: ## Validate Terraform
	@echo "$(GREEN)Validating Terraform...$(NC)"
	terraform -chdir=terraform validate
	@echo "$(GREEN)Terraform validated!$(NC)"

infra-plan: ## Plan Terraform
	@echo "$(GREEN)Planning Terraform...$(NC)"
	terraform -chdir=terraform plan
	@echo "$(GREEN)Terraform planned!$(NC)"

infra-apply: ## Apply Terraform
	@echo "$(GREEN)Applying Terraform...$(NC)"
	terraform -chdir=terraform apply
	@echo "$(GREEN)Terraform applied!$(NC)"

infra-destroy: ## Destroy Terraform
	@echo "$(GREEN)Destroying Terraform...$(NC)"
	terraform -chdir=terraform destroy
	@echo "$(GREEN)Terraform destroyed!$(NC)"

##@ Testing
test: ## Run tests
	@echo "$(GREEN)Running tests...$(NC)"
	python -m pytest backend/ frontend/ -v

test-backend: ## Run backend tests only
	@echo "$(GREEN)Running backend tests...$(NC)"
	python -m pytest backend/ -v

test-frontend: ## Run frontend tests only
	@echo "$(GREEN)Running frontend tests...$(NC)"
	python -m pytest frontend/ -v

test-coverage: ## Run tests with coverage
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	python -m pytest --cov=backend --cov=frontend --cov-report=html --cov-report=term

##@ Code Quality
format: ## Format code with black
	@echo "$(GREEN)Formatting code...$(NC)"
	black backend/ frontend/
	@echo "$(GREEN)Code formatted!$(NC)"

lint: ## Lint code with flake8
	@echo "$(GREEN)Linting code...$(NC)"
	flake8 backend/ frontend/
	@echo "$(GREEN)Linting complete!$(NC)"

lint-fix: ## Fix linting issues
	@echo "$(GREEN)Fixing linting issues...$(NC)"
	autopep8 --in-place --recursive backend/ frontend/
	@echo "$(GREEN)Linting issues fixed!$(NC)"

quality: format lint ## Run all code quality checks

##@ Building & Deployment
build: ## Build Docker images
	@echo "$(GREEN)Building Docker images...$(NC)"
	docker-compose build --parallel --no-cache
	@echo "$(GREEN)Build complete!$(NC)"

##@ Database
db-shell: ## Connect to MongoDB shell
	docker-compose exec mongodb mongosh scottlms

db-reset: ## Reset database (WARNING: deletes all data)
	@echo "$(RED)WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ]
	docker-compose exec mongodb mongosh scottlms --eval "db.dropDatabase()"
	@echo "$(GREEN)Database reset!$(NC)"

test-all: test test-coverage ## Run all tests with coverage
build-all: build test quality ## Build, test, and quality check

##@ Information
status: ## Show development environment status
	@echo "$(BLUE)=== Development Environment Status ===$(NC)"
	@echo ""
	@echo "$(YELLOW)Container Status:$(NC)"
	@docker-compose ps
	@echo ""
	@echo "$(YELLOW)Service URLs:$(NC)"
	@echo "  • Frontend: http://localhost:8501"
	@echo "  • API: http://localhost:8000"
	@echo "  • API Docs: http://localhost:8000/docs"
	@echo "  • MongoDB: mongodb://localhost:27017/scottlms"

info: ## Show project information
	@echo "$(BLUE)ScottLMS - Simplified Learning Management System$(NC)"
	@echo ""
	@echo "$(YELLOW)Project Structure:$(NC)"
	@echo "  • Backend: backend/ (FastAPI)"
	@echo "  • Frontend: frontend/ (Streamlit)"
	@echo "  • Database: MongoDB"
	@echo ""
	@echo "$(YELLOW)Quick Start:$(NC)"
	@echo "  • make setup    - Complete development setup"
	@echo "  • make start    - Start development environment"
	@echo "  • make test     - Run tests"
	@echo "  • make stop     - Stop development environment"
	@echo "  • make destroy  - Destroy all resources"
	@echo ""
	@echo "$(YELLOW)Development:$(NC)"
	@echo "  • make start    - Start with Docker Compose"
	@echo "  • make logs     - View logs"
	@echo "  • make restart  - Restart services"
	@echo ""
	@echo "$(YELLOW)Testing:$(NC)"
	@echo "  • make test           - Run all tests"
	@echo "  • make test-backend   - Backend tests only"
	@echo "  • make test-frontend  - Frontend tests only"
	@echo "  • make test-coverage  - Tests with coverage"
	@echo ""
	@echo "$(YELLOW)Code Quality:$(NC)"
	@echo "  • make format    - Format code"
	@echo "  • make lint      - Lint code"
	@echo "  • make quality   - Format + lint"