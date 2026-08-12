# 🔐 Authentication Module

The Authentication Module provides comprehensive authentication capabilities for Azure environments, ensuring that every request to the MCP Platform Framework is properly authenticated before processing.

## 🎯 Overview

The Authentication Module handles:
- **Entra ID Integration**: Azure AD authentication with multi-tenant support
- **JWT Validation**: Token signature verification, claims validation, expiration checking
- **Managed Identity Support**: System-assigned and user-assigned identities
- **OAuth2 Handling**: Authorization code flow, client credentials flow, token refresh
- **Caller Attribution**: User identity extraction, service principal identification, request context enrichment

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Authentication Module            │
├─────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Entra ID       │  │  JWT Validation  │ │
│  │  Integration    │  │  & Verification  │ │
│  └─────────────────┘  └─────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Managed Identity│  │ OAuth2 Handling │ │
│  │   Support       │  │                 │ │
│  └─────────────────┘  └─────────────────┘ │
│  ┌─────────────────────────────────────┐ │
│  │        Token Validation              │ │
│  │      & Caller Attribution            │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## 📦 Installation

The Authentication Module is included as part of the MCP Platform Framework. No additional installation is required.

```bash
# Install the platform framework
pip install mcp-platform-framework
```

## 🚀 Quick Start

### Basic Usage

```python
from platform.auth import authenticated_tool, get_caller_identity

@authenticated_tool
def get_donor_data(donor_id: str):
    # Get caller information
    caller = get_caller_identity()
    
    # Domain logic
    return donor_service.get_donor(donor_id)
```

### Configuration

```python
# config/authentication.py
from platform.auth.config import EntraIDConfig

# Entra ID Configuration
ENTRA_ID_CONFIG = EntraIDConfig(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    audience="api://mcp-platform",
    issuer="https://login.microsoftonline.com/your-tenant-id/v2.0"
)

# Token Configuration
TOKEN_CONFIG = {
    "access_token_lifetime": 3600,  # 1 hour
    "refresh_token_lifetime": 86400,  # 24 hours
    "token_cache_ttl": 300,  # 5 minutes
    "max_token_cache_size": 1000
}
```

## 🔧 Configuration

### Environment Variables

```bash
# Entra ID Configuration
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret  # For development only

# Authentication Settings
AUTH_AUDIENCE=api://mcp-platform
AUTH_ISSUER=https://login.microsoftonline.com/your-tenant-id/v2.0
AUTH_TOKEN_LIFETIME=3600
AUTH_REFRESH_TOKEN_LIFETIME=86400

# Managed Identity
MANAGED_IDENTITY_ENABLED=true
```

### Configuration File

```yaml
# config/authentication.yaml
authentication:
  entra_id:
    tenant_id: ${AZURE_TENANT_ID}
    client_id: ${AZURE_CLIENT_ID}
    audience: ${AUTH_AUDIENCE}
    issuer: ${AUTH_ISSUER}
    allowed_tenants:
      - "my-org.org"
    
  token:
    access_lifetime: 3600
    refresh_lifetime: 86400
    cache_ttl: 300
    max_cache_size: 1000
    
  managed_identity:
    enabled: true
    
  security:
    require_https: true
    cors_origins:
      - "https://my-org.org"
      - "https://mcp.my-org.org"
    rate_limiting:
      enabled: true
      requests_per_minute: 1000
```

## 🎯 API Reference

### Decorators

#### `@authenticated_tool`

Decorates a function to require authentication.

```python
from platform.auth import authenticated_tool

@authenticated_tool
def my_tool():
    # This tool requires authentication
    pass

# With custom error message
@authenticated_tool(error_message="Authentication required for this tool")
def my_tool():
    pass
```

**Parameters:**
- `error_message` (str, optional): Custom error message for authentication failures
- `error_code` (str, optional): Custom error code (default: "AUTH-001")

**Raises:**
- `AuthenticationError`: If authentication fails

#### `@authenticated_tool_async`

Async version of `@authenticated_tool`.

```python
from platform.auth import authenticated_tool_async

@authenticated_tool_async
async def my_async_tool():
    # This async tool requires authentication
    pass
```

### Functions

#### `get_caller_identity()`

Gets the identity of the current caller.

```python
from platform.auth import get_caller_identity

caller = get_caller_identity()
print(f"User: {caller.identity}")
print(f"Name: {caller.name}")
print(f"Email: {caller.email}")
print(f"Roles: {caller.roles}")
print(f"Permissions: {caller.permissions}")
```

**Returns:**
- `CallerIdentity`: Object containing caller information

**Raises:**
- `AuthenticationError`: If not authenticated

#### `validate_token(token)`

Validates a JWT token.

