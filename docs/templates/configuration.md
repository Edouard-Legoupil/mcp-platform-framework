# ⚙️ Template Configuration

Comprehensive guide to configuring the MCP Platform Framework template system for your organization's specific needs.

## 🎯 Overview

The MCP Platform Framework template system is highly configurable, allowing you to customize:

- **Template Content**: What files and directories are included in generated domains
- **Template Parameters**: What parameters are required and their validation rules
- **Template Behavior**: How templates are processed and generated
- **Organization Standards**: Default values and conventions for your organization
- **Integration**: How the template system integrates with your development workflow

## 🏗️ Configuration Structure

### Template Configuration Files

The template system uses several configuration files:

```
templates/
├── template-config.yaml      # Main template configuration
├── parameters.yaml           # Parameter definitions
├── defaults.yaml             # Default values
├── validation.yaml           # Validation rules
└── organization/
    ├── standards.yaml        # Organization standards
    ├── teams.yaml            # Team definitions
    └── classifications.yaml   # Classification levels
```

### Main Configuration File

```yaml
# templates/template-config.yaml

# Template system version
version: "1.0.0"

# Template repository settings
template_repository:
  path: "./templates"
  default_template: "domain"
  
# Template processing
template_processing:
  engine: "jinja2"
  autoescape: true
  trim_blocks: true
  lstrip_blocks: true
  
# Output settings
output:
  default_path: "./mcp-{domain_name}"
  overwrite_existing: false
  create_parent_dirs: true
  
# File permissions
permissions:
  default_file: "0644"
  default_dir: "0755"
  executable: "0755"
  
# Post-generation hooks
post_generation:
  enabled: true
  hooks:
    - name: "initialize_git"
      script: "scripts/initialize_git.py"
      description: "Initialize git repository"
      enabled: true
      
    - name: "install_dependencies"
      script: "scripts/install_dependencies.py"
      description: "Install Python dependencies"
      enabled: false  # Let user install manually
      
    - name: "validate_domain"
      script: "scripts/validate_domain.py"
      description: "Validate generated domain"
      enabled: true

# Logging
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "template-generator.log"
  max_size: 10485760  # 10MB
  backup_count: 5
```

## 📝 Parameter Configuration

### Parameter Definitions

```yaml
# templates/parameters.yaml

# Parameter categories
categories:
  - name: "required"
    description: "Required parameters that must be provided"
    
  - name: "optional"
    description: "Optional parameters with default values"
    
  - name: "advanced"
    description: "Advanced parameters for custom configurations"

# Parameter definitions
parameters:
  # Required parameters
  - name: "domain"
    category: "required"
    description: "Domain name (PascalCase)"
    type: "string"
    required: true
    default: null
    validation:
      - type: "required"
      - type: "pattern"
        pattern: "^[A-Z][a-zA-Z0-9]*$"
        message: "Domain name must be in PascalCase"
      - type: "max_length"
        max: 50
        message: "Domain name must be 50 characters or less"
    ui:
      type: "text"
      label: "Domain Name"
      placeholder: "DonorManagement"
      help: "Enter the domain name in PascalCase (e.g., DonorManagement, Finance)"

  - name: "description"
    category: "required"
    description: "Domain description"
    type: "string"
    required: true
    default: null
    validation:
      - type: "required"
      - type: "max_length"
        max: 500
        message: "Description must be 500 characters or less"
    ui:
      type: "textarea"
      label: "Description"
      placeholder: "Domain for managing donor information and portfolios"
      rows: 3

  - name: "owner"
    category: "required"
    description: "Owning team or department"
    type: "string"
    required: true
    default: null
    options:
      - "DER"
      - "Finance"
      - "HR"
      - "IT"
      - "Operations"
      - "SupplyChain"
      - "Programs"
    validation:
      - type: "required"
      - type: "in_list"
        list: "options"
        message: "Owner must be one of the predefined teams"
    ui:
      type: "select"
      label: "Owner"
      help: "Select the team that owns this domain"

  - name: "classification"
    category: "required"
    description: "Default data classification level"
    type: "string"
    required: true
    default: "CONFIDENTIAL"
    options:
      - "PUBLIC"
      - "INTERNAL"
      - "CONFIDENTIAL"
      - "STRICTLY_CONFIDENTIAL"
    validation:
      - type: "required"
      - type: "in_list"
        list: "options"
        message: "Classification must be one of the predefined levels"
    ui:
      type: "select"
      label: "Default Classification"
      help: "Select the default data classification level for this domain"

  # Optional parameters
  - name: "environment"
    category: "optional"
    description: "Default environment"
    type: "string"
    required: false
    default: "dev"
    options:
      - "dev"
      - "test"
      - "prod"
    validation:
      - type: "in_list"
        list: "options"
        message: "Environment must be one of: dev, test, prod"
    ui:
      type: "select"
      label: "Default Environment"
      help: "Select the default environment for this domain"

  - name: "output"
    category: "optional"
    description: "Output directory path"
    type: "string"
    required: false
    default: "./mcp-{domain_name}"
    validation:
      - type: "path"
        exists: false
        message: "Output directory must not already exist"
    ui:
      type: "text"
      label: "Output Directory"
      placeholder: "./mcp-DonorManagement"
      help: "Path where the domain will be created"

  - name: "include_examples"
    category: "optional"
    description: "Include example tools and code"
    type: "boolean"
    required: false
    default: true
    ui:
      type: "checkbox"
      label: "Include Examples"
      help: "Include example tools and code in the generated domain"

  - name: "include_tests"
    category: "optional"
    description: "Include test files"
    type: "boolean"
    required: false
    default: true
    ui:
      type: "checkbox"
      label: "Include Tests"
      help: "Include test files in the generated domain"

  - name: "include_docs"
    category: "optional"
    description: "Include documentation files"
    type: "boolean"
    required: false
    default: true
    ui:
      type: "checkbox"
      label: "Include Documentation"
      help: "Include documentation files in the generated domain"

  - name: "include_pipelines"
    category: "optional"
    description: "Include CI/CD pipeline files"
    type: "boolean"
    required: false
    default: true
    ui:
      type: "checkbox"
      label: "Include Pipelines"
      help: "Include CI/CD pipeline files in the generated domain"

  # Advanced parameters
  - name: "template_version"
    category: "advanced"
    description: "Template version to use"
    type: "string"
    required: false
    default: "latest"
    options:
      - "latest"
      - "1.0.0"
      - "1.1.0"
    validation:
      - type: "in_list"
        list: "options"
        message: "Template version must be one of the available versions"
    ui:
      type: "select"
      label: "Template Version"
      help: "Select the template version to use for domain generation"

  - name: "python_version"
    category: "advanced"
    description: "Python version for the domain"
    type: "string"
    required: false
    default: "3.11"
    options:
      - "3.9"
      - "3.10"
      - "3.11"
      - "3.12"
    validation:
      - type: "in_list"
        list: "options"
        message: "Python version must be one of the supported versions"
    ui:
      type: "select"
      label: "Python Version"
      help: "Select the Python version for the domain"

  - name: "azure_functions_version"
    category: "advanced"
    description: "Azure Functions version"
    type: "string"
    required: false
    default: "4"
    options:
      - "3"
      - "4"
    validation:
      - type: "in_list"
        list: "options"
        message: "Azure Functions version must be 3 or 4"
    ui:
      type: "select"
      label: "Azure Functions Version"
      help: "Select the Azure Functions version for deployment"
```

