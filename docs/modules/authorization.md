# 🛡️ Authorization Module

The Authorization Module provides enterprise-grade Role-Based Access Control (RBAC) with fine-grained permission management for the MCP Platform Framework. It ensures that authenticated users can only perform actions they are authorized to perform.

## 🎯 Overview

The Authorization Module handles:
- **Enterprise RBAC**: Role definitions, hierarchy, and inheritance
- **Permission Decorators**: Easy-to-use decorators for permission checks
- **Policy Enforcement**: Centralized policy definitions and caching
- **Standardized Checks**: Consistent permission naming and validation
- **Audit Logging**: Comprehensive logging of all authorization decisions

## 🏗️ Architecture

```
┌────────────────────────────────────────────┐
│         Authorization Module               │
├────────────────────────────────────────────┤
│  ┌───────────────────┐  ┌────────────────┐ │
│  │   RBAC Engine     │  │ Permission     │ │
│  │                   │  │  Decorators    │ │
│  └───────────────────┘  └────────────────┘ │
│  ┌───────────────────┐  ┌────────────────┐ │
│  │ Policy Enforcement│  │ Standardized   │ │
│  │                   │  │  Checks        │ │
│  └───────────────────┘  └────────────────┘ │
└────────────────────────────────────────────┘
```

## 📦 Installation

The Authorization Module is included as part of the MCP Platform Framework.

```bash
# Install the platform framework
pip install mcp-platform-framework
```

## 🚀 Quick Start

### Basic Usage

```python
from platform.auth import requires_permission, requires_role

# Permission-based authorization
@requires_permission("donor.read")
def get_donor(donor_id: str):
    return donor_service.get(donor_id)

# Role-based authorization
@requires_role("donor_analyst")
def get_donor_analytics():
    return analytics_service.get_donor_metrics()

# Multiple permissions
@requires_any_permission(["donor.read", "donor.admin"])
def get_donor_list():
    return donor_service.list_all()
```

### Configuration

```python
# config/authorization.py
from platform.auth.config import RBACConfig

# RBAC Configuration
RBAC_CONFIG = RBACConfig(
    # Policy store configuration
    policy_store_type="azure_blob",  # or "database", "file"
    policy_store_connection_string="DefaultEndpointsProtocol=https;...",
    
    # Caching configuration
    cache_enabled=True,
    cache_ttl=300,  # 5 minutes
    cache_max_size=10000,
    
    # Permission hierarchy
    permission_hierarchy={
        "donor.admin": ["donor.read", "donor.write", "donor.delete"],
        "finance.admin": ["finance.read", "finance.write", "finance.report"]
    },
    
    # Default permissions
    default_permissions={
        "donor_analyst": ["donor.read", "donor.analytics"],
        "donor_manager": ["donor.read", "donor.write", "donor.analytics"]
    }
)
```

## 🔧 Configuration

### Environment Variables

```bash
# RBAC Configuration
RBAC_POLICY_STORE_TYPE=azure_blob
RBAC_POLICY_STORE_CONNECTION_STRING=your-connection-string
RBAC_CACHE_ENABLED=true
RBAC_CACHE_TTL=300
RBAC_CACHE_MAX_SIZE=10000
```

### Configuration File

```yaml
# config/authorization.yaml
authorization:
  policy_store:
    type: azure_blob  # azure_blob, database, file
    connection_string: ${RBAC_POLICY_STORE_CONNECTION_STRING}
    container: rbac-policies
    
  cache:
    enabled: true
    ttl: 300
    max_size: 10000
    
  permission_hierarchy:
    donor.admin:
      - donor.read
      - donor.write
      - donor.delete
    finance.admin:
      - finance.read
      - finance.write
      - finance.report
      - finance.confidential
    
  default_permissions:
    donor_analyst:
      - donor.read
      - donor.analytics
    donor_manager:
      - donor.read
      - donor.write
      - donor.analytics
    finance_analyst:
      - finance.read
      - finance.report
    
  audit:
    log_success: true
    log_failure: true
    log_all_checks: false
```

## 🎯 API Reference

### Decorators

#### `@requires_permission(permission)`

Requires the caller to have the specified permission.

