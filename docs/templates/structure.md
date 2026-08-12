# 🏗️ Domain Structure Guide

## Overview

This guide describes the standard structure for MCP Platform Framework domains, ensuring consistency across all domain implementations and facilitating integration with the platform.

## 🎯 Standard Domain Structure

Every MCP domain follows this standard structure:

```
mcp-xxx-domain/                    # Domain repository root
├── .github/                      # GitHub workflows (optional)
│   └── workflows/                # CI/CD workflows
│       ├── build.yml
│       ├── deploy.yml
│       └── test.yml
│
├── azure-pipelines/              # Azure DevOps pipelines (optional)
│   ├── build.yml
│   ├── deploy.yml
│   └── templates/
│
├── config/                       # Configuration files
│   ├── default.json              # Default configuration
│   ├── development.json          # Development environment
│   ├── test.json                 # Test environment
│   ├── staging.json              # Staging environment
│   └── production.json           # Production environment
│
├── docs/                         # Domain documentation
│   ├── README.md                 # Domain overview
│   ├── api-reference.md          # API documentation
│   ├── architecture.md           # Architecture decisions
│   └── examples.md               # Usage examples
│
├── metadata/                     # Domain metadata
│   ├── domain.json               # Domain metadata
│   ├── catalog.json              # Catalog registration
│   ├── compliance.json           # Compliance information
│   └── governance.json           # Governance policies
│
├── semantic_models/              # Semantic model definitions
│   ├── model1.json               # Semantic model 1
│   ├── model2.json               # Semantic model 2
│   └── README.md                 # Model documentation
│
├── tests/                        # Domain tests
│   ├── __init__.py
│   ├── conftest.py               # Pytest fixtures
│   ├── integration/              # Integration tests
│   │   ├── __init__.py
│   │   └── test_*.py
│   ├── unit/                     # Unit tests
│   │   ├── __init__.py
│   │   └── test_*.py
│   └── security/                 # Security tests
│       ├── __init__.py
│       └── test_*.py
│
├── tools/                        # MCP tools
│   ├── __init__.py               # Tool exports
│   ├── tool_category1/           # Tool category
│   │   ├── __init__.py
│   │   └── *.py
│   └── tool_category2/           # Another tool category
│       ├── __init__.py
│       └── *.py
│
├── platform_framework/           # Platform framework (git submodule)
│   └── ...
│
├── .gitignore                    # Git ignore patterns
├── .gitleaks.toml                # Secret scanning config
├── CHANGELOG.md                  # Change log
├── LICENSE                       # License file
├── pyproject.toml                # Project configuration
├── README.md                     # Project README
└── requirements.txt              # Python dependencies
```

## 📁 Directory Descriptions

### 📂 Root Directory

**Purpose**: Contains project-wide configuration and documentation files.

**Key Files:**

- **`.gitignore`** - Specifies files and directories to ignore in version control
- **`.gitleaks.toml`** - Configuration for secret scanning
- **`CHANGELOG.md`** - Records all notable changes to the domain
- **`LICENSE`** - License file (typically MIT or Apache 2.0)
- **`pyproject.toml`** - Project metadata and build configuration
- **`README.md`** - Project overview and setup instructions
- **`requirements.txt`** - Python dependencies for the domain

### 📂 config/

**Purpose**: Contains environment-specific configuration files.

**Structure:**
```
config/
├── default.json              # Shared defaults across all environments
├── development.json          # Development environment configuration
├── test.json                 # Test environment configuration
├── staging.json              # Staging environment configuration
└── production.json           # Production environment configuration
```

**Configuration Hierarchy:**
1. Environment-specific file (e.g., `production.json`)
2. Default configuration (`default.json`)
3. Environment variables
4. Framework defaults

### 📂 docs/

**Purpose**: Contains domain-specific documentation.

**Structure:**
```
docs/
├── README.md                 # Domain overview and getting started
├── api-reference.md          # API documentation for domain tools
├── architecture.md           # Architecture decisions and patterns
├── examples.md               # Usage examples and code snippets
├── best-practices.md         # Domain-specific best practices
└── troubleshooting.md        # Common issues and solutions
```

### 📂 metadata/

**Purpose**: Contains domain metadata for registration, compliance, and governance.

**Key Files:**

- **`domain.json`** - Core domain metadata
- **`catalog.json`** - Catalog registration information
- **`compliance.json`** - Compliance requirements and standards
- **`governance.json`** - Governance policies and procedures

