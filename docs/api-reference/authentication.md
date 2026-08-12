# 🔐 Authentication API Reference

The Authentication API provides comprehensive authentication capabilities for Azure environments, ensuring secure access to the MCP Platform Framework.

## 🎯 Overview

The Authentication API handles:

- **Entra ID Integration**: Azure AD authentication with multi-tenant support
- **JWT Validation**: Token signature verification, claims validation, expiration checking
- **Managed Identity Support**: System-assigned and user-assigned identities
- **OAuth2 Handling**: Authorization code flow, client credentials flow, token refresh
- **Caller Attribution**: User identity extraction, service principal identification, request context enrichment

## 🏗️ Core Classes

### AuthenticationService

Main authentication service that orchestrates all authentication operations.

**Class Signature:**
```python
class AuthenticationService:
    def __init__(
        self,
        config: Optional[AuthConfig] = None,
        token_cache: Optional[TokenCache] = None
    ):
        """
        Initialize the Authentication Service.
        
        Args:
            config: Authentication configuration
            token_cache: Optional token cache for performance optimization
        """
```

**Methods:**

#### `validate_token()`
Validate a JWT token and extract claims.

```python
async def validate_token(
    self,
    token: str,
    audience: Optional[str] = None,
    issuer: Optional[str] = None
) -> TokenValidationResult:
    """
    Validate a JWT token and extract claims.
    
    Args:
        token: JWT token to validate
        audience: Expected audience (defaults to config)
        issuer: Expected issuer (defaults to config)
        
    Returns:
        TokenValidationResult with validated claims
        
    Raises:
        AuthenticationError: If token validation fails
    """
```

**Example:**
```python
from platform.auth import AuthenticationService

auth_service = AuthenticationService()

try:
    result = await auth_service.validate_token("eyJhbGciOiJIUzI1NiIs...")
    print(f"Valid token for user: {result.claims.get('preferred_username')}")
except AuthenticationError as e:
    print(f"Token validation failed: {e.error_code}")
```

#### `get_caller_identity()`
Extract caller identity from the current request context.

```python
def get_caller_identity(self) -> CallerIdentity:
    """
    Extract caller identity from the current request context.
    
    Returns:
        CallerIdentity with user information
        
    Raises:
        AuthenticationError: If no valid identity can be determined
    """
```

**Example:**
```python
from platform.auth import get_caller_identity

try:
    caller = get_caller_identity()
    print(f"Caller: {caller.username}")
    print(f"Roles: {caller.roles}")
    print(f"Is authenticated: {caller.is_authenticated}")
except AuthenticationError as e:
    print(f"Authentication required: {e.message}")
```

#### `get_access_token()`
Get an access token for a specific resource using Managed Identity.

```python
async def get_access_token(
    self,
    resource: str,
    identity: Optional[str] = None
) -> AccessToken:
    """
    Get an access token for a specific resource using Managed Identity.
    
    Args:
        resource: Target resource (e.g., "https://management.azure.com")
        identity: Optional specific identity to use (system or user-assigned)
        
    Returns:
        AccessToken with token and expiration
        
    Raises:
        AuthenticationError: If token acquisition fails
    """
```

**Example:**
```python
from platform.auth import AuthenticationService

auth_service = AuthenticationService()

# Get token for Azure Resource Manager
token = await auth_service.get_access_token("https://management.azure.com")
print(f"Access token: {token.token}")
print(f"Expires in: {token.expires_in} seconds")
```

#### `refresh_token()`
Refresh an expired access token.

```python
async def refresh_token(self, refresh_token: str) -> AccessToken:
    """
    Refresh an expired access token.
    
    Args:
        refresh_token: Refresh token to use
        
    Returns:
        New AccessToken
        
    Raises:
        AuthenticationError: If token refresh fails
    """
```

### EntraIDConfig

Configuration for Entra ID (Azure AD) authentication.

