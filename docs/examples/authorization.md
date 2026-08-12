# 🛡️ Authorization Examples

**Comprehensive examples for implementing authorization in MCP Platform Framework**

This guide demonstrates how to implement **authorization** in the MCP Platform Framework using the built-in RBAC system, permission decorators, and policy enforcement.

## 📋 Table of Contents

- [Authorization Architecture](#-authorization-architecture) - Overview of the authorization system
- [Basic Authorization Patterns](#-basic-authorization-patterns) - Simple permission and role checks
- [Advanced Authorization Scenarios](#-advanced-authorization-scenarios) - Complex permission combinations
- [Domain-Specific Examples](#-domain-specific-examples) - Real-world domain authorization
- [Integration with Other Modules](#-integration-with-other-modules) - Combining auth with other framework features
- [Testing Authorization](#-testing-authorization) - Writing tests for authorization logic
- [Best Practices](#-best-practices) - Recommended patterns and anti-patterns

## 🎯 Authorization Architecture

The MCP Platform Framework provides a comprehensive authorization system:

```
Authorization Flow:
1. Request → 2. Authentication → 3. Permission Check → 4. Policy Enforcement → 5. Access Granted/Denied

Key Components:
├── RBAC Engine - Role and permission management
├── Permission Decorators - Easy-to-use Python decorators
├── Policy Enforcement - Centralized policy evaluation
├── Audit Logging - Comprehensive access logging
└── Cache Layer - Performance optimization
```

## 🏗️ Setup

### Prerequisites

1. **MCP Platform Framework** installed
2. **Authentication Module** configured
3. **RBAC Configuration** defined
4. **Azure Key Vault** for secret management (optional)

### Configuration

**config/authorization.py**
```python
from platform.auth.config import RBACConfig

# RBAC Configuration for Donor Management Domain
RBAC_CONFIG = RBACConfig(
    # Policy store configuration
    policy_store_type="azure_blob",
    policy_store_connection_string="DefaultEndpointsProtocol=https;...",
    
    # Caching configuration
    cache_enabled=True,
    cache_ttl=300,  # 5 minutes
    cache_max_size=10000,
    
    # Permission hierarchy
    permission_hierarchy={
        "donor.admin": ["donor.read", "donor.write", "donor.delete", "donor.analytics"],
        "finance.admin": ["finance.read", "finance.write", "finance.report"],
        "system.admin": ["*"]  # Wildcard for all permissions
    },
    
    # Default role permissions
    default_permissions={
        "donor_analyst": ["donor.read", "donor.analytics"],
        "donor_manager": ["donor.read", "donor.write", "donor.analytics"],
        "finance_analyst": ["finance.read", "finance.report"],
        "admin": ["donor.admin", "finance.admin"]
    }
)
```

## 🚀 Basic Authorization Patterns

### Permission-Based Authorization

```python
from platform.auth import requires_permission, get_current_user

# Single permission check
@requires_permission("donor.read")
def get_donor(donor_id: str) -> dict:
    """Get donor information - requires donor.read permission"""
    user = get_current_user()
    return donor_service.get_by_id(donor_id)

# Multiple permissions (ALL required)
@requires_permission(["donor.read", "finance.read"])
def get_donor_financial_summary(donor_id: str) -> dict:
    """Get donor financial summary - requires both donor.read and finance.read"""
    return financial_service.get_donor_summary(donor_id)
```

### Role-Based Authorization

```python
from platform.auth import requires_role, requires_any_role

# Single role check
@requires_role("donor_analyst")
def get_donor_analytics() -> dict:
    """Get donor analytics - requires donor_analyst role"""
    return analytics_service.get_donor_metrics()

# Multiple roles (ANY required)
@requires_any_role(["donor_analyst", "donor_manager", "admin"])
def get_donor_list() -> list:
    """Get donor list - requires any of the specified roles"""
    return donor_service.list_all()
```

### Combined Permission and Role Checks

```python
from platform.auth import requires_permission, requires_role

# Combined check - must have role AND permission
@requires_role("donor_manager")
@requires_permission("donor.analytics")
def get_advanced_donor_analytics() -> dict:
    """Advanced analytics requiring both role and specific permission"""
    return advanced_analytics_service.get_comprehensive_metrics()
```

## 🎯 Advanced Authorization Scenarios

### Permission Hierarchy

```python
from platform.auth import requires_permission

# This will work because donor.admin includes donor.read
@requires_permission("donor.read")
def get_donor_basic_info(donor_id: str) -> dict:
    """Get basic donor info - accessible with donor.read or donor.admin"""
    return donor_service.get_basic_info(donor_id)

# This requires the specific admin permission
@requires_permission("donor.admin")
def delete_donor(donor_id: str) -> bool:
    """Delete donor - requires donor.admin permission"""
    return donor_service.delete(donor_id)
```

### Dynamic Permission Checks

```python
from platform.auth import check_permission, check_any_permission, get_user_permissions

def get_donor_data_with_dynamic_check(donor_id: str, include_sensitive: bool = False) -> dict:
    """Get donor data with dynamic permission checks"""
    
    # Always check basic read permission
    if not check_permission("donor.read"):
        raise PermissionError("donor.read permission required")
    
    donor_data = donor_service.get_by_id(donor_id)
    
    # Check for sensitive data access
    if include_sensitive and not check_permission("donor.sensitive.read"):
        donor_data.pop("ssn", None)
        donor_data.pop("financial_details", None)
    
    return donor_data
```

### Custom Permission Logic

```python
from platform.auth import get_current_user, check_permission

def get_donor_portfolio(donor_id: str) -> dict:
    """Get donor portfolio with custom authorization logic"""
    user = get_current_user()
    
    # Check if user is accessing their own data
    if user.user_id == donor_id:
        # Allow users to access their own portfolio
        return donor_service.get_portfolio(donor_id)
    
    # For other users, require specific permission
    if check_permission("donor.portfolio.read"):
        return donor_service.get_portfolio(donor_id)
    
    # Check if user is in the same department
    if user.department == donor_service.get_department(donor_id):
        return donor_service.get_portfolio(donor_id)
    
    raise PermissionError("Access denied to donor portfolio")
```

## 🏢 Domain-Specific Examples

### Donor Management Domain

```python
from platform.auth import requires_permission, requires_role
from platform.telemetry import telemetry
from platform.audit import audit_log

class DonorService:
    
    @requires_permission("donor.read")
    @telemetry("GetDonor")
    @audit_log("DONOR_READ")
    def get_donor(self, donor_id: str) -> dict:
        """Get donor information with full framework integration"""
        return self._donor_repository.get_by_id(donor_id)
    
    @requires_permission("donor.write")
    @telemetry("UpdateDonor")
    @audit_log("DONOR_UPDATE")
    def update_donor(self, donor_id: str, data: dict) -> dict:
        """Update donor information"""
        return self._donor_repository.update(donor_id, data)
    
    @requires_permission("donor.delete")
    @telemetry("DeleteDonor")
    @audit_log("DONOR_DELETE")
    def delete_donor(self, donor_id: str) -> bool:
        """Delete donor record"""
        return self._donor_repository.delete(donor_id)
    
    @requires_role("donor_analyst")
    @telemetry("GetDonorAnalytics")
    def get_analytics(self, donor_id: str) -> dict:
        """Get donor analytics - role-based access"""
        return self._analytics_service.get_donor_metrics(donor_id)
```

### Finance Domain

```python
from platform.auth import requires_permission, requires_any_permission
from platform.classification import classification

class FinanceService:
    
    @requires_permission("finance.read")
    @classification("CONFIDENTIAL")
    def get_financial_report(self, report_id: str) -> dict:
        """Get financial report - confidential data"""
        return self._report_repository.get_by_id(report_id)
    
    @requires_any_permission(["finance.admin", "finance.report"])
    @classification("INTERNAL")
    def generate_financial_report(self, parameters: dict) -> dict:
        """Generate financial report"""
        return self._report_service.generate(parameters)
    
    @requires_permission("finance.admin")
    @classification("STRICTLY_CONFIDENTIAL")
    def get_budget_forecast(self) -> dict:
        """Get budget forecast - strictly confidential"""
        return self._forecast_service.get_current_forecast()
```

## 🔗 Integration with Other Modules

### Authorization + Authentication

```python
from platform.auth import authenticated_tool, requires_permission

# Combined authentication and authorization
@authenticated_tool
@requires_permission("donor.read")
def get_donor_tool(donor_id: str) -> dict:
    """MCP tool with both authentication and authorization"""
    return donor_service.get_by_id(donor_id)
```

### Authorization + Telemetry + Audit

```python
from platform.auth import requires_permission
from platform.telemetry import telemetry
from platform.audit import audit_log

@requires_permission("donor.analytics")
@telemetry("GetDonorPortfolioHealth")
@audit_log("DONOR_ANALYTICS_ACCESS")
def get_donor_portfolio_health(donor_id: str) -> dict:
    """Get donor portfolio health with full framework integration"""
    return analytics_service.get_portfolio_health(donor_id)
```

### Authorization + Data Classification

```python
from platform.auth import requires_permission
from platform.classification import classification

@requires_permission("finance.sensitive.read")
@classification("STRICTLY_CONFIDENTIAL")
def get_financial_details(donor_id: str) -> dict:
    """Get sensitive financial details with classification"""
    return finance_service.get_donor_financials(donor_id)
```

## 🧪 Testing Authorization

### Unit Tests

```python
import pytest
from unittest.mock import patch, MagicMock
from platform.auth import requires_permission, check_permission
from platform.auth.exceptions import PermissionDeniedError

class TestAuthorization:
    
    @patch('platform.auth.get_current_user')
    def test_requires_permission_granted(self, mock_get_user):
        """Test that permission check passes with valid permission"""
        mock_get_user.return_value = MagicMock(permissions=["donor.read"])
        
        @requires_permission("donor.read")
        def test_function():
            return "success"
        
        result = test_function()
        assert result == "success"
    
    @patch('platform.auth.get_current_user')
    def test_requires_permission_denied(self, mock_get_user):
        """Test that permission check fails without valid permission"""
        mock_get_user.return_value = MagicMock(permissions=["other.permission"])
        
        @requires_permission("donor.read")
        def test_function():
            return "should not reach here"
        
        with pytest.raises(PermissionDeniedError):
            test_function()
    
    @patch('platform.auth.get_current_user')
    def test_requires_any_permission(self, mock_get_user):
        """Test that any permission check works with multiple permissions"""
        mock_get_user.return_value = MagicMock(permissions=["donor.read", "finance.read"])
        
        @requires_permission(["donor.read", "finance.read"])
        def test_function():
            return "success"
        
        result = test_function()
        assert result == "success"
```

### Integration Tests

```python
import pytest
from fastapi.testclient import TestClient
from main import app
from platform.auth import get_test_token

class TestAuthorizationIntegration:
    
    def test_authorization_endpoint_access(self):
        """Test endpoint access with different authorization levels"""
        client = TestClient(app)
        
        # Test with donor_analyst role
        token = get_test_token(roles=["donor_analyst"], permissions=["donor.read"])
        response = client.get(
            "/api/donors/123",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        # Test without required permission
        token = get_test_token(roles=["viewer"], permissions=[])
        response = client.get(
            "/api/donors/123",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403
        assert "Permission denied" in response.text
```

## ⭐ Best Practices

### ✅ DO's

1. **Use specific permissions** - Prefer `donor.read` over broad permissions like `donor.*`
2. **Leverage permission hierarchy** - Define clear permission hierarchies in your RBAC config
3. **Combine with other decorators** - Use authorization with telemetry, audit, and classification decorators
4. **Test thoroughly** - Write comprehensive tests for all authorization scenarios
5. **Use role-based for complex logic** - Use roles when permission logic becomes too complex

### ❌ DON'Ts

1. **Don't hardcode user checks** - Always use the framework's authorization decorators
2. **Don't bypass authorization** - Never use `check_permission(False)` or similar workarounds
3. **Don't use broad permissions** - Avoid wildcard permissions like `*` in production
4. **Don't cache authorization decisions** - Let the framework handle caching
5. **Don't mix business logic with auth** - Keep authorization separate from business logic

### 🔒 Security Considerations

1. **Always validate on server-side** - Never rely on client-side authorization checks
2. **Use HTTPS** - Ensure all authorization tokens are transmitted securely
3. **Rotate secrets regularly** - Regularly rotate RBAC configuration secrets
4. **Monitor access** - Use the audit logging to monitor authorization decisions
5. **Principle of least privilege** - Grant only the minimum permissions required

## 📚 Related Documentation

1. **[Authorization Module](../modules/authorization.md)** - Deep dive into authorization module
2. **[Authentication Examples](authentication.md)** - See authentication patterns
3. **[Security Best Practices](../best-practices/security.md)** - Follow security recommendations
4. **[Donor Management Example](donor-management.md)** - Complete domain example

## 🆘 Troubleshooting

### Common Issues

**Issue: Permission denied even with correct role**
```bash
# Check your RBAC configuration
python -c "from config.authorization import RBAC_CONFIG; print(RBAC_CONFIG.default_permissions)"

# Verify user permissions
python -c "from platform.auth import get_current_user; print(get_current_user().permissions)"
```

**Issue: Authorization decorators not working**
```bash
# Ensure decorators are imported correctly
# Check that @requires_permission is imported from platform.auth

# Verify decorator order - authentication should come before authorization
@authenticated_tool
@requires_permission("donor.read")
def my_function():
    pass
```

**Issue: Performance problems with authorization checks**
```bash
# Enable caching in RBAC configuration
RBAC_CONFIG = RBACConfig(
    cache_enabled=True,
    cache_ttl=300,
    cache_max_size=10000
)

# Monitor cache hit rate
from platform.auth.cache import get_cache_stats
print(get_cache_stats())
```

## 📞 Need help?

Check the [FAQ](../FAQ.md) or open an issue in the repository.