**Example domain.json:**
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
  "tags": ["donor", "fundraising", "analytics"],
  "dependencies": ["Fabric", "KeyVault", "ApplicationInsights"],
  "contact": "donor-team@domain.com",
  "documentation": "https://docs.domain.com/donor-management"
}
```

### 📂 semantic_models/

**Purpose**: Contains semantic model definitions for Microsoft Fabric integration.

**Structure:**
```
semantic_models/
├── README.md                 # Semantic model documentation
├── donor_model.json           # Donor semantic model
├── campaign_model.json        # Campaign semantic model
└── financial_model.json       # Financial semantic model
```

**Semantic Model File Structure:**
```json
{
  "name": "DonorManagementModel",
  "displayName": "Donor Management Model",
  "description": "Semantic model for donor data and analytics",
  "tables": [
    {
      "name": "DonorTable",
      "displayName": "Donors",
      "description": "Donor information and demographics",
      "columns": [
        {
          "name": "DonorID",
          "displayName": "Donor ID",
          "dataType": "string",
          "isPrimaryKey": true
        },
        {
          "name": "DonorName",
          "displayName": "Donor Name",
          "dataType": "string"
        }
      ]
    }
  ],
  "relationships": [
    {
      "name": "Donor_Contributions",
      "from": "DonorTable",
      "to": "ContributionTable",
      "fromColumn": "DonorID",
      "toColumn": "DonorID"
    }
  ],
  "measures": [
    {
      "name": "TotalDonors",
      "displayName": "Total Donors",
      "expression": "COUNTROWS(DonorTable)"
    }
  ]
}
```

### 📂 tests/

**Purpose**: Contains all domain tests organized by type.

**Structure:**
```
tests/
├── __init__.py               # Test package initialization
├── conftest.py               # Pytest fixtures and configuration
├── integration/              # Integration tests
│   ├── __init__.py
│   ├── test_donor_analytics.py
│   └── test_fabric_integration.py
├── security/                 # Security tests
│   ├── __init__.py
│   ├── test_authentication.py
│   └── test_authorization.py
└── unit/                     # Unit tests
    ├── __init__.py
    ├── test_donor_crud.py
    └── test_donor_scoring.py
```

### 📂 tools/

**Purpose**: Contains all MCP tools organized by functionality.

**Structure:**
```
tools/
├── __init__.py               # Tool package initialization and exports
├── analytics/                # Analytics tools
│   ├── __init__.py
│   ├── donor_analytics.py
│   └── portfolio_analytics.py
├── crud/                     # CRUD operations
│   ├── __init__.py
│   ├── donor_crud.py
│   └── campaign_crud.py
├── pipeline/                 # Pipeline management tools
│   ├── __init__.py
│   └── donor_pipeline.py
└── scoring/                  # Scoring tools
    ├── __init__.py
    └── donor_scoring.py
```

**Tool File Structure:**
```python
"""
Module description

This module provides [functionality] for the [Domain] domain.
"""

from typing import Dict, Any, List, Optional
from mcp_framework.platform import MCPFramework
from mcp_framework.auth import authenticated_tool, requires_permission
from mcp_framework.telemetry import track_tool_execution
from mcp_framework.classification import classification
from mcp_framework.audit import audit_log
from mcp_framework.fabric import SemanticModelClient
from mcp_framework.error_handling import MCPError, ErrorCodes

# Initialize framework
framework = MCPFramework()

# Initialize clients and services
fabric_client = SemanticModelClient(
    workspace_id=framework.config.get("fabric.workspace_id")
)

# Define tools
@authenticated_tool
@requires_permission("domain.permission")
@classification("CONFIDENTIAL")
@track_tool_execution
@audit_log(action="domain.action")
def ToolName(param1: str, param2: int = 10) -> Dict[str, Any]:
    """
    Tool description
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter (default: 10)
        
    Returns:
        Dictionary containing the tool results
        
    Raises:
        MCPError: If an error occurs during tool execution
        
    Examples:
        >>> ToolName("test", 5)
        {'status': 'success', 'result': 'test - 5'}
    """
    try:
        # Tool implementation
        result = {
            "status": "success",
            "param1": param1,
            "param2": param2
        }
        return result
    except Exception as e:
        framework.logger.error(f"Error in ToolName: {str(e)}")
        raise MCPError(
            error_code=ErrorCodes.TOOL_EXECUTION_FAILED,
            message=f"Tool execution failed: {str(e)}",
            category="ToolError"
        )

