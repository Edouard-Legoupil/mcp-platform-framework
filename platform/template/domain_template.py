"""Domain Template for MCP Framework"""
import os
import json
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from pathlib import Path


@dataclass
class DomainTemplate:
    """
    Domain template for creating new MCP domain repositories.
    
    This class defines the structure and configuration for a new domain
    that will use the MCP Platform Framework.
    """
    # Domain information
    name: str
    description: str
    version: str = "1.0.0"
    author: str = ""
    maintainer: str = ""
    
    # Repository information
    repository_name: Optional[str] = None
    repository_url: Optional[str] = None
    
    # MCP Framework configuration
    mcp_version: str = "1.0.0"
    enable_telemetry: bool = True
    enable_audit: bool = True
    enable_authentication: bool = True
    enable_authorization: bool = True
    enable_classification: bool = True
    auto_discover_tools: bool = True
    
    # Tool paths
    tool_paths: List[str] = field(default_factory=lambda: ["tools", "queries", "actions", "resources"])
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    dev_dependencies: List[str] = field(default_factory=list)
    
    # Environment configuration
    environments: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize default values"""
        if self.repository_name is None:
            self.repository_name = f"mcp-{self.name.lower().replace(' ', '-')}"
        
        if not self.environments:
            self.environments = {
                "dev": {
                    "resource_group": f"{self.repository_name}-dev-rg",
                    "location": "eastus",
                    "mcp_domain": self.name
                },
                "test": {
                    "resource_group": f"{self.repository_name}-test-rg",
                    "location": "eastus",
                    "mcp_domain": self.name
                },
                "prod": {
                    "resource_group": f"{self.repository_name}-prod-rg",
                    "location": "eastus",
                    "mcp_domain": self.name
                }
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary"""
        return {
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'author': self.author,
            'maintainer': self.maintainer,
            'repository_name': self.repository_name,
            'repository_url': self.repository_url,
            'mcp_version': self.mcp_version,
            'enable_telemetry': self.enable_telemetry,
            'enable_audit': self.enable_audit,
            'enable_authentication': self.enable_authentication,
            'enable_authorization': self.enable_authorization,
            'enable_classification': self.enable_classification,
            'auto_discover_tools': self.auto_discover_tools,
            'tool_paths': self.tool_paths,
            'dependencies': self.dependencies,
            'dev_dependencies': self.dev_dependencies,
            'environments': self.environments,
            'tags': self.tags,
            'categories': self.categories
        }
    
    def save_to_file(self, file_path: str):
        """Save template to JSON file"""
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def from_file(cls, file_path: str) -> 'DomainTemplate':
        """Load template from JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return cls(**data)
    
    def get_directory_structure(self) -> Dict[str, Any]:
        """Get the directory structure for the domain"""
        return {
            self.repository_name: {
                'README.md': self._get_readme_content(),
                'requirements.txt': self._get_requirements_content(),
                'requirements-dev.txt': self._get_dev_requirements_content(),
                'setup.py': self._get_setup_content(),
                'main.py': self._get_main_content(),
                'config.py': self._get_config_content(),
                'platform_framework/': {
                    '__init__.py': '# Import platform framework from central repository'
                },
                'tools/': {
                    '__init__.py': self._get_tools_init_content(),
                    'example_tool.py': self._get_example_tool_content()
                },
                'tests/': {
                    '__init__.py': '',
                    'unit/': {
                        '__init__.py': '',
                        'test_tools.py': self._get_test_tools_content()
                    },
                    'integration/': {
                        '__init__.py': '',
                        'test_integration.py': self._get_test_integration_content()
                    }
                },
                '.github/': {
                    'workflows/': {
                        'ci-cd.yml': self._get_github_workflow_content()
                    }
                },
                'deployment/': {
                    'parameters.json': self._get_deployment_parameters_content()
                }
            }
        }
    
    def _get_readme_content(self) -> str:
        """Get README content"""
        return f"""# {self.name} Domain

## Description
{self.description}

## MCP Platform Framework

This domain uses the MCP Platform Framework version {self.mcp_version}.

## Features

- **Authentication**: {'Enabled' if self.enable_authentication else 'Disabled'}
- **Authorization**: {'Enabled' if self.enable_authorization else 'Disabled'}
- **Telemetry**: {'Enabled' if self.enable_telemetry else 'Disabled'}
- **Audit Logging**: {'Enabled' if self.enable_audit else 'Disabled'}
- **Data Classification**: {'Enabled' if self.enable_classification else 'Disabled'}
- **Auto Tool Discovery**: {'Enabled' if self.auto_discover_tools else 'Disabled'}

## Environment Configuration

