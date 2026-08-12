# 🛠️ Tool Development Guide

**Learn how to create MCP tools using the platform framework**

This guide provides comprehensive examples and best practices for developing tools in the MCP Platform Framework. Tools are the primary way domains expose their business capabilities to clients.

## 📋 Table of Contents

- [Tool Types](#-tool-types) - Different types of tools and when to use them
- [Basic Tool Development](#-basic-tool-development) - Creating your first tool
- [Tool Decorators](#-tool-decorators) - Using decorators for automatic integration
- [Tool Parameters](#-tool-parameters) - Defining and validating parameters
- [Tool Metadata](#-tool-metadata) - Adding rich metadata to tools
- [Error Handling in Tools](#-error-handling-in-tools) - Proper error handling patterns
- [Testing Tools](#-testing-tools) - Writing tests for your tools
- [Best Practices](#-best-practices) - Recommended patterns for tool development

## 🎯 Tool Types

The MCP Platform Framework supports four types of tools, each with specific use cases:

| Tool Type | Decorator | Use Case | Example |
|-----------|-----------|----------|---------|
| **FUNCTION** | `@tool` | General-purpose tools | `get_donor_info()` |
| **RESOURCE** | `@resource` | Data retrieval tools | `get_donor_data()` |
| **QUERY** | `@query` | Data query tools | `query_donors()` |
| **ACTION** | `@action` | Data modification tools | `update_donor()` |

### When to Use Each Type

- **FUNCTION**: Default tool type for general operations that don't fit the other categories
- **RESOURCE**: Use for tools that retrieve specific resources or entities
- **QUERY**: Use for tools that perform queries (filtering, searching, aggregating)
- **ACTION**: Use for tools that modify data or perform actions

## 🚀 Basic Tool Development

### Simple Tool Example

```python
from platform import tool

@tool(description="Get a simple greeting")
def say_hello(name: str = "World") -> dict:
    """Return a greeting message"""
    return {
        "message": f"Hello, {name}!",
        "timestamp": "2026-01-01T00:00:00Z"
    }
```

### Tool with Parameters

```python
from platform import tool

@tool(description="Calculate donor health score")
def calculate_donor_health(
    donor_id: str,
    time_period: str = "30d",
    include_projections: bool = False
) -> dict:
    """
    Calculate health score for a donor based on their activity
    
    Args:
        donor_id: The donor identifier
        time_period: Time period for calculation (7d, 30d, 90d, 1y)
        include_projections: Whether to include future projections
    
    Returns:
        Dictionary with health score and details
    """
    # Business logic here
    health_score = 85.5  # This would be calculated from actual data
    
    return {
        "donor_id": donor_id,
        "health_score": health_score,
        "time_period": time_period,
        "include_projections": include_projections,
        "status": "healthy" if health_score >= 70 else "at_risk"
    }
```

## 🏷️ Tool Decorators

The platform provides several decorators to enhance your tools with automatic functionality:

### Authentication Decorators

```python
from platform import tool
from platform.auth import authenticated_tool, requires_permission, requires_role

# Require authentication (default: requires authentication)
@tool(description="Get donor information")
@authenticated_tool
def get_donor_info(donor_id: str) -> dict:
    # Only authenticated users can access this tool
    pass

# Require specific permission
@tool(description="Update donor information")
@authenticated_tool
@requires_permission("donor.write")
def update_donor(donor_id: str, data: dict) -> bool:
    # Only users with "donor.write" permission can access this tool
    pass

# Require specific role
@tool(description="Admin operations")
@authenticated_tool
@requires_role("donor_admin")
def admin_operation() -> dict:
    # Only users with "donor_admin" role can access this tool
    pass

# Multiple requirements
@tool(description="Sensitive donor operation")
@authenticated_tool
@requires_permission("donor.write")
@requires_role("donor_manager")
def sensitive_operation(donor_id: str) -> dict:
    # Requires authentication, "donor.write" permission, AND "donor_manager" role
    pass
```

### Classification Decorators

```python
from platform import tool
from platform.classification import classification, classify_data

# Set tool classification level
@tool(description="Get donor financial data")
@classification("CONFIDENTIAL")
def get_donor_financial_data(donor_id: str) -> dict:
    # This tool handles confidential data
    pass

# Classify returned data
@tool(description="Get public donor list")
@classify_data("PUBLIC")
def get_public_donor_list() -> list:
    # Data returned by this tool is public
    pass

# Combined classification
@tool(description="Get donor portfolio")
@classification("CONFIDENTIAL")
@classify_data("INTERNAL")
def get_donor_portfolio(donor_id: str) -> dict:
    # Tool requires confidential access, returns internal data
    pass
```

### Telemetry and Audit Decorators

```python
from platform import tool
from platform.telemetry import track_tool_telemetry
from platform.audit import audit_tool_access, audit_data_access

# Automatic telemetry tracking
@tool(description="Get donor data")
@track_tool_telemetry
def get_donor_data(donor_id: str) -> dict:
    # Execution time, status, etc. are automatically tracked
    pass

# Automatic audit logging
@tool(description="Access sensitive donor data")
@audit_tool_access
def access_sensitive_data(donor_id: str) -> dict:
    # Access is automatically logged to audit storage
    pass

# Audit data access (for read operations)
@tool(description="Query donor information")
@audit_data_access
def query_donor_info(filter: str) -> list:
    # Data access is automatically logged
    pass
```

### Combined Decorators Example

```python
from platform import tool
from platform.auth import authenticated_tool, requires_permission
from platform.classification import classification
from platform.telemetry import track_tool_telemetry
from platform.audit import audit_tool_access

@tool(description="Get comprehensive donor portfolio health")
@authenticated_tool
@requires_permission("donor.health.read")
@classification("CONFIDENTIAL")
@track_tool_telemetry
@audit_tool_access
def get_donor_portfolio_health(donor_id: str) -> dict:
    """
    Get comprehensive health analysis for a donor's portfolio
    
    This tool:
    - Requires authentication
    - Requires "donor.health.read" permission
    - Handles confidential data
    - Tracks execution metrics
    - Logs access to audit storage
    """
    # Business logic here
    return {
        "donor_id": donor_id,
        "health_score": 85.5,
        "status": "healthy",
        "metrics": {
            "engagement": 0.85,
            "contribution_frequency": 0.92,
            "growth_potential": 0.78
        }
    }
```

## 📝 Tool Parameters

### Parameter Types and Validation

```python
from platform import tool
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field, validator

@tool(description="Advanced donor search")
def search_donors(
    # Basic types
    query: str,
    limit: int = 10,
    offset: int = 0,
    
    # Optional parameters
    donor_type: Optional[str] = None,
    status: Optional[str] = None,
    
    # List parameters
    tags: List[str] = [],
    regions: List[str] = [],
    
    # Date parameters
    created_after: Optional[date] = None,
    created_before: Optional[date] = None,
    
    # Boolean parameters
    include_inactive: bool = False,
    include_projections: bool = False,
    
    # Dictionary parameters
    filters: Dict[str, Any] = {},
    
    # Complex types
    date_range: Optional[Dict[str, date]] = None
) -> dict:
    """
    Search donors with advanced filtering options
    """
    # Parameter validation and processing
    if limit < 1 or limit > 100:
        raise ValueError("Limit must be between 1 and 100")
    
    if offset < 0:
        raise ValueError("Offset must be non-negative")
    
    # Business logic here
    return {
        "query": query,
        "results": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }
```

### Using Pydantic Models for Complex Parameters

```python
from platform import tool
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class DonorFilter(BaseModel):
    """Filter criteria for donor search"""
    min_contribution: Optional[float] = Field(None, gt=0, description="Minimum contribution amount")
    max_contribution: Optional[float] = Field(None, gt=0, description="Maximum contribution amount")
    status: Optional[str] = Field(None, description="Donor status filter")
    tags: List[str] = Field(default_factory=list, description="Tags to filter by")
    created_after: Optional[date] = Field(None, description="Created after date")
    created_before: Optional[date] = Field(None, description="Created before date")

class SortOptions(BaseModel):
    """Sorting options for results"""
    field: str = Field("created_at", description="Field to sort by")
    direction: str = Field("desc", description="Sort direction (asc/desc)")

@tool(description="Advanced donor search with complex parameters")
def advanced_donor_search(
    query: str,
    filters: Optional[DonorFilter] = None,
    sort: Optional[SortOptions] = None,
    limit: int = 10,
    offset: int = 0
) -> dict:
    """
    Search donors with complex filtering and sorting
    """
    # Use the validated Pydantic models
    filter_criteria = filters or DonorFilter()
    sort_options = sort or SortOptions()
    
    # Business logic here
    return {
        "query": query,
        "filters": filter_criteria.dict(),
        "sort": sort_options.dict(),
        "results": [],
        "total": 0
    }
```

## 📊 Tool Metadata

### Adding Rich Metadata

```python
from platform import tool
from platform.registration import ToolType

@tool(
    name="GetDonorPortfolioHealth",  # Explicit name (defaults to function name)
    description="Get comprehensive health analysis for a donor's portfolio",
    tool_type=ToolType.FUNCTION,  # Explicit tool type (defaults to FUNCTION)
    classification="CONFIDENTIAL",  # Data classification level
    requires_authentication=True,  # Require authentication (default: True)
    requires_authorization=True,  # Require authorization (default: True)
    timeout_seconds=60,  # Maximum execution time (default: 30)
    max_retries=3,  # Maximum number of retries (default: 3)
    rate_limit="100/hour",  # Rate limiting configuration
    owner="DonorManagement",  # Tool owner
    maintainer="donor-team@example.com",  # Tool maintainer
    sla="Gold",  # Service Level Agreement
    tags=["donor", "portfolio", "health", "analytics"],  # Tags for categorization
    categories=["Analytics", "Donor Management"]  # Categories for grouping
)
def get_donor_portfolio_health(donor_id: str) -> dict:
    """Get comprehensive health analysis for a donor's portfolio"""
    # Business logic here
    pass
```

### Tool Metadata from Function Signature

The framework automatically extracts metadata from the function:

```python
from platform import tool

@tool(description="Get donor information by ID")
def get_donor_info(
    donor_id: str,  # Parameter name, type, and default extracted
    include_details: bool = False,  # Optional parameter
    format: str = "json"  # Optional parameter with default
) -> dict:  # Return type extracted
    """
    Get information about a specific donor.
    
    This docstring becomes the tool description if not provided in decorator.
    """
    # Business logic here
    pass
```

## ❌ Error Handling in Tools

### Standard Error Handling

```python
from platform import tool
from platform.errors import MCPError, ErrorCategory

@tool(description="Get donor by ID")
def get_donor(donor_id: str) -> dict:
    """Get donor information by ID"""
    
    # Check if donor exists
    donor = find_donor_by_id(donor_id)
    
    if donor is None:
        # Raise standardized error
        raise MCPError(
            error_code="DONOR-001",
            category=ErrorCategory.DataAccess,
            message="Donor not found",
            details={"donor_id": donor_id},
            http_status=404
        )
    
    return donor
```

### Error Categories

```python
from platform.errors import ErrorCategory

# Available error categories:
ErrorCategory.DataAccess      # Data access errors (404, etc.)
ErrorCategory.Validation      # Input validation errors (400)
ErrorCategory.Authentication   # Authentication errors (401)
ErrorCategory.Authorization    # Authorization errors (403)
ErrorCategory.RateLimit       # Rate limiting errors (429)
ErrorCategory.Internal        # Internal server errors (500)
ErrorCategory.Timeout         # Timeout errors (504)
ErrorCategory.Conflict        # Conflict errors (409)
ErrorCategory.NotImplemented  # Not implemented (501)
```

### Custom Error Handling

```python
from platform import tool
from platform.errors import MCPError, ErrorCategory

class DonorError(MCPError):
    """Custom error class for donor-related errors"""
    
    def __init__(self, error_code: str, message: str, **kwargs):
        super().__init__(
            error_code=error_code,
            category=ErrorCategory.DataAccess,
            message=message,
            domain="DonorManagement",
            **kwargs
        )

@tool(description="Update donor information")
def update_donor(donor_id: str, data: dict) -> dict:
    """Update donor information"""
    
    # Validate input
    if not donor_id:
        raise DonorError(
            error_code="DONOR-002",
            message="Donor ID is required"
        )
    
    if not data:
        raise DonorError(
            error_code="DONOR-003",
            message="Update data is required"
        )
    
    # Check if donor exists
    donor = find_donor_by_id(donor_id)
    if donor is None:
        raise DonorError(
            error_code="DONOR-001",
            message="Donor not found",
            details={"donor_id": donor_id}
        )
    
    # Business logic here
    return update_donor_in_database(donor_id, data)
```

### Error Response Format

All errors are automatically formatted into a standardized response:

```json
{
  "error": {
    "error_code": "DONOR-001",
    "category": "DataAccess",
    "message": "Donor not found",
    "details": {
      "donor_id": "12345"
    },
    "timestamp": "2026-01-01T12:00:00Z",
    "request_id": "abc-123-def-456",
    "domain": "DonorManagement",
    "tool": "get_donor"
  },
  "status": "error",
  "status_code": 404
}
```

## 🧪 Testing Tools

### Unit Testing

```python
import pytest
from unittest.mock import patch, MagicMock
from tools.donor_tools import get_donor_info, DonorError

class TestDonorTools:
    """Unit tests for donor tools"""
    
    @patch('tools.donor_tools.find_donor_by_id')
    def test_get_donor_success(self, mock_find_donor):
        """Test successful donor retrieval"""
        # Setup mock
        mock_donor = {
            "donor_id": "12345",
            "name": "John Doe",
            "email": "john@example.com"
        }
        mock_find_donor.return_value = mock_donor
        
        # Execute
        result = get_donor_info(donor_id="12345")
        
        # Assert
        assert result == mock_donor
        mock_find_donor.assert_called_once_with("12345")
    
    @patch('tools.donor_tools.find_donor_by_id')
    def test_get_donor_not_found(self, mock_find_donor):
        """Test donor not found error"""
        # Setup mock
        mock_find_donor.return_value = None
        
        # Execute and assert exception
        with pytest.raises(DonorError) as exc_info:
            get_donor_info(donor_id="99999")
        
        # Assert error details
        assert exc_info.value.error_code == "DONOR-001"
        assert exc_info.value.category == "DataAccess"
        assert "Donor not found" in exc_info.value.message
        assert exc_info.value.details["donor_id"] == "99999"
    
    def test_get_donor_invalid_input(self):
        """Test invalid input validation"""
        # Test empty donor_id
        with pytest.raises(ValueError) as exc_info:
            get_donor_info(donor_id="")
        
        assert "Donor ID is required" in str(exc_info.value)
```

### Integration Testing

```python
import pytest
from platform.framework import get_framework
from tools.donor_tools import get_donor_info

class TestDonorToolsIntegration:
    """Integration tests for donor tools"""
    
    def test_tool_registration(self):
        """Test that tools are properly registered"""
        framework = get_framework()
        registry = framework.registry
        
        # Check if tool is registered
        tool_registration = registry.get_tool_by_name("get_donor_info")
        assert tool_registration is not None
        assert tool_registration.metadata.name == "get_donor_info"
        assert tool_registration.metadata.domain == "DonorManagement"
    
    def test_tool_metadata(self):
        """Test tool metadata is correct"""
        framework = get_framework()
        registry = framework.registry
        
        tool_registration = registry.get_tool_by_name("get_donor_info")
        metadata = tool_registration.metadata
        
        assert metadata.description == "Get donor information by ID"
        assert metadata.tool_type.value == "function"
        assert "donor_id" in metadata.parameters
        assert metadata.parameters["donor_id"].type == "str"
        assert metadata.parameters["donor_id"].required is True
```

### Mocking Fabric Connectivity

```python
import pytest
from unittest.mock import patch, MagicMock
from tools.donor_tools import get_donor_portfolio_health
from platform.connectivity import semantic_model

class TestFabricIntegration:
    """Tests for Fabric connectivity integration"""
    
    @patch('platform.connectivity.semantic_models.SemanticModelClient.execute')
    def test_semantic_model_integration(self, mock_execute):
        """Test integration with semantic models"""
        # Setup mock
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.data = [{"HealthScore": 85.5, "Status": "healthy"}]
        mock_result.error = None
        mock_execute.return_value = mock_result
        
        # Execute
        result = get_donor_portfolio_health(donor_id="12345")
        
        # Assert
        assert result["health_score"] == 85.5
        assert result["status"] == "healthy"
        
        # Check semantic model was called correctly
        mock_execute.assert_called_once()
        call_args = mock_execute.call_args
        assert "12345" in call_args[0][0]  # Query contains donor_id
```

## ⭐ Best Practices

### 1. **Use Semantic Models for Business Metrics**

⭐ **Best Practice**: Always use semantic models instead of direct table access for business metrics.

```python
# ✅ Good - Use semantic models
from platform.connectivity import semantic_model

@tool(description="Get donor portfolio health")
def get_donor_portfolio_health(donor_id: str) -> dict:
    query = f"EVALUATE DonorPortfolioHealth WHERE DonorID = {donor_id}"
    result = semantic_model.execute(query, model_id="DonorManagement")
    return result.data[0] if result.data else {}

# ❌ Bad - Direct table access
from platform.connectivity import warehouse

@tool(description="Get donor portfolio health")
def get_donor_portfolio_health(donor_id: str) -> dict:
    # Don't do this - bypasses semantic layer
    query = f"SELECT * FROM DonorPortfolio WHERE DonorID = {donor_id}"
    result = warehouse.execute(query)
    return result.data[0] if result.data else {}
```

### 2. **Always Use Decorators**

⭐ **Best Practice**: Use platform decorators for automatic integration.

```python
# ✅ Good - Full decorator usage
@tool(description="Get donor information")
@authenticated_tool
@requires_permission("donor.read")
@classification("CONFIDENTIAL")
@track_tool_telemetry
@audit_tool_access
def get_donor_info(donor_id: str) -> dict:
    pass

# ❌ Bad - Missing decorators
@tool(description="Get donor information")
def get_donor_info(donor_id: str) -> dict:
    # Missing authentication, authorization, classification, etc.
    pass
```

### 3. **Validate Input Parameters**

⭐ **Best Practice**: Always validate input parameters.

```python
# ✅ Good - Input validation
@tool(description="Update donor information")
def update_donor(donor_id: str, data: dict) -> dict:
    if not donor_id:
        raise ValueError("Donor ID is required")
    
    if not data:
        raise ValueError("Update data is required")
    
    if not isinstance(data, dict):
        raise TypeError("Update data must be a dictionary")
    
    # Business logic
    pass

# ❌ Bad - No input validation
@tool(description="Update donor information")
def update_donor(donor_id: str, data: dict) -> dict:
    # No validation - could cause errors or security issues
    pass
```

### 4. **Use Proper Error Handling**

⭐ **Best Practice**: Use standardized error handling.

```python
# ✅ Good - Standardized errors
from platform.errors import MCPError, ErrorCategory

@tool(description="Get donor by ID")
def get_donor(donor_id: str) -> dict:
    donor = find_donor_by_id(donor_id)
    
    if donor is None:
        raise MCPError(
            error_code="DONOR-001",
            category=ErrorCategory.DataAccess,
            message="Donor not found",
            details={"donor_id": donor_id},
            http_status=404
        )
    
    return donor

# ❌ Bad - Generic exceptions
@tool(description="Get donor by ID")
def get_donor(donor_id: str) -> dict:
    donor = find_donor_by_id(donor_id)
    
    if donor is None:
        raise ValueError("Donor not found")  # Generic error
    
    return donor
```

### 5. **Add Comprehensive Documentation**

⭐ **Best Practice**: Add detailed docstrings and metadata.

```python
# ✅ Good - Comprehensive documentation
@tool(
    description="Get comprehensive donor portfolio health analysis",
    tags=["donor", "portfolio", "health", "analytics"],
    categories=["Analytics", "Donor Management"]
)
def get_donor_portfolio_health(
    donor_id: str,
    time_period: str = "30d",
    include_projections: bool = False
) -> dict:
    """
    Get comprehensive health analysis for a donor's portfolio.
    
    This tool calculates a health score based on multiple factors including:
    - Contribution frequency and amount
    - Engagement level
    - Growth potential
    - Risk factors
    
    Args:
        donor_id: The unique identifier for the donor
        time_period: Time period for analysis (7d, 30d, 90d, 1y)
        include_projections: Whether to include future projections in the analysis
    
    Returns:
        Dictionary containing:
        - donor_id: The donor identifier
        - health_score: Numeric score (0-100)
        - status: Health status (healthy, at_risk, poor)
        - metrics: Detailed health metrics
        - timestamp: Analysis timestamp
    
    Raises:
        MCPError: If donor is not found (DONOR-001)
        ValueError: If invalid time_period is provided
    
    Example:
        >>> get_donor_portfolio_health("12345", time_period="90d")
        {
            'donor_id': '12345',
            'health_score': 85.5,
            'status': 'healthy',
            'metrics': {...},
            'timestamp': '2026-01-01T12:00:00Z'
        }
    """
    # Business logic here
    pass

# ❌ Bad - Minimal documentation
@tool(description="Get donor health")
def get_donor_health(donor_id: str) -> dict:
    pass
```

### 6. **Use Type Hints**

⭐ **Best Practice**: Always use type hints for better IDE support and validation.

```python
# ✅ Good - Full type hints
from typing import Optional, List, Dict, Any
from datetime import datetime, date

@tool(description="Search donors")
def search_donors(
    query: str,
    limit: int = 10,
    offset: int = 0,
    filters: Optional[Dict[str, Any]] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "desc"
) -> Dict[str, Any]:
    pass

# ❌ Bad - No type hints
@tool(description="Search donors")
def search_donors(query, limit=10, offset=0, filters=None, sort_by=None, sort_order="desc"):
    pass
```

### 7. **Keep Tools Focused**

⭐ **Best Practice**: Each tool should do one thing well.

```python
# ✅ Good - Focused tools
@tool(description="Get donor basic information")
def get_donor_basic_info(donor_id: str) -> dict:
    # Only gets basic info
    pass

@tool(description="Get donor financial information")
def get_donor_financial_info(donor_id: str) -> dict:
    # Only gets financial info
    pass

@tool(description="Get donor portfolio health")
def get_donor_portfolio_health(donor_id: str) -> dict:
    # Only calculates health score
    pass

# ❌ Bad - Monolithic tool
@tool(description="Get all donor information")
def get_donor_everything(donor_id: str) -> dict:
    # Does everything - hard to maintain, test, and understand
    pass
```

### 8. **Use Pydantic for Complex Parameters**

⭐ **Best Practice**: Use Pydantic models for complex parameter validation.

```python
# ✅ Good - Pydantic models for complex parameters
from pydantic import BaseModel, Field
from typing import Optional, List

class DonorSearchCriteria(BaseModel):
    min_contribution: Optional[float] = Field(None, gt=0)
    max_contribution: Optional[float] = Field(None, gt=0)
    status: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    created_after: Optional[date] = None

@tool(description="Search donors with complex criteria")
def search_donors(criteria: DonorSearchCriteria) -> list:
    # criteria is automatically validated
    pass

# ❌ Bad - Manual validation
@tool(description="Search donors")
def search_donors(
    min_contribution=None,
    max_contribution=None,
    status=None,
    tags=None,
    created_after=None
) -> list:
    # Manual validation required
    if min_contribution is not None and min_contribution <= 0:
        raise ValueError("min_contribution must be positive")
    # ... more manual validation
    pass
```

## 📚 Quick Reference

### Tool Decorator Summary

| Decorator | Purpose | Example |
|-----------|---------|---------|
| `@tool` | Register a tool | `@tool(description="Get info")` |
| `@resource` | Register a resource tool | `@resource(description="Get data")` |
| `@query` | Register a query tool | `@query(description="Query data")` |
| `@action` | Register an action tool | `@action(description="Update data")` |
| `@authenticated_tool` | Require authentication | `@authenticated_tool` |
| `@requires_permission` | Require permission | `@requires_permission("read")` |
| `@requires_role` | Require role | `@requires_role("admin")` |
| `@classification` | Set classification | `@classification("CONFIDENTIAL")` |
| `@classify_data` | Classify returned data | `@classify_data("INTERNAL")` |
| `@track_tool_telemetry` | Track execution | `@track_tool_telemetry` |
| `@audit_tool_access` | Audit access | `@audit_tool_access` |
| `@audit_data_access` | Audit data access | `@audit_data_access` |

### Error Category Summary

| Category | HTTP Status | Use Case |
|----------|-------------|----------|
| `DataAccess` | 404 | Resource not found |
| `Validation` | 400 | Invalid input |
| `Authentication` | 401 | Authentication failed |
| `Authorization` | 403 | Permission denied |
| `RateLimit` | 429 | Too many requests |
| `Internal` | 500 | Server error |
| `Timeout` | 504 | Request timeout |
| `Conflict` | 409 | Resource conflict |
| `NotImplemented` | 501 | Feature not implemented |

### Classification Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| `PUBLIC` | Publicly accessible data | Public reports, general information |
| `INTERNAL` | Internal business data | Departmental data, internal metrics |
| `CONFIDENTIAL` | Sensitive business data | Donor information, financial data |
| `STRICTLY_CONFIDENTIAL` | Highly sensitive data | Personal data, legal documents |

---

## 🎯 Next Steps

- **[Semantic Model Access](semantic-models.md)** - Learn how to query Power BI semantic models
- **[Warehouse Queries](warehouse-queries.md)** - Execute SQL queries against Fabric warehouses
- **[Lakehouse Operations](lakehouse-operations.md)** - Work with Fabric lakehouses
- **[Authentication Examples](authentication.md)** - See authentication patterns
- **[Authorization Examples](authorization.md)** - See authorization patterns

---

**🛠️ You're now ready to develop powerful MCP tools!**

- **Need more examples?** Check out the [Examples](../README.md) section
- **Have questions?** See the [FAQ](../FAQ.md)
- **Found an issue?** Open a bug report
- **Have feedback?** Open a discussion