### Default Values

```yaml
# templates/defaults.yaml

# Default values for parameters
defaults:
  domain: null  # Must be provided
  description: null  # Must be provided
  owner: "DER"
  classification: "CONFIDENTIAL"
  environment: "dev"
  output: "./mcp-{domain_name}"
  include_examples: true
  include_tests: true
  include_docs: true
  include_pipelines: true
  template_version: "latest"
  python_version: "3.11"
  azure_functions_version: "4"

# Default configuration for generated domains
domain_defaults:
  version: "1.0.0"
  debug: true
  log_level: "INFO"
  
  # Framework defaults
  framework:
    auto_discovery: true
    tool_modules:
      - "tools"
    
  # Security defaults
  security:
    authentication_required: true
    authorization_required: true
    audit_enabled: true
    
  # Monitoring defaults
  monitoring:
    telemetry_enabled: true
    metrics_enabled: true
    logging_enabled: true
    
  # Performance defaults
  performance:
    max_concurrent_requests: 100
    request_timeout: 30
    cache_enabled: true
    cache_ttl: 300

# Default environment-specific configurations
environment_defaults:
  dev:
    debug: true
    log_level: "DEBUG"
    cache_enabled: false
    performance_monitoring: false
    
  test:
    debug: false
    log_level: "INFO"
    cache_enabled: true
    performance_monitoring: true
    
  prod:
    debug: false
    log_level: "WARNING"
    cache_enabled: true
    performance_monitoring: true
    audit_enabled: true
```

## 🎯 Organization Configuration

### Organization Standards

```yaml
# templates/organization/standards.yaml

# Organization information
organization:
  name: "UNHCR"
  description: "United Nations High Commissioner for Refugees"
  
# Domain naming conventions
naming_conventions:
  domain:
    pattern: "^[A-Z][a-zA-Z0-9]*$"
    max_length: 50
    examples:
      - "DonorManagement"
      - "Finance"
      - "CampaignAnalytics"
    
  tool:
    pattern: "^[A-Z][a-zA-Z0-9]*$"
    max_length: 50
    examples:
      - "GetDonorPortfolio"
      - "UpdateCampaignStatus"
      - "CalculateBudget"
    
  variable:
    pattern: "^[a-z][a-z0-9_]*$"
    max_length: 50
    examples:
      - "donor_id"
      - "campaign_name"
      - "total_amount"

# Code style standards
code_style:
  indentation: 4
  max_line_length: 120
  quote_style: "double"
  line_ending: "lf"
  
# Documentation standards
documentation:
  format: "markdown"
  required_files:
    - "README.md"
    - "docs/api-reference.md"
  
# Testing standards
testing:
  required_coverage: 80
  test_framework: "pytest"
  required_test_types:
    - "unit"
    - "integration"
  
# Security standards
security:
  authentication_required: true
  authorization_required: true
  audit_logging_required: true
  data_classification_required: true
  secret_management: "key_vault"
```

### Team Definitions