```python
@dataclass
class EntraIDConfig:
    tenant_id: str
    client_id: str
    audience: str = "api://mcp-platform"
    issuer: Optional[str] = None
    scopes: List[str] = field(default_factory=lambda: ["openid", "profile", "email"])
    
    # Token validation
    validate_signature: bool = True
    validate_issuer: bool = True
    validate_audience: bool = True
    validate_expiration: bool = True
    
    # Clock skew tolerance
    clock_skew_seconds: int = 300  # 5 minutes
```

### TokenValidationResult

Result of token validation containing extracted claims.

```python
@dataclass
class TokenValidationResult:
    claims: Dict[str, Any]
    is_valid: bool = True
    validation_errors: List[str] = field(default_factory=list)
    
    @property
    def username(self) -> Optional[str]:
        return self.claims.get("preferred_username") or self.claims.get("upn")
    
    @property
    def roles(self) -> List[str]:
        return self.claims.get("roles", [])
    
    @property
    def object_id(self) -> Optional[str]:
        return self.claims.get("oid")
    
    @property
    def tenant_id(self) -> Optional[str]:
        return self.claims.get("tid")
```

### CallerIdentity

Represents the identity of the current caller.

```python
@dataclass
class CallerIdentity:
    username: Optional[str] = None
    object_id: Optional[str] = None
    tenant_id: Optional[str] = None
    roles: List[str] = field(default_factory=list)
    claims: Dict[str, Any] = field(default_factory=dict)
    is_authenticated: bool = False
    authentication_method: Optional[str] = None
    
    def has_role(self, role: str) -> bool:
        return role in self.roles
    
    def has_any_role(self, roles: List[str]) -> bool:
        return any(self.has_role(role) for role in roles)
```

### AccessToken

Represents an access token with expiration information.

```python
@dataclass
class AccessToken:
    token: str
    token_type: str = "Bearer"
    expires_in: int = 3600
    ext_expires_in: int = 3600
    expires_on: datetime = field(default_factory=datetime.utcnow)
    not_before: Optional[datetime] = None
    resource: Optional[str] = None
    
    def is_expired(self) -> bool:
        return datetime.utcnow() >= self.expires_on
    
    def is_about_to_expire(self, threshold_seconds: int = 300) -> bool:
        return (self.expires_on - datetime.utcnow()).total_seconds() < threshold_seconds
```

## 🎪 Decorators

### `@authenticated_tool`
Decorator to ensure a tool requires authentication.

```python
def authenticated_tool(
    func: Optional[Callable] = None,
    *,
    allow_anonymous: bool = False,
    required_claims: Optional[List[str]] = None
) -> Callable:
    """
    Decorator to ensure a tool requires authentication.
    
    Args:
        func: Function to decorate
        allow_anonymous: If True, allow unauthenticated access
        required_claims: List of claims that must be present
        
    Returns:
        Decorated function
    """
```

**Example:**
```python
from platform.auth import authenticated_tool

@authenticated_tool
def get_donor_data(donor_id: str):
    # This tool requires authentication
    caller = get_caller_identity()
    return donor_service.get_donor(donor_id)

@authenticated_tool(allow_anonymous=True)
def get_public_info():
    # This tool allows anonymous access
    return public_service.get_info()
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
MANAGED_IDENTITY_CLIENT_ID=your-managed-identity-client-id

# Token Cache
TOKEN_CACHE_ENABLED=true
TOKEN_CACHE_TTL=300
TOKEN_CACHE_MAX_SIZE=1000
```

### Configuration File

```yaml
# config/authentication.yaml
authentication:
  entra_id:
    tenant_id: your-tenant-id
    client_id: your-client-id
    audience: api://mcp-platform
    issuer: https://login.microsoftonline.com/your-tenant-id/v2.0
    scopes:
      - openid
      - profile
      - email
    
    validation:
      validate_signature: true
      validate_issuer: true
      validate_audience: true
      validate_expiration: true
      clock_skew_seconds: 300
  
  managed_identity:
    enabled: true
    client_id: your-managed-identity-client-id
  
  token_cache:
    enabled: true
    ttl: 300
    max_size: 1000
```

