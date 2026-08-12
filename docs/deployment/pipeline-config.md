# ⚙️ Pipeline Configuration Guide

## Overview

This guide covers the configuration options and best practices for setting up CI/CD pipelines for the MCP Platform Framework, including both Azure DevOps and GitHub Actions configurations.

## 📋 Pipeline Configuration Structure

The MCP Platform Framework uses a consistent pipeline configuration structure across both Azure DevOps and GitHub Actions:

```
├── azure-pipelines/          # Azure DevOps pipelines
│   ├── build.yml             # Build and test pipeline
│   ├── deploy.yml            # Deployment pipeline
│   ├── promote.yml           # Environment promotion pipeline
│   ├── templates/            # Reusable pipeline templates
│   │   ├── build-template.yml
│   │   ├── deploy-template.yml
│   │   └── variables.yml
│   └── environments/         # Environment-specific configs
│       ├── development.yml
│       ├── test.yml
│       ├── staging.yml
│       └── production.yml
│
└── .github/                  # GitHub Actions workflows
    └── workflows/
        ├── build.yml         # Build and test workflow
        ├── deploy.yml        # Deployment workflow
        ├── promote.yml       # Environment promotion workflow
        ├── security.yml      # Security scanning workflow
        ├── cleanup.yml       # Cleanup workflow
        └── scheduled.yml      # Scheduled tasks workflow
```

## 🎯 Pipeline Configuration Options

### Common Configuration Parameters

| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| `environment` | Target environment (development, test, staging, production) | development | ✅ |
| `pythonVersion` | Python version to use | 3.11 | ✅ |
| `buildId` | Build ID to deploy | latest | ❌ |
| `runTests` | Whether to run tests | true | ❌ |
| `runSmokeTests` | Whether to run smoke tests after deployment | true | ❌ |
| `useDeploymentSlots` | Use deployment slots for zero-downtime deployment | false | ❌ |
| `autoApprove` | Auto-approve deployments (not recommended for production) | false | ❌ |

### Environment-Specific Configuration

**Development Environment:**
```yaml
# Development-specific configuration
environment: development
pythonVersion: '3.11'
runTests: true
runSmokeTests: true
useDeploymentSlots: false
autoApprove: true  # Auto-approve for development
```

**Test Environment:**
```yaml
# Test-specific configuration
environment: test
pythonVersion: '3.11'
runTests: true
runSmokeTests: true
useDeploymentSlots: false
autoApprove: false  # Require manual approval
```

**Staging Environment:**
```yaml
# Staging-specific configuration
environment: staging
pythonVersion: '3.11'
runTests: true
runSmokeTests: true
useDeploymentSlots: false
autoApprove: false  # Require manual approval
```

**Production Environment:**
```yaml
# Production-specific configuration
environment: production
pythonVersion: '3.11'
runTests: true
runSmokeTests: true
useDeploymentSlots: true  # Use deployment slots for zero-downtime
autoApprove: false  # Always require manual approval
```

## 🏗️ Build Pipeline Configuration

### Build Configuration Options

**Basic Build Configuration:**
```yaml
# Basic build configuration
build:
  name: Build and Test
  runs-on: ubuntu-latest
  
  steps:
  - name: Checkout
    uses: actions/checkout@v4
    
  - name: Setup Python
    uses: actions/setup-python@v4
    with:
      python-version: '3.11'
      cache: 'pip'
    
  - name: Install Dependencies
    run: |
      pip install -r requirements.txt
      pip install -r requirements-dev.txt
    
  - name: Run Tests
    run: |
      pytest tests/unit --cov=mcp_framework
    
  - name: Build Package
    run: |
      python -m build
```

