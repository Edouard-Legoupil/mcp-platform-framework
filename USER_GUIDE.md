# 🚀 MCP Framework - User Guide

**For MCP Server Developers**

This guide is for developers who want to **build their own MCP servers using this framework**. If you're looking to contribute to the framework itself, see [FRAMEWORK_DOCUMENTATION.md](FRAMEWORK_DOCUMENTATION.md).

---

## 📋 Table of Contents

1. [Quick Start](#-quick-start)
2. [Understanding the Framework](#-understanding-the-framework)
3. [Creating Your MCP Server](#-creating-your-mcp-server)
4. [Implementing Tools](#-implementing-tools)
5. [Defining Resources](#-defining-resources)
6. [Adding Prompt Templates](#-adding-prompt-templates)
7. [Configuration](#-configuration)
8. [Deployment](#-deployment)
9. [Testing](#-testing)
10. [Best Practices](#-best-practices)
11. [Troubleshooting](#-troubleshooting)

---

## 🌟 Quick Start

### Prerequisites
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
- [Python 3.11+](https://www.python.org/downloads/)
- [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local)

### 1. Clone and Setup
```bash
# Clone the template
git clone https://github.com/your-org/mcp-framework.git
cd mcp-framework

# Create your environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r src/azure/requirements.txt
```

### 2. Configure Your Server
```bash
# Copy the environment template
cp .env.example .env

# Edit .env with your configuration
nano .env

# Required: Set all Azure resource tags
APPLICATION_NAME=YourServerName
BUSINESS_OWNER=your-email@example.com
COST_CENTRE=YOUR-COST-CENTER
ENVIRONMENT=Development
PROJECT=YourProjectName
TECHNICAL_OWNER=tech-email@example.com
```

### 3. Create Your First Tool
```bash
# Create a new tool file
mkdir -p my_domain/tools
cat > my_domain/tools/my_tool.py << 'EOF'
def greet_user(name: str) -> dict:
    """Greets a user by name"""
    return {"message": f"Hello, {name}!"}
EOF
```

### 4. Register Your Tool
Edit `platform/registration/registry.py`:
```python
from my_domain.tools.my_tool import greet_user

TOOLS = [
    {
        "name": "greet_user",
        "description": "Greets a user by name",
        "handler": "my_domain.tools.my_tool.greet_user",
        "domain": "my_domain",
        "version": "1.0.0"
    }
]
```

### 5. Deploy to Azure
```bash
# Run the deployment script
./deploy/scripts/deploy.sh
```

---

## 🏗️ Understanding the Framework

### What the Framework Provides

The MCP Framework handles all the **infrastructure concerns** so you can focus on your **business logic**:

#### ✅ Framework Handles (You Don't Need to Implement)
- **Authentication & Authorization** - Entra ID, JWT validation, RBAC
- **Telemetry** - Automatic logging, metrics, tracing
- **Error Handling** - Standardized error responses and recovery
- **Configuration** - Environment variables, Key Vault integration
- **Data Connectivity** - Fabric, Warehouse, Lakehouse connectors
- **Audit Logging** - Immutable audit trail for all operations
- **Data Classification** - Automatic data governance controls
- **MCP Protocol Compliance** - All required endpoints implemented

#### 🎯 You Implement (Your Domain Logic)
- **Tools** - Your business functions
- **Resources** - Your data sources
- **Prompt Templates** - Your Copilot Studio templates
- **Domain Ontologies** - Your semantic definitions

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    YOUR MCP SERVER                              │
├─────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    FRAMEWORK LAYER                        ││
│  │  ✅ Authentication, Authorization, Telemetry, Errors     ││
│  │  ✅ Configuration, Connectivity, Audit, Classification    ││
│  └─────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    YOUR DOMAIN LAYER                       ││
│  │  🎯 Tools, Resources, Prompts, Ontologies               ││
│  │  🎯 Business Logic, Domain Models                        ││
│  └─────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 AZURE FUNCTIONS v4                             │
│  ✅ HTTP Triggers, Function App, Storage, Application Insights  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Creating Your MCP Server

### Project Structure

```bash
mcp-framework/
├── .env.example                    # Environment template
├── .funcignore                     # Deployment ignore
├── USER_GUIDE.md                   # This guide
├── FRAMEWORK_DOCUMENTATION.md      # Framework internals
├── TEMPLATE_GUIDE.md               # Quick start template
│
├── src/
│   └── azure/
│       ├── function_app.py         # ✅ Framework - Main entry point
│       ├── host.json               # ✅ Framework - Azure config
│       └── requirements.txt        # ✅ Framework - Dependencies
│
├── platform/                       # ✅ Framework - Core services
│   ├── registration/               # Tool registration
│   ├── catalog/                    # Resource catalog
│   └── template/                   # Prompt templates
│
└── my_domain/                      # 🎯 YOUR CODE - Create this!
    ├── tools/                      # Your tool implementations
    │   ├── __init__.py
    │   └── my_tool.py
    ├── resources/                  # Your resource definitions
    │   └── my_resource.py
    └── prompts/                     # Your prompt templates
        └── my_prompt.py
```

### Step 1: Create Your Domain Directory

```bash
# Create your domain directory
mkdir -p my_domain/tools my_domain/resources my_domain/prompts

# Create package initialization files
touch my_domain/__init__.py my_domain/tools/__init__.py my_domain/resources/__init__.py my_domain/prompts/__init__.py
```

### Step 2: Update Function App to Include Your Domain

Edit `src/azure/function_app.py` to import your domain:

```python
# Add at the top with other imports
from my_domain.tools import my_tool  # Import your tools module

# The framework will automatically discover tools registered in your domain
```

---

## ⚒️ Implementing Tools

### Tool Basics

A **Tool** is a function that can be executed via the MCP protocol. Tools are the primary way users interact with your MCP server.

### Simple Tool Example

```python
# my_domain/tools/greeting_tool.py
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def greet_user(name: str, greeting: str = "Hello") -> Dict[str, Any]:
    """
    Greets a user with a customizable greeting.
    
    Args:
        name: The user's name
        greeting: Optional greeting word (default: "Hello")
        
    Returns:
        Dict with greeting message
    """
    message = f"{greeting}, {name}!"
    logger.info(f"Greeted user: {name}")
    
    return {
        "message": message,
        "success": True
    }
```

### Tool with Complex Logic

```python
# my_domain/tools/data_processor.py
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

def process_data(items: List[Dict], filter_value: str = None) -> Dict[str, Any]:
    """
    Processes a list of items with optional filtering.
    
    Args:
        items: List of dictionaries to process
        filter_value: Optional value to filter by
        
    Returns:
        Dict with processed results
    """
    if filter_value:
        filtered_items = [item for item in items if filter_value in str(item)]
    else:
        filtered_items = items
    
    result = {
        "original_count": len(items),
        "filtered_count": len(filtered_items),
        "items": filtered_items,
        "success": True
    }
    
    logger.info(f"Processed {len(items)} items, returned {len(filtered_items)}")
    return result
```

### Tool Registration

Edit `platform/registration/registry.py`:

```python
from my_domain.tools.greeting_tool import greet_user
from my_domain.tools.data_processor import process_data

TOOLS = [
    {
        "name": "greet_user",
        "description": "Greets a user with a customizable greeting",
        "handler": "my_domain.tools.greeting_tool.greet_user",
        "domain": "my_domain",
        "version": "1.0.0",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "User's name"},
                "greeting": {"type": "string", "default": "Hello", "description": "Greeting word"}
            },
            "required": ["name"]
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "success": {"type": "boolean"}
            }
        }
    },
    {
        "name": "process_data",
        "description": "Processes a list of items with optional filtering",
        "handler": "my_domain.tools.data_processor.process_data",
        "domain": "my_domain",
        "version": "1.0.0",
        "input_schema": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of items to process"
                },
                "filter_value": {
                    "type": "string",
                    "description": "Optional filter value",
                    "default": None
                }
            },
            "required": ["items"]
        }
    }
]
```

### Tool Best Practices

✅ **Do:**
- Use type hints for parameters and return values
- Include comprehensive docstrings
- Add logging for debugging
- Validate input parameters
- Return consistent response formats
- Handle errors gracefully

❌ **Don't:**
- Include business logic in tool registration
- Access external services directly (use framework connectors)
- Bypass framework authentication/authorization
- Modify framework core files
- Store sensitive data in tool code

---

## 📚 Defining Resources

### Resource Basics

**Resources** are data sources that can be accessed via the MCP protocol. They represent your domain's data entities.

### Resource Example

```python
# my_domain/resources/donor_resource.py
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from platform.catalog.models import Resource

@dataclass
class DonorResource:
    """Represents a donor in the system"""
    name: str
    description: str
    type: str = "donor"
    uri: str
    mime_type: str = "application/json"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "uri": self.uri,
            "mimeType": self.mime_type
        }

# List of resources to register
RESOURCES: List[Resource] = [
    Resource(
        name="donors",
        description="List of all donors",
        type="collection",
        uri="/api/donors",
        mime_type="application/json"
    ),
    Resource(
        name="donor/{id}",
        description="Individual donor details",
        type="item",
        uri="/api/donors/{id}",
        mime_type="application/json"
    )
]
```

### Resource Access Implementation

```python
# my_domain/resources/donor_handler.py
from typing import Dict, Any, Optional
from platform.catalog.client import get_catalog_client

class DonorResourceHandler:
    """Handles access to donor resources"""
    
    def __init__(self):
        self.client = get_catalog_client()
    
    def get_donor(self, donor_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific donor by ID"""
        # Use framework's catalog client to access data
        resource = self.client.get_resource_by_name(f"donor/{donor_id}")
        if resource:
            return self._fetch_donor_data(donor_id)
        return None
    
    def list_donors(self) -> List[Dict[str, Any]]:
        """List all donors"""
        return self._fetch_all_donors()
    
    def _fetch_donor_data(self, donor_id: str) -> Dict[str, Any]:
        """Internal method to fetch donor data"""
        # Use framework's connectivity layer
        from platform.connectivity.warehouse import query_warehouse
        
        query = f"SELECT * FROM donors WHERE id = '{donor_id}'"
        result = query_warehouse(query)
        return result
```

---

## 📝 Adding Prompt Templates

### Prompt Template Basics

**Prompt Templates** enable Copilot Studio integration by providing reusable prompt patterns.

### Prompt Template Example

```python
# my_domain/prompts/report_generator.py
from typing import Dict, Any, List
from dataclasses import dataclass
from platform.template.models import PromptTemplate

@dataclass
class ReportPrompt:
    """Prompt template for generating reports"""
    name: str
    description: str
    template: str
    arguments: List[str]

# Define your prompt templates
PROMPTS: List[PromptTemplate] = [
    PromptTemplate(
        name="generate_donor_report",
        description="Generate a comprehensive donor report",
        template="""
Generate a comprehensive report about donor {donor_id} for the {report_type} purpose.

Include the following sections:
1. Donor Overview
2. Contribution History
3. Engagement Metrics
4. Recommendations

Format the response as a professional business report.
""",
        arguments=["donor_id", "report_type"]
    ),
    PromptTemplate(
        name="summarize_campaign",
        description="Summarize a fundraising campaign",
        template="""
Summarize the {campaign_name} campaign that ran from {start_date} to {end_date}.

Include:
- Total funds raised
- Number of donors
- Average donation amount
- Top 3 donors
- Campaign highlights
""",
        arguments=["campaign_name", "start_date", "end_date"]
    )
]
```

### Prompt Template with Dynamic Content

```python
# my_domain/prompts/dynamic_prompt.py
from typing import Dict, Any
from platform.template.template_generator import get_template_generator

def generate_custom_prompt(prompt_name: str, context: Dict[str, Any]) -> str:
    """Generate a prompt with dynamic context"""
    generator = get_template_generator()
    prompt = generator.get_prompt_by_name(prompt_name)
    
    if not prompt:
        raise ValueError(f"Prompt '{prompt_name}' not found")
    
    # Apply context to template
    template = prompt.template
    for key, value in context.items():
        template = template.replace(f"{{{{{key}}}}}", str(value))
    
    return template
```

---

## ⚙️ Configuration

### Environment Variables

The framework uses environment variables for configuration. See `.env.example` for all available options.

#### Required Variables
```bash
# Azure Resource Configuration
AZURE_RESOURCE_GROUP=your-resource-group
AZURE_LOCATION=eastus
AZURE_FUNCTION_APP_NAME=your-function-app
AZURE_STORAGE_ACCOUNT_NAME=yourstorageaccount

# Required Azure Resource Tags
APPLICATION_NAME=YourAppName
BUSINESS_OWNER=your-email@example.com
COST_CENTRE=YOUR-COST-CENTER
ENVIRONMENT=Development
PROJECT=YourProjectName
TECHNICAL_OWNER=tech-email@example.com
```

#### MCP Server Configuration
```bash
# Server metadata
MCP_SERVER_NAME="My MCP Server"
MCP_SERVER_VERSION="1.0.0"
MCP_PROTOCOL_VERSION="2024-11-05"
MCP_ENVIRONMENT="Development"
MCP_DOMAIN="YourDomain"

# Feature flags
MCP_ENABLE_TELEMETRY=true
MCP_ENABLE_AUDIT=true
MCP_ENABLE_AUTH=false
MCP_ENABLE_AUTHORIZATION=false
MCP_ENABLE_CLASSIFICATION=false
```

### Local Development Configuration

Create `local.settings.json` from the example:

```bash
cp local.settings.json.example local.settings.json
```

This file contains local development settings for Azure Functions Core Tools.

---

## ☁️ Deployment

### Quick Deployment

```bash
# Run the deployment script
./deploy/scripts/deploy.sh
```

The script will:
1. Validate your configuration
2. Create all required Azure resources
3. Apply required tags to all resources
4. Deploy your MCP server
5. Verify the deployment

### Manual Deployment Steps

#### 1. Create Azure Resources

```bash
# Login to Azure
az login

# Create resource group with tags
az group create \
    --name $AZURE_RESOURCE_GROUP \
    --location $AZURE_LOCATION \
    --tags APPLICATION_NAME=$APPLICATION_NAME \
             BUSINESS_OWNER=$BUSINESS_OWNER \
             COST_CENTRE=$COST_CENTRE \
             ENVIRONMENT=$ENVIRONMENT \
             PROJECT=$PROJECT \
             TECHNICAL_OWNER=$TECHNICAL_OWNER

# Create storage account
az storage account create \
    --name $AZURE_STORAGE_ACCOUNT_NAME \
    --resource-group $AZURE_RESOURCE_GROUP \
    --location $AZURE_LOCATION \
    --sku Standard_LRS \
    --tags APPLICATION_NAME=$APPLICATION_NAME \
             BUSINESS_OWNER=$BUSINESS_OWNER \
             COST_CENTRE=$COST_CENTRE \
             ENVIRONMENT=$ENVIRONMENT \
             PROJECT=$PROJECT \
             TECHNICAL_OWNER=$TECHNICAL_OWNER
```

#### 2. Create Function App

```bash
# Create Function App
az functionapp create \
    --name $AZURE_FUNCTION_APP_NAME \
    --resource-group $AZURE_RESOURCE_GROUP \
    --consumption-plan-location $AZURE_LOCATION \
    --runtime python \
    --runtime-version 3.11 \
    --functions-version 4 \
    --storage-account $AZURE_STORAGE_ACCOUNT_NAME \
    --os-type Linux \
    --tags APPLICATION_NAME=$APPLICATION_NAME \
             BUSINESS_OWNER=$BUSINESS_OWNER \
             COST_CENTRE=$COST_CENTRE \
             ENVIRONMENT=$ENVIRONMENT \
             PROJECT=$PROJECT \
             TECHNICAL_OWNER=$TECHNICAL_OWNER
```

#### 3. Deploy Your Code

```bash
# Deploy from src/azure directory
cd src/azure
func azure functionapp publish $AZURE_FUNCTION_APP_NAME
```

### Deployment Configuration

#### Remote Build (Recommended)
```bash
# In .env
DEPLOYMENT_METHOD=remote
ENABLE_ORYX_BUILD=true
SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

#### Local Build
```bash
# In .env
DEPLOYMENT_METHOD=local
ENABLE_ORYX_BUILD=false
SCM_DO_BUILD_DURING_DEPLOYMENT=false

# Build locally first
pip install -r requirements.txt -t .python_packages

# Deploy without build
func azure functionapp publish $AZURE_FUNCTION_APP_NAME --no-build
```

---

## 🧪 Testing

### Local Testing

```bash
# Start Azure Functions locally
cd src/azure
func start

# Test your endpoints
curl http://localhost:7071/mcp/health
curl http://localhost:7071/mcp/metadata
curl -X POST http://localhost:7071/mcp/tools/greet_user \
  -H "Content-Type: application/json" \
  -d '{"name": "John"}'
```

### Testing Your Tools

```python
# test_my_tools.py
import unittest
from my_domain.tools.greeting_tool import greet_user
from my_domain.tools.data_processor import process_data

class TestMyTools(unittest.TestCase):
    
    def test_greet_user(self):
        result = greet_user("Alice")
        self.assertEqual(result["message"], "Hello, Alice!")
        self.assertTrue(result["success"])
    
    def test_greet_user_custom_greeting(self):
        result = greet_user("Bob", greeting="Hi")
        self.assertEqual(result["message"], "Hi, Bob!")
    
    def test_process_data(self):
        items = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
        result = process_data(items)
        self.assertEqual(result["original_count"], 2)
        self.assertEqual(result["filtered_count"], 2)
        self.assertTrue(result["success"])
    
    def test_process_data_with_filter(self):
        items = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
        result = process_data(items, filter_value="Item 1")
        self.assertEqual(result["filtered_count"], 1)

if __name__ == "__main__":
    unittest.main()
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/unit/test_my_tools.py

# Run with coverage
python -m pytest --cov=my_domain tests/
```

---

## 🎯 Best Practices

### Project Organization

✅ **Do:**
- Keep your domain code in a separate directory (`my_domain/`, `your_org/`, etc.)
- Use clear, descriptive names for tools and resources
- Follow the existing framework patterns
- Document your tools with docstrings and schemas
- Use type hints for better code maintainability

❌ **Don't:**
- Modify framework core files (`platform/`, `src/azure/`) unless contributing
- Mix framework code with your domain code
- Store secrets in code (use environment variables or Key Vault)
- Create tools without proper error handling
- Bypass framework authentication/authorization

### Tool Development

1. **Start Small** - Create simple tools first, then add complexity
2. **Test Locally** - Always test tools locally before deploying
3. **Add Validation** - Validate inputs and handle edge cases
4. **Use Logging** - Add appropriate logging for debugging
5. **Document** - Include docstrings and schema definitions

### Performance

1. **Optimize Data Access** - Use framework connectors efficiently
2. **Cache Results** - Cache frequent queries when appropriate
3. **Batch Operations** - Process data in batches when possible
4. **Async Operations** - Use async/await for I/O-bound operations
5. **Monitor Usage** - Use framework telemetry to track performance

### Security

1. **Never Store Secrets** - Use environment variables or Azure Key Vault
2. **Validate Inputs** - Always validate and sanitize user inputs
3. **Use Framework Auth** - Leverage framework authentication/authorization
4. **Classify Data** - Use framework data classification for sensitive data
5. **Audit Operations** - Framework automatically audits all operations

---

## 🐛 Troubleshooting

### Common Issues

#### "0 functions found" Error
**Cause:** Multiple FunctionApp instances or incorrect entry point
**Solution:** Ensure only one `func.FunctionApp()` instance exists in `src/azure/function_app.py`

#### Oryx Build Hanging
**Cause:** Rust-dependent packages (cryptography>=42.0.0)
**Solution:** The framework already pins `python-jose[cryptography]>=3.3.0,<42.0.0` to avoid this

#### Deployment Stuck
**Cause:** Missing AzureWebJobsStorage connection string
**Solution:** Ensure storage account is created and connection string is set in Function App settings

#### Tool Not Found
**Cause:** Tool not registered or incorrect handler path
**Solution:** Check `platform/registration/registry.py` for correct tool registration

### Debugging Commands

```bash
# Check Function App status
az functionapp show --name $AZURE_FUNCTION_APP_NAME --resource-group $AZURE_RESOURCE_GROUP

# View deployment logs
az webapp deployment log show --name $AZURE_FUNCTION_APP_NAME --resource-group $AZURE_RESOURCE_GROUP

# Check Function App settings
az functionapp config appsettings list --name $AZURE_FUNCTION_APP_NAME --resource-group $AZURE_RESOURCE_GROUP

# Test locally
func start --verbose

# Check function discovery
func azure functionapp function list --name $AZURE_FUNCTION_APP_NAME --resource-group $AZURE_RESOURCE_GROUP
```

### Getting Help

1. **Check this guide** - Most common questions are answered here
2. **Check FRAMEWORK_DOCUMENTATION.md** - For framework internals
3. **Check TEMPLATE_GUIDE.md** - For quick start examples
4. **Review examples** - In `docs/examples/` directory
5. **Open an issue** - If you encounter bugs or need features

---

## 📚 Additional Resources

### MCP Server Development
- [Framework Documentation (FRAMEWORK_DOCUMENTATION.md)](FRAMEWORK_DOCUMENTATION.md) - **For Framework Contributors**
- [Template Guide (TEMPLATE_GUIDE.md)](TEMPLATE_GUIDE.md) - **Quick Start Examples**
- [Main README (README.md)](README.md) - **Project Overview**

### Data Source Integration
- **[Fabric Integration Guide (FABRIC_INTEGRATION_GUIDE.md)](FABRIC_INTEGRATION_GUIDE.md)** - **🎯 Connect to Microsoft Fabric Semantic Models**
  - Step-by-step Fabric connection setup
  - Semantic model tool creation
  - Resource exposure for Fabric data
  - Complete end-to-end examples
  - Troubleshooting guide

### External Documentation
- [Azure Functions Documentation](https://learn.microsoft.com/en-us/azure/azure-functions/) - **Azure Functions Official Docs**
- [MCP Protocol Specification](https://github.com/modelcontextprotocol/specification) - **MCP Official Spec**
- [Microsoft Fabric Documentation](https://learn.microsoft.com/en-us/fabric/) - **Fabric Official Docs**

---

## 🎉 Next Steps

1. ✅ **Read this guide** - You're here!
2. 📁 **Create your domain directory** - `my_domain/`
3. ⚒️ **Implement your first tool** - Start with a simple function
4. 📝 **Register your tool** - Add to `platform/registration/registry.py`
5. ☁️ **Deploy to Azure** - Run `./deploy/scripts/deploy.sh`
6. 🧪 **Test your server** - Verify all endpoints work
7. 🚀 **Build more tools** - Expand your MCP server capabilities

---

**💡 Remember**: The framework handles all the infrastructure. You focus on your business logic. If you get stuck, check the examples and remember - you're only responsible for your domain code in your domain directory!
