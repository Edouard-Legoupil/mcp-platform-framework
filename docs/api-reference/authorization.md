# 🛡️ Authorization API Reference

The Authorization API provides comprehensive access control and permission management for the MCP Platform Framework, ensuring that authenticated users have appropriate permissions to perform actions.

## 🎯 Overview

The Authorization API handles:

- **Role-Based Access Control (RBAC)**: Role assignment and permission checking
- **Permission Decorators**: Easy-to-use decorators for authorization checks
- **Policy Enforcement**: Centralized policy management and enforcement
- **Standardized Authorization Checks**: Consistent authorization patterns across all tools
- **Integration with Entra ID**: Leverage Azure AD roles and groups

## 🏗️ Core Classes

### AuthorizationService

Main authorization service that orchestrates all authorization operations.

**Class Signature:**
```python
class AuthorizationService:
    def __init__(
        self,
        config: Optional[AuthzConfig] = None,
        policy_store: Optional[PolicyStore] = None
    ):
        """
        Initialize the Authorization Service.
        
        Args:
            config: Authorization configuration
            policy_store: Optional policy store for custom policies
        """
```

**Methods:**

#### `check_permission()`
Check if the current caller has a specific permission.

```python
def check_permission(
    self,
    permission: str,
    caller: Optional[CallerIdentity] = None
) -> bool:
    """
    Check if the current caller has a specific permission.
    
    Args:
        permission: Permission to check (e.g., "donor.read", "donor.write")
        caller: Optional caller identity (defaults to current context)
        
    Returns:
        True if caller has permission, False otherwise
    """
```

**Example:**
```python
from platform.authorization import AuthorizationService

authz_service = AuthorizationService()

# Check if current caller can read donor data
if authz_service.check_permission("donor.read"):
    return donor_service.get_donor(donor_id)
else:
    raise AuthorizationError("Insufficient permissions")
```

#### `check_role()`
Check if the current caller has a specific role.

```python
def check_role(
    self,
    role: str,
    caller: Optional[CallerIdentity] = None
) -> bool:
    """
    Check if the current caller has a specific role.
    
    Args:
        role: Role to check (e.g., "donor_analyst", "admin")
        caller: Optional caller identity (defaults to current context)
        
    Returns:
        True if caller has role, False otherwise
    """
```

**Example:**
```python
from platform.authorization import AuthorizationService

authz_service = AuthorizationService()

# Check if current caller is a donor analyst
if authz_service.check_role("donor_analyst"):
    return donor_service.get_analytics()
else:
    raise AuthorizationError("Role required: donor_analyst")
```

#### `get_permissions()`
Get all permissions for the current caller.

```python
def get_permissions(self, caller: Optional[CallerIdentity] = None) -> List[str]:
    """
    Get all permissions for the current caller.
    
    Args:
        caller: Optional caller identity (defaults to current context)
        
    Returns:
        List of permission strings
    """
```

**Example:**
```python
from platform.authorization import AuthorizationService

authz_service = AuthorizationService()

# Get all permissions for current caller
permissions = authz_service.get_permissions()
print(f"Caller permissions: {permissions}")
```

#### `get_roles()`
Get all roles for the current caller.

```python
def get_roles(self, caller: Optional[CallerIdentity] = None) -> List[str]:
    """
    Get all roles for the current caller.
    
    Args:
        caller: Optional caller identity (defaults to current context)
        
    Returns:
        List of role strings
    """
```

### AuthzConfig

Configuration for authorization services.

```python
@dataclass
class AuthzConfig:
    # RBAC Configuration
    rbac_enabled: bool = True
    
    # Role-Permission Mapping
    role_permissions: Dict[str, List[str]] = field(default_factory=dict)
    
    # Default Permissions
    default_permissions: List[str] = field(default_factory=list)
    
    # Policy Configuration
    policy_enabled: bool = True
    policy_files: List[str] = field(default_factory=list)
    
    # Entra ID Integration
    entra_id_integration: bool = True
    group_claim: str = "groups"
    role_claim: str = "roles"
    
    # Caching
    cache_enabled: bool = True
    cache_ttl: int = 300  # 5 minutes
```

### Permission

Represents a permission in the system.

```python
@dataclass
class Permission:
    name: str
    description: str = ""
    category: str = "general"
    resource: str = "*"
    action: str = "*"
    
    def matches(self, resource: str, action: str) -> bool:
        return (self.resource == "*" or self.resource == resource) and \
               (self.action == "*" or self.action == action)
    
    @classmethod
    def from_string(cls, permission_string: str) -> "Permission":
        # Parse permission string like "donor.read" or "finance:reports:read"
        parts = permission_string.split(".")
        if len(parts) == 2:
            return cls(resource=parts[0], action=parts[1], name=permission_string)
        else:
            return cls(name=permission_string)
```