**Advanced Build Configuration:**
```yaml
# Advanced build configuration with caching and parallel testing
build:
  name: Build and Test
  runs-on: ubuntu-latest
  strategy:
    matrix:
      python-version: ['3.11', '3.12']
    
  steps:
  - name: Checkout
    uses: actions/checkout@v4
    with:
      fetch-depth: 0
    
  - name: Setup Python ${{ matrix.python-version }}
    uses: actions/setup-python@v4
    with:
      python-version: ${{ matrix.python-version }}
      cache: 'pip'
      cache-dependency-path: |
        requirements.txt
        requirements-dev.txt
    
  - name: Cache Test Data
    uses: actions/cache@v3
    with:
      path: ~/.cache/test-data
      key: ${{ runner.os }}-test-data-${{ hashFiles('tests/data/**') }}
    
  - name: Install Dependencies
    run: |
      python -m pip install --upgrade pip
      pip install -r requirements.txt
      pip install -r requirements-dev.txt
    
  - name: Lint Code
    run: |
      pip install flake8 black isort mypy
      flake8 src/ tests/ --max-line-length=120
      black --check src/ tests/
      isort --check src/ tests/
      mypy src/ --ignore-missing-imports
    
  - name: Run Unit Tests
    run: |
      pytest tests/unit -n auto --cov=mcp_framework --cov-report=xml
    
  - name: Run Integration Tests
    if: github.ref == 'refs/heads/main'
    run: |
      pytest tests/integration -n auto
    
  - name: Run Security Tests
    if: github.ref == 'refs/heads/main'
    run: |
      pytest tests/security
    
  - name: Build Package
    if: github.ref == 'refs/heads/main'
    run: |
      pip install build twine
      python -m build
```

### Test Configuration

**Unit Test Configuration:**
```yaml
# Unit test configuration
unit_tests:
  enabled: true
  coverage:
    enabled: true
    minimum_coverage: 80
    exclude:
      - tests/*
      - venv/*
  parallel: true
  workers: 4
  timeout: 300  # 5 minutes
```

**Integration Test Configuration:**
```yaml
# Integration test configuration
integration_tests:
  enabled: true
  test_environment: test
  test_data:
    fabric_workspace: test-workspace
    semantic_models:
      - TestDonorModel
      - TestFinancialModel
  timeout: 600  # 10 minutes
```

**Security Test Configuration:**
```yaml
# Security test configuration
security_tests:
  enabled: true
  dependency_scanning: true
  secret_detection: true
  vulnerability_assessment: true
  tools:
    - bandit
    - safety
    - pip-audit
    - trivy
```

## 🚀 Deployment Pipeline Configuration

### Deployment Configuration Options

**Basic Deployment Configuration:**
```yaml
# Basic deployment configuration
deploy:
  name: Deploy
  runs-on: ubuntu-latest
  environment: development
  
  steps:
  - name: Checkout
    uses: actions/checkout@v4
    
  - name: Azure Login
    uses: azure/login@v1
    with:
      creds: ${{ secrets.AZURE_CREDENTIALS }}
    
  - name: Deploy Function App
    run: |
      az functionapp deployment source config-zip \
        --name mcp-dev-func \
        --resource-group mcp-dev-rg \
        --src dist/*.zip
    
  - name: Set Application Settings
    run: |
      az functionapp config appsettings set \
        --name mcp-dev-func \
        --resource-group mcp-dev-rg \
        --settings MCP_ENVIRONMENT=development
```

**Advanced Deployment Configuration:**
```yaml
# Advanced deployment configuration with zero-downtime
deploy:
  name: Deploy
  runs-on: ubuntu-latest
  environment: production
  
  steps:
  - name: Checkout
    uses: actions/checkout@v4
    
  - name: Azure Login
    uses: azure/login@v1
    with:
      creds: ${{ secrets.AZURE_CREDENTIALS }}
    
  - name: Create Deployment Slot
    run: |
      az functionapp deployment slot create \
        --name mcp-prod-func \
        --resource-group mcp-prod-rg \
        --slot staging
    
  - name: Deploy to Staging Slot
    run: |
      az functionapp deployment source config-zip \
        --name mcp-prod-func \
        --resource-group mcp-prod-rg \
        --slot staging \
        --src dist/*.zip
    
  - name: Set Application Settings
    run: |
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
    
  - name: Warm Up Staging Slot
    run: |
      for i in {1..5}; do
        curl -X POST https://mcp-prod-func-staging.azurewebsites.net/api/tools/HealthCheck \
          -H "Content-Type: application/json" \
          -d '{"arguments": {}}' && break || sleep 10
      done
    
  - name: Swap Slots
    run: |
      az functionapp deployment slot swap \
        --name mcp-prod-func \
        --resource-group mcp-prod-rg \
        --slot staging \
        --target-slot production
    
  - name: Clean Up Old Slot
    run: |
      az functionapp deployment slot delete \
        --name mcp-prod-func \
        --resource-group mcp-prod-rg \
        --slot staging
```

