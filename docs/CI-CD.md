# CI/CD Pipeline Documentation

This document describes the Continuous Integration and Continuous Deployment (CI/CD) pipeline for ScottLMS using GitHub Actions.

## Overview

The CI/CD pipeline consists of two main workflows:

1. **PR Validation** - Runs on pull requests to ensure code quality
2. **Production Deployment** - Runs on pushes to main branch to deploy to production

## Workflows

### 1. PR Validation Workflow (`pr-validation.yml`)

**Triggers:**
- Pull requests to `main` or `develop` branches
- Manual trigger via GitHub Actions UI

**Jobs:**

#### Test & Code Quality
- **Python Setup**: Sets up Python 3.11 environment
- **MongoDB Service**: Starts MongoDB 7.0 for testing
- **Dependencies**: Installs all required packages including testing tools
- **Code Quality Checks**:
  - Linting with flake8
  - Format checking with black
  - Import sorting with isort
  - Security scanning with bandit
  - Dependency vulnerability check with safety
- **Testing**: Runs pytest with coverage reporting
- **Coverage**: Uploads coverage reports to Codecov

#### Docker Build Test
- **Build**: Tests Docker image build process
- **Health Check**: Verifies the built image can start and respond to health checks

#### Infrastructure Validation
- **Terraform**: Validates Terraform configuration
- **Format Check**: Ensures Terraform code is properly formatted
- **Plan**: Creates a dry-run plan to catch configuration errors

#### Kubernetes Validation
- **Manifest Validation**: Validates all Kubernetes YAML files
- **Dry Run**: Tests applying manifests without actually deploying

#### Security Scanning
- **Trivy**: Scans for vulnerabilities in dependencies and filesystem
- **SARIF Upload**: Uploads results to GitHub Security tab

#### Performance Testing
- **k6 Load Testing**: Runs basic performance tests
- **Health Endpoint**: Tests response times under load

### 2. Production Deployment Workflow (`production-deploy.yml`)

**Triggers:**
- Pushes to `main` branch
- Manual trigger with environment selection

**Jobs:**

#### Pre-deployment Checks
- **Environment Setup**: Determines target environment
- **Image Tagging**: Generates unique image tags
- **Validation**: Ensures deployment parameters are valid

#### Infrastructure Deployment
- **Terraform**: Deploys AWS infrastructure
- **ECR**: Ensures container registry is available
- **Environment**: Uses GitHub Environments for approval gates

#### Build and Push
- **Docker Build**: Builds application image
- **ECR Push**: Pushes image to Amazon ECR
- **Manifest Update**: Updates Kubernetes manifests with new image tag

#### Application Deployment
- **Kubernetes**: Deploys application to EKS cluster
- **Health Checks**: Verifies deployment is successful
- **Rollback**: Automatic rollback on failure

#### Post-deployment Tests
- **Smoke Tests**: Basic functionality verification
- **Load Tests**: Performance validation
- **Health Monitoring**: Continuous health checks

#### Notifications
- **Summary**: Detailed deployment summary
- **Slack**: Optional Slack notifications (if configured)

## Required Secrets

### GitHub Secrets

The following secrets must be configured in your GitHub repository:

#### AWS Secrets
```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_ACCOUNT_ID
```

#### MongoDB Atlas Secrets
```
MONGODB_ATLAS_PUBLIC_KEY
MONGODB_ATLAS_PRIVATE_KEY
MONGODB_ATLAS_PROJECT_ID
```

#### Optional Secrets
```
SLACK_WEBHOOK_URL  # For Slack notifications
```

### Environment Variables

The following environment variables are used in the workflows:

```yaml
AWS_REGION: us-west-2
PROJECT_NAME: scottlms
ECR_REGISTRY: {AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com
ECR_REPOSITORY: scottlms-api
```

## GitHub Environments

Configure the following environments in your GitHub repository:

### Production Environment
- **Name**: `production`
- **Protection Rules**: 
  - Required reviewers (optional)
  - Wait timer (optional)
  - Restrict to main branch

### Staging Environment
- **Name**: `staging`
- **Protection Rules**: 
  - Required reviewers (optional)

## Manual Deployment

You can manually trigger deployments using the GitHub Actions UI:

1. Go to the "Actions" tab in your repository
2. Select the "Production Deployment" workflow
3. Click "Run workflow"
4. Choose your options:
   - **Environment**: production or staging
   - **Skip Infrastructure**: Skip infrastructure deployment if only deploying code changes

## Monitoring and Alerts

### GitHub Actions
- All workflow runs are logged in the Actions tab
- Failed runs send notifications to repository watchers
- Status checks prevent merging of failed PRs

### Application Monitoring
- Health checks run continuously
- Performance metrics are collected
- Error rates are monitored

### Infrastructure Monitoring
- AWS CloudWatch monitors infrastructure health
- Terraform state is tracked
- Resource usage is monitored

## Troubleshooting

### Common Issues

#### Build Failures
- Check Docker build logs
- Verify all dependencies are in requirements.txt
- Ensure Dockerfile is properly configured

#### Test Failures
- Review test output in Actions logs
- Check for flaky tests
- Verify test database setup

#### Deployment Failures
- Check Kubernetes logs: `kubectl logs -f deployment/scottlms-api -n scottlms`
- Verify AWS credentials and permissions
- Check Terraform state and outputs

#### Infrastructure Issues
- Review Terraform plan output
- Check AWS resource limits
- Verify network configuration

### Debug Commands

```bash
# Check workflow status
gh run list

# View workflow logs
gh run view <run-id>

# Check deployment status
kubectl get pods -n scottlms

# View application logs
kubectl logs -f deployment/scottlms-api -n scottlms

# Check infrastructure status
cd terraform && terraform show
```

## Best Practices

### Code Quality
- Always run tests locally before pushing
- Use meaningful commit messages
- Keep PRs small and focused
- Review all code changes

### Security
- Never commit secrets to the repository
- Use GitHub Secrets for sensitive data
- Regularly update dependencies
- Monitor security alerts

### Deployment
- Test changes in staging before production
- Use feature flags for risky changes
- Monitor deployments closely
- Have rollback plans ready

### Infrastructure
- Review Terraform changes carefully
- Use infrastructure as code principles
- Monitor resource usage
- Keep documentation updated

## Customization

### Adding New Tests
1. Add test files to the `tests/` directory
2. Update `pytest.ini` if needed
3. Tests will automatically run in CI

### Adding New Environments
1. Create new environment in GitHub
2. Update workflow files with new environment
3. Configure environment-specific secrets

### Modifying Deployment Process
1. Edit workflow files in `.github/workflows/`
2. Test changes in a separate branch
3. Update documentation as needed

## Support

For issues with the CI/CD pipeline:

1. Check the Actions tab for error details
2. Review this documentation
3. Check GitHub Actions documentation
4. Create an issue in the repository
