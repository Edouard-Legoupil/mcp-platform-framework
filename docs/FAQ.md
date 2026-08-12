# Frequently Asked Questions

## 📋 General Questions

### What is the MCP Platform Framework?

The MCP Platform Framework is a comprehensive framework designed for building Model Context Protocol (MCP) tools that integrate seamlessly with Microsoft Fabric and Azure environments. It provides a standardized way to develop, deploy, and manage MCP tools while ensuring security, compliance, and observability.

### What are the key principles of the MCP Platform Framework?

The framework follows several key principles:

1. **Separation of Concerns**: Domains own business capabilities; the platform owns everything else
2. **Standardization**: Consistent patterns and interfaces across all tools
3. **Security by Design**: Built-in security controls and compliance
4. **Observability**: Comprehensive monitoring and telemetry
5. **Automation**: Automated registration, documentation, and deployment

### Who should use this framework?

This framework is designed for:
- **Domain Teams**: Building MCP tools for specific business domains (Donor Management, Finance, Supply Chain, etc.)
- **Platform Teams**: Managing the MCP infrastructure and cross-cutting concerns
- **DevOps Teams**: Deploying and maintaining MCP tools in production
- **Compliance Teams**: Ensuring tools meet organizational governance requirements

### What are the prerequisites for using this framework?

- **Azure Subscription**: Active Azure subscription with appropriate permissions
- **Microsoft Fabric**: Access to Fabric workspaces and capacities
- **Python**: Version 3.9, 3.10, or 3.11
- **Azure CLI**: Version 2.50.0 or higher
- **Azure Functions Core Tools**: Version 4.x

---

## 🚀 Getting Started

### How do I create a new MCP domain?

To create a new MCP domain:

1. **Use the template**: Clone the MCP template repository
2. **Configure domain**: Update domain-specific configuration in `config/`
3. **Implement tools**: Add your tool implementations in the `tools/` directory
4. **Test locally**: Run and test your tools locally
5. **Deploy**: Deploy to Azure Function App

See the [Creating Domains](templates/creating-domains.md) guide for detailed instructions.

### How do I add a new tool to my domain?

To add a new tool:

1. **Create tool file**: Add a new Python file in the `tools/` directory
2. **Use decorators**: Decorate your function with `@tool` and other required decorators
3. **Add metadata**: Provide complete metadata (name, description, classification, etc.)
4. **Implement logic**: Write your tool's business logic
5. **Test**: Test the tool locally and in your environment

Example:
```python
from platform.framework import tool
from platform.catalog import Classification, SLATier
from platform.auth import authenticated_tool

@authenticated_tool
@tool(
    name="MyNewTool",
    description="Description of what this tool does",
    classification=Classification.CONFIDENTIAL,
    sla_tier=SLATier.GOLD,
    owner="YOUR_TEAM",
    domain="YourDomain"
)
def my_new_tool(param1: str, param2: int = 10) -> dict:
    """
    Detailed docstring explaining the tool's purpose, parameters, 
    return values, and examples.
    """
    # Your implementation here
    return {"result": "success"}
```

### How do I test my tools locally?

To test tools locally:

1. **Set up local environment**: Configure `local.settings.json` with your settings
2. **Install dependencies**: Run `pip install -r requirements.txt`
3. **Run locally**: Use `func start` to run the Function App locally
4. **Test endpoints**: Call your tool endpoints using HTTP requests

Example:
```bash
# Start the function app locally
func start

# Test a tool endpoint
curl -X POST http://localhost:7071/api/tools/MyTool \
  -H "Content-Type: application/json" \
  -d '{"param1": "value1"}'
```

### How do I deploy my tools?

To deploy your tools:

1. **Configure deployment**: Set up your deployment configuration
2. **Create infrastructure**: Deploy ARM/Bicep templates for infrastructure
3. **Deploy code**: Deploy your Function App code
4. **Verify**: Test the deployed endpoints

See the [Deployment Overview](deployment/overview.md) for detailed deployment instructions.

---

## 🔧 Configuration

### How do I configure my domain?

Domain configuration is managed through YAML files in the `config/` directory:

```yaml
# config/prod.yaml
environment: "prod"
domain: "DonorManagement"
owner: "DER"

azure:
  function_app:
    name: "mcp-donor-prod"
    resource_group: "mcp-prod-rg"
  
fabric:
  workspace: "PROD"
  endpoint: "https://api.fabric.microsoft.com"

features:
  auto_registration: true
  telemetry: true
  audit_logging: true
```