### Deployment Slot Configuration

**Deployment Slot Settings:**
```yaml
# Deployment slot configuration
deployment_slots:
  enabled: true
  auto_swap: false  # Manual swap for production
  warmup_enabled: true
  warmup_endpoint: /api/tools/HealthCheck
  warmup_retries: 5
  warmup_delay: 10
  
  slots:
    staging:
      auto_scale: false
      min_instances: 1
      max_instances: 1
    
    production:
      auto_scale: true
      min_instances: 2
      max_instances: 10
```

### Application Settings Configuration

**Environment-Specific Settings:**
```yaml
# Application settings for each environment
application_settings:
  development:
    MCP_ENVIRONMENT: development
    AZURE_SUBSCRIPTION_ID: dev-subscription-id
    AZURE_RESOURCE_GROUP: mcp-dev-rg
    FABRIC_TENANT_ID: dev-tenant-id
    FABRIC_WORKSPACE_ID: dev-workspace-id
    DEBUG: true
    LOG_LEVEL: DEBUG
    
  test:
    MCP_ENVIRONMENT: test
    AZURE_SUBSCRIPTION_ID: test-subscription-id
    AZURE_RESOURCE_GROUP: mcp-test-rg
    KEY_VAULT_URI: https://mcp-test-kv.vault.azure.net/
    FABRIC_TENANT_ID: test-tenant-id
    FABRIC_WORKSPACE_ID: test-workspace-id
    DEBUG: false
    LOG_LEVEL: INFO
    
  staging:
    MCP_ENVIRONMENT: staging
    AZURE_SUBSCRIPTION_ID: staging-subscription-id
    AZURE_RESOURCE_GROUP: mcp-staging-rg
    KEY_VAULT_URI: https://mcp-staging-kv.vault.azure.net/
    FABRIC_TENANT_ID: staging-tenant-id
    FABRIC_WORKSPACE_ID: staging-workspace-id
    DEBUG: false
    LOG_LEVEL: INFO
    
  production:
    MCP_ENVIRONMENT: production
    AZURE_SUBSCRIPTION_ID: prod-subscription-id
    AZURE_RESOURCE_GROUP: mcp-prod-rg
    KEY_VAULT_URI: https://mcp-prod-kv.vault.azure.net/
    FABRIC_TENANT_ID: prod-tenant-id
    FABRIC_WORKSPACE_ID: prod-workspace-id
    DEBUG: false
    LOG_LEVEL: WARNING
```

## 🔄 Environment Promotion Configuration

### Promotion Rules

**Promotion Path Configuration:**
```yaml
# Promotion path configuration
promotion:
  allowed_paths:
    - from: development
      to: test
      auto_approve: true
      
    - from: test
      to: staging
      auto_approve: false
      required_approvers:
        - devops@domain.com
        - qa@domain.com
      
    - from: staging
      to: production
      auto_approve: false
      required_approvers:
        - devops@domain.com
        - security@domain.com
        - business-owner@domain.com
      
  validation:
    required_checks:
      - build_success
      - unit_tests_pass
      - integration_tests_pass
      - security_scan_pass
      - code_review_approved
```

### Promotion Workflow Configuration