```python
from platform.auth import requires_permission

@requires_permission("donor.read")
def get_donor(donor_id: str):
    return donor_service.get(donor_id)

# With custom error message
@requires_permission("donor.read", error_message="Read access to donor data required")
def get_donor(donor_id: str):
    pass
```

**Parameters:**
- `permission` (str): The required permission
- `error_message` (str, optional): Custom error message
- `error_code` (str, optional): Custom error code (default: "AUTHZ-001")

**Raises:**
- `AuthorizationError`: If the caller doesn't have the required permission

#### `@requires_any_permission(permissions)`

Requires the caller to have at least one of the specified permissions.

```python
from platform.auth import requires_any_permission

@requires_any_permission(["donor.read", "donor.admin"])
def get_donor_list():
    return donor_service.list_all()
```

**Parameters:**
- `permissions` (List[str]): List of permissions, any one of which is required
- `error_message` (str, optional): Custom error message
- `error_code` (str, optional): Custom error code (default: "AUTHZ-002")

**Raises:**
- `AuthorizationError`: If the caller doesn't have any of the required permissions

#### `@requires_all_permissions(permissions)`

Requires the caller to have all of the specified permissions.

```python
from platform.auth import requires_all_permissions

@requires_all_permissions(["donor.read", "donor.analytics"])
def get_donor_analytics():
    return analytics_service.get_donor_metrics()
```

**Parameters:**
- `permissions` (List[str]): List of permissions, all of which are required
- `error_message` (str, optional): Custom error message
- `error_code` (str, optional): Custom error code (default: "AUTHZ-003")

**Raises:**
- `AuthorizationError`: If the caller doesn't have all of the required permissions

#### `@requires_role(role)`

Requires the caller to have the specified role.

```python
from platform.auth import requires_role

@requires_role("donor_analyst")
def get_donor_report():
    return report_service.generate_donor_report()
```

**Parameters:**
- `role` (str): The required role
- `error_message` (str, optional): Custom error message
- `error_code` (str, optional): Custom error code (default: "AUTHZ-004")

**Raises:**
- `AuthorizationError`: If the caller doesn't have the required role

#### `@requires_any_role(roles)`

Requires the caller to have at least one of the specified roles.

```python
from platform.auth import requires_any_role

@requires_any_role(["donor_analyst", "donor_manager"])
def get_donor_data():
    return donor_service.get_data()
```

**Parameters:**
- `roles` (List[str]): List of roles, any one of which is required
- `error_message` (str, optional): Custom error message
- `error_code` (str, optional): Custom error code (default: "AUTHZ-005")

#### `@requires_all_roles(roles)`

Requires the caller to have all of the specified roles.

```python
from platform.auth import requires_all_roles

@requires_all_roles(["donor_analyst", "finance_analyst"])
def get_cross_domain_report():
    return report_service.generate_cross_domain_report()
```

**Parameters:**
- `roles` (List[str]): List of roles, all of which are required
- `error_message` (str, optional): Custom error message
- `error_code` (str, optional): Custom error code (default: "AUTHZ-006")

### Functions

#### `check_permission(caller, permission)`

Check if a caller has a specific permission.

```python
from platform.auth import check_permission, get_caller_identity

caller = get_caller_identity()
if check_permission(caller, "donor.read"):
    # User has permission
    pass
```

**Parameters:**
- `caller` (CallerIdentity): The caller to check
- `permission` (str): The permission to check

**Returns:**
- `bool`: True if the caller has the permission, False otherwise

#### `check_any_permission(caller, permissions)`

Check if a caller has any of the specified permissions.

```python
from platform.auth import check_any_permission, get_caller_identity

caller = get_caller_identity()
if check_any_permission(caller, ["donor.read", "donor.admin"]):
    # User has at least one permission
    pass
```

**Parameters:**
- `caller` (CallerIdentity): The caller to check
- `permissions` (List[str]): List of permissions to check

**Returns:**
- `bool`: True if the caller has any of the permissions, False otherwise

#### `check_all_permissions(caller, permissions)`

Check if a caller has all of the specified permissions.

