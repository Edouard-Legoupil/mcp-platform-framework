# 🏗️ Creating New Domains

Step-by-step guide to creating new MCP domain repositories using the MCP Platform Framework template system.

## 🎯 Overview

This guide provides detailed instructions for creating new MCP domains using the template system. Whether you're creating your first domain or your hundredth, this guide will walk you through the process from start to finish.

## 🚀 Quick Start

### Create a Domain in 5 Minutes

```bash
# 1. Create the domain
python -m platform.template.template_generator \
    --domain DonorManagement \
    --description "Domain for managing donor information and portfolios" \
    --owner DER \
    --classification CONFIDENTIAL

# 2. Navigate to the domain
cd mcp-donor-management

# 3. Install dependencies
pip install -r requirements.txt

# 4. Test locally
python main.py

# 5. Start developing tools
# Edit files in the tools/ directory
```

That's it! You now have a fully functional MCP domain with all the framework capabilities built-in.

## 📋 Step-by-Step Domain Creation

### Step 1: Plan Your Domain

Before creating a domain, take some time to plan:

#### Domain Design Considerations

✅ **Single Responsibility**: Each domain should have a single, well-defined responsibility
✅ **Clear Boundaries**: Define what data and operations belong to this domain
✅ **Minimal Dependencies**: Minimize dependencies on other domains
✅ **Consistent Naming**: Use consistent naming conventions

**Example Domain Responsibilities:**

| Domain | Responsibility | Example Tools |
|--------|---------------|---------------|
| DonorManagement | Manage donor information and relationships | GetDonor, UpdateDonor, SearchDonors |
| Finance | Manage financial data and reporting | GetFinancialReport, CalculateBudget, ProcessPayment |
| CampaignManagement | Manage fundraising campaigns | GetCampaign, UpdateCampaignStatus, CalculateCampaignROI |
| SupplyChain | Manage supply chain operations | GetInventory, ProcessOrder, TrackShipment |

#### Domain Naming Conventions

✅ **Use PascalCase**: `DonorManagement`, `Finance`, `CampaignAnalytics`
✅ **Be Descriptive**: Clearly indicate the domain's purpose
✅ **Be Concise**: Keep names reasonably short
✅ **Avoid Acronyms**: Unless widely understood in your organization

❌ **Avoid**: `DM`, `Fin`, `Campaign`, `SCM`
✅ **Use**: `DonorManagement`, `Finance`, `CampaignManagement`, `SupplyChainManagement`

### Step 2: Gather Required Information

You'll need the following information to create a domain:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `domain` | Domain name (PascalCase) | `DonorManagement` |
| `description` | Domain description | "Domain for managing donor information and portfolios" |
| `owner` | Owning team/department | `DER` |
| `classification` | Default data classification | `CONFIDENTIAL` |
| `environment` | Default environment | `dev` |
| `output` | Output directory | `./mcp-donor-management` |

### Step 3: Create the Domain

#### Command Line Method

```bash
# Basic domain creation
python -m platform.template.template_generator \
    --domain DonorManagement \
    --description "Domain for managing donor information and portfolios" \
    --owner DER \
    --classification CONFIDENTIAL

# With additional parameters
python -m platform.template.template_generator \
    --domain DonorManagement \
    --description "Domain for managing donor information and portfolios" \
    --owner DER \
    --classification CONFIDENTIAL \
    --environment dev \
    --output ./mcp-donor-management \
    --include-examples true
```

#### Interactive Method

```bash
# Start interactive mode
python -m platform.template.template_generator

# Or explicitly
python -m platform.template.template_generator --interactive

# Example interactive session:
$ python -m platform.template.template_generator

MCP Domain Template Generator
==============================

Enter domain name [DonorManagement]: DonorManagement
Enter domain description: Domain for managing donor information and portfolios

Select owner:
  1. DER
  2. Finance
  3. HR
  4. IT
  5. Operations
Select (1-5) [1]: 1

Select default classification:
  1. PUBLIC
  2. INTERNAL
  3. CONFIDENTIAL
  4. STRICTLY_CONFIDENTIAL
Select (1-4) [3]: 3

Select default environment:
  1. dev
  2. test
  3. prod
Select (1-3) [1]: 1

Include example tools and code? (y/n) [y]: y
Output directory [./mcp-donor-management]: 

Generating domain...
✓ Domain created successfully at ./mcp-donor-management
```

