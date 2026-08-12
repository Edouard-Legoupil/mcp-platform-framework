# 🚀 Deployment Module

The Deployment Module provides CI/CD pipeline templates and deployment automation for Azure Function Apps, enabling domains to deploy their MCP services with standardized infrastructure and processes.

## 🎯 Overview

The Deployment Module handles:
- **Build Validation**: Code quality checks, dependency validation, package building
- **Testing Frameworks**: Unit, integration, performance, and security testing
- **Security Scanning**: Dependency vulnerability scanning, secret detection, code analysis
- **Deployment Pipelines**: ARM template deployment, Bicep template deployment, Azure DevOps integration, GitHub Actions support

## 🏗️ Architecture

```
┌───────────────────────────────────────────┐
│          Deployment Module                │
├───────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Build           │  │ Testing         │ │
│  │ Validation      │  │ Frameworks      │ │
│  └─────────────────┘  └─────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Security        │  │ Deployment      │ │
│  │ Scanning        │  │ Pipelines       │ │
│  └─────────────────┘  └─────────────────┘ │
└───────────────────────────────────────────┘
```

## 🚀 Quick Start

### Basic Deployment

```bash
# Deploy using Azure CLI
az deployment group create \
    --resource-group your-resource-group \
    --template-file deployment/main.bicep \
    --parameters @deployment/parameters/dev.json
```

### Configuration

```python
# deployment/config.py
from platform.deployment import DeploymentConfig

DEPLOYMENT_CONFIG = DeploymentConfig(
    # Deployment settings
    deployment_type="function_app",
    target_platform="azure",
    
    # Azure settings
    azure={
        "subscription_id": "your-subscription-id",
        "resource_group": "your-resource-group",
        "location": "eastus",
        "function_app_name": "mcp-donor-dev"
    },
    
    # Build settings
    build={
        "python_version": "3.11",
        "requirements_file": "requirements.txt",
        "build_command": "pip install -r requirements.txt",
        "output_directory": "./dist"
    },
    
    # Testing settings
    testing={
        "unit_tests": {
            "enabled": True,
            "command": "pytest tests/unit",
            "coverage": True
        },
        "integration_tests": {
            "enabled": True,
            "command": "pytest tests/integration",
            "environment": "test"
        },
        "security_tests": {
            "enabled": True,
            "command": "pytest tests/security"
        },
        "performance_tests": {
            "enabled": False,
            "command": "pytest tests/performance"
        }
    },
    
    # Security scanning
    security_scanning={
        "dependency_scanning": {
            "enabled": True,
            "tool": "safety",
            "severity_threshold": "high"
        },
        "secret_scanning": {
            "enabled": True,
            "tool": "gitleaks",
            "config_file": ".gitleaks.toml"
        },
        "code_analysis": {
            "enabled": True,
            "tool": "bandit",
            "config_file": ".bandit.yml"
        }
    },
    
    # CI/CD settings
    ci_cd={
        "pipeline_type": "azure_devops",  # or "github_actions"
        "trigger": {
            "branches": ["main", "develop"],
            "paths": ["src/**", "tests/**"]
        },
        "schedule": {
            "enabled": True,
            "cron": "0 0 * * *"  # Daily at midnight
        }
    }
)
```

## 🔧 Configuration

### Environment Variables

```bash
# Deployment Configuration
DEPLOYMENT_TYPE=function_app
TARGET_PLATFORM=azure

# Azure Configuration
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=your-resource-group
AZURE_LOCATION=eastus
AZURE_FUNCTION_APP_NAME=mcp-donor-dev

# Build Configuration
BUILD_PYTHON_VERSION=3.11
BUILD_REQUIREMENTS_FILE=requirements.txt
BUILD_OUTPUT_DIRECTORY=./dist

# Testing Configuration
TEST_UNIT_ENABLED=true
TEST_INTEGRATION_ENABLED=true
TEST_SECURITY_ENABLED=true

# Security Scanning
SECURITY_DEPENDENCY_SCANNING_ENABLED=true
SECURITY_SECRET_SCANNING_ENABLED=true
SECURITY_CODE_ANALYSIS_ENABLED=true

# CI/CD Configuration
CI_CD_PIPELINE_TYPE=azure_devops
CI_CD_TRIGGER_BRANCHES=main,develop
CI_CD_SCHEDULE_ENABLED=true
```

### Configuration File