# Register tools
framework.register_tools([ToolName])
```

## 📄 File Templates

### pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "mcp-xxx-domain"
version = "1.0.0"
description = "MCP Domain for [Domain Name]"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.11"
authors = [
    {name = "Your Organization", email = "team@domain.com"}
]
keywords = ["mcp", "domain-name", "business-capability"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
]
dependencies = [
    "mcp-platform-framework>=1.0.0",
    "azure-identity>=1.15.0",
    "azure-keyvault-secrets>=4.5.0",
    "azure-monitor-opentelemetry>=1.0.0",
    "opentelemetry-api>=1.20.0",
    "opentelemetry-sdk>=1.20.0",
    "pydantic>=2.5.0",
]

[project.optional-dependencies]
dev = [
    "black>=24.0.0",
    "flake8>=6.1.0",
    "isort>=5.13.0",
    "mypy>=1.8.0",
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.11.0",
]

[project.urls]
Homepage = "https://github.com/your-org/mcp-xxx-domain"
Documentation = "https://docs.domain.com/xxx-domain"
Repository = "https://github.com/your-org/mcp-xxx-domain"
Issues = "https://github.com/your-org/mcp-xxx-domain/issues"

[tool.setuptools.packages.find]
where = ["."]
include = ["mcp_xxx_domain*"]

[tool.black]
line-length = 120
target-version = ["py311", "py312"]

[tool.isort]
profile = "black"
line_length = 120

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --tb=short"

[tool.coverage.run]
source = ["tools", "semantic_models"]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:"
]
```

### requirements.txt

```
# MCP Platform Framework
mcp-platform-framework>=1.0.0

# Azure Dependencies
azure-identity>=1.15.0
azure-keyvault-secrets>=4.5.0
azure-monitor-opentelemetry>=1.0.0

# OpenTelemetry
opentelemetry-api>=1.20.0
opentelemetry-sdk>=1.20.0
opentelemetry-exporter-otlp>=1.20.0

# Data Processing
pandas>=2.1.0
numpy>=1.26.0

# Type Checking
pydantic>=2.5.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0

# Code Quality
black>=24.0.0
flake8>=6.1.0
isort>=5.13.0
mypy>=1.8.0
```

### .gitignore

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/
.venv/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.nox/

# Type checking
.mypy_cache/

# Environment
.env
.env.local
.env.*.local

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# Project specific
platform_framework/  # This is a git submodule
```

## 🏗️ Domain Creation Process

### Step 1: Create Repository

```bash
# Create new repository from template
gh repo create mcp-xxx-domain --template your-org/mcp-platform-template --private

# Or clone the template
git clone https://github.com/your-org/mcp-platform-template.git mcp-xxx-domain
cd mcp-xxx-domain

# Remove template git history
rm -rf .git

# Initialize new git repository
git init
git add .
git commit -m "Initial commit from MCP Platform Template"

# Create new repository on GitHub
gh repo create mcp-xxx-domain --private --push
```

### Step 2: Configure Domain

```bash
# Update domain metadata
# Edit metadata/domain.json with your domain information

# Update project configuration
# Edit pyproject.toml with your domain name and details

# Update documentation
# Edit README.md and docs/ with your domain-specific content

# Update configuration
# Edit config/*.json with your environment-specific settings
```

### Step 3: Add Platform Framework

```bash
# Add platform framework as git submodule
git submodule add https://github.com/your-org/mcp-platform-framework.git platform_framework

# Initialize and update submodule
git submodule update --init --recursive

# Commit submodule
git add platform_framework
git commit -m "Add MCP Platform Framework as submodule"
```

### Step 4: Develop Domain Tools

```bash
# Create tools directory
mkdir -p tools/analytics tools/crud tools/pipeline

# Create __init__.py files
touch tools/__init__.py tools/analytics/__init__.py tools/crud/__init__.py tools/pipeline/__init__.py

# Create your first tool
cat > tools/crud/__init__.py << 'EOF'
from .donor_crud import GetDonor, CreateDonor, UpdateDonor, DeleteDonor

