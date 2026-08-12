# 🏭 Template System Overview

Comprehensive overview of the MCP Platform Framework template system, including architecture, components, and how it enables rapid domain development.

## 🎯 Overview

The MCP Platform Framework Template System is a powerful tool for creating new domain repositories with all the necessary infrastructure, configuration, and best practices built-in. It enables organizations to:

- **Standardize** domain development across the organization
- **Accelerate** domain creation from days to minutes
- **Ensure** consistency in structure, security, and compliance
- **Simplify** onboarding of new developers
- **Maintain** high quality and reliability standards

## 🏗️ Template System Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Template System                           │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Template       │  │  Generator      │  │  Renderer       │ │
│  │  Repository     │  │  Engine         │  │  Engine         │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Template       │  │  Configuration  │  │  Validation     │ │
│  │  Definitions    │  │  Manager        │  │  Engine         │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Domain Generation                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Input          │  │  Template       │  │  Output         │ │
│  │  Parameters     │──▶│  Processing     │──▶│  Generation     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Template Repository Structure

The template repository contains all the files and directories that will be copied to new domain repositories:

```
templates/
├── domain/                    # Main domain template
│   ├── tools/                 # Tool implementations
│   │   ├── __init__.py
│   │   └── example_tools.py
│   ├── semantic_models/       # Semantic model access
│   │   ├── __init__.py
│   │   └── models.py
│   ├── tests/                 # Test suite
│   │   ├── unit/
│   │   │   └── __init__.py
│   │   ├── integration/
│   │   │   └── __init__.py
│   │   └── conftest.py
│   ├── docs/                  # Documentation
│   │   ├── README.md
│   │   └── api-reference.md
│   ├── config/                # Configuration
│   │   ├── domain.yaml
│   │   ├── authentication.yaml
│   │   ├── authorization.yaml
│   │   ├── telemetry.yaml
│   │   ├── audit.yaml
│   │   └── fabric.yaml
│   ├── metadata/              # Metadata
│   │   ├── catalog.json
│   │   └── governance.json
│   ├── pipelines/             # CI/CD pipelines
│   │   └── azure-devops.yml
│   ├── platform_framework/    # Platform integration
│   │   └── __init__.py
│   ├── main.py                # Azure Function entry point
│   ├── requirements.txt       # Python dependencies
│   ├── pyproject.toml        # Project configuration
│   └── README.md              # Domain README
├── partials/                  # Reusable template components
│   ├── auth/
│   │   ├── __init__.py
│   │   └── decorators.py
│   ├── telemetry/
│   │   ├── __init__.py
│   │   └── decorators.py
│   ├── audit/
│   │   ├── __init__.py
│   │   └── decorators.py
│   └── ...
└── README.md
```

### Generator Engine

The generator engine is responsible for:

1. **Parameter Processing**: Validating and processing input parameters
2. **Template Selection**: Selecting the appropriate template based on domain type
3. **Template Rendering**: Rendering template files with provided parameters
4. **File Generation**: Creating the domain repository structure
5. **Validation**: Validating the generated domain
6. **Post-Processing**: Running any post-generation scripts

```python
# Generator Engine Architecture
class TemplateGenerator:
    def __init__(self, template_repository: TemplateRepository):
        self.template_repository = template_repository
        self.renderer = TemplateRenderer()
        self.validator = DomainValidator()
        self.post_processor = PostProcessor()
    
    async def generate_domain(self, parameters: DomainParameters) -> DomainGenerationResult:
        # 1. Validate parameters
        self._validate_parameters(parameters)
        
        # 2. Select template
        template = self.template_repository.get_template(parameters.domain_type)
        
        # 3. Render template with parameters
        rendered_files = self.renderer.render_template(template, parameters)
        
        # 4. Create output directory
        self._create_output_directory(parameters.output_path)
        
        # 5. Write rendered files
        self._write_files(rendered_files, parameters.output_path)
        
        # 6. Validate generated domain
        validation_result = self.validator.validate_domain(parameters.output_path)
        
        # 7. Run post-processing
        await self.post_processor.process(parameters.output_path)
        
        return DomainGenerationResult(
            success=True,
            path=parameters.output_path,
            validation_result=validation_result
        )
```

### Template Renderer

The template renderer handles:

- **Variable Substitution**: Replacing placeholders with actual values
- **Conditional Rendering**: Including or excluding files based on conditions
- **Template Inheritance**: Extending and overriding template files
- **File Transformation**: Modifying file contents during rendering