```yaml
# deployment/config.yaml
deployment:
  type: function_app
  target_platform: azure
  
  azure:
    subscription_id: ${AZURE_SUBSCRIPTION_ID}
    resource_group: ${AZURE_RESOURCE_GROUP}
    location: ${AZURE_LOCATION}
    function_app_name: ${AZURE_FUNCTION_APP_NAME}
    
    # Function App settings
    function_app:
      runtime: python
      runtime_version: 3.11
      os: Linux
      plan:
        type: Consumption  # or Premium, Dedicated
        tier: Dynamic  # or PremiumV2, Standard
        
      # Scale settings
      scale:
        min_instances: 1
        max_instances: 10
        max_concurrent_requests: 100
        
      # Networking
      networking:
        vnet_integration: false
        private_endpoints: true
        allowed_ips: []
        
      # Identity
      identity:
        type: SystemAssigned  # or UserAssigned, SystemAssignedUserAssigned
        user_assigned_identity: null
        
      # Storage
      storage:
        account_name: null  # Auto-generated if not specified
        mount_path: /home/site/wwwroot
        
  build:
    python_version: ${BUILD_PYTHON_VERSION}
    requirements_file: ${BUILD_REQUIREMENTS_FILE}
    build_command: "pip install -r requirements.txt"
    output_directory: ${BUILD_OUTPUT_DIRECTORY}
    
    # Build artifacts
    artifacts:
      - name: function_app
        path: ./dist
        
  testing:
    unit_tests:
      enabled: ${TEST_UNIT_ENABLED}
      command: "pytest tests/unit -v"
      coverage: true
      coverage_command: "pytest tests/unit --cov=src --cov-report=xml"
      
    integration_tests:
      enabled: ${TEST_INTEGRATION_ENABLED}
      command: "pytest tests/integration -v"
      environment: test
      
    security_tests:
      enabled: ${TEST_SECURITY_ENABLED}
      command: "pytest tests/security -v"
      
    performance_tests:
      enabled: false
      command: "pytest tests/performance -v"
      
  security_scanning:
    dependency_scanning:
      enabled: ${SECURITY_DEPENDENCY_SCANNING_ENABLED}
      tool: safety
      severity_threshold: high
      fail_on_vulnerability: true
      
    secret_scanning:
      enabled: ${SECURITY_SECRET_SCANNING_ENABLED}
      tool: gitleaks
      config_file: .gitleaks.toml
      fail_on_secret: true
      
    code_analysis:
      enabled: ${SECURITY_CODE_ANALYSIS_ENABLED}
      tool: bandit
      config_file: .bandit.yml
      fail_on_issue: true
      
  ci_cd:
    pipeline_type: ${CI_CD_PIPELINE_TYPE}
    
    trigger:
      branches:
        - main
        - develop
      paths:
        - src/**
        - tests/**
      
    schedule:
      enabled: ${CI_CD_SCHEDULE_ENABLED}
      cron: "0 0 * * *"
      
    # Azure DevOps specific
    azure_devops:
      pool:
        name: Azure Pipelines
        vm_image: ubuntu-latest
        
      stages:
        - name: Build
          depends_on: []
          
        - name: Test
          depends_on: [Build]
          
        - name: Security
          depends_on: [Build]
          
        - name: Deploy
          depends_on: [Test, Security]
          condition: succeeded()
```

## 🎯 API Reference

### Functions

#### `deploy(config, environment)`

Deploys the application to the specified environment.

```python
from platform.deployment import deploy, DeploymentConfig

# Create deployment configuration
config = DeploymentConfig(
    deployment_type="function_app",
    target_platform="azure",
    azure={
        "subscription_id": "your-subscription-id",
        "resource_group": "your-resource-group",
        "function_app_name": "mcp-donor-dev"
    }
)

# Deploy to Dev environment
deploy(config, environment="Dev")

# Deploy to Production environment
deploy(config, environment="Production")
```

**Parameters:**
- `config` (DeploymentConfig): Deployment configuration
- `environment` (str): Environment to deploy to (Dev, Test, Production)

**Returns:**
- `DeploymentResult`: Result of the deployment

#### `build_package(config)`

Builds the deployment package.

```python
from platform.deployment import build_package, DeploymentConfig

config = DeploymentConfig(
    build={
        "python_version": "3.11",
        "requirements_file": "requirements.txt",
        "build_command": "pip install -r requirements.txt",
        "output_directory": "./dist"
    }
)

# Build package
result = build_package(config)
print(f"Build successful: {result.success}")
print(f"Package path: {result.package_path}")
```

**Parameters:**
- `config` (DeploymentConfig): Deployment configuration

**Returns:**
- `BuildResult`: Result of the build

#### `run_tests(config, test_type=None)`

Runs tests based on configuration.

```python
from platform.deployment import run_tests, DeploymentConfig

config = DeploymentConfig(
    testing={
        "unit_tests": {
            "enabled": True,
            "command": "pytest tests/unit"
        },
        "integration_tests": {
            "enabled": True,
            "command": "pytest tests/integration"
        }
    }
)

# Run all tests
result = run_tests(config)

# Run specific test type
result = run_tests(config, test_type="unit")
```

**Parameters:**
- `config` (DeploymentConfig): Deployment configuration
- `test_type` (str, optional): Type of tests to run (unit, integration, security, performance)

**Returns:**
- `TestResult`: Result of the tests

#### `run_security_scan(config, scan_type=None)`

Runs security scanning based on configuration.

```python
from platform.deployment import run_security_scan, DeploymentConfig

config = DeploymentConfig(
    security_scanning={
        "dependency_scanning": {
            "enabled": True,
            "tool": "safety"
        },
        "secret_scanning": {
            "enabled": True,
            "tool": "gitleaks"
        }
    }
)

# Run all security scans
result = run_security_scan(config)

# Run specific scan type
result = run_security_scan(config, scan_type="dependency")
```

**Parameters:**
- `config` (DeploymentConfig): Deployment configuration
- `scan_type` (str, optional): Type of scan to run (dependency, secret, code)

**Returns:**
- `SecurityScanResult`: Result of the security scan

### Classes

#### `DeploymentConfig`

Main deployment configuration class.

```python
from platform.deployment import DeploymentConfig

# Create deployment configuration
config = DeploymentConfig(
    deployment_type="function_app",
    target_platform="azure",
    
    azure={
        "subscription_id": "your-subscription-id",
        "resource_group": "your-resource-group",
        "location": "eastus",
        "function_app_name": "mcp-donor-dev"
    },
    
    build={
        "python_version": "3.11",
        "requirements_file": "requirements.txt",
        "build_command": "pip install -r requirements.txt",
        "output_directory": "./dist"
    },
    
    testing={
        "unit_tests": {"enabled": True, "command": "pytest tests/unit"},
        "integration_tests": {"enabled": True, "command": "pytest tests/integration"}
    },
    
    security_scanning={
        "dependency_scanning": {"enabled": True, "tool": "safety"},
        "secret_scanning": {"enabled": True, "tool": "gitleaks"}
    },
    
    ci_cd={
        "pipeline_type": "azure_devops",
        "trigger": {"branches": ["main", "develop"]}
    }
)

# Access configuration values
print(f"Deployment type: {config.deployment_type}")
print(f"Function App name: {config.azure.function_app_name}")
print(f"Python version: {config.build.python_version}")
print(f"Unit tests enabled: {config.testing.unit_tests.enabled}")
```

