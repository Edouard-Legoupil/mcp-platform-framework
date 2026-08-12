# 🌍 Environment Configuration Guide

## Overview

This guide covers environment-specific configuration for deploying the MCP Platform Framework to different environments (Development, Test, Staging, Production) in Azure.

## 🎯 Environment Strategy

The MCP Platform Framework supports a multi-environment deployment strategy with the following environments:

| Environment | Purpose | Characteristics | Cost Optimization |
|-------------|---------|----------------|-------------------|
| **Development** | Local development | Full debugging, hot-reload | Low cost, local resources |
| **Test** | Automated testing | CI/CD integration, test data | Shared test resources |
| **Staging** | Pre-production validation | Production-like, user testing | Reduced scale |
| **Production** | Live deployment | Full scale, high availability | Production resources |

## 📋 Environment Configuration Files

Each environment has its own configuration file in the `config/` directory:

```
config/
├── default.json          # Shared defaults across all environments
├── development.json      # Development environment
├── test.json             # Test environment
├── staging.json          # Staging environment
└── production.json       # Production environment
```

## 🏗️ Development Environment

### Purpose
- Local development and testing
- Rapid iteration and debugging
- Individual developer workstations

### Configuration

**config/development.json**
```json
{
  "environment": "development",
  "debug": true,
  "log_level": "DEBUG",
  "hot_reload": true,
  
  "azure": {
    "subscription_id": "dev-subscription-id",
    "resource_group": "mcp-dev-rg",
    "location": "eastus",
    "use_emulator": true
  },
  
  "fabric": {
    "tenant_id": "dev-tenant-id",
    "workspace_id": "dev-workspace-id",
    "use_test_data": true
  },
  
  "function_app": {
    "host": "localhost",
    "port": 7071,
    "use_local_storage": true
  },
  
  "telemetry": {
    "enabled": true,
    "console_output": true,
    "application_insights": false
  },
  
  "authentication": {
    "enabled": true,
    "require_authentication": false,
    "mock_auth": true
  },
  
  "audit": {
    "enabled": false
  }
}
```

### Local Development Setup

```bash
# Clone the repository
git clone https://github.com/your-org/mcp-platform-framework.git
cd mcp-platform-framework

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Create local.settings.json for Function App
cat > local.settings.json << EOF
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "FUNCTIONS_EXTENSION_VERSION": "~4",
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "MCP_ENVIRONMENT": "development",
    "AZURE_SUBSCRIPTION_ID": "dev-subscription-id",
    "AZURE_RESOURCE_GROUP": "mcp-dev-rg"
  }
}
EOF

# Run the Function App locally
func start
```

### Development Tools

- **Azure Storage Emulator**: For local storage testing
- **Azure Functions Core Tools**: For local Function App execution
- **VS Code Debugger**: For debugging MCP tools
- **Postman/Newman**: For API testing

```bash
# Install Azure Functions Core Tools
npm install -g azure-functions-core-tools@4

# Start Azure Storage Emulator (Windows)
AzureStorageEmulator.exe start

# Start Azure Storage Emulator (Docker)
docker run -p 10000:10000 -p 10001:10001 mcr.microsoft.com/azure-storage/azurite
```

## 🧪 Test Environment

### Purpose
- Automated testing in CI/CD pipelines
- Integration testing with test data
- Performance and load testing

### Configuration

**config/test.json**
```json
{
  "environment": "test",
  "debug": false,
  "log_level": "INFO",
  "hot_reload": false,
  
  "azure": {
    "subscription_id": "test-subscription-id",
    "resource_group": "mcp-test-rg",
    "location": "eastus",
    "use_emulator": false
  },
  
  "fabric": {
    "tenant_id": "test-tenant-id",
    "workspace_id": "test-workspace-id",
    "use_test_data": true,
    "test_semantic_models": [
      "TestDonorModel",
      "TestFinancialModel",
      "TestCampaignModel"
    ]
  },
  
  "function_app": {
    "host": "mcp-test-func.azurewebsites.net",
    "port": 443,
    "use_https": true
  },
  
  "telemetry": {
    "enabled": true,
    "console_output": false,
    "application_insights": true,
    "tracking_level": "INFO"
  },
  
  "authentication": {
    "enabled": true,
    "require_authentication": true,
    "mock_auth": false,
    "test_users": [
      {
        "username": "test.user@domain.com",
        "roles": ["donor_analyst", "test_user"],
        "permissions": ["donor.read", "test.all"]
      }
    ]
  },
  
  "audit": {
    "enabled": true,
    "log_level": "INFO",
    "retention_days": 30
  },
  
  "testing": {
    "run_integration_tests": true,
    "run_performance_tests": true,
    "run_security_tests": true,
    "test_data_path": "/test-data"
  }
}
```

