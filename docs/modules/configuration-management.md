# 📁 Configuration Management Module

The Configuration Management Module provides environment-aware configuration management with Azure Key Vault integration for the MCP Platform Framework, ensuring that all configuration is externalized, secure, and properly managed across different environments.

## 🎯 Overview

The Configuration Management Module handles:
- **Environment-Aware Configuration**: Separate configurations for DEV, TEST, PROD
- **Azure Key Vault Integration**: Standardized secret retrieval through Key Vault
- **Configuration Validation**: Schema validation and required field checking
- **Secret Management**: No credentials in code, developers cannot access secrets directly

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│      Configuration Management Module      │
├─────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Environment     │  │ Key Vault       │ │
│  │ Configuration   │  │ Integration     │ │
│  └─────────────────┘  └─────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Validation      │  │ Secret          │ │
│  │                 │  │ Management      │ │
│  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────┘
```

## 🚀 Quick Start

### Basic Usage

```python
from platform.config import config, keyvault

# Access configuration
environment = config.environment  # "Dev", "Test", or "Production"
domain = config.domain  # "DonorManagement"

# Retrieve secrets from Key Vault
fabric_credentials = keyvault.get_secret("fabric-credentials")
database_password = keyvault.get_secret("db-password")
```

### Configuration

```python
# config/configuration.py
from platform.config import Configuration, EnvironmentConfig

# Define configuration for each environment
CONFIG = Configuration(
    default_environment="Dev",
    environments={
        "Dev": EnvironmentConfig(
            domain="DonorManagement",
            environment="Dev",
            fabric_endpoint="https://dev-fabric.unhcr.org",
            azure_key_vault="dev-kv-unhcr",
            azure_function_app="dev-mcp-donor",
            logging_level="DEBUG",
            telemetry_enabled=True
        ),
        "Test": EnvironmentConfig(
            domain="DonorManagement",
            environment="Test",
            fabric_endpoint="https://test-fabric.unhcr.org",
            azure_key_vault="test-kv-unhcr",
            azure_function_app="test-mcp-donor",
            logging_level="INFO",
            telemetry_enabled=True
        ),
        "Production": EnvironmentConfig(
            domain="DonorManagement",
            environment="Production",
            fabric_endpoint="https://fabric.unhcr.org",
            azure_key_vault="prod-kv-unhcr",
            azure_function_app="mcp-donor",
            logging_level="WARNING",
            telemetry_enabled=True
        )
    }
)
```

## 🔧 Configuration

### Environment Variables

```bash
# Environment Configuration
ENVIRONMENT=Dev  # or Test, Production
DOMAIN=DonorManagement

# Azure Configuration
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_KEY_VAULT=your-key-vault-name

# Fabric Configuration
FABRIC_ENDPOINT=https://dev-fabric.unhcr.org

# Logging Configuration
LOGGING_LEVEL=DEBUG
LOGGING_TELEMETRY_ENABLED=true

# Feature Flags
FEATURE_NEW_DASHBOARD=false
FEATURE_ADVANCED_ANALYTICS=true
```

### Configuration File

```yaml
# config/config.yaml
configuration:
  default_environment: Dev
  
  environments:
    Dev:
      domain: DonorManagement
      environment: Dev
      
      fabric:
        endpoint: "https://dev-fabric.unhcr.org"
        semantic_models:
          - DonorManagement
          - Finance
        
      azure:
        tenant_id: ${AZURE_TENANT_ID}
        client_id: ${AZURE_CLIENT_ID}
        key_vault: ${AZURE_KEY_VAULT}
        function_app: "dev-mcp-donor"
        
      logging:
        level: DEBUG
        telemetry: true
        
      features:
        new_dashboard: false
        advanced_analytics: true
        
    Test:
      domain: DonorManagement
      environment: Test
      
      fabric:
        endpoint: "https://test-fabric.unhcr.org"
        semantic_models:
          - DonorManagement
          - Finance
        
      azure:
        tenant_id: ${AZURE_TENANT_ID}
        client_id: ${AZURE_CLIENT_ID}
        key_vault: "test-kv-unhcr"
        function_app: "test-mcp-donor"
        
      logging:
        level: INFO
        telemetry: true
        
      features:
        new_dashboard: true
        advanced_analytics: true
        
    Production:
      domain: DonorManagement
      environment: Production
      
      fabric:
        endpoint: "https://fabric.unhcr.org"
        semantic_models:
          - DonorManagement
          - Finance
        
      azure:
        tenant_id: ${AZURE_TENANT_ID}
        client_id: ${AZURE_CLIENT_ID}
        key_vault: "prod-kv-unhcr"
        function_app: "mcp-donor"
        
      logging:
        level: WARNING
        telemetry: true
        
      features:
        new_dashboard: true
        advanced_analytics: true