```python
from platform.auth import check_all_permissions, get_caller_identity

caller = get_caller_identity()
if check_all_permissions(caller, ["donor.read", "donor.analytics"]):
    # User has all permissions
    pass
```

**Parameters:**
- `caller` (CallerIdentity): The caller to check
- `permissions` (List[str]): List of permissions to check

**Returns:**
- `bool`: True if the caller has all of the permissions, False otherwise

#### `check_role(caller, role)`

Check if a caller has a specific role.

```python
from platform.auth import check_role, get_caller_identity

caller = get_caller_identity()
if check_role(caller, "donor_analyst"):
    # User has role
    pass
```

**Parameters:**
- `caller` (CallerIdentity): The caller to check
- `role` (str): The role to check

**Returns:**
- `bool`: True if the caller has the role, False otherwise

### Classes

#### `RBACEngine`

The core RBAC engine that performs permission checks.

```python
from platform.auth import RBACEngine, PolicyStore

# Create policy store
policy_store = PolicyStore(
    store_type="azure_blob",
    connection_string="DefaultEndpointsProtocol=https;..."
)

# Create RBAC engine
rbac = RBACEngine(policy_store)

# Check permission
caller = get_caller_identity()
has_permission = await rbac.check_permission(caller, "donor.read")
```

**Parameters:**
- `policy_store` (PolicyStore): The policy store to use
- `cache_enabled` (bool, optional): Whether to enable caching (default: True)
- `cache_ttl` (int, optional): Cache TTL in seconds (default: 300)
- `cache_max_size` (int, optional): Maximum cache size (default: 10000)

**Methods:**
- `check_permission(caller, permission)`: Check if caller has permission
- `check_any_permission(caller, permissions)`: Check if caller has any permission
- `check_all_permissions(caller, permissions)`: Check if caller has all permissions
- `check_role(caller, role)`: Check if caller has role
- `get_effective_permissions(caller)`: Get all effective permissions for caller
- `get_role_permissions(role)`: Get permissions for a role
- `clear_cache()`: Clear the permission cache

#### `PolicyStore`

Stores and retrieves RBAC policies.

```python
from platform.auth import PolicyStore

# Create policy store
policy_store = PolicyStore(
    store_type="azure_blob",
    connection_string="DefaultEndpointsProtocol=https;...",
    container="rbac-policies"
)

# Get permissions for a role
permissions = await policy_store.get_role_permissions("donor_analyst")

# Get all roles
roles = await policy_store.get_all_roles()

# Get all permissions
permissions = await policy_store.get_all_permissions()
```

**Parameters:**
- `store_type` (str): Type of store ("azure_blob", "database", "file")
- `connection_string` (str): Connection string for the store
- `container` (str, optional): Container name for Azure Blob storage
- `table_name` (str, optional): Table name for database storage
- `file_path` (str, optional): File path for file storage

**Methods:**
- `get_role_permissions(role)`: Get permissions for a role
- `get_all_roles()`: Get all roles
- `get_all_permissions()`: Get all permissions
- `get_user_roles(user_id)`: Get roles for a user
- `get_user_permissions(user_id)`: Get permissions for a user
- `set_role_permissions(role, permissions)`: Set permissions for a role
- `add_permission_to_role(role, permission)`: Add a permission to a role
- `remove_permission_from_role(role, permission)`: Remove a permission from a role

## 📊 Permission Model

### Permission Structure

Permissions follow a hierarchical naming convention: `{domain}.{action}`

```
donor.read        # Read donor data
donor.write       # Create or update donor data
donor.delete      # Delete donor data
donor.admin       # Full donor management access
donor.analytics   # Access donor analytics

finance.read      # Read financial data
finance.write     # Create or update financial data
finance.report    # Generate financial reports
finance.admin     # Full finance management access
finance.confidential  # Access confidential financial data

system.admin      # System administration
system.audit      # Access audit logs
system.config     # Manage system configuration
```

### Role Definitions