## 🚀 Quick Start

### Basic Authentication Setup

```python
from platform.auth import AuthenticationService, EntraIDConfig

# Configure authentication
config = EntraIDConfig(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    audience="api://mcp-platform"
)

# Initialize authentication service
auth_service = AuthenticationService(config=config)

# Validate a token
result = await auth_service.validate_token("your-jwt-token")
print(f"Authenticated user: {result.username}")
```

### Azure Function Integration

```python
from platform.auth import authenticated_tool, get_caller_identity
import azure.functions as func

@authenticated_tool
def main(req: func.HttpRequest) -> func.HttpResponse:
    # Get caller identity
    caller = get_caller_identity()
    
    if not caller.is_authenticated:
        return func.HttpResponse("Unauthorized", status_code=401)
    
    return func.HttpResponse(f"Hello, {caller.username}!")
```

### Managed Identity Usage

```python
from platform.auth import AuthenticationService

async def access_azure_resource():
    auth_service = AuthenticationService()
    
    # Get access token for Azure Resource Manager
    token = await auth_service.get_access_token("https://management.azure.com")
    
    # Use token to call Azure APIs
    headers = {
        "Authorization": f"Bearer {token.token}",
        "Content-Type": "application/json"
    }
    
    # Make API call
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://management.azure.com/api/resource",
            headers=headers
        ) as response:
            return await response.json()
```

## ⭐ Best Practices

### Token Validation

✅ **Always Validate Tokens**
```python
# Good: Always validate tokens before processing
@authenticated_tool
def sensitive_operation():
    caller = get_caller_identity()
    # Process request
```

❌ **Never Bypass Validation**
```python
# Bad: Bypassing token validation
def sensitive_operation(token: str):
    # Process request without validation - SECURITY RISK!
```

### Token Management

✅ **Use Short-Lived Tokens**
```python
# Good: Use short token lifetimes
config = EntraIDConfig(
    token_lifetime=3600,  # 1 hour
    refresh_token_lifetime=86400  # 24 hours
)
```

✅ **Cache Tokens Appropriately**
```python
# Good: Use token caching for performance
from platform.auth.cache import TokenCache

cache = TokenCache(ttl=300, max_size=1000)
auth_service = AuthenticationService(token_cache=cache)
```

### Error Handling

✅ **Handle Authentication Errors Gracefully**
```python
from platform.auth import AuthenticationError

try:
    result = await auth_service.validate_token(token)
except AuthenticationError as e:
    if e.error_code == "TOKEN_EXPIRED":
        # Handle expired token
        return redirect_to_login()
    elif e.error_code == "INVALID_SIGNATURE":
        # Handle invalid token
        return error_response("Invalid token")
    else:
        # Handle other errors
        logger.error(f"Authentication error: {e}")
        return error_response("Authentication failed")
```

## 🔍 Troubleshooting

### Common Issues

**Token validation fails with "Invalid signature"**
- Verify that the `AZURE_TENANT_ID` is correct
- Check that the token is from the expected issuer
- Ensure the audience matches the expected audience

**Managed Identity token acquisition fails**
- Verify that Managed Identity is enabled for the resource
- Check that the resource has the required permissions
- Ensure the target resource URL is correct

**Caller identity is None**
- Verify that the request includes a valid authorization header
- Check that the token is properly formatted (Bearer token)
- Ensure the authentication middleware is configured

**Token cache is not working**
- Verify that token caching is enabled in configuration
- Check that the cache TTL is appropriate
- Ensure the cache size is sufficient

## 📚 Related Documentation

- [Platform API](platform.md) - Core framework classes
- [Authorization API](authorization.md) - Access control and permissions
- [Authentication Module](../modules/authentication.md) - Module overview
- [Security Best Practices](../best-practices/security.md) - Security recommendations

---

**🎉 Ready to implement authentication?** Start with the `@authenticated_tool` decorator for simple integration.

**Need more details?** Check the [Authentication Module](../modules/authentication.md) for comprehensive module documentation.