```python
# Template Renderer
class TemplateRenderer:
    def __init__(self):
        self.engine = Jinja2Environment(
            loader=FileSystemLoader('templates'),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters and functions
        self._setup_custom_filters()
    
    def render_template(self, template: Template, parameters: DomainParameters) -> List[RenderedFile]:
        rendered_files = []
        
        for template_file in template.files:
            # Render file content
            content = self._render_file_content(template_file, parameters)
            
            # Determine output path
            output_path = self._get_output_path(template_file, parameters)
            
            rendered_files.append(RenderedFile(
                path=output_path,
                content=content,
                permissions=template_file.permissions
            ))
        
        return rendered_files
    
    def _render_file_content(self, template_file: TemplateFile, parameters: DomainParameters) -> str:
        template = self.engine.get_template(template_file.path)
        return template.render(**parameters.to_dict())
```

## 📦 Template Types

### Domain Templates

The primary template type for creating new MCP domains:

```python
@dataclass
class DomainTemplate:
    name: str = "domain"
    description: str = "Standard MCP domain template"
    version: str = "1.0.0"
    
    # Template files and directories
    files: List[TemplateFile] = field(default_factory=list)
    
    # Template parameters
    parameters: List[TemplateParameter] = field(default_factory=list)
    
    # Conditional rendering rules
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    # Post-generation hooks
    post_hooks: List[PostGenerationHook] = field(default_factory=list)
```

### Template Parameters

Parameters that can be customized when generating a domain:

```python
@dataclass
class TemplateParameter:
    name: str
    description: str
    required: bool = True
    default: Any = None
    type: str = "string"  # string, int, float, bool, list, dict
    options: Optional[List[Any]] = None  # For dropdown/selection parameters
    validation: Optional[Callable] = None
    
    # UI hints for interactive generation
    ui_type: str = "text"  # text, textarea, select, checkbox, etc.
    ui_label: Optional[str] = None
    ui_placeholder: Optional[str] = None
    ui_help: Optional[str] = None

# Common domain parameters
DOMAIN_PARAMETERS = [
    TemplateParameter(
        name="domain",
        description="Domain name (e.g., DonorManagement, Finance)",
        required=True,
        type="string",
        validation=lambda x: bool(x) and x.isidentifier(),
        ui_type="text",
        ui_label="Domain Name",
        ui_placeholder="DonorManagement"
    ),
    TemplateParameter(
        name="description",
        description="Domain description",
        required=True,
        type="string",
        ui_type="textarea",
        ui_label="Description",
        ui_placeholder="Domain for managing donor information and portfolios"
    ),
    TemplateParameter(
        name="owner",
        description="Domain owner (team or department)",
        required=True,
        type="string",
        options=["DER", "Finance", "HR", "IT", "Operations"],
        ui_type="select",
        ui_label="Owner"
    ),
    TemplateParameter(
        name="classification",
        description="Default data classification level",
        required=True,
        type="string",
        options=["PUBLIC", "INTERNAL", "CONFIDENTIAL", "STRICTLY_CONFIDENTIAL"],
        default="CONFIDENTIAL",
        ui_type="select",
        ui_label="Classification"
    ),
    TemplateParameter(
        name="environment",
        description="Default environment",
        required=False,
        type="string",
        options=["dev", "test", "prod"],
        default="dev",
        ui_type="select",
        ui_label="Environment"
    ),
    TemplateParameter(
        name="include_examples",
        description="Include example tools and code",
        required=False,
        type="bool",
        default=True,
        ui_type="checkbox",
        ui_label="Include Examples"
    )
]
```

## 🎪 Template Features

### Automatic Framework Integration

Every domain automatically includes:

```python
# platform_framework/__init__.py
"""
Platform Framework Integration for {domain_name}

This module provides automatic integration with the MCP Platform Framework,
including authentication, authorization, telemetry, audit logging, and more.
"""

from platform.framework import MCPFramework
from platform.auth import authenticated_tool, get_caller_identity
from platform.authorization import requires_permission, requires_role
from platform.telemetry import track_tool_telemetry, TelemetryService
from platform.audit import audit_tool_access, AuditService
from platform.classification import classification
from platform.registration import tool
from platform.errors import handle_errors

# Initialize framework
framework = MCPFramework(
    domain="{domain_name}",
    environment="{environment}"
)

# Initialize services
auth_service = framework.auth_service
authz_service = framework.authz_service
telemetry_service = framework.telemetry_service
audit_service = framework.audit_service

# Convenience functions
def get_domain():
    return "{domain_name}"

def get_environment():
    return "{environment}"
```