#### Programmatic Method

```python
from platform.template.template_generator import TemplateGenerator

# Create generator
generator = TemplateGenerator()

# Define parameters
parameters = {
    "domain": "DonorManagement",
    "description": "Domain for managing donor information and portfolios",
    "owner": "DER",
    "classification": "CONFIDENTIAL",
    "environment": "dev",
    "output": "./mcp-donor-management",
    "include_examples": True
}

# Generate domain
result = await generator.generate_domain(**parameters)

if result.success:
    print(f"Domain created successfully at {result.path}")
else:
    print(f"Error creating domain: {result.error}")
```

### Step 4: Verify the Generated Domain

After generation, verify that the domain was created correctly:

```bash
# Navigate to the domain
cd mcp-donor-management

# Check the structure
find . -type f | head -20

# Expected output:
./tools/__init__.py
./tools/donor_tools.py
./semantic_models/__init__.py
./semantic_models/models.py
./tests/unit/__init__.py
./tests/integration/__init__.py
./tests/conftest.py
./docs/README.md
./config/domain.yaml
./config/authentication.yaml
./config/authorization.yaml
./config/telemetry.yaml
./config/audit.yaml
./config/fabric.yaml
./metadata/catalog.json
./metadata/governance.json
./pipelines/azure-devops.yml
./platform_framework/__init__.py
./main.py
./requirements.txt
./pyproject.toml
./README.md
```

### Step 5: Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# For development, you might also want:
pip install -r requirements-dev.txt

# Verify installation
python -c "from platform.framework import MCPFramework; print('Framework installed successfully')"
```

### Step 6: Configure the Domain

Edit the configuration files to match your specific requirements:

```bash
# Edit domain configuration
nano config/domain.yaml

# Edit authentication configuration
nano config/authentication.yaml

# Edit authorization configuration
nano config/authorization.yaml

# Edit other configurations as needed
```

**Example domain.yaml:**
```yaml
domain:
  name: DonorManagement
  description: Domain for managing donor information and portfolios
  owner: DER
  classification: CONFIDENTIAL
  environment: dev
  version: 1.0.0

tool_discovery:
  enabled: true
  modules:
    - tools

security:
  authentication_required: true
  default_classification: CONFIDENTIAL

performance:
  max_concurrent_requests: 100
  request_timeout: 30

monitoring:
  telemetry_enabled: true
  audit_enabled: true
```

### Step 7: Test the Domain Locally

```bash
# Run the domain locally
python main.py

# Expected output:
Starting MCP Domain: DonorManagement
Environment: dev
Framework initialized successfully
Tool discovery: Found 0 tools
Server running on http://localhost:8000

# Test with curl
curl http://localhost:8000/health

# Expected response:
{"status": "healthy", "domain": "DonorManagement", "version": "1.0.0"}
```

### Step 8: Develop Your Tools

Now you're ready to start developing your domain-specific tools:

```bash
# Edit the tools file
nano tools/donor_tools.py

# Or create a new tools file
nano tools/campaign_tools.py
```

**Example Tool Implementation:**
```python
# tools/donor_tools.py
from platform_framework import (
    authenticated_tool,
    requires_permission,
    track_tool_telemetry,
    audit_tool_access,
    classification,
    handle_errors,
    tool
)
from platform.connectivity import FabricClient

# Initialize Fabric client
fabric = FabricClient()

@tool(
    name="GetDonorPortfolio",
    description="Retrieve comprehensive donor portfolio information",
    classification="CONFIDENTIAL"
)
@authenticated_tool
@requires_permission("donor.read")
@track_tool_telemetry
@audit_tool_access(classification="CONFIDENTIAL")
@classification("CONFIDENTIAL")
@handle_errors
async def get_donor_portfolio(donor_id: str) -> dict:
    """
    Retrieve comprehensive donor portfolio information.
    
    Args:
        donor_id: The ID of the donor to retrieve
        
    Returns:
        Dictionary containing donor portfolio information
    """
    # Get semantic model
    semantic_model = fabric.get_semantic_model("DonorAnalytics")
    
    # Execute query
    results = await semantic_model.execute(
        f'EVALUATE FILTER(Donors, Donors[DonorID] = "{donor_id}")'
    )
    
    if not results or not results.rows:
        raise DataAccessError("DATA_001", "Donor not found", donor_id=donor_id)
    
    # Process results
    portfolio = process_portfolio_results(results.rows[0])
    
    return portfolio