```

## 🎯 API Reference

### Functions

#### `get_config()`

Gets the current configuration.

```python
from platform.config import get_config

config = get_config()
print(f"Environment: {config.environment}")
print(f"Domain: {config.domain}")
print(f"Fabric endpoint: {config.fabric.endpoint}")
```

**Returns:**
- `Configuration`: The current configuration object

#### `get_environment_config(environment=None)`

Gets the configuration for a specific environment.

```python
from platform.config import get_environment_config

# Get current environment config
current_config = get_environment_config()

# Get specific environment config
dev_config = get_environment_config("Dev")
test_config = get_environment_config("Test")
```

**Parameters:**
- `environment` (str, optional): Environment name (defaults to current environment)

**Returns:**
- `EnvironmentConfig`: The environment configuration

#### `get_secret(secret_name, version=None)`

Retrieves a secret from Azure Key Vault.

```python
from platform.config import keyvault

# Get current secret
fabric_credentials = keyvault.get_secret("fabric-credentials")

# Get specific version of secret
old_credentials = keyvault.get_secret("fabric-credentials", version="v1")
```

**Parameters:**
- `secret_name` (str): Name of the secret
- `version` (str, optional): Version of the secret

**Returns:**
- `str`: The secret value

**Raises:**
- `SecretNotFoundError`: If the secret is not found
- `KeyVaultError`: If there's an error accessing Key Vault

#### `get_connection_string(name)`

Gets a connection string from configuration or Key Vault.

```python
from platform.config import get_connection_string

# Get connection string from config
fabric_connection = get_connection_string("fabric")

# Get connection string from Key Vault
storage_connection = get_connection_string("storage-account")
```

**Parameters:**
- `name` (str): Name of the connection string

**Returns:**
- `str`: The connection string

#### `get_feature_flag(name, default=None)`

Gets a feature flag value.

```python
from platform.config import get_feature_flag

# Get feature flag
new_dashboard_enabled = get_feature_flag("new_dashboard")

# Get with default
analytics_enabled = get_feature_flag("analytics_enabled", default=True)
```

**Parameters:**
- `name` (str): Feature flag name
- `default` (any, optional): Default value if flag not found

**Returns:**
- The feature flag value

### Classes

#### `Configuration`

Main configuration class.

```python
from platform.config import Configuration, EnvironmentConfig

# Create configuration
config = Configuration(
    default_environment="Dev",
    environments={
        "Dev": EnvironmentConfig(
            domain="DonorManagement",
            environment="Dev",
            fabric_endpoint="https://dev-fabric.unhcr.org"
        ),
        "Test": EnvironmentConfig(
            domain="DonorManagement",
            environment="Test",
            fabric_endpoint="https://test-fabric.unhcr.org"
        ),
        "Production": EnvironmentConfig(
            domain="DonorManagement",
            environment="Production",
            fabric_endpoint="https://fabric.unhcr.org"
        )
    }
)

# Access current environment
current_env = config.get_current_environment()

# Access specific environment
dev_env = config.get_environment("Dev")

# Check if environment exists
if config.has_environment("Staging"):
    staging_env = config.get_environment("Staging")