```python
from platform.auth import validate_token

try:
    claims = validate_token("eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...")
    print(f"Token valid for: {claims['sub']}")
except AuthenticationError as e:
    print(f"Token validation failed: {e}")
```

**Parameters:**
- `token` (str): JWT token to validate

**Returns:**
- `dict`: Decoded token claims

**Raises:**
- `AuthenticationError`: If token is invalid

#### `get_managed_identity_token(resource)`

Gets an access token using Managed Identity.

```python
from platform.auth import get_managed_identity_token

# Get token for Fabric
token = await get_managed_identity_token("https://fabric.my-org.org")

# Get token for Key Vault
token = await get_managed_identity_token("https://vault.azure.net")
```

**Parameters:**
- `resource` (str): The resource to get a token for
- `client_id` (str, optional): Client ID for user-assigned identity

**Returns:**
- `str`: Access token

**Raises:**
- `ManagedIdentityError`: If token acquisition fails

### Classes

#### `CallerIdentity`

Represents the identity of a caller.

```python
from platform.auth import CallerIdentity

# Create a caller identity
caller = CallerIdentity(
    identity="john.doe@my-org.org",
    name="John Doe",
    email="john.doe@my-org.org",
    roles=["donor_analyst"],
    permissions=["donor.read", "donor.analytics"],
    authentication_method=["mfa"]
)

# Check permissions
if caller.has_permission("donor.read"):
    print("User can read donor data")

if caller.has_role("donor_analyst"):
    print("User is a donor analyst")

# Get maximum classification
max_classification = caller.get_max_classification()
```

**Attributes:**
- `identity` (str): Unique identifier (usually email or object ID)
- `name` (str): Display name
- `email` (str): Email address
- `roles` (List[str]): List of roles
- `permissions` (List[str]): List of permissions
- `authentication_method` (List[str]): Authentication methods used
- `is_service_principal` (bool): Whether this is a service principal

**Methods:**
- `has_permission(permission)`: Check if caller has a specific permission
- `has_role(role)`: Check if caller has a specific role
- `has_any_permission(permissions)`: Check if caller has any of the specified permissions
- `has_any_role(roles)`: Check if caller has any of the specified roles
- `get_max_classification()`: Get the highest classification level the caller can access

#### `JWTValidator`

Validates JWT tokens.

```python
from platform.auth import JWTValidator

validator = JWTValidator(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    audience="api://mcp-platform"
)

# Validate a token
claims = validator.validate("eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...")
```

**Parameters:**
- `tenant_id` (str): Azure AD tenant ID
- `client_id` (str): Azure AD client ID
- `audience` (str): Expected audience
- `issuer` (str, optional): Expected issuer
- `jwks_cache_ttl` (int, optional): JWKS cache TTL in seconds (default: 3600)

**Methods:**
- `validate(token)`: Validate a JWT token
- `get_signing_keys()`: Get the signing keys from the JWKS endpoint

## 🔐 Entra ID Integration

### Configuration

```python
from platform.auth.entra_id import EntraIDConfig, EntraIDClient

# Create configuration
config = EntraIDConfig(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    client_secret="your-client-secret",  # For confidential clients
    audience="api://mcp-platform",
    redirect_uri="https://your-app.com/auth/callback"
)

# Create client
client = EntraIDClient(config)
```

### Authentication Flows

#### Authorization Code Flow

```python
from platform.auth.entra_id import AuthorizationCodeFlow

# Create flow
flow = AuthorizationCodeFlow(
    client=client,
    scopes=["api://mcp-platform/tool.call"]
)

# Get authorization URL
auth_url = flow.get_authorization_url(
    state="random-state-string",
    redirect_uri="https://your-app.com/auth/callback"
)

# Exchange code for token
token = await flow.exchange_code_for_token(
    code="authorization-code",
    redirect_uri="https://your-app.com/auth/callback"
)
```

#### Client Credentials Flow

```python
from platform.auth.entra_id import ClientCredentialsFlow

# Create flow
flow = ClientCredentialsFlow(client=client)

# Get access token
token = await flow.get_access_token()
```

#### On-Behalf-Of Flow

```python
from platform.auth.entra_id import OnBehalfOfFlow

# Create flow
flow = OnBehalfOfFlow(client=client)

# Exchange user token for service token
token = await flow.exchange_token(
    user_token="user-access-token",
    scopes=["api://mcp-platform/tool.call"]
)
```

## 🛡️ Managed Identity Support

### System-Assigned Identity

```python
from platform.auth.managed_identity import SystemAssignedIdentity

# Get access token
identity = SystemAssignedIdentity()
token = await identity.get_access_token("https://fabric.my-org.org")
```

### User-Assigned Identity