### Standard Tool Structure

Example tool implementation with all framework capabilities:

```python
# tools/donor_tools.py
"""
Donor Management Tools

This module contains all MCP tools for the DonorManagement domain.
"""

from platform_framework import (
    authenticated_tool,
    requires_permission,
    requires_role,
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
def get_donor_portfolio(donor_id: str) -> dict:
    """
    Retrieve comprehensive donor portfolio information.
    
    Args:
        donor_id: The ID of the donor to retrieve
        
    Returns:
        Dictionary containing donor portfolio information
        
    Raises:
        AuthenticationError: If not authenticated
        AuthorizationError: If insufficient permissions
        DataAccessError: If donor not found
    """
    # Get semantic model
    semantic_model = fabric.get_semantic_model("DonorAnalytics")
    
    # Execute query
    results = await semantic_model.execute(
        f"EVALUATE FILTER(Donors, Donors[DonorID] = \"{donor_id}\")"
    )
    
    if not results or not results.rows:
        raise DataAccessError("DATA_001", "Donor not found", donor_id=donor_id)
    
    # Process results
    portfolio = process_portfolio_results(results.rows[0])
    
    return portfolio
```

### Configuration Management

Standard configuration files for all domains:

```yaml
# config/domain.yaml
domain:
  name: {domain_name}
  description: {description}
  owner: {owner}
  classification: {classification}
  environment: {environment}
  version: 1.0.0
  
  # Tool registration
  tool_discovery:
    enabled: true
    modules:
      - tools
    
  # Security
  security:
    authentication_required: true
    default_classification: {classification}
    
  # Performance
  performance:
    max_concurrent_requests: 100
    request_timeout: 30
    
  # Monitoring
  monitoring:
    telemetry_enabled: true
    audit_enabled: true
```

### Metadata Files

Automatic generation of metadata files for catalog integration:

```json
// metadata/catalog.json
{
  "domain": {
    "name": "{domain_name}",
    "description": "{description}",
    "owner": "{owner}",
    "classification": "{classification}",
    "environment": "{environment}",
    "version": "1.0.0"
  },
  "catalog": {
    "register_in_catalog": true,
    "catalog_name": "MCP Platform Catalog",
    "update_frequency": "daily"
  },
  "governance": {
    "compliance_required": true,
    "data_classification": "{classification}",
    "retention_policy": "7_years",
    "access_review_frequency": "quarterly"
  }
}
```

## 🚀 Template Generation Process

### Step-by-Step Generation

1. **Parameter Collection**: Gather all required parameters from the user
2. **Parameter Validation**: Validate all parameters and provide feedback
3. **Template Selection**: Select the appropriate template based on domain type
4. **Template Rendering**: Render all template files with the provided parameters
5. **Directory Creation**: Create the output directory structure
6. **File Writing**: Write all rendered files to the output directory
7. **Validation**: Validate the generated domain structure and files
8. **Post-Processing**: Run any post-generation scripts or hooks
9. **Completion**: Provide summary and next steps to the user

### Generation Example

```bash
# Command line generation
python -m platform.template.template_generator \
    --domain DonorManagement \
    --description "Domain for managing donor information and portfolios" \
    --owner DER \
    --classification CONFIDENTIAL \
    --environment dev \
    --output ./mcp-donor-management \
    --include-examples true

# Output
Creating new MCP domain: DonorManagement
Output directory: ./mcp-donor-management

Processing template files...
✓ Created tools/__init__.py
✓ Created tools/donor_tools.py
✓ Created semantic_models/__init__.py
✓ Created semantic_models/models.py
✓ Created tests/unit/__init__.py
✓ Created tests/integration/__init__.py
✓ Created tests/conftest.py
✓ Created docs/README.md
✓ Created config/domain.yaml
✓ Created config/authentication.yaml
✓ Created config/authorization.yaml
✓ Created config/telemetry.yaml
✓ Created config/audit.yaml
✓ Created config/fabric.yaml
✓ Created metadata/catalog.json
✓ Created metadata/governance.json
✓ Created pipelines/azure-devops.yml
✓ Created platform_framework/__init__.py
✓ Created main.py
✓ Created requirements.txt
✓ Created pyproject.toml
✓ Created README.md

Validating generated domain...
✓ Domain structure is valid
✓ All required files are present
✓ Configuration files are valid
✓ No syntax errors detected

Domain generation complete!

Next steps:
1. cd mcp-donor-management
2. pip install -r requirements.txt
3. Edit config/domain.yaml with your specific configuration
4. Start developing tools in the tools/ directory
5. Test locally with: python main.py
```