### Role

Represents a role with associated permissions.

```python
@dataclass
class Role:
    name: str
    description: str = ""
    permissions: List[str] = field(default_factory=list)
    is_system_role: bool = False
    
    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions
    
    def add_permission(self, permission: str) -> None:
        if permission not in self.permissions:
            self.permissions.append(permission)
    
    def remove_permission(self, permission: str) -> None:
        if permission in self.permissions:
            self.permissions.remove(permission)
```

## 🎪 Decorators

### `@requires_permission()`
Decorator to ensure a tool requires specific permissions.

```python
def requires_permission(
    *permissions: str,
    any_permission: bool = False
) -> Callable:
    """
    Decorator to ensure a tool requires specific permissions.
    
    Args:
        *permissions: List of required permissions
        any_permission: If True, caller needs any of the permissions (AND logic by default)
        
    Returns:
        Decorated function
    """
```

**Example:**
```python
from platform.authorization import requires_permission

@requires_permission("donor.read")
def get_donor_data(donor_id: str):
    # Requires donor.read permission
    return donor_service.get_donor(donor_id)

@requires_permission("donor.read", "donor.write", any_permission=True)
def get_or_create_donor(donor_id: str):
    # Requires either donor.read OR donor.write permission
    return donor_service.get_or_create(donor_id)
```

### `@requires_role()`
Decorator to ensure a tool requires specific roles.

```python
def requires_role(
    *roles: str,
    any_role: bool = False
) -> Callable:
    """
    Decorator to ensure a tool requires specific roles.
    
    Args:
        *roles: List of required roles
        any_role: If True, caller needs any of the roles (AND logic by default)
        
    Returns:
        Decorated function
    """
```

**Example:**
```python
from platform.authorization import requires_role

@requires_role("donor_analyst")
def get_donor_analytics():
    # Requires donor_analyst role
    return analytics_service.get_donor_analytics()

@requires_role("admin", "super_admin", any_role=True)
def admin_operation():
    # Requires either admin OR super_admin role
    return admin_service.perform_operation()
```

### `@check_policy()`
Decorator to enforce custom policies.

```python
def check_policy(
    policy_name: str,
    *args: Any,
    **kwargs: Any
) -> Callable:
    """
    Decorator to enforce custom policies.
    
    Args:
        policy_name: Name of the policy to enforce
        *args: Additional arguments for policy evaluation
        **kwargs: Additional keyword arguments for policy evaluation
        
    Returns:
        Decorated function
    """
```

**Example:**
```python
from platform.authorization import check_policy

@check_policy("data_classification", min_classification="CONFIDENTIAL")
def get_sensitive_data():
    # Requires data to be classified as CONFIDENTIAL or higher
    return data_service.get_sensitive_data()
```

## 🔧 Configuration

### Environment Variables

```bash
# Authorization Configuration
AUTHZ_ENABLED=true
AUTHZ_RBAC_ENABLED=true
AUTHZ_POLICY_ENABLED=true

# Entra ID Integration
AUTHZ_ENTRA_ID_INTEGRATION=true
AUTHZ_GROUP_CLAIM=groups
AUTHZ_ROLE_CLAIM=roles

# Caching
AUTHZ_CACHE_ENABLED=true
AUTHZ_CACHE_TTL=300
```

### Configuration File

```yaml
# config/authorization.yaml
authorization:
  rbac:
    enabled: true
    
    # Role-Permission Mapping
    role_permissions:
      donor_analyst:
        - donor.read
        - donor.analytics
        - reports.view
      
      donor_manager:
        - donor.read
        - donor.write
        - donor.delete
        - donor.analytics
      
      admin:
        - "*"
    
    default_permissions:
      - public.read
  
  policy:
    enabled: true
    policy_files:
      - policies/data_classification.yaml
      - policies/geographic_restrictions.yaml
  
  entra_id:
    integration: true
    group_claim: groups
    role_claim: roles
  
  cache:
    enabled: true
    ttl: 300
```

### Policy File Example