__all__ = ["GetDonor", "CreateDonor", "UpdateDonor", "DeleteDonor"]
EOF
```

### Step 5: Add Tests

```bash
# Create test directory structure
mkdir -p tests/unit tests/integration tests/security

# Create __init__.py files
touch tests/__init__.py tests/unit/__init__.py tests/integration/__init__.py tests/security/__init__.py

# Create conftest.py for fixtures
cat > tests/conftest.py << 'EOF'
import pytest
from unittest.mock import patch
from mcp_framework.platform import MCPFramework

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    with patch.dict('os.environ', {
        'MCP_ENVIRONMENT': 'test',
        'AZURE_SUBSCRIPTION_ID': 'test-subscription-id'
    }):
        framework = MCPFramework()
        yield framework
EOF
```

### Step 6: Configure CI/CD

```bash
# Create GitHub Actions workflows
mkdir -p .github/workflows

# Create build workflow
cat > .github/workflows/build.yml << 'EOF'
name: Build and Test

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - run: pip install -r requirements.txt
    - run: pip install -e .
    - run: pytest tests/unit
EOF

# Create deploy workflow
cat > .github/workflows/deploy.yml << 'EOF'
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - run: pip install -r requirements.txt
    - run: pip install -e .
    - run: echo "Deploy to development"
EOF
```

## 📋 Naming Conventions

### Repository Naming

- **Format**: `mcp-[domain-name]-domain`
- **Examples**:
  - `mcp-donor-management-domain`
  - `mcp-financial-reporting-domain`
  - `mcp-supply-chain-domain`

### Domain Naming

- **Format**: PascalCase
- **Examples**:
  - `DonorManagement`
  - `FinancialReporting`
  - `SupplyChain`

### Tool Naming

- **Format**: PascalCase verbs
- **Examples**:
  - `GetDonorPipeline`
  - `CalculateDonorScore`
  - `UpdateCampaignStatus`
  - `DeleteFinancialRecord`

### File Naming

- **Python files**: snake_case.py
- **Configuration files**: kebab-case.json
- **Documentation files**: kebab-case.md
- **Test files**: test_*.py

### Variable Naming

- **Python variables**: snake_case
- **Configuration keys**: kebab-case
- **Environment variables**: SCREAMING_SNAKE_CASE

## 🛡️ Security Requirements

### Repository Security

1. **Private Repositories**: All domain repositories must be private
2. **Branch Protection**: Main branch must have protection rules
3. **Code Owners**: Define CODEOWNERS for critical files
4. **Secret Scanning**: Enable secret scanning on all repositories
5. **Dependency Scanning**: Enable dependency vulnerability scanning

### Code Security

1. **No Hardcoded Secrets**: Never commit secrets to version control
2. **Environment Variables**: Use environment variables for configuration
3. **Key Vault Integration**: Use Azure Key Vault for all secrets
4. **Input Validation**: Validate all tool inputs
5. **Error Handling**: Never expose sensitive information in errors

### Access Control

1. **Least Privilege**: Grant minimum required permissions
2. **Service Principals**: Use dedicated service principals for each domain
3. **Managed Identity**: Use Managed Identity where possible
4. **Access Reviews**: Regularly review and audit access

## 📊 Quality Standards

### Code Quality

1. **Type Hints**: All functions must have type hints
2. **Docstrings**: All public functions must have docstrings
3. **Code Formatting**: Use black for code formatting
4. **Import Sorting**: Use isort for import sorting
5. **Linting**: Use flake8 for linting
6. **Type Checking**: Use mypy for type checking

### Testing

1. **Unit Tests**: All functions must have unit tests
2. **Integration Tests**: Test integration with external services
3. **Security Tests**: Test for security vulnerabilities
4. **Test Coverage**: Minimum 80% code coverage
5. **CI/CD Testing**: All tests must pass in CI/CD

### Documentation

1. **README**: Every repository must have a README
2. **API Documentation**: Document all public APIs
3. **Examples**: Provide usage examples
4. **Architecture**: Document architecture decisions
5. **Changelog**: Maintain a changelog

## 🔄 Versioning

### Semantic Versioning

Follow [Semantic Versioning 2.0.0](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: Backwards-compatible new features
- **PATCH**: Backwards-compatible bug fixes

### Version Files

1. **pyproject.toml**: Package version
2. **metadata/domain.json**: Domain version
3. **CHANGELOG.md**: Version history

### Version Updates

```bash
# Update version in pyproject.toml
# Update version in metadata/domain.json
# Update CHANGELOG.md

