# 🏢 Donor Management Domain Example

## Overview

Complete example of a **Donor Management Domain** using the MCP Platform Framework, demonstrating domain structure, tool development, Fabric integration, authentication, and telemetry.

## 🎯 Domain Structure

```
mcp-donor-management/
├── tools/                    # MCP tools
│   ├── donor_crud.py         # Create, Read, Update, Delete
│   ├── donor_analytics.py    # Analytics and reporting
│   ├── donor_pipeline.py     # Pipeline management
│   └── donor_scoring.py      # Donor scoring
├── semantic_models/          # Fabric semantic models
├── tests/                    # Domain tests
├── config/                   # Environment configs
├── metadata/                 # Domain metadata
└── platform_framework/        # Platform (git submodule)
```

## 📋 Domain Metadata

**metadata/domain.json**
```json
{
  "name": "DonorManagement",
  "display_name": "Donor Management",
  "description": "Domain for managing donor relationships, analytics, and portfolio health",
  "version": "1.0.0",
  "owner": "DER",
  "team": "Fundraising",
  "classification": "CONFIDENTIAL",
  "sla": "Gold",
  "tags": ["donor", "fundraising", "analytics", "portfolio"]
}
```

## 🛠️ Tool Implementation

### CRUD Tools Example

**tools/donor_crud.py**
```python
from typing import Dict, Any
from mcp_framework.platform import MCPFramework
from mcp_framework.auth import authenticated_tool, requires_permission
from mcp_framework.telemetry import track_tool_execution
from mcp_framework.classification import classification
from mcp_framework.audit import audit_log
from mcp_framework.fabric import SemanticModelClient
from mcp_framework.error_handling import MCPError, ErrorCodes

framework = MCPFramework()
fabric_client = SemanticModelClient(workspace_id=framework.config.get("fabric.workspace_id"))

@authenticated_tool
@requires_permission("donor.read")
@classification("CONFIDENTIAL")
@track_tool_execution
@audit_log(action="donor.read")
def GetDonor(donor_id: str) -> Dict[str, Any]:
    """Retrieve donor information by ID"""
    try:
        query = f"EVALUATE VAR DonorData = FILTER(DonorTable, DonorTable[DonorID] = \"{donor_id}\") RETURN GENERATE(DonorData, ALL)"
        result = fabric_client.execute(query, model_id="DonorModel")
        
        if not result:
            raise MCPError(error_code=ErrorCodes.DONOR_NOT_FOUND, message=f"Donor {donor_id} not found", category="DataNotFound")
        
        return {"status": "success", "donor": result[0]}
    except Exception as e:
        raise MCPError(error_code=ErrorCodes.DONOR_ACCESS_ERROR, message=str(e), category="DataAccess")

framework.register_tools([GetDonor])
```

### Analytics Tools Example

**tools/donor_analytics.py**
```python
from typing import Dict, Any, List
from datetime import datetime, timedelta
from mcp_framework.platform import MCPFramework
from mcp_framework.auth import authenticated_tool, requires_permission
from mcp_framework.telemetry import track_tool_execution
from mcp_framework.classification import classification
from mcp_framework.audit import audit_log
from mcp_framework.fabric import SemanticModelClient

framework = MCPFramework()
fabric_client = SemanticModelClient(workspace_id=framework.config.get("fabric.workspace_id"))

@authenticated_tool
@requires_permission("donor.analytics")
@classification("CONFIDENTIAL")
@track_tool_execution
@audit_log(action="donor.analytics")
def GetDonorPortfolioHealth(donor_id: str) -> Dict[str, Any]:
    """Calculate donor portfolio health score"""
    try:
        # Get donor data
        donor = GetDonor(donor_id)
        contributions = GetDonorContributionHistory(donor_id)
        
        # Calculate health metrics
        health_score = calculate_health_score(contributions)
        health_category = get_health_category(health_score)
        
        return {
            "status": "success",
            "donor_id": donor_id,
            "health_score": round(health_score, 2),
            "health_category": health_category,
            "recommendations": get_recommendations(health_score)
        }
    except Exception as e:
        framework.logger.error(f"Error calculating portfolio health: {str(e)}")
        raise

def calculate_health_score(contributions: Dict[str, Any]) -> float:
    """Calculate health score based on contribution patterns"""
    # Implementation logic here
    return 85.5  # Example score

def get_health_category(score: float) -> str:
    """Convert score to category"""
    if score >= 90: return "Excellent"
    elif score >= 80: return "Very Good"
    elif score >= 70: return "Good"
    elif score >= 60: return "Fair"
    elif score >= 50: return "Poor"
    else: return "Critical"

def get_recommendations(score: float) -> List[str]:
    """Generate recommendations based on score"""
    if score < 70:
        return ["Schedule donor interview", "Review engagement strategy"]
    else:
        return ["Maintain regular contact", "Explore giving opportunities"]

framework.register_tools([GetDonorPortfolioHealth])
```

