# ⚙️ Configuration Guide

## Overview

This guide covers all configuration aspects of the MCP Platform Framework, from local development settings to production deployment configurations for Azure and Microsoft Fabric environments.

## 📁 Configuration Structure

The MCP Platform Framework uses a hierarchical configuration system with the following priority order (highest to lowest):

1. **Environment Variables** - Runtime environment overrides
2. **Key Vault Secrets** - Secure configuration from Azure Key Vault
3. **Configuration Files** - JSON/YAML files in the `config/` directory
4. **Default Values** - Built-in framework defaults

```
config/
├── default.json          # Default configuration
├── development.json      # Development environment
├── test.json             # Test environment
├── staging.json          # Staging environment
└── production.json       # Production environment
```

## 🌐 Environment Configuration

### Environment Detection

The framework automatically detects the environment based on:

1. **Environment Variable**: `MCP_ENVIRONMENT` or `AZURE_ENVIRONMENT`
2. **Azure Function App Settings**: When deployed to Azure
3. **Default**: `development` if not specified

```python
# Environment detection logic
import os

environment = os.getenv('MCP_ENVIRONMENT', 'development')
```

### Environment-Specific Files

Create environment-specific configuration files:

**config/development.json**
```json
{
  "environment": "development",
  "debug": true,
  "log_level": "DEBUG",
  "azure": {
    "subscription_id": "dev-subscription-id",
    "resource_group": "mcp-dev-rg",
    "location": "eastus"
  },
  "fabric": {
    "tenant_id": "dev-tenant-id",
    "workspace_id": "dev-workspace-id"
  }
}
```

**config/production.json**
```json
{
  "environment": "production",
  "debug": false,
  "log_level": "INFO",
  "azure": {
    "subscription_id": "prod-subscription-id",
    "resource_group": "mcp-prod-rg",
    "location": "eastus2"
  },
  "fabric": {
    "tenant_id": "prod-tenant-id",
    "workspace_id": "prod-workspace-id"
  }
}
```

## 🔐 Azure Configuration

### Azure Authentication

The framework supports multiple authentication methods:

#### 1. DefaultAzureCredential (Recommended)

```python
from azure.identity import DefaultAzureCredential

# Automatically tries multiple authentication methods
credential = DefaultAzureCredential()
```

**Authentication Chain:**
1. Environment variables (`AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID`)
2. Managed Identity (when running in Azure)
3. Visual Studio Code authentication
4. Azure CLI authentication
5. Interactive browser authentication

#### 2. Service Principal

```python
from azure.identity import ClientSecretCredential

credential = ClientSecretCredential(
    tenant_id=os.getenv('AZURE_TENANT_ID'),
    client_id=os.getenv('AZURE_CLIENT_ID'),
    client_secret=os.getenv('AZURE_CLIENT_SECRET')
)
```

#### 3. Managed Identity

```python
from azure.identity import ManagedIdentityCredential

# System-assigned identity
credential = ManagedIdentityCredential()

# User-assigned identity
credential = ManagedIdentityCredential(client_id=os.getenv('AZURE_CLIENT_ID'))
```

### Azure Resource Configuration

**Required Environment Variables:**

```bash
# Azure Subscription
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=mcp-platform-rg
AZURE_LOCATION=eastus

# Azure Key Vault
KEY_VAULT_NAME=mcp-platform-kv
KEY_VAULT_URI=https://mcp-platform-kv.vault.azure.net/

# Azure Function App
FUNCTION_APP_NAME=mcp-platform-func
FUNCTION_APP_STORAGE=mcpplatformstorage

# Application Insights
APP_INSIGHTS_NAME=mcp-platform-insights
APP_INSIGHTS_CONNECTION_STRING=InstrumentationKey=...
```

### Azure Key Vault Integration

The framework automatically integrates with Azure Key Vault for secrets management.

```python
from mcp_framework.config import Config

# Access configuration
config = Config()

# Get a secret from Key Vault
secret_value = config.get_secret("my-secret-name")

# Get configuration value (tries Key Vault first, then config files)
db_connection = config.get("database.connection_string")
```

