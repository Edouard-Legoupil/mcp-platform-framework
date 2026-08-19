"""
MCP Framework - Azure Functions v4 Implementation
This module implements the FunctionApp with explicit function decorators
as required by Azure Functions v4 Python programming model.

Compatible with:
- Azure Functions v4 Python
- Model Context Protocol (MCP)
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

# Create the FunctionApp instance - THIS IS REQUIRED FOR AZURE FUNCTIONS V4
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Import MCP Server for handling MCP protocol requests
from .mcp_server import MCPServer

# Create MCP Server instance
mcp_server = MCPServer()


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
    return mcp_server._handle_health(
        method=req.method,
        headers=dict(req.headers),
        query_params=dict(req.params)
    )


@app.function_name(name="mcp_metadata")
@app.route(route="mcp/metadata", methods=["GET"])
def mcp_metadata(req: func.HttpRequest) -> func.HttpResponse:
    """
    MCP Server Metadata Endpoint
    Required by Copilot to discover server capabilities
    """
    return mcp_server._handle_metadata(
        method=req.method,
        headers=dict(req.headers),
        query_params=dict(req.params)
    )


@app.function_name(name="mcp_tools_list")
@app.route(route="mcp/tools", methods=["GET"])
def mcp_tools_list(req: func.HttpRequest) -> func.HttpResponse:
    """
    MCP Tools List Endpoint
    Required by Copilot to discover available tools
    """
    return mcp_server._handle_tools_list(
        method=req.method,
        headers=dict(req.headers),
        query_params=dict(req.params)
    )


@app.function_name(name="mcp_tools_metadata")
@app.route(route="mcp/tools/{tool_name}", methods=["GET"])
def mcp_tools_metadata(req: func.HttpRequest, tool_name: str) -> func.HttpResponse:
    """
    MCP Tool Metadata Endpoint
    Required by Copilot to understand tool parameters and return types
    """
    return mcp_server._handle_tool_metadata(
        tool_name=tool_name,
        method=req.method,
        headers=dict(req.headers)
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
    except Exception:
        body = {}
    
    return mcp_server._handle_tool_execute(
        tool_name=tool_name,
        method=req.method,
        headers=dict(req.headers),
        body=body
    )


@app.function_name(name="mcp_resources_list")
@app.route(route="mcp/resources", methods=["GET"])
def mcp_resources_list(req: func.HttpRequest) -> func.HttpResponse:
    """
    MCP Resources List Endpoint
    Required by Copilot to discover available data resources
    """
    return mcp_server._handle_resources_list(
        method=req.method,
        headers=dict(req.headers),
        query_params=dict(req.params)
    )


@app.function_name(name="mcp_resources_access")
@app.route(route="mcp/resources/{resource_name}", methods=["GET"])
def mcp_resources_access(req: func.HttpRequest, resource_name: str) -> func.HttpResponse:
    """
    MCP Resource Access Endpoint
    Required by Copilot to access resource data
    """
    return mcp_server._handle_resources(
        path=f"/mcp/resources/{resource_name}",
        method=req.method,
        headers=dict(req.headers),
        query_params=dict(req.params)
    )


@app.function_name(name="mcp_prompts_list")
@app.route(route="mcp/prompts", methods=["GET"])
def mcp_prompts_list(req: func.HttpRequest) -> func.HttpResponse:
    """
    MCP Prompts List Endpoint
    Required by Copilot Studio for prompt template discovery
    """
    return mcp_server._handle_prompts_list(
        method=req.method,
        headers=dict(req.headers),
        query_params=dict(req.params)
    )


@app.function_name(name="mcp_prompts_get")
@app.route(route="mcp/prompts/{prompt_name}", methods=["GET"])
def mcp_prompts_get(req: func.HttpRequest, prompt_name: str) -> func.HttpResponse:
    """
    MCP Prompt Template Endpoint
    Required by Copilot Studio to retrieve prompt templates
    """
    return mcp_server._handle_prompts(
        path=f"/mcp/prompts/{prompt_name}",
        method=req.method,
        headers=dict(req.headers),
        query_params=dict(req.params)
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
    except Exception:
        body = {}
    
    return mcp_server._handle_completions(
        method=req.method,
        headers=dict(req.headers),
        query_params=dict(req.params),
        body=body
    )


# ============================================================================
# LEGACY API ENDPOINTS
# These endpoints maintain backward compatibility with existing MCP Framework
# ============================================================================

@app.function_name(name="api_health")
@app.route(route="api/health", methods=["GET"])
def api_health(req: func.HttpRequest) -> func.HttpResponse:
    """
    Legacy Health Check Endpoint
    Maintains backward compatibility with existing MCP Framework
    """
    from .function_app import app as legacy_app
    return legacy_app.handle_request(req)


@app.function_name(name="api_tools")
@app.route(route="api/tools", methods=["GET", "POST"])
def api_tools(req: func.HttpRequest) -> func.HttpResponse:
    """
    Legacy Tools Endpoint
    Maintains backward compatibility with existing MCP Framework
    """
    from .function_app import app as legacy_app
    return legacy_app.handle_request(req)


@app.function_name(name="api_metadata")
@app.route(route="api/metadata", methods=["GET"])
def api_metadata(req: func.HttpRequest) -> func.HttpResponse:
    """
    Legacy Metadata Endpoint
    Maintains backward compatibility with existing MCP Framework
    """
    from .function_app import app as legacy_app
    return legacy_app.handle_request(req)


# ============================================================================
# CATCH-ALL ENDPOINT
# Handles any other routes not explicitly defined
# ============================================================================

@app.function_name(name="catch_all")
@app.route(route="{*path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def catch_all(req: func.HttpRequest, path: str) -> func.HttpResponse:
    """
    Catch-all endpoint for any undefined routes
    Routes to MCP Server for handling
    """
    # Skip if this is a defined MCP or API endpoint
    mcp_endpoints = [
        "mcp/health", "mcp/metadata", "mcp/tools", "mcp/resources", 
        "mcp/prompts", "mcp/completions"
    ]
    api_endpoints = ["api/health", "api/tools", "api/metadata"]
    
    if any(path.startswith(ep) for ep in mcp_endpoints + api_endpoints):
        # This should have been handled by explicit endpoints
        return func.HttpResponse(
            json.dumps({"error": "Endpoint not found"}),
            status_code=404,
            mimetype='application/json'
        )
    
    # Route to MCP Server for any other paths
    from unittest.mock import Mock
    mock_req = Mock(spec=func.HttpRequest)
    mock_req.method = req.method
    mock_req.path = path
    mock_req.headers = dict(req.headers)
    mock_req.params = dict(req.params)
    mock_req.get_json = req.get_json
    mock_req.get_body = req.get_body
    
    return mcp_server.handle_request(mock_req)