```

**Parameters:**
- `default_environment` (str): Default environment name
- `environments` (dict): Dictionary of environment configurations
- `environment_variable` (str, optional): Environment variable name for environment (default: "ENVIRONMENT")

**Methods:**
- `get_current_environment()`: Get current environment configuration
- `get_environment(name)`: Get specific environment configuration
- `has_environment(name)`: Check if environment exists
- `get_all_environments()`: Get all environment configurations
- `set_environment(name)`: Set the current environment
- `validate()`: Validate configuration

#### `EnvironmentConfig`

Environment-specific configuration.

```python
from platform.config import EnvironmentConfig

# Create environment configuration
env_config = EnvironmentConfig(
    domain="DonorManagement",
    environment="Dev",
    
    # Fabric configuration
    fabric=FabricConfig(
        endpoint="https://dev-fabric.unhcr.org",
        semantic_models=["DonorManagement", "Finance"]
    ),
    
    # Azure configuration
    azure=AzureConfig(
        tenant_id="your-tenant-id",
        client_id="your-client-id",
        key_vault="dev-kv-unhcr",
        function_app="dev-mcp-donor"
    ),
    
    # Logging configuration
    logging=LoggingConfig(
        level="DEBUG",
        telemetry=True,
        application_insights_enabled=True
    ),
    
    # Feature flags
    features={
        "new_dashboard": False,
        "advanced_analytics": True
    }
)

# Access configuration values
print(f"Domain: {env_config.domain}")
print(f"Environment: {env_config.environment}")
print(f"Fabric endpoint: {env_config.fabric.endpoint}")
print(f"Key Vault: {env_config.azure.key_vault}")
print(f"Logging level: {env_config.logging.level}")
print(f"New dashboard enabled: {env_config.features.new_dashboard}")
```

**Attributes:**
- `domain` (str): Domain name
- `environment` (str): Environment name
- `fabric` (FabricConfig): Fabric configuration
- `azure` (AzureConfig): Azure configuration
- `logging` (LoggingConfig): Logging configuration
- `features` (dict): Feature flags
- `custom` (dict): Custom configuration values

#### `KeyVaultClient`

Client for Azure Key Vault integration.

```python
from platform.config import KeyVaultClient

# Create Key Vault client
keyvault = KeyVaultClient(
    vault_url="https://dev-kv-unhcr.vault.azure.net",
    tenant_id="your-tenant-id",
    client_id="your-client-id"
)

# Get secret
secret_value = keyvault.get_secret("fabric-credentials")

# Get secret with version
secret_value = keyvault.get_secret("fabric-credentials", version="v1")

# Get key
key = keyvault.get_key("encryption-key")

# Get certificate
certificate = keyvault.get_certificate("ssl-certificate")

# List secrets
secrets = keyvault.list_secrets()

# Check if secret exists
if keyvault.secret_exists("fabric-credentials"):
    print("Secret exists")
```

**Parameters:**
- `vault_url` (str): Key Vault URL
- `tenant_id` (str): Azure tenant ID
- `client_id` (str): Azure client ID
- `client_secret` (str, optional): Azure client secret
- `use_managed_identity` (bool, optional): Use Managed Identity

**Methods:**
- `get_secret(name, version=None)`: Get a secret
- `get_key(name, version=None)`: Get a key
- `get_certificate(name, version=None)`: Get a certificate
- `list_secrets()`: List all secrets
- `list_keys()`: List all keys
- `list_certificates()`: List all certificates
- `secret_exists(name)`: Check if secret exists
- `create_secret(name, value)`: Create a new secret
- `update_secret(name, value)`: Update a secret
- `delete_secret(name)`: Delete a secret

#### `ConfigValidator`

Validates configuration.

```python
from platform.config import ConfigValidator, Configuration

# Create validator
validator = ConfigValidator()

# Validate configuration
config = Configuration(...)
errors = validator.validate(config)

if errors:
    print(f"Configuration errors: {errors}")
else:
    print("Configuration is valid")

# Validate with schema
schema = {
    "required": ["domain", "environment", "fabric.endpoint"],
    "properties": {
        "domain": {"type": "string", "minLength": 1},
        "environment": {"type": "string", "enum": ["Dev", "Test", "Production"]},
        "fabric": {
            "type": "object",
            "required": ["endpoint"],
            "properties": {
                "endpoint": {"type": "string", "format": "uri"}
            }
        }
    }
}