```python
from platform.auth.managed_identity import UserAssignedIdentity

# Get access token
identity = UserAssignedIdentity(client_id="your-user-assigned-identity-id")
token = await identity.get_access_token("https://fabric.my-org.org")
```

### DefaultAzureCredential Integration

```python
from platform.auth.managed_identity import DefaultAzureCredentialIdentity

# Use DefaultAzureCredential (tries multiple identity sources)
identity = DefaultAzureCredentialIdentity()
token = await identity.get_access_token("https://fabric.my-org.org")
```

## 🔒 Security Features

### Token Validation

```python
from platform.auth import TokenValidator

validator = TokenValidator()

# Validate token signature
validator.validate_signature(token)

# Validate token expiration
validator.validate_expiration(token)

# Validate token audience
validator.validate_audience(token, "api://mcp-platform")

# Validate token issuer
validator.validate_issuer(token, "https://login.microsoftonline.com/your-tenant-id/v2.0")

# Validate all claims
validator.validate_all(token)
```

### Token Revocation

```python
from platform.auth import TokenRevocationService

# Check if token is revoked
revocation_service = TokenRevocationService()
is_revoked = await revocation_service.is_token_revoked(token)

# Revoke a token
await revocation_service.revoke_token(token, reason="Suspicious activity")

# Revoke all tokens for a user
await revocation_service.revoke_user_tokens(user_id, reason="Account compromised")
```

### Rate Limiting

```python
from platform.auth import RateLimiter

# Create rate limiter
limiter = RateLimiter(
    requests_per_minute=1000,
    burst_size=100
)

# Check if request is allowed
is_allowed = await limiter.is_allowed(ip_address="192.168.1.100")

# Check with user identification
is_allowed = await limiter.is_allowed(
    ip_address="192.168.1.100",
    user_id="john.doe@my-org.org"
)
```

## 📊 Monitoring and Telemetry

### Authentication Metrics

```python
from platform.auth import AuthenticationMetrics

# Get metrics
metrics = AuthenticationMetrics()

# Get authentication success rate
success_rate = await metrics.get_success_rate()

# Get authentication failures by type
failures_by_type = await metrics.get_failures_by_type()

# Get active sessions
active_sessions = await metrics.get_active_sessions()
```

### Audit Logging

```python
from platform.auth import AuthenticationAuditLogger

# Create audit logger
audit_logger = AuthenticationAuditLogger()

# Log authentication success
await audit_logger.log_success(
    user="john.doe@my-org.org",
    authentication_method="EntraID",
    ip_address="192.168.1.100",
    user_agent="Mozilla/5.0..."
)

# Log authentication failure
await audit_logger.log_failure(
    user="john.doe@my-org.org",
    failure_reason="Invalid token",
    error_code="AUTH-001",
    ip_address="192.168.1.100",
    user_agent="Mozilla/5.0..."
)
```

## 🚀 Best Practices

### ⭐ Use Decorators for Authentication

Always use the `@authenticated_tool` decorator for tools that require authentication.

```python
# Good
@authenticated_tool
def get_sensitive_data():
    pass

# Bad - Manual authentication check
@tool
def get_sensitive_data():
    if not is_authenticated():
        raise AuthenticationError()
    pass
```

### ⭐ Use Managed Identity for Service-to-Service

Use Managed Identity instead of service principals with secrets.

```python
# Good
token = await get_managed_identity_token("https://fabric.my-org.org")

# Bad - Using service principal with secret
token = await get_token_with_secret("client-id", "client-secret")
```

### ⭐ Validate All Token Claims

Always validate all required claims (sub, iss, aud, exp, nbf).

```python
# Good
claims = validate_token(token, validate_all_claims=True)

# Bad - Only validating some claims
claims = validate_token(token, validate_exp=False)
```

### ⭐ Use Short-Lived Tokens

Configure short token lifetimes and use refresh tokens.

```python
# Good
config = {
    "access_token_lifetime": 3600,  # 1 hour
    "refresh_token_lifetime": 86400  # 24 hours
}

# Bad - Long-lived tokens
config = {
    "access_token_lifetime": 86400,  # 24 hours
    "refresh_token_lifetime": 2592000  # 30 days
}
```

### ⭐ Implement Token Revocation

Implement token revocation for compromised tokens.

```python
# Good
if await revocation_service.is_token_revoked(token):
    raise TokenRevokedError()

# Bad - No revocation check
claims = validate_token(token)  # No revocation check
```

### ⭐ Use HTTPS Everywhere

Always use HTTPS for all communications.

```python
# Good
config = {
    "require_https": True,
    "redirect_http_to_https": True
}

# Bad - Allowing HTTP
config = {
    "require_https": False
}
```

## 🔍 Troubleshooting

### Common Issues

#### Token Validation Failed

**Error:** `AuthenticationError: Token validation failed`