**Key Vault Configuration:**

```bash
# Create Key Vault
az keyvault create --name mcp-platform-kv --resource-group mcp-platform-rg --location eastus

# Add secrets
az keyvault secret set --vault-name mcp-platform-kv --name database-connection --value "your-connection-string"

# Grant access to Function App
az keyvault set-policy --name mcp-platform-kv --object-id <function-app-identity> --secret-permissions get list
```

## 🏭 Microsoft Fabric Configuration

### Fabric Authentication

```python
from mcp_framework.fabric import FabricClient

# Initialize Fabric client
fabric_client = FabricClient(
    tenant_id=os.getenv('FABRIC_TENANT_ID'),
    workspace_id=os.getenv('FABRIC_WORKSPACE_ID')
)
```

**Required Environment Variables:**

```bash
# Fabric Configuration
FABRIC_TENANT_ID=your-fabric-tenant-id
FABRIC_WORKSPACE_ID=your-workspace-id
FABRIC_ENDPOINT=https://api.fabric.microsoft.com

# Service Principal for Fabric (if not using DefaultAzureCredential)
FABRIC_CLIENT_ID=your-client-id
FABRIC_CLIENT_SECRET=your-client-secret
```

### Semantic Model Configuration

```python
from mcp_framework.fabric import SemanticModelClient

# Configure semantic model access
semantic_client = SemanticModelClient(
    workspace_id=os.getenv('FABRIC_WORKSPACE_ID'),
    model_id="DonorManagementModel"
)

# Execute query against semantic model
results = semantic_client.execute(
    "EVALUATE SUMMARIZE('DonorTable')"
)
```

**Configuration in config files:**

```json
{
  "fabric": {
    "tenant_id": "your-tenant-id",
    "workspace_id": "your-workspace-id",
    "semantic_models": {
      "DonorManagement": {
        "model_id": "DonorManagementModel",
        "classification": "CONFIDENTIAL"
      },
      "FinancialMetrics": {
        "model_id": "FinancialMetricsModel",
        "classification": "INTERNAL"
      }
    }
  }
}
```

### Warehouse and Lakehouse Configuration

```python
from mcp_framework.fabric import WarehouseClient, LakehouseClient

# Warehouse configuration
warehouse_client = WarehouseClient(
    workspace_id=os.getenv('FABRIC_WORKSPACE_ID'),
    warehouse_id="DataWarehouse"
)

# Lakehouse configuration
lakehouse_client = LakehouseClient(
    workspace_id=os.getenv('FABRIC_WORKSPACE_ID'),
    lakehouse_id="DataLakehouse"
)
```

## 🛡️ Security Configuration

### Data Classification

Configure data classification levels for your domain:

```json
{
  "classification": {
    "default": "INTERNAL",
    "tools": {
      "GetDonorPipeline": "CONFIDENTIAL",
      "GetFinancialReports": "STRICTLY_CONFIDENTIAL",
      "GetPublicMetrics": "PUBLIC"
    },
    "semantic_models": {
      "DonorManagement": "CONFIDENTIAL",
      "PublicReports": "PUBLIC"
    }
  }
}
```

### Authentication Configuration

```json
{
  "authentication": {
    "enabled": true,
    "providers": ["entra_id", "managed_identity"],
    "require_authentication": true,
    "allowed_audiences": ["api://mcp-platform"],
    "token_validation": {
      "issuer": "https://login.microsoftonline.com/{tenant}/v2.0",
      "audience": "api://mcp-platform",
      "lifetime": 3600
    }
  }
}
```

### Authorization Configuration

```json
{
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
        }
      ]
    }
  }
}
```

## 📊 Telemetry Configuration

### Application Insights

```json
{
  "telemetry": {
    "enabled": true,
    "provider": "application_insights",
    "application_insights": {
      "connection_string": "InstrumentationKey=...",
      "tracking_level": "INFO",
      "sample_rate": 100,
      "disable_telemetry": false
    },
    "custom_dimensions": {
      "domain": "DonorManagement",
      "environment": "development",
      "version": "1.0.0"
    },
    "tool_tracking": {
      "enabled": true,
      "track_parameters": true,
      "track_duration": true,
      "track_status": true,
      "track_errors": true
    }
  }
}
```

