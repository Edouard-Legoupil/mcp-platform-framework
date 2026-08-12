# 🔒 Security Best Practices

Comprehensive security guidelines and recommendations for building secure MCP services using the MCP Platform Framework.

## 🎯 Overview

Security is paramount for MCP services, which often handle sensitive business data and operations. This guide provides best practices for:

- **Authentication**: Secure identity verification
- **Authorization**: Proper access control
- **Data Protection**: Safeguarding sensitive information
- **Compliance**: Meeting regulatory requirements
- **Secure Development**: Building security into your development process

## 🏗️ Authentication Best Practices

### ✅ Always Use Authentication

**⭐ Best Practice**: Every tool should require authentication unless explicitly designed for public access.

```python
from platform.auth import authenticated_tool

# Good: Always require authentication by default
@authenticated_tool
def get_donor_data(donor_id: str):
    caller = get_caller_identity()
    return donor_service.get_donor(donor_id)

# Only allow anonymous access when explicitly required
@authenticated_tool(allow_anonymous=True)
def get_public_info():
    return public_service.get_info()
```

**❌ Anti-Pattern**: Tools without authentication
```python
# Bad: No authentication - security risk!
def get_donor_data(donor_id: str):
    return donor_service.get_donor(donor_id)
```

### ✅ Use Strong Authentication Methods

**⭐ Best Practice**: Use Entra ID with JWT validation and Managed Identity for service-to-service communication.

```python
from platform.auth import AuthenticationService, EntraIDConfig

# Good: Strong authentication configuration
config = EntraIDConfig(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    audience="api://mcp-platform",
    validate_signature=True,
    validate_issuer=True,
    validate_audience=True,
    validate_expiration=True
)

auth_service = AuthenticationService(config=config)
```

**❌ Anti-Pattern**: Weak authentication configuration
```python
# Bad: Weak authentication - missing validations
config = EntraIDConfig(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    validate_signature=False,  # Security risk!
    validate_expiration=False   # Security risk!
)
```

### ✅ Validate Tokens Thoroughly

**⭐ Best Practice**: Always validate all aspects of JWT tokens.

```python
from platform.auth import AuthenticationService

auth_service = AuthenticationService()

# Good: Comprehensive token validation
try:
    result = await auth_service.validate_token(
        token=token,
        audience="api://mcp-platform",
        issuer="https://login.microsoftonline.com/your-tenant-id/v2.0"
    )
    if result.is_valid:
        # Process request
        pass
except AuthenticationError as e:
    # Handle invalid token
    logger.warning(f"Token validation failed: {e.error_code}")
    raise
```

### ✅ Use Managed Identity for Service Access

**⭐ Best Practice**: Use Managed Identity instead of service principals with secrets.

```python
from platform.auth import AuthenticationService

auth_service = AuthenticationService()

# Good: Use Managed Identity for Azure resource access
token = await auth_service.get_access_token("https://management.azure.com")

# Use token for Azure API calls
headers = {
    "Authorization": f"Bearer {token.token}",
    "Content-Type": "application/json"
}
```

**❌ Anti-Pattern**: Using service principal secrets
```python
# Bad: Hardcoded service principal secrets - security risk!
client_id = "your-client-id"
client_secret = "your-client-secret"  # Never do this!
```

## 🛡️ Authorization Best Practices

### ✅ Implement Principle of Least Privilege

**⭐ Best Practice**: Grant only the minimum permissions required for each role.

```python
from platform.authorization import requires_permission, requires_role

# Good: Granular permissions
@requires_permission("donor.read")
def view_donor(donor_id: str):
    return donor_service.get_donor(donor_id)

@requires_permission("donor.write")
def update_donor(donor_id: str, data: dict):
    return donor_service.update_donor(donor_id, data)

@requires_permission("donor.delete")
def delete_donor(donor_id: str):
    return donor_service.delete_donor(donor_id)
```

**❌ Anti-Pattern**: Over-permissioning
```python
# Bad: Granting excessive permissions
@requires_permission("donor.write")  # Write permission for read-only operation
def view_donor(donor_id: str):
    return donor_service.get_donor(donor_id)
```

### ✅ Use Role-Based Access Control (RBAC)

**⭐ Best Practice**: Define clear roles with appropriate permissions.

```python
from platform.authorization import AuthorizationService, AuthzConfig

# Good: Well-defined role hierarchy
config = AuthzConfig(
    role_permissions={
        "viewer": ["donor.read"],
        "analyst": ["donor.read", "donor.analytics"],
        "manager": ["donor.read", "donor.write", "donor.delete"],
        "admin": ["*"]  # All permissions
    }
)

authz_service = AuthorizationService(config=config)
```