```yaml
# Example role definitions
roles:
  # Donor Domain Roles
  donor_viewer:
    description: "Can view donor data"
    permissions:
      - "donor.read"
    
  donor_analyst:
    description: "Can view and analyze donor data"
    permissions:
      - "donor.read"
      - "donor.analytics"
    
  donor_manager:
    description: "Can manage donor data"
    permissions:
      - "donor.read"
      - "donor.write"
      - "donor.analytics"
    
  donor_admin:
    description: "Full access to donor domain"
    permissions:
      - "donor.admin"
    
  # Finance Domain Roles
  finance_viewer:
    description: "Can view financial data"
    permissions:
      - "finance.read"
    
  finance_analyst:
    description: "Can view and analyze financial data"
    permissions:
      - "finance.read"
      - "finance.report"
    
  finance_manager:
    description: "Can manage financial data"
    permissions:
      - "finance.read"
      - "finance.write"
      - "finance.report"
    
  finance_admin:
    description: "Full access to finance domain"
    permissions:
      - "finance.admin"
      - "finance.confidential"
    
  # Cross-Domain Roles
  cross_domain_analyst:
    description: "Can access data across domains for analysis"
    permissions:
      - "donor.read"
      - "finance.read"
      - "supply.read"
    
  # System Roles
  system_admin:
    description: "System administrator with full access"
    permissions:
      - "*"  # All permissions
    
  security_officer:
    description: "Security officer with audit and configuration access"
    permissions:
      - "system.audit"
      - "system.config"
      - "system.admin"
```

### Permission Hierarchy

```yaml
# Permission inheritance
permission_hierarchy:
  # Admin permissions inherit all domain permissions
  donor.admin:
    - "donor.read"
    - "donor.write"
    - "donor.delete"
    - "donor.analytics"
    
  finance.admin:
    - "finance.read"
    - "finance.write"
    - "finance.report"
    - "finance.confidential"
    
  # Wildcard permissions
  "*":
    - "*"  # All permissions
```

## 🔐 Security Features

### Least Privilege Enforcement

The Authorization Module enforces the principle of least privilege by:
1. Requiring explicit permission grants
2. Supporting fine-grained permission definitions
3. Providing permission inheritance for admin roles
4. Supporting wildcard permissions for system administrators

### Permission Caching

```python
from platform.auth import RBACEngine

# Create RBAC engine with caching
rbac = RBACEngine(
    policy_store=policy_store,
    cache_enabled=True,
    cache_ttl=300,  # 5 minutes
    cache_max_size=10000
)

# Check permission (cached)
has_permission = await rbac.check_permission(caller, "donor.read")

# Clear cache if needed
rbac.clear_cache()
```

### Audit Logging

```python
from platform.auth import AuthorizationAuditLogger

# Create audit logger
audit_logger = AuthorizationAuditLogger()

# Log authorization success
await audit_logger.log_success(
    caller="john.doe@my-org.org",
    permission="donor.read",
    resource="donor:DON-12345",
    action="read"
)

# Log authorization failure
await audit_logger.log_failure(
    caller="john.doe@my-org.org",
    permission="donor.admin",
    resource="donor:DON-12345",
    action="delete",
    reason="Insufficient permissions"
)
```

### Policy Enforcement Points

The Authorization Module integrates with the framework at multiple points:

1. **Tool Level**: Decorators on individual tools
2. **Domain Level**: Domain-wide permission requirements
3. **Resource Level**: Resource-specific access controls
4. **API Level**: API endpoint authorization

## 📈 Monitoring and Metrics

### Authorization Metrics

```python
from platform.auth import AuthorizationMetrics

# Get metrics
metrics = AuthorizationMetrics()

# Get authorization success rate
success_rate = await metrics.get_success_rate()

# Get authorization failures by type
failures_by_type = await metrics.get_failures_by_type()

# Get most denied permissions
denied_permissions = await metrics.get_most_denied_permissions()

# Get permission usage statistics
permission_usage = await metrics.get_permission_usage()
```

### Metrics Available

| Metric | Description | Use Case |
|--------|-------------|----------|
| `authorization_success_rate` | Percentage of successful authorization checks | Monitor overall authorization health |
| `authorization_failures` | Count of authorization failures | Detect access issues |
| `authorization_failures_by_permission` | Failures grouped by permission | Identify problematic permissions |
| `authorization_failures_by_role` | Failures grouped by role | Identify role configuration issues |
| `permission_usage` | Count of permission checks | Optimize permission model |
| `role_usage` | Count of role checks | Optimize role assignments |
| `cache_hit_rate` | Percentage of cached permission checks | Monitor cache effectiveness |