## 📊 Domain Testing

**tests/test_donor_tools.py**
```python
import pytest
from unittest.mock import patch, MagicMock
from mcp_framework.testing import MCPTestClient
from tools.donor_crud import GetDonor

@pytest.fixture
def client():
    return MCPTestClient()

@pytest.fixture
def mock_fabric_client():
    with patch('tools.donor_crud.SemanticModelClient') as mock:
        client = MagicMock()
        client.execute.return_value = [{"DonorID": "D001", "Name": "Test Donor"}]
        mock.return_value = client
        yield client

def test_get_donor_success(client, mock_fabric_client):
    result = GetDonor("D001")
    assert result["status"] == "success"
    assert result["donor"]["DonorID"] == "D001"

def test_get_donor_not_found(client):
    with patch('tools.donor_crud.fabric_client.execute') as mock_execute:
        mock_execute.return_value = []
        with pytest.raises(Exception):  # Should raise MCPError
            GetDonor("D999")
```

## 🚀 Deployment

### Domain Configuration

**config/development.json**
```json
{
  "environment": "development",
  "domain": "DonorManagement",
  "debug": true,
  "log_level": "DEBUG",
  "azure": {
    "subscription_id": "dev-subscription-id",
    "resource_group": "mcp-donor-dev-rg",
    "location": "eastus"
  },
  "fabric": {
    "tenant_id": "dev-tenant-id",
    "workspace_id": "dev-workspace-id",
    "semantic_models": {
      "DonorModel": "DonorManagementModel"
    }
  }
}
```

### Project Configuration

**pyproject.toml**
```toml
[project]
name = "mcp-donor-management"
version = "1.0.0"
description = "MCP Domain for Donor Management"
requires-python = ">=3.11"
dependencies = [
    "mcp-platform-framework>=1.0.0",
    "azure-identity>=1.15.0",
    "azure-keyvault-secrets>=4.5.0"
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

## 📚 Best Practices

1. **⭐ Follow Domain Separation** - Keep business logic in domain
2. **⭐ Use Semantic Models** - Access data through models, not direct tables
3. **⭐ Implement Proper Error Handling** - Use MCPError with custom codes
4. **⭐ Secure All Tools** - Always use authentication and authorization decorators
5. **⭐ Classify Data** - Apply appropriate classification to all tools
6. **⭐ Monitor Performance** - Use telemetry and audit logging

## 🛠️ Troubleshooting

### Tool Registration Failed
**Error**: `Tool 'GetDonor' already registered`
**Solution**: Register all tools in one place to avoid duplicates

### Semantic Model Connection Failed
**Error**: `Authentication failed`
**Solution**: Verify Azure authentication and Key Vault permissions

### Permission Denied
**Error**: `User does not have required permission 'donor.read'`
**Solution**: Assign appropriate role to user or service principal

## 📚 Next Steps

1. **[Tool Development Guide](tool-development.md)** - Learn tool development
2. **[Semantic Model Access](semantic-models.md)** - Fabric integration
3. **[Deployment Guide](../deployment/overview.md)** - Deploy your domain
4. **[Best Practices](../best-practices/README.md)** - Follow recommended patterns

---

**Need help?** Check the [FAQ](../FAQ.md) or open an issue in the repository.