**Manual Promotion Configuration:**
```yaml
# Manual promotion configuration
manual_promotion:
  enabled: true
  notification:
    email: true
    teams: true
    slack: true
    
  approval:
    timeout_minutes: 480  # 8 hours
    reminders:
      enabled: true
      interval_minutes: 60
      
  validation:
    pre_promotion:
      - check_source_environment_health
      - check_target_environment_ready
      - validate_configuration
      
    post_promotion:
      - run_smoke_tests
      - verify_deployment
      - notify_stakeholders
```

**Automated Promotion Configuration:**
```yaml
# Automated promotion configuration (for non-production environments)
automated_promotion:
  enabled: true
  environments:
    - from: development
      to: test
      trigger: on_main_merge
      conditions:
        - build_success
        - unit_tests_pass
        
    - from: test
      to: staging
      trigger: manual
      conditions:
        - build_success
        - unit_tests_pass
        - integration_tests_pass
```

## 🔐 Security Configuration

### Pipeline Security Settings

**Security Scanning Configuration:**
```yaml
# Security scanning configuration
security_scanning:
  enabled: true
  
  dependency_scanning:
    enabled: true
    tools:
      - pip-audit
      - safety
    severity_threshold: high
    
  secret_scanning:
    enabled: true
    tools:
      - trufflehog
      - gitleaks
    patterns:
      - azure
      - aws
      - github
      - generic
    
  code_scanning:
    enabled: true
    tools:
      - bandit
      - semgrep
    
  container_scanning:
    enabled: true
    tools:
      - trivy
    severity_threshold: critical
```

**Access Control Configuration:**
```yaml
# Access control configuration
access_control:
  environments:
    development:
      allowed_users:
        - developer1@domain.com
        - developer2@domain.com
      allowed_teams:
        - developers
      
    test:
      allowed_users:
        - devops1@domain.com
        - qa1@domain.com
      allowed_teams:
        - devops
        - qa
      
    staging:
      allowed_users:
        - devops1@domain.com
        - qa1@domain.com
        - business1@domain.com
      allowed_teams:
        - devops
        - qa
        - business
      
    production:
      allowed_users:
        - devops1@domain.com
        - security1@domain.com
        - business1@domain.com
      allowed_teams:
        - devops
        - security
        - business
      
  approvals:
    development:
      required: false
      
    test:
      required: false
      
    staging:
      required: true
      minimum_approvers: 1
      
    production:
      required: true
      minimum_approvers: 2
```

### Secret Management Configuration

**Secret Handling Configuration:**
```yaml
# Secret management configuration
secrets:
  management: azure_key_vault
  
  azure_key_vault:
    enabled: true
    key_vault_uri: ${KEY_VAULT_URI}
    
  gitHub_secrets:
    enabled: true
    secrets:
      - AZURE_CREDENTIALS
      - AZURE_SUBSCRIPTION_ID
      - KEY_VAULT_URI
      - FABRIC_TENANT_ID
      - FABRIC_WORKSPACE_ID
    
  rotation:
    enabled: true
    frequency: 90_days
    notification:
      enabled: true
      days_before_expiry: 30
```

## 📊 Monitoring and Alerting Configuration

### Pipeline Monitoring Configuration

**Monitoring Settings:**
```yaml
# Pipeline monitoring configuration
monitoring:
  enabled: true
  
  metrics:
    - name: pipeline_success_rate
      description: Percentage of successful pipeline runs
      target: 95
      
    - name: pipeline_duration
      description: Average pipeline duration
      target: 300  # 5 minutes
      
    - name: deployment_frequency
      description: Number of deployments per day
      target: 10
      
    - name: mean_time_to_recovery
      description: Average time to recover from failures
      target: 60  # 1 hour
  
  alerts:
    - name: pipeline_failure
      condition: pipeline_status == 'failed'
      severity: high
      notification:
        - email: devops@domain.com
        - teams: devops-team
        - slack: #devops
      
    - name: deployment_failure
      condition: deployment_status == 'failed'
      severity: critical
      notification:
        - email: devops@domain.com,security@domain.com
        - teams: devops-team,security-team
        - pagerduty: devops-pagerduty
      
    - name: long_running_pipeline
      condition: pipeline_duration > 600  # 10 minutes
      severity: medium
      notification:
        - email: devops@domain.com
```