### Test Environment Setup

```bash
# Create test resource group
az group create --name mcp-test-rg --location eastus

# Deploy test resources
az deployment group create \
  --resource-group mcp-test-rg \
  --template-file infrastructure/test.bicep \
  --parameters environment=test

# Configure test Key Vault
az keyvault create --name mcp-test-kv --resource-group mcp-test-rg --location eastus
az keyvault secret set --vault-name mcp-test-kv --name test-secret --value "test-value"

# Grant test permissions
az role assignment create \
  --assignee "test-service-principal" \
  --role "Contributor" \
  --resource-group mcp-test-rg
```

### Test Data Management

```bash
# Create test Fabric workspace
az fabric workspace create --name test-workspace --resource-group mcp-test-rg

# Deploy test semantic models
az fabric semantic-model create \
  --workspace test-workspace \
  --name TestDonorModel \
  --definition @test-models/donor-model.json

# Load test data
az fabric lakehouse data load \
  --workspace test-workspace \
  --lakehouse TestLakehouse \
  --source @test-data/donors.csv \
  --target-table Donors
```

## 🚀 Staging Environment

### Purpose
- Pre-production validation
- User acceptance testing (UAT)
- Performance testing with production-like data
- Final validation before production deployment

### Configuration

**config/staging.json**
```json
{
  "environment": "staging",
  "debug": false,
  "log_level": "INFO",
  "hot_reload": false,
  
  "azure": {
    "subscription_id": "staging-subscription-id",
    "resource_group": "mcp-staging-rg",
    "location": "eastus2",
    "use_emulator": false,
    "scale": {
      "function_app": {
        "sku": "P1v2",
        "min_instances": 1,
        "max_instances": 3
      },
      "app_service_plan": "B1"
    }
  },
  
  "fabric": {
    "tenant_id": "staging-tenant-id",
    "workspace_id": "staging-workspace-id",
    "use_production_data": false,
    "data_volume": "medium"
  },
  
  "function_app": {
    "host": "mcp-staging-func.azurewebsites.net",
    "port": 443,
    "use_https": true,
    "cors_origins": [
      "https://staging.domain.com",
      "https://uat.domain.com"
    ]
  },
  
  "telemetry": {
    "enabled": true,
    "console_output": false,
    "application_insights": true,
    "tracking_level": "INFO",
    "sample_rate": 100
  },
  
  "authentication": {
    "enabled": true,
    "require_authentication": true,
    "mock_auth": false,
    "allowed_audiences": ["api://mcp-platform-staging"],
    "token_validation": {
      "issuer": "https://login.microsoftonline.com/staging-tenant-id/v2.0",
      "audience": "api://mcp-platform-staging",
      "lifetime": 3600
    }
  },
  
  "authorization": {
    "enabled": true,
    "rbac": {
      "enabled": true,
      "roles": {
        "staging_user": {
          "permissions": ["donor.read", "finance.read"],
          "description": "Staging environment user"
        },
        "staging_admin": {
          "permissions": ["*"],
          "description": "Staging environment administrator"
        }
      }
    }
  },
  
  "audit": {
    "enabled": true,
    "log_level": "INFO",
    "retention_days": 90,
    "compliance": {
      "enabled": true,
      "standards": ["ISO27001"]
    }
  },
  
  "feature_flags": {
    "new_features": {
      "enabled": true,
      "rollout_percentage": 50
    },
    "experimental_features": {
      "enabled": true,
      "enabled_for": ["admin@domain.com"]
    }
  }
}
```

### Staging Environment Setup