### Interactive Generation

For a more user-friendly experience, use the interactive mode:

```bash
# Interactive mode
python -m platform.template.template_generator --interactive

# Or simply
python -m platform.template.template_generator

# Example interactive session
$ python -m platform.template.template_generator

MCP Domain Template Generator
==============================

Enter domain name: DonorManagement
Enter domain description: Domain for managing donor information and portfolios
Select owner:
  1. DER
  2. Finance
  3. HR
  4. IT
  5. Operations
Select (1-5): 1
Select default classification:
  1. PUBLIC
  2. INTERNAL
  3. CONFIDENTIAL
  4. STRICTLY_CONFIDENTIAL
Select (1-4): 3
Select default environment:
  1. dev
  2. test
  3. prod
Select (1-3): 1
Include example tools and code? (y/n): y
Output directory [./mcp-donor-management]: 

Generating domain...
```

## 🔧 Template Customization

### Customizing Templates

You can customize the template system for your organization's specific needs:

```python
# Custom template configuration
class CustomTemplateGenerator(TemplateGenerator):
    def __init__(self):
        super().__init__(template_repository)
        self._setup_custom_templates()
        self._setup_custom_parameters()
        self._setup_custom_hooks()
    
    def _setup_custom_templates(self):
        # Add custom templates
        self.template_repository.add_template(
            CustomDomainTemplate(
                name="custom_domain",
                description="Custom domain template for our organization",
                files=[...],
                parameters=[...]
            )
        )
    
    def _setup_custom_parameters(self):
        # Add custom parameters
        self.parameters.extend([
            TemplateParameter(
                name="custom_parameter",
                description="Our custom parameter",
                required=True,
                type="string"
            )
        ])
    
    def _setup_custom_hooks(self):
        # Add custom post-generation hooks
        self.post_hooks.append(
            PostGenerationHook(
                name="custom_hook",
                script="scripts/custom_hook.py",
                description="Run our custom post-generation script"
            )
        )
```

### Template Inheritance

Create specialized templates that inherit from base templates:

```python
# Base template
base_template = DomainTemplate(
    name="base_domain",
    description="Base domain template",
    files=[...],
    parameters=[...]
)

# Specialized template
specialized_template = DomainTemplate(
    name="specialized_domain",
    description="Specialized domain template",
    parent=base_template,
    files=[...],  # Additional files
    parameters=[...],  # Additional parameters
    overrides={
        "config/domain.yaml": "specialized_config.yaml",
        "tools/__init__.py": "specialized_tools_init.py"
    }
)
```

### Conditional Rendering

Include or exclude files based on parameters:

```python
# Conditional template files
template_files = [
    TemplateFile(
        path="tools/__init__.py",
        content="...",
        condition=lambda params: True  # Always include
    ),
    TemplateFile(
        path="tools/example_tools.py",
        content="...",
        condition=lambda params: params.get("include_examples", True)
    ),
    TemplateFile(
        path="config/advanced.yaml",
        content="...",
        condition=lambda params: params.get("advanced_config", False)
    ),
    TemplateFile(
        path="tests/performance/",
        content="...",
        condition=lambda params: params.get("include_performance_tests", False)
    )
]
```

## 📊 Template Versioning

### Version Management

The template system supports versioning to manage template evolution:

```python
@dataclass
class TemplateVersion:
    version: str
    description: str
    release_date: datetime
    changes: List[str]
    compatibility: str  # Semantic versioning compatibility
    
    # Migration information
    migration_required: bool = False
    migration_script: Optional[str] = None

# Template version history
TEMPLATE_VERSIONS = [
    TemplateVersion(
        version="1.0.0",
        description="Initial template version",
        release_date=datetime(2024, 1, 1),
        changes=[
            "Initial domain template structure",
            "Basic framework integration",
            "Standard configuration files"
        ],
        compatibility="1.0.0"
    ),
    TemplateVersion(
        version="1.1.0",
        description="Enhanced template with improved features",
        release_date=datetime(2024, 3, 15),
        changes=[
            "Added semantic model support",
            "Improved error handling patterns",
            "Enhanced security configuration",
            "Added performance testing templates"
        ],
        compatibility="1.0.0",
        migration_required=False
    ),
    TemplateVersion(
        version="2.0.0",
        description="Major template update with breaking changes",
        release_date=datetime(2024, 6, 1),
        changes=[
            "Restructured domain directory layout",
            "New configuration format",
            "Improved tool registration",
            "Enhanced telemetry integration"
        ],
        compatibility="2.0.0",
        migration_required=True,
        migration_script="scripts/migrate_1x_to_2x.py"
    )
]
```

