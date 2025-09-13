# ScottLMS Makefile
# This Makefile provides convenient commands for development, testing, and deployment

.PHONY: help install dev build test clean deploy infra status logs shell format lint security-check

# Default target
.DEFAULT_GOAL := help

# Variables
PROJECT_NAME := scottlms
AWS_REGION := us-west-2
ENVIRONMENT := production
IMAGE_TAG := latest
PYTHON := python3
PIP := pip3

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

##@ Help
help: ## Display this help message
	@echo "$(BLUE)ScottLMS - Learning Management System$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make $(BLUE)<target>$(NC)\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development Setup
install: ## Install Python dependencies
	@echo "$(GREEN)Installing Python dependencies...$(NC)"
	$(PYTHON) -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt
	@echo "$(GREEN)Dependencies installed successfully!$(NC)"

dev-setup: ## Set up development environment
	@echo "$(GREEN)Setting up development environment...$(NC)"
	@if [ ! -f .env ]; then \
		if [ -f env.example ]; then \
			cp env.example .env; \
			echo "$(YELLOW)Created .env file from env.example. Please update with your values.$(NC)"; \
		else \
			echo "$(YELLOW)Creating basic .env file...$(NC)"; \
			echo "API_V1_STR=/api/v1" > .env; \
			echo "PROJECT_NAME=ScottLMS" >> .env; \
			echo "SECRET_KEY=dev-secret-key-change-in-production" >> .env; \
			echo "MONGODB_URL=mongodb://localhost:27017/scottlms" >> .env; \
			echo "DATABASE_NAME=scottlms" >> .env; \
			echo "ENVIRONMENT=development" >> .env; \
			echo "DEBUG=true" >> .env; \
			echo "LOG_LEVEL=info" >> .env; \
		fi; \
	fi
	@echo "$(GREEN)Development environment setup complete!$(NC)"

dev: ## Start development environment with Docker Compose
	@echo "$(GREEN)Starting development environment...$(NC)"
	docker-compose up -d
	@echo "$(YELLOW)Waiting for all services to be healthy...$(NC)"
	@timeout 120 bash -c 'until docker-compose ps | grep -q "healthy"; do sleep 2; done' || echo "$(RED)Warning: Some services may not be fully healthy yet$(NC)"
	@echo "$(GREEN)Development environment started!$(NC)"
	@echo "$(BLUE)Access URLs:$(NC)"
	@echo "  • API: http://localhost"
	@echo "  • API Docs: http://localhost/docs"
	@echo "  • MongoDB Express: http://localhost:8081 (admin/admin)"

dev-logs: ## View development environment logs
	docker-compose logs -f

dev-stop: ## Stop development environment
	@echo "$(GREEN)Stopping development environment...$(NC)"
	docker-compose down

dev-restart: ## Restart development environment
	@echo "$(GREEN)Restarting development environment...$(NC)"
	docker-compose restart

dev-health: ## Check health status of all services
	@echo "$(BLUE)=== ScottLMS Health Status ===$(NC)"
	@echo ""
	@echo "$(YELLOW)Container Status:$(NC)"
	@docker-compose ps
	@echo ""
	@echo "$(YELLOW)Detailed Health Checks:$(NC)"
	@echo ""
	@echo "$(BLUE)1. API Service (FastAPI):$(NC)"
	@if curl -s http://localhost:8000/health 2>/dev/null | grep -q "healthy"; then \
		echo "   $(GREEN)✅ API is healthy$(NC)"; \
		curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo "   $(GREEN)✅ API responding$(NC)"; \
	else \
		echo "   $(RED)❌ API health check failed$(NC)"; \
	fi
	@echo ""
	@echo "$(BLUE)2. MongoDB Database:$(NC)"
	@if docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')" 2>/dev/null | grep -q "ok.*1"; then \
		echo "   $(GREEN)✅ MongoDB is healthy$(NC)"; \
		echo "   $(GREEN)   Connection: Active$(NC)"; \
		echo "   $(GREEN)   Database: scottlms$(NC)"; \
	else \
		echo "   $(RED)❌ MongoDB health check failed$(NC)"; \
	fi
	@echo ""
	@echo "$(BLUE)3. Mongo Express (Web UI):$(NC)"
	@if curl -s http://localhost:8081 2>/dev/null | grep -q "Unauthorized\|mongo-express"; then \
		echo "   $(GREEN)✅ Mongo Express is healthy$(NC)"; \
		echo "   $(GREEN)   Web Interface: http://localhost:8081$(NC)"; \
		echo "   $(GREEN)   Credentials: admin/admin$(NC)"; \
	else \
		echo "   $(RED)❌ Mongo Express health check failed$(NC)"; \
	fi
	@echo ""
	@echo "$(BLUE)4. Frontend (Streamlit):$(NC)"
	@if curl -s http://localhost 2>/dev/null | grep -q "Streamlit\|ScottLMS"; then \
		echo "   $(GREEN)✅ Frontend is healthy$(NC)"; \
		echo "   $(GREEN)   Web Interface: http://localhost$(NC)"; \
		echo "   $(GREEN)   Dashboard: Ready$(NC)"; \
	else \
		echo "   $(RED)❌ Frontend health check failed$(NC)"; \
	fi
	@echo ""
	@echo "$(YELLOW)Service URLs:$(NC)"
	@echo "   • Frontend: http://localhost"
	@echo "   • API: http://localhost:8000"
	@echo "   • API Docs: http://localhost:8000/docs"
	@echo "   • MongoDB Express: http://localhost:8081"
	@echo ""