### Custom Metrics

```python
from mcp_framework.telemetry import TelemetryClient

telemetry = TelemetryClient()

# Track custom metrics
telemetry.track_metric("tool.execution.time", 450, {"tool": "GetDonorPipeline"})
telemetry.track_metric("data.rows.returned", 150, {"model": "DonorManagement"})

# Track custom events
telemetry.track_event("HighValueDonorAccess", {"donor_id": "D12345", "value": 1000000})
```

## 📝 Audit Logging Configuration

```json
{
  "audit": {
    "enabled": true,
    "provider": "azure_monitor",
    "log_level": "INFO",
    "sensitive_actions": [
      "donor.read",
      "finance.write",
      "forecast.generate",
      "report.export"
    ],
    "retention_days": 365,
    "storage": {
      "account_name": "mcpplatformstorage",
      "container_name": "audit-logs",
      "blob_prefix": "audit"
    },
    "compliance": {
      "enabled": true,
      "standards": ["ISO27001", "SOC2"],
      "immutable_logs": true
    }
  }
}
```

## 🔄 Error Handling Configuration

```json
{
  "error_handling": {
    "enabled": true,
    "error_codes": {
      "DONOR-001": {
        "category": "DataAccess",
        "message": "Access denied to donor data",
        "severity": "HIGH",
        "http_status": 403
      },
      "DONOR-002": {
        "category": "DataNotFound",
        "message": "Donor not found",
        "severity": "MEDIUM",
        "http_status": 404
      },
      "FABRIC-001": {
        "category": "ConnectionError",
        "message": "Fabric connection failed",
        "severity": "HIGH",
        "http_status": 503
      }
    },
    "retry_policy": {
      "enabled": true,
      "max_retries": 3,
      "retry_delay": 1000,
      "backoff_factor": 2,
      "retryable_errors": ["ConnectionError", "TimeoutError", "RateLimitError"]
    },
    "circuit_breaker": {
      "enabled": true,
      "failure_threshold": 5,
      "recovery_timeout": 30000,
      "half_open_after": 60000
    }
  }
}
```

## 🏗️ Tool Registration Configuration

```json
{
  "tool_registration": {
    "enabled": true,
    "auto_discovery": true,
    "discovery_paths": ["tools", "src/tools"],
    "metadata_extraction": {
      "enabled": true,
      "extract_from_docstring": true,
      "extract_from_type_hints": true,
      "extract_from_decorators": true
    },
    "catalog_integration": {
      "enabled": true,
      "catalog_name": "MCP Platform Catalog",
      "auto_register": true,
      "metadata": {
        "owner": "DER",
        "domain": "DonorManagement",
        "sla": "Gold",
        "classification": "Confidential"
      }
    }
  }
}
```

## 📦 Deployment Configuration

### Function App Configuration

**local.settings.json** (for local development):
```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "FUNCTIONS_EXTENSION_VERSION": "~4",
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "APPINSIGHTS_INSTRUMENTATIONKEY": "your-instrumentation-key",
    "MCP_ENVIRONMENT": "development",
    "AZURE_SUBSCRIPTION_ID": "your-subscription-id",
    "AZURE_RESOURCE_GROUP": "mcp-dev-rg",
    "KEY_VAULT_NAME": "mcp-dev-kv",
    "FABRIC_TENANT_ID": "your-fabric-tenant-id",
    "FABRIC_WORKSPACE_ID": "your-workspace-id"
  }
}
```

### Production Configuration

For production deployments, configure these application settings in your Function App:

| Setting | Value | Description |
|---------|-------|-------------|
| `FUNCTIONS_WORKER_RUNTIME` | `python` | Python runtime |
| `FUNCTIONS_EXTENSION_VERSION` | `~4` | Functions extension version |
| `AzureWebJobsStorage` | `<storage-connection-string>` | Storage account connection |
| `APPINSIGHTS_INSTRUMENTATIONKEY` | `<instrumentation-key>` | Application Insights key |
| `MCP_ENVIRONMENT` | `production` | Environment name |
| `AZURE_SUBSCRIPTION_ID` | `<subscription-id>` | Azure subscription ID |
| `AZURE_RESOURCE_GROUP` | `<resource-group>` | Resource group name |
| `KEY_VAULT_URI` | `<key-vault-uri>` | Key Vault URI |
| `FABRIC_TENANT_ID` | `<fabric-tenant-id>` | Fabric tenant ID |
| `FABRIC_WORKSPACE_ID` | `<workspace-id>` | Fabric workspace ID |

## 🧪 Testing Configuration

```json
{
  "testing": {
    "unit_tests": {
      "enabled": true,
      "coverage": {
        "enabled": true,
        "minimum_coverage": 80,
        "exclude": ["tests/*", "venv/*"]
      },
      "mocking": {
        "azure": true,
        "fabric": true,
        "authentication": true
      }
    },
    "integration_tests": {
      "enabled": true,
      "test_environment": "test",
      "test_data": {
        "fabric_workspace": "test-workspace",
        "semantic_models": ["TestDonorModel", "TestFinancialModel"]
      }
    },
    "performance_tests": {
      "enabled": true,
      "load_testing": {
        "concurrent_users": 100,
        "duration": "5m",
        "ramp_up": "1m"
      },
      "thresholds": {
        "response_time": 500,
        "error_rate": 0.01,
        "throughput": 100
      }
    },
    "security_tests": {
      "enabled": true,
      "dependency_scanning": true,
      "secret_detection": true,
      "vulnerability_assessment": true
    }
  }
}
```

## 📁 Configuration Management Best Practices

### 1. Environment Separation

⭐ **Best Practice**: Always use separate configuration files for each environment.

```
config/
├── default.json          # Shared defaults
├── development.json      # Development overrides
├── test.json             # Test environment
├── staging.json          # Staging environment
└── production.json       # Production environment
```

### 2. Secrets Management

⭐ **Best Practice**: Never store secrets in configuration files or code.

✅ **Do:**
- Use Azure Key Vault for all secrets
- Use Managed Identity for authentication
- Use environment variables for non-sensitive configuration

❌ **Don't:**
- Commit secrets to version control
- Hardcode secrets in source code
- Store secrets in configuration files

### 3. Configuration Validation

⭐ **Best Practice**: Validate configuration on startup.

```python
from mcp_framework.config import Config
from pydantic import BaseModel, ValidationError

class AppConfig(BaseModel):
    azure_subscription_id: str
    azure_resource_group: str
    fabric_tenant_id: str
    fabric_workspace_id: str
    environment: str

try:
    config = Config()
    app_config = AppConfig(**config.dict())
    print("✅ Configuration validated successfully")
except ValidationError as e:
    print(f"❌ Configuration validation failed: {e}")
    raise
```

### 4. Configuration Changes

⭐ **Best Practice**: Use feature flags for gradual rollouts.

```json
{
  "feature_flags": {
    "new_donor_api": {
      "enabled": false,
      "rollout_percentage": 0,
      "enabled_for": ["user1@domain.com", "user2@domain.com"]
    },
    "enhanced_analytics": {
      "enabled": true,
      "rollout_percentage": 100
    }
  }
}
```

## 🛠️ Configuration Utilities

### Configuration Helper Functions

```python
from mcp_framework.config import Config

config = Config()

# Get configuration value with fallback
value = config.get("my.setting", default="default-value")

# Get required configuration value
required_value = config.get_required("my.required.setting")

# Get secret from Key Vault
secret = config.get_secret("my-secret-name")

# Check if setting exists
if config.has("optional.setting"):
    value = config.get("optional.setting")

# Get environment
environment = config.get_environment()
```

### Environment Variable Utilities

```python
import os
from mcp_framework.utils import get_env, get_env_required

# Get environment variable with default
value = get_env("MY_VARIABLE", default="default")

# Get required environment variable
required_value = get_env_required("REQUIRED_VARIABLE")

# Get boolean environment variable
debug_mode = get_env("DEBUG", default=False, type=bool)

# Get integer environment variable
port = get_env("PORT", default=8080, type=int)
```