errors = validator.validate_with_schema(config, schema)
```

**Methods:**
- `validate(config)`: Validate configuration with default schema
- `validate_with_schema(config, schema)`: Validate configuration with custom schema
- `validate_environment(env_config)`: Validate environment configuration
- `get_validation_errors(config)`: Get detailed validation errors

## 📊 Configuration Structure

### Standard Configuration Format

```json
{
  "domain": "DonorManagement",
  "environment": "Dev",
  "fabric": {
    "endpoint": "https://dev-fabric.unhcr.org",
    "semantic_models": ["DonorManagement", "Finance"],
    "warehouses": ["GoldLayer", "SilverLayer"],
    "lakehouses": ["Gold"],
    "timeout": 60,
    "max_retries": 3
  },
  "azure": {
    "tenant_id": "your-tenant-id",
    "client_id": "your-client-id",
    "key_vault": "dev-kv-unhcr",
    "function_app": "dev-mcp-donor",
    "storage_account": "devstorageunhcr",
    "application_insights": "dev-appinsights"
  },
  "logging": {
    "level": "DEBUG",
    "telemetry": true,
    "application_insights_enabled": true,
    "log_analytics_enabled": true
  },
  "features": {
    "new_dashboard": false,
    "advanced_analytics": true,
    "experimental_features": false
  },
  "security": {
    "require_https": true,
    "cors_origins": ["https://unhcr.org", "https://mcp.unhcr.org"],
    "rate_limiting": {
      "enabled": true,
      "requests_per_minute": 1000
    }
  }
}
```

### Environment-Specific Configuration

```yaml
# config/environments/dev.yaml
domain: DonorManagement
environment: Dev

fabric:
  endpoint: "https://dev-fabric.unhcr.org"
  semantic_models:
    - DonorManagement
    - Finance
  warehouses:
    - GoldLayer
    - SilverLayer
  lakehouses:
    - Gold
  timeout: 60
  max_retries: 3

azure:
  tenant_id: "your-tenant-id"
  client_id: "your-client-id"
  key_vault: "dev-kv-unhcr"
  function_app: "dev-mcp-donor"
  storage_account: "devstorageunhcr"

logging:
  level: DEBUG
  telemetry: true
  application_insights_enabled: true

features:
  new_dashboard: false
  advanced_analytics: true

# config/environments/prod.yaml
domain: DonorManagement
environment: Production

fabric:
  endpoint: "https://fabric.unhcr.org"
  semantic_models:
    - DonorManagement
    - Finance
  warehouses:
    - GoldLayer
    - SilverLayer
  lakehouses:
    - Gold
  timeout: 300
  max_retries: 5

azure:
  tenant_id: "your-tenant-id"
  client_id: "your-client-id"
  key_vault: "prod-kv-unhcr"
  function_app: "mcp-donor"
  storage_account: "prodstorageunhcr"

logging:
  level: WARNING
  telemetry: true
  application_insights_enabled: true

features:
  new_dashboard: true
  advanced_analytics: true
```

## 📈 Monitoring and Metrics

### Key Metrics

| Metric | Description | Target | Alert Threshold |
|--------|-------------|--------|-----------------|
| Config Load Time | Time to load configuration | < 100ms | > 500ms |
| Config Validation Time | Time to validate configuration | < 50ms | > 200ms |
| Key Vault Calls | Number of Key Vault API calls | Varies | > 1000/min |
| Key Vault Latency | Key Vault API latency | < 100ms | > 500ms |
| Config Changes | Configuration changes detected | 0 | > 5/day |
| Missing Secrets | Attempts to access non-existent secrets | 0 | > 1/hour |

### Configuration Queries

```kusto
// Get configuration load times
ConfigurationLoads
| where TimeGenerated > ago(1d)
| summarize avg(LoadTimeMs), max(LoadTimeMs), min(LoadTimeMs) by Environment
| order by avg_LoadTimeMs desc

// Get Key Vault usage
KeyVaultCalls
| where TimeGenerated > ago(1d)
| summarize count() by Operation, StatusCode
| order by count_ desc