**Parameters:**
- `deployment_type` (str): Type of deployment (function_app, container, etc.)
- `target_platform` (str): Target platform (azure, aws, etc.)
- `azure` (dict): Azure-specific configuration
- `build` (dict): Build configuration
- `testing` (dict): Testing configuration
- `security_scanning` (dict): Security scanning configuration
- `ci_cd` (dict): CI/CD configuration

#### `DeploymentResult`

Result of a deployment operation.

```python
from platform.deployment import DeploymentResult

# Create deployment result
result = DeploymentResult(
    success=True,
    deployment_id="deploy-20260501-103000-001",
    environment="Dev",
    start_time=datetime.utcnow(),
    end_time=datetime.utcnow(),
    duration=45.5,
    status="Succeeded",
    message="Deployment completed successfully",
    resource_id="/subscriptions/.../Microsoft.Web/sites/mcp-donor-dev",
    endpoint="https://mcp-donor-dev.azurewebsites.net"
)

# Access result properties
print(f"Success: {result.success}")
print(f"Deployment ID: {result.deployment_id}")
print(f"Duration: {result.duration} seconds")
print(f"Status: {result.status}")
print(f"Endpoint: {result.endpoint}")
```

**Attributes:**
- `success` (bool): Whether deployment was successful
- `deployment_id` (str): Unique deployment ID
- `environment` (str): Environment deployed to
- `start_time` (datetime): Deployment start time
- `end_time` (datetime): Deployment end time
- `duration` (float): Deployment duration in seconds
- `status` (str): Deployment status
- `message` (str): Deployment message
- `resource_id` (str): Azure resource ID
- `endpoint` (str): Deployment endpoint
- `errors` (List[str]): List of errors (if any)
- `warnings` (List[str]): List of warnings (if any)

#### `AzureDeployer`

Handles deployment to Azure.

```python
from platform.deployment import AzureDeployer, DeploymentConfig

# Create Azure deployer
deployer = AzureDeployer(
    subscription_id="your-subscription-id",
    resource_group="your-resource-group"
)

# Deploy Function App
result = deployer.deploy_function_app(
    name="mcp-donor-dev",
    location="eastus",
    runtime="python",
    runtime_version="3.11",
    package_path="./dist",
    config=DeploymentConfig(...)
)

# Deploy using ARM template
result = deployer.deploy_arm_template(
    template_path="deployment/main.bicep",
    parameters={
        "functionAppName": "mcp-donor-dev",
        "location": "eastus",
        "storageAccountName": "mcpdonordevstorage"
    }
)

# Get deployment status
status = deployer.get_deployment_status("mcp-donor-dev")

# Delete deployment
deployer.delete_deployment("mcp-donor-dev")
```

**Parameters:**
- `subscription_id` (str): Azure subscription ID
- `resource_group` (str): Azure resource group
- `default_location` (str, optional): Default Azure location

**Methods:**
- `deploy_function_app(name, **kwargs)`: Deploy a Function App
- `deploy_arm_template(template_path, parameters)`: Deploy using ARM template
- `deploy_bicep_template(template_path, parameters)`: Deploy using Bicep template
- `get_deployment_status(name)`: Get deployment status
- `list_deployments()`: List all deployments
- `delete_deployment(name)`: Delete a deployment
- `update_deployment(name, **kwargs)`: Update a deployment

#### `PipelineGenerator`

Generates CI/CD pipeline files.

```python
from platform.deployment import PipelineGenerator, DeploymentConfig

# Create pipeline generator
generator = PipelineGenerator(
    pipeline_type="azure_devops",
    config=DeploymentConfig(...)
)

# Generate Azure DevOps pipeline
pipeline_yaml = generator.generate_azure_devops_pipeline()

# Generate GitHub Actions workflow
workflow_yaml = generator.generate_github_actions_workflow()

# Save pipeline file
generator.save_pipeline_file("azure-pipelines.yml")
```

**Parameters:**
- `pipeline_type` (str): Type of pipeline (azure_devops, github_actions)
- `config` (DeploymentConfig): Deployment configuration

**Methods:**
- `generate_azure_devops_pipeline()`: Generate Azure DevOps pipeline YAML
- `generate_github_actions_workflow()`: Generate GitHub Actions workflow YAML
- `save_pipeline_file(path)`: Save pipeline file to disk
- `validate_pipeline()`: Validate pipeline configuration

## 📊 Infrastructure as Code

