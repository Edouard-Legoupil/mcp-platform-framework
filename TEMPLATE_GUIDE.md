# MCP Framework - Azure Functions Template Guide

## 🎯 Overview

This repository serves as a **template for creating MCP (Model Context Protocol) servers** that can be deployed as **Azure Functions** and integrated with **Microsoft Copilot** and **Copilot Studio**.

## 🚀 Quick Start

### 1. Clone the Template

```bash
# Clone the repository
git clone https://github.com/Edouard-Legoupil/mcp-platform-framework.git your-mcp-server
cd your-mcp-server

# Remove git history to start fresh
rm -rf .git

# Initialize new git repository
git init
```

### 2. Configure Your MCP Server

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env

# Update project name in pyproject.toml (if exists)
# Update server name in src/azure/function_app.py
```

### 3. Add Your Tools

Create your MCP tools in the `tools/` directory:

```bash
# Create tools directory
mkdir -p tools

# Create a sample tool
cat > tools/your_tool.py << 'EOF'
"""
Your MCP Tool Implementation
"""
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def your_tool_function(arg1: str, arg2: int = 10) -> Dict[str, Any]:
    """
    Your tool implementation.
    
    Args:
        arg1: First argument (required)
        arg2: Second argument (optional, default: 10)
    
    Returns:
        Dictionary with tool results
    """
    logger.info(f"Executing your_tool with arg1={arg1}, arg2={arg2}")
    
    # Your tool logic here
    result = {
        "status": "success",
        "message": f"Processed {arg1} with value {arg2}",
        "data": {"arg1": arg1, "arg2": arg2, "sum": len(arg1) + arg2}
    }
    
    return result
EOF
```

### 4. Register Your Tools

Edit `src/azure/function_app.py` to register your tools:

```python
# Add to the imports at the top
from tools.your_tool import your_tool_function

# Or better, use the platform registry (recommended)
# The framework will automatically discover tools in the tools/ directory
```

### 5. Deploy to Azure

```bash
# Make deploy script executable
chmod +x deploy/scripts/deploy.sh

# Deploy
./deploy/scripts/deploy.sh
```

### 6. Test Your MCP Server

```bash
# Test health endpoint
curl https://your-function-app.azurewebsites.net/mcp/health

# List tools
curl https://your-function-app.azurewebsites.net/mcp/tools

# Execute your tool
curl -X POST https://your-function-app.azurewebsites.net/mcp/tools/your_tool/execute \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"arg1": "test", "arg2": 5}}'
```

---

## 📁 Template Structure

```
mcp-framework/
├── src/
│   └── azure/
│       ├── __init__.py          # Package initialization
│       ├── function_app.py      # Main Function App with MCP endpoints
│       ├── host.json            # Azure Functions configuration
│       └── requirements.txt     # Production dependencies
├── tools/                      # ✨ YOUR TOOLS GO HERE ✨
│   ├── __init__.py            # Tools package initialization
│   └── your_tool.py           # Example tool implementation
├── .env.example                # Environment variables template
├── .funcignore                 # Deployment ignore file
├── .gitignore                 # Git ignore file
├── TEMPLATE_GUIDE.md          # This guide
├── pyproject.toml             # Python project configuration (optional)
└── deploy/
    ├── README.md               # Deployment guide
    └── scripts/
        └── deploy.sh            # Deployment script
```

---

## 🛠️ Template Customization

### 1. Update Server Metadata

Edit `src/azure/function_app.py`:

```python
# Update these constants at the top of the file
MCP_SERVER_NAME = "Your MCP Server Name"
MCP_SERVER_VERSION = "1.0.0"
MCP_PROTOCOL_VERSION = "2024-11-05"
```

### 2. Add Custom Configuration

Add your custom environment variables to `.env.example`:

```bash
# Custom configuration
YOUR_CUSTOM_SETTING=your-default-value
ANOTHER_SETTING=another-value
```

Then access them in your tools:

```python
import os

def your_tool_function():
    custom_setting = os.getenv('YOUR_CUSTOM_SETTING', 'default')
    # Use custom_setting in your logic
```

### 3. Add Dependencies

Add your tool dependencies to `src/azure/requirements.txt`:

```bash
# Your custom dependencies
your-package>=1.0.0
another-package>=2.0.0
```

**Important:** Avoid packages that require Rust compilation (like `cryptography>=42.0.0`) as they can hang Oryx builds.

### 4. Customize Deployment

Edit `deploy/scripts/deploy.sh` to add custom deployment steps:

```bash
# Add custom pre-deployment steps
pre_deploy() {
    log_info "Running custom pre-deployment steps..."
    # Your custom logic here
}