### Logging Configuration

**Pipeline Logging Settings:**
```yaml
# Pipeline logging configuration
logging:
  enabled: true
  
  levels:
    development: debug
    test: info
    staging: info
    production: warning
  
  retention:
    development: 7_days
    test: 30_days
    staging: 90_days
    production: 365_days
  
  destinations:
    - azure_monitor
    - log_analytics
    - storage_account
  
  audit_logging:
    enabled: true
    log_all_actions: true
    log_secrets: false
```

## 🧹 Cleanup Configuration

### Artifact Cleanup Configuration

**Artifact Retention Configuration:**
```yaml
# Artifact cleanup configuration
cleanup:
  artifacts:
    retention_days: 30
    max_artifacts: 100
    
    patterns:
      - name: build-artifacts
        retention_days: 30
        max_size_mb: 1000
        
      - name: test-results
        retention_days: 90
        max_size_mb: 500
        
      - name: logs
        retention_days: 30
        max_size_mb: 200
  
  deployments:
    retention_days: 90
    max_deployments: 50
    
    patterns:
      - name: development
        retention_days: 7
        max_deployments: 10
        
      - name: test
        retention_days: 30
        max_deployments: 20
        
      - name: staging
        retention_days: 90
        max_deployments: 30
        
      - name: production
        retention_days: 365
        max_deployments: 50
```

### Resource Cleanup Configuration

**Resource Cleanup Settings:**
```yaml
# Resource cleanup configuration
resource_cleanup:
  enabled: true
  
  schedules:
    - name: daily_cleanup
      cron: '0 3 * * *'  # 3 AM every day
      environments:
        - development
        - test
      
    - name: weekly_cleanup
      cron: '0 4 * * 1'  # 4 AM every Monday
      environments:
        - staging
      
    - name: monthly_cleanup
      cron: '0 5 1 * *'  # 5 AM on the 1st of every month
      environments:
        - production
  
  actions:
    - name: delete_old_deployments
      enabled: true
      keep_last: 5
      
    - name: delete_old_artifacts
      enabled: true
      keep_last: 10
      
    - name: delete_old_logs
      enabled: true
      keep_last: 30
```

## 📅 Scheduled Tasks Configuration

### Scheduled Pipeline Configuration

**Scheduled Tasks:**
```yaml
# Scheduled tasks configuration
scheduled_tasks:
  - name: daily_health_check
    schedule: '0 0 * * *'  # Midnight every day
    description: Daily health check of all Function Apps
    enabled: true
    
    actions:
      - check_function_app_health
      - check_key_vault_access
      - check_fabric_connectivity
      - send_health_report
    
    notification:
      on_success: false
      on_failure: true
      recipients:
        - devops@domain.com
    
  - name: weekly_security_scan
    schedule: '0 2 * * 1'  # 2 AM every Monday
    description: Weekly security scan
    enabled: true
    
    actions:
      - dependency_scan
      - secret_scan
      - vulnerability_scan
      - generate_security_report
    
    notification:
      on_success: true
      on_failure: true
      recipients:
        - security@domain.com
        - devops@domain.com
    
  - name: monthly_performance_test
    schedule: '0 3 1 * *'  # 3 AM on the 1st of every month
    description: Monthly performance testing
    enabled: true
    
    actions:
      - run_load_tests
      - run_stress_tests
      - generate_performance_report
    
    notification:
      on_success: true
      on_failure: true
      recipients:
        - devops@domain.com
        - performance@domain.com
```

## 🛡️ Compliance Configuration

### Compliance Settings