```yaml
# templates/organization/teams.yaml

# Team definitions
teams:
  - name: "DER"
    full_name: "Donor Engagement and Resource Mobilization"
    description: "Responsible for donor management and resource mobilization"
    email: "der@unhcr.org"
    domains:
      - "DonorManagement"
      - "CampaignManagement"
      - "Fundraising"
    permissions:
      - "domain:create"
      - "domain:manage"
      - "tool:deploy"
    
  - name: "Finance"
    full_name: "Finance Department"
    description: "Responsible for financial management and reporting"
    email: "finance@unhcr.org"
    domains:
      - "Finance"
      - "Budgeting"
      - "Reporting"
    permissions:
      - "domain:create"
      - "domain:manage"
      - "tool:deploy"
    
  - name: "HR"
    full_name: "Human Resources"
    description: "Responsible for human resources management"
    email: "hr@unhcr.org"
    domains:
      - "HRManagement"
      - "Payroll"
      - "Recruitment"
    permissions:
      - "domain:create"
      - "domain:manage"
    
  - name: "IT"
    full_name: "Information Technology"
    description: "Responsible for IT infrastructure and support"
    email: "it@unhcr.org"
    domains:
      - "ITManagement"
      - "Infrastructure"
      - "Support"
    permissions:
      - "domain:create"
      - "domain:manage"
      - "domain:deploy"
      - "platform:admin"
    
  - name: "Operations"
    full_name: "Operations Department"
    description: "Responsible for operational activities"
    email: "operations@unhcr.org"
    domains:
      - "OperationsManagement"
      - "Logistics"
      - "Procurement"
    permissions:
      - "domain:create"
      - "domain:manage"
      - "tool:deploy"

# Team permissions matrix
permissions_matrix:
  DER:
    domains:
      create: true
      manage: true
      delete: false
    tools:
      deploy: true
      manage: true
    platform:
      admin: false
      configure: false
    
  Finance:
    domains:
      create: true
      manage: true
      delete: false
    tools:
      deploy: true
      manage: true
    platform:
      admin: false
      configure: false
    
  IT:
    domains:
      create: true
      manage: true
      delete: true
    tools:
      deploy: true
      manage: true
    platform:
      admin: true
      configure: true
```

### Classification Levels

```yaml
# templates/organization/classifications.yaml

# Data classification levels
classifications:
  - level: "PUBLIC"
    description: "Information that can be freely shared with the public"
    color: "green"
    icon: "🟢"
    examples:
      - "Public reports"
      - "Press releases"
      - "Public website content"
    requirements:
      access_control: "none"
      audit_logging: "none"
      encryption: "none"
      retention: "permanent"
    
  - level: "INTERNAL"
    description: "Information for internal use only"
    color: "blue"
    icon: "🔵"
    examples:
      - "Internal policies"
      - "Meeting minutes"
      - "Internal communications"
    requirements:
      access_control: "authentication"
      audit_logging: "optional"
      encryption: "optional"
      retention: "7_years"
    
  - level: "CONFIDENTIAL"
    description: "Sensitive information that requires protection"
    color: "orange"
    icon: "🟠"
    examples:
      - "Donor information"
      - "Financial data"
      - "Personnel records"
    requirements:
      access_control: "authentication + authorization"
      audit_logging: "required"
      encryption: "required"
      retention: "7_years"
    
  - level: "STRICTLY_CONFIDENTIAL"
    description: "Highly sensitive information requiring maximum protection"
    color: "red"
    icon: "🔴"
    examples:
      - "PII (Personally Identifiable Information)"
      - "Medical records"
      - "Legal documents"
      - "Passwords and credentials"
    requirements:
      access_control: "authentication + authorization + approval"
      audit_logging: "required"
      encryption: "required"
      retention: "3_years"

# Classification hierarchy
classification_hierarchy:
  - "PUBLIC"
  - "INTERNAL"
  - "CONFIDENTIAL"
  - "STRICTLY_CONFIDENTIAL"

# Classification rules
classification_rules:
  # Default classification for different data types
  defaults:
    donor: "CONFIDENTIAL"
    financial: "CONFIDENTIAL"
    personnel: "CONFIDENTIAL"
    pii: "STRICTLY_CONFIDENTIAL"
    public: "PUBLIC"
    
  # Inheritance rules
  inheritance:
    # If a parent is classified, children inherit the classification
    inherit_from_parent: true
    
    # Higher classification takes precedence
    precedence: "higher"
    
  # Automatic classification based on content
  content_based:
    enabled: true
    patterns:
      - pattern: "ssn|social.*security|national.*id"
        classification: "STRICTLY_CONFIDENTIAL"
        
      - pattern: "password|secret|token|key|credential"
        classification: "STRICTLY_CONFIDENTIAL"
        
      - pattern: "donor|contribution|financial"
        classification: "CONFIDENTIAL"
        
      - pattern: "internal|confidential"
        classification: "INTERNAL"
```

## 🔧 Template Customization

### Custom Templates

Create custom templates for specific domain types:

```python
# templates/generators/custom_templates.py

from platform.template import DomainTemplate, TemplateFile

# Custom template for analytics domains
analytics_template = DomainTemplate(
    name="analytics_domain",
    description="Template for analytics-focused domains",
    version="1.0.0",
    
    # Additional files for analytics domains
    files=[
        TemplateFile(
            path="tools/analytics_tools.py",
            content="""
# Analytics tools for {domain_name}
from platform_framework import (
    authenticated_tool,
    requires_permission,
    track_tool_telemetry,
    tool
)
from platform.connectivity import FabricClient

fabric = FabricClient()

@tool(
    name="GetAnalyticsDashboard",
    description="Retrieve analytics dashboard for {domain_name}",
    classification="CONFIDENTIAL"
)
@authenticated_tool
@requires_permission("analytics.read")
@track_tool_telemetry
async def get_analytics_dashboard(time_range: str = "30d") -> dict:
    semantic_model = fabric.get_semantic_model("{domain_name}Analytics")
    results = await semantic_model.execute(
        f"EVALUATE {domain_name}Dashboard({time_range})"
    )
    return process_dashboard_results(results)

@tool(
    name="ExportAnalyticsData",
    description="Export analytics data for {domain_name}",
    classification="CONFIDENTIAL"
)
@authenticated_tool
@requires_permission("analytics.export")
@track_tool_telemetry
async def export_analytics_data(format: str = "csv", time_range: str = "30d") -> bytes:
    semantic_model = fabric.get_semantic_model("{domain_name}Analytics")
    results = await semantic_model.execute(
        f"EVALUATE {domain_name}DataExport({time_range})"
    )
    return export_data(results, format)
""",
            condition=lambda params: True
        ),
        
        TemplateFile(
            path="config/analytics.yaml",
            content="""
# Analytics configuration for {domain_name}
analytics:
  dashboard:
    enabled: true
    refresh_interval: 300  # 5 minutes
    
  data_export:
    enabled: true
    max_rows: 100000
    formats:
      - csv
      - json
      - excel
    
  caching:
    enabled: true
    ttl: 3600  # 1 hour
    max_size: 1000
""",
            condition=lambda params: True
        )
    ],
    
    # Additional parameters for analytics domains
    parameters=[
        TemplateParameter(
            name="analytics_model",
            description="Name of the analytics semantic model",
            type="string",
            required=True,
            default=lambda params: f"{params['domain']}Analytics"
        ),
        TemplateParameter(
            name="enable_dashboard",
            description="Enable analytics dashboard",
            type="boolean",
            required=False,
            default=True
        ),
        TemplateParameter(
            name="enable_data_export",
            description="Enable data export functionality",
            type="boolean",
            required=False,
            default=True
        )
    ],
    
    # Parent template
    parent="domain"
)

# Custom template for data processing domains
data_processing_template = DomainTemplate(
    name="data_processing_domain",
    description="Template for data processing domains",
    version="1.0.0",
    
    files=[
        TemplateFile(
            path="tools/processing_tools.py",
            content="""
# Data processing tools for {domain_name}
from platform_framework import (
    authenticated_tool,
    requires_permission,
    track_tool_telemetry,
    tool
)
from platform.connectivity import FabricClient
import pandas as pd

fabric = FabricClient()

@tool(
    name="ProcessData",
    description="Process data for {domain_name}",
    classification="CONFIDENTIAL"
)
@authenticated_tool
@requires_permission("data.process")
@track_tool_telemetry
async def process_data(data: dict, process_type: str) -> dict:
    # Process data based on type
    if process_type == "clean":
        return clean_data(data)
    elif process_type == "transform":
        return transform_data(data)
    elif process_type == "aggregate":
        return aggregate_data(data)
    else:
        raise ValueError(f"Unknown process type: {process_type}")

@tool(
    name="BatchProcess",
    description="Batch process data for {domain_name}",
    classification="CONFIDENTIAL"
)
@authenticated_tool
@requires_permission("data.batch_process")
@track_tool_telemetry
async def batch_process(data_list: list, process_type: str) -> list:
    results = []
    for data in data_list:
        result = await process_data(data, process_type)
        results.append(result)
    return results
""",
            condition=lambda params: True
        ),
        
        TemplateFile(
            path="config/processing.yaml",
            content="""
# Data processing configuration for {domain_name}
processing:
  batch_size: 1000
  max_concurrent: 10
  timeout: 300  # 5 minutes
  
  cleanup:
    enabled: true
    rules:
      - field: "email"
        pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
        
      - field: "phone"
        pattern: "^\\+?[0-9\\s-]{10,}$"
    
  transformation:
    enabled: true
    rules:
      - from: "first_name"
        to: "firstName"
        
      - from: "last_name"
        to: "lastName"
""",
            condition=lambda params: True
        )
    ],
    
    parent="domain"
)

# Register custom templates
def register_custom_templates():
    template_repository = TemplateRepository()
    
    template_repository.add_template(analytics_template)
    template_repository.add_template(data_processing_template)
    
    return template_repository
```

### Template Inheritance

Create specialized templates that extend base templates:

```python
# templates/generators/template_inheritance.py

from platform.template import DomainTemplate, TemplateFile, TemplateParameter

# Base template
base_template = DomainTemplate(
    name="base_domain",
    description="Base domain template",
    version="1.0.0",
    
    files=[
        TemplateFile(
            path="tools/__init__.py",
            content="""
# Tools module for {domain_name}
from . import *
""",
            condition=lambda params: True
        ),
        TemplateFile(
            path="config/domain.yaml",
            content="""
domain:
  name: {domain_name}
  description: {description}
  owner: {owner}
  classification: {classification}
  environment: {environment}
  version: 1.0.0
""",
            condition=lambda params: True
        )
    ],
    
    parameters=[
        TemplateParameter(name="domain", required=True),
        TemplateParameter(name="description", required=True),
        TemplateParameter(name="owner", required=True),
        TemplateParameter(name="classification", required=True),
        TemplateParameter(name="environment", required=False, default="dev")
    ]
)

# Specialized template for high-security domains
high_security_template = DomainTemplate(
    name="high_security_domain",
    description="Template for high-security domains",
    version="1.0.0",
    
    # Inherit from base template
    parent=base_template,
    
    # Additional files for high-security domains
    files=[
        TemplateFile(
            path="security/",
            content=None,  # Directory
            condition=lambda params: True
        ),
        TemplateFile(
            path="security/audit_rules.yaml",
            content="""
# Audit rules for high-security domain
audit:
  log_all_access: true
  log_all_changes: true
  sensitive_fields:
    - ssn
    - credit_card
    - password
    - token
    - secret
  
  retention:
    days: 365
    immutable: true
""",
            condition=lambda params: True
        ),
        TemplateFile(
            path="security/encryption.yaml",
            content="""
# Encryption configuration for high-security domain
encryption:
  enabled: true
  algorithm: AES-256
  key_rotation: 90  # days
  
  field_level:
    enabled: true
    fields:
      - ssn
      - credit_card
      - password
""",
            condition=lambda params: True
        )
    ],
    
    # Override base template files
    overrides={
        "config/domain.yaml": """
domain:
  name: {domain_name}
  description: {description}
  owner: {owner}
  classification: STRICTLY_CONFIDENTIAL
  environment: {environment}
  version: 1.0.0
  
  security:
    high_security: true
    audit_all: true
    encrypt_all: true
"""
    },
    
    # Additional parameters
    parameters=[
        TemplateParameter(
            name="security_level",
            description="Security level for the domain",
            type="string",
            required=True,
            default="high",
            options=["standard", "high", "maximum"]
        ),
        TemplateParameter(
            name="audit_retention_days",
            description="Audit log retention in days",
            type="int",
            required=False,
            default=365
        )
    ]
)

# Specialized template for data-intensive domains
data_intensive_template = DomainTemplate(
    name="data_intensive_domain",
    description="Template for data-intensive domains",
    version="1.0.0",
    
    parent=base_template,
    
    files=[
        TemplateFile(
            path="data/",
            content=None,  # Directory
            condition=lambda params: True
        ),
        TemplateFile(
            path="data/models.py",
            content="""
# Data models for {domain_name}
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime

@dataclass
class {domain_name}Data:
    id: str
    name: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
""",
            condition=lambda params: True
        ),
        TemplateFile(
            path="config/data.yaml",
            content="""
# Data configuration for {domain_name}
data:
  storage:
    type: azure_blob
    account: {storage_account}
    container: {domain_name | lower}-data
    
  caching:
    enabled: true
    type: redis
    host: localhost
    port: 6379
    ttl: 3600
    
  processing:
    batch_size: 1000
    max_workers: 10
    timeout: 300
""",
            condition=lambda params: True
        )
    ],
    
    overrides={
        "config/domain.yaml": """
domain:
  name: {domain_name}
  description: {description}
  owner: {owner}
  classification: {classification}
  environment: {environment}
  version: 1.0.0
  
  data:
    intensive: true
    storage: azure_blob
    caching: redis
"""
    },
    
    parameters=[
        TemplateParameter(
            name="storage_account",
            description="Azure storage account for data",
            type="string",
            required=True
        ),
        TemplateParameter(
            name="enable_caching",
            description="Enable data caching",
            type="boolean",
            required=False,
            default=True
        ),
        TemplateParameter(
            name="max_batch_size",
            description="Maximum batch size for data processing",
            type="int",
            required=False,
            default=1000
        )
    ]
)
```

### Conditional Template Files

Include or exclude files based on parameters:

```python
# templates/generators/conditional_files.py

from platform.template import TemplateFile

# Conditional files based on parameters
conditional_files = [
    # Always include these files
    TemplateFile(
        path="tools/__init__.py",
        content="""
# Tools module for {domain_name}
from . import *
""",
        condition=lambda params: True
    ),
    
    # Include example tools if requested
    TemplateFile(
        path="tools/example_tools.py",
        content="""
# Example tools for {domain_name}
from platform_framework import (
    authenticated_tool,
    requires_permission,
    track_tool_telemetry,
    tool
)

@tool(
    name="HelloWorld",
    description="Example tool that returns a greeting",
    classification="PUBLIC"
)
@authenticated_tool
@track_tool_telemetry
def hello_world(name: str = "World") -> dict:
    return {"message": f"Hello, {name}!"}

@tool(
    name="Echo",
    description="Example tool that echoes input",
    classification="PUBLIC"
)
@authenticated_tool
@track_tool_telemetry
def echo(input: Any) -> Any:
    return input
""",
        condition=lambda params: params.get("include_examples", True)
    ),
    
    # Include test files if requested
    TemplateFile(
        path="tests/unit/test_example_tools.py",
        content="""
# Unit tests for example tools
import pytest
from tools.example_tools import hello_world, echo

class TestExampleTools:
    def test_hello_world(self):
        result = hello_world()
        assert result["message"] == "Hello, World!"
        
    def test_hello_world_with_name(self):
        result = hello_world("Alice")
        assert result["message"] == "Hello, Alice!"
        
    def test_echo(self):
        result = echo("test")
        assert result == "test"
        
    def test_echo_complex(self):
        test_data = {"key": "value", "number": 42}
        result = echo(test_data)
        assert result == test_data
""",
        condition=lambda params: params.get("include_tests", True) and params.get("include_examples", True)
    ),
    
    # Include documentation if requested
    TemplateFile(
        path="docs/README.md",
        content="""
# {domain_name} Domain

## Overview

This domain provides MCP tools for {description}.

## Quick Start

### Local Development

```bash
pip install -r requirements.txt
python main.py
```

### Deployment

```bash
az functionapp deployment source config-zip \\
    --resource-group mcp-platform-rg \\
    --name mcp-{domain_name | lower}-{environment} \\
    --src .
```

## Tools

See the [API Reference](api-reference.md) for detailed tool documentation.

## Configuration

See the configuration files in the `config/` directory.

## Support

For issues or questions, contact the {owner} team.
""",
        condition=lambda params: params.get("include_docs", True)
    ),
    
    # Include API reference if requested
    TemplateFile(
        path="docs/api-reference.md",
        content="""
# {domain_name} API Reference

## Tools

### HelloWorld

Example tool that returns a greeting.

**Endpoint**: `POST /api/tools/HelloWorld`

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| name | string | No | Name to greet (default: "World") |

**Returns**:

```json
{
  "message": "string"
}
```

**Example**:

```bash
curl -X POST http://localhost:8000/api/tools/HelloWorld \\
  -H "Content-Type: application/json" \\
  -d '{"name": "Alice"}'