// Get Key Vault latency
KeyVaultCalls
| where TimeGenerated > ago(1d)
| summarize avg(DurationMs), max(DurationMs) by Operation
| order by avg_DurationMs desc

// Get configuration validation errors
ConfigurationErrors
| where TimeGenerated > ago(1d)
| summarize count() by ErrorType, Environment
| order by count_ desc
```

## 🚀 Best Practices

### ⭐ Use Environment-Specific Configuration

Always use separate configurations for each environment.

```python
# Good - Environment-specific configuration
config = Configuration(
    environments={
        "Dev": EnvironmentConfig(
            fabric_endpoint="https://dev-fabric.unhcr.org",
            logging_level="DEBUG"
        ),
        "Test": EnvironmentConfig(
            fabric_endpoint="https://test-fabric.unhcr.org",
            logging_level="INFO"
        ),
        "Production": EnvironmentConfig(
            fabric_endpoint="https://fabric.unhcr.org",
            logging_level="WARNING"
        )
    }
)

# Bad - Single configuration for all environments
config = Configuration(
    environments={
        "Dev": EnvironmentConfig(
            fabric_endpoint="https://fabric.unhcr.org",  # Same for all
            logging_level="DEBUG"
        ),
        "Production": EnvironmentConfig(
            fabric_endpoint="https://fabric.unhcr.org",  # Same as Dev
            logging_level="DEBUG"  # Should be WARNING
        )
    }
)
```

### ⭐ Use Key Vault for Secrets

Never store secrets in code or configuration files.

```python
# Good - Secrets in Key Vault
fabric_credentials = keyvault.get_secret("fabric-credentials")
database_password = keyvault.get_secret("db-password")

# Bad - Secrets in code
fabric_credentials = "username:password@server"  # Never do this!
database_password = "mysecretpassword"  # Never do this!
```

### ⭐ Validate Configuration

Always validate configuration on startup.

```python
# Good - Configuration validation
from platform.config import ConfigValidator

validator = ConfigValidator()
errors = validator.validate(config)

if errors:
    raise ConfigurationError(f"Invalid configuration: {errors}")

# Bad - No validation
# No validation of configuration
```

### ⭐ Use Feature Flags

Use feature flags for controlling functionality.

```python
# Good - Feature flags
from platform.config import get_feature_flag

if get_feature_flag("new_dashboard", default=False):
    # Enable new dashboard
    enable_new_dashboard()
else:
    # Use old dashboard
    enable_old_dashboard()

# Bad - Hardcoded feature checks
# if environment == "Dev":
#     enable_new_dashboard()
# else:
#     enable_old_dashboard()
```

### ⭐ Use Configuration Schemas

Define schemas for configuration validation.

```python
# Good - Configuration schema
schema = {
    "required": ["domain", "environment", "fabric.endpoint"],
    "properties": {
        "domain": {"type": "string", "minLength": 1},
        "environment": {"type": "string", "enum": ["Dev", "Test", "Production"]},
        "fabric": {
            "type": "object",
            "required": ["endpoint"],
            "properties": {
                "endpoint": {"type": "string", "format": "uri"}
            }
        }
    }
}

# Bad - No schema validation
# No validation of configuration structure
```

### ⭐ Cache Configuration

Cache configuration to avoid repeated loading.

```python
# Good - Configuration caching
from platform.config import get_config

# Configuration is automatically cached
config = get_config()

# Bad - Repeated configuration loading
# config = load_config()  # Loads from file every time
```

### ⭐ Use Default Values

Provide default values for optional configuration.

```python
# Good - Default values
from platform.config import get_config

config = get_config()
logging_level = config.logging.level if config.logging else "INFO"

# Bad - No defaults
# logging_level = config.logging.level  # Could raise AttributeError
```

## 🔍 Troubleshooting

### Common Issues

#### Configuration Not Loading

**Symptoms:** Configuration values are None or missing

**Causes:**
- Configuration file not found
- Environment variable not set
- Incorrect file path
- Syntax errors in configuration file

**Solutions:**
1. Check configuration file exists
2. Verify environment variable is set
3. Check file path is correct
4. Validate YAML/JSON syntax

```python
# Debug configuration loading
from platform.config import Configuration