```bash
# Create staging resource group
az group create --name mcp-staging-rg --location eastus2

# Deploy staging infrastructure
az deployment group create \
  --resource-group mcp-staging-rg \
  --template-file infrastructure/staging.bicep \
  --parameters environment=staging

# Configure staging Key Vault
az keyvault create --name mcp-staging-kv --resource-group mcp-staging-rg --location eastus2
az keyvault set-policy --name mcp-staging-kv \
  --object-id <staging-service-principal> \
  --secret-permissions get list set delete

# Deploy staging Function App
az functionapp create \
  --name mcp-staging-func \
  --resource-group mcp-staging-rg \
  --consumption-plan-location eastus2 \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --storage-account mcpstagingstorage \
  --os-type Linux

# Configure Application Insights
az monitor app-insights create \
  --name mcp-staging-insights \
  --resource-group mcp-staging-rg \
  --location eastus2 \
  --application-type web

# Connect Function App to Application Insights
az functionapp update \
  --name mcp-staging-func \
  --resource-group mcp-staging-rg \
  --app-insights mcp-staging-insights
```

### Staging Data Setup

```bash
# Create staging Fabric workspace
az fabric workspace create --name staging-workspace --resource-group mcp-staging-rg

# Deploy staging semantic models (subset of production)
az fabric semantic-model create \
  --workspace staging-workspace \
  --name DonorManagementModel \
  --definition @models/donor-model.json

# Load staging data (anonymized production data)
az fabric lakehouse data load \
  --workspace staging-workspace \
  --lakehouse StagingLakehouse \
  --source @data/staging-donors.csv \
  --target-table Donors
```

## 🏭 Production Environment

### Purpose
- Live production deployment
- High availability and scalability
- Full production data
- End-user access

### Configuration

**config/production.json**
```json
{
  "environment": "production",
  "debug": false,
  "log_level": "WARNING",
  "hot_reload": false,
  
  "azure": {
    "subscription_id": "production-subscription-id",
    "resource_group": "mcp-prod-rg",
    "location": "eastus2",
    "use_emulator": false,
    "scale": {
      "function_app": {
        "sku": "P2v2",
        "min_instances": 2,
        "max_instances": 10,
        "auto_scale": true
      },
      "app_service_plan": "P2v2"
    },
    "high_availability": {
      "enabled": true,
      "zones": [1, 2, 3],
      "backup": {
        "enabled": true,
        "frequency": "Daily",
        "retention_days": 30
      }
    }
  },
  
  "fabric": {
    "tenant_id": "production-tenant-id",
    "workspace_id": "production-workspace-id",
    "use_production_data": true,
    "data_volume": "large",
    "cache": {
      "enabled": true,
      "ttl": 3600
    }
  },
  
  "function_app": {
    "host": "mcp-prod-func.azurewebsites.net",
    "port": 443,
    "use_https": true,
    "cors_origins": [
      "https://domain.com",
      "https://www.domain.com",
      "https://app.domain.com"
    ],
    "custom_domains": [
      "mcp.domain.com",
      "api.domain.com"
    ]
  },
  
  "telemetry": {
    "enabled": true,
    "console_output": false,
    "application_insights": true,
    "tracking_level": "WARNING",
    "sample_rate": 100,
    "export_to_log_analytics": true
  },
  
  "authentication": {
    "enabled": true,
    "require_authentication": true,
    "mock_auth": false,
    "allowed_audiences": ["api://mcp-platform"],
    "token_validation": {
      "issuer": "https://login.microsoftonline.com/production-tenant-id/v2.0",
      "audience": "api://mcp-platform",
      "lifetime": 3600,
      "clock_skew": 300
    },
    "multi_tenant": false
  },
  
  "authorization": {
    "enabled": true,
    "rbac": {
      "enabled": true,
      "roles": {
        "donor_analyst": {
          "permissions": ["donor.read", "donor.analytics"],
          "description": "Access to donor data and analytics"
        },
        "finance_manager": {
          "permissions": ["finance.read", "finance.write", "finance.forecast"],
          "description": "Full access to financial data"
        },
        "campaign_manager": {
          "permissions": ["campaign.read", "campaign.write", "campaign.analytics"],
          "description": "Full access to campaign data"
        },
        "admin": {
          "permissions": ["*"],
          "description": "Full access to all data and features"
        }
      }
    },
    "policy_enforcement": {
      "enabled": true,
      "policies": [
        {
          "name": "require-classification",
          "description": "All tools must have classification declared"
        },
        {
          "name": "audit-sensitive-access",
          "description": "Audit all access to CONFIDENTIAL and STRICTLY_CONFIDENTIAL data"
        },
        {
          "name": "rate-limiting",
          "description": "Apply rate limiting to prevent abuse"
        }
      ]
    }
  },
  
  "audit": {
    "enabled": true,
    "log_level": "INFO",
    "retention_days": 365,
    "immutable_logs": true,
    "compliance": {
      "enabled": true,
      "standards": ["ISO27001", "SOC2", "GDPR"],
      "audit_frequency": "Daily"
    },
    "storage": {
      "account_name": "mcpprodstorage",
      "container_name": "audit-logs",
      "blob_prefix": "audit/production"
    }
  },
  
  "error_handling": {
    "enabled": true,
    "retry_policy": {
      "enabled": true,
      "max_retries": 3,
      "retry_delay": 1000,
      "backoff_factor": 2
    },
    "circuit_breaker": {
      "enabled": true,
      "failure_threshold": 5,
      "recovery_timeout": 60000
    },
    "alerting": {
      "enabled": true,
      "critical_errors": ["DONOR-001", "FABRIC-001"],
      "notification_channels": ["email", "teams", "pagerduty"]
    }
  },
  
  "feature_flags": {
    "new_features": {
      "enabled": false,
      "rollout_percentage": 0
    }
  }
}
```

