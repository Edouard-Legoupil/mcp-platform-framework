# 🔵 Azure DevOps CI/CD Pipeline Guide

## Overview

This guide provides comprehensive instructions for setting up CI/CD pipelines using Azure DevOps to build, test, and deploy the MCP Platform Framework to Azure Function Apps.

## 📋 Prerequisites

Before setting up Azure DevOps pipelines, ensure you have:

- ✅ **Azure DevOps Organization** created
- ✅ **Project** created within the organization
- ✅ **Service Connection** to your Azure subscription
- ✅ **Agent Pool** configured (Microsoft-hosted or self-hosted)
- ✅ **Repository** connected to Azure DevOps
- ✅ **Azure Resources** provisioned (Resource Groups, Key Vault, etc.)

## 🔧 Azure DevOps Setup

### 1. Create Azure DevOps Organization

1. Go to [Azure DevOps](https://dev.azure.com/)
2. Sign in with your Microsoft account
3. Click "New organization" and follow the prompts
4. Choose a name (e.g., `your-org-mcp`)
5. Select your region

### 2. Create Project

```bash
# Using Azure CLI
az devops project create \
  --org-url https://dev.azure.com/your-org \
  --name mcp-platform \
  --description "MCP Platform Framework CI/CD" \
  --visibility private \
  --source-control git
```

Or create manually:
1. Navigate to your organization
2. Click "New project"
3. Enter name: `mcp-platform`
4. Select visibility: Private
5. Select version control: Git
6. Click "Create"

### 3. Set Up Service Connection

1. Go to Project Settings → Service connections
2. Click "New service connection"
3. Select "Azure Resource Manager"
4. Choose "Service principal (manual)" or "Service principal (automatic)"
5. Enter:
   - **Connection name**: `Azure-MCP-Production`
   - **Subscription ID**: Your Azure subscription ID
   - **Service principal ID**: Your service principal client ID
   - **Service principal key**: Your service principal client secret
   - **Tenant ID**: Your Azure AD tenant ID
6. Click "Verify and save"

**Recommended Service Connections:**
- `Azure-MCP-Development` - Development environment
- `Azure-MCP-Test` - Test environment
- `Azure-MCP-Staging` - Staging environment
- `Azure-MCP-Production` - Production environment

### 4. Configure Agent Pool

**Option A: Microsoft-hosted Agents (Recommended for most scenarios)**

- Use the default `Azure Pipelines` pool
- Supports Windows, Linux, and macOS
- No maintenance required
- Free tier: 1,800 minutes/month

**Option B: Self-hosted Agents (For advanced scenarios)**

```bash
# Install self-hosted agent on Linux
mkdir myagent && cd myagent
wget https://vstsagentpackage.azureedge.net/agent/2.206.1/vsts-agent-linux-x64-2.206.1.tar.gz
tar zxvf vsts-agent-linux-x64-2.206.1.tar.gz
./config.sh --unattended \
  --url https://dev.azure.com/your-org \
  --auth pat \
  --token YOUR_PAT \
  --pool Default \
  --agent $HOSTNAME \
  --replace
./run.sh
```

## 📁 Pipeline Structure

```
azure-pipelines/
├── build.yml              # Build and test pipeline
├── deploy.yml             # Deployment pipeline
├── promote.yml            # Environment promotion pipeline
├── templates/             # Reusable pipeline templates
│   ├── build-template.yml
│   ├── test-template.yml
│   ├── deploy-template.yml
│   └── variables.yml
└── environments/          # Environment-specific configurations
    ├── development.yml
    ├── test.yml
    ├── staging.yml
    └── production.yml
```

## 🏗️ Build Pipeline

### Basic Build Pipeline

**azure-pipelines/build.yml**
```yaml
name: $(Build.BuildNumber)-$(Date:yyyyMMdd)

trigger:
  branches:
    include:
      - main
      - releases/*
  paths:
    exclude:
      - docs/*
      - README.md
      - CHANGELOG.md

pr:
  branches:
    include:
      - main
      - releases/*
  paths:
    exclude:
      - docs/*

variables:
  - name: python.version
    value: '3.11'
  - name: build.number
    value: $(Build.BuildNumber)
  - name: isMainBranch
    value: $[eq(variables['Build.SourceBranch'], 'refs/heads/main')]

stages:
- stage: Build
  displayName: Build and Test
  jobs:
  - job: Build
    displayName: Build
    pool:
      vmImage: 'ubuntu-latest'
    
    steps:
    - task: UsePythonVersion@0
      displayName: 'Use Python $(python.version)'
      inputs:
        versionSpec: $(python.version)
        addToPath: true
    
    - script: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
      displayName: 'Install dependencies'
    
    - script: |
        pip install -e .
      displayName: 'Install package'
    
    - script: |
        python -m pytest tests/unit --cov=mcp_framework --cov-report=xml --junitxml=test-results.xml
      displayName: 'Run unit tests'
      env:
        MCP_ENVIRONMENT: test
        AZURE_SUBSCRIPTION_ID: $(AZURE_SUBSCRIPTION_ID)
    
    - task: PublishTestResults@2
      displayName: 'Publish test results'
      inputs:
        testResultsFormat: 'JUnit'
        testResultsFiles: '**/test-results.xml'
        failTaskOnFailedTests: true
    
    - task: PublishCodeCoverageResults@1
      displayName: 'Publish code coverage'
      inputs:
        codeCoverageTool: 'Cobertura'
        summaryFileLocation: '**/coverage.xml'
        reportDirectory: '**/htmlcov'
    
    - script: |
        python -m pytest tests/integration --junitxml=integration-results.xml
      displayName: 'Run integration tests'
      condition: and(succeeded(), eq(variables.isMainBranch, 'true'))
      env:
        MCP_ENVIRONMENT: test
        AZURE_SUBSCRIPTION_ID: $(AZURE_SUBSCRIPTION_ID)
        AZURE_RESOURCE_GROUP: mcp-test-rg
        KEY_VAULT_NAME: mcp-test-kv
        FABRIC_TENANT_ID: $(FABRIC_TENANT_ID)
        FABRIC_WORKSPACE_ID: $(FABRIC_WORKSPACE_ID)
    
    - task: PublishTestResults@2
      displayName: 'Publish integration test results'
      condition: and(succeeded(), eq(variables.isMainBranch, 'true'))
      inputs:
        testResultsFormat: 'JUnit'
        testResultsFiles: '**/integration-results.xml'
        failTaskOnFailedTests: true
    
    - script: |
        python -m pytest tests/security --junitxml=security-results.xml
      displayName: 'Run security tests'
      condition: and(succeeded(), eq(variables.isMainBranch, 'true'))
    
    - task: PublishTestResults@2
      displayName: 'Publish security test results'
      condition: and(succeeded(), eq(variables.isMainBranch, 'true'))
      inputs:
        testResultsFormat: 'JUnit'
        testResultsFiles: '**/security-results.xml'
        failTaskOnFailedTests: true
    
    - script: |
        pip install build twine
        python -m build
      displayName: 'Build package'
      condition: and(succeeded(), eq(variables.isMainBranch, 'true'))
    
    - task: PublishPipelineArtifact@1
      displayName: 'Publish package artifact'
      condition: and(succeeded(), eq(variables.isMainBranch, 'true'))
      inputs:
        targetPath: 'dist'
        artifact: 'mcp-platform-package'
        publishLocation: 'pipeline'
    
    - task: PublishPipelineArtifact@1
      displayName: 'Publish test artifacts'
      condition: and(succeeded(), eq(variables.isMainBranch, 'true'))
      inputs:
        targetPath: 'test-results'
        artifact: 'test-results'
        publishLocation: 'pipeline'
```

### Advanced Build Pipeline with Caching

```yaml
name: $(Build.BuildNumber)-$(Date:yyyyMMdd)

variables:
  - name: python.version
    value: '3.11'
  - name: cacheKey
    value: $(Pipeline.Workspace)-python-$(python.version)-$(hash('requirements.txt'))

stages:
- stage: Build
  displayName: Build and Test
  jobs:
  - job: Build
    displayName: Build
    pool:
      vmImage: 'ubuntu-latest'
    
    steps:
    - task: Cache@2
      displayName: 'Cache pip packages'
      inputs:
        key: $(cacheKey)
        path: $(pip.getPipelineCacheDir)/pip
        restoreKeys: |
          $(Pipeline.Workspace)-python-$(python.version)-
          $(Pipeline.Workspace)-python-
        cacheHitVar: CACHE_RESTORED
    
    - task: UsePythonVersion@0
      displayName: 'Use Python $(python.version)'
      inputs:
        versionSpec: $(python.version)
        addToPath: true
    
    - script: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        if [ -z "$(CACHE_RESTORED)" ]; then
          pip cache dir
        fi
      displayName: 'Install dependencies'
    
    - script: |
        pip install -e .
      displayName: 'Install package'
    
    - script: |
        python -m pytest tests/unit --cov=mcp_framework --cov-report=xml --junitxml=test-results.xml -n auto
      displayName: 'Run unit tests with parallel execution'
      env:
        MCP_ENVIRONMENT: test
        PYTEST_XDIST_WORKER_COUNT: 4
    
    - script: |
        python -m pytest tests/integration --junitxml=integration-results.xml -n auto
      displayName: 'Run integration tests'
      condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
      env:
        MCP_ENVIRONMENT: test
        AZURE_SUBSCRIPTION_ID: $(AZURE_SUBSCRIPTION_ID)
    
    - task: ComponentGovernanceComponentDetection@0
      displayName: 'Component governance check'
      inputs:
        scanType: 'Register'
        verbosity: 'Verbose'
        alertNonCompliantStatus: true
        alertUnscannedStatus: true
```

## 🚀 Deployment Pipeline

### Multi-Stage Deployment Pipeline

**azure-pipelines/deploy.yml**
```yaml
name: $(Build.BuildNumber)-deploy-$(Date:yyyyMMdd)

trigger: none

pr: none

resources:
  pipelines:
  - pipeline: build-pipeline
    source: 'MCP-Platform-Build'
    trigger: true
    branch: main

variables:
  - name: python.version
    value: '3.11'
  - name: environment
    value: ''

stages:
- stage: Deploy_Development
  displayName: Deploy to Development
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  dependsOn: []
  jobs:
  - deployment: Deploy_Dev
    displayName: Deploy to Development
    environment: 'Development'
    pool:
      vmImage: 'ubuntu-latest'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: UsePythonVersion@0
            displayName: 'Use Python $(python.version)'
            inputs:
              versionSpec: $(python.version)
          
          - task: DownloadPipelineArtifact@2
            displayName: 'Download package artifact'
            inputs:
              buildType: 'current'
              artifactName: 'mcp-platform-package'
              targetPath: '$(Pipeline.Workspace)/dist'
          
          - script: |
              pip install $(Pipeline.Workspace)/dist/*.whl
            displayName: 'Install package'
          
          - task: AzureCLI@2
            displayName: 'Deploy to Development Function App'
            inputs:
              azureSubscription: 'Azure-MCP-Development'
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                az functionapp deployment source config-zip \
                  --name mcp-dev-func \
                  --resource-group mcp-dev-rg \
                  --src $(Pipeline.Workspace)/dist/*.zip
                
                # Set application settings
                az functionapp config appsettings set \
                  --name mcp-dev-func \
                  --resource-group mcp-dev-rg \
                  --settings MCP_ENVIRONMENT=development
                
                # Restart Function App
                az functionapp restart \
                  --name mcp-dev-func \
                  --resource-group mcp-dev-rg
          
          - script: |
              # Run smoke tests
              curl -X POST https://mcp-dev-func.azurewebsites.net/api/tools/GetDonorPipeline \
                -H "Content-Type: application/json" \
                -d '{"arguments": {}}'
            displayName: 'Run smoke tests'
            timeoutInMinutes: 5

- stage: Deploy_Test
  displayName: Deploy to Test
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  dependsOn: Deploy_Development
  jobs:
  - deployment: Deploy_Test
    displayName: Deploy to Test
    environment: 'Test'
    pool:
      vmImage: 'ubuntu-latest'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: UsePythonVersion@0
            displayName: 'Use Python $(python.version)'
            inputs:
              versionSpec: $(python.version)
          
          - task: DownloadPipelineArtifact@2
            displayName: 'Download package artifact'
            inputs:
              buildType: 'current'
              artifactName: 'mcp-platform-package'
              targetPath: '$(Pipeline.Workspace)/dist'
          
          - script: |
              pip install $(Pipeline.Workspace)/dist/*.whl
            displayName: 'Install package'
          
          - task: AzureCLI@2
            displayName: 'Deploy to Test Function App'
            inputs:
              azureSubscription: 'Azure-MCP-Test'
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                az functionapp deployment source config-zip \
                  --name mcp-test-func \
                  --resource-group mcp-test-rg \
                  --src $(Pipeline.Workspace)/dist/*.zip
                
                # Set application settings
                az functionapp config appsettings set \
                  --name mcp-test-func \
                  --resource-group mcp-test-rg \
                  --settings MCP_ENVIRONMENT=test
                
                # Configure Key Vault integration
                az functionapp config appsettings set \
                  --name mcp-test-func \
                  --resource-group mcp-test-rg \
                  --settings KEY_VAULT_URI=https://mcp-test-kv.vault.azure.net/
                
                # Restart Function App
                az functionapp restart \
                  --name mcp-test-func \
                  --resource-group mcp-test-rg
          
          - script: |
              # Run integration tests against test environment
              python -m pytest tests/integration/test_environment.py --junitxml=test-env-results.xml
            displayName: 'Run environment tests'
            env:
              MCP_ENVIRONMENT: test
              AZURE_SUBSCRIPTION_ID: $(AZURE_SUBSCRIPTION_ID)
              AZURE_RESOURCE_GROUP: mcp-test-rg
          
          - task: PublishTestResults@2
            displayName: 'Publish environment test results'
            inputs:
              testResultsFormat: 'JUnit'
              testResultsFiles: '**/test-env-results.xml'

- stage: Deploy_Staging
  displayName: Deploy to Staging
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  dependsOn: Deploy_Test
  jobs:
  - deployment: Deploy_Staging
    displayName: Deploy to Staging
    environment: 'Staging'
    pool:
      vmImage: 'ubuntu-latest'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: UsePythonVersion@0
            displayName: 'Use Python $(python.version)'
            inputs:
              versionSpec: $(python.version)
          
          - task: DownloadPipelineArtifact@2
            displayName: 'Download package artifact'
            inputs:
              buildType: 'current'
              artifactName: 'mcp-platform-package'
              targetPath: '$(Pipeline.Workspace)/dist'
          
          - script: |
              pip install $(Pipeline.Workspace)/dist/*.whl
            displayName: 'Install package'
          
          - task: AzureCLI@2
            displayName: 'Deploy to Staging Function App'
            inputs:
              azureSubscription: 'Azure-MCP-Staging'
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                az functionapp deployment source config-zip \
                  --name mcp-staging-func \
                  --resource-group mcp-staging-rg \
                  --src $(Pipeline.Workspace)/dist/*.zip
                
                # Set application settings
                az functionapp config appsettings set \
                  --name mcp-staging-func \
                  --resource-group mcp-staging-rg \
                  --settings MCP_ENVIRONMENT=staging
                
                # Configure production-like settings
                az functionapp config appsettings set \
                  --name mcp-staging-func \
                  --resource-group mcp-staging-rg \
                  --settings AZURE_RESOURCE_GROUP=mcp-staging-rg
                
                # Restart Function App
                az functionapp restart \
                  --name mcp-staging-func \
                  --resource-group mcp-staging-rg
          
          - script: |
              # Run UAT tests
              python -m pytest tests/uat --junitxml=uat-results.xml
            displayName: 'Run UAT tests'
            env:
              MCP_ENVIRONMENT: staging
              AZURE_SUBSCRIPTION_ID: $(AZURE_SUBSCRIPTION_ID)
              AZURE_RESOURCE_GROUP: mcp-staging-rg
          
          - task: PublishTestResults@2
            displayName: 'Publish UAT test results'
            inputs:
              testResultsFormat: 'JUnit'
              testResultsFiles: '**/uat-results.xml'
          
          - task: ManualValidation@0
            displayName: 'Manual approval for production'
            timeoutInMinutes: 480
            inputs:
              notifyUsers: 'admin@domain.com,devops@domain.com'
              instructions: 'Please validate the staging deployment and approve for production'
              onTimeout: 'reject'

- stage: Deploy_Production
  displayName: Deploy to Production
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  dependsOn: Deploy_Staging
  jobs:
  - deployment: Deploy_Production
    displayName: Deploy to Production
    environment: 'Production'
    pool:
      vmImage: 'ubuntu-latest'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: UsePythonVersion@0
            displayName: 'Use Python $(python.version)'
            inputs:
              versionSpec: $(python.version)
          
          - task: DownloadPipelineArtifact@2
            displayName: 'Download package artifact'
            inputs:
              buildType: 'current'
              artifactName: 'mcp-platform-package'
              targetPath: '$(Pipeline.Workspace)/dist'
          
          - script: |
              pip install $(Pipeline.Workspace)/dist/*.whl
            displayName: 'Install package'
          
          - task: AzureCLI@2
            displayName: 'Deploy to Production Function App'
            inputs:
              azureSubscription: 'Azure-MCP-Production'
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                # Deploy with zero downtime using deployment slots
                az functionapp deployment slot create \
                  --name mcp-prod-func \
                  --resource-group mcp-prod-rg \
                  --slot staging
                
                az functionapp deployment source config-zip \
                  --name mcp-prod-func \
                  --resource-group mcp-prod-rg \
                  --slot staging \
                  --src $(Pipeline.Workspace)/dist/*.zip
                
                # Set application settings for staging slot
                az functionapp config appsettings set \
                  --name mcp-prod-func \
                  --resource-group mcp-prod-rg \
                  --slot staging \
                  --settings MCP_ENVIRONMENT=production
                
                # Warm up the staging slot
                curl -X POST https://mcp-prod-func-staging.azurewebsites.net/api/tools/HealthCheck \
                  -H "Content-Type: application/json" \
                  -d '{"arguments": {}}'
                
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
          
          - script: |
              # Run production smoke tests
              python -m pytest tests/production/smoke.py --junitxml=prod-smoke-results.xml
            displayName: 'Run production smoke tests'
            env:
              MCP_ENVIRONMENT: production
              AZURE_SUBSCRIPTION_ID: $(AZURE_SUBSCRIPTION_ID)
              AZURE_RESOURCE_GROUP: mcp-prod-rg
          
          - task: PublishTestResults@2
            displayName: 'Publish production smoke test results'
            inputs:
              testResultsFormat: 'JUnit'
              testResultsFiles: '**/prod-smoke-results.xml'
          
          - script: |
              # Send deployment notification
              echo "Production deployment completed successfully"
              # Add your notification logic here (email, Teams, Slack, etc.)
            displayName: 'Send deployment notification'
```

## 🔄 Environment Promotion Pipeline

**azure-pipelines/promote.yml**
```yaml
name: $(Build.BuildNumber)-promote-$(Date:yyyyMMdd)

trigger: none

parameters:
- name: sourceEnvironment
  displayName: 'Source Environment'
  type: string
  default: test
  values:
  - development
  - test
  - staging

- name: targetEnvironment
  displayName: 'Target Environment'
  type: string
  default: staging
  values:
  - test
  - staging
  - production

- name: buildId
  displayName: 'Build ID'
  type: string
  default: ''

stages:
- stage: Validate
  displayName: Validate Source Environment
  jobs:
  - job: Validate_Source
    displayName: Validate Source Environment
    pool:
      vmImage: 'ubuntu-latest'
    
    steps:
    - script: |
        echo "Validating source environment: ${{ parameters.sourceEnvironment }}"
        echo "Target environment: ${{ parameters.targetEnvironment }}"
      displayName: 'Display promotion details'
    
    - task: AzureCLI@2
      displayName: 'Check source Function App'
      inputs:
        azureSubscription: 'Azure-MCP-${{ parameters.sourceEnvironment }}'
        scriptType: 'bash'
        scriptLocation: 'inlineScript'
        inlineScript: |
          az functionapp show \
            --name mcp-${{ parameters.sourceEnvironment }}-func \
            --resource-group mcp-${{ parameters.sourceEnvironment }}-rg
          
          # Check if Function App is running
          STATUS=$(az functionapp show \
            --name mcp-${{ parameters.sourceEnvironment }}-func \
            --resource-group mcp-${{ parameters.sourceEnvironment }}-rg \
            --query state \
            --output tsv)
          
          if [ "$STATUS" != "Running" ]; then
            echo "Source Function App is not running"
            exit 1
          fi
    
    - task: AzureCLI@2
      displayName: 'Check target Function App'
      inputs:
        azureSubscription: 'Azure-MCP-${{ parameters.targetEnvironment }}'
        scriptType: 'bash'
        scriptLocation: 'inlineScript'
        inlineScript: |
          az functionapp show \
            --name mcp-${{ parameters.targetEnvironment }}-func \
            --resource-group mcp-${{ parameters.targetEnvironment }}-rg
    
    - script: |
        # Validate environment promotion path
        if [ "${{ parameters.sourceEnvironment }}" = "development" ] && [ "${{ parameters.targetEnvironment }}" != "test" ]; then
          echo "Invalid promotion: development can only promote to test"
          exit 1
        fi
        
        if [ "${{ parameters.sourceEnvironment }}" = "test" ] && [ "${{ parameters.targetEnvironment }}" != "staging" ]; then
          echo "Invalid promotion: test can only promote to staging"
          exit 1
        fi
        
        if [ "${{ parameters.sourceEnvironment }}" = "staging" ] && [ "${{ parameters.targetEnvironment }}" != "production" ]; then
          echo "Invalid promotion: staging can only promote to production"
          exit 1
        fi
      displayName: 'Validate promotion path'

- stage: Approve
  displayName: Approval Gate
  dependsOn: Validate
  condition: and(succeeded(), ne('${{ parameters.targetEnvironment }}', 'development'))
  jobs:
  - job: Approve_Promotion
    displayName: Approve Promotion
    pool: server
    timeoutInMinutes: 480
    
    steps:
    - task: ManualValidation@0
      displayName: 'Approve promotion to ${{ parameters.targetEnvironment }}'
      inputs:
        notifyUsers: 'admin@domain.com,devops@domain.com'
        instructions: |
          Please review and approve the promotion from ${{ parameters.sourceEnvironment }} to ${{ parameters.targetEnvironment }}.
          
          Source: mcp-${{ parameters.sourceEnvironment }}-func
          Target: mcp-${{ parameters.targetEnvironment }}-func
          
          Build ID: ${{ parameters.buildId }}
        onTimeout: 'reject'

- stage: Deploy
  displayName: Deploy to Target Environment
  dependsOn: Approve
  condition: and(succeeded(), eq(dependencies.Approve.result, 'Succeeded'))
  jobs:
  - deployment: Deploy_Target
    displayName: Deploy to ${{ parameters.targetEnvironment }}
    environment: '${{ parameters.targetEnvironment }}'
    pool:
      vmImage: 'ubuntu-latest'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: UsePythonVersion@0
            displayName: 'Use Python 3.11'
            inputs:
              versionSpec: '3.11'
          
          - task: DownloadBuildFromCurrentPipeline@0
            displayName: 'Download build artifact'
            condition: and(succeeded(), ne('${{ parameters.buildId }}', ''))
            inputs:
              buildType: 'specific'
              project: 'mcp-platform'
              definition: 'MCP-Platform-Build'
              buildVersionToDownload: 'specific'
              buildId: '${{ parameters.buildId }}'
              artifactName: 'mcp-platform-package'
              targetPath: '$(Pipeline.Workspace)/dist'
          
          - task: DownloadPipelineArtifact@2
            displayName: 'Download current build artifact'
            condition: eq('${{ parameters.buildId }}', '')
            inputs:
              buildType: 'current'
              artifactName: 'mcp-platform-package'
              targetPath: '$(Pipeline.Workspace)/dist'
          
          - script: |
              pip install $(Pipeline.Workspace)/dist/*.whl
            displayName: 'Install package'
          
          - task: AzureCLI@2
            displayName: 'Deploy to ${{ parameters.targetEnvironment }}'
            inputs:
              azureSubscription: 'Azure-MCP-${{ parameters.targetEnvironment }}'
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                az functionapp deployment source config-zip \
                  --name mcp-${{ parameters.targetEnvironment }}-func \
                  --resource-group mcp-${{ parameters.targetEnvironment }}-rg \
                  --src $(Pipeline.Workspace)/dist/*.zip
                
                # Set environment-specific settings
                az functionapp config appsettings set \
                  --name mcp-${{ parameters.targetEnvironment }}-func \
                  --resource-group mcp-${{ parameters.targetEnvironment }}-rg \
                  --settings MCP_ENVIRONMENT=${{ parameters.targetEnvironment }}
                
                # Restart Function App
                az functionapp restart \
                  --name mcp-${{ parameters.targetEnvironment }}-func \
                  --resource-group mcp-${{ parameters.targetEnvironment }}-rg
          
          - script: |
              # Run post-deployment tests
              python -m pytest tests/environment/${{ parameters.targetEnvironment }}.py --junitxml=post-deploy-results.xml
            displayName: 'Run post-deployment tests'
            env:
              MCP_ENVIRONMENT: ${{ parameters.targetEnvironment }}
              AZURE_SUBSCRIPTION_ID: $(AZURE_SUBSCRIPTION_ID)
              AZURE_RESOURCE_GROUP: mcp-${{ parameters.targetEnvironment }}-rg
          
          - task: PublishTestResults@2
            displayName: 'Publish post-deployment test results'
            inputs:
              testResultsFormat: 'JUnit'
              testResultsFiles: '**/post-deploy-results.xml'
          
          - script: |
              echo "Successfully promoted from ${{ parameters.sourceEnvironment }} to ${{ parameters.targetEnvironment }}"
            displayName: 'Promotion complete'
```

## 📁 Pipeline Templates

### Build Template

**azure-pipelines/templates/build-template.yml**
```yaml
parameters:
- name: pythonVersion
  type: string
  default: '3.11'

- name: testTypes
  type: object
  default:
    unit: true
    integration: false
    security: false

- name: environment
  type: string
  default: 'development'

steps:
- task: UsePythonVersion@0
  displayName: 'Use Python ${{ parameters.pythonVersion }}'
  inputs:
    versionSpec: ${{ parameters.pythonVersion }}
    addToPath: true

- script: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if [ "${{ parameters.testTypes.integration }}" = "true" ] || [ "${{ parameters.testTypes.security }}" = "true" ]; then
      pip install -r requirements-dev.txt
    fi
  displayName: 'Install dependencies'

- script: |
    pip install -e .
  displayName: 'Install package'

- script: |
    python -m pytest tests/unit --cov=mcp_framework --cov-report=xml --junitxml=unit-results.xml
  displayName: 'Run unit tests'
  condition: eq(${{ parameters.testTypes.unit }}, true)
  env:
    MCP_ENVIRONMENT: ${{ parameters.environment }}

- task: PublishTestResults@2
  displayName: 'Publish unit test results'
  condition: and(succeeded(), eq(${{ parameters.testTypes.unit }}, true))
  inputs:
    testResultsFormat: 'JUnit'
    testResultsFiles: '**/unit-results.xml'

- task: PublishCodeCoverageResults@1
  displayName: 'Publish code coverage'
  condition: and(succeeded(), eq(${{ parameters.testTypes.unit }}, true))
  inputs:
    codeCoverageTool: 'Cobertura'
    summaryFileLocation: '**/coverage.xml'

- script: |
    python -m pytest tests/integration --junitxml=integration-results.xml
  displayName: 'Run integration tests'
  condition: eq(${{ parameters.testTypes.integration }}, true)
  env:
    MCP_ENVIRONMENT: ${{ parameters.environment }}
    AZURE_SUBSCRIPTION_ID: $(AZURE_SUBSCRIPTION_ID)
    AZURE_RESOURCE_GROUP: mcp-${{ parameters.environment }}-rg

- task: PublishTestResults@2
  displayName: 'Publish integration test results'
  condition: and(succeeded(), eq(${{ parameters.testTypes.integration }}, true))
  inputs:
    testResultsFormat: 'JUnit'
    testResultsFiles: '**/integration-results.xml'

- script: |
    python -m pytest tests/security --junitxml=security-results.xml
  displayName: 'Run security tests'
  condition: eq(${{ parameters.testTypes.security }}, true)

- task: PublishTestResults@2
  displayName: 'Publish security test results'
  condition: and(succeeded(), eq(${{ parameters.testTypes.security }}, true))
  inputs:
    testResultsFormat: 'JUnit'
    testResultsFiles: '**/security-results.xml'

- script: |
    pip install build twine
    python -m build
  displayName: 'Build package'

- task: PublishPipelineArtifact@1
  displayName: 'Publish package artifact'
  inputs:
    targetPath: 'dist'
    artifact: 'mcp-platform-package'
    publishLocation: 'pipeline'
```

### Deploy Template

**azure-pipelines/templates/deploy-template.yml**
```yaml
parameters:
- name: environment
  type: string

- name: serviceConnection
  type: string

- name: functionAppName
  type: string

- name: resourceGroup
  type: string

- name: runSmokeTests
  type: boolean
  default: true

- name: useDeploymentSlots
  type: boolean
  default: false

steps:
- task: UsePythonVersion@0
  displayName: 'Use Python 3.11'
  inputs:
    versionSpec: '3.11'

- task: DownloadPipelineArtifact@2
  displayName: 'Download package artifact'
  inputs:
    buildType: 'current'
    artifactName: 'mcp-platform-package'
    targetPath: '$(Pipeline.Workspace)/dist'

- script: |
    pip install $(Pipeline.Workspace)/dist/*.whl
  displayName: 'Install package'

- task: AzureCLI@2
  displayName: 'Deploy to ${{ parameters.environment }} Function App'
  inputs:
    azureSubscription: ${{ parameters.serviceConnection }}
    scriptType: 'bash'
    scriptLocation: 'inlineScript'
    inlineScript: |
      if [ "${{ parameters.useDeploymentSlots }}" = "true" ]; then
        # Create deployment slot
        az functionapp deployment slot create \
          --name ${{ parameters.functionAppName }} \
          --resource-group ${{ parameters.resourceGroup }} \
          --slot staging
        
        # Deploy to staging slot
        az functionapp deployment source config-zip \
          --name ${{ parameters.functionAppName }} \
          --resource-group ${{ parameters.resourceGroup }} \
          --slot staging \
          --src $(Pipeline.Workspace)/dist/*.zip
        
        # Set application settings for staging slot
        az functionapp config appsettings set \
          --name ${{ parameters.functionAppName }} \
          --resource-group ${{ parameters.resourceGroup }} \
          --slot staging \
          --settings MCP_ENVIRONMENT=${{ parameters.environment }}
        
        # Warm up staging slot
        curl -X POST https://${{ parameters.functionAppName }}-staging.azurewebsites.net/api/tools/HealthCheck \
          -H "Content-Type: application/json" \
          -d '{"arguments": {}}' \
          --retry 5 --retry-delay 10
        
        # Swap slots
        az functionapp deployment slot swap \
          --name ${{ parameters.functionAppName }} \
          --resource-group ${{ parameters.resourceGroup }} \
          --slot staging \
          --target-slot production
        
        # Clean up old staging slot
        az functionapp deployment slot delete \
          --name ${{ parameters.functionAppName }} \
          --resource-group ${{ parameters.resourceGroup }} \
          --slot staging
      else
        # Direct deployment
        az functionapp deployment source config-zip \
          --name ${{ parameters.functionAppName }} \
          --resource-group ${{ parameters.resourceGroup }} \
          --src $(Pipeline.Workspace)/dist/*.zip
        
        # Set application settings
        az functionapp config appsettings set \
          --name ${{ parameters.functionAppName }} \
          --resource-group ${{ parameters.resourceGroup }} \
          --settings MCP_ENVIRONMENT=${{ parameters.environment }}
        
        # Restart Function App
        az functionapp restart \
          --name ${{ parameters.functionAppName }} \
          --resource-group ${{ parameters.resourceGroup }}
      fi

- script: |
    # Run smoke tests
    if [ "${{ parameters.runSmokeTests }}" = "true" ]; then
      python -m pytest tests/smoke --junitxml=smoke-results.xml
    fi
  displayName: 'Run smoke tests'
  condition: eq(${{ parameters.runSmokeTests }}, true)
  env:
    MCP_ENVIRONMENT: ${{ parameters.environment }}
    AZURE_SUBSCRIPTION_ID: $(AZURE_SUBSCRIPTION_ID)
    AZURE_RESOURCE_GROUP: ${{ parameters.resourceGroup }}

- task: PublishTestResults@2
  displayName: 'Publish smoke test results'
  condition: and(succeeded(), eq(${{ parameters.runSmokeTests }}, true))
  inputs:
    testResultsFormat: 'JUnit'
    testResultsFiles: '**/smoke-results.xml'
```

## 🌐 Environment Configurations

### Development Environment

**azure-pipelines/environments/development.yml**
```yaml
name: Development

variables:
  - name: environment
    value: development
  - name: functionAppName
    value: mcp-dev-func
  - name: resourceGroup
    value: mcp-dev-rg
  - name: serviceConnection
    value: Azure-MCP-Development
  - name: useDeploymentSlots
    value: false
  - name: runSmokeTests
    value: true

resources:
  repositories:
  - repository: self

trigger: none

pr: none
```

### Test Environment

**azure-pipelines/environments/test.yml**
```yaml
name: Test

variables:
  - name: environment
    value: test
  - name: functionAppName
    value: mcp-test-func
  - name: resourceGroup
    value: mcp-test-rg
  - name: serviceConnection
    value: Azure-MCP-Test
  - name: useDeploymentSlots
    value: false
  - name: runSmokeTests
    value: true

resources:
  repositories:
  - repository: self

trigger: none

pr: none
```

### Staging Environment

**azure-pipelines/environments/staging.yml**
```yaml
name: Staging

variables:
  - name: environment
    value: staging
  - name: functionAppName
    value: mcp-staging-func
  - name: resourceGroup
    value: mcp-staging-rg
  - name: serviceConnection
    value: Azure-MCP-Staging
  - name: useDeploymentSlots
    value: false
  - name: runSmokeTests
    value: true

resources:
  repositories:
  - repository: self

trigger: none

pr: none

# Manual validation gate for production
- deployment: Manual_Approval
  displayName: Manual Approval
  environment: Staging
  pool: server
  strategy:
    runOnce:
      deploy:
        steps:
        - task: ManualValidation@0
          displayName: 'Approve for production'
          timeoutInMinutes: 480
          inputs:
            notifyUsers: 'admin@domain.com,devops@domain.com'
            instructions: 'Please validate the staging deployment and approve for production'
            onTimeout: 'reject'
```

### Production Environment

**azure-pipelines/environments/production.yml**
```yaml
name: Production

variables:
  - name: environment
    value: production
  - name: functionAppName
    value: mcp-prod-func
  - name: resourceGroup
    value: mcp-prod-rg
  - name: serviceConnection
    value: Azure-MCP-Production
  - name: useDeploymentSlots
    value: true
  - name: runSmokeTests
    value: true

resources:
  repositories:
  - repository: self

trigger: none

pr: none

# Production deployment requires manual approval
- deployment: Manual_Approval
  displayName: Manual Approval
  environment: Production
  pool: server
  strategy:
    runOnce:
      deploy:
        steps:
        - task: ManualValidation@0
          displayName: 'Approve production deployment'
          timeoutInMinutes: 1440
          inputs:
            notifyUsers: 'admin@domain.com,devops@domain.com,security@domain.com'
            instructions: |
              Production deployment requires approval from:
              - DevOps Team
              - Security Team
              - Business Owner
              
              Please ensure all checks are completed before approving.
            onTimeout: 'reject'
```

## 🔐 Security Configuration

### Pipeline Security

```yaml
# Secure pipeline variables
variables:
  - group: 'MCP-Production-Variables'  # Variable group in Azure DevOps

# Service connections with least privilege
# - Development: Contributor on dev resources
# - Test: Contributor on test resources
# - Staging: Contributor on staging resources
# - Production: Contributor on production resources (with approvals)

# Secure file handling
- task: DownloadSecureFile@1
  displayName: 'Download secure configuration'
  inputs:
    secureFile: 'mcp-production-config.json'
    retryCount: 3

# Secret scanning in pipeline
- task: CredentialScan@3
  displayName: 'Scan for secrets'
  inputs:
    toolMajorVersion: 'V2'
    suppressionsFile: '.gdn/credential-suppressions.json'
    debugMode: false
```

### Variable Groups

1. **Create Variable Groups in Azure DevOps:**
   - Go to Pipelines → Library
   - Click "+ Variable group"
   - Add variables for each environment

2. **Development Variables:**
   - `AZURE_SUBSCRIPTION_ID`: Development subscription ID
   - `AZURE_RESOURCE_GROUP`: mcp-dev-rg
   - `KEY_VAULT_NAME`: mcp-dev-kv
   - `FABRIC_TENANT_ID`: Development Fabric tenant ID
   - `FABRIC_WORKSPACE_ID`: Development workspace ID

3. **Production Variables:**
   - `AZURE_SUBSCRIPTION_ID`: Production subscription ID
   - `AZURE_RESOURCE_GROUP`: mcp-prod-rg
   - `KEY_VAULT_URI`: https://mcp-prod-kv.vault.azure.net/
   - `FABRIC_TENANT_ID`: Production Fabric tenant ID
   - `FABRIC_WORKSPACE_ID`: Production workspace ID

### Service Connection Security

- **Principle of Least Privilege**: Each service connection should have only the permissions it needs
- **Separate Connections**: Use separate service connections for each environment
- **Managed Identity**: Consider using Managed Identity instead of service principals
- **Certificate Authentication**: Use certificate-based authentication for production

## 📊 Monitoring and Alerts

### Pipeline Monitoring

```yaml
# Add monitoring to your pipeline
- task: AzureMonitor@0
  displayName: 'Monitor deployment'
  inputs:
    azureSubscription: 'Azure-MCP-Monitoring'
    action: 'QueryLogAnalytics'
    workspaceId: '/subscriptions/.../resourceGroups/.../providers/Microsoft.OperationalInsights/workspaces/...'
    query: |
      requests
      | where timestamp > ago(1h)
      | where success == false
      | project timestamp, operation_Name, resultCode, resultDescription
      | order by timestamp desc
    logType: 'AzureDiagnostics'
    timeRange: 'PT1H'
    outputVariable: 'failedRequests'

# Create alerts for pipeline failures
- task: AzureCLI@2
  displayName: 'Create deployment alert'
  inputs:
    azureSubscription: 'Azure-MCP-Monitoring'
    scriptType: 'bash'
    scriptLocation: 'inlineScript'
    inlineScript: |
      # Create alert for failed deployments
      az monitor metrics alert create \
        --name "MCP-Deployment-Failed" \
        --resource-group mcp-monitoring-rg \
        --scopes "/subscriptions/.../resourceGroups/mcp-prod-rg/providers/Microsoft.Web/sites/mcp-prod-func" \
        --condition "Failed Requests > 0" \
        --description "MCP Platform deployment failed" \
        --actions "your-email@domain.com" \
        --severity 2
```

### Pipeline Dashboards

1. **Create a Pipeline Dashboard:**
   - Go to your project → Dashboards
   - Click "New dashboard"
   - Add widgets for:
     - Pipeline status
     - Test results
     - Deployment frequency
     - Build success rate
     - Deployment duration

2. **Add Pipeline Widgets:**
   - Build history
   - Release history
   - Test results trend
   - Code coverage trend
   - Deployment frequency

## 🛡️ Compliance and Governance

### Pipeline Compliance

```yaml
# Add compliance checks to your pipeline
- task: PowerShell@2
  displayName: 'Check pipeline compliance'
  inputs:
    targetType: 'inline'
    script: |
      # Check for required approvals
      $requiredApprovals = @("Development", "Test", "Staging")
      $currentEnvironment = "${{ parameters.environment }}"
      
      if ($currentEnvironment -eq "Production" -and $env:SYSTEM_APPROVALID -eq "") {
        Write-Error "Production deployment requires manual approval"
        exit 1
      }
      
      # Check for security scans
      if ($currentEnvironment -ne "Development") {
        if (-not (Test-Path "$(Pipeline.Workspace)/security-scan-results.xml")) {
          Write-Error "Security scan results not found"
          exit 1
        }
      }

# Add governance tags to resources
- task: AzureCLI@2
  displayName: 'Tag deployed resources'
  inputs:
    azureSubscription: ${{ parameters.serviceConnection }}
    scriptType: 'bash'
    scriptLocation: 'inlineScript'
    inlineScript: |
      # Tag Function App with governance information
      az functionapp update \
        --name ${{ parameters.functionAppName }} \
        --resource-group ${{ parameters.resourceGroup }} \
        --tags Environment=${{ parameters.environment }} \
          Owner=MCP-Platform \
          CostCenter=IT \
          Compliance=ISO27001 \
          Pipeline=$(Build.BuildId)
```

### Audit Logging

```yaml
# Enable audit logging for pipeline
- task: AzureCLI@2
  displayName: 'Log pipeline execution'
  inputs:
    azureSubscription: 'Azure-MCP-Monitoring'
    scriptType: 'bash'
    scriptLocation: 'inlineScript'
    inlineScript: |
      # Log pipeline execution to Log Analytics
      az monitor log-analytics data collect \
        --workspace "/subscriptions/.../resourceGroups/.../providers/Microsoft.OperationalInsights/workspaces/..." \
        --data '{
          "TimeGenerated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
          "PipelineId": "$(System.DefinitionId)",
          "PipelineName": "$(System.DefinitionName)",
          "BuildId": "$(Build.BuildId)",
          "BuildNumber": "$(Build.BuildNumber)",
          "Environment": "${{ parameters.environment }}",
          "Status": "$(Agent.JobStatus)",
          "RequestedFor": "$(Build.RequestedFor)",
          "SourceBranch": "$(Build.SourceBranch)",
          "SourceVersion": "$(Build.SourceVersion)"
        }'
```

## ⚡ Performance Optimization

### Pipeline Optimization

```yaml
# Optimized pipeline with parallel jobs
stages:
- stage: Build
  displayName: Build
  jobs:
  - job: Build_Package
    displayName: Build Package
    pool:
      vmImage: 'ubuntu-latest'
    steps:
    - template: templates/build-template.yml
      parameters:
        pythonVersion: '3.11'
        testTypes:
          unit: true
          integration: false
          security: false
        environment: 'development'

  - job: Run_Integration_Tests
    displayName: Integration Tests
    dependsOn: Build_Package
    pool:
      vmImage: 'ubuntu-latest'
    steps:
    - template: templates/build-template.yml
      parameters:
        pythonVersion: '3.11'
        testTypes:
          unit: false
          integration: true
          security: false
        environment: 'test'
    env:
      AZURE_SUBSCRIPTION_ID: $(AZURE_SUBSCRIPTION_ID)
      AZURE_RESOURCE_GROUP: mcp-test-rg

  - job: Run_Security_Tests
    displayName: Security Tests
    dependsOn: Build_Package
    pool:
      vmImage: 'ubuntu-latest'
    steps:
    - template: templates/build-template.yml
      parameters:
        pythonVersion: '3.11'
        testTypes:
          unit: false
          integration: false
          security: true
        environment: 'test'

# Use parallel execution for tests
- script: |
    python -m pytest tests/unit -n auto --dist=loadfile
  displayName: 'Run unit tests in parallel'
  env:
    PYTEST_XDIST_WORKER_COUNT: 4
```

### Caching Strategies

```yaml
# Cache multiple dependencies
- task: Cache@2
  displayName: 'Cache pip packages'
  inputs:
    key: 'pip-$(python.version)-$(hash(