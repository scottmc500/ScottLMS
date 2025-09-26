# ScottLMS - Simplified Makefile
# Essential commands for development, testing, and deployment

.PHONY: help install dev test clean format lint build deploy

# Default target
.DEFAULT_GOAL := help

# Variables
PROJECT_NAME := scottlms
PYTHON := python3
PIP := pip3
TAG ?= abc123
DOCKER_HUB_USERNAME ?= user123
DOCKER_HUB_PASSWORD ?= password123

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

##@ Development
docker-build: ## Build development environment with Docker
	@echo "$(GREEN)Building development environment...$(NC)"
	TAG=$(TAG) docker compose build --parallel --no-cache
	TAG=latest docker compose build --parallel
	@echo "$(GREEN)Development environment built!$(NC)"

docker-start: ## Start development environment with Docker
	@echo "$(GREEN)Starting development environment...$(NC)"
	docker compose up -d
	@echo "$(GREEN)Development environment started!$(NC)"
	@echo "$(BLUE)Access URLs:$(NC)"
	@echo "  • Frontend: http://localhost"
	@echo "  • API: http://localhost:8000"
	@echo "  • API Docs: http://localhost:8000/docs"
	@echo "  • MongoDB Express: http://localhost:8081 (admin/admin)"

docker-logs: ## View development logs
	docker compose logs -f

docker-stop: ## Stop development environment
	@echo "$(GREEN)Stopping development environment...$(NC)"
	docker compose down

docker-restart: docker-stop docker-build docker-start ## Restart development environment

docker-rebuild: docker-destroy docker-build docker-start ## Rebuild development environment

docker-destroy: ## Destroy all development resources (containers, volumes, networks)
	@echo "$(GREEN)Cleaning up everything...$(NC)"
	docker compose down -v --remove-orphans
	docker rmi -f $(shell docker images -q)
	docker system prune -af
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache/ htmlcov/ .coverage
	@echo "$(GREEN)All development resources destroyed!$(NC)"

docker-push: ## Push Docker images to Docker Hub
	@echo "$(GREEN)Pushing Docker images to Docker Hub...$(NC)"
	TAG=$(TAG) docker compose push
	TAG=latest docker compose push
	@echo "$(GREEN)Docker images pushed to Docker Hub!$(NC)"

docker-test-backend: ## Test backend with Docker
	@echo "$(GREEN)Testing backend with Docker (tag: $(TAG))...$(NC)"
	docker run --platform linux/amd64 --rm smchenry2014/scottlms-api:$(TAG) python -m pytest
	@echo "$(GREEN)Backend tests completed!$(NC)"

docker-test-frontend: ## Test frontend with Docker
	@echo "$(GREEN)Testing frontend with Docker (tag: $(TAG))...$(NC)"
	docker run --platform linux/amd64 --rm smchenry2014/scottlms-ui:$(TAG) python -m pytest
	@echo "$(GREEN)Frontend tests completed!$(NC)"

docker-test-all: docker-test-backend docker-test-frontend ## Test all with Docker

##@ Terraform Commands
terraform-init: ## Initialize Terraform
	@echo "$(GREEN)Initializing Terraform...$(NC)"
	terraform -chdir=terraform init
	@echo "$(GREEN)Terraform initialized!$(NC)"

terraform-validate: ## Validate Terraform
	@echo "$(GREEN)Validating Terraform...$(NC)"
	terraform -chdir=terraform validate
	@echo "$(GREEN)Terraform validated!$(NC)"

terraform-set-fmt: ## Set Terraform format
	@echo "$(GREEN)Setting Terraform format...$(NC)"
	terraform -chdir=terraform fmt -recursive
	@echo "$(GREEN)Terraform format set!$(NC)"

terraform-check-fmt: ## Check Terraform format
	@echo "$(GREEN)Checking Terraform format...$(NC)"
	terraform -chdir=terraform fmt -check -recursive
	@echo "$(GREEN)Terraform format checked!$(NC)"

terraform-plan: ## Plan Terraform
	@echo "$(GREEN)Planning Terraform...$(NC)"
	terraform -chdir=terraform plan
	@echo "$(GREEN)Terraform planned!$(NC)"

terraform-apply: ## Apply Terraform
	@echo "$(GREEN)Applying Terraform...$(NC)"
	terraform -chdir=terraform apply -auto-approve
	@echo "$(GREEN)Terraform applied!$(NC)"

terraform-destroy: ## Destroy Terraform
	@echo "$(GREEN)Destroying Terraform...$(NC)"
	terraform -chdir=terraform destroy -auto-approve
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

##@ Kubernetes Commands
k8s-sync-kubeconfig: ## Save kubeconfig to ~/.kube/config and set cluster context
	@echo "$(GREEN)Saving kubeconfig to ~/.kube/config...$(NC)"
	terraform -chdir=terraform output -raw linode_cluster_kubeconfig > ~/.kube/config
	cat ~/.kube/config
	@kubectl cluster-info
	@echo "$(GREEN)Kubeconfig saved to ~/.kube/config!$(NC)"

k8s-set-environment: ## Set environment variables and deploy infrastructure
	@echo "$(GREEN)Setting environment variables for Kubernetes infrastructure...$(NC)"
	@echo "$(GREEN)Deploying environment to Kubernetes...$(NC)"
	@kubectl apply -f kubernetes/environment.yaml
	@echo "$(GREEN)Creating application secrets...$(NC)"
	@kubectl delete secret scottlms-secrets -n scottlms --ignore-not-found
	$(eval MONGODB_URL := $(shell terraform -chdir=terraform output -raw mongodb_url))
	@kubectl create secret generic scottlms-secrets -n scottlms --from-literal=MONGODB_URL=$(MONGODB_URL)
	@echo "$(GREEN)Application secrets created!$(NC)"
	@echo "$(GREEN)Creating Docker Hub credentials...$(NC)"
	@kubectl delete secret docker-hub-credentials -n scottlms --ignore-not-found
	@kubectl create secret docker-registry docker-hub-credentials -n scottlms --docker-username=$(DOCKER_HUB_USERNAME) --docker-password=$(DOCKER_HUB_PASSWORD)
	@echo "$(GREEN)Docker Hub credentials created!$(NC)"
	@echo "$(GREEN)Infrastructure deployment complete!$(NC)"