### Production Environment Setup

```bash
# Create production resource group
az group create --name mcp-prod-rg --location eastus2

# Deploy production infrastructure with high availability
az deployment group create \
  --resource-group mcp-prod-rg \
  --template-file infrastructure/production.bicep \
  --parameters environment=production

# Configure production Key Vault with high security
az keyvault create --name mcp-prod-kv --resource-group mcp-prod-rg --location eastus2 \
  --sku premium \
  --enable-purge-protection true \
  --enable-soft-delete true \
  --soft-delete-retention-days 90

# Configure Key Vault access policies
az keyvault set-policy --name mcp-prod-kv \
  --object-id <production-service-principal> \
  --secret-permissions get list \
  --key-permissions get list \
  --certificate-permissions get list

# Deploy production Function App with Premium plan
az functionapp create \
  --name mcp-prod-func \
  --resource-group mcp-prod-rg \
  --plan mcp-prod-plan \
  --sku P2v2 \
  --min-instances 2 \
  --max-instances 10 \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --storage-account mcpprodstorage \
  --os-type Linux \
  --zone 1 2 3

# Configure Application Insights for production
az monitor app-insights create \
  --name mcp-prod-insights \
  --resource-group mcp-prod-rg \
  --location eastus2 \
  --application-type web \
  --workspace mcp-prod-log-analytics

# Configure auto-scale rules
az monitor autoscale create \
  --name mcp-prod-autoscale \
  --resource-group mcp-prod-rg \
  --target-resource "/subscriptions/production-subscription-id/resourceGroups/mcp-prod-rg/providers/Microsoft.Web/sites/mcp-prod-func" \
  --min-count 2 \
  --max-count 10 \
  --count 2

# Add scale rule for CPU
az monitor autoscale rule create \
  --autoscale-name mcp-prod-autoscale \
  --resource-group mcp-prod-rg \
  --condition "Percentage CPU > 70 avg 5m" \
  --scale out 1

# Add scale rule for memory
az monitor autoscale rule create \
  --autoscale-name mcp-prod-autoscale \
  --resource-group mcp-prod-rg \
  --condition "Memory Working Set > 80% avg 5m" \
  --scale out 1
```

### Production Data Setup

```bash
# Create production Fabric workspace
az fabric workspace create --name production-workspace --resource-group mcp-prod-rg

# Deploy production semantic models
az fabric semantic-model create \
  --workspace production-workspace \
  --name DonorManagementModel \
  --definition @models/donor-model.json

az fabric semantic-model create \
  --workspace production-workspace \
  --name FinancialMetricsModel \
  --definition @models/financial-model.json

# Configure data refresh schedules
az fabric data-pipeline create \
  --workspace production-workspace \
  --name DonorDataRefresh \
  --schedule "0 2 * * *" \
  --source @pipelines/donor-refresh.json

# Set up data caching
az fabric cache configure \
  --workspace production-workspace \
  --lakehouse ProductionLakehouse \
  --ttl 3600 \
  --enabled true
```

