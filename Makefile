# ScottLMS Makefile
# This Makefile provides convenient commands for development, testing, and deployment

.PHONY: help install dev build test clean deploy infra status logs shell format lint security-check

# Default target
.DEFAULT_GOAL := help

# Variables
PROJECT_NAME := scottlms
AWS_REGION := us-east-1
ENVIRONMENT := production
IMAGE_TAG := latest
PYTHON := python3
PIP := pip3
AWS_PROFILE := ScottLMS-Permission-Set-055239228382

# Colors for output
RED := \033[0;31m
ORANGE := \033[38;5;208m
YELLOW := \033[1;33m
GREEN := \033[0;32m
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
	@echo "$(GREEN)Building Docker images...$(NC)"
	docker-compose build --parallel --no-cache
	@echo "$(GREEN)Starting development environment...$(NC)"
	docker-compose up -d
	@echo "$(YELLOW)Waiting for all services to be healthy...$(NC)"
	@timeout 120 bash -c 'until docker-compose ps | grep -q "healthy"; do sleep 2; done' || echo "$(ORANGE)Warning: Some services may not be fully healthy yet$(NC)"
	@echo "$(GREEN)Development environment started!$(NC)"
	@echo "$(BLUE)Access URLs:$(NC)"
	@echo "  • Frontend (UI): http://localhost"
	@echo "  • API: http://localhost:8000"
	@echo "  • API Docs: http://localhost:8000/docs"
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
	@echo "$(ORANGE)WARNING: This will delete all data in the database!$(NC)"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ]
	docker-compose exec mongodb mongosh scottlms --eval "db.dropDatabase()"
	@echo "$(GREEN)Database reset complete!$(NC)"

db-backup: ## Backup database
	@echo "$(GREEN)Creating database backup...$(NC)"
	mkdir -p backups
	docker-compose exec mongodb mongodump --db scottlms --out /tmp/backup
	docker cp $$(docker-compose ps -q mongodb):/tmp/backup ./backups/backup-$$(date +%Y%m%d-%H%M%S)
	@echo "$(GREEN)Database backup created!$(NC)"


##@ AWS Authentication
aws-login: ## Login to AWS SSO and get temporary credentials (interactive)
	@if [ "$$CI" = "true" ] || [ "$$GITHUB_ACTIONS" = "true" ]; then \
		echo "$(YELLOW)Running in CI/CD environment. Using existing AWS credentials.$(NC)"; \
		echo "$(GREEN)AWS credentials should be configured via GitHub Actions secrets.$(NC)"; \
	else \
		echo "$(GREEN)Logging into AWS SSO...$(NC)"; \
		aws sso login --profile $(AWS_PROFILE); \
		echo "$(GREEN)Getting temporary credentials...$(NC)"; \
		eval $$(aws configure export-credentials --profile $(AWS_PROFILE) --format env) && \
		export AWS_ACCESS_KEY_ID=$$AWS_ACCESS_KEY_ID && \
		export AWS_SECRET_ACCESS_KEY=$$AWS_SECRET_ACCESS_KEY && \
		export AWS_SESSION_TOKEN=$$AWS_SESSION_TOKEN && \
		export AWS_DEFAULT_REGION=$(AWS_REGION) && \
		echo "$(GREEN)AWS credentials configured!$(NC)" && \
		echo "$(YELLOW)Credentials expire at: $$AWS_CREDENTIAL_EXPIRATION$(NC)"; \
	fi

aws-test: ## Test AWS credentials
	@echo "$(GREEN)Testing AWS credentials...$(NC)"
	aws sts get-caller-identity

aws-status: ## Show AWS authentication status
	@echo "$(BLUE)=== AWS Authentication Status ===$(NC)"
	@echo ""
	@echo "$(YELLOW)Current AWS Profile:$(NC)"
	@echo "$$AWS_PROFILE"
	@echo ""
	@echo "$(YELLOW)AWS Identity:$(NC)"
	@aws sts get-caller-identity 2>/dev/null || echo "$(RED)❌ Not authenticated$(NC)"
	@echo ""
	@echo "$(YELLOW)Available AWS Profiles:$(NC)"
	@aws configure list-profiles 2>/dev/null || echo "$(RED)❌ No profiles configured$(NC)"

##@ Infrastructure
infra-init:
	@echo "$(GREEN)Initializing Terraform...$(NC)"
	@if [ "$$CI" = "true" ] || [ "$$GITHUB_ACTIONS" = "true" ]; then \
		echo "$(YELLOW)Using CI/CD AWS credentials...$(NC)"; \
		cd terraform && terraform init; \
	else \
		echo "$(YELLOW)Using SSO AWS credentials...$(NC)"; \
		eval $$(aws configure export-credentials --profile $(AWS_PROFILE) --format env) && \
		export AWS_ACCESS_KEY_ID=$$AWS_ACCESS_KEY_ID && \
		export AWS_SECRET_ACCESS_KEY=$$AWS_SECRET_ACCESS_KEY && \
		export AWS_SESSION_TOKEN=$$AWS_SESSION_TOKEN && \
		export AWS_DEFAULT_REGION=$(AWS_REGION) && \
		unset AWS_PROFILE && \
		cd terraform && terraform init; \
	fi

infra-validate:
	@echo "$(GREEN)Validating Terraform configuration...$(NC)"
	@eval $$(aws configure export-credentials --profile $(AWS_PROFILE) --format env) && \
	export AWS_ACCESS_KEY_ID=$$AWS_ACCESS_KEY_ID && \
	export AWS_SECRET_ACCESS_KEY=$$AWS_SECRET_ACCESS_KEY && \
	export AWS_SESSION_TOKEN=$$AWS_SESSION_TOKEN && \
	export AWS_DEFAULT_REGION=$(AWS_REGION) && \
	unset AWS_PROFILE && \
	cd terraform && terraform validate

infra-fmt:
	@echo "$(GREEN)Formatting Terraform configuration...$(NC)"
	@eval $$(aws configure export-credentials --profile $(AWS_PROFILE) --format env) && \
	export AWS_ACCESS_KEY_ID=$$AWS_ACCESS_KEY_ID && \
	export AWS_SECRET_ACCESS_KEY=$$AWS_SECRET_ACCESS_KEY && \
	export AWS_SESSION_TOKEN=$$AWS_SESSION_TOKEN && \
	export AWS_DEFAULT_REGION=$(AWS_REGION) && \
	unset AWS_PROFILE && \
	cd terraform && terraform fmt -recursive

infra-plan:
	@echo "$(GREEN)Planning Terraform deployment...$(NC)"
	@eval $$(aws configure export-credentials --profile $(AWS_PROFILE) --format env) && \
	export AWS_ACCESS_KEY_ID=$$AWS_ACCESS_KEY_ID && \
	export AWS_SECRET_ACCESS_KEY=$$AWS_SECRET_ACCESS_KEY && \
	export AWS_SESSION_TOKEN=$$AWS_SESSION_TOKEN && \
	export AWS_DEFAULT_REGION=$(AWS_REGION) && \
	unset AWS_PROFILE && \
	cd terraform && terraform plan -out=tfplan

infra-apply:
	@echo "$(GREEN)Applying Terraform configuration...$(NC)"
	@eval $$(aws configure export-credentials --profile $(AWS_PROFILE) --format env) && \
	export AWS_ACCESS_KEY_ID=$$AWS_ACCESS_KEY_ID && \
	export AWS_SECRET_ACCESS_KEY=$$AWS_SECRET_ACCESS_KEY && \
	export AWS_SESSION_TOKEN=$$AWS_SESSION_TOKEN && \
	export AWS_DEFAULT_REGION=$(AWS_REGION) && \
	unset AWS_PROFILE && \
	cd terraform && terraform apply tfplan

infra-destroy:
	@echo "$(RED)WARNING: This will destroy all infrastructure!$(NC)"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ]
	@eval $$(aws configure export-credentials --profile $(AWS_PROFILE) --format env) && \
	export AWS_ACCESS_KEY_ID=$$AWS_ACCESS_KEY_ID && \
	export AWS_SECRET_ACCESS_KEY=$$AWS_SECRET_ACCESS_KEY && \
	export AWS_SESSION_TOKEN=$$AWS_SESSION_TOKEN && \
	export AWS_DEFAULT_REGION=$(AWS_REGION) && \
	unset AWS_PROFILE && \
	cd terraform && terraform destroy -auto-approve

infra-output:
	@eval $$(aws configure export-credentials --profile $(AWS_PROFILE) --format env) && \
	export AWS_ACCESS_KEY_ID=$$AWS_ACCESS_KEY_ID && \
	export AWS_SECRET_ACCESS_KEY=$$AWS_SECRET_ACCESS_KEY && \
	export AWS_SESSION_TOKEN=$$AWS_SESSION_TOKEN && \
	export AWS_DEFAULT_REGION=$(AWS_REGION) && \
	unset AWS_PROFILE && \
	cd terraform && terraform output

infra-clean-plan: ## Clean up Terraform plan file
	@echo "$(GREEN)Cleaning up Terraform plan file...$(NC)"
	@if [ -f terraform/tfplan ]; then \
		rm terraform/tfplan; \
		echo "$(GREEN)Plan file removed$(NC)"; \
	else \
		echo "$(YELLOW)No plan file found$(NC)"; \
	fi

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

deploy-ecs: aws-login ## Deploy application to ECS using Terraform
	@echo "$(GREEN)Deploying to ECS using Terraform...$(NC)"
	@eval $$(aws configure export-credentials --profile $(AWS_PROFILE) --format env) && \
	export AWS_ACCESS_KEY_ID=$$AWS_ACCESS_KEY_ID && \
	export AWS_SECRET_ACCESS_KEY=$$AWS_SECRET_ACCESS_KEY && \
	export AWS_SESSION_TOKEN=$$AWS_SESSION_TOKEN && \
	export AWS_DEFAULT_REGION=$(AWS_REGION) && \
	unset AWS_PROFILE && \
	cd terraform && terraform apply -var="image_tag=$(IMAGE_TAG)" -auto-approve
	@echo "$(GREEN)Waiting for ECS services to be ready...$(NC)"
	@eval $$(aws configure export-credentials --profile $(AWS_PROFILE) --format env) && \
	export AWS_ACCESS_KEY_ID=$$AWS_ACCESS_KEY_ID && \
	export AWS_SECRET_ACCESS_KEY=$$AWS_SECRET_ACCESS_KEY && \
	export AWS_SESSION_TOKEN=$$AWS_SESSION_TOKEN && \
	export AWS_DEFAULT_REGION=$(AWS_REGION) && \
	aws ecs wait services-stable --cluster $(PROJECT_NAME)-$(ENVIRONMENT) --services scottlms-api scottlms-frontend
	@echo "$(GREEN)ECS deployment complete!$(NC)"

deploy: deploy-build deploy-ecs ## Full deployment (build + deploy to ECS)

##@ Monitoring & Debugging
status: aws-login ## Show ECS deployment status
	@echo "$(BLUE)=== ECS Deployment Status ===$(NC)"
	@eval $$(aws configure export-credentials --profile $(AWS_PROFILE) --format env) && \
	export AWS_ACCESS_KEY_ID=$$AWS_ACCESS_KEY_ID && \
	export AWS_SECRET_ACCESS_KEY=$$AWS_SECRET_ACCESS_KEY && \
	export AWS_SESSION_TOKEN=$$AWS_SESSION_TOKEN && \
	export AWS_DEFAULT_REGION=$(AWS_REGION) && \
	echo "$(YELLOW)ECS Cluster:$(NC)" && \
	aws ecs describe-clusters --clusters $(PROJECT_NAME)-$(ENVIRONMENT) --query 'clusters[0].{Name:clusterName,Status:status,RunningTasks:runningTasksCount,PendingTasks:pendingTasksCount}' --output table && \
	echo "" && \
	echo "$(YELLOW)ECS Services:$(NC)" && \
	aws ecs list-services --cluster $(PROJECT_NAME)-$(ENVIRONMENT) --query 'serviceArns[]' --output table && \
	echo "" && \
	echo "$(YELLOW)Load Balancer:$(NC)" && \
	aws elbv2 describe-load-balancers --names $(PROJECT_NAME)-$(ENVIRONMENT) --query 'LoadBalancers[0].{Name:LoadBalancerName,DNSName:DNSName,State:State.Code}' --output table 2>/dev/null || echo "$(RED)Load balancer not found$(NC)"

logs: aws-login ## View ECS application logs
	@echo "$(GREEN)Viewing ECS application logs...$(NC)"
	@eval $$(aws configure export-credentials --profile $(AWS_PROFILE) --format env) && \
	export AWS_ACCESS_KEY_ID=$$AWS_ACCESS_KEY_ID && \
	export AWS_SECRET_ACCESS_KEY=$$AWS_SECRET_ACCESS_KEY && \
	export AWS_SESSION_TOKEN=$$AWS_SESSION_TOKEN && \
	export AWS_DEFAULT_REGION=$(AWS_REGION) && \
	aws logs tail /ecs/scottlms-api --follow

logs-frontend: aws-login ## View ECS frontend logs
	@echo "$(GREEN)Viewing ECS frontend logs...$(NC)"
	@eval $$(aws configure export-credentials --profile $(AWS_PROFILE) --format env) && \
	export AWS_ACCESS_KEY_ID=$$AWS_ACCESS_KEY_ID && \
	export AWS_SECRET_ACCESS_KEY=$$AWS_SECRET_ACCESS_KEY && \
	export AWS_SESSION_TOKEN=$$AWS_SESSION_TOKEN && \
	export AWS_DEFAULT_REGION=$(AWS_REGION) && \
	aws logs tail /ecs/scottlms-frontend --follow

logs-all: aws-login ## View all ECS logs
	@echo "$(GREEN)Viewing all ECS logs...$(NC)"
	@eval $$(aws configure export-credentials --profile $(AWS_PROFILE) --format env) && \
	export AWS_ACCESS_KEY_ID=$$AWS_ACCESS_KEY_ID && \
	export AWS_SECRET_ACCESS_KEY=$$AWS_SECRET_ACCESS_KEY && \
	export AWS_SESSION_TOKEN=$$AWS_SESSION_TOKEN && \
	export AWS_DEFAULT_REGION=$(AWS_REGION) && \
	aws logs tail /ecs/scottlms-api /ecs/scottlms-frontend --follow

shell: aws-login ## Get shell access to running ECS task
	@echo "$(GREEN)Getting shell access to ECS task...$(NC)"
	@eval $$(aws configure export-credentials --profile $(AWS_PROFILE) --format env) && \
	export AWS_ACCESS_KEY_ID=$$AWS_ACCESS_KEY_ID && \
	export AWS_SECRET_ACCESS_KEY=$$AWS_SECRET_ACCESS_KEY && \
	export AWS_SESSION_TOKEN=$$AWS_SESSION_TOKEN && \
	export AWS_DEFAULT_REGION=$(AWS_REGION) && \
	TASK_ARN=$$(aws ecs list-tasks --cluster $(PROJECT_NAME)-$(ENVIRONMENT) --service-name scottlms-api --query 'taskArns[0]' --output text) && \
	aws ecs execute-command --cluster $(PROJECT_NAME)-$(ENVIRONMENT) --task $$TASK_ARN --container scottlms-api --interactive --command "/bin/bash"

urls: aws-login ## Show application URLs
	@echo "$(BLUE)=== Application URLs ===$(NC)"
	@eval $$(aws configure export-credentials --profile $(AWS_PROFILE) --format env) && \
	export AWS_ACCESS_KEY_ID=$$AWS_ACCESS_KEY_ID && \
	export AWS_SECRET_ACCESS_KEY=$$AWS_SECRET_ACCESS_KEY && \
	export AWS_SESSION_TOKEN=$$AWS_SESSION_TOKEN && \
	export AWS_DEFAULT_REGION=$(AWS_REGION) && \
	ALB_DNS=$$(aws elbv2 describe-load-balancers --names $(PROJECT_NAME)-$(ENVIRONMENT) --query 'LoadBalancers[0].DNSName' --output text 2>/dev/null) && \
	if [ "$$ALB_DNS" != "None" ] && [ -n "$$ALB_DNS" ]; then \
		echo "$(GREEN)Frontend: http://$$ALB_DNS:8080$(NC)"; \
		echo "$(GREEN)API: http://$$ALB_DNS$(NC)"; \
		echo "$(GREEN)API Docs: http://$$ALB_DNS/docs$(NC)"; \
	else \
		echo "$(RED)Load balancer not found. Run 'make infra-apply' first.$(NC)"; \
	fi

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
	cd terraform && terraform plan -var="environment=test" -var="project_name=scottlms-test" -out=ci-test-plan && \
	rm -f ci-test-plan

ci-ecs: aws-login ## Validate ECS configuration with Terraform
	@echo "$(GREEN)Validating ECS configuration with Terraform...$(NC)"
	@eval $$(aws configure export-credentials --profile $(AWS_PROFILE) --format env) && \
	export AWS_ACCESS_KEY_ID=$$AWS_ACCESS_KEY_ID && \
	export AWS_SECRET_ACCESS_KEY=$$AWS_SECRET_ACCESS_KEY && \
	export AWS_SESSION_TOKEN=$$AWS_SESSION_TOKEN && \
	export AWS_DEFAULT_REGION=$(AWS_REGION) && \
	unset AWS_PROFILE && \
	cd terraform && terraform plan -var="image_tag=latest" -out=ci-plan && \
	rm -f ci-plan

ci-all: ci-test ci-docker ci-terraform ci-ecs ## Run all CI checks locally

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
	docker rmi -f $(shell docker images -q)
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

deploy-all: infra-apply deploy-build deploy-ecs ## Full deployment pipeline
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
	@echo "  • FastAPI Backend: backend/"
	@echo "  • Frontend: frontend/"
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
	@echo "  • make deploy-all   - Full deployment pipeline (ECS)"
	@echo "  • make monitor      - Show status and follow logs"
	@echo "  • make reset        - Reset everything and restart"
	@echo ""
	@echo "$(YELLOW)AWS Commands:$(NC)"
	@echo "  • make aws-login    - Login to AWS SSO"
	@echo "  • make aws-test     - Test AWS credentials"
	@echo "  • make aws-status   - Show AWS authentication status"
	@echo ""
	@echo "$(YELLOW)Infrastructure Commands:$(NC)"
	@echo "  • make infra-init      - Initialize Terraform"
	@echo "  • make infra-validate  - Validate Terraform configuration"
	@echo "  • make infra-fmt       - Format Terraform files"
	@echo "  • make infra-plan      - Plan Terraform deployment (saves to tfplan)"
	@echo "  • make infra-apply     - Apply Terraform configuration (uses tfplan)"
	@echo "  • make infra-destroy   - Destroy all infrastructure"
	@echo "  • make infra-output    - Show Terraform outputs"
	@echo "  • make infra-clean-plan- Clean up plan file"
	@echo "  • make status          - Check ECS deployment status"
	@echo "  • make urls            - Show application URLs"
	@echo ""
	@echo "$(YELLOW)Common Commands:$(NC)"
	@echo "  • make dev          - Start development environment"
	@echo "  • make test         - Run tests"
	@echo "  • make deploy       - Deploy to production (ECS)"
	@echo "  • make logs         - View application logs"