```

### Echo

Example tool that echoes input.

**Endpoint**: `POST /api/tools/Echo`

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| input | any | Yes | Input to echo |

**Returns**: The input value

**Example**:

```bash
curl -X POST http://localhost:8000/api/tools/Echo \\
  -H "Content-Type: application/json" \\
  -d '{"input": "test"}'
```
""",
        condition=lambda params: params.get("include_docs", True) and params.get("include_examples", True)
    ),
    
    # Include pipeline files if requested
    TemplateFile(
        path="pipelines/azure-devops.yml",
        content="""
# Azure DevOps pipeline for {domain_name}

trigger:
  branches:
    include:
      - main
      - releases/*

variables:
  python.version: '3.11'
  azureSubscription: 'mcp-platform-subscription'
  functionAppName: 'mcp-{domain_name | lower}-$(Environment)'
  resourceGroup: 'mcp-platform-rg'

stages:
- stage: Build
  jobs:
  - job: Build
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

- stage: Deploy
  dependsOn: Build
  condition: succeeded()
  jobs:
  - deployment: Deploy
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
            inputs:
              azureSubscription: '$(azureSubscription)'
              appType: 'functionAppLinux'
              appName: '$(functionAppName)'
              deployToSlotOrASE: false
              resourceGroupName: '$(resourceGroup)'
              package: '.'
              runtimeStack: 'PYTHON'
              runtimeVersion: '3.11'
""",
        condition=lambda params: params.get("include_pipelines", True)
    )
]
```

## 🔍 Template Validation

### Validation Rules

```yaml
# templates/validation.yaml

# Validation rules for template parameters
parameter_validation:
  domain:
    - type: "required"
      message: "Domain name is required"
    
    - type: "pattern"
      pattern: "^[A-Z][a-zA-Z0-9]*$"
      message: "Domain name must be in PascalCase (start with uppercase letter, followed by letters and numbers)"
    
    - type: "max_length"
      max: 50
      message: "Domain name must be 50 characters or less"
    
    - type: "reserved_words"
      words:
        - "platform"
        - "framework"
        - "mcp"
        - "azure"
        - "microsoft"
      message: "Domain name cannot contain reserved words"
    
    - type: "unique"
      message: "Domain name must be unique across the organization"

  description:
    - type: "required"
      message: "Description is required"
    
    - type: "max_length"
      max: 500
      message: "Description must be 500 characters or less"

  owner:
    - type: "required"
      message: "Owner is required"
    
    - type: "in_list"
      list:
        - "DER"
        - "Finance"
        - "HR"
        - "IT"
        - "Operations"
      message: "Owner must be one of the predefined teams"

  classification:
    - type: "required"
      message: "Classification is required"
    
    - type: "in_list"
      list:
        - "PUBLIC"
        - "INTERNAL"
        - "CONFIDENTIAL"
        - "STRICTLY_CONFIDENTIAL"
      message: "Classification must be one of the predefined levels"

# Validation rules for generated domains
domain_validation:
  required_files:
    - "tools/__init__.py"
    - "config/domain.yaml"
    - "main.py"
    - "requirements.txt"
    - "README.md"
    
  required_directories:
    - "tools"
    - "config"
    - "tests"
    - "docs"
    
  forbidden_files:
    - ".env"
    - "*.pyc"
    - "__pycache__"
    - ".git"
    
  forbidden_patterns:
    - "password.*="
    - "secret.*="
    - "token.*="
    - "api_key.*="
    
  file_content_validation:
    "config/*.yaml":
      - type: "yaml"
        message: "Configuration files must be valid YAML"
      
    "*.py":
      - type: "python_syntax"
        message: "Python files must have valid syntax"
      
    "requirements.txt":
      - type: "pip_packages"
        message: "All packages in requirements.txt must be valid"

# Validation rules for template files
template_validation:
  file_names:
    - type: "pattern"
      pattern: "^[a-zA-Z0-9._-]+$"
      message: "File names must contain only alphanumeric characters, dots, underscores, and hyphens"
    
    - type: "max_length"
      max: 255
      message: "File names must be 255 characters or less"
    
  file_contents:
    - type: "no_secrets"
      patterns:
        - "password"
        - "secret"
        - "token"
        - "api_key"
        - "connection_string"
      message: "Template files must not contain secrets or sensitive information"
    
    - type: "valid_template_syntax"
      message: "Template files must have valid template syntax"
```

### Custom Validators