## 🔄 Environment Promotion

### Promotion Strategy

The MCP Platform Framework follows a structured promotion process:

```
Development → Test → Staging → Production
```

### Promotion Checklist

#### Development to Test
- [ ] ✅ All unit tests pass
- [ ] ✅ Code review completed
- [ ] ✅ Security scan passed
- [ ] ✅ Documentation updated
- [ ] ✅ Merge to main branch

#### Test to Staging
- [ ] ✅ All integration tests pass
- [ ] ✅ Performance tests pass
- [ ] ✅ Security tests pass
- [ ] ✅ Test data validated
- [ ] ✅ Approval from QA team

#### Staging to Production
- [ ] ✅ User acceptance testing (UAT) completed
- [ ] ✅ Performance testing with production-like data
- [ ] ✅ Security validation completed
- [ ] ✅ Backup and recovery tested
- [ ] ✅ Approval from business stakeholders
- [ ] ✅ Change management approval

### Automated Promotion with Azure DevOps

```yaml
# azure-pipelines/promote.yml
trigger: none

parameters:
- name: sourceEnvironment
  type: string
  default: test
- name: targetEnvironment
  type: string
  default: staging

stages:
- stage: Validate
  jobs:
  - job: ValidateSource
    steps:
    - script: echo "Validating source environment: ${{ parameters.sourceEnvironment }}"
    - task: AzureCLI@2
      inputs:
        azureSubscription: 'Azure-Service-Connection'
        scriptType: 'ps'
        scriptLocation: 'inlineScript'
        inlineScript: |
          az functionapp show --name mcp-${{ parameters.sourceEnvironment }}-func --resource-group mcp-${{ parameters.sourceEnvironment }}-rg

- stage: Deploy
  dependsOn: Validate
  jobs:
  - job: DeployToTarget
    steps:
    - script: echo "Deploying to target environment: ${{ parameters.targetEnvironment }}"
    - task: AzureCLI@2
      inputs:
        azureSubscription: 'Azure-Service-Connection'
        scriptType: 'bash'
        scriptLocation: 'inlineScript'
        inlineScript: |
          az deployment group create \
            --resource-group mcp-${{ parameters.targetEnvironment }}-rg \
            --template-file infrastructure/${{ parameters.targetEnvironment }}.bicep \
            --parameters environment=${{ parameters.targetEnvironment }}
```

### Manual Promotion with GitHub Actions

```yaml
# .github/workflows/promote.yml
name: Promote Environment

on:
  workflow_dispatch:
    inputs:
      source_environment:
        description: 'Source environment'
        required: true
        default: 'test'
      target_environment:
        description: 'Target environment'
        required: true
        default: 'staging'

jobs:
  promote:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Azure Login
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Validate Source Environment
      run: |
        az functionapp show --name mcp-${{ github.event.inputs.source_environment }}-func --resource-group mcp-${{ github.event.inputs.source_environment }}-rg
    
    - name: Deploy to Target Environment
      run: |
        az deployment group create \
          --resource-group mcp-${{ github.event.inputs.target_environment }}-rg \
          --template-file infrastructure/${{ github.event.inputs.target_environment }}.bicep \
          --parameters environment=${{ github.event.inputs.target_environment }}
```

## 📊 Environment Comparison

| Feature | Development | Test | Staging | Production |
|---------|-------------|------|---------|------------|
| **Debugging** | ✅ Full | ❌ Limited | ❌ Disabled | ❌ Disabled |
| **Logging Level** | DEBUG | INFO | INFO | WARNING |
| **Hot Reload** | ✅ Enabled | ❌ Disabled | ❌ Disabled | ❌ Disabled |
| **Authentication** | ⚠️ Optional | ✅ Required | ✅ Required | ✅ Required |
| **Audit Logging** | ❌ Disabled | ✅ Enabled | ✅ Enabled | ✅ Enabled |
| **Telemetry** | ✅ Console | ✅ App Insights | ✅ App Insights | ✅ App Insights |
| **Data Volume** | ⚠️ Test Data | ⚠️ Test Data | ⚠️ Subset | ✅ Full |
| **Scaling** | ❌ Single Instance | ⚠️ Limited | ⚠️ Auto-scale | ✅ Auto-scale |
| **High Availability** | ❌ No | ❌ No | ⚠️ Basic | ✅ Full |
| **Backup** | ❌ No | ❌ No | ⚠️ Daily | ✅ Daily + Geo |
| **Cost Optimization** | ✅ Local | ✅ Shared | ⚠️ Reduced | ❌ Production |