def process_portfolio_results(row: dict) -> dict:
    """Process raw portfolio results into a structured format."""
    return {
        "donor_id": row.get("DonorID"),
        "name": row.get("DonorName"),
        "total_contribution": row.get("TotalContribution"),
        "portfolio_value": row.get("PortfolioValue"),
        "risk_score": row.get("RiskScore"),
        "last_updated": row.get("LastUpdated")
    }
```

### Step 9: Test Your Tools

```bash
# Run unit tests
pytest tests/unit/ -v

# Run integration tests
pytest tests/integration/ -v

# Run all tests
pytest -v

# Test specific tool
python -c "
import asyncio
from tools.donor_tools import get_donor_portfolio

async def test_tool():
    try:
        result = await get_donor_portfolio('12345')
        print('Tool result:', result)
    except Exception as e:
        print('Tool error:', e)

asyncio.run(test_tool())
"
```

### Step 10: Deploy the Domain

```bash
# Deploy to Azure Function App
az functionapp deployment source config-zip \
    --resource-group mcp-platform-rg \
    --name mcp-donor-management-dev \
    --src .

# Check deployment status
az functionapp show \
    --resource-group mcp-platform-rg \
    --name mcp-donor-management-dev \
    --query state

# Test the deployed function
curl https://mcp-donor-management-dev.azurewebsites.net/api/health
```

## 📁 Domain Structure Overview

The generated domain has the following structure:

```
mcp-donor-management/
├── tools/                    # MCP tool implementations
│   ├── __init__.py          # Tool module initialization
│   └── donor_tools.py       # Example domain-specific tools
├── semantic_models/          # Semantic model access
│   ├── __init__.py          # Semantic model module initialization
│   └── models.py            # Semantic model definitions
├── tests/                    # Test suite
│   ├── unit/                # Unit tests
│   │   └── __init__.py
│   ├── integration/         # Integration tests
│   │   └── __init__.py
│   └── conftest.py           # Test fixtures and configuration
├── docs/                     # Domain-specific documentation
│   ├── README.md            # Domain README
│   └── api-reference.md      # API reference
├── config/                   # Configuration files
│   ├── domain.yaml          # Domain configuration
│   ├── authentication.yaml  # Authentication configuration
│   ├── authorization.yaml   # Authorization configuration
│   ├── telemetry.yaml       # Telemetry configuration
│   ├── audit.yaml           # Audit configuration
│   └── fabric.yaml          # Fabric configuration
├── metadata/                 # Domain metadata
│   ├── catalog.json         # Catalog registration metadata
│   └── governance.json      # Governance and compliance metadata
├── pipelines/                # CI/CD pipeline definitions
│   └── azure-devops.yml      # Azure DevOps pipeline
├── platform_framework/       # Platform framework integration
│   └── __init__.py          # Framework initialization
├── main.py                   # Azure Function entry point
├── requirements.txt          # Python dependencies
├── pyproject.toml           # Project configuration
└── README.md                 # Domain-specific README
```

## 🔧 Domain Configuration

### Configuration Files

Every domain includes several configuration files:

| File | Purpose | Required |
|------|---------|----------|
| `config/domain.yaml` | Domain-specific configuration | ✅ Yes |
| `config/authentication.yaml` | Authentication settings | ✅ Yes |
| `config/authorization.yaml` | Authorization settings | ✅ Yes |
| `config/telemetry.yaml` | Telemetry settings | ✅ Yes |
| `config/audit.yaml` | Audit logging settings | ✅ Yes |
| `config/fabric.yaml` | Fabric connectivity settings | ✅ Yes |

### Environment Configuration

Configure different settings for different environments:

```yaml
# config/domain.yaml
environments:
  dev:
    debug: true
    log_level: DEBUG
    cache_enabled: false
    
  test:
    debug: false
    log_level: INFO
    cache_enabled: true
    
  prod:
    debug: false
    log_level: WARNING
    cache_enabled: true
    performance_monitoring: true