### Migration Support

Support for migrating existing domains to new template versions:

```python
class TemplateMigrator:
    def __init__(self):
        self.migrations = {
            "1.0.0": self._migrate_to_1_1_0,
            "1.1.0": self._migrate_to_2_0_0
        }
    
    async def migrate_domain(self, domain_path: str, target_version: str) -> MigrationResult:
        # Get current version
        current_version = self._get_current_version(domain_path)
        
        # Get migration path
        migration_path = self._get_migration_path(current_version, target_version)
        
        # Apply migrations in order
        for migration in migration_path:
            result = await self._apply_migration(domain_path, migration)
            if not result.success:
                return MigrationResult(
                    success=False,
                    current_version=current_version,
                    target_version=target_version,
                    error=f"Migration to {migration} failed: {result.error}"
                )
        
        # Update version
        self._update_version(domain_path, target_version)
        
        return MigrationResult(
            success=True,
            current_version=current_version,
            target_version=target_version
        )
    
    async def _apply_migration(self, domain_path: str, version: str) -> MigrationResult:
        migration_func = self.migrations.get(version)
        if migration_func:
            return await migration_func(domain_path)
        return MigrationResult(success=True)
    
    async def _migrate_to_1_1_0(self, domain_path: str) -> MigrationResult:
        # Migration logic for 1.0.0 -> 1.1.0
        try:
            # Add semantic model support
            self._add_semantic_model_files(domain_path)
            
            # Update configuration
            self._update_configuration(domain_path)
            
            return MigrationResult(success=True)
        except Exception as e:
            return MigrationResult(success=False, error=str(e))
```

## 📋 Template System Checklist

### ✅ Template System Setup Checklist

- [ ] Template repository is properly structured
- [ ] All template files are valid and properly formatted
- [ ] Template parameters are defined and validated
- [ ] Template rendering engine is configured
- [ ] Template validation is implemented
- [ ] Post-generation hooks are configured
- [ ] Template versioning is set up
- [ ] Migration scripts are available
- [ ] Template documentation is complete
- [ ] Template testing is in place

### ✅ Domain Generation Checklist

- [ ] All required parameters are provided
- [ ] Parameter validation passes
- [ ] Template selection is correct
- [ ] Template rendering completes successfully
- [ ] Output directory is created
- [ ] All files are written correctly
- [ ] Generated domain passes validation
- [ ] Post-generation hooks run successfully
- [ ] Generation summary is provided

## 🚨 Common Template System Issues

### Template Generation Fails

**Problem**: Template generation fails with errors.

**Solutions**:
- Verify all required parameters are provided
- Check parameter validation rules
- Ensure template files exist and are readable
- Check for syntax errors in template files
- Verify output directory permissions

### Generated Domain Doesn't Work

**Problem**: The generated domain doesn't work as expected.

**Solutions**:
- Check that all required dependencies are installed
- Verify configuration files are correct
- Ensure framework integration is working
- Check for missing or incorrect file permissions
- Review template validation results

### Missing Files in Generated Domain

**Problem**: Some files are missing from the generated domain.

**Solutions**:
- Check template file definitions
- Verify conditional rendering rules
- Ensure all template files are included
- Check for errors during file writing

### Template Version Conflicts

**Problem**: Issues arise from template version mismatches.

**Solutions**:
- Check current template version
- Verify compatibility with target version
- Run migration scripts if needed
- Review version-specific documentation

## 📚 Related Documentation

- [Creating New Domains](creating-domains.md) - Step-by-step domain creation guide
- [Template Configuration](configuration.md) - Template customization and configuration
- [Domain Structure](structure.md) - Standard domain repository structure
- [Getting Started](../getting-started/README.md) - General getting started guide
- [Architecture](../architecture/README.md) - Framework architecture overview

---

**🎉 Ready to understand the template system?** This overview provides a comprehensive look at how the template system works and how you can leverage it for rapid domain development.

**Need to create a domain?** Check out the [Creating New Domains](creating-domains.md) guide for step-by-step instructions.