**Compliance Configuration:**
```yaml
# Compliance configuration
compliance:
  enabled: true
  
  standards:
    - ISO27001
    - SOC2
    - GDPR
    - HIPAA
  
  requirements:
    - name: pipeline_approvals
      description: All production deployments require manual approval
      enabled: true
      environments:
        - production
      
    - name: security_scanning
      description: All code must pass security scanning before deployment
      enabled: true
      environments:
        - test
        - staging
        - production
      
    - name: audit_logging
      description: All pipeline actions must be logged
      enabled: true
      environments:
        - development
        - test
        - staging
        - production
      
    - name: access_control
      description: Access to production environments must be restricted
      enabled: true
      environments:
        - production
  
  reporting:
    enabled: true
    frequency: monthly
    recipients:
      - compliance@domain.com
      - security@domain.com
```

### Governance Configuration

**Governance Settings:**
```yaml
# Governance configuration
governance:
  enabled: true
  
  tagging:
    enabled: true
    required_tags:
      - Environment
      - Owner
      - CostCenter
      - Compliance
      - Pipeline
    
  naming_conventions:
    enabled: true
    patterns:
      function_app: mcp-[environment]-func
      resource_group: mcp-[environment]-rg
      key_vault: mcp-[environment]-kv
      storage_account: mcp[environment]storage
  
  resource_limits:
    enabled: true
    limits:
      function_app:
        development:
          max_instances: 1
          sku: Y1
        test:
          max_instances: 2
          sku: B1
        staging:
          max_instances: 3
          sku: P1v2
        production:
          max_instances: 10
          sku: P2v2
```

## ⚡ Performance Optimization Configuration

### Pipeline Performance Settings

**Performance Configuration:**
```yaml
# Pipeline performance configuration
performance:
  enabled: true
  
  parallelism:
    enabled: true
    max_parallel_jobs: 4
    
    strategies:
      test:
        parallel: true
        workers: 4
        
      build:
        parallel: false
        
      deploy:
        parallel: false
  
  caching:
    enabled: true
    
    caches:
      - name: pip_cache
        path: ~/.cache/pip
        key: pip-${{ hashFiles('requirements.txt') }}
        restore_keys: |
          pip-
      
      - name: test_data_cache
        path: ~/.cache/test-data
        key: test-data-${{ hashFiles('tests/data/**') }}
        restore_keys: |
          test-data-
      
      - name: build_cache
        path: .cache
        key: build-${{ hashFiles('src/**', 'setup.py') }}
        restore_keys: |
          build-
  
  timeout:
    build: 300  # 5 minutes
    test: 600  # 10 minutes
    deploy: 900  # 15 minutes
    overall: 1800  # 30 minutes
```

### Resource Optimization

**Resource Configuration:**
```yaml
# Resource optimization configuration
resources:
  agents:
    development:
      type: ubuntu-latest
      size: small
      
    test:
      type: ubuntu-latest
      size: medium
      
    staging:
      type: ubuntu-latest
      size: medium
      
    production:
      type: ubuntu-latest
      size: large
  
  storage:
    artifacts:
      retention_days: 30
      max_size_gb: 10
      
    logs:
      retention_days: 90
      max_size_gb: 5
```

## 🛠️ Configuration Management

### Configuration File Structure

**Recommended Configuration Files:**
```
config/
├── pipeline/                  # Pipeline-specific configuration
│   ├── azure-devops.yml       # Azure DevOps pipeline config
│   ├── github-actions.yml     # GitHub Actions workflow config
│   ├── build.yml              # Build configuration
│   ├── deploy.yml             # Deployment configuration
│   ├── environments/          # Environment-specific configs
│   │   ├── development.yml
│   │   ├── test.yml
│   │   ├── staging.yml
│   │   └── production.yml
│   └── templates/             # Reusable templates
│       ├── build-template.yml
│       └── deploy-template.yml
│
└── defaults.yml              # Default configuration values
```

### Configuration Validation