##@ Frontend
frontend: ## Start Streamlit frontend
	@echo "$(BLUE)Starting Streamlit frontend...$(NC)"
	@echo "$(YELLOW)Frontend will be available at: http://localhost:8501$(NC)"
	@echo "$(YELLOW)Press Ctrl+C to stop$(NC)"
	@streamlit run frontend.py

frontend-install: ## Install frontend dependencies
	@echo "$(BLUE)Installing frontend dependencies...$(NC)"
	@pip install streamlit requests

##@ Building & Testing
build: ## Build Docker image
	@echo "$(GREEN)Building Docker image...$(NC)"
	docker build -t $(PROJECT_NAME)-api:$(IMAGE_TAG) .
	@echo "$(GREEN)Docker image built successfully!$(NC)"

test: ## Run tests
	@echo "$(GREEN)Running tests...$(NC)"
	. venv/bin/activate && pytest -v

test-coverage: ## Run tests with coverage report
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	. venv/bin/activate && pytest --cov=app --cov-report=html --cov-report=term

test-watch: ## Run tests in watch mode
	@echo "$(GREEN)Running tests in watch mode...$(NC)"
	. venv/bin/activate && pytest-watch

##@ Code Quality
format: ## Format code with black and isort
	@echo "$(GREEN)Formatting code...$(NC)"
	. venv/bin/activate && black app/ tests/
	. venv/bin/activate && isort app/ tests/
	@echo "$(GREEN)Code formatted successfully!$(NC)"

lint: ## Lint code with flake8
	@echo "$(GREEN)Linting code...$(NC)"
	. venv/bin/activate && flake8 app/ tests/

lint-fix: ## Fix linting issues automatically
	@echo "$(GREEN)Fixing linting issues...$(NC)"
	. venv/bin/activate && autopep8 --in-place --recursive app/ tests/

security-check: ## Run security checks
	@echo "$(GREEN)Running security checks...$(NC)"
	. venv/bin/activate && bandit -r app/
	. venv/bin/activate && safety check

quality: format lint security-check ## Run all code quality checks

##@ Database
db-shell: ## Connect to MongoDB shell
	docker-compose exec mongodb mongosh scottlms

db-reset: ## Reset database (WARNING: This will delete all data)
	@echo "$(YELLOW)WARNING: This will delete all data in the database!$(NC)"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ]
	docker-compose exec mongodb mongosh scottlms --eval "db.dropDatabase()"
	@echo "$(GREEN)Database reset complete!$(NC)"

db-backup: ## Backup database
	@echo "$(GREEN)Creating database backup...$(NC)"
	mkdir -p backups
	docker-compose exec mongodb mongodump --db scottlms --out /tmp/backup
	docker cp $$(docker-compose ps -q mongodb):/tmp/backup ./backups/backup-$$(date +%Y%m%d-%H%M%S)
	@echo "$(GREEN)Database backup created!$(NC)"

##@ Infrastructure
infra-init: ## Initialize Terraform
	@echo "$(GREEN)Initializing Terraform...$(NC)"
	cd terraform && terraform init

infra-plan: ## Plan Terraform deployment
	@echo "$(GREEN)Planning Terraform deployment...$(NC)"
	cd terraform && terraform plan -var="environment=$(ENVIRONMENT)"

infra-apply: ## Apply Terraform configuration
	@echo "$(GREEN)Applying Terraform configuration...$(NC)"
	cd terraform && terraform apply -var="environment=$(ENVIRONMENT)" -auto-approve