### ✅ Combine Permission and Role Checks

**⭐ Best Practice**: Use both permissions and roles for defense in depth.

```python
from platform.authorization import requires_permission, requires_role

# Good: Multiple layers of authorization
@requires_permission("donor.read")
@requires_role("donor_analyst")
def get_donor_analytics(donor_id: str):
    return analytics_service.get_analytics(donor_id)
```

### ✅ Check Authorization Early

**⭐ Best Practice**: Check authorization before performing any operations.

```python
from platform.authorization import AuthorizationService

authz_service = AuthorizationService()

# Good: Check authorization first
def get_donor_data(donor_id: str):
    # Check authorization before any processing
    if not authz_service.check_permission("donor.read"):
        raise AuthorizationError(
            error_code="AUTHZ-001",
            category="Authorization",
            message="Insufficient permissions. Required: donor.read"
        )
    
    # Only proceed if authorized
    return donor_service.get_donor(donor_id)
```

**❌ Anti-Pattern**: Checking authorization late
```python
# Bad: Authorization check after processing
def get_donor_data(donor_id: str):
    # Process data first - waste of resources if unauthorized
    data = donor_service.get_donor(donor_id)
    
    # Authorization check too late
    if not authz_service.check_permission("donor.read"):
        raise AuthorizationError("Access denied")
    
    return data
```

## 🏷️ Data Classification Best Practices

### ✅ Classify All Data

**⭐ Best Practice**: Every tool and data element should have a classification level.

```python
from platform.classification import classification, classify_data

# Good: Explicit classification
@classification("CONFIDENTIAL")
def get_donor_portfolio(donor_id: str):
    return donor_service.get_portfolio(donor_id)

@classification("STRICTLY_CONFIDENTIAL")
def get_sensitive_financial_data():
    return financial_service.get_sensitive_data()

@classification("PUBLIC")
def get_public_reports():
    return report_service.get_public_reports()
```

### ✅ Enforce Classification Controls

**⭐ Best Practice**: Enforce classification-based access controls.

```python
from platform.classification import classification
from platform.authorization import requires_permission

# Good: Classification enforcement
@classification("CONFIDENTIAL", enforce=True)
@requires_permission("confidential.read")
def get_confidential_data():
    return data_service.get_confidential_data()
```

### ✅ Classify Data Fields

**⭐ Best Practice**: Classify individual data fields for granular control.

```python
from platform.classification import classify_data

# Good: Field-level classification
@classify_data(
    ssn="STRICTLY_CONFIDENTIAL",
    credit_card="STRICTLY_CONFIDENTIAL",
    name="CONFIDENTIAL",
    email="CONFIDENTIAL",
    phone="CONFIDENTIAL"
)
def process_donor_data(donor_data: dict):
    return data_service.process(donor_data)
```

### ✅ Handle Classification in Audit Logging

**⭐ Best Practice**: Include classification in audit logs for compliance.

```python
from platform.audit import audit_tool_access

# Good: Classification in audit logs
@audit_tool_access(classification="CONFIDENTIAL")
def get_donor_portfolio(donor_id: str):
    return donor_service.get_portfolio(donor_id)
```

## 🔐 Secret Management Best Practices

### ✅ Never Hardcode Secrets

**⭐ Best Practice**: Always use Azure Key Vault for secrets management.

```python
from platform.keyvault import keyvault_get_secret

# Good: Retrieve secrets from Key Vault
connection_string = keyvault_get_secret("database-connection-string")
api_key = keyvault_get_secret("external-api-key")
```

**❌ Anti-Pattern**: Hardcoded secrets
```python
# Bad: Hardcoded secrets - major security risk!
connection_string = "Server=my-server;Database=my-db;User=admin;Password=secret123"
api_key = "abc123-xyz456"
```

### ✅ Use Managed Identity for Azure Resources

**⭐ Best Practice**: Use Managed Identity instead of connection strings with credentials.

```python
from platform.auth import AuthenticationService

auth_service = AuthenticationService()

# Good: Use Managed Identity for Azure SQL
token = await auth_service.get_access_token("https://database.windows.net/")

# Use token for authentication
connection_string = f"Server=my-server.database.windows.net;Database=my-db;Authentication=Active Directory Password"
```

### ✅ Rotate Secrets Regularly

**⭐ Best Practice**: Implement secret rotation policies.