```yaml
# policies/data_classification.yaml
policies:
  data_classification:
    description: "Enforce data classification requirements"
    rules:
      - name: "confidential_access"
        condition: "resource.classification == 'CONFIDENTIAL'"
        required_permissions:
          - "confidential.read"
        
      - name: "strictly_confidential_access"
        condition: "resource.classification == 'STRICTLY_CONFIDENTIAL'"
        required_permissions:
          - "strictly_confidential.read"
        required_roles:
          - "security_officer"
```

## 🚀 Quick Start

### Basic Authorization Setup

```python
from platform.authorization import AuthorizationService, AuthzConfig

# Configure authorization
config = AuthzConfig(
    rbac_enabled=True,
    role_permissions={
        "donor_analyst": ["donor.read", "donor.analytics"],
        "donor_manager": ["donor.read", "donor.write", "donor.delete"]
    }
)

# Initialize authorization service
authz_service = AuthorizationService(config=config)

# Check permissions
if authz_service.check_permission("donor.read"):
    print("Access granted!")
else:
    print("Access denied!")
```

### Using Decorators

```python
from platform.authorization import requires_permission, requires_role

# Permission-based authorization
@requires_permission("donor.read")
def get_donor_data(donor_id: str):
    return donor_service.get_donor(donor_id)

# Role-based authorization
@requires_role("donor_analyst")
def get_donor_analytics():
    return analytics_service.get_analytics()

# Combined authorization
@requires_permission("donor.read")
@requires_role("donor_analyst")
def get_donor_portfolio():
    return portfolio_service.get_portfolio()
```

### Azure Function Integration

```python
from platform.authorization import requires_permission, get_caller_permissions
import azure.functions as func

@requires_permission("donor.read")
def main(req: func.HttpRequest) -> func.HttpResponse:
    # Get caller permissions
    permissions = get_caller_permissions()
    
    # Process request
    donor_data = donor_service.get_donor(req.params.get("donor_id"))
    
    return func.HttpResponse(f"Donor data: {donor_data}")
```

## ⭐ Best Practices

### Permission Design

✅ **Use Resource.Action Format**
```python
# Good: Clear, hierarchical permissions
"donor.read"
"donor.write"
"donor.delete"
"finance.reports.view"
"finance.reports.edit"
```

❌ **Avoid Vague Permissions**
```python
# Bad: Unclear what "access" means
"donor.access"
"finance.allow"
```

### Role Design

✅ **Role Hierarchy**
```python
# Good: Hierarchical roles with increasing permissions
roles = {
    "viewer": ["donor.read"],
    "analyst": ["donor.read", "donor.analytics"],
    "manager": ["donor.read", "donor.write", "donor.delete"],
    "admin": ["*"]
}
```

✅ **Principle of Least Privilege**
```python
# Good: Assign minimum required permissions
@requires_permission("donor.read")  # Only read permission needed
def view_donor(donor_id: str):
    pass

# Bad: Over-permissioning
@requires_permission("donor.write")  # Write permission not needed for read operation
def view_donor(donor_id: str):
    pass
```

### Error Handling

✅ **Provide Clear Authorization Errors**
```python
from platform.authorization import AuthorizationError

try:
    if not authz_service.check_permission("donor.read"):
        raise AuthorizationError(
            error_code="AUTHZ-001",
            category="Authorization",
            message="Insufficient permissions. Required: donor.read"
        )
except AuthorizationError as e:
    logger.warning(f"Authorization denied: {e.error_code}")
    return error_response(status_code=403, error=e)
```

## 🔍 Troubleshooting

### Common Issues

**Permission check always returns False**
- Verify that the caller has the required roles
- Check that role-permission mapping is correctly configured
- Ensure the caller identity is properly extracted

**Role check fails for valid users**
- Verify that roles are correctly assigned to users in Entra ID
- Check that the role claim is correctly configured
- Ensure role names match exactly (case-sensitive)

**Policy enforcement not working**
- Verify that policy files are correctly formatted
- Check that policies are loaded and enabled
- Ensure policy conditions are correctly specified

**Performance issues with authorization checks**
- Enable caching for authorization results
- Verify that cache TTL is appropriate
- Check for excessive permission checks in hot paths

## 📚 Related Documentation

- [Platform API](platform.md) - Core framework classes
- [Authentication API](authentication.md) - Authentication services
- [Authorization Module](../modules/authorization.md) - Module overview
- [Security Best Practices](../best-practices/security.md) - Security recommendations

---

**🎉 Ready to implement authorization?** Start with the `@requires_permission` and `@requires_role` decorators for simple integration.

**Need more details?** Check the [Authorization Module](../modules/authorization.md) for comprehensive module documentation.