### ARM Template Example

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "functionAppName": {
      "type": "string",
      "defaultValue": "mcp-donor-dev"
    },
    "location": {
      "type": "string",
      "defaultValue": "eastus"
    },
    "storageAccountName": {
      "type": "string",
      "defaultValue": "mcpdonordevstorage"
    },
    "appInsightsName": {
      "type": "string",
      "defaultValue": "mcp-donor-dev-appinsights"
    },
    "keyVaultName": {
      "type": "string",
      "defaultValue": "mcp-donor-dev-kv"
    }
  },
  "variables": {
    "storageAccountId": "[resourceId('Microsoft.Storage/storageAccounts', parameters('storageAccountName'))]",
    "appInsightsId": "[resourceId('Microsoft.Insights/components', parameters('appInsightsName'))]",
    "keyVaultId": "[resourceId('Microsoft.KeyVault/vaults', parameters('keyVaultName'))]",
    "functionAppId": "[resourceId('Microsoft.Web/sites', parameters('functionAppName'))]"
  },
  "resources": [
    {
      "type": "Microsoft.Storage/storageAccounts",
      "apiVersion": "2023-01-01",
      "name": "[parameters('storageAccountName')]",
      "location": "[parameters('location')]",
      "sku": {
        "name": "Standard_LRS"
      },
      "kind": "StorageV2",
      "properties": {
        "accessTier": "Hot"
      }
    },
    {
      "type": "Microsoft.Insights/components",
      "apiVersion": "2020-02-02",
      "name": "[parameters('appInsightsName')]",
      "location": "[parameters('location')]",
      "properties": {
        "Application_Type": "web",
        "Flow_Type": "Bluefield",
        "Request_Source": "rest"
      }
    },
    {
      "type": "Microsoft.KeyVault/vaults",
      "apiVersion": "2023-02-01",
      "name": "[parameters('keyVaultName')]",
      "location": "[parameters('location')]",
      "properties": {
        "sku": {
          "name": "standard",
          "family": "A"
        },
        "tenantId": "[subscription().tenantId]",
        "accessPolicies": []
      }
    },
    {
      "type": "Microsoft.Web/sites",
      "apiVersion": "2022-03-01",
      "name": "[parameters('functionAppName')]",
      "location": "[parameters('location')]",
      "kind": "functionapp,linux",
      "properties": {
        "serverFarmId": "[resourceId('Microsoft.Web/serverfarms', 'ASP-' + parameters('functionAppName'))]",
        "siteConfig": {
          "appSettings": [
            {
              "name": "AzureWebJobsStorage",
              "value": "[concat('DefaultEndpointsProtocol=https;AccountName=', parameters('storageAccountName'), ';AccountKey=', listKeys(variables('storageAccountId'), '2023-01-01').keys[0].value, ';EndpointSuffix=core.windows.net')]"
            },
            {
              "name": "FUNCTIONS_EXTENSION_VERSION",
              "value": "~4"
            },
            {
              "name": "FUNCTIONS_WORKER_RUNTIME",
              "value": "python"
            },
            {
              "name": "Python_VERSION",
              "value": "3.11"
            },
            {
              "name": "APPINSIGHTS_INSTRUMENTATIONKEY",
              "value": "[reference(variables('appInsightsId'), '2020-02-02').InstrumentationKey]"
            },
            {
              "name": "ENVIRONMENT",
              "value": "Dev"
            },
            {
              "name": "DOMAIN",
              "value": "DonorManagement"
            }
          ],
          "linuxFxVersion": "PYTHON|3.11"
        },
        "httpsOnly": true
      },
      "dependsOn": [
        "[resourceId('Microsoft.Storage/storageAccounts', parameters('storageAccountName'))]",
        "[resourceId('Microsoft.Insights/components', parameters('appInsightsName'))]"
      ]
    },
    {
      "type": "Microsoft.Web/serverfarms",
      "apiVersion": "2022-03-01",
      "name": "[concat('ASP-', parameters('functionAppName'))]",
      "location": "[parameters('location')]",
      "sku": {
        "name": "Y1",
        "tier": "Dynamic"
      },
      "kind": "functionapp,linux",
      "properties": {}
    }
  ],
  "outputs": {
    "functionAppEndpoint": {
      "type": "string",
      "value": "[concat('https://', parameters('functionAppName'), '.azurewebsites.net')]"
    },
    "storageAccountName": {
      "type": "string",
      "value": "[parameters('storageAccountName')]"
    },
    "appInsightsName": {
      "type": "string",
      "value": "[parameters('appInsightsName')]"
    },
    "keyVaultName": {
      "type": "string",
      "value": "[parameters('keyVaultName')]"
    }
  }
}
```

### Bicep Template Example

```bicep
param functionAppName string = 'mcp-donor-dev'
param location string = 'eastus'
param storageAccountName string = 'mcpdonordevstorage'
param appInsightsName string = 'mcp-donor-dev-appinsights'
param keyVaultName string = 'mcp-donor-dev-kv'

var storageAccountId = 'Microsoft.Storage/storageAccounts/${storageAccountName}'
var appInsightsId = 'Microsoft.Insights/components/${appInsightsName}'
var keyVaultId = 'Microsoft.KeyVault/vaults/${keyVaultName}'
var functionAppId = 'Microsoft.Web/sites/${functionAppName}'

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  properties: {
    Application_Type: 'web'
    Flow_Type: 'Bluefield'
    Request_Source: 'rest'
  }
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-02-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: {
      name: 'standard'
      family: 'A'
    }
    tenantId: subscription().tenantId
    accessPolicies: []
  }
}

resource serverFarm 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: 'ASP-${functionAppName}'
  location: location
  sku: {
    name: 'Y1'
    tier: 'Dynamic'
  }
  kind: 'functionapp,linux'
  properties: {}
}

resource functionApp 'Microsoft.Web/sites@2022-03-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp,linux'
  properties: {
    serverFarmId: serverFarm.id
    siteConfig: {
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};AccountKey=${listKeys(storageAccountId, '2023-01-01').keys[0].value};EndpointSuffix=core.windows.net'
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'Python_VERSION'
          value: '3.11'
        }
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: appInsights.properties.InstrumentationKey
        }
        {
          name: 'ENVIRONMENT'
          value: 'Dev'
        }
        {
          name: 'DOMAIN'
          value: 'DonorManagement'
        }
      ]
      linuxFxVersion: 'PYTHON|3.11'
    }
    httpsOnly: true
  }
  dependsOn: [
    storageAccount
    appInsights
    serverFarm
  ]
}