## 🔄 Configuration Reloading

The framework supports hot-reloading of configuration in development:

```python
from mcp_framework.config import Config

config = Config()

# Reload configuration from files
config.reload()

# Watch for configuration changes (development only)
config.watch_for_changes()
```

## 🛡️ Security Considerations

### Configuration Security

- 🔒 **Encrypt sensitive configuration**: Use Azure Key Vault for all secrets
- 🔒 **Restrict access**: Use RBAC to control access to configuration
- 🔒 **Audit changes**: Enable audit logging for configuration changes
- 🔒 **Validate inputs**: Always validate configuration values
- 🔒 **Use HTTPS**: Always use HTTPS for configuration endpoints

### Configuration Encryption

For additional security, encrypt sensitive configuration files:

```bash
# Encrypt configuration file (Linux/macOS)
openssl enc -aes-256-cbc -salt -in config/production.json -out config/production.json.enc

# Decrypt configuration file
openssl enc -d -aes-256-cbc -in config/production.json.enc -out config/production.json
```

## ⚡ Performance Tips

### Configuration Caching

⭐ **Best Practice**: Cache configuration values that are accessed frequently.

```python
from mcp_framework.config import Config
from functools import lru_cache

config = Config()

@lru_cache(maxsize=128)
def get_cached_config(key: str, default=None):
    return config.get(key, default=default)
```

### Lazy Loading

⭐ **Best Practice**: Load configuration lazily to improve startup time.

```python
from mcp_framework.config import Config

class LazyConfig:
    def __init__(self):
        self._config = None
        self._loaded = False
    
    def _load_config(self):
        if not self._loaded:
            self._config = Config()
            self._loaded = True
        return self._config
    
    def get(self, key, default=None):
        return self._load_config().get(key, default)

# Usage
lazy_config = LazyConfig()
value = lazy_config.get("my.setting")
```

## 🛠️ Troubleshooting

### Common Configuration Issues

#### Configuration File Not Found

**Error**: `Configuration file not found: config/development.json`

**Solution**:
```bash
# Create the missing configuration file
mkdir -p config
touch config/development.json

# Or specify a different environment
MCP_ENVIRONMENT=production python your_app.py
```

#### Invalid Configuration Format

**Error**: `Invalid JSON in configuration file`

**Solution**: Validate your JSON files:
```bash
# Use jq to validate JSON
jq empty config/development.json

# Or use Python
python -c "import json; json.load(open('config/development.json'))"
```

#### Missing Required Configuration

**Error**: `Required configuration 'azure.subscription_id' not found`

**Solution**:
```bash
# Set the missing environment variable
export AZURE_SUBSCRIPTION_ID=your-subscription-id

# Or add it to your configuration file
{
  "azure": {
    "subscription_id": "your-subscription-id"
  }
}
```

#### Key Vault Access Denied

**Error**: `Access denied to Key Vault`

**Solution**:
```bash
# Grant access to the Key Vault
az keyvault set-policy --name mcp-platform-kv \
    --object-id <your-object-id> \
    --secret-permissions get list

# Or use Managed Identity
az keyvault set-policy --name mcp-platform-kv \
    --spn <function-app-identity> \
    --secret-permissions get list
```

## 📚 Next Steps

After configuring your environment:

1. **[Quick Start](quick-start.md)** - Get started with basic MCP tool development
2. **[Deployment Overview](../deployment/overview.md)** - Deploy your MCP server
3. **[Tool Development](../examples/tool-development.md)** - Create your first MCP tools

## 🔗 Related Documentation

- [Installation Guide](installation.md)
- [Prerequisites](prerequisites.md)
- [Deployment Overview](../deployment/overview.md)
- [Azure Configuration](https://docs.microsoft.com/en-us/azure/)
- [Microsoft Fabric Configuration](https://learn.microsoft.com/en-us/fabric/)

---

**Need help?** Check the [FAQ](../FAQ.md) or open an issue in the repository.