**Causes:**
- Invalid token signature
- Token has expired
- Wrong audience or issuer
- Missing required claims

**Solutions:**
1. Verify the token is from the correct issuer
2. Check token expiration time
3. Verify the audience matches your API
4. Ensure all required claims are present

```python
# Debug token validation
try:
    claims = validate_token(token)
    print(f"Token valid: {claims}")
except AuthenticationError as e:
    print(f"Validation error: {e}")
    print(f"Error code: {e.error_code}")
    print(f"Error details: {e.details}")
```

#### Managed Identity Token Acquisition Failed

**Error:** `ManagedIdentityError: Failed to acquire token`

**Causes:**
- Managed Identity not enabled
- Incorrect resource URL
- Network issues

**Solutions:**
1. Ensure Managed Identity is enabled for your Function App
2. Verify the resource URL is correct
3. Check network connectivity to Azure Instance Metadata Service

```python
# Debug Managed Identity
try:
    token = await get_managed_identity_token("https://fabric.my-org.org")
    print(f"Token acquired: {token[:20]}...")
except ManagedIdentityError as e:
    print(f"Managed Identity error: {e}")
```

#### Rate Limiting

**Error:** `RateLimitExceededError: Too many requests`

**Causes:**
- Too many requests from a single IP or user
- Burst limit exceeded

**Solutions:**
1. Implement client-side rate limiting
2. Use exponential backoff for retries
3. Increase rate limits if needed

```python
# Handle rate limiting
try:
    result = await my_tool()
except RateLimitExceededError as e:
    retry_after = e.retry_after
    await asyncio.sleep(retry_after)
    result = await my_tool()
```

## 📚 Examples

### Complete Authentication Flow

```python
from platform.auth import authenticated_tool, get_caller_identity
from platform.auth.entra_id import EntraIDClient

# Initialize Entra ID client
client = EntraIDClient(
    tenant_id="your-tenant-id",
    client_id="your-client-id"
)

@authenticated_tool
def get_donor_portfolio(donor_id: str):
    # Get caller information
    caller = get_caller_identity()
    
    # Check if caller has required permission
    if not caller.has_permission("donor.read"):
        raise AuthorizationError(
            error_code="AUTHZ-001",
            message="Permission denied"
        )
    
    # Get data from Fabric using Managed Identity
    token = await get_managed_identity_token("https://fabric.my-org.org")
    fabric_client = FabricClient(token)
    
    # Get donor data
    donor_data = await fabric_client.get_donor(donor_id)
    
    # Log access
    await audit_logger.log_data_access(
        user=caller.identity,
        resource=f"donor:{donor_id}",
        action="read",
        classification="CONFIDENTIAL"
    )
    
    return donor_data
```

### Multi-Tenant Authentication

```python
from platform.auth import authenticated_tool, get_caller_identity
from platform.auth.entra_id import MultiTenantConfig

# Configure multi-tenant support
config = MultiTenantConfig(
    allowed_tenants=["my-org.org", "partner.org"],
    tenant_mapping={
        "my-org.org": {"roles": ["donor_analyst", "donor_manager"]},
        "partner.org": {"roles": ["partner_user"]}
    }
)

@authenticated_tool
def cross_tenant_tool():
    caller = get_caller_identity()
    
    # Get tenant-specific configuration
    tenant_config = config.get_tenant_config(caller.tenant_id)
    
    # Apply tenant-specific logic
    if caller.tenant_id == "my-org.org":
        # UNHCR-specific logic
        pass
    elif caller.tenant_id == "partner.org":
        # Partner-specific logic
        pass
    
    return {"message": "Cross-tenant operation successful"}
```

---

## 📖 API Reference

### Exceptions

| Exception | Description | Error Code |
|-----------|-------------|------------|
| `AuthenticationError` | Base authentication error | AUTH-001 |
| `TokenValidationError` | Token validation failed | AUTH-002 |
| `TokenExpiredError` | Token has expired | AUTH-003 |
| `TokenRevokedError` | Token has been revoked | AUTH-004 |
| `ManagedIdentityError` | Managed Identity error | AUTH-005 |
| `RateLimitExceededError` | Rate limit exceeded | AUTH-006 |
| `TenantValidationError` | Tenant validation failed | AUTH-007 |

### Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| AUTH-001 | Authentication required | 401 |
| AUTH-002 | Token validation failed | 401 |
| AUTH-003 | Token expired | 401 |
| AUTH-004 | Token revoked | 401 |
| AUTH-005 | Managed Identity error | 500 |
| AUTH-006 | Rate limit exceeded | 429 |
| AUTH-007 | Tenant validation failed | 403 |

---

*⭐ = Best Practice | 🔒 = Security Requirement | ⚡ = Performance Consideration*