try:
    config = Configuration()
    print(f"Configuration loaded successfully")
    print(f"Current environment: {config.get_current_environment().environment}")
except Exception as e:
    print(f"Configuration loading failed: {e}")
    import traceback
    traceback.print_exc()
```

#### Key Vault Access Failed

**Error:** `KeyVaultError: Failed to access Key Vault`

**Causes:**
- Incorrect Key Vault URL
- Invalid credentials
- Network connectivity issues
- Key Vault permissions not configured

**Solutions:**
1. Check Key Vault URL: `AZURE_KEY_VAULT`
2. Verify credentials: `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`
3. Check network connectivity to Key Vault
4. Verify Key Vault permissions

```python
# Debug Key Vault access
from platform.config import KeyVaultClient

try:
    keyvault = KeyVaultClient(
        vault_url="https://dev-kv-unhcr.vault.azure.net"
    )
    
    # Test connection
    secrets = keyvault.list_secrets()
    print(f"Key Vault access successful: {len(secrets)} secrets found")
    
    # Test secret retrieval
    secret = keyvault.get_secret("test-secret")
    print(f"Secret retrieval successful")
    
except Exception as e:
    print(f"Key Vault access failed: {e}")
    print(f"Vault URL: {keyvault.vault_url}")
    print(f"Authentication type: {keyvault.authentication_type}")
```

#### Secret Not Found

**Error:** `SecretNotFoundError: Secret not found: fabric-credentials`

**Causes:**
- Secret doesn't exist in Key Vault
- Typo in secret name
- Wrong Key Vault
- Secret was deleted

**Solutions:**
1. Check secret exists in Key Vault
2. Verify secret name spelling
3. Check correct Key Vault is being used
4. Create the secret if missing

```python
# Debug secret access
from platform.config import keyvault

# List all secrets to check if it exists
secrets = keyvault.list_secrets()
print(f"Available secrets: {[s.name for s in secrets]}")

# Check if specific secret exists
if keyvault.secret_exists("fabric-credentials"):
    print("Secret exists")
else:
    print("Secret does not exist")
```

#### Configuration Validation Failed

**Error:** `ConfigurationError: Invalid configuration: {...}`

**Causes:**
- Required fields missing
- Invalid field types
- Values out of range
- Custom validation failed

**Solutions:**
1. Check validation errors for details
2. Add missing required fields
3. Fix invalid field types
4. Correct out-of-range values

```python
# Debug configuration validation
from platform.config import ConfigValidator, Configuration

validator = ConfigValidator()
config = Configuration(...)

# Get detailed validation errors
errors = validator.get_validation_errors(config)

for error in errors:
    print(f"Field: {error.field}")
    print(f"Error: {error.message}")
    print(f"Expected: {error.expected}")
    print(f"Actual: {error.actual}")
    print("---")
```

## 📚 Examples

### Complete Configuration Example

```python
from platform.config import (
    Configuration, 
    EnvironmentConfig, 
    FabricConfig, 
    AzureConfig, 
    LoggingConfig,
    get_config,
    keyvault
)
from platform.fabric import get_semantic_model

# Initialize configuration
config = Configuration(
    default_environment="Dev",
    environments={
        "Dev": EnvironmentConfig(
            domain="DonorManagement",
            environment="Dev",
            fabric=FabricConfig(
                endpoint="https://dev-fabric.unhcr.org",
                semantic_models=["DonorManagement", "Finance"],
                timeout=60,
                max_retries=3
            ),
            azure=AzureConfig(
                tenant_id="your-tenant-id",
                client_id="your-client-id",
                key_vault="dev-kv-unhcr",
                function_app="dev-mcp-donor"
            ),
            logging=LoggingConfig(
                level="DEBUG",
                telemetry=True,
                application_insights_enabled=True
            ),
            features={
                "new_dashboard": False,
                "advanced_analytics": True
            }
        ),
        "Production": EnvironmentConfig(
            domain="DonorManagement",
            environment="Production",
            fabric=FabricConfig(
                endpoint="https://fabric.unhcr.org",
                semantic_models=["DonorManagement", "Finance"],
                timeout=300,
                max_retries=5
            ),
            azure=AzureConfig(
                tenant_id="your-tenant-id",
                client_id="your-client-id",
                key_vault="prod-kv-unhcr",
                function_app="mcp-donor"
            ),
            logging=LoggingConfig(
                level="WARNING",
                telemetry=True,
                application_insights_enabled=True
            ),
            features={
                "new_dashboard": True,
                "advanced_analytics": True
            }
        )
    }
)