**Configuration Schema:**
```yaml
# Configuration schema for validation
schema:
  type: object
  properties:
    environment:
      type: string
      enum: [development, test, staging, production]
      
    pythonVersion:
      type: string
      pattern: ^3\.(11|12)$
      
    buildId:
      type: string
      pattern: ^[a-f0-9]{8}$
      
    runTests:
      type: boolean
      
    runSmokeTests:
      type: boolean
      
    useDeploymentSlots:
      type: boolean
      
  required:
    - environment
    - pythonVersion
```

**Configuration Validation Script:**
```python
# config/validate.py
import json
import jsonschema
from pathlib import Path

# Load configuration
config_path = Path(__file__).parent / "pipeline" / "config.json"
with open(config_path) as f:
    config = json.load(f)

# Load schema
schema_path = Path(__file__).parent / "schema.json"
with open(schema_path) as f:
    schema = json.load(f)

# Validate configuration
try:
    jsonschema.validate(instance=config, schema=schema)
    print("✅ Configuration is valid")
except jsonschema.ValidationError as e:
    print(f"❌ Configuration validation failed: {e}")
    raise
```

## 📚 Best Practices

### Pipeline Configuration Best Practices

1. **⭐ Use Environment-Specific Configuration**
   - Create separate configuration files for each environment
   - Use environment variables for sensitive data
   - Implement environment-specific settings and limits

2. **⭐ Implement Security Controls**
   - Use manual approvals for production deployments
   - Enable security scanning for all environments
   - Implement least privilege access control
   - Rotate secrets regularly

3. **⭐ Optimize Performance**
   - Use caching for dependencies and build artifacts
   - Run tests in parallel where possible
   - Set appropriate timeouts for each job
   - Use appropriate agent sizes for each environment

4. **⭐ Enable Monitoring and Alerting**
   - Monitor pipeline success rates and durations
   - Set up alerts for pipeline failures
   - Log all pipeline actions for audit purposes
   - Implement compliance reporting

5. **⭐ Implement Cleanup Processes**
   - Set artifact retention policies
   - Clean up old deployments regularly
   - Remove unused resources
   - Optimize storage usage

6. **⭐ Use Infrastructure as Code**
   - Define pipeline configuration in code
   - Version control all configuration files
   - Use templates for reusable components
   - Implement configuration validation

## 🛠️ Troubleshooting

### Common Configuration Issues

#### Invalid Configuration Format

**Error**: `Invalid YAML syntax in pipeline configuration`

**Solution**:
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('azure-pipelines/build.yml'))"

# Or use yamllint
yamllint azure-pipelines/build.yml
```

#### Missing Required Configuration

**Error**: `Required configuration 'environment' not found`

**Solution**:
```yaml
# Add the missing configuration
environment: development
```

#### Invalid Environment Name

**Error**: `Invalid environment: 'dev'. Must be one of: development, test, staging, production`

**Solution**:
```yaml
# Use a valid environment name
environment: development
```

#### Configuration Validation Failed

**Error**: `Configuration validation failed: 'pythonVersion' is a required property`

**Solution**:
```yaml
# Add the missing required property
pythonVersion: '3.11'
```

#### Pipeline Timeout

**Error**: `Job timed out after 60 minutes`

**Solution**:
```yaml
# Increase the timeout
timeoutInMinutes: 120
```

## 📚 Next Steps

- **[Azure DevOps Pipelines](azure-devops.md)** - Set up Azure DevOps pipelines
- **[GitHub Actions Workflows](github-actions.md)** - Set up GitHub Actions workflows
- **[Deployment Overview](overview.md)** - Understand the deployment process
- **[Function App Deployment](function-app.md)** - Deploy to Azure Function App

## 🔗 Related Documentation

- [Azure DevOps Pipeline Documentation](https://docs.microsoft.com/en-us/azure/devops/pipelines/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [YAML Configuration Reference](https://yaml.org/spec/1.2/spec.html)
- [JSON Schema Validation](https://json-schema.org/)

---

**Need help?** Check the [FAQ](../FAQ.md) or open an issue in the repository.