# Add custom post-deployment steps
post_deploy() {
    log_info "Running custom post-deployment steps..."
    # Your custom logic here
}

# Call them in main()
main() {
    pre_deploy
    # ... existing deployment code ...
    post_deploy
}
```

---

## 📦 Tool Development Guide

### Creating a New Tool

1. **Create the tool file** in `tools/` directory:

```python
# tools/your_tool.py
"""
Your MCP Tool

This tool performs a specific action and can be called via the MCP protocol.
"""
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def your_tool_function(
    required_arg: str,
    optional_arg: Optional[int] = None
) -> Dict[str, Any]:
    """
    Your tool implementation.
    
    This function will be called when users invoke your tool through MCP.
    
    Args:
        required_arg: A required string argument
        optional_arg: An optional integer argument
    
    Returns:
        Dictionary containing the tool's response
        
    Raises:
        ValueError: If arguments are invalid
        Exception: For any other errors
    """
    # Validate arguments
    if not required_arg:
        raise ValueError("required_arg cannot be empty")
    
    # Your tool logic here
    result = {
        "status": "success",
        "input": {"required_arg": required_arg, "optional_arg": optional_arg},
        "output": {"result": f"Processed: {required_arg}"}
    }
    
    logger.info(f"Tool executed with: {result}")
    return result
```

2. **Register the tool** (automatic discovery recommended):

The framework automatically discovers tools in the `tools/` directory. Each function in a tool module will be registered as a separate MCP tool.

Or manually register in `src/azure/function_app.py`:

```python
# Import your tool
from tools.your_tool import your_tool_function

# The framework will automatically register it
# Or you can manually add it to the tool registry
```

### Tool Best Practices

1. **Use type hints** - Helps with documentation and validation
2. **Validate inputs** - Raise `ValueError` for invalid arguments
3. **Return consistent format** - Always return a dictionary
4. **Use logging** - Helps with debugging
5. **Handle errors gracefully** - Return error information in the response
6. **Keep tools focused** - Each tool should do one thing well

### Example Tool with Complex Logic

```python
# tools/data_processor.py
"""
Data Processing Tool

Processes data from various sources and returns structured results.
"""
from typing import Dict, Any, List, Optional
import logging
import json

logger = logging.getLogger(__name__)


def process_data(
    data: Dict[str, Any],
    format: str = "json",
    include_metadata: bool = True
) -> Dict[str, Any]:
    """
    Process data and return structured results.
    
    Args:
        data: Input data dictionary
        format: Output format (json, csv, etc.)
        include_metadata: Whether to include metadata in output
    
    Returns:
        Processed data with results
    """
    try:
        # Process the data
        processed = {
            "original_size": len(json.dumps(data)),
            "fields": list(data.keys()),
            "values": list(data.values())
        }
        
        # Add metadata if requested
        if include_metadata:
            processed["metadata"] = {
                "timestamp": datetime.utcnow().isoformat(),
                "format": format
            }
        
        return {
            "status": "success",
            "processed": processed,
            "format": format
        }
        
    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "input": {"data": str(data)[:100], "format": format}
        }
