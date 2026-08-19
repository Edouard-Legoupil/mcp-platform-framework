"""
MCP Framework - Azure Functions v4 Implementation
Clean implementation using explicit @app.function_name decorators

This is the main entry point for Azure Functions v4 Python programming model.
All MCP Protocol endpoints are implemented as individual functions with explicit decorators.

Compatible with:
- Azure Functions v4 Python
- Model Context Protocol (MCP) v2024-11-05
- Microsoft Copilot and Copilot Studio
"""

import azure.functions as func
import logging
import json
import os
from typing import Optional, Dict, Any, List
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create the FunctionApp instance - REQUIRED FOR AZURE FUNCTIONS V4
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# MCP Protocol Constants
MCP_PROTOCOL_VERSION = "2024-11-05"
MCP_SERVER_NAME = os.getenv('MCP_SERVER_NAME', 'MCP Framework Server')
MCP_SERVER_VERSION = os.getenv('MCP_SERVER_VERSION', '1.0.0')


# ============================================================================
# MCP PROTOCOL ENDPOINTS
# These endpoints implement the Model Context Protocol (MCP) specification
# Required for Microsoft Copilot and Copilot Studio integration
# ============================================================================

@app.function_name(name="mcp_health")
@app.route(route="mcp/health", methods=["GET"])
def mcp_health(req: func.HttpRequest) -> func.HttpResponse:
    """
    MCP Health Check Endpoint
    Required by Copilot to verify server availability
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "server": MCP_SERVER_NAME,
        "version": MCP_SERVER_VERSION,
        "protocol": MCP_PROTOCOL_VERSION,
        "environment": os.environ.get('MCP_ENVIRONMENT', 'Dev')
    }
    
    return func.HttpResponse(
        json.dumps(health_status),
        status_code=200,
        mimetype='application/json'
    )


@app.function_name(name="mcp_metadata")
@app.route(route="mcp/metadata", methods=["GET"])
def mcp_metadata(req: func.HttpRequest) -> func.HttpResponse:
    """
    MCP Server Metadata Endpoint
    Required by Copilot to discover server capabilities
    """
    metadata = {
        "name": MCP_SERVER_NAME,
        "version": MCP_SERVER_VERSION,
        "protocol": MCP_PROTOCOL_VERSION,
        "description": "MCP Framework Server for Microsoft Copilot and Copilot Studio",
        "capabilities": {
            "tools": True,
            "resources": True,
            "prompts": True,
            "completions": True
        },
        "endpoints": {
            "health": "/mcp/health",
            "metadata": "/mcp/metadata",
            "tools": "/mcp/tools",
            "resources": "/mcp/resources",
            "prompts": "/mcp/prompts",
            "completions": "/mcp/completions"
        }
    }
    
    return func.HttpResponse(
        json.dumps(metadata),
        status_code=200,
        mimetype='application/json'
    )


@app.function_name(name="mcp_tools_list")
@app.route(route="mcp/tools", methods=["GET"])
def mcp_tools_list(req: func.HttpRequest) -> func.HttpResponse:
    """
    MCP Tools List Endpoint
    Required by Copilot to discover available tools
    """
    try:
        from platform.registration import get_tool_registry
        registry = get_tool_registry()
        tools = registry.get_all_tools()
        
        tools_list = []
        for tool in tools:
            tools_list.append({
                "name": tool.metadata.name,
                "description": tool.metadata.description,
                "domain": tool.metadata.domain,
                "version": tool.metadata.version
            })
        
        return func.HttpResponse(
            json.dumps({
                "tools": tools_list,
                "count": len(tools_list)
            }),
            status_code=200,
            mimetype='application/json'
        )
        
    except ImportError:
        # Platform imports not available
        logger.warning("Platform imports not available, returning empty tool list")
        return func.HttpResponse(
            json.dumps({
                "tools": [],
                "count": 0
            }),
            status_code=200,
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"Error listing tools: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype='application/json'
        )


@app.function_name(name="mcp_tools_metadata")
@app.route(route="mcp/tools/{tool_name}", methods=["GET"])
def mcp_tools_metadata(req: func.HttpRequest, tool_name: str) -> func.HttpResponse:
    """
    MCP Tool Metadata Endpoint
    Required by Copilot to understand tool parameters and return types
    """
    try:
        from platform.registration import get_tool_registry
        registry = get_tool_registry()
        tool = registry.get_tool_by_name(tool_name)
        
        if not tool:
            return func.HttpResponse(
                json.dumps({"error": f"Tool '{tool_name}' not found"}),
                status_code=404,
                mimetype='application/json'
            )
        
        return func.HttpResponse(
            json.dumps({
                "name": tool.metadata.name,
                "description": tool.metadata.description,
                "domain": tool.metadata.domain,
                "version": tool.metadata.version,
                "inputSchema": tool.metadata.input_schema or {},
                "outputSchema": tool.metadata.output_schema or {}
            }),
            status_code=200,
            mimetype='application/json'
        )
        
    except ImportError:
        logger.warning("Platform imports not available")
        return func.HttpResponse(
            json.dumps({"error": f"Tool '{tool_name}' not found"}),
            status_code=404,
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"Error getting tool metadata: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype='application/json'
        )


@app.function_name(name="mcp_tools_execute")
@app.route(route="mcp/tools/{tool_name}/execute", methods=["POST"])
def mcp_tools_execute(req: func.HttpRequest, tool_name: str) -> func.HttpResponse:
    """
    MCP Tool Execution Endpoint
    Required by Copilot to execute tools with user-provided arguments
    """
    try:
        body = req.get_json() if req.get_body() else {}
        arguments = body.get('arguments', {})
        
        from platform.registration import get_tool_registry
        registry = get_tool_registry()
        tool = registry.get_tool_by_name(tool_name)
        
        if not tool:
            return func.HttpResponse(
                json.dumps({"error": f"Tool '{tool_name}' not found"}),
                status_code=404,
                mimetype='application/json'
            )
        
        # Execute the tool
        module_name, func_name = tool.handler.rsplit('.', 1)
        import importlib
        module = importlib.import_module(module_name)
        tool_func = getattr(module, func_name)
        
        result = tool_func(**arguments)
        
        return func.HttpResponse(
            json.dumps({
                "success": True,
                "result": result,
                "tool": tool_name
            }),
            status_code=200,
            mimetype='application/json'
        )
        
    except ImportError as e:
        logger.error(f"Platform imports not available: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Tool '{tool_name}' not found"}),
            status_code=404,
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "success": False,
                "error": str(e),
                "tool": tool_name
            }),
            status_code=500,
            mimetype='application/json'
        )


@app.function_name(name="mcp_resources_list")
@app.route(route="mcp/resources", methods=["GET"])
def mcp_resources_list(req: func.HttpRequest) -> func.HttpResponse:
    """
    MCP Resources List Endpoint
    Required by Copilot to discover available data resources
    """
    try:
        from platform.catalog import get_catalog_client
        client = get_catalog_client()
        resources = client.get_all_resources()
        
        resources_list = []
        for resource in resources:
            resources_list.append({
                "name": resource.name,
                "description": resource.description,
                "type": resource.type,
                "uri": resource.uri,
                "mimeType": resource.mime_type
            })
        
        return func.HttpResponse(
            json.dumps({
                "resources": resources_list,
                "count": len(resources_list)
            }),
            status_code=200,
            mimetype='application/json'
        )
        
    except ImportError:
        logger.warning("Platform catalog not available")
        return func.HttpResponse(
            json.dumps({
                "resources": [],
                "count": 0
            }),
            status_code=200,
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"Error listing resources: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype='application/json'
        )


@app.function_name(name="mcp_resources_access")
@app.route(route="mcp/resources/{resource_name}", methods=["GET"])
def mcp_resources_access(req: func.HttpRequest, resource_name: str) -> func.HttpResponse:
    """
    MCP Resource Access Endpoint
    Required by Copilot to access resource data
    """
    try:
        from platform.catalog import get_catalog_client
        client = get_catalog_client()
        resource = client.get_resource_by_name(resource_name)
        
        if not resource:
            return func.HttpResponse(
                json.dumps({"error": f"Resource '{resource_name}' not found"}),
                status_code=404,
                mimetype='application/json'
            )
        
        return func.HttpResponse(
            json.dumps({
                "name": resource.name,
                "description": resource.description,
                "type": resource.type,
                "uri": resource.uri,
                "mimeType": resource.mime_type
            }),
            status_code=200,
            mimetype='application/json'
        )
        
    except ImportError:
        logger.warning("Platform catalog not available")
        return func.HttpResponse(
            json.dumps({"error": f"Resource '{resource_name}' not found"}),
            status_code=404,
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"Error accessing resource {resource_name}: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype='application/json'
        )


@app.function_name(name="mcp_prompts_list")
@app.route(route="mcp/prompts", methods=["GET"])
def mcp_prompts_list(req: func.HttpRequest) -> func.HttpResponse:
    """
    MCP Prompts List Endpoint
    Required by Copilot Studio for prompt template discovery
    """
    try:
        from platform.template import get_template_generator
        generator = get_template_generator()
        prompts = generator.get_all_prompts()
        
        prompts_list = []
        for prompt in prompts:
            prompts_list.append({
                "name": prompt.name,
                "description": prompt.description
            })
        
        return func.HttpResponse(
            json.dumps({
                "prompts": prompts_list,
                "count": len(prompts_list)
            }),
            status_code=200,
            mimetype='application/json'
        )
        
    except ImportError:
        logger.warning("Platform template generator not available")
        return func.HttpResponse(
            json.dumps({
                "prompts": [],
                "count": 0
            }),
            status_code=200,
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"Error listing prompts: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype='application/json'
        )


@app.function_name(name="mcp_prompts_get")
@app.route(route="mcp/prompts/{prompt_name}", methods=["GET"])
def mcp_prompts_get(req: func.HttpRequest, prompt_name: str) -> func.HttpResponse:
    """
    MCP Prompt Template Endpoint
    Required by Copilot Studio to retrieve prompt templates
    """
    try:
        from platform.template import get_template_generator
        generator = get_template_generator()
        prompt = generator.get_prompt_by_name(prompt_name)
        
        if not prompt:
            return func.HttpResponse(
                json.dumps({"error": f"Prompt '{prompt_name}' not found"}),
                status_code=404,
                mimetype='application/json'
            )
        
        return func.HttpResponse(
            json.dumps({
                "name": prompt.name,
                "description": prompt.description,
                "template": prompt.template,
                "arguments": prompt.arguments
            }),
            status_code=200,
            mimetype='application/json'
        )
        
    except ImportError:
        logger.warning("Platform template generator not available")
        return func.HttpResponse(
            json.dumps({"error": f"Prompt '{prompt_name}' not found"}),
            status_code=404,
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"Error getting prompt {prompt_name}: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype='application/json'
        )


@app.function_name(name="mcp_completions")
@app.route(route="mcp/completions", methods=["POST"])
def mcp_completions(req: func.HttpRequest) -> func.HttpResponse:
    """
    MCP Completions Endpoint
    Required by Copilot Studio to generate completions from prompt templates
    """
    try:
        body = req.get_json() if req.get_body() else {}
        prompt_name = body.get('prompt')
        context = body.get('context', {})
        
        if not prompt_name:
            return func.HttpResponse(
                json.dumps({"error": "prompt parameter is required"}),
                status_code=400,
                mimetype='application/json'
            )
        
        from platform.template import get_template_generator
        generator = get_template_generator()
        prompt = generator.get_prompt_by_name(prompt_name)
        
        if not prompt:
            return func.HttpResponse(
                json.dumps({"error": f"Prompt '{prompt_name}' not found"}),
                status_code=404,
                mimetype='application/json'
            )
        
        # Apply context to template
        template = prompt.template
        for key, value in context.items():
            template = template.replace(f"{{{{{key}}}}}", str(value))
        
        return func.HttpResponse(
            json.dumps({
                "completion": template,
                "prompt": prompt_name
            }),
            status_code=200,
            mimetype='application/json'
        )
        
    except ImportError:
        logger.warning("Platform template generator not available")
        return func.HttpResponse(
            json.dumps({"error": "Prompt templates not available"}),
            status_code=500,
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"Error generating completion: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype='application/json'
        )