output functionAppEndpoint string = 'https://${functionAppName}.azurewebsites.net'
output storageAccountName string = storageAccountName
output appInsightsName string = appInsightsName
output keyVaultName string = keyVaultName
```

## 📈 Monitoring and Metrics

### Key Metrics

| Metric | Description | Target | Alert Threshold |
|--------|-------------|--------|-----------------|
| Deployment Success Rate | Percentage of successful deployments | > 99% | < 95% |
| Deployment Duration | Average deployment time | < 5min | > 15min |
| Build Success Rate | Percentage of successful builds | > 99% | < 95% |
| Test Success Rate | Percentage of successful tests | > 95% | < 90% |
| Security Scan Issues | Number of security issues found | 0 | > 5 |
| Pipeline Queue Time | Time spent waiting in queue | < 1min | > 5min |
| Deployment Frequency | Deployments per day | Varies | < 1/day |

### Deployment Queries

```kusto
// Get deployment success rate
Deployments
| where TimeGenerated > ago(30d)
| summarize 
    total=count(),
    success=countif(Status == "Succeeded"),
    failed=countif(Status == "Failed")
| extend success_rate=toreal(success) / toreal(total) * 100
| project total, success, failed, success_rate

// Get deployment duration
Deployments
| where TimeGenerated > ago(30d)
| where Status == "Succeeded"
| extend duration_minutes=toreal(DurationSeconds) / 60
| summarize avg(duration_minutes), max(duration_minutes), min(duration_minutes)

// Get deployment failures
Deployments
| where TimeGenerated > ago(30d)
| where Status == "Failed"
| summarize count() by FailureReason
| order by count_ desc

// Get build success rate
Builds
| where TimeGenerated > ago(30d)
| summarize 
    total=count(),
    success=countif(Status == "Succeeded"),
    failed=countif(Status == "Failed")
| extend success_rate=toreal(success) / toreal(total) * 100

// Get test success rate
Tests
| where TimeGenerated > ago(30d)
| summarize 
    total=count(),
    passed=countif(Status == "Passed"),
    failed=countif(Status == "Failed")
| extend success_rate=toreal(passed) / toreal(total) * 100

// Get security scan issues
SecurityScans
| where TimeGenerated > ago(30d)
| where IssuesFound > 0
| summarize count() by ScanType, Severity
| order by count_ desc
```

## 🚀 Best Practices

### ⭐ Use Infrastructure as Code

Always use ARM templates or Bicep for infrastructure deployment.

```bash
# Good - Using Bicep
az deployment group create \
    --resource-group your-resource-group \
    --template-file deployment/main.bicep \
    --parameters @deployment/parameters/dev.json