# Get current configuration
current_config = get_config()

# Access configuration values
print(f"Current environment: {current_config.environment}")
print(f"Domain: {current_config.domain}")
print(f"Fabric endpoint: {current_config.fabric.endpoint}")

# Get secrets from Key Vault
try:
    fabric_credentials = keyvault.get_secret("fabric-credentials")
    print(f"Fabric credentials retrieved: {len(fabric_credentials)} chars")
except Exception as e:
    print(f"Failed to get fabric credentials: {e}")

# Use configuration in application
if current_config.features.new_dashboard:
    print("New dashboard is enabled")
    enable_new_dashboard()
else:
    print("New dashboard is disabled")
    enable_old_dashboard()

# Get semantic model using configuration
semantic_model = get_semantic_model("DonorManagement")
result = semantic_model.execute(
    query="SELECT DonorCount, TotalRevenue FROM DonorMetrics WHERE Year = 2026"
)
```

### Environment Detection Example

```python
from platform.config import get_config, get_environment_config

# Get current environment
config = get_config()
current_env = config.environment

# Get environment-specific configuration
env_config = get_environment_config(current_env)

# Use environment-specific settings
if current_env == "Dev":
    # Development-specific settings
    debug_mode = True
    cache_enabled = False
elif current_env == "Test":
    # Test-specific settings
    debug_mode = False
    cache_enabled = True
else:  # Production
    # Production-specific settings
    debug_mode = False
    cache_enabled = True

# Or use feature flags
from platform.config import get_feature_flag

debug_mode = get_feature_flag("debug_mode", default=False)
cache_enabled = get_feature_flag("cache_enabled", default=True)
```

### Secure Configuration with Key Vault

```python
from platform.config import keyvault, get_config
from platform.fabric import FabricClient

# Get configuration
config = get_config()

# Get secrets from Key Vault
try:
    # Get Fabric credentials
    fabric_client_id = keyvault.get_secret("fabric-client-id")
    fabric_client_secret = keyvault.get_secret("fabric-client-secret")
    fabric_tenant_id = keyvault.get_secret("fabric-tenant-id")
    
    # Create Fabric client with secure credentials
    fabric_client = FabricClient(
        endpoint=config.fabric.endpoint,
        client_id=fabric_client_id,
        client_secret=fabric_client_secret,
        tenant_id=fabric_tenant_id
    )
    
    # Use client
    response = fabric_client.get("/api/v1/workspaces")
    
except Exception as e:
    print(f"Failed to initialize Fabric client: {e}")
    raise
```

---

## 📖 API Reference

### Exceptions

| Exception | Description | Error Code |
|-----------|-------------|------------|
| `ConfigurationError` | Base configuration error | CONFIG-001 |
| `EnvironmentNotFoundError` | Environment not found | CONFIG-002 |
| `SecretNotFoundError` | Secret not found in Key Vault | CONFIG-003 |
| `KeyVaultError` | Key Vault access error | CONFIG-004 |
| `ValidationError` | Configuration validation error | CONFIG-005 |

### Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| CONFIG-001 | Configuration error | 500 |
| CONFIG-002 | Environment not found | 404 |
| CONFIG-003 | Secret not found | 404 |
| CONFIG-004 | Key Vault error | 500 |
| CONFIG-005 | Validation error | 400 |

---

*⭐ = Best Practice | 🔒 = Security Requirement | ⚡ = Performance Consideration*