```

### Configuration Management

Use environment variables for sensitive configuration:

```bash
# Set environment variables
export MCP_DOMAIN=DonorManagement
export MCP_ENVIRONMENT=dev
export AZURE_TENANT_ID=your-tenant-id
export AZURE_CLIENT_ID=your-client-id

# Or use a .env file
cat > .env << EOF
MCP_DOMAIN=DonorManagement
MCP_ENVIRONMENT=dev
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
EOF
```

## 🛠️ Domain Development Workflow

### Local Development

```bash
# 1. Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run locally
python main.py

# 4. Test tools
pytest tests/ -v

# 5. Make changes and repeat
```

### Using the Development Server

```bash
# Start development server
python main.py --debug

# Test with HTTP requests
curl http://localhost:8000/api/tools

# Test specific tool
curl -X POST http://localhost:8000/api/tools/GetDonorPortfolio \
  -H "Content-Type: application/json" \
  -d '{"donor_id": "12345"}'
```

### Debugging

```bash
# Run with debug logging
python main.py --log-level DEBUG

# Use Python debugger
python -m pdb main.py

# Or use breakpoints in your code
import pdb; pdb.set_trace()
```

## 📊 Domain Testing

### Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── test_tools.py        # Tool unit tests
│   ├── test_services.py     # Service unit tests
│   └── ...
├── integration/            # Integration tests
│   ├── test_fabric.py      # Fabric integration tests
│   ├── test_database.py    # Database integration tests
│   └── ...
├── performance/            # Performance tests
│   ├── test_load.py         # Load tests
│   └── test_concurrency.py # Concurrency tests
├── security/               # Security tests
│   ├── test_auth.py        # Authentication tests
│   └── test_validation.py  # Input validation tests
└── conftest.py             # Shared test fixtures
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_tools.py

# Run specific test function
pytest tests/unit/test_tools.py::test_get_donor_portfolio

# Run with coverage
pytest --cov=tools --cov-report=html

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run with specific markers
pytest -m "unit and donor"
```

### Test Configuration

```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
def mock_fabric_client():
    """Mock Fabric client for testing."""
    with patch('platform.connectivity.FabricClient') as mock_client:
        mock_semantic_model = AsyncMock()
        mock_semantic_model.execute.return_value = {
            "rows": [{"DonorID": "123", "DonorName": "Test Donor"}]
        }
        mock_client.return_value.get_semantic_model.return_value = mock_semantic_model
        yield mock_client

@pytest.fixture
def test_donor_data():
    """Test donor data."""
    return {
        "DonorID": "123",
        "DonorName": "Test Donor",
        "TotalContribution": 10000.0,
        "PortfolioValue": 50000.0,
        "RiskScore": 2.5
    }

@pytest.fixture
async def donor_service():
    """Test donor service."""
    from tools.donor_tools import DonorService
    return DonorService()
```

## 🚀 Domain Deployment

### Deployment Options

| Method | Description | Best For |
|--------|-------------|----------|
| Azure CLI | Command line deployment | Quick testing, automation |
| Azure Portal | Web-based deployment | Manual deployments |
| Azure DevOps | CI/CD pipeline | Production deployments |
| GitHub Actions | CI/CD pipeline | Open source, GitHub users |

### Azure CLI Deployment

```bash
# Create resource group
az group create \
    --name mcp-platform-rg \
    --location eastus

# Create storage account for deployment
az storage account create \
    --name mcpdeploymentsa \
    --resource-group mcp-platform-rg \
    --location eastus \
    --sku Standard_LRS

# Deploy Function App
az functionapp create \
    --name mcp-donor-management-dev \
    --resource-group mcp-platform-rg \
    --consumption-plan-location eastus \
    --runtime python \
    --runtime-version 3.11 \
    --functions-version 4 \
    --storage-account mcpdeploymentsa \
    --os-type Linux

# Deploy code
az functionapp deployment source config-zip \
    --resource-group mcp-platform-rg \
    --name mcp-donor-management-dev \
    --src .

# Check deployment status
az functionapp show \
    --resource-group mcp-platform-rg \
    --name mcp-donor-management-dev \
    --query state
```

### Azure DevOps Deployment

The template includes a sample Azure DevOps pipeline:

```yaml
# pipelines/azure-devops.yml
trigger:
  branches:
    include:
      - main
      - releases/*
  paths:
    exclude:
      - docs/*
      - README.md

variables:
  python.version: '3.11'
  azureSubscription: 'mcp-platform-subscription'
  functionAppName: 'mcp-donor-management-$(Environment)'
  resourceGroup: 'mcp-platform-rg'

stages:
- stage: Build
  displayName: Build stage
  jobs:
  - job: Build
    displayName: Build
    pool:
      vmImage: 'ubuntu-latest'
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '$(python.version)'
    
    - script: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov
      displayName: 'Install dependencies'
    
    - script: |
        pytest tests/ --cov=tools --cov-report=xml
      displayName: 'Run tests'
    
    - task: PublishTestResults@2
      condition: succeededOrFailed()
      inputs:
        testResultsFormat: 'JUnit'
        testResultsFiles: '**/test-results.xml'
    
    - task: PublishCodeCoverageResults@1
      inputs:
        codeCoverageTool: Cobertura
        summaryFileLocation: '$(System.DefaultWorkingDirectory)/**/coverage.xml'

- stage: Deploy
  displayName: Deploy stage
  dependsOn: Build
  condition: succeeded()
  jobs:
  - deployment: Deploy
    displayName: Deploy
    environment: '$(Environment)'
    pool:
      vmImage: 'ubuntu-latest'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '$(python.version)'
          
          - script: |
              python -m pip install --upgrade pip
              pip install -r requirements.txt
            displayName: 'Install dependencies'
          
          - task: AzureFunctionApp@1
            displayName: 'Deploy Azure Function'
            inputs:
              azureSubscription: '$(azureSubscription)'
              appType: 'functionAppLinux'
              appName: '$(functionAppName)'
              deployToSlotOrASE: false
              resourceGroupName: '$(resourceGroup)'
              package: '.'
              runtimeStack: 'PYTHON'
              runtimeVersion: '3.11'
              startUpCommand: 'gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app'
```

## 📝 Domain Documentation

### README.md

Every domain should have a comprehensive README.md file:

```markdown
# DonorManagement Domain

## Overview

The DonorManagement domain provides MCP tools for managing donor information, portfolios, and relationships. This domain is owned by the DER team and handles all donor-related operations.

## Features

- **Donor Information**: Retrieve and update donor details
- **Portfolio Management**: Manage donor portfolios and investments
- **Relationship Tracking**: Track donor relationships and interactions
- **Analytics**: Generate donor analytics and reports

## Tools

| Tool | Description | Classification |
|------|-------------|----------------|
| GetDonor | Retrieve donor information | CONFIDENTIAL |
| UpdateDonor | Update donor information | CONFIDENTIAL |
| GetDonorPortfolio | Retrieve donor portfolio | CONFIDENTIAL |
| GetDonorAnalytics | Generate donor analytics | CONFIDENTIAL |

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python main.py

# Test tools
pytest tests/ -v
```

### Deployment

```bash
# Deploy to Azure
az functionapp deployment source config-zip \
    --resource-group mcp-platform-rg \
    --name mcp-donor-management-dev \
    --src .
```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| MCP_DOMAIN | Domain name | Yes | DonorManagement |
| MCP_ENVIRONMENT | Environment | Yes | dev |
| AZURE_TENANT_ID | Azure tenant ID | Yes | - |
| AZURE_CLIENT_ID | Azure client ID | Yes | - |

### Configuration Files

- `config/domain.yaml` - Domain configuration
- `config/authentication.yaml` - Authentication settings
- `config/authorization.yaml` - Authorization settings
- `config/telemetry.yaml` - Telemetry settings
- `config/audit.yaml` - Audit settings
- `config/fabric.yaml` - Fabric settings

## Security

### Authentication

This domain requires authentication. All tools are protected with the `@authenticated_tool` decorator.

### Authorization

Tools require specific permissions:

- `donor.read` - Read donor information
- `donor.write` - Update donor information
- `donor.analytics` - Access donor analytics

### Data Classification

All data in this domain is classified as CONFIDENTIAL by default.

## Monitoring

This domain includes comprehensive monitoring:

- **Telemetry**: Automatic Application Insights integration
- **Audit Logging**: Compliance logging for sensitive operations
- **Error Tracking**: Comprehensive error tracking and reporting

## Support

For issues or questions, contact the DER team.

## License