## 🚀 Best Practices

### ⭐ Use Permission Decorators

Always use the permission decorators for authorization checks.

```python
# Good
@requires_permission("donor.read")
def get_donor(donor_id: str):
    pass

# Bad - Manual permission check
@tool
def get_donor(donor_id: str):
    if not check_permission(get_caller_identity(), "donor.read"):
        raise AuthorizationError()
    pass
```

### ⭐ Use Specific Permissions

Use specific permissions rather than broad ones.

```python
# Good - Specific permission
@requires_permission("donor.read")
def get_donor(donor_id: str):
    pass

# Bad - Broad permission
@requires_permission("donor.admin")
def get_donor(donor_id: str):
    pass
```

### ⭐ Follow Least Privilege Principle

Grant only the minimum permissions required.

```python
# Good - Minimum permissions
roles:
  donor_viewer:
    permissions:
      - "donor.read"

# Bad - Excessive permissions
roles:
  donor_viewer:
    permissions:
      - "donor.admin"
```

### ⭐ Use Permission Hierarchy

Leverage permission hierarchy for admin roles.

```python
# Good - Use hierarchy
permission_hierarchy:
  donor.admin:
    - "donor.read"
    - "donor.write"
    - "donor.delete"

# Bad - Duplicate permissions
roles:
  donor_admin:
    permissions:
      - "donor.read"
      - "donor.write"
      - "donor.delete"
      - "donor.admin"
```

### ⭐ Cache Permission Checks

Enable caching for better performance.

```python
# Good - Caching enabled
rbac = RBACEngine(
    policy_store=policy_store,
    cache_enabled=True,
    cache_ttl=300
)

# Bad - Caching disabled
rbac = RBACEngine(
    policy_store=policy_store,
    cache_enabled=False
)
```

### ⭐ Log Authorization Decisions

Log both successes and failures for audit purposes.

```python
# Good - Comprehensive logging
audit_logger = AuthorizationAuditLogger()
await audit_logger.log_success(...)  # Log successes
await audit_logger.log_failure(...)  # Log failures

# Bad - No logging
# No audit logging configured
```

## 🔍 Troubleshooting

### Common Issues

#### Permission Denied

**Error:** `AuthorizationError: Permission denied: donor.read required`

**Causes:**
- User doesn't have the required permission
- Permission not assigned to user's role
- Permission not in user's direct permissions
- Cache stale

**Solutions:**
1. Check user's permissions: `caller.permissions`
2. Check user's roles: `caller.roles`
3. Check role permissions: `await policy_store.get_role_permissions(role)`
4. Clear cache: `rbac.clear_cache()`

```python
# Debug permission check
caller = get_caller_identity()
print(f"User permissions: {caller.permissions}")
print(f"User roles: {caller.roles}")

for role in caller.roles:
    permissions = await policy_store.get_role_permissions(role)
    print(f"Role {role} permissions: {permissions}")

# Check specific permission
has_permission = await rbac.check_permission(caller, "donor.read")
print(f"Has donor.read: {has_permission}")
```

#### Role Not Found

**Error:** `AuthorizationError: Role not found: donor_analyst`

**Causes:**
- Role not defined in policy store
- Typo in role name
- Policy store not properly configured

**Solutions:**
1. Check role definitions in policy store
2. Verify role name spelling
3. Check policy store configuration

```python
# Debug role lookup
roles = await policy_store.get_all_roles()
print(f"Available roles: {roles}")

# Check if role exists
role_exists = role_name in roles
print(f"Role {role_name} exists: {role_exists}")
```

#### Cache Issues

**Error:** `AuthorizationError: Permission denied` (but user should have permission)

**Causes:**
- Cache stale after permission changes
- Cache size exceeded
- Cache TTL too long

**Solutions:**
1. Clear cache: `rbac.clear_cache()`
2. Reduce cache TTL
3. Increase cache size

```python
# Clear cache
rbac.clear_cache()

# Check cache statistics
print(f"Cache size: {rbac.cache_size()}")
print(f"Cache hit rate: {rbac.cache_hit_rate()}")
```