## 🛡️ Environment Security

### Security by Environment

#### Development
- **Access**: Individual developers
- **Authentication**: Local or Azure CLI
- **Network**: Local machine or VPN
- **Data**: Test data only
- **Secrets**: Local configuration or test Key Vault

#### Test
- **Access**: CI/CD pipelines, testers
- **Authentication**: Service principal
- **Network**: Private VNet or restricted access
- **Data**: Test data only
- **Secrets**: Test Key Vault

#### Staging
- **Access**: Limited users, stakeholders
- **Authentication**: Entra ID with MFA
- **Network**: Private VNet with NSG rules
- **Data**: Anonymized production data
- **Secrets**: Staging Key Vault with access controls

#### Production
- **Access**: Authorized users only
- **Authentication**: Entra ID with MFA, conditional access
- **Network**: Private VNet, firewalls, WAF
- **Data**: Production data with encryption
- **Secrets**: Production Key Vault with strict access controls

### Security Controls

```json
{
  "security": {
    "development": {
      "network": {
        "allow_local": true,
        "allow_vpn": true,
        "restrict_public": false
      },
      "authentication": {
        "require_mfa": false,
        "allow_mock": true
      }
    },
    "test": {
      "network": {
        "allow_local": false,
        "allow_vpn": true,
        "restrict_public": true
      },
      "authentication": {
        "require_mfa": false,
        "allow_mock": false
      }
    },
    "staging": {
      "network": {
        "allow_local": false,
        "allow_vpn": true,
        "restrict_public": true,
        "ip_restrictions": ["192.168.1.0/24", "10.0.0.0/8"]
      },
      "authentication": {
        "require_mfa": true,
        "allow_mock": false
      }
    },
    "production": {
      "network": {
        "allow_local": false,
        "allow_vpn": true,
        "restrict_public": true,
        "ip_restrictions": ["192.168.1.0/24"],
        "waf_enabled": true,
        "ddos_protection": true
      },
      "authentication": {
        "require_mfa": true,
        "allow_mock": false,
        "conditional_access": true
      },
      "encryption": {
        "at_rest": true,
        "in_transit": true,
        "key_rotation": true
      }
    }
  }
}
```

## 📈 Environment Monitoring

### Monitoring by Environment

#### Development
- **Metrics**: Basic function execution metrics
- **Logs**: Console output, debug logs
- **Alerts**: None (developer responsibility)
- **Retention**: 7 days

#### Test
- **Metrics**: Function execution, test results
- **Logs**: Structured logs, test output
- **Alerts**: Test failures, critical errors
- **Retention**: 30 days

#### Staging
- **Metrics**: Performance, usage, errors
- **Logs**: Structured logs, audit logs
- **Alerts**: Errors, performance issues, security events
- **Retention**: 90 days

#### Production
- **Metrics**: All metrics with high granularity
- **Logs**: Structured logs, audit logs, security logs
- **Alerts**: All critical events, performance, security, compliance
- **Retention**: 365 days (or as per compliance)

### Monitoring Configuration

```json
{
  "monitoring": {
    "development": {
      "metrics": {
        "enabled": true,
        "granularity": "1m",
        "retention": 7
      },
      "logs": {
        "enabled": true,
        "level": "DEBUG",
        "retention": 7
      },
      "alerts": {
        "enabled": false
      }
    },
    "test": {
      "metrics": {
        "enabled": true,
        "granularity": "5m",
        "retention": 30
      },
      "logs": {
        "enabled": true,
        "level": "INFO",
        "retention": 30
      },
      "alerts": {
        "enabled": true,
        "critical_only": true
      }
    },
    "staging": {
      "metrics": {
        "enabled": true,
        "granularity": "1m",
        "retention": 90
      },
      "logs": {
        "enabled": true,
        "level": "INFO",
        "retention": 90
      },
      "alerts": {
        "enabled": true,
        "level": "WARNING"
      }
    },
    "production": {
      "metrics": {
        "enabled": true,
        "granularity": "1m",
        "retention": 365
      },
      "logs": {
        "enabled": true,
        "level": "WARNING",
        "retention": 365
      },
      "alerts": {
        "enabled": true,
        "level": "ERROR"
      }
    }
  }
}
```