```

---

## 🔧 Framework Customization

### Customizing MCP Endpoints

You can customize the MCP protocol endpoints in `src/azure/function_app.py`:

```python
@app.function_name(name="custom_endpoint")
@app.route(route="custom/path", methods=["GET", "POST"])
def custom_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    Custom MCP endpoint for your specific needs.
    """
    # Your custom logic here
    return func.HttpResponse(
        json.dumps({"message": "Custom endpoint response"}),
        status_code=200,
        mimetype='application/json'
    )
```

### Adding Custom Middleware

Add middleware for authentication, logging, etc.:

```python
# In src/azure/function_app.py

@app.middleware
def custom_middleware(req: func.HttpRequest, next_func):
    """
    Custom middleware for all requests.
    """
    # Pre-processing logic
    logger.info(f"Request: {req.method} {req.path}")
    
    # Call next middleware/function
    response = next_func(req)
    
    # Post-processing logic
    logger.info(f"Response: {response.status_code}")
    
    return response

# Apply middleware to all functions
app.use_middleware(custom_middleware)
```

---

## 📊 Testing Your MCP Server

### Local Testing

```bash
# Test imports
python -c "import sys; sys.path.insert(0, 'src'); from azure.function_app import app; print('✓ Imports successful')"

# Test tool execution locally
python -c "
import sys
sys.path.insert(0, 'src')
sys.path.insert(0, 'tools')
from your_tool import your_tool_function
result = your_tool_function('test', 5)
print('Tool result:', result)
"
```

### Azure Testing

```bash
# Test health endpoint
curl https://your-function-app.azurewebsites.net/mcp/health

# Test metadata endpoint
curl https://your-function-app.azurewebsites.net/mcp/metadata

# List all tools
curl https://your-function-app.azurewebsites.net/mcp/tools

# Get tool metadata
curl https://your-function-app.azurewebsites.net/mcp/tools/your_tool

# Execute tool
curl -X POST https://your-function-app.azurewebsites.net/mcp/tools/your_tool/execute \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"arg1": "value1", "arg2": 10}}'
```

---

## 🛡️ Error Handling

### Tool Error Handling

```python
def your_tool_function(arg: str) -> Dict[str, Any]:
    """
    Tool with proper error handling.
    """
    try:
        # Validate input
        if not arg:
            raise ValueError("Argument cannot be empty")
        
        # Process
        result = {"status": "success", "data": arg.upper()}
        return result
        
    except ValueError as e:
        # Return user-friendly error
        return {
            "status": "error",
            "error_type": "validation_error",
            "error_message": str(e),
            "suggestions": ["Provide a non-empty string argument"]
        }
    except Exception as e:
        # Return generic error
        return {
            "status": "error",
            "error_type": "internal_error",
            "error_message": "An unexpected error occurred",
            "error_details": str(e)  # Only in development
        }
```

### HTTP Error Handling

```python
@app.function_name(name="protected_endpoint")
@app.route(route="protected", methods=["GET"])
def protected_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    Endpoint with authentication.
    """
    # Check for API key
    api_key = req.headers.get("X-API-Key")
    expected_key = os.getenv("API_KEY")
    
    if api_key != expected_key:
        return func.HttpResponse(
            json.dumps({"error": "Unauthorized"}),
            status_code=401,
            mimetype='application/json'
        )
    
    # Process request
    return func.HttpResponse(
        json.dumps({"status": "success"}),
        status_code=200,
        mimetype='application/json'
    )
```

---

## 📚 Advanced Features

### Resource Access

Implement resource endpoints for data access:

```python
@app.function_name(name="get_resource")
@app.route(route="mcp/resources/{resource_name}", methods=["GET"])
def get_resource(req: func.HttpRequest, resource_name: str) -> func.HttpResponse:
    """
    Custom resource access endpoint.
    """
    # Your resource access logic
    if resource_name == "config":
        return func.HttpResponse(
            json.dumps({"name": "config", "type": "configuration", "data": {"key": "value"}}),
            status_code=200,
            mimetype='application/json'
        )
    else:
        return func.HttpResponse(
            json.dumps({"error": f"Resource '{resource_name}' not found"}),
            status_code=404,
            mimetype='application/json'
        )
```

### Prompt Templates

Add custom prompt templates:

```python
@app.function_name(name="custom_prompt")
@app.route(route="mcp/prompts/custom", methods=["GET"])
def custom_prompt(req: func.HttpRequest) -> func.HttpResponse:
    """
    Custom prompt template.
    """
    prompt = {
        "name": "custom_prompt",
        "description": "A custom prompt template",
        "template": "Analyze the following data: {data}",
        "arguments": [
            {"name": "data", "type": "string", "description": "Data to analyze"}
        ]
    }
    
    return func.HttpResponse(
        json.dumps(prompt),
        status_code=200,
        mimetype='application/json'
    )
```

---

## 🚀 Deployment Best Practices

### 1. Use Environment Variables

Always use environment variables for configuration:

```python
# Good
API_KEY = os.getenv("API_KEY", "default-value")

# Bad
API_KEY = "hardcoded-key"
```

### 2. Validate Configuration

Add validation in your deployment script:

```bash
# In deploy/scripts/deploy.sh
validate_configuration() {
    if [ -z "$API_KEY" ]; then
        log_error "API_KEY is required"
        exit 1
    fi
    # ... more validations
}
```

### 3. Use Remote Build

Remote build (Oryx) is recommended for automatic dependency resolution:

```bash
# In deploy.sh
DEPLOYMENT_METHOD=remote  # Default
```

### 4. Monitor Deployments

Check deployment logs:

```bash
# Stream logs
az webapp log tail --name your-function-app --resource-group your-rg