infra-destroy: ## Destroy Terraform infrastructure (WARNING: This will delete all resources)
	@echo "$(RED)WARNING: This will destroy all infrastructure!$(NC)"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ]
	cd terraform && terraform destroy -var="environment=$(ENVIRONMENT)" -auto-approve

infra-output: ## Show Terraform outputs
	cd terraform && terraform output

##@ Deployment
deploy-build: ## Build and push Docker image to ECR
	@echo "$(GREEN)Building and pushing Docker image...$(NC)"
	@ECR_REPO_URL=$$(aws ecr describe-repositories --repository-names "$(PROJECT_NAME)-api" --region $(AWS_REGION) --query 'repositories[0].repositoryUri' --output text 2>/dev/null); \
	if [ "$$ECR_REPO_URL" = "None" ] || [ -z "$$ECR_REPO_URL" ]; then \
		echo "$(RED)ECR repository not found. Please run 'make infra-apply' first.$(NC)"; \
		exit 1; \
	fi; \
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $$ECR_REPO_URL; \
	docker build -t $(PROJECT_NAME)-api:$(IMAGE_TAG) .; \
	docker tag $(PROJECT_NAME)-api:$(IMAGE_TAG) $$ECR_REPO_URL:$(IMAGE_TAG); \
	docker push $$ECR_REPO_URL:$(IMAGE_TAG); \
	echo "$(GREEN)Image pushed to $$ECR_REPO_URL:$(IMAGE_TAG)$(NC)"

deploy-k8s: ## Deploy application to Kubernetes
	@echo "$(GREEN)Deploying to Kubernetes...$(NC)"
	aws eks update-kubeconfig --region $(AWS_REGION) --name $(PROJECT_NAME)-$(ENVIRONMENT)
	kubectl apply -k k8s/
	@echo "$(GREEN)Waiting for deployment to be ready...$(NC)"
	kubectl wait --for=condition=available --timeout=300s deployment/scottlms-api -n scottlms
	@echo "$(GREEN)Deployment complete!$(NC)"

deploy: deploy-build deploy-k8s ## Full deployment (build + deploy)

##@ Monitoring & Debugging
status: ## Show deployment status
	@echo "$(BLUE)Kubernetes Status:$(NC)"
	kubectl get pods -n scottlms
	@echo ""
	@echo "$(BLUE)Services:$(NC)"
	kubectl get services -n scottlms
	@echo ""
	@echo "$(BLUE)Ingress:$(NC)"
	kubectl get ingress -n scottlms

logs: ## View application logs
	kubectl logs -f deployment/scottlms-api -n scottlms

logs-prev: ## View previous application logs
	kubectl logs --previous deployment/scottlms-api -n scottlms

shell: ## Get shell access to running pod
	kubectl exec -it deployment/scottlms-api -n scottlms -- /bin/bash

port-forward: ## Port forward to access application locally
	kubectl port-forward service/scottlms-api-service 8000:80 -n scottlms

##@ CI/CD
ci-test: ## Run CI tests locally
	@echo "$(GREEN)Running CI tests locally...$(NC)"
	. venv/bin/activate && pytest --cov=app --cov-report=xml --cov-report=html --junitxml=pytest-report.xml
	. venv/bin/activate && flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics
	. venv/bin/activate && black --check app/
	. venv/bin/activate && isort --check-only app/
	. venv/bin/activate && bandit -r app/
	. venv/bin/activate && safety check

ci-docker: ## Test Docker build locally
	@echo "$(GREEN)Testing Docker build...$(NC)"
	docker build -t scottlms-api:test .
	docker run -d --name ci-test -p 8000:8000 scottlms-api:test
	sleep 10
	curl -f http://localhost:8000/health || exit 1
	docker stop ci-test && docker rm ci-test

ci-terraform: ## Validate Terraform configuration
	@echo "$(GREEN)Validating Terraform...$(NC)"
	cd terraform && terraform fmt -check -recursive
	cd terraform && terraform init -backend=false
	cd terraform && terraform validate
	cd terraform && terraform plan -var="environment=test" -var="project_name=scottlms-test"

ci-k8s: ## Validate Kubernetes manifests
	@echo "$(GREEN)Validating Kubernetes manifests...$(NC)"
	kubectl apply --dry-run=client -k k8s/

ci-all: ci-test ci-docker ci-terraform ci-k8s ## Run all CI checks locally

