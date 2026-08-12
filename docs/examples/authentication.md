# 🔐 Authentication Guide

## Overview

This guide demonstrates how to implement **authentication** in the MCP Platform Framework using various authentication providers, including **Entra ID (Azure AD)**, **Managed Identity**, and **Service Principals**.

## 🎯 Authentication Architecture

The MCP Platform Framework supports multiple authentication methods:

```
Authentication Flow:
1. Client Request → 2. Token Validation → 3. Identity Verification → 4. Access Granted

Supported Providers:
├── Entra ID (Azure AD)
│   ├── Service Principal
│   ├── Managed Identity
│   └── User Authentication
├── Azure Key Vault
├── Azure Functions Authentication
└── Custom Authentication Providers
```

## 🏗️ Setup

### Prerequisites

1. **Azure AD Tenant** configured
2. **Service Principal** or **Managed Identity** for application authentication
3. **Azure Key Vault** for secret management
4. **MCP Platform Framework** installed

### Configuration

**config/development.json**
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
      "lifetime": 3600,
      "clock_skew": 300
    },
    "mock_auth": false
  }
}
```

### Environment Variables

```bash
# Required environment variables
export AZURE_TENANT_ID=your-tenant-id
export AZURE_CLIENT_ID=your-client-id
export AZURE_CLIENT_SECRET=your-client-secret

# For Managed Identity
export AZURE_CLIENT_ID=managed-identity-client-id

# For development (mock authentication)
export MCP_ENVIRONMENT=development
export MOCK_AUTH=true
```

## 🔧 Authentication Providers

### 1. Entra ID (Azure AD) Authentication

#### Service Principal Authentication

```python
from azure.identity import ClientSecretCredential
from mcp_framework.auth import AuthService

# Create credential
credential = ClientSecretCredential(
    tenant_id=os.getenv('AZURE_TENANT_ID'),
    client_id=os.getenv('AZURE_CLIENT_ID'),
    client_secret=os.getenv('AZURE_CLIENT_SECRET')
)

# Initialize authentication service
auth_service = AuthService(
    providers=["entra_id"],
    credential=credential,
    allowed_audiences=["api://mcp-platform"]
)

# Validate token
def validate_token(token: str) -> dict:
    """Validate JWT token using Entra ID"""
    try:
        claims = auth_service.validate_token(token)
        return {
            "status": "success",
            "valid": True,
            "claims": claims
        }
    except Exception as e:
        return {
            "status": "error",
            "valid": False,
            "error": str(e)
        }
```

#### Managed Identity Authentication

```python
from azure.identity import ManagedIdentityCredential
from mcp_framework.auth import AuthService

# Create credential (automatically uses Managed Identity)
credential = ManagedIdentityCredential()

# Initialize authentication service
auth_service = AuthService(
    providers=["managed_identity"],
    credential=credential
)

# Get access token for other Azure resources
def get_access_token(resource: str = "https://management.azure.com/") -> str:
    """Get access token for a specific resource"""
    try:
        token = credential.get_token(resource)
        return token.token
    except Exception as e:
        raise Exception(f"Failed to get access token: {str(e)}")
```

#### User Authentication (Interactive)

```python
from azure.identity import InteractiveBrowserCredential
from mcp_framework.auth import AuthService

# Create credential (opens browser for user authentication)
credential = InteractiveBrowserCredential()

# Initialize authentication service
auth_service = AuthService(
    providers=["entra_id"],
    credential=credential,
    allow_interactive=True
)