# Bad - Manual deployment
# az functionapp create --name mcp-donor-dev --resource-group your-resource-group ...
```

### ⭐ Use CI/CD Pipelines

Always use automated CI/CD pipelines for deployment.

```yaml
# Good - Azure DevOps Pipeline
trigger:
  branches:
    include:
      - main
      - develop
  paths:
    include:
      - src/**
      - tests/**

stages:
  - stage: Build
    jobs:
      - job: Build
        steps:
          - script: pip install -r requirements.txt
          - script: pip install pytest pytest-cov
          - script: python -m pytest tests/unit --cov=src

  - stage: Test
    dependsOn: Build
    jobs:
      - job: Test
        steps:
          - script: python -m pytest tests/integration
          - script: python -m pytest tests/security

  - stage: Deploy
    dependsOn: Test
    condition: succeeded()
    jobs:
      - job: Deploy
        steps:
          - script: az deployment group create --template-file deployment/main.bicep --parameters @deployment/parameters/dev.json
```

### ⭐ Implement Security Scanning

Always include security scanning in your pipeline.

```yaml
# Good - Security scanning in pipeline
- stage: Security
  dependsOn: Build
  jobs:
    - job: SecurityScan
      steps:
        - script: pip install safety
        - script: safety check --full-report
        
        - script: pip install gitleaks
        - script: gitleaks detect --source . --report-path gitleaks-report.json
        
        - script: pip install bandit
        - script: bandit -r src/ -f json -o bandit-report.json
```

### ⭐ Use Multiple Environments

Always deploy to multiple environments (Dev, Test, Production).

```yaml
# Good - Multiple environments
jobs:
  - job: Deploy_Dev
    steps:
      - script: az deployment group create --template-file deployment/main.bicep --parameters @deployment/parameters/dev.json
    
  - job: Deploy_Test
    dependsOn: Deploy_Dev
    condition: succeeded()
    steps:
      - script: az deployment group create --template-file deployment/main.bicep --parameters @deployment/parameters/test.json
    
  - job: Deploy_Production
    dependsOn: Deploy_Test
    condition: succeeded()
    steps:
      - script: az deployment group create --template-file deployment/main.bicep --parameters @deployment/parameters/prod.json
```

### ⭐ Implement Approval Gates

Use approval gates for production deployments.

```yaml
# Good - Approval gates
- stage: Deploy_Production
  dependsOn: Deploy_Test
  condition: succeeded()
  jobs:
    - job: Approve_Production
      pool: server
      steps:
        - task: ManualValidation@0
          inputs:
            notifyUsers: "team@my-org.org"
            instructions: "Please review and approve production deployment"
            onTimeout: "reject"
    
    - job: Deploy_Production
      dependsOn: Approve_Production
      condition: succeeded()
      steps:
        - script: az deployment group create --template-file deployment/main.bicep --parameters @deployment/parameters/prod.json
```

### ⭐ Use Deployment Slots

Use deployment slots for zero-downtime deployments.

```bicep
// Good - Deployment slots
resource functionApp 'Microsoft.Web/sites@2022-03-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp,linux'
  properties: {
    serverFarmId: serverFarm.id
    siteConfig: {
      // ... other settings
    }
    httpsOnly: true
  }
}

resource stagingSlot 'Microsoft.Web/sites/slots@2022-03-01' = {
  name: '${functionAppName}/staging'
  location: location
  kind: 'functionapp,linux'
  properties: {
    serverFarmId: serverFarm.id
    siteConfig: {
      // ... same settings as production
    }
    httpsOnly: true
  }
}
```

### ⭐ Monitor Deployments

Monitor deployment health and performance.

```python
# Good - Deployment monitoring
from platform.deployment import AzureDeployer

deployer = AzureDeployer(
    subscription_id="your-subscription-id",
    resource_group="your-resource-group"
)

# Get deployment status
status = deployer.get_deployment_status("mcp-donor-dev")
print(f"Status: {status.status}")
print(f"Last deployment: {status.last_deployment_time}")
print(f"Uptime: {status.uptime}")

# Get deployment metrics
metrics = deployer.get_deployment_metrics("mcp-donor-dev")
print(f"Request count: {metrics.request_count}")
print(f"Error rate: {metrics.error_rate}")
print(f"Response time: {metrics.avg_response_time}")
```

## 🔍 Troubleshooting

### Common Issues

#### Deployment Failed

**Error:** `DeploymentFailedError: Deployment failed`

**Causes:**
- Syntax errors in ARM/Bicep template
- Missing required parameters
- Resource already exists
- Permission issues
- Quota limits exceeded

**Solutions:**
1. Validate template syntax
2. Check all required parameters are provided
3. Check for existing resources
4. Verify deployment permissions
5. Check Azure quota limits

```bash
# Debug deployment
az deployment group validate \
    --resource-group your-resource-group \
    --template-file deployment/main.bicep \
    --parameters @deployment/parameters/dev.json

# Check deployment logs
az deployment group show \
    --resource-group your-resource-group \
    --name deployment-name

# Check resource provider status
az provider show --namespace Microsoft.Web
```

#### Build Failed

**Error:** `BuildFailedError: Build failed`

**Causes:**
- Missing dependencies
- Syntax errors in code
- Test failures
- Build tool issues

**Solutions:**
1. Check build logs for errors
2. Verify all dependencies are installed
3. Run tests locally
4. Check build tool versions

```bash
# Debug build locally
pip install -r requirements.txt
pip install pytest pytest-cov
python -m pytest tests/unit --cov=src

# Check Python version
python --version

# Check pip version
pip --version
```

#### Tests Failed

**Error:** `TestFailedError: Tests failed`

**Causes:**
- Test environment not configured correctly
- Missing test dependencies
- Flaky tests
- Test data issues

**Solutions:**
1. Run tests locally to reproduce
2. Check test environment configuration
3. Verify test dependencies
4. Fix flaky tests
5. Check test data

```bash
# Debug tests locally
pip install -r requirements.txt
pip install -r requirements-test.txt
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_specific.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

#### Security Scan Failed

**Error:** `SecurityScanFailedError: Security scan failed`

**Causes:**
- Vulnerable dependencies
- Hardcoded secrets
- Security issues in code
- Scan tool configuration issues

**Solutions:**
1. Review security scan reports
2. Update vulnerable dependencies
3. Remove hardcoded secrets
4. Fix security issues in code
5. Check scan tool configuration

```bash
# Debug security scanning locally
pip install safety
safety check --full-report

pip install gitleaks
gitleaks detect --source . --report-path gitleaks-report.json

pip install bandit
bandit -r src/ -f json -o bandit-report.json
```

## 📚 Examples

### Complete Deployment Pipeline

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
      - main
      - develop
  paths:
    include:
      - src/**
      - tests/**
      - deployment/**

schedules:
  - cron: "0 0 * * *"
    displayName: Daily midnight build
    branches:
      include:
        - main

variables:
  python.version: '3.11'
  azureSubscription: 'your-azure-service-connection'

stages:
  - stage: Build
    displayName: Build
    jobs:
      - job: Build
        displayName: Build
        pool:
          vmImage: 'ubuntu-latest'
        
        steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '$(python.version)'
            displayName: 'Use Python $(python.version)'
          
          - script: |
              python -m pip install --upgrade pip
              pip install -r requirements.txt
              pip install -r requirements-test.txt
            displayName: 'Install dependencies'
          
          - script: |
              pip install pytest pytest-cov pytest-azurepipelines
              python -m pytest tests/unit --cov=src --cov-report=xml -o junitxml=test-results.xml
            displayName: 'Run unit tests'
          
          - task: PublishTestResults@2
            condition: succeededOrFailed()
            inputs:
              testResultsFiles: '**/test-results.xml'
              testRunTitle: 'Unit Tests'
            displayName: 'Publish unit test results'
          
          - task: PublishCodeCoverageResults@1
            inputs:
              codeCoverageTool: Cobertura
              summaryFileLocation: '$(System.DefaultWorkingDirectory)/**/coverage.xml'
              reportDirectory: '$(System.DefaultWorkingDirectory)'
            displayName: 'Publish code coverage'
          
          - script: |
              mkdir -p $(Build.ArtifactStagingDirectory)/dist
              cp -r src/* $(Build.ArtifactStagingDirectory)/dist/
              cp requirements.txt $(Build.ArtifactStagingDirectory)/dist/
            displayName: 'Prepare artifacts'
          
          - task: PublishBuildArtifacts@1
            inputs:
              PathtoPublish: '$(Build.ArtifactStagingDirectory)/dist'
              ArtifactName: 'drop'
              publishLocation: 'Container'
            displayName: 'Publish artifacts'

  - stage: Security
    displayName: Security
    dependsOn: Build
    condition: succeeded()
    jobs:
      - job: SecurityScan
        displayName: Security Scan
        pool:
          vmImage: 'ubuntu-latest'
        
        steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '$(python.version)'
            displayName: 'Use Python $(python.version)'
          
          - script: |
              pip install safety
              safety check --full-report --output json > safety-report.json || true
            displayName: 'Dependency scanning'
          
          - script: |
              pip install gitleaks
              gitleaks detect --source . --report-path gitleaks-report.json --exit-code 0
            displayName: 'Secret scanning'
          
          - script: |
              pip install bandit
              bandit -r src/ -f json -o bandit-report.json || true
            displayName: 'Code analysis'
          
          - task: PublishBuildArtifacts@1
            inputs:
              PathtoPublish: '$(System.DefaultWorkingDirectory)/*.json'
              ArtifactName: 'security-reports'
              publishLocation: 'Container'
            displayName: 'Publish security reports'

  - stage: Test
    displayName: Test
    dependsOn: Build
    condition: succeeded()
    jobs:
      - job: IntegrationTests
        displayName: Integration Tests
        pool:
          vmImage: 'ubuntu-latest'
        
        steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '$(python.version)'
            displayName: 'Use Python $(python.version)'
          
          - script: |
              pip install -r requirements.txt
              pip install -r requirements-test.txt
            displayName: 'Install dependencies'
          
          - script: |
              python -m pytest tests/integration -v -o junitxml=integration-test-results.xml
            displayName: 'Run integration tests'
            env:
              ENVIRONMENT: Test
              AZURE_TENANT_ID: $(AZURE_TENANT_ID)
              AZURE_CLIENT_ID: $(AZURE_CLIENT_ID)
              AZURE_CLIENT_SECRET: $(AZURE_CLIENT_SECRET)
          
          - task: PublishTestResults@2
            condition: succeededOrFailed()
            inputs:
              testResultsFiles: '**/integration-test-results.xml'
              testRunTitle: 'Integration Tests'
            displayName: 'Publish integration test results'

  - stage: Deploy_Dev
    displayName: Deploy to Dev
    dependsOn: [Test, Security]
    condition: succeeded()
    jobs:
      - job: Deploy_Dev
        displayName: Deploy to Dev
        pool:
          vmImage: 'ubuntu-latest'
        
        steps:
          - task: DownloadBuildArtifacts@1
            inputs:
              buildType: 'current'
              downloadType: 'single'
              artifactName: 'drop'
              downloadPath: '$(System.ArtifactsDirectory)'
            displayName: 'Download artifacts'
          
          - task: AzureCLI@2
            inputs:
              azureSubscription: '$(azureSubscription)'
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                az deployment group create \
                  --resource-group your-resource-group \
                  --template-file deployment/main.bicep \
                  --parameters @deployment/parameters/dev.json \
                  --mode Incremental
            displayName: 'Deploy to Dev'

  - stage: Deploy_Production
    displayName: Deploy to Production
    dependsOn: Deploy_Dev
    condition: succeeded()
    jobs:
      - job: Approve_Production
        displayName: Approve Production
        pool: server
        steps:
          - task: ManualValidation@0
            inputs:
              notifyUsers: "team@my-org.org"
              instructions: "Please review and approve production deployment"
              onTimeout: "reject"
            displayName: 'Approve production deployment'
      
      - job: Deploy_Production
        displayName: Deploy to Production
        dependsOn: Approve_Production
        condition: succeeded()
        pool:
          vmImage: 'ubuntu-latest'
        
        steps:
          - task: DownloadBuildArtifacts@1
            inputs:
              buildType: 'current'
              downloadType: 'single'
              artifactName: 'drop'
              downloadPath: '$(System.ArtifactsDirectory)'
            displayName: 'Download artifacts'
          
          - task: AzureCLI@2
            inputs:
              azureSubscription: '$(azureSubscription)'
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                az deployment group create \
                  --resource-group your-resource-group \
                  --template-file deployment/main.bicep \
                  --parameters @deployment/parameters/prod.json \
                  --mode Incremental
            displayName: 'Deploy to Production'