```python
from platform.keyvault import KeyVaultClient

# Good: Regular secret rotation
keyvault = KeyVaultClient()

# Rotate a secret
new_secret = keyvault.rotate_secret("api-key", new_value="new-api-key")

# Set expiration for secrets
keyvault.set_secret_expiration("temp-key", expiration_days=30)
```

### ✅ Use Secret References in Configuration

**⭐ Best Practice**: Reference secrets in configuration without exposing values.

```yaml
# Good: Secret references in configuration
# config/application.yaml

 database:
   connection_string: "@Microsoft.KeyVault(SecretUri=https://my-vault.vault.azure.net/secrets/database-connection-string)"
   
 api:
   key: "@Microsoft.KeyVault(SecretUri=https://my-vault.vault.azure.net/secrets/api-key)"
```

## 🛡️ Audit Logging Best Practices

### ✅ Audit All Sensitive Operations

**⭐ Best Practice**: Log all access to sensitive data and operations.

```python
from platform.audit import audit_tool_access, audit_data_access

# Good: Comprehensive audit logging
@audit_tool_access(classification="CONFIDENTIAL")
def get_donor_portfolio(donor_id: str):
    return donor_service.get_portfolio(donor_id)

@audit_data_access(
    data_type="donor",
    access_type="read",
    classification="CONFIDENTIAL",
    fields=["name", "contact_info", "contribution_history"]
)
def get_donor_details(donor_id: str):
    return donor_service.get_details(donor_id)
```

### ✅ Include Relevant Context in Audit Logs

**⭐ Best Practice**: Include caller identity, timestamp, and operation details.

```python
from platform.audit import AuditService

audit_service = AuditService()

# Good: Comprehensive audit context
await audit_service.log_access(
    action="read",
    resource="donor:12345",
    classification="CONFIDENTIAL",
    metadata={
        "tool": "GetDonorPortfolio",
        "domain": "DonorManagement",
        "query_parameters": {"include_history": True},
        "ip_address": request.client_ip
    }
)
```

### ✅ Redact Sensitive Data from Audit Logs

**⭐ Best Practice**: Never log sensitive data like PII, passwords, or tokens.

```python
from platform.audit import audit_tool_access

# Good: Redact sensitive fields
@audit_tool_access(
    classification="CONFIDENTIAL",
    log_arguments=True,
    sensitive_fields=["ssn", "credit_card", "password", "token"]
)
def process_payment(payment_info: dict):
    return payment_service.process(payment_info)
```

### ✅ Secure Audit Log Storage

**⭐ Best Practice**: Store audit logs securely with encryption and immutability.

```python
from platform.audit import AuditConfig

# Good: Secure audit storage configuration
config = AuditConfig(
    storage_account="secure-audit-storage",
    container="audit-logs",
    encryption_enabled=True,
    immutable_storage_enabled=True,  # Prevent tampering
    retention_days=365,  # 1 year retention
    redact_sensitive_data=True
)
```

## 🔒 Network Security Best Practices

### ✅ Use Private Endpoints

**⭐ Best Practice**: Use private endpoints for Azure services to avoid public internet exposure.

```python
# Good: Private endpoint configuration
# In your Bicep/ARM template

resource privateEndpoint 'Microsoft.Network/privateEndpoints@2023-05-01' = {
  name: 'mcp-storage-pe'
  location: resourceGroup().location
  properties: {
    subnet: {
      id: subnetId
    }
    privateLinkServiceConnections: [
      {
        name: 'storage-connection'
        properties: {
          privateLinkServiceId: storageAccount.properties.privateEndpointConnections[0].properties.privateLinkServiceId
          groupIds: ['blob']
        }
      }
    ]
  }
}
```

### ✅ Implement Network Security Groups (NSGs)

**⭐ Best Practice**: Restrict network access with NSGs.

```python
# Good: NSG rules for MCP services
# In your Bicep/ARM template

resource nsg 'Microsoft.Network/networkSecurityGroups@2023-05-01' = {
  name: 'mcp-nsg'
  location: resourceGroup().location
  properties: {
    securityRules: [
      {
        name: 'Allow-AzureServices'
        properties: {
          priority: 100
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: 'AzureLoadBalancer'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '443'
          protocol: 'Tcp'
        }
      }
      {
        name: 'Deny-All-Inbound'
        properties: {
          priority: 4096
          access: 'Deny'
          direction: 'Inbound'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '*'
          protocol: '*'
        }
      }
    ]
  }
}
```

### ✅ Use Azure Firewall

**⭐ Best Practice**: Implement Azure Firewall for additional network protection.