## 💰 Cost Optimization

### Cost by Environment

| Resource | Development | Test | Staging | Production |
|----------|-------------|------|---------|------------|
| **Function App** | Local (Free) | Consumption ($) | Premium ($$) | Premium ($$$) |
| **Storage** | Local (Free) | Standard ($) | Standard ($$) | Premium ($$$) |
| **Key Vault** | Local (Free) | Standard ($) | Standard ($) | Premium ($$) |
| **Application Insights** | Local (Free) | Basic ($) | Standard ($$) | Premium ($$$) |
| **Fabric** | Local (Free) | Test ($) | Development ($$) | Production ($$$) |
| **Network** | Local (Free) | Shared ($) | Private ($$) | Private + WAF ($$$) |

### Cost Optimization Strategies

#### Development
- ✅ Use local development tools (Storage Emulator, Functions Core Tools)
- ✅ Use free tier Azure resources where possible
- ✅ Share development resources among team members
- ✅ Clean up unused resources regularly

#### Test
- ✅ Use consumption-based Function App (pay per execution)
- ✅ Share test resources across multiple projects
- ✅ Use test data instead of production data
- ✅ Schedule test environments to run only during business hours

#### Staging
- ✅ Use smaller instance sizes (B1, P1v2)
- ✅ Limit auto-scaling (min: 1, max: 3)
- ✅ Use reduced data volume
- ✅ Schedule staging environments to run only when needed

#### Production
- ✅ Use auto-scaling to match demand
- ✅ Implement caching to reduce compute costs
- ✅ Use reserved instances for predictable workloads
- ✅ Monitor and optimize resource usage regularly

## 🛠️ Troubleshooting

### Common Environment Issues

#### Environment Configuration Not Found

**Error**: `Configuration for environment 'staging' not found`

**Solution**:
```bash
# Check if the configuration file exists
ls -la config/staging.json

# Create the missing configuration file
cp config/production.json config/staging.json

# Or specify a different environment
MCP_ENVIRONMENT=production python your_app.py
```

#### Environment Mismatch

**Error**: `Environment mismatch: expected 'production' but got 'staging'`

**Solution**:
```bash
# Check the current environment
MCP_ENVIRONMENT=staging python -c "from mcp_framework.config import Config; print(Config().get_environment())"

# Ensure consistent environment across all components
export MCP_ENVIRONMENT=staging
export AZURE_ENVIRONMENT=staging
```

#### Resource Not Found in Environment

**Error**: `Resource 'mcp-staging-kv' not found in subscription`

**Solution**:
```bash
# Check available resources in the subscription
az resource list --resource-group mcp-staging-rg

# Create the missing resource
az keyvault create --name mcp-staging-kv --resource-group mcp-staging-rg --location eastus
```

#### Permission Denied in Environment

**Error**: `Insufficient permissions to access resource in staging`

**Solution**:
```bash
# Check your permissions
az role assignment list --assignee your-email@domain.com --resource-group mcp-staging-rg

# Grant necessary permissions
az role assignment create \
  --assignee your-email@domain.com \
  --role "Contributor" \
  --resource-group mcp-staging-rg
```

## 📚 Next Steps

- **[Deployment Overview](overview.md)** - Understand the deployment process
- **[Azure DevOps](azure-devops.md)** - Set up CI/CD with Azure DevOps
- **[GitHub Actions](github-actions.md)** - Set up CI/CD with GitHub Actions
- **[Function App Deployment](function-app.md)** - Deploy to Azure Function App

## 🔗 Related Documentation

- [Configuration Guide](../getting-started/configuration.md)
- [Azure Environment Documentation](https://docs.microsoft.com/en-us/azure/)
- [Microsoft Fabric Environments](https://learn.microsoft.com/en-us/fabric/)

---

**Need help?** Check the [FAQ](../FAQ.md) or open an issue in the repository.