```python
# templates/validators.py

from platform.template import TemplateValidator, ValidationResult, ValidationError
import re
import yaml
import ast

class CustomTemplateValidator(TemplateValidator):
    def __init__(self):
        super().__init__()
        self._setup_custom_validators()
    
    def _setup_custom_validators(self):
        # Add custom validation rules
        self.validators["domain_name"] = self._validate_domain_name
        self.validators["python_syntax"] = self._validate_python_syntax
        self.validators["yaml_syntax"] = self._validate_yaml_syntax
        self.validators["no_hardcoded_secrets"] = self._validate_no_hardcoded_secrets
    
    def _validate_domain_name(self, value: str, params: dict) -> ValidationResult:
        """Validate domain name."""
        errors = []
        
        # Check required
        if not value:
            errors.append(ValidationError("Domain name is required"))
            return ValidationResult(valid=False, errors=errors)
        
        # Check PascalCase pattern
        if not re.match(r'^[A-Z][a-zA-Z0-9]*$', value):
            errors.append(ValidationError(
                "Domain name must be in PascalCase (start with uppercase letter, followed by letters and numbers)"
            ))
        
        # Check length
        if len(value) > 50:
            errors.append(ValidationError("Domain name must be 50 characters or less"))
        
        # Check reserved words
        reserved_words = ["platform", "framework", "mcp", "azure", "microsoft"]
        if any(word in value.lower() for word in reserved_words):
            errors.append(ValidationError("Domain name cannot contain reserved words"))
        
        # Check uniqueness (would need access to domain registry)
        # if domain_exists(value):
        #     errors.append(ValidationError("Domain name must be unique"))
        
        return ValidationResult(valid=len(errors) == 0, errors=errors)
    
    def _validate_python_syntax(self, content: str, params: dict) -> ValidationResult:
        """Validate Python syntax."""
        errors = []
        
        try:
            ast.parse(content)
        except SyntaxError as e:
            errors.append(ValidationError(f"Python syntax error: {e}"))
        
        return ValidationResult(valid=len(errors) == 0, errors=errors)
    
    def _validate_yaml_syntax(self, content: str, params: dict) -> ValidationResult:
        """Validate YAML syntax."""
        errors = []
        
        try:
            yaml.safe_load(content)
        except yaml.YAMLError as e:
            errors.append(ValidationError(f"YAML syntax error: {e}"))
        
        return ValidationResult(valid=len(errors) == 0, errors=errors)
    
    def _validate_no_hardcoded_secrets(self, content: str, params: dict) -> ValidationResult:
        """Validate that no secrets are hardcoded."""
        errors = []
        
        # Patterns that might indicate hardcoded secrets
        secret_patterns = [
            r'password\s*[=:]\s*["\''][^"\']+["\']',
            r'secret\s*[=:]\s*["\''][^"\']+["\']',
            r'token\s*[=:]\s*["\''][^"\']+["\']',
            r'api_key\s*[=:]\s*["\''][^"\']+["\']',
            r'connection_string\s*[=:]\s*["\''][^"\']+["\']',
            r'client_secret\s*[=:]\s*["\''][^"\']+["\']'
        ]
        
        for pattern in secret_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                errors.append(ValidationError(
                    f"Potential hardcoded secret found matching pattern: {pattern}"
                ))
        
        return ValidationResult(valid=len(errors) == 0, errors=errors)
```

## 📊 Template System Management

### Template Registry

```python
# templates/registry.py

from platform.template import TemplateRegistry, DomainTemplate

class MCPTemplateRegistry(TemplateRegistry):
    def __init__(self):
        super().__init__()
        self._load_builtin_templates()
        self._load_custom_templates()
    
    def _load_builtin_templates(self):
        """Load built-in templates."""
        from platform.template.builtin import (
            base_domain_template,
            analytics_domain_template,
            data_processing_template,
            high_security_template
        )
        
        self.register_template(base_domain_template)
        self.register_template(analytics_domain_template)
        self.register_template(data_processing_template)
        self.register_template(high_security_template)
    
    def _load_custom_templates(self):
        """Load custom templates from configuration."""
        import os
        from pathlib import Path
        from importlib import import_module
        
        # Look for custom templates in the templates/custom directory
        custom_dir = Path(__file__).parent / "custom"
        if custom_dir.exists():
            for template_file in custom_dir.glob("*.py"):
                if template_file.name != "__init__.py":
                    module_name = f"templates.custom.{template_file.stem}"
                    try:
                        module = import_module(module_name)
                        if hasattr(module, "TEMPLATE"):
                            self.register_template(module.TEMPLATE)
                    except ImportError as e:
                        print(f"Warning: Could not load custom template {module_name}: {e}")
    
    def get_template(self, name: str) -> DomainTemplate:
        """Get a template by name."""
        template = super().get_template(name)
        if template is None:
            raise ValueError(f"Template '{name}' not found")
        return template
    
    def list_templates(self) -> list:
        """List all available templates."""
        return list(self.templates.keys())
    
    def get_template_info(self, name: str) -> dict:
        """Get information about a template."""
        template = self.get_template(name)
        return {
            "name": template.name,
            "description": template.description,
            "version": template.version,
            "parameters": [
                {
                    "name": p.name,
                    "description": p.description,
                    "required": p.required,
                    "default": p.default,
                    "type": p.type,
                    "options": p.options
                }
                for p in template.parameters
            ],
            "parent": template.parent.name if template.parent else None
        }
```

### Template Versioning