```python
# Good: Azure Firewall configuration
# In your Bicep/ARM template

resource firewall 'Microsoft.Network/azureFirewalls@2023-05-01' = {
  name: 'mcp-firewall'
  location: resourceGroup().location
  properties: {
    applicationRuleCollections: [
      {
        name: 'mcp-apps'
        properties: {
          priority: 100
          action: {
            type: 'Allow'
          }
          rules: [
            {
              name: 'Allow-Fabric'
              priority: 100
              sourceAddresses: ['*']
              targetFqdns: ['*.fabric.microsoft.com']
              protocols: [
                {
                  protocolType: 'Https'
                  port: 443
                }
              ]
            }
          ]
        }
      }
    ]
  }
}
```

## 🔍 Monitoring and Incident Response

### ✅ Monitor Security Events

**⭐ Best Practice**: Set up alerts for security-related events.

```python
from platform.telemetry import TelemetryService

telemetry = TelemetryService()

# Good: Track security-relevant events
telemetry.track_custom_event(
    event_name="SecurityEvent",
    properties={
        "event_type": "failed_authentication",
        "user": user,
        "ip_address": ip_address,
        "reason": "invalid_token"
    },
    metrics={
        "failed_attempts": 1
    }
)
```

### ✅ Implement Automated Security Responses

**⭐ Best Practice**: Automate responses to security threats.

```python
from platform.auth import AuthenticationService

auth_service = AuthenticationService()

# Good: Automated security responses
class SecurityMonitor:
    def __init__(self):
        self.failed_attempts = {}
    
    async def check_authentication(self, token: str, ip_address: str) -> bool:
        try:
            result = await auth_service.validate_token(token)
            return result.is_valid
        except AuthenticationError as e:
            # Track failed attempts
            self.failed_attempts[ip_address] = self.failed_attempts.get(ip_address, 0) + 1
            
            # Lock out after too many attempts
            if self.failed_attempts[ip_address] > 5:
                await self.lock_out_ip(ip_address)
                return False
            
            return False
    
    async def lock_out_ip(self, ip_address: str):
        # Implement IP lockout logic
        await security_service.lock_out_ip(ip_address, duration_minutes=30)
```

## 📋 Security Checklist

### ✅ Pre-Deployment Security Checklist

- [ ] All tools have authentication enabled (unless explicitly public)
- [ ] All tools have appropriate authorization checks
- [ ] All data is properly classified
- [ ] All secrets are stored in Azure Key Vault
- [ ] Managed Identity is used for Azure resource access
- [ ] Audit logging is enabled for sensitive operations
- [ ] Sensitive data is redacted from logs
- [ ] Network security groups are properly configured
- [ ] Private endpoints are used where appropriate
- [ ] All dependencies are up-to-date and free of vulnerabilities

### ✅ Runtime Security Checklist

- [ ] Authentication tokens are validated on every request
- [ ] Authorization is checked before any operation
- [ ] Audit logs are being generated and stored
- [ ] Security events are being monitored
- [ ] Automated security responses are working
- [ ] Secrets are being rotated regularly

## 🚨 Common Security Pitfalls

### ❌ Hardcoded Credentials

**Problem**: Credentials in code can be exposed in version control or logs.

**Solution**: Always use Azure Key Vault or Managed Identity.

### ❌ Missing Authentication

**Problem**: Tools without authentication can be accessed by anyone.

**Solution**: Always use `@authenticated_tool` decorator.

### ❌ Over-Permissioning

**Problem**: Granting excessive permissions increases attack surface.

**Solution**: Follow principle of least privilege.

### ❌ Sensitive Data in Logs

**Problem**: Logging sensitive data can lead to data breaches.

**Solution**: Use redaction and never log PII or credentials.

### ❌ Missing Input Validation

**Problem**: Unvalidated input can lead to injection attacks.

**Solution**: Always validate and sanitize all inputs.

### ❌ Insecure Dependencies

**Problem**: Vulnerable dependencies can compromise your service.

**Solution**: Regularly scan dependencies for vulnerabilities.

## 📚 Related Documentation

- [Authentication API](../api-reference/authentication.md) - Authentication services
- [Authorization API](../api-reference/authorization.md) - Authorization services
- [Audit API](../api-reference/audit.md) - Audit logging services
- [Classification Module](../modules/data-classification.md) - Data classification
- [Key Vault Integration](../modules/configuration-management.md#key-vault-integration) - Secret management

---

**🎉 Ready to secure your MCP services?** Implement these security best practices to build a robust security foundation.

**Need more details?** Check the specific API references for implementation details and advanced security patterns.