k8s-deploy-frontend: ## Deploy frontend (check, build, or update)
	@echo "$(GREEN)Checking frontend deployment...$(NC)"
	@if kubectl get deployment scottlms-frontend -n scottlms >/dev/null 2>&1; then \
		echo "$(YELLOW)Frontend deployment exists, updating...$(NC)"; \
		kubectl apply -f kubernetes/presentation.yaml; \
		echo "$(GREEN)Forcing fresh image pull and pod recreation...$(NC)"; \
		kubectl rollout restart deployment/scottlms-frontend -n scottlms; \
		echo "$(GREEN)Waiting for frontend rollout to complete...$(NC)"; \
		kubectl rollout status deployment/scottlms-frontend -n scottlms --timeout=300s; \
		echo "$(GREEN)Frontend updated with fresh image!$(NC)"; \
	else \
		echo "$(YELLOW)Frontend deployment not found, creating...$(NC)"; \
		kubectl apply -f kubernetes/presentation.yaml; \
		echo "$(GREEN)Waiting for frontend deployment to be ready...$(NC)"; \
		kubectl rollout status deployment/scottlms-frontend -n scottlms --timeout=300s; \
		echo "$(GREEN)Frontend created!$(NC)"; \
	fi
	$(eval FRONTEND_EXTERNAL_IP := $(shell kubectl get service scottlms-frontend-loadbalancer -n scottlms -o jsonpath='{.status.loadBalancer.ingress[0].ip}'))
	@echo "$(GREEN)Frontend external IP: $(FRONTEND_EXTERNAL_IP)$(NC)"
	@echo "$(GREEN)Frontend deployment complete!$(NC)"
	
k8s-deploy-backend: ## Deploy backend (check, build, or update)
	@echo "$(GREEN)Checking backend deployment...$(NC)"
	@if kubectl get deployment scottlms-api -n scottlms >/dev/null 2>&1; then \
		echo "$(YELLOW)Backend deployment exists, updating...$(NC)"; \
		kubectl apply -f kubernetes/application.yaml; \
		echo "$(GREEN)Forcing fresh image pull and pod recreation...$(NC)"; \
		kubectl rollout restart deployment/scottlms-api -n scottlms; \
		echo "$(GREEN)Waiting for backend rollout to complete...$(NC)"; \
		kubectl rollout status deployment/scottlms-api -n scottlms --timeout=300s; \
		echo "$(GREEN)Backend updated with fresh image!$(NC)"; \
	else \
		echo "$(YELLOW)Backend deployment not found, creating...$(NC)"; \
		kubectl apply -f kubernetes/application.yaml; \
		echo "$(GREEN)Waiting for backend deployment to be ready...$(NC)"; \
		kubectl rollout status deployment/scottlms-api -n scottlms --timeout=300s; \
		echo "$(GREEN)Backend created!$(NC)"; \
	fi
	$(eval BACKEND_EXTERNAL_IP := $(shell kubectl get service scottlms-api-loadbalancer -n scottlms -o jsonpath='{.status.loadBalancer.ingress[0].ip}'))
	@echo "$(GREEN)Backend external IP: $(BACKEND_EXTERNAL_IP):8000$(NC)"
	@echo "$(GREEN)Backend deployment complete!$(NC)"

full-deployment: docker-build docker-push k8s-sync-kubeconfig k8s-set-environment k8s-deploy-backend k8s-deploy-frontend ## Full deployment
	@echo "$(GREEN)Full deployment complete!$(NC)"

##@ Health Checks
perform-health-checks: ## Perform health check on backend and frontend
	@echo "$(GREEN)Performing health checks...$(NC)"
	$(eval BACKEND_EXTERNAL_IP := $(shell kubectl get service scottlms-api-loadbalancer -n scottlms -o jsonpath='{.status.loadBalancer.ingress[0].ip}'))
	$(eval FRONTEND_EXTERNAL_IP := $(shell kubectl get service scottlms-frontend-loadbalancer -n scottlms -o jsonpath='{.status.loadBalancer.ingress[0].ip}'))
	@echo "$(GREEN)Checking backend availability...$(NC)"
	@curl -f http://$(BACKEND_EXTERNAL_IP):8000/health || exit 1
	@echo ""
	@echo "$(GREEN)Checking frontend availability...$(NC)"
	@curl -I -f http://$(FRONTEND_EXTERNAL_IP) || exit 1
	@echo "$(GREEN)Health checks complete!$(NC)"

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
	docker compose build --parallel --no-cache
	@echo "$(GREEN)Build complete!$(NC)"

##@ Database
db-shell: ## Connect to MongoDB shell
	docker compose exec mongodb mongosh scottlms

db-reset: ## Reset database (WARNING: deletes all data)
	@echo "$(RED)WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ]
	docker compose exec mongodb mongosh scottlms --eval "db.dropDatabase()"
	@echo "$(GREEN)Database reset!$(NC)"

test-all: test test-coverage ## Run all tests with coverage
build-all: docker-build test quality ## Build, test, and quality check

##@ Information
status: ## Show development environment status
	@echo "$(BLUE)=== Development Environment Status ===$(NC)"
	@echo ""
	@echo "$(YELLOW)Container Status:$(NC)"
	@docker compose ps
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