## 📚 Examples

### Complete Authorization Flow

```python
from platform.auth import (
    authenticated_tool, 
    requires_permission, 
    requires_role,
    get_caller_identity
)

@authenticated_tool
@requires_permission("donor.read")
def get_donor(donor_id: str):
    """Get donor information"""
    caller = get_caller_identity()
    
    # Additional fine-grained check
    if donor_id.startswith("CONFIDENTIAL-"):
        requires_permission("donor.confidential")(lambda: None)()
    
    # Get donor data
    donor = await donor_service.get(donor_id)
    
    # Log access
    await audit_logger.log_data_access(
        user=caller.identity,
        resource=f"donor:{donor_id}",
        action="read",
        classification=donor.classification
    )
    
    return donor

@authenticated_tool
@requires_role("donor_admin")
def delete_donor(donor_id: str):
    """Delete donor information"""
    caller = get_caller_identity()
    
    # Get donor data
    donor = await donor_service.get(donor_id)
    
    # Delete donor
    await donor_service.delete(donor_id)
    
    # Log deletion
    await audit_logger.log_data_modification(
        user=caller.identity,
        resource=f"donor:{donor_id}",
        action="delete",
        classification=donor.classification
    )
    
    return {"status": "deleted", "donor_id": donor_id}
```

### Dynamic Permission Checking

```python
from platform.auth import check_permission, get_caller_identity

@authenticated_tool
def get_donor_report(report_type: str):
    """Get donor report with dynamic permission checking"""
    caller = get_caller_identity()
    
    # Check permission based on report type
    if report_type == "basic":
        if not check_permission(caller, "donor.read"):
            raise AuthorizationError(
                error_code="AUTHZ-001",
                message="Basic report requires donor.read permission"
            )
    elif report_type == "detailed":
        if not check_permission(caller, "donor.analytics"):
            raise AuthorizationError(
                error_code="AUTHZ-001",
                message="Detailed report requires donor.analytics permission"
            )
    elif report_type == "confidential":
        if not check_permission(caller, "donor.confidential"):
            raise AuthorizationError(
                error_code="AUTHZ-001",
                message="Confidential report requires donor.confidential permission"
            )
    
    # Generate report
    report = await report_service.generate(report_type)
    
    return report
```

### Role-Based Access Control

```python
from platform.auth import requires_role, get_caller_identity

@authenticated_tool
@requires_role("donor_analyst")
def get_donor_analytics():
    """Get donor analytics - requires donor_analyst role"""
    caller = get_caller_identity()
    
    # Get analytics data
    analytics = await analytics_service.get_donor_metrics()
    
    return analytics

@authenticated_tool
@requires_any_role(["donor_analyst", "finance_analyst"])
def get_cross_domain_analytics():
    """Get cross-domain analytics - requires either donor_analyst or finance_analyst"""
    caller = get_caller_identity()
    
    # Get cross-domain analytics
    analytics = await analytics_service.get_cross_domain_metrics()
    
    return analytics

@authenticated_tool
@requires_all_roles(["donor_admin", "finance_admin"])
def manage_cross_domain_settings():
    """Manage cross-domain settings - requires both donor_admin and finance_admin"""
    caller = get_caller_identity()
    
    # Manage settings
    settings = await settings_service.get_cross_domain_settings()
    
    return settings
```

---

## 📖 API Reference

### Exceptions

| Exception | Description | Error Code |
|-----------|-------------|------------|
| `AuthorizationError` | Base authorization error | AUTHZ-001 |
| `PermissionDeniedError` | Permission denied | AUTHZ-002 |
| `RoleRequiredError` | Role required | AUTHZ-003 |
| `InsufficientPermissionsError` | Insufficient permissions | AUTHZ-004 |

### Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| AUTHZ-001 | Authorization required | 403 |
| AUTHZ-002 | Permission denied | 403 |
| AUTHZ-003 | Role required | 403 |
| AUTHZ-004 | Insufficient permissions | 403 |

---

*⭐ = Best Practice | 🔒 = Security Requirement | ⚡ = Performance Consideration*