# Get deployment logs
az functionapp deployment log show --name your-function-app --resource-group your-rg
```

### 5. Test Before Deployment

Always test locally before deploying:

```bash
# Test imports
python -c "from src.azure.function_app import app; print('✓ Imports OK')"

# Test tool execution
python -c "from tools.your_tool import your_function; print(your_function('test'))"
```

---

## 📖 Examples

### Example 1: Simple Calculator Tool

```python
# tools/calculator.py
"""
Simple Calculator Tool
"""
from typing import Dict, Any


def add(a: float, b: float) -> Dict[str, Any]:
    """Add two numbers."""
    return {"status": "success", "result": a + b}


def subtract(a: float, b: float) -> Dict[str, Any]:
    """Subtract two numbers."""
    return {"status": "success", "result": a - b}


def multiply(a: float, b: float) -> Dict[str, Any]:
    """Multiply two numbers."""
    return {"status": "success", "result": a * b}


def divide(a: float, b: float) -> Dict[str, Any]:
    """Divide two numbers."""
    if b == 0:
        return {"status": "error", "error": "Division by zero"}
    return {"status": "success", "result": a / b}
```

### Example 2: Data Query Tool

```python
# tools/data_query.py
"""
Data Query Tool

Queries data from various sources.
"""
from typing import Dict, Any, List, Optional
import requests
import os


def query_api(
    endpoint: str,
    params: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Query an external API.
    
    Args:
        endpoint: API endpoint URL
        params: Query parameters
    
    Returns:
        API response data
    """
    try:
        api_key = os.getenv("API_KEY")
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        
        response = requests.get(endpoint, params=params, headers=headers)
        response.raise_for_status()
        
        return {
            "status": "success",
            "data": response.json(),
            "endpoint": endpoint
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error": str(e),
            "endpoint": endpoint
        }
```

### Example 3: File Processing Tool

```python
# tools/file_processor.py
"""
File Processing Tool

Processes files from Azure Blob Storage.
"""
from typing import Dict, Any
from azure.storage.blob import BlobServiceClient
import os


def process_blob(
    container: str,
    blob_name: str
) -> Dict[str, Any]:
    """
    Process a blob from Azure Blob Storage.
    
    Args:
        container: Blob container name
        blob_name: Blob name
    
    Returns:
        Processed blob data
    """
    try:
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        blob_client = blob_service_client.get_blob_client(container=container, blob=blob_name)
        blob_data = blob_client.download_blob().readall()
        
        # Process the blob data
        processed = {
            "original_size": len(blob_data),
            "content_type": blob_client.get_blob_properties().content_type,
            "preview": blob_data[:100].decode('utf-8', errors='replace')
        }
        
        return {"status": "success", "data": processed}
        
    except Exception as e:
        return {"status": "error", "error": str(e)}
```

---

## 🎯 Template Customization Checklist

Before using this template, customize the following:

- [ ] **Project Name** - Update in `.env.example` and documentation
- [ ] **Server Metadata** - Update `MCP_SERVER_NAME`, `MCP_SERVER_VERSION` in `function_app.py`
- [ ] **Tool Directory** - Add your tools in `tools/`
- [ ] **Dependencies** - Add your dependencies to `requirements.txt`
- [ ] **Environment Variables** - Add your custom variables to `.env.example`
- [ ] **Deployment Configuration** - Update default values in `deploy.sh`
- [ ] **Documentation** - Update README and guides with your project info

---

## 📞 Support & Resources

### Documentation

- [Azure Functions Python v4](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- [Model Context Protocol](https://github.com/modelcontextprotocol/specification)
- [Microsoft Copilot](https://docs.github.com/en/copilot)
- [Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/)

### Community

- [MCP Framework Discussions](https://github.com/your-org/mcp-framework/discussions)
- [Azure Functions Community](https://github.com/Azure/azure-functions)

### Troubleshooting

See the deployment guide in `deploy/README.md` for common issues and solutions.

---

## 🏁 Next Steps

1. **Clone the template** and customize it for your MCP server
2. **Add your tools** in the `tools/` directory
3. **Configure environment** variables in `.env`
4. **Test locally** to ensure everything works
5. **Deploy to Azure** using the deployment script
6. **Integrate with Copilot** and start using your MCP server

---

*Template Version: 1.0.0*
*Generated by Mistral Vibe*
*Co-Authored-By: Mistral Vibe <vibe@mistral.ai>*