```

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Build, Test, and Deploy

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'src/**'
      - 'tests/**'
      - 'deployment/**'
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight

env:
  PYTHON_VERSION: '3.11'
  AZURE_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
  AZURE_RESOURCE_GROUP: 'your-resource-group'

jobs:
  build:
    name: Build
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      
      - name: Run unit tests
        run: |
          pip install pytest pytest-cov
          python -m pytest tests/unit --cov=src --cov-report=xml -o junitxml=test-results.xml
      
      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: unit-test-results
          path: test-results.xml
      
      - name: Upload coverage report
        uses: actions/upload-artifact@v3
        with:
          name: coverage-report
          path: coverage.xml
      
      - name: Prepare artifacts
        run: |
          mkdir -p dist
          cp -r src/* dist/
          cp requirements.txt dist/
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: deployment-artifacts
          path: dist/

  security:
    name: Security
    needs: build
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Dependency scanning
        run: |
          pip install safety
          safety check --full-report --output json > safety-report.json || true
      
      - name: Secret scanning
        run: |
          pip install gitleaks
          gitleaks detect --source . --report-path gitleaks-report.json --exit-code 0
      
      - name: Code analysis
        run: |
          pip install bandit
          bandit -r src/ -f json -o bandit-report.json || true
      
      - name: Upload security reports
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: |
            safety-report.json
            gitleaks-report.json
            bandit-report.json

  test:
    name: Test
    needs: build
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      
      - name: Run integration tests
        run: |
          python -m pytest tests/integration -v -o junitxml=integration-test-results.xml
        env:
          ENVIRONMENT: Test
          AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
          AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
          AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
      
      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: integration-test-results
          path: integration-test-results.xml

  deploy_dev:
    name: Deploy to Dev
    needs: [test, security]
    runs-on: ubuntu-latest
    environment:
      name: Dev
      url: https://mcp-donor-dev.azurewebsites.net
    
    steps:
      - name: Download artifacts
        uses: actions/download-artifact@v3
        with:
          name: deployment-artifacts
          path: dist/
      
      - name: Login to Azure
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Deploy to Dev
        run: |
          az deployment group create \
            --resource-group ${{ env.AZURE_RESOURCE_GROUP }} \
            --template-file deployment/main.bicep \
            --parameters @deployment/parameters/dev.json \
            --mode Incremental

  deploy_production:
    name: Deploy to Production
    needs: deploy_dev
    runs-on: ubuntu-latest
    environment:
      name: Production
      url: https://mcp-donor.azurewebsites.net
    
    steps:
      - name: Download artifacts
        uses: actions/download-artifact@v3
        with:
          name: deployment-artifacts
          path: dist/
      
      - name: Login to Azure
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Deploy to Production
        run: |
          az deployment group create \
            --resource-group ${{ env.AZURE_RESOURCE_GROUP }} \
            --template-file deployment/main.bicep \
            --parameters @deployment/parameters/prod.json \
            --mode Incremental
```