# Authenticate user
def authenticate_user() -> dict:
    """Authenticate user interactively"""
    try:
        token = credential.get_token("https://management.azure.com/")
        return {
            "status": "success",
            "access_token": token.token,
            "expires_on": token.expires_on
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
```

### 2. DefaultAzureCredential (Recommended)

The `DefaultAzureCredential` automatically tries multiple authentication methods:

```python
from azure.identity import DefaultAzureCredential
from mcp_framework.auth import AuthService

# Create credential (tries multiple methods in order)
credential = DefaultAzureCredential()

# Authentication method order:
# 1. Environment variables (AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID)
# 2. Managed Identity (when running in Azure)
# 3. Visual Studio Code authentication
# 4. Azure CLI authentication
# 5. Interactive browser authentication

# Initialize authentication service
auth_service = AuthService(
    providers=["entra_id"],
    credential=credential
)

# Use the credential directly
def get_default_token() -> str:
    """Get token using DefaultAzureCredential"""
    try:
        token = credential.get_token("https://management.azure.com/")
        return token.token
    except Exception as e:
        raise Exception(f"Failed to get token: {str(e)}")
```

### 3. Azure Functions Authentication

```python
from mcp_framework.auth import AuthService
from mcp_framework.platform import MCPFramework

# Initialize framework
framework = MCPFramework()

# Initialize authentication service for Function Apps
auth_service = AuthService(
    providers=["azure_functions"],
    function_app=True
)

# Get user information from Function App request
@framework.tool
@auth_service.authenticated
def get_user_info(request) -> dict:
    """Get authenticated user information"""
    try:
        user = auth_service.get_user_info(request)
        return {
            "status": "success",
            "user": {
                "id": user.get("id"),
                "name": user.get("name"),
                "email": user.get("email"),
                "claims": user.get("claims", {})
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
```

## 🛡️ Token Validation

### JWT Token Validation

```python
from mcp_framework.auth import AuthService, TokenValidationResult

# Initialize authentication service
auth_service = AuthService(
    providers=["entra_id"],
    allowed_audiences=["api://mcp-platform"],
    issuer="https://login.microsoftonline.com/{tenant}/v2.0"
)

# Validate JWT token
def validate_jwt_token(token: str) -> TokenValidationResult:
    """Validate JWT token"""
    try:
        result = auth_service.validate_token(token)
        
        if result.valid:
            return {
                "status": "success",
                "valid": True,
                "claims": result.claims,
                "scopes": result.scopes,
                "roles": result.roles
            }
        else:
            return {
                "status": "error",
                "valid": False,
                "error": result.error
            }
    except Exception as e:
        return {
            "status": "error",
            "valid": False,
            "error": str(e)
        }
```

### Token Claims Extraction

```python
def extract_token_claims(token: str) -> dict:
    """Extract claims from JWT token"""
    try:
        result = auth_service.validate_token(token)
        
        if result.valid:
            claims = result.claims
            
            # Extract common claims
            user_info = {
                "user_id": claims.get("oid"),
                "username": claims.get("upn"),
                "email": claims.get("email"),
                "name": claims.get("name"),
                "tenant_id": claims.get("tid"),
                "issuer": claims.get("iss"),
                "audience": claims.get("aud"),
                "expiration": claims.get("exp"),
                "issued_at": claims.get("iat"),
                "scopes": claims.get("scp", []),
                "roles": claims.get("roles", [])
            }
            
            return {
                "status": "success",
                "user_info": user_info,
                "all_claims": claims
            }
        else:
            return {
                "status": "error",
                "error": result.error
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
```

### Token Verification

```python
def verify_token_signature(token: str) -> bool:
    """Verify token signature"""
    try:
        result = auth_service.validate_token(token)
        return result.valid
    except Exception:
        return False

def verify_token_audience(token: str, expected_audience: str) -> bool:
    """Verify token audience"""
    try:
        result = auth_service.validate_token(token)
        if result.valid:
            claims = result.claims
            audience = claims.get("aud")
            
            # Handle both single audience and array of audiences
            if isinstance(audience, str):
                return audience == expected_audience
            elif isinstance(audience, list):
                return expected_audience in audience
        
        return False
    except Exception:
        return False

def verify_token_expiration(token: str) -> bool:
    """Verify token has not expired"""
    try:
        result = auth_service.validate_token(token)
        if result.valid:
            claims = result.claims
            exp = claims.get("exp")
            
            if exp:
                import time
                current_time = int(time.time())
                return current_time < exp
        
        return False
    except Exception:
        return False
```

## 🔐 Securing MCP Tools

### Authentication Decorators

```python
from mcp_framework.auth import authenticated_tool, requires_permission
from mcp_framework.platform import MCPFramework

framework = MCPFramework()

# Basic authentication
@authenticated_tool
def my_tool(param: str) -> dict:
    """Tool that requires authentication"""
    return {"status": "success", "param": param}

# Authentication with specific permissions
@authenticated_tool
@requires_permission("donor.read")
def get_donor(donor_id: str) -> dict:
    """Get donor information (requires donor.read permission)"""
    # Tool implementation
    return {"status": "success", "donor_id": donor_id}

# Authentication with multiple permissions
@authenticated_tool
@requires_permission("donor.read", "donor.analytics")
def get_donor_analytics(donor_id: str) -> dict:
    """Get donor analytics (requires both donor.read and donor.analytics)"""
    # Tool implementation
    return {"status": "success", "donor_id": donor_id}
```

### Custom Authentication Logic

```python
from mcp_framework.auth import authenticated_tool
from mcp_framework.platform import MCPFramework

framework = MCPFramework()

# Custom authentication function
def custom_auth_check(request) -> bool:
    """Custom authentication logic"""
    # Check for API key in headers
    api_key = request.headers.get("X-API-Key")
    
    if api_key:
        # Validate API key (e.g., from database or Key Vault)
        valid_key = get_valid_api_key()
        return api_key == valid_key
    
    # Fall back to default authentication
    return True

# Use custom authentication
@authenticated_tool(auth_func=custom_auth_check)
def my_tool_with_custom_auth(param: str) -> dict:
    """Tool with custom authentication"""
    return {"status": "success", "param": param}
```

### Role-Based Authentication

```python
from mcp_framework.auth import authenticated_tool, requires_role

# Require specific role
@authenticated_tool
@requires_role("admin")
def admin_tool(param: str) -> dict:
    """Tool that requires admin role"""
    return {"status": "success", "param": param}

# Require any of multiple roles
@authenticated_tool
@requires_role("admin", "superuser")
def privileged_tool(param: str) -> dict:
    """Tool that requires admin or superuser role"""
    return {"status": "success", "param": param}
```

## 📊 Authentication in Tools

### Getting User Information

```python
from mcp_framework.auth import authenticated_tool, get_current_user
from mcp_framework.platform import MCPFramework

framework = MCPFramework()

@authenticated_tool
def get_current_user_info() -> dict:
    """Get information about the currently authenticated user"""
    try:
        user = get_current_user()
        
        return {
            "status": "success",
            "user": {
                "id": user.get("id"),
                "name": user.get("name"),
                "email": user.get("email"),
                "tenant_id": user.get("tenant_id"),
                "claims": user.get("claims", {})
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
```

### Checking Permissions

```python
from mcp_framework.auth import authenticated_tool, has_permission

@authenticated_tool
def check_user_permissions() -> dict:
    """Check what permissions the current user has"""
    try:
        permissions = [
            "donor.read",
            "donor.write",
            "donor.delete",
            "donor.analytics",
            "admin.access"
        ]
        
        user_permissions = {}
        for perm in permissions:
            user_permissions[perm] = has_permission(perm)
        
        return {
            "status": "success",
            "permissions": user_permissions
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
```

### Audit Logging for Authentication

```python
from mcp_framework.auth import authenticated_tool
from mcp_framework.audit import audit_log
from mcp_framework.telemetry import track_tool_execution

@authenticated_tool
@audit_log(action="authentication.check")
@track_tool_execution
def check_authentication() -> dict:
    """Check authentication status with audit logging"""
    try:
        user = get_current_user()
        
        # Log authentication event
        framework.logger.info(
            "Authentication check",
            extra={
                "user_id": user.get("id"),
                "user_name": user.get("name"),
                "authenticated": True,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        return {
            "status": "success",
            "authenticated": True,
            "user": user
        }
    except Exception as e:
        # Log failed authentication
        framework.logger.warning(
            "Authentication check failed",
            extra={
                "error": str(e),
                "authenticated": False,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        return {
            "status": "error",
            "authenticated": False,
            "error": str(e)
        }
```

## 🧪 Testing Authentication

### Unit Tests

```python
import pytest
from unittest.mock import patch, MagicMock
from mcp_framework.auth import AuthService, authenticated_tool

def test_token_validation():
    """Test JWT token validation"""
    with patch('mcp_framework.auth.AuthService') as mock_auth:
        # Setup mock
        mock_instance = MagicMock()
        mock_instance.validate_token.return_value = MagicMock(
            valid=True,
            claims={"oid": "user-id", "name": "Test User"}
        )
        mock_auth.return_value = mock_instance
        
        # Test validation
        auth_service = AuthService()
        result = auth_service.validate_token("test-token")
        
        assert result.valid is True
        assert result.claims["oid"] == "user-id"

def test_authenticated_tool():
    """Test authenticated tool decorator"""
    with patch('mcp_framework.auth.get_current_user') as mock_user:
        mock_user.return_value = {"id": "user-id", "name": "Test User"}
        
        @authenticated_tool
        def test_tool():
            return {"status": "success"}
        
        # Test with valid user
        result = test_tool()
        assert result["status"] == "success"
```

### Integration Tests

```python
@pytest.mark.integration
def test_entra_id_authentication():
    """Test authentication with Entra ID"""
    from azure.identity import DefaultAzureCredential
    from mcp_framework.auth import AuthService
    
    # This test requires actual Azure AD configuration
    credential = DefaultAzureCredential()
    
    auth_service = AuthService(
        providers=["entra_id"],
        credential=credential
    )
    
    # Test token acquisition
    token = credential.get_token("https://management.azure.com/")
    assert token is not None
    assert len(token.token) > 0
```

## 📈 Monitoring Authentication

### Authentication Metrics

```python
from mcp_framework.telemetry import TelemetryClient
from mcp_framework.auth import authenticated_tool

telemetry = TelemetryClient()

@authenticated_tool
@telemetry.track_operation("authentication")
def track_authenticated_request() -> dict:
    """Track authenticated requests"""
    try:
        user = get_current_user()
        
        # Track authentication metrics
        telemetry.track_metric("authentication.success", 1)
        telemetry.track_metric("authentication.users", 1, {"user_id": user.get("id")})
        
        return {"status": "success", "user": user}
    except Exception as e:
        # Track failed authentication
        telemetry.track_metric("authentication.failure", 1)
        telemetry.track_exception(e)
        raise
```

### Authentication Logging

```python
import logging
from mcp_framework.platform import MCPFramework

framework = MCPFramework()
logger = framework.logger

def log_authentication_event(user: dict, success: bool, error: str = None):
    """Log authentication events"""
    event_type = "authentication_success" if success else "authentication_failure"
    
    logger.info(
        event_type,
        extra={
            "user_id": user.get("id") if user else None,
            "user_name": user.get("name") if user else None,
            "success": success,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
    )
```

## 🛠️ Best Practices

### Authentication Best Practices

1. **⭐ Use DefaultAzureCredential** - Automatically handles multiple authentication methods
2. **⭐ Always Validate Tokens** - Never trust tokens without validation
3. **⭐ Use HTTPS** - Always use HTTPS for authentication endpoints
4. **⭐ Implement Token Expiration** - Check token expiration times
5. **⭐ Use Secure Storage** - Store secrets in Azure Key Vault, not in code
6. **⭐ Log Authentication Events** - Monitor authentication attempts
7. **⭐ Handle Errors Gracefully** - Provide meaningful error messages
8. **⭐ Use Least Privilege** - Grant minimum required permissions

### Security Best Practices

1. **⭐ Never Hardcode Secrets** - Use environment variables or Key Vault
2. **⭐ Rotate Credentials Regularly** - Change service principal secrets periodically
3. **⭐ Use Managed Identity** - Prefer Managed Identity over service principals when possible
4. **⭐ Enable Multi-Factor Authentication** - Require MFA for sensitive operations
5. **⭐ Implement Conditional Access** - Use Azure AD conditional access policies
6. **⭐ Monitor for Anomalies** - Set up alerts for suspicious authentication patterns

### Performance Best Practices

1. **⭐ Cache Tokens** - Cache access tokens to avoid frequent acquisition
2. **⭐ Use Token Refresh** - Refresh tokens before they expire
3. **⭐ Minimize Token Scope** - Request only the scopes you need
4. **⭐ Use Connection Pooling** - Reuse connections for better performance

## 🛠️ Troubleshooting

### Common Authentication Issues

#### Invalid Token

**Error**: `AuthenticationError: Invalid token`

**Solution**:
```python
# Verify the token is valid
result = auth_service.validate_token(token)
print(f"Token valid: {result.valid}")
print(f"Error: {result.error}")

# Common issues:
# - Token has expired
# - Token signature is invalid
# - Token audience doesn't match
# - Token issuer doesn't match
```

#### Permission Denied

**Error**: `AuthenticationError: Permission denied`

**Solution**:
```bash
# Verify the service principal has the required permissions
az role assignment list --assignee your-service-principal

# Grant necessary permissions
az role assignment create \
  --assignee your-service-principal \
  --role "Contributor" \
  --scope "/subscriptions/your-subscription-id"
```

#### Credential Not Found

**Error**: `CredentialUnavailableError: DefaultAzureCredential failed to acquire a token`

**Solution**:
```bash
# Verify environment variables are set
echo $AZURE_TENANT_ID
echo $AZURE_CLIENT_ID
echo $AZURE_CLIENT_SECRET

# Or use Azure CLI authentication
az login

# Or use Managed Identity (when running in Azure)
```

#### Token Expired

**Error**: `AuthenticationError: Token has expired`

**Solution**:
```python
# Refresh the token
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
token = credential.get_token("https://management.azure.com/")

# Token will be automatically refreshed if expired
```

#### Invalid Audience

**Error**: `AuthenticationError: Invalid audience`

**Solution**:
```python
# Verify the token audience matches the expected audience
result = auth_service.validate_token(token)
print(f"Token audience: {result.claims.get('aud')}")
print(f"Expected audience: api://mcp-platform")

# Update the authentication configuration
auth_service = AuthService(
    allowed_audiences=["api://mcp-platform", "api://other-audience"]
)
```

## 📚 Next Steps

1. **[Authorization Guide](authorization.md)** - Learn about authorization and RBAC
2. **[Authentication Module](../modules/authentication.md)** - Deep dive into authentication module
3. **[Security Best Practices](../best-practices/security.md)** - Follow security recommendations
4. **[Donor Management Example](donor-management.md)** - Complete domain example

## 🔗 Related Documentation

- [Azure Identity Client Library](https://docs.microsoft.com/en-us/python/api/overview/azure/identity-readme)
- [Microsoft Entra ID Documentation](https://learn.microsoft.com/en-us/entra/identity/)
- [Azure AD Authentication Flows](https://docs.microsoft.com/en-us/azure/active-directory/develop/authentication-flows)
- [JWT Token Validation](https://jwt.io/introduction)

---

**Need help?** Check the [FAQ](../FAQ.md) or open an issue in the repository.