This domain is licensed under the MIT License.
```

### API Reference

Document all your tools in the API reference:

```markdown
# DonorManagement API Reference

## Tools

### GetDonor

Retrieve donor information.

**Endpoint**: `POST /api/tools/GetDonor`

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| donor_id | string | Yes | The ID of the donor to retrieve |

**Returns**:

```json
{
  "donor_id": "string",
  "name": "string",
  "email": "string",
  "phone": "string",
  "address": "object",
  "status": "string",
  "created_date": "string",
  "last_updated": "string"
}
```

**Example**:

```bash
curl -X POST https://mcp-donor-management-dev.azurewebsites.net/api/tools/GetDonor \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"donor_id": "12345"}'
```

**Response**:

```json
{
  "donor_id": "12345",
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1-555-123-4567",
  "address": {
    "street": "123 Main St",
    "city": "New York",
    "state": "NY",
    "zip": "10001",
    "country": "USA"
  },
  "status": "active",
  "created_date": "2024-01-15T10:30:00Z",
  "last_updated": "2024-06-20T14:45:00Z"
}
```

### UpdateDonor

Update donor information.

**Endpoint**: `POST /api/tools/UpdateDonor`

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| donor_id | string | Yes | The ID of the donor to update |
| data | object | Yes | The donor data to update |

**Returns**:

```json
{
  "success": true,
  "donor_id": "string",
  "message": "string"
}
```

**Example**:

```bash
curl -X POST https://mcp-donor-management-dev.azurewebsites.net/api/tools/UpdateDonor \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "donor_id": "12345",
    "data": {
      "name": "John Doe",
      "email": "john.doe.new@example.com",
      "phone": "+1-555-987-6543"
    }
  }'
```
```

## 🔍 Troubleshooting

### Common Issues

**Domain generation fails**
- Verify all required parameters are provided
- Check that the output directory doesn't already exist
- Ensure you have write permissions in the target directory
- Check for syntax errors in template files

**Domain doesn't start locally**
- Verify all dependencies are installed (`pip install -r requirements.txt`)
- Check that all required environment variables are set
- Ensure there are no syntax errors in your code
- Check the logs for error messages

**Tools aren't discovered**
- Verify that tools are decorated with `@tool` decorator
- Check that tools are in the correct directory (tools/)
- Ensure there are no syntax errors in the tool files
- Check that the tool module is imported in tools/__init__.py

**Authentication fails**
- Verify that authentication is properly configured
- Check that the required environment variables are set
- Ensure the token is valid and not expired
- Check the token audience and issuer

**Authorization fails**
- Verify that the caller has the required permissions
- Check that the role-permission mapping is correct
- Ensure the caller identity is properly extracted
- Check that the authorization decorators are applied

**Fabric connectivity fails**
- Verify that the workspace ID is correct
- Check that the Fabric endpoints are accessible
- Ensure authentication is properly configured
- Check that the service principal has the required permissions

### Debugging Tips

**Enable debug logging:**
```bash
python main.py --log-level DEBUG
```

**Check Application Insights:**
- View telemetry in the Azure portal
- Check for exceptions and errors
- Review request logs and traces

**Test individual components:**
```python
# Test authentication
python -c "
from platform.auth import AuthenticationService
import asyncio

async def test():
    service = AuthenticationService()
    result = await service.validate_token('your-token')
    print('Token valid:', result.is_valid)

asyncio.run(test())
"

# Test Fabric connectivity
python -c "
from platform.connectivity import FabricClient
import asyncio

async def test():
    client = FabricClient()
    semantic_model = client.get_semantic_model('DonorAnalytics')
    results = await semantic_model.execute('EVALUATE Donors')
    print('Results:', results)

asyncio.run(test())
"
```

## 📚 Related Documentation

- [Template System Overview](overview.md) - Template architecture and components
- [Template Configuration](configuration.md) - Template customization and configuration
- [Domain Structure](structure.md) - Standard domain repository structure
- [Getting Started](../getting-started/README.md) - General getting started guide
- [API Reference](../api-reference/README.md) - Framework API documentation

---

**🎉 Ready to create your first domain?** Follow this step-by-step guide to create a new MCP domain with all the framework capabilities built-in.

**Need more details?** Check out the [Template System Overview](overview.md) for a deeper understanding of how the template system works.