# Create version tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

## 📦 Dependency Management

### Dependency Principles

1. **Minimal Dependencies**: Only include necessary dependencies
2. **Version Pinning**: Pin all dependencies to specific versions
3. **Security Updates**: Regularly update dependencies for security fixes
4. **Compatibility**: Ensure all dependencies are compatible
5. **Testing**: Test with all supported dependency versions

### Dependency Files

1. **requirements.txt**: Production dependencies
2. **requirements-dev.txt**: Development dependencies
3. **pyproject.toml**: Package dependencies and metadata

### Dependency Updates

```bash
# Update dependencies
pip install --upgrade package-name

# Update requirements.txt
pip freeze > requirements.txt

# Test with updated dependencies
pytest tests/

# Commit dependency updates
git add requirements.txt
git commit -m "Update dependencies"
```

## 🌐 Integration with Platform

### Platform Framework Integration

1. **Git Submodule**: Add platform framework as git submodule
2. **Version Compatibility**: Ensure compatibility with platform version
3. **API Usage**: Use platform APIs for cross-cutting concerns
4. **Configuration**: Follow platform configuration patterns

### Catalog Registration

1. **Metadata**: Provide complete metadata in metadata/catalog.json
2. **Registration**: Register domain with enterprise catalog
3. **Discovery**: Ensure domain is discoverable by other services
4. **Documentation**: Document integration points

### Monitoring and Observability

1. **Telemetry**: Implement telemetry for all tools
2. **Logging**: Use structured logging
3. **Metrics**: Track key performance metrics
4. **Alerts**: Configure alerts for critical issues

## 🛠️ Best Practices

### Domain Development Best Practices

1. **⭐ Follow Domain Separation Principle**
   - Keep business logic in the domain
   - Use platform for cross-cutting concerns
   - Avoid duplicating platform functionality

2. **⭐ Implement Proper Error Handling**
   - Use MCPError for domain-specific errors
   - Define custom error codes
   - Provide meaningful error messages

3. **⭐ Use Semantic Models**
   - Access data through semantic models
   - Use DAX for complex queries
   - Implement caching where appropriate

4. **⭐ Secure All Tools**
   - Always use authentication decorators
   - Implement proper authorization checks
   - Classify all tools appropriately

5. **⭐ Monitor Performance**
   - Track tool execution times
   - Monitor error rates
   - Set up alerts for issues

6. **⭐ Document Thoroughly**
   - Document all tools and APIs
   - Provide usage examples
   - Document architecture decisions

## 🛠️ Troubleshooting

### Common Structure Issues

#### Missing Required Files

**Error**: `ModuleNotFoundError: No module named 'mcp_xxx_domain'`

**Solution**:
```bash
# Ensure __init__.py files exist in all directories
find . -type d -name "tools" -exec touch {}/__init__.py \;
find . -type d -name "tests" -exec touch {}/__init__.py \;
```

#### Incorrect Package Structure

**Error**: `Package directory does not contain __init__.py`

**Solution**:
```bash
# Create __init__.py files in all package directories
touch tools/__init__.py
```

#### Dependency Conflicts

**Error**: `ImportError: cannot import name 'X' from 'Y'`

**Solution**:
```bash
# Check dependency versions
pip list | grep package-name

# Update dependencies
pip install --upgrade package-name

# Or pin to a specific version
pip install package-name==1.2.3
```

#### Configuration Not Found

**Error**: `Configuration file not found: config/development.json`

**Solution**:
```bash
# Create the missing configuration file
mkdir -p config
touch config/development.json

# Or specify a different environment
MCP_ENVIRONMENT=production python your_script.py
```

## 📚 Next Steps

1. **[Creating Domains Guide](creating-domains.md)** - Step-by-step domain creation
2. **[Template Overview](overview.md)** - Understand the template system
3. **[Template Configuration](configuration.md)** - Configure your domain template
4. **[API Reference](../api-reference/README.md)** - Explore available APIs

## 🔗 Related Documentation

- [MCP Platform Framework Documentation](../README.md)
- [GitHub Repository Templates](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository)
- [Python Packaging Guide](https://packaging.python.org/en/latest/)
- [Semantic Versioning](https://semver.org/)

---

**Need help?** Check the [FAQ](../FAQ.md) or open an issue in the repository.