{json.dumps(self.environments, indent=2)}

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run locally:
   ```bash
   python main.py
   ```

3. Deploy to Azure:
   ```bash
   az functionapp create --resource-group <resource-group> --name <function-app-name> --runtime python --runtime-version 3.11 --functions-version 4
   ```
"""
    
    def _get_requirements_content(self) -> str:
        """Get requirements.txt content"""
        lines = [
            "# Domain Requirements",
            f"# MCP Platform Framework {self.mcp_version}",
            "",
            "# Import from central platform framework",
            "-e git+https://github.com/your-org/mcp-platform-framework.git@" + self.mcp_version,
            ""
        ]
        
        if self.dependencies:
            lines.append("# Domain-specific dependencies")
            for dep in self.dependencies:
                lines.append(dep)
        
        return "\n".join(lines)
    
    def _get_dev_requirements_content(self) -> str:
        """Get requirements-dev.txt content"""
        lines = [
            "# Development Requirements",
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "httpx>=0.24.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0"
        ]
        
        if self.dev_dependencies:
            lines.extend(self.dev_dependencies)
        
        return "\n".join(lines)
    
    def _get_setup_content(self) -> str:
        """Get setup.py content"""
        return f"""from setuptools import setup, find_packages

setup(
    name="{self.repository_name}",
    version="{self.version}",
    description="{self.description}",
    author="{self.author}",
    maintainer="{self.maintainer}",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        # MCP Platform Framework
        "mcp-platform-framework>={self.mcp_version}",
        # Add domain-specific dependencies here
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
    ],
)
"""
    
    def _get_main_content(self) -> str:
        """Get main.py content"""
        return f"""import os
from platform.framework import initialize_framework, get_framework
from platform.registration import set_domain_context

# Initialize domain context
set_domain_context("{self.name}")

# Initialize framework
framework = initialize_framework(
    domain="{self.name}",
    environment=os.getenv('MCP_ENVIRONMENT', 'Dev'),
    enable_telemetry={str(self.enable_telemetry).lower()},
    enable_audit={str(self.enable_audit).lower()},
    enable_authentication={str(self.enable_authentication).lower()},
    enable_authorization={str(self.enable_authorization).lower()},
    enable_classification={str(self.enable_classification).lower()},
    auto_discover_tools={str(self.auto_discover_tools).lower()}
)

# Import domain tools
from tools import example_tool

if __name__ == "__main__":
    print(f"{self.name} domain initialized with MCP Framework {self.mcp_version}")
    print(f"Environment: {{framework.get_environment()}}")
    print(f"Domain: {{framework.get_domain()}}")
"""
    
    def _get_config_content(self) -> str:
        """Get config.py content"""
        return f"""import os
from platform.config import ConfigManager, get_config_manager

def get_domain_config():
    '''Get domain-specific configuration'''
    return {{
        'domain': '{self.name}',
        'version': '{self.version}',
        'description': '{self.description}',
        'author': '{self.author}',
        'maintainer': '{self.maintainer}'
    }}
"""
    
    def _get_tools_init_content(self) -> str:
        """Get tools/__init__.py content"""
        return f"""from .example_tool import *

__all__ = []
"""
    
    def _get_example_tool_content(self) -> str:
        """Get example tool content"""
        return f"""from platform import tool, resource, query, action
from platform.classification import classification
from platform.auth import authenticated_tool, requires_permission

@tool(description="Example tool for {self.name} domain")
@classification("INTERNAL")
@authenticated_tool
@requires_permission("domain.read")
def example_tool(user_id: str = None) -> dict:
    '''Example tool that demonstrates MCP framework features'''
    return {{
        'message': 'Hello from {self.name} domain!',
        'user_id': user_id,
        'domain': '{self.name}',
        'version': '{self.version}'
    }}

@resource(description="Get domain information")
@classification("PUBLIC")
def get_domain_info() -> dict:
    '''Get information about this domain'''
    return {{
        'name': '{self.name}',
        'description': '{self.description}',
        'version': '{self.version}',
        'author': '{self.author}'
    }}

@query(description="Query domain data")
@classification("CONFIDENTIAL")
def query_domain_data(query: str) -> list:
    '''Query data in this domain'''
    # This would query Fabric semantic models or warehouses
    return [{{
        'query': query,
        'domain': '{self.name}',
        'results': []
    }}]

@action(description="Perform domain action")
@classification("CONFIDENTIAL")
def perform_domain_action(action: str, data: dict = None) -> dict:
    '''Perform an action in this domain'''
    return {{
        'action': action,
        'data': data or {{}},
        'status': 'completed',
        'domain': '{self.name}'
    }}
"""
    
    def _get_test_tools_content(self) -> str:
        """Get test tools content"""
        return f"""import pytest