##@ Utilities
clean: ## Clean up Docker images and containers
	@echo "$(GREEN)Cleaning up Docker resources...$(NC)"
	docker system prune -f
	docker image prune -f

clean-all: ## Clean up everything (Docker, Python cache, etc.)
	@echo "$(GREEN)Cleaning up all resources...$(NC)"
	docker system prune -af
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache/ htmlcov/ .coverage

update-deps: ## Update Python dependencies
	@echo "$(GREEN)Updating dependencies...$(NC)"
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt --upgrade

check-deps: ## Check for outdated dependencies
	@echo "$(GREEN)Checking for outdated dependencies...$(NC)"
	. venv/bin/activate && pip list --outdated

##@ Quick Commands (Combined Workflows)
quick-start: dev-setup install dev ## Quick start for new developers
	@echo "$(GREEN)Quick start complete!$(NC)"
	@echo "$(BLUE)Your development environment is ready!$(NC)"

quick-deploy: infra-apply deploy ## Quick deployment to production
	@echo "$(GREEN)Quick deployment complete!$(NC)"

##@ Super Commands (One Command Does Everything)
setup: dev-setup install ## Complete development setup (env + deps)
	@echo "$(GREEN)Development setup complete!$(NC)"

start: dev ## Start development environment
	@echo "$(GREEN)Development environment started!$(NC)"

stop: dev-stop ## Stop development environment
	@echo "$(GREEN)Development environment stopped!$(NC)"

destroy: dev-stop ## Destroy all development resources (containers, volumes, networks)
	@echo "$(YELLOW)Destroying all development resources...$(NC)"
	docker-compose down -v --remove-orphans
	docker system prune -f
	@echo "$(GREEN)All development resources destroyed!$(NC)"

restart: dev-stop dev ## Restart development environment
	@echo "$(GREEN)Development environment restarted!$(NC)"

test-all: test test-coverage ## Run all tests with coverage
	@echo "$(GREEN)All tests completed!$(NC)"

quality-all: format lint security-check ## Run all code quality checks
	@echo "$(GREEN)All quality checks completed!$(NC)"

build-all: build test quality-all ## Build, test, and quality check
	@echo "$(GREEN)Build pipeline completed!$(NC)"

deploy-all: infra-apply deploy-build deploy-k8s ## Full deployment pipeline
	@echo "$(GREEN)Full deployment completed!$(NC)"

infra-all: infra-init infra-plan infra-apply ## Complete infrastructure setup
	@echo "$(GREEN)Infrastructure setup completed!$(NC)"

monitor: status logs ## Show status and follow logs
	@echo "$(GREEN)Monitoring started!$(NC)"

clean-dev: dev-stop clean ## Clean development environment
	@echo "$(GREEN)Development environment cleaned!$(NC)"

reset: dev-stop db-reset dev ## Reset everything and restart
	@echo "$(GREEN)Environment reset complete!$(NC)"

##@ Information
info: ## Show project information
	@echo "$(BLUE)ScottLMS - Learning Management System$(NC)"
	@echo ""
	@echo "$(YELLOW)Project Structure:$(NC)"
	@echo "  • FastAPI Backend: app/"
	@echo "  • Kubernetes Manifests: k8s/"
	@echo "  • Infrastructure: terraform/"
	@echo "  • Scripts: scripts/"
	@echo ""
	@echo "$(YELLOW)Key URLs:$(NC)"
	@echo "  • Frontend: http://localhost"
	@echo "  • API: http://localhost:8000"
	@echo "  • API Docs: http://localhost:8000/docs"
	@echo "  • MongoDB Express: http://localhost:8081"
	@echo ""
	@echo "$(YELLOW)Super Commands (One Command Does Everything):$(NC)"
	@echo "  • make setup        - Complete development setup"
	@echo "  • make start        - Start development environment"
	@echo "  • make stop         - Stop development environment"
	@echo "  • make destroy      - Destroy all development resources"
	@echo "  • make test-all     - Run all tests with coverage"
	@echo "  • make quality-all  - Run all code quality checks"
	@echo "  • make build-all    - Build, test, and quality check"
	@echo "  • make deploy-all   - Full deployment pipeline"
	@echo "  • make monitor      - Show status and follow logs"
	@echo "  • make reset        - Reset everything and restart"
	@echo ""
	@echo "$(YELLOW)Common Commands:$(NC)"
	@echo "  • make dev          - Start development environment"
	@echo "  • make test         - Run tests"
	@echo "  • make deploy       - Deploy to production"
	@echo "  • make status       - Check deployment status"