### How do I manage secrets?

Secrets should be stored in Azure Key Vault and accessed through the framework:

```python
from platform.keyvault import get_secret

# Retrieve a secret
api_key = get_secret("my-api-key")
db_connection = get_secret("database-connection-string")
```

Never hardcode secrets in your code or configuration files.

### How do I configure authentication?

Authentication is configured through the framework and uses Microsoft Entra ID:

```python
from platform.auth import AuthConfig, AuthenticationModule

# Configure authentication
auth_config = AuthConfig(
    entra_id_tenant_id=os.getenv("AZURE_TENANT_ID"),
    allowed_audiences=["api://mcp.unhcr.org"]
)

auth_module = AuthenticationModule(config=auth_config)
```

### How do I set up permissions?

Permissions are managed through Azure RBAC and the framework's authorization module:

```python
from platform.authorization import requires_permission

@requires_permission("donor.read")
def get_donor_data(donor_id: str) -> dict:
    # Only users with donor.read permission can access this
    pass
```

---

## 🔒 Security

### How does authentication work?

The framework supports multiple authentication methods:

1. **Microsoft Entra ID**: Primary authentication method
2. **JWT Validation**: Validates JWT tokens from Entra ID
3. **Managed Identity**: For service-to-service authentication
4. **OAuth2**: For user authentication flows

Authentication is handled automatically when you use the `@authenticated_tool` decorator.

### How does authorization work?

Authorization is role-based and uses the framework's authorization module:

- **Role-Based Access Control (RBAC)**: Define roles and permissions
- **Permission Decorators**: Use `@requires_permission` decorator
- **Policy Enforcement**: Enforces access policies automatically

Example:
```python
from platform.authorization import requires_permission

@requires_permission("donor.read")
def get_donor_profile(donor_id: str) -> dict:
    # Only users with donor.read permission can access
    pass
```

### How do I handle data classification?

Data classification is enforced through the framework's classification module:

```python
from platform.catalog import Classification
from platform.classification import classification

@tool(
    name="GetDonorData",
    classification=Classification.CONFIDENTIAL
)
def get_donor_data(donor_id: str) -> dict:
    # This tool handles CONFIDENTIAL data
    pass

@classification("CONFIDENTIAL")
def process_sensitive_data(data: dict) -> dict:
    # This function processes CONFIDENTIAL data
    pass
```

Classification levels:
- **PUBLIC**: No restrictions
- **INTERNAL**: Authenticated access only
- **CONFIDENTIAL**: Authorized access only
- **STRICTLY_CONFIDENTIAL**: Strict access controls

### How do I secure my Function App?

Function App security best practices:

1. **Enable HTTPS Only**: Always enforce HTTPS
2. **Configure CORS**: Restrict cross-origin requests
3. **Use Managed Identity**: For accessing other Azure services
4. **Enable Authentication**: Use Entra ID for user authentication
5. **Configure Network Security**: Use private endpoints for production
6. **Enable Monitoring**: Configure Application Insights

---

## 📊 Monitoring and Telemetry

### How does telemetry work?

The framework automatically collects telemetry for all tool invocations:

```python
from platform.telemetry import telemetry

# Custom metrics
telemetry.track_metric("custom.metric", 42)

# Custom events
telemetry.track_event("CustomEvent", {"key": "value"})

# Custom traces
telemetry.track_trace("Debug message", "INFO")
```

Telemetry includes:
- Tool name and version
- Requester identity
- Duration and status
- Token usage
- Environment and workspace
- Domain ownership

### How do I monitor my tools?

Monitoring is provided through Azure Monitor and Application Insights:

1. **Metrics**: Track tool invocations, errors, latency
2. **Logs**: View detailed logs for debugging
3. **Alerts**: Configure alerts for errors or performance issues
4. **Dashboards**: Create custom dashboards for your tools

Example Kusto query:
```kusto
requests
| where cloud_RoleName == "mcp-func-prod"
| where url contains "/api/tools/"
| project timestamp, operation_Name, resultCode, duration
| order by timestamp desc
```

### How do I set up alerts?

Configure alerts in Azure Monitor for:

- **High error rates**: Alert when error rate exceeds threshold
- **High latency**: Alert when response time is too slow
- **Failed requests**: Alert on 5xx errors
- **Rate limiting**: Alert when rate limits are approached