from tools.example_tool import example_tool, get_domain_info, query_domain_data, perform_domain_action

class TestExampleTools:
    def test_example_tool(self):
        result = example_tool(user_id="test-user")
        assert result['message'] == 'Hello from {self.name} domain!'
        assert result['user_id'] == 'test-user'
        assert result['domain'] == '{self.name}'
    
    def test_get_domain_info(self):
        result = get_domain_info()
        assert result['name'] == '{self.name}'
        assert result['description'] == '{self.description}'
    
    def test_query_domain_data(self):
        result = query_domain_data("test query")
        assert len(result) == 1
        assert result[0]['query'] == "test query"
    
    def test_perform_domain_action(self):
        result = perform_domain_action("test-action", {{"key": "value"}})
        assert result['action'] == "test-action"
        assert result['status'] == "completed"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
"""
    
    def _get_test_integration_content(self) -> str:
        """Get test integration content"""
        return f"""import pytest
from platform.framework import get_framework

class TestDomainIntegration:
    def test_framework_initialization(self):
        framework = get_framework()
        assert framework.get_domain() == '{self.name}'
        assert framework.is_development() or framework.is_test() or framework.is_production()
    
    def test_tool_registry(self):
        framework = get_framework()
        tools = framework.registry.get_all_tools()
        assert len(tools) > 0
        
        # Check if our tools are registered
        tool_names = [tool.metadata.name for tool in tools]
        assert 'example_tool' in tool_names
        assert 'get_domain_info' in tool_names

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
"""
    
    def _get_github_workflow_content(self) -> str:
        """Get GitHub workflow content"""
        return f"""name: {self.name} CI/CD

on:
  push:
    branches: [ main, releases/** ]
    paths-ignore:
      - 'docs/**'
      - 'README.md'
      - '.gitignore'
      - 'LICENSE'
  pull_request:
    branches: [ feature/**, bugfix/** ]
    paths-ignore:
      - 'docs/**'
      - 'README.md'

env:
  PROJECT_NAME: {self.repository_name}
  MCP_DOMAIN: {self.name}
  PYTHON_VERSION: '3.11'

jobs:
  build:
    name: Build and Test
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{{ env.PYTHON_VERSION }}}
          cache: 'pip'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Install dev dependencies
        if: github.ref == 'refs/heads/main'
        run: pip install -r requirements-dev.txt
      
      - name: Run tests
        run: python -m pytest tests/ --cov=platform --cov-report=xml --junitxml=test-results.xml -v
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: test-results.xml
      
      - name: Upload coverage report
        if: github.ref == 'refs/heads/main'
        uses: actions/upload-artifact@v3
        with:
          name: coverage-report
          path: coverage/

  deploy-dev:
    name: Deploy to Development
    needs: build
    if: success()
    runs-on: ubuntu-latest
    environment: Development
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{{ env.PYTHON_VERSION }}}
          cache: 'pip'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Login to Azure
        uses: azure/login@v1
        with:
          creds: ${{{ secrets.AZURE_CREDENTIALS }}}
      
      - name: Deploy Infrastructure
        run: |
          az deployment group create \\
            --resource-group {self.environments['dev']['resource_group']} \\
            --template-file deployment/mcp-deployment.bicep \\
            --parameters \\
              projectName={self.repository_name} \\
              environment=dev \\
              location={self.environments['dev']['location']} \\
              mcpDomain={self.name}
      
      - name: Deploy Function App
        run: |
          az functionapp deployment source config-zip \\
            --resource-group {self.environments['dev']['resource_group']} \\
            --name {self.repository_name}-dev-func \\
            --src .
"""
    
    def _get_deployment_parameters_content(self) -> str:
        """Get deployment parameters content"""
        return json.dumps({
            'project_name': self.repository_name,
            'mcp_domain': self.name,
            'environments': self.environments,
            'enable_telemetry': self.enable_telemetry,
            'enable_audit': self.enable_audit,
            'enable_authentication': self.enable_authentication,
            'enable_authorization': self.enable_authorization,
            'enable_classification': self.enable_classification,
            'auto_discover_tools': self.auto_discover_tools
        }, indent=2)


def create_domain_template(
    name: str,
    description: str,
    author: str = "",
    maintainer: str = "",
    **kwargs
) -> DomainTemplate:
    """
    Create a new domain template.
    
    Args:
        name: Domain name
        description: Domain description
        author: Author name
        maintainer: Maintainer email
        **kwargs: Additional template parameters
    
    Returns:
        DomainTemplate instance
    """
    return DomainTemplate(
        name=name,
        description=description,
        author=author,
        maintainer=maintainer,
        **kwargs
    )