```python
# templates/versioning.py

from platform.template import TemplateVersion, TemplateMigrator
from datetime import datetime
from typing import Dict, List, Optional

class MCPTemplateVersionManager:
    def __init__(self):
        self.versions: Dict[str, TemplateVersion] = {}
        self.migrator = TemplateMigrator()
        self._load_versions()
    
    def _load_versions(self):
        """Load template versions."""
        # Version 1.0.0
        self.versions["1.0.0"] = TemplateVersion(
            version="1.0.0",
            description="Initial template version",
            release_date=datetime(2024, 1, 1),
            changes=[
                "Initial domain template structure",
                "Basic framework integration",
                "Standard configuration files",
                "Tool registration support",
                "Authentication and authorization support"
            ],
            compatibility="1.0.0",
            migration_required=False
        )
        
        # Version 1.1.0
        self.versions["1.1.0"] = TemplateVersion(
            version="1.1.0",
            description="Enhanced template with improved features",
            release_date=datetime(2024, 3, 15),
            changes=[
                "Added semantic model support",
                "Improved error handling patterns",
                "Enhanced security configuration",
                "Added performance testing templates",
                "Better documentation templates"
            ],
            compatibility="1.0.0",
            migration_required=False
        )
        
        # Version 2.0.0
        self.versions["2.0.0"] = TemplateVersion(
            version="2.0.0",
            description="Major template update with breaking changes",
            release_date=datetime(2024, 6, 1),
            changes=[
                "Restructured domain directory layout",
                "New configuration format (YAML)",
                "Improved tool registration",
                "Enhanced telemetry integration",
                "Better Azure Functions integration",
                "Updated dependency management"
            ],
            compatibility="2.0.0",
            migration_required=True,
            migration_script="scripts/migrate_1x_to_2x.py"
        )
        
        # Version 2.1.0
        self.versions["2.1.0"] = TemplateVersion(
            version="2.1.0",
            description="Template with advanced features",
            release_date=datetime(2024, 9, 1),
            changes=[
                "Added support for custom templates",
                "Template inheritance",
                "Conditional file inclusion",
                "Improved parameter validation",
                "Better error handling in templates",
                "Enhanced documentation"
            ],
            compatibility="2.0.0",
            migration_required=False
        )
    
    def get_version(self, version: str) -> Optional[TemplateVersion]:
        """Get a specific version."""
        return self.versions.get(version)
    
    def get_latest_version(self) -> TemplateVersion:
        """Get the latest version."""
        return max(self.versions.values(), key=lambda v: v.release_date)
    
    def get_compatible_versions(self, version: str) -> List[TemplateVersion]:
        """Get all versions compatible with the specified version."""
        target_version = self.get_version(version)
        if target_version is None:
            return []
        
        compatible = []
        for v in self.versions.values():
            if self._is_compatible(v.compatibility, target_version.version):
                compatible.append(v)
        
        return sorted(compatible, key=lambda v: v.release_date, reverse=True)
    
    def _is_compatible(self, compatibility: str, target_version: str) -> bool:
        """Check if two versions are compatible."""
        # Simple implementation - versions are compatible if they share the same major version
        # In a real implementation, you would use proper semantic versioning
        return compatibility.split(".")[0] == target_version.split(".")[0]
    
    def get_migration_path(self, from_version: str, to_version: str) -> List[str]:
        """Get the migration path from one version to another."""
        from_ver = self.get_version(from_version)
        to_ver = self.get_version(to_version)
        
        if from_ver is None or to_ver is None:
            return []
        
        # Get all versions between from_version and to_version
        all_versions = sorted(
            [v for v in self.versions.values() 
             if from_ver.release_date <= v.release_date <= to_ver.release_date],
            key=lambda v: v.release_date
        )
        
        # Extract version strings
        return [v.version for v in all_versions if v.version != from_version]
    
    async def migrate_domain(self, domain_path: str, target_version: str) -> bool:
        """Migrate a domain to a specific template version."""
        current_version = self._get_domain_version(domain_path)
        if current_version == target_version:
            return True
        
        migration_path = self.get_migration_path(current_version, target_version)
        if not migration_path:
            return False
        
        for version in migration_path:
            success = await self.migrator.migrate_domain(domain_path, version)
            if not success:
                return False
        
        return True
    
    def _get_domain_version(self, domain_path: str) -> str:
        """Get the current template version of a domain."""
        # In a real implementation, this would read from a version file in the domain
        import os
        version_file = os.path.join(domain_path, ".template-version")
        if os.path.exists(version_file):
            with open(version_file, 'r') as f:
                return f.read().strip()
        return "1.0.0"  # Default to first version
```

## 📋 Configuration Checklist

### ✅ Template System Configuration Checklist

- [ ] Template repository is properly structured
- [ ] All template files are valid and properly formatted
- [ ] Template parameters are defined and validated
- [ ] Default values are set appropriately
- [ ] Template validation rules are configured
- [ ] Organization standards are defined
- [ ] Team definitions are complete
- [ ] Classification levels are defined
- [ ] Custom templates are registered
- [ ] Template versioning is set up
- [ ] Migration scripts are available
- [ ] Template documentation is complete

### ✅ Domain Generation Configuration Checklist

- [ ] All required parameters are defined
- [ ] Parameter validation rules are in place
- [ ] Default values are appropriate
- [ ] Conditional rendering rules are configured
- [ ] Template inheritance is set up correctly
- [ ] Post-generation hooks are configured
- [ ] Template versioning is working
- [ ] Migration paths are defined

## 🚨 Common Configuration Issues

### Template Not Found

**Problem**: The specified template cannot be found.

**Solutions**:
- Verify the template name is correct
- Check that the template is registered in the template registry
- Ensure the template files exist in the correct location
- Check for typos in the template name

### Invalid Parameter Value

**Problem**: A parameter value fails validation.

**Solutions**:
- Check the parameter validation rules
- Verify the input value matches the expected format
- Check for typos in the parameter value
- Review the parameter options if it's a selection parameter

### Missing Required Parameter

**Problem**: A required parameter is missing.

**Solutions**:
- Check which parameters are marked as required
- Provide a value for all required parameters
- Use default values where available
- Check the parameter definitions

### Template Version Incompatible

**Problem**: The requested template version is not compatible.

**Solutions**:
- Check the compatibility of the requested version
- Use a compatible version
- Migrate the domain to a compatible version first
- Review the version compatibility matrix

### Configuration File Syntax Error

**Problem**: A configuration file has syntax errors.

**Solutions**:
- Validate YAML files for correct syntax
- Check for proper indentation
- Verify all required fields are present
- Use a YAML validator

## 📚 Related Documentation

- [Template System Overview](overview.md) - Template architecture and components
- [Creating New Domains](creating-domains.md) - Step-by-step domain creation guide
- [Domain Structure](structure.md) - Standard domain repository structure
- [Getting Started](../getting-started/README.md) - General getting started guide
- [Architecture](../architecture/README.md) - Framework architecture overview

---

**🎉 Ready to configure the template system?** Use this guide to customize the template system for your organization's specific needs.

**Need to create a domain?** Check out the [Creating New Domains](creating-domains.md) guide for step-by-step instructions.