Example:
```bash
az monitor metrics alert create \
    --name "MCP-High-Error-Rate" \
    --resource-group mcp-prod-rg \
    --scopes /subscriptions/.../Microsoft.Web/sites/mcp-func-prod \
    --condition "Requests where ResponseCode == 5xx" \
    --threshold 5 \
    --window-size 5m \
    --action-group /subscriptions/.../actionGroups/EmailAdmins
```

---

## 📝 Tool Development

### What are the best practices for tool development?

1. **Use Type Hints**: Always use type hints for parameters and return values
2. **Write Comprehensive Docstrings**: Include detailed descriptions, examples, and notes
3. **Validate Inputs**: Validate all input parameters
4. **Handle Errors**: Use the framework's error handling patterns
5. **Add Telemetry**: Track custom metrics and events as needed
6. **Follow Naming Conventions**: Use consistent naming for tools and parameters
7. **Document Changes**: Maintain changelogs for breaking changes

### How do I handle errors in my tools?

Use the framework's error handling patterns:

```python
from platform.errors import MCPError, ValidationError, NotFoundError

def get_donor_data(donor_id: str) -> dict:
    if not donor_id:
        raise ValidationError("donor_id is required", code="DONOR-001")
    
    donor = find_donor(donor_id)
    if not donor:
        raise NotFoundError(f"Donor {donor_id} not found", code="DONOR-002")
    
    return donor
```

### How do I access Fabric data?

Use the framework's Fabric connectivity module:

```python
from platform.connectivity import FabricClient, SemanticModel

# Create Fabric client
fabric = FabricClient()

# Access semantic model
semantic_model = SemanticModel("DonorAnalytics")
result = semantic_model.execute("SELECT * FROM Donors WHERE Status = 'Active'")

# Or use direct Fabric API
result = fabric.execute_query("SELECT * FROM Donors")
```

### How do I use semantic models?

Semantic models provide a business-friendly way to access data:

```python
from platform.connectivity import SemanticModel

# Create semantic model
model = SemanticModel("DonorPortfolio")

# Execute query
result = model.execute(
    "SELECT DonorID, TotalContributions, LastContributionDate "
    "FROM DonorPortfolio WHERE Status = 'Active'"
)

# Get metadata
metadata = model.get_metadata()
```

---

## 🔄 Deployment

### How do I deploy to Azure Function App?

Deployment steps:

1. **Create infrastructure**: Deploy ARM/Bicep templates
2. **Configure Function App**: Set up application settings and connection strings
3. **Deploy code**: Deploy your Function App code
4. **Verify**: Test the deployed endpoints

See the [Function App Deployment Guide](deployment/function-app.md) for detailed instructions.

### How do I use ARM templates?

ARM templates provide declarative infrastructure deployment:

```bash
# Deploy using ARM template
az deployment group create \
    --name "mcp-deployment" \
    --resource-group mcp-prod-rg \
    --template-file ./templates/main.json \
    --parameters @./templates/parameters/prod.json
```

See the [ARM Templates Guide](deployment/arm-templates.md) for complete templates.

### How do I use Bicep templates?

Bicep provides a cleaner syntax for infrastructure deployment:

```bash
# Deploy using Bicep template
az deployment group create \
    --name "mcp-deployment" \
    --resource-group mcp-prod-rg \
    --template-file ./templates/main.bicep \
    --parameters @./templates/parameters/prod.bicepparam
```

See the [Bicep Templates Guide](deployment/bicep-templates.md) for complete templates.

### How do I set up CI/CD?

The framework includes pre-configured CI/CD pipelines for:

- **Azure DevOps**: YAML pipelines with multi-stage deployment
- **GitHub Actions**: Workflow files for automated deployment
- **GitLab CI/CD**: Pipeline configuration for GitLab

Example Azure DevOps pipeline:
```yaml
# azure-pipelines.yml
stages:
  - stage: Build
    jobs:
      - job: Build
        steps:
          - task: UsePythonVersion@0
          - script: pip install -r requirements.txt
          - script: pytest tests/
  
  - stage: Deploy
    jobs:
      - job: Deploy
        steps:
          - task: AzureFunctionApp@1
            inputs:
              appName: mcp-func-prod
              package: .
```

---

## 📚 Documentation

### How do I generate documentation?

Documentation is generated automatically from tool metadata:

```python
from platform.docs import DocumentationGenerator, OutputFormat

generator = DocumentationGenerator()

# Generate documentation for a tool
generator.generate_tool_docs(
    tool_name="GetDonorPortfolioHealth",
    output_formats=[OutputFormat.MARKDOWN, OutputFormat.HTML],
    output_dir="./docs/generated"
)

# Generate documentation for a domain
generator.generate_domain_docs(
    domain="DonorManagement",
    output_formats=[OutputFormat.MARKDOWN],
    output_dir="./docs/domains"
)
```

### How do I customize documentation templates?

Create custom templates in the `templates/docs/` directory:

```bash
templates/docs/
├── tool.md.j2              # Individual tool documentation
├── domain.md.j2            # Domain overview documentation
├── index.md.j2             # Main index page
├── api_spec.yaml.j2        # OpenAPI specification
└── styles.css              # HTML styling
```

### How do I add examples to my documentation?

Add examples in your tool's docstring:

```python
def get_donor_profile(donor_id: str) -> dict:
    """
    Retrieves donor profile information.
    
    Examples:
        >>> get_donor_profile("123e4567-e89b-12d3-a456-426614174000")
        {
            'donor_id': '123e4567-e89b-12d3-a456-426614174000',
            'name': 'John Doe',
            'email': 'john.doe@unhcr.org'
        }
    """
```

---

## 🔍 Troubleshooting

### My tool is not being registered in the catalog

Check the following:

1. **Tool decorator**: Ensure your tool has the `@tool` decorator
2. **Metadata**: Verify all required metadata fields are provided
3. **Catalog endpoint**: Check that the catalog endpoint is configured correctly
4. **Permissions**: Ensure the Function App has permission to register tools
5. **Logs**: Check the Function App logs for registration errors

### My tool is not appearing in search results

Check the following:

1. **Registration**: Verify the tool was successfully registered
2. **Sync status**: Check if the catalog sync is up to date
3. **Filters**: Verify your search filters are correct
4. **Classification**: Ensure the tool's classification allows it to be discovered

### I'm getting authentication errors

Check the following:

1. **Authentication configuration**: Verify Entra ID configuration
2. **Token validation**: Check that tokens are being validated correctly
3. **Audience**: Ensure the token audience matches your configuration
4. **Issuer**: Verify the token issuer is correct
5. **Permissions**: Check that the caller has the required permissions

### I'm getting authorization errors

Check the following:

1. **Permissions**: Verify the caller has the required permissions
2. **Role assignments**: Check that roles are assigned correctly
3. **Policy configuration**: Verify authorization policies are configured
4. **Token scope**: Ensure the token has the correct scope

### My Function App is not starting

Check the following:

1. **Configuration**: Verify all required application settings are configured
2. **Dependencies**: Ensure all Python dependencies are installed
3. **Logs**: Check the Function App logs for startup errors
4. **Connection strings**: Verify storage account connection strings are correct
5. **Identity**: Check that Managed Identity is configured correctly

---

## 📞 Support

### Where can I get help?

1. **Documentation**: Check this FAQ and the comprehensive documentation
2. **Examples**: Review the example implementations in the `examples/` directory
3. **Community**: Ask questions in the MCP community channels
4. **Issues**: Report issues in the GitHub repository
5. **Support Team**: Contact the MCP support team for production issues

### How do I report a bug?

To report a bug:

1. **Check existing issues**: Search for similar issues in the repository
2. **Create minimal reproduction**: Create a minimal example that reproduces the issue
3. **Include details**: Provide steps to reproduce, expected vs actual behavior
4. **Add logs**: Include relevant log output
5. **Submit issue**: Create a new issue in the GitHub repository

### How do I request a feature?

To request a feature:

1. **Check roadmap**: Review the project roadmap for planned features
2. **Describe use case**: Explain your use case and requirements
3. **Provide examples**: Include examples of how the feature would be used
4. **Submit request**: Create a feature request in the GitHub repository

---

## 📚 Additional Resources

- [MCP Platform Framework Documentation](README.md)
- [Architecture Overview](architecture/overview.md)
- [Getting Started](getting-started/README.md)
- [Module Documentation](modules/README.md)
- [Deployment Guide](deployment/overview.md)
- [Examples](examples/tool-development.md)

---

## 🔄 Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-05-01 | Initial FAQ |
| 1.1.0 | 2026-05-15 | Added deployment troubleshooting |
| 1.2.0 | 2026-06-01 | Added security section |
| 1.3.0 | 2026-06-15 | Added monitoring section |