### Python Deployment Script

```python
#!/usr/bin/env python3
"""
Deployment script for MCP Platform Framework
"""

import argparse
import logging
import sys
from pathlib import Path

from platform.deployment import (
    AzureDeployer,
    DeploymentConfig,
    build_package,
    run_tests,
    run_security_scan
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Deploy MCP Platform Framework')
    
    parser.add_argument(
        '--environment',
        choices=['Dev', 'Test', 'Production'],
        default='Dev',
        help='Environment to deploy to'
    )
    
    parser.add_argument(
        '--build',
        action='store_true',
        help='Build the deployment package'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run tests'
    )
    
    parser.add_argument(
        '--security',
        action='store_true',
        help='Run security scanning'
    )
    
    parser.add_argument(
        '--deploy',
        action='store_true',
        help='Deploy to Azure'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all steps: build, test, security, deploy'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='deployment/config.yaml',
        help='Path to deployment configuration file'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser.parse_args()


def load_config(config_path):
    """Load deployment configuration"""
    import yaml
    
    config_path = Path(config_path)
    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        config_data = yaml.safe_load(f)
    
    return DeploymentConfig(**config_data.get('deployment', {}))


def main():
    """Main deployment function"""
    args = parse_arguments()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Load configuration
    logger.info("Loading deployment configuration...")
    config = load_config(args.config)
    logger.info(f"Configuration loaded for environment: {args.environment}")
    
    # Set environment
    config.set_environment(args.environment)
    
    # Run steps
    if args.all or args.build:
        logger.info("Building deployment package...")
        build_result = build_package(config)
        if not build_result.success:
            logger.error(f"Build failed: {build_result.error}")
            sys.exit(1)
        logger.info(f"Build successful: {build_result.package_path}")
    
    if args.all or args.test:
        logger.info("Running tests...")
        test_result = run_tests(config)
        if not test_result.success:
            logger.error(f"Tests failed: {test_result.error}")
            sys.exit(1)
        logger.info(f"Tests passed: {test_result.passed_count} passed, {test_result.failed_count} failed")
    
    if args.all or args.security:
        logger.info("Running security scanning...")
        security_result = run_security_scan(config)
        if not security_result.success:
            logger.error(f"Security scanning failed: {security_result.error}")
            sys.exit(1)
        logger.info(f"Security scanning passed: {security_result.issues_found} issues found")
    
    if args.all or args.deploy:
        logger.info("Deploying to Azure...")
        deployer = AzureDeployer(
            subscription_id=config.azure.subscription_id,
            resource_group=config.azure.resource_group
        )
        
        deploy_result = deployer.deploy_function_app(
            name=config.azure.function_app_name,
            location=config.azure.location,
            runtime="python",
            runtime_version=config.build.python_version,
            package_path="./dist",
            config=config
        )
        
        if not deploy_result.success:
            logger.error(f"Deployment failed: {deploy_result.error}")
            sys.exit(1)
        
        logger.info(f"Deployment successful!")
        logger.info(f"Endpoint: {deploy_result.endpoint}")
        logger.info(f"Deployment ID: {deploy_result.deployment_id}")


if __name__ == "__main__":
    main()
```

---

## 📖 API Reference

### Exceptions

| Exception | Description | Error Code |
|-----------|-------------|------------|
| `DeploymentError` | Base deployment error | DEPLOY-001 |
| `BuildError` | Build error | DEPLOY-002 |
| `TestError` | Test error | DEPLOY-003 |
| `SecurityScanError` | Security scanning error | DEPLOY-004 |
| `AzureDeploymentError` | Azure deployment error | DEPLOY-005 |
| `ConfigurationError` | Configuration error | DEPLOY-006 |

### Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| DEPLOY-001 | Deployment error | 500 |
| DEPLOY-002 | Build error | 500 |
| DEPLOY-003 | Test error | 500 |
| DEPLOY-004 | Security scanning error | 500 |
| DEPLOY-005 | Azure deployment error | 500 |
| DEPLOY-006 | Configuration error | 400 |

---

*⭐ = Best Practice | 🔒 = Security Requirement | ⚡ = Performance Consideration*