# 🟣 GitHub Actions CI/CD Pipeline Guide

## Overview

This guide provides comprehensive instructions for setting up CI/CD pipelines using GitHub Actions to build, test, and deploy the MCP Platform Framework to Azure Function Apps.

## 📋 Prerequisites

Before setting up GitHub Actions workflows, ensure you have:

- ✅ **GitHub Repository** for your MCP Platform Framework
- ✅ **GitHub Secrets** configured for Azure authentication
- ✅ **Azure Resources** provisioned (Resource Groups, Key Vault, Function Apps)
- ✅ **Service Principal** or Managed Identity for authentication

## 🔧 GitHub Setup

### 1. Create GitHub Repository

1. Go to [GitHub](https://github.com/)
2. Click the "+" icon → "New repository"
3. Enter repository name: `mcp-platform-framework`
4. Choose visibility: Private (recommended)
5. Initialize with README (optional)
6. Add .gitignore: Python
7. Click "Create repository"

### 2. Configure GitHub Secrets

Go to Repository Settings → Secrets and variables → Actions:

**Required Secrets:**

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `AZURE_CREDENTIALS` | Azure service principal credentials | JSON object |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID | `xxxx-xxxx-xxxx` |
| `AZURE_RESOURCE_GROUP` | Resource group name | `mcp-prod-rg` |
| `AZURE_FUNCTIONAPP_NAME` | Function App name | `mcp-prod-func` |
| `KEY_VAULT_URI` | Key Vault URI | `https://mcp-kv.vault.azure.net/` |
| `FABRIC_TENANT_ID` | Fabric tenant ID | `xxxx-xxxx-xxxx` |
| `FABRIC_WORKSPACE_ID` | Fabric workspace ID | `xxxx-xxxx-xxxx` |

**How to create AZURE_CREDENTIALS:**

```bash
# Create service principal and get credentials
az ad sp create-for-rbac --name mcp-github-sp --skip-assignment

# Get the JSON output
az ad sp show --id <client-id> --query "{clientId:appId, clientSecret:password, tenantId:appOwnerTenantId}" -o json

# Copy the JSON output and add to GitHub Secrets as AZURE_CREDENTIALS
```

### 3. Set Up Environment Variables

Go to Repository Settings → Environments:

**Create Environments:**
- `development` - For development deployments
- `test` - For test deployments
- `staging` - For staging deployments
- `production` - For production deployments (with protection rules)

**Configure Protection Rules for Production:**
- Require manual approval for deployments
- Require specific reviewers
- Add environment-specific secrets

## 📁 Workflow Structure

```
.github/
└── workflows/
    ├── build.yml              # Build and test workflow
    ├── deploy.yml             # Deployment workflow
    ├── promote.yml            # Environment promotion workflow
    ├── security.yml           # Security scanning workflow
    ├── cleanup.yml            # Cleanup workflow
    └── scheduled.yml          # Scheduled tasks workflow
```

## 🏗️ Build Workflow

### Basic Build Workflow

**.github/workflows/build.yml**
```yaml
name: Build and Test

on:
  push:
    branches:
      - main
      - releases/**
    paths-ignore:
      - 'docs/**'
      - 'README.md'
      - 'CHANGELOG.md'
  pull_request:
    branches:
      - main
      - releases/**
    paths-ignore:
      - 'docs/**'

concurrency:
  group: build-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build:
    name: Build and Test
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11']
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      with:
        fetch-depth: 0
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        cache: 'pip'
        cache-dependency-path: |
          requirements.txt
          requirements-dev.txt
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Install package
      run: |
        pip install -e .
    
    - name: Run linting
      run: |
        pip install flake8 black isort mypy
        flake8 src/ tests/ --max-line-length=120 --extend-ignore=E203
        black --check src/ tests/
        isort --check src/ tests/
        mypy src/ --ignore-missing-imports
    
    - name: Run unit tests
      run: |
        python -m pytest tests/unit --cov=mcp_framework --cov-report=xml --junitxml=test-results.xml -v
      env:
        MCP_ENVIRONMENT: test
        AZURE_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: unit-test-results
        path: test-results.xml
        retention-days: 30
    
    - name: Upload coverage report
      uses: actions/upload-artifact@v3
      with:
        name: coverage-report
        path: coverage.xml
        retention-days: 30
    
    - name: Run integration tests
      if: github.ref == 'refs/heads/main'
      run: |
        python -m pytest tests/integration --junitxml=integration-results.xml -v
      env:
        MCP_ENVIRONMENT: test
        AZURE_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
        AZURE_RESOURCE_GROUP: mcp-test-rg
        KEY_VAULT_NAME: mcp-test-kv
        FABRIC_TENANT_ID: ${{ secrets.FABRIC_TENANT_ID }}
        FABRIC_WORKSPACE_ID: ${{ secrets.FABRIC_WORKSPACE_ID }}
    
    - name: Upload integration test results
      uses: actions/upload-artifact@v3
      if: always() && github.ref == 'refs/heads/main'
      with:
        name: integration-test-results
        path: integration-results.xml
        retention-days: 30
    
    - name: Build package
      if: github.ref == 'refs/heads/main'
      run: |
        pip install build twine
        python -m build
    
    - name: Upload package artifact
      uses: actions/upload-artifact@v3
      if: github.ref == 'refs/heads/main'
      with:
        name: mcp-platform-package
        path: dist/
        retention-days: 30
```

### Advanced Build Workflow with Caching

```yaml
name: Build and Test with Caching

on:
  push:
    branches:
      - main
      - releases/**
  pull_request:
    branches:
      - main

concurrency:
  group: build-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build:
    name: Build and Test
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      with:
        fetch-depth: 0
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        cache: 'pip'
        cache-dependency-path: |
          requirements.txt
          requirements-dev.txt
    
    - name: Cache test data
      uses: actions/cache@v3
      with:
        path: ~/.cache/test-data
        key: ${{ runner.os }}-test-data-${{ hashFiles('tests/data/**') }}
        restore-keys: |
          ${{ runner.os }}-test-data-
    
    - name: Cache build artifacts
      uses: actions/cache@v3
      with:
        path: .cache
        key: ${{ runner.os }}-build-${{ hashFiles('src/**', 'setup.py', 'pyproject.toml') }}
        restore-keys: |
          ${{ runner.os }}-build-
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        if [ "${{ github.ref }}" = "refs/heads/main" ]; then
          pip install -r requirements-dev.txt
        fi
    
    - name: Install package
      run: |
        pip install -e .
    
    - name: Run parallel tests
      run: |
        pip install pytest-xdist
        python -m pytest tests/unit -n auto --cov=mcp_framework --cov-report=xml --junitxml=test-results.xml
      env:
        MCP_ENVIRONMENT: test
        PYTEST_XDIST_WORKER_COUNT: 4
    
    - name: Run integration tests
      if: github.ref == 'refs/heads/main'
      run: |
        python -m pytest tests/integration -n auto --junitxml=integration-results.xml
      env:
        MCP_ENVIRONMENT: test
        AZURE_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
        AZURE_RESOURCE_GROUP: mcp-test-rg
    
    - name: Run security tests
      if: github.ref == 'refs/heads/main'
      run: |
        python -m pytest tests/security --junitxml=security-results.xml
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      if: github.ref == 'refs/heads/main'
      with:
        name: build-artifacts
        path: |
          dist/
          test-results.xml
          integration-results.xml
          security-results.xml
          coverage.xml
        retention-days: 30
```

## 🚀 Deployment Workflow

### Multi-Environment Deployment Workflow

**.github/workflows/deploy.yml**
```yaml
name: Deploy MCP Platform

on:
  workflow_run:
    workflows: ['Build and Test']
    branches: [main]
    types:
      - completed
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy to'
        required: true
        default: 'development'
        type: choice
        options:
        - development
        - test
        - staging
        - production
      build_id:
        description: 'Build ID to deploy'
        required: false

concurrency:
  group: deploy-${{ github.ref }}-${{ inputs.environment || 'development' }}
  cancel-in-progress: false

jobs:
  deploy:
    name: Deploy to ${{ inputs.environment || 'development' }}
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment || 'development' }}
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Download build artifact
      uses: actions/download-artifact@v3
      with:
        name: mcp-platform-package
        path: dist
    
    - name: Install package
      run: |
        pip install dist/*.whl
    
    - name: Azure Login
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
        enable-AzPSSession: true
    
    - name: Set Azure subscription
      run: |
        az account set --subscription ${{ secrets.AZURE_SUBSCRIPTION_ID }}
    
    - name: Deploy to Development
      if: inputs.environment == 'development' || (inputs.environment == '' && github.ref == 'refs/heads/main')
      run: |
        # Deploy to development Function App
        az functionapp deployment source config-zip \
          --name mcp-dev-func \
          --resource-group mcp-dev-rg \
          --src dist/*.zip
        
        # Set application settings
        az functionapp config appsettings set \
          --name mcp-dev-func \
          --resource-group mcp-dev-rg \
          --settings MCP_ENVIRONMENT=development
        
        # Restart Function App
        az functionapp restart \
          --name mcp-dev-func \
          --resource-group mcp-dev-rg
      env:
        AZURE_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
    
    - name: Deploy to Test
      if: inputs.environment == 'test'
      run: |
        # Deploy to test Function App
        az functionapp deployment source config-zip \
          --name mcp-test-func \
          --resource-group mcp-test-rg \
          --src dist/*.zip
        
        # Set application settings
        az functionapp config appsettings set \
          --name mcp-test-func \
          --resource-group mcp-test-rg \
          --settings MCP_ENVIRONMENT=test
        
        az functionapp config appsettings set \
          --name mcp-test-func \
          --resource-group mcp-test-rg \
          --settings KEY_VAULT_URI=https://mcp-test-kv.vault.azure.net/
        
        # Restart Function App
        az functionapp restart \
          --name mcp-test-func \
          --resource-group mcp-test-rg
      env:
        AZURE_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
    
    - name: Deploy to Staging
      if: inputs.environment == 'staging'
      run: |
        # Deploy to staging Function App
        az functionapp deployment source config-zip \
          --name mcp-staging-func \
          --resource-group mcp-staging-rg \
          --src dist/*.zip
        
        # Set application settings
        az functionapp config appsettings set \
          --name mcp-staging-func \
          --resource-group mcp-staging-rg \
          --settings MCP_ENVIRONMENT=staging
        
        az functionapp config appsettings set \
          --name mcp-staging-func \
          --resource-group mcp-staging-rg \
          --settings AZURE_RESOURCE_GROUP=mcp-staging-rg
        
        # Restart Function App
        az functionapp restart \
          --name mcp-staging-func \
          --resource-group mcp-staging-rg
      env:
        AZURE_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
    
    - name: Deploy to Production
      if: inputs.environment == 'production'
      run: |
        # Deploy with zero downtime using deployment slots
        az functionapp deployment slot create \
          --name mcp-prod-func \
          --resource-group mcp-prod-rg \
          --slot staging
        
        az functionapp deployment source config-zip \
          --name mcp-prod-func \
          --resource-group mcp-prod-rg \
          --slot staging \
          --src dist/*.zip
        
        # Set application settings for staging slot
        az functionapp config appsettings set \
          --name mcp-prod-func \
          --resource-group mcp-prod-rg \
          --slot staging \
          --settings MCP_ENVIRONMENT=production
        
        az functionapp config appsettings set \
          --name mcp-prod-func \
          --resource-group mcp-prod-rg \
          --slot staging \
          --settings KEY_VAULT_URI=${{ secrets.KEY_VAULT_URI }}
        
        # Warm up the staging slot
        for i in {1..5}; do
          curl -X POST https://mcp-prod-func-staging.azurewebsites.net/api/tools/HealthCheck \
            -H "Content-Type: application/json" \
            -d '{"arguments": {}}' && break || sleep 10
        done
        
        # Swap slots (zero downtime deployment)
        az functionapp deployment slot swap \
          --name mcp-prod-func \
          --resource-group mcp-prod-rg \
          --slot staging \
          --target-slot production
        
        # Clean up old staging slot
        az functionapp deployment slot delete \
          --name mcp-prod-func \
          --resource-group mcp-prod-rg \
          --slot staging
      env:
        AZURE_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
    
    - name: Run smoke tests
      run: |
        # Install test dependencies
        pip install pytest requests
        
        # Run smoke tests based on environment
        case "${{ inputs.environment || 'development' }}" in
          development)
            python -m pytest tests/smoke/development.py -v
            ;;
          test)
            python -m pytest tests/smoke/test.py -v
            ;;
          staging)
            python -m pytest tests/smoke/staging.py -v
            ;;
          production)
            python -m pytest tests/smoke/production.py -v
            ;;
        esac
      env:
        MCP_ENVIRONMENT: ${{ inputs.environment || 'development' }}
        AZURE_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
        AZURE_RESOURCE_GROUP: mcp-${{ inputs.environment || 'development' }}-rg
    
    - name: Azure Logout
      if: always()
      run: |
        az logout
```

## 🔄 Environment Promotion Workflow

**.github/workflows/promote.yml**
```yaml
name: Promote Environment

on:
  workflow_dispatch:
    inputs:
      source_environment:
        description: 'Source environment'
        required: true
        type: choice
        options:
        - development
        - test
        - staging
        default: test
      target_environment:
        description: 'Target environment'
        required: true
        type: choice
        options:
        - test
        - staging
        - production
        default: staging
      build_id:
        description: 'Build ID to promote'
        required: false

concurrency:
  group: promote-${{ inputs.source_environment }}-${{ inputs.target_environment }}
  cancel-in-progress: false

jobs:
  validate:
    name: Validate Promotion
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
    
    - name: Azure Login
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Validate source environment
      run: |
        # Check if source Function App exists and is running
        SOURCE_APP="mcp-${{ inputs.source_environment }}-func"
        SOURCE_RG="mcp-${{ inputs.source_environment }}-rg"
        
        echo "Checking source Function App: $SOURCE_APP"
        STATUS=$(az functionapp show --name $SOURCE_APP --resource-group $SOURCE_RG --query state --output tsv)
        
        if [ "$STATUS" != "Running" ]; then
          echo "Source Function App is not running"
          exit 1
        fi
    
    - name: Validate target environment
      run: |
        # Check if target Function App exists
        TARGET_APP="mcp-${{ inputs.target_environment }}-func"
        TARGET_RG="mcp-${{ inputs.target_environment }}-rg"
        
        echo "Checking target Function App: $TARGET_APP"
        az functionapp show --name $TARGET_APP --resource-group $TARGET_RG
    
    - name: Validate promotion path
      run: |
        # Validate that promotion follows the correct path
        case "${{ inputs.source_environment }}" in
          development)
            if [ "${{ inputs.target_environment }}" != "test" ]; then
              echo "Invalid promotion: development can only promote to test"
              exit 1
            fi
            ;;
          test)
            if [ "${{ inputs.target_environment }}" != "staging" ]; then
              echo "Invalid promotion: test can only promote to staging"
              exit 1
            fi
            ;;
          staging)
            if [ "${{ inputs.target_environment }}" != "production" ]; then
              echo "Invalid promotion: staging can only promote to production"
              exit 1
            fi
            ;;
        esac
    
    - name: Azure Logout
      if: always()
      run: |
        az logout
    
    outputs:
      source_app: mcp-${{ inputs.source_environment }}-func
      source_rg: mcp-${{ inputs.source_environment }}-rg
      target_app: mcp-${{ inputs.target_environment }}-func
      target_rg: mcp-${{ inputs.target_environment }}-rg

  approve:
    name: Approval Gate
    needs: validate
    if: inputs.target_environment != 'development'
    runs-on: ubuntu-latest
    environment: ${{ inputs.target_environment }}
    
    steps:
    - name: Wait for approval
      run: |
        echo "Waiting for approval to promote from ${{ inputs.source_environment }} to ${{ inputs.target_environment }}"
        echo "Source: ${{ needs.validate.outputs.source_app }}"
        echo "Target: ${{ needs.validate.outputs.target_app }}"

  deploy:
    name: Deploy to Target
    needs: [validate, approve]
    if: inputs.target_environment != 'development'
    runs-on: ubuntu-latest
    environment: ${{ inputs.target_environment }}
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Azure Login
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Set Azure subscription
      run: |
        az account set --subscription ${{ secrets.AZURE_SUBSCRIPTION_ID }}
    
    - name: Download build artifact
      uses: actions/download-artifact@v3
      with:
        name: mcp-platform-package
        path: dist
    
    - name: Install package
      run: |
        pip install dist/*.whl
    
    - name: Deploy to target environment
      run: |
        TARGET_APP="${{ needs.validate.outputs.target_app }}"
        TARGET_RG="${{ needs.validate.outputs.target_rg }}"
        
        echo "Deploying to $TARGET_APP in $TARGET_RG"
        
        # Deploy the package
        az functionapp deployment source config-zip \
          --name $TARGET_APP \
          --resource-group $TARGET_RG \
          --src dist/*.zip
        
        # Set environment-specific settings
        az functionapp config appsettings set \
          --name $TARGET_APP \
          --resource-group $TARGET_RG \
          --settings MCP_ENVIRONMENT=${{ inputs.target_environment }}
        
        # Set Key Vault URI if available
        if [ "${{ inputs.target_environment }}" != "development" ]; then
          az functionapp config appsettings set \
            --name $TARGET_APP \
            --resource-group $TARGET_RG \
            --settings KEY_VAULT_URI=${{ secrets.KEY_VAULT_URI }}
        fi
        
        # Restart Function App
        az functionapp restart \
          --name $TARGET_APP \
          --resource-group $TARGET_RG
    
    - name: Run post-deployment tests
      run: |
        pip install pytest requests
        python -m pytest tests/environment/${{ inputs.target_environment }}.py -v
      env:
        MCP_ENVIRONMENT: ${{ inputs.target_environment }}
        AZURE_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
        AZURE_RESOURCE_GROUP: ${{ needs.validate.outputs.target_rg }}
    
    - name: Azure Logout
      if: always()
      run: |
        az logout
```

## 🔒 Security Scanning Workflow

**.github/workflows/security.yml**
```yaml
name: Security Scanning

on:
  push:
    branches:
      - main
      - releases/**
  pull_request:
    branches:
      - main
  schedule:
    - cron: '0 2 * * 1'  # Run every Monday at 2 AM
  workflow_dispatch:

concurrency:
  group: security-${{ github.ref }}
  cancel-in-progress: true

jobs:
  dependency-scan:
    name: Dependency Scanning
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install safety pip-audit
    
    - name: Run Safety check
      run: |
        safety check --full-report
    
    - name: Run pip-audit
      run: |
        pip-audit --strict
    
    - name: Upload security report
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: dependency-scan-report
        path: |
          safety-report.json
          pip-audit-report.json
        retention-days: 30

  secret-scan:
    name: Secret Scanning
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      with:
        fetch-depth: 0
    
    - name: Run TruffleHog
      uses: trufflesecurity/trufflehog@main
      with:
        path: ./
        base: main
        head: HEAD
        extra_args: --debug --only-verified
    
    - name: Run Gitleaks
      uses: gitleaks/gitleaks-action@v2
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        GITLEAKS_CONFIG: .gitleaks.toml

  code-scan:
    name: Code Security Scan
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install Bandit
      run: |
        pip install bandit
    
    - name: Run Bandit
      run: |
        bandit -r src/ -f json -o bandit-report.json
    
    - name: Upload Bandit report
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: bandit-report
        path: bandit-report.json
        retention-days: 30

  container-scan:
    name: Container Scanning
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
    
    - name: Build Docker image
      run: |
        docker build -t mcp-platform:latest .
    
    - name: Run Trivy
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: 'mcp-platform:latest'
        format: 'sarif'
        output: 'trivy-results.sarif'
        severity: 'CRITICAL,HIGH'
    
    - name: Upload Trivy report
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: trivy-report
        path: trivy-results.sarif
        retention-days: 30
    
    - name: Upload to GitHub Security Tab
      uses: github/codeql-action/upload-sarif@v2
      if: always()
      with:
        sarif_file: trivy-results.sarif
```

## 🧹 Cleanup Workflow

**.github/workflows/cleanup.yml**
```yaml
name: Cleanup

on:
  schedule:
    - cron: '0 3 * * *'  # Run every day at 3 AM
  workflow_dispatch:

concurrency:
  group: cleanup
  cancel-in-progress: false

jobs:
  cleanup-artifacts:
    name: Cleanup Old Artifacts
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
    
    - name: Azure Login
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Set Azure subscription
      run: |
        az account set --subscription ${{ secrets.AZURE_SUBSCRIPTION_ID }}
    
    - name: Cleanup old Function App deployments
      run: |
        # List all Function Apps
        az functionapp list --query "[].{name:name, resourceGroup:resourceGroup}" -o tsv | while read -r app rg; do
          echo "Cleaning up old deployments for $app in $rg"
          
          # Keep last 5 deployments
          az functionapp deployment list \
            --name $app \
            --resource-group $rg \
            --query "[?active == \`false\`].{id:id, timestamp:timestamp}" -o json | \
          jq -r 'sort_by(.timestamp) | .[:-5] | .[].id' | while read -r deploymentId; do
            echo "Deleting old deployment: $deploymentId"
            az functionapp deployment delete --ids $deploymentId --yes
          done
        done
    
    - name: Cleanup old storage blobs
      run: |
        # Cleanup old artifacts in storage accounts
        az storage account list --query "[].{name:name, resourceGroup:resourceGroup}" -o tsv | while read -r account rg; do
          echo "Cleaning up old blobs in $account"
          
          # Get connection string
          conn_str=$(az storage account show-connection-string --name $account --resource-group $rg -o tsv)
          
          # List and delete old blobs (older than 30 days)
          az storage blob list \
            --account-name $account \
            --container-name artifacts \
            --query "[?properties.lastModified < \`$(date -d '30 days ago' +%Y-%m-%dT%H:%M:%SZ)\`].name" -o tsv | \
          while read -r blob; do
            echo "Deleting old blob: $blob"
            az storage blob delete \
              --account-name $account \
              --container-name artifacts \
              --name $blob \
              --yes
          done
        done
    
    - name: Azure Logout
      if: always()
      run: |
        az logout

  cleanup-github-artifacts:
    name: Cleanup GitHub Artifacts
    runs-on: ubuntu-latest
    
    steps:
    - name: Delete old workflow runs
      uses: Mattraks/delete-workflow-runs@v2
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
        repository: ${{ github.repository }}
        keep_minimum_runs: 30
        days_to_keep: 30
```

## 📅 Scheduled Tasks Workflow

**.github/workflows/scheduled.yml**
```yaml
name: Scheduled Tasks

on:
  schedule:
    - cron: '0 0 * * *'  # Run every day at midnight
  workflow_dispatch:

concurrency:
  group: scheduled
  cancel-in-progress: false

jobs:
  health-check:
    name: Health Check
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
    
    - name: Azure Login
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Set Azure subscription
      run: |
        az account set --subscription ${{ secrets.AZURE_SUBSCRIPTION_ID }}
    
    - name: Check Function App health
      run: |
        # Check all Function Apps
        az functionapp list --query "[].{name:name, resourceGroup:resourceGroup, state:state}" -o json | \
        jq -r '.[] | select(.state != "Running") | "Function App \(.name) in \(.resourceGroup) is not running (state: \(.state))"