"""
MCP Server Implementation for Azure Functions
Compatible with Microsoft Copilot and Copilot Studio

This module implements the Model Context Protocol (MCP) server interface
required for integration with Microsoft Copilot and Copilot Studio.

MCP Server Requirements:
- Must implement MCP protocol endpoints
- Must support tool discovery and execution
- Must support resource access
- Must support prompt and completion APIs
- Must handle authentication and authorization
- Must provide health and metadata endpoints
"""

import json
import logging
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import azure.functions as func

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MCP Protocol Constants
MCP_PROTOCOL_VERSION = "2024-11-05"  # Latest MCP protocol version
MCP_SERVER_NAME = "MCP Framework Server"
MCP_SERVER_VERSION = "1.0.0"


class MCPServer:
    """
    MCP Server implementation for Azure Functions.
    
    This class implements the Model Context Protocol (MCP) server interface
    required for integration with Microsoft Copilot and Copilot Studio.
    
    MCP Protocol Endpoints:
    - /mcp/health - Server health check
    - /mcp/metadata - Server metadata
    - /mcp/tools - Tool discovery and listing
    - /mcp/tools/{tool_name} - Tool metadata
    - /mcp/tools/{tool_name}/execute - Tool execution
    - /mcp/resources - Resource discovery
    - /mcp/resources/{resource_name} - Resource access
    - /mcp/prompts - Prompt templates
    - /mcp/completions - Completion API
    """
    
    def __init__(self):
        """Initialize the MCP Server"""
        self.server_name = MCP_SERVER_NAME
        self.server_version = MCP_SERVER_VERSION
        self.protocol_version = MCP_PROTOCOL_VERSION
        self._initialized = False
        self._tools = []
        self._resources = []
        self._prompts = []
        
        # Initialize the server
        self._initialize_server()
    
    def _initialize_server(self):
        """Initialize the MCP Server"""
        if self._initialized:
            return
        
        try:
            # Initialize from environment
            self.server_name = os.getenv('MCP_SERVER_NAME', MCP_SERVER_NAME)
            self.server_version = os.getenv('MCP_SERVER_VERSION', MCP_SERVER_VERSION)
            
            # Load tools, resources, and prompts
            self._load_tools()
            self._load_resources()
            self._load_prompts()
            
            logger.info(f"MCP Server initialized: {self.server_name} v{self.server_version}")
            logger.info(f"Protocol version: {self.protocol_version}")
            logger.info(f"Loaded {len(self._tools)} tools, {len(self._resources)} resources, {len(self._prompts)} prompts")
            
            self._initialized = True
            
        except Exception as e:
            logger.error(f"Error initializing MCP Server: {str(e)}")
            raise
    
    def _load_tools(self):
        """Load available tools from the registry"""
        try:
            # Try to import from platform.registration
            from platform.registration import get_tool_registry
            registry = get_tool_registry()
            tools = registry.get_all_tools()
            
            self._tools = []
            for tool in tools:
                tool_info = {
                    'name': tool.metadata.name,
                    'description': tool.metadata.description,
                    'domain': tool.metadata.domain,
                    'version': tool.metadata.version,
                    'inputSchema': tool.metadata.input_schema,
                    'outputSchema': tool.metadata.output_schema,
                    'handler': tool.handler,
                    'tool_id': tool.tool_id
                }
                self._tools.append(tool_info)
                
            logger.info(f"Loaded {len(self._tools)} tools from registry")
            
        except ImportError:
            # Platform imports not available, use fallback
            logger.warning("Platform imports not available, using fallback tool list")
            self._tools = []
        except Exception as e:
            logger.error(f"Error loading tools: {str(e)}")
            self._tools = []
    
    def _load_resources(self):
        """Load available resources"""
        try:
            # Try to import from platform
            from platform.catalog import get_catalog_client
            client = get_catalog_client()
            resources = client.get_all_resources()
            
            self._resources = []
            for resource in resources:
                resource_info = {
                    'name': resource.name,
                    'description': resource.description,
                    'type': resource.type,
                    'uri': resource.uri,
                    'mimeType': resource.mime_type,
                    'access': resource.access
                }
                self._resources.append(resource_info)
                
            logger.info(f"Loaded {len(self._resources)} resources")
            
        except ImportError:
            logger.warning("Platform catalog not available, using fallback resource list")
            self._resources = []
        except Exception as e:
            logger.error(f"Error loading resources: {str(e)}")
            self._resources = []
    
    def _load_prompts(self):
        """Load available prompt templates"""
        try:
            # Try to import from platform
            from platform.template import get_template_generator
            generator = get_template_generator()
            prompts = generator.get_all_prompts()
            
            self._prompts = []
            for prompt in prompts:
                prompt_info = {
                    'name': prompt.name,
                    'description': prompt.description,
                    'template': prompt.template,
                    'arguments': prompt.arguments
                }
                self._prompts.append(prompt_info)
                
            logger.info(f"Loaded {len(self._prompts)} prompts")
            
        except ImportError:
            logger.warning("Platform template generator not available, using fallback prompt list")
            self._prompts = []
        except Exception as e:
            logger.error(f"Error loading prompts: {str(e)}")
            self._prompts = []
    
    def handle_request(self, req: func.HttpRequest) -> func.HttpResponse:
        """
        Handle MCP protocol requests.
        
        This method routes requests to the appropriate MCP endpoint handler.
        """
        try:
            method = req.method
            path = req.path
            headers = dict(req.headers)
            query_params = dict(req.params)
            
            # Parse request body
            try:
                body = req.get_json() if req.get_body() else {}
            except Exception:
                body = {}
            
            logger.info(f"MCP Request: {method} {path}")
            
            # Route to appropriate handler
            if path == "/mcp/health" or path == "/mcp/health/":
                return self._handle_health(method, headers, query_params)
            
            elif path == "/mcp/metadata" or path == "/mcp/metadata/":
                return self._handle_metadata(method, headers, query_params)
            
            elif path.startswith("/mcp/tools/"):
                return self._handle_tools(path, method, headers, query_params, body)
            
            elif path == "/mcp/tools" or path == "/mcp/tools/":
                return self._handle_tools_list(method, headers, query_params)
            
            elif path.startswith("/mcp/resources/"):
                return self._handle_resources(path, method, headers, query_params)
            
            elif path == "/mcp/resources" or path == "/mcp/resources/":
                return self._handle_resources_list(method, headers, query_params)
            
            elif path.startswith("/mcp/prompts/"):
                return self._handle_prompts(path, method, headers, query_params)
            
            elif path == "/mcp/prompts" or path == "/mcp/prompts/":
                return self._handle_prompts_list(method, headers, query_params)
            
            elif path == "/mcp/completions" or path == "/mcp/completions/":
                return self._handle_completions(method, headers, query_params, body)
            
            else:
                return self._handle_not_found(path)
                
        except Exception as e:
            logger.error(f"Error handling MCP request: {str(e)}")
            return self._handle_error(e)
    
    def _handle_health(self, method: str, headers: Dict[str, str], query_params: Dict[str, str]) -> func.HttpResponse:
        """Handle MCP health check endpoint"""
        if method != "GET":
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                status_code=405,
                mimetype='application/json'
            )
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "server": self.server_name,
            "version": self.server_version,
            "protocol": self.protocol_version,
            "environment": os.environ.get('MCP_ENVIRONMENT', 'Dev')
        }
        
        return func.HttpResponse(
            json.dumps(health_status),
            status_code=200,
            mimetype='application/json'
        )
    
    def _handle_metadata(self, method: str, headers: Dict[str, str], query_params: Dict[str, str]) -> func.HttpResponse:
        """Handle MCP metadata endpoint"""
        if method != "GET":
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                status_code=405,
                mimetype='application/json'
            )
        
        metadata = {
            "name": self.server_name,
            "version": self.server_version,
            "protocol": self.protocol_version,
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
    
    def _handle_tools_list(self, method: str, headers: Dict[str, str], query_params: Dict[str, str]) -> func.HttpResponse:
        """Handle MCP tools list endpoint"""
        if method != "GET":
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                status_code=405,
                mimetype='application/json'
            )
        
        tools_list = []
        for tool in self._tools:
            tools_list.append({
                "name": tool['name'],
                "description": tool['description'],
                "domain": tool.get('domain', 'unknown'),
                "version": tool.get('version', '1.0.0')
            })
        
        return func.HttpResponse(
            json.dumps({
                "tools": tools_list,
                "count": len(tools_list)
            }),
            status_code=200,
            mimetype='application/json'
        )
    
    def _handle_tools(self, path: str, method: str, headers: Dict[str, str], query_params: Dict[str, str], body: Dict[str, Any]) -> func.HttpResponse:
        """Handle MCP tools endpoint"""
        # Extract tool name from path: /mcp/tools/{tool_name}[/execute]
        parts = path.split('/')
        if len(parts) < 4:
            return func.HttpResponse(
                json.dumps({"error": "Invalid path"}),
                status_code=400,
                mimetype='application/json'
            )
        
        tool_name = parts[3]
        
        # Check if this is an execute request
        if len(parts) >= 5 and parts[4] == "execute":
            return self._handle_tool_execute(tool_name, method, headers, body)
        else:
            return self._handle_tool_metadata(tool_name, method, headers)
    
    def _handle_tool_metadata(self, tool_name: str, method: str, headers: Dict[str, str]) -> func.HttpResponse:
        """Handle MCP tool metadata endpoint"""
        if method != "GET":
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                status_code=405,
                mimetype='application/json'
            )
        
        # Find the tool
        tool = next((t for t in self._tools if t['name'] == tool_name), None)
        if not tool:
            return func.HttpResponse(
                json.dumps({"error": f"Tool '{tool_name}' not found"}),
                status_code=404,
                mimetype='application/json'
            )
        
        return func.HttpResponse(
            json.dumps({
                "name": tool['name'],
                "description": tool['description'],
                "domain": tool.get('domain', 'unknown'),
                "version": tool.get('version', '1.0.0'),
                "inputSchema": tool.get('inputSchema', {}),
                "outputSchema": tool.get('outputSchema', {})
            }),
            status_code=200,
            mimetype='application/json'
        )
    
    def _handle_tool_execute(self, tool_name: str, method: str, headers: Dict[str, str], body: Dict[str, Any]) -> func.HttpResponse:
        """Handle MCP tool execution endpoint"""
        if method != "POST":
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                status_code=405,
                mimetype='application/json'
            )
        
        # Find the tool
        tool = next((t for t in self._tools if t['name'] == tool_name), None)
        if not tool:
            return func.HttpResponse(
                json.dumps({"error": f"Tool '{tool_name}' not found"}),
                status_code=404,
                mimetype='application/json'
            )
        
        try:
            # Extract arguments from body
            arguments = body.get('arguments', {})
            
            # Execute the tool
            module_name, func_name = tool['handler'].rsplit('.', 1)
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
    
    def _handle_resources_list(self, method: str, headers: Dict[str, str], query_params: Dict[str, str]) -> func.HttpResponse:
        """Handle MCP resources list endpoint"""
        if method != "GET":
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                status_code=405,
                mimetype='application/json'
            )
        
        resources_list = []
        for resource in self._resources:
            resources_list.append({
                "name": resource['name'],
                "description": resource['description'],
                "type": resource['type'],
                "uri": resource['uri'],
                "mimeType": resource.get('mimeType', 'text/plain')
            })
        
        return func.HttpResponse(
            json.dumps({
                "resources": resources_list,
                "count": len(resources_list)
            }),
            status_code=200,
            mimetype='application/json'
        )
    
    def _handle_resources(self, path: str, method: str, headers: Dict[str, str], query_params: Dict[str, str]) -> func.HttpResponse:
        """Handle MCP resources endpoint"""
        # Extract resource name from path: /mcp/resources/{resource_name}
        parts = path.split('/')
        if len(parts) < 4:
            return func.HttpResponse(
                json.dumps({"error": "Invalid path"}),
                status_code=400,
                mimetype='application/json'
            )
        
        resource_name = parts[3]
        
        # Find the resource
        resource = next((r for r in self._resources if r['name'] == resource_name), None)
        if not resource:
            return func.HttpResponse(
                json.dumps({"error": f"Resource '{resource_name}' not found"}),
                status_code=404,
                mimetype='application/json'
            )
        
        if method == "GET":
            # Return resource content
            try:
                # For now, return resource metadata
                # In a real implementation, this would fetch the actual resource content
                return func.HttpResponse(
                    json.dumps({
                        "name": resource['name'],
                        "description": resource['description'],
                        "type": resource['type'],
                        "uri": resource['uri'],
                        "mimeType": resource.get('mimeType', 'text/plain')
                    }),
                    status_code=200,
                    mimetype='application/json'
                )
            except Exception as e:
                return func.HttpResponse(
                    json.dumps({"error": str(e)}),
                    status_code=500,
                    mimetype='application/json'
                )
        else:
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                status_code=405,
                mimetype='application/json'
            )
    
    def _handle_prompts_list(self, method: str, headers: Dict[str, str], query_params: Dict[str, str]) -> func.HttpResponse:
        """Handle MCP prompts list endpoint"""
        if method != "GET":
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                status_code=405,
                mimetype='application/json'
            )
        
        prompts_list = []
        for prompt in self._prompts:
            prompts_list.append({
                "name": prompt['name'],
                "description": prompt['description']
            })
        
        return func.HttpResponse(
            json.dumps({
                "prompts": prompts_list,
                "count": len(prompts_list)
            }),
            status_code=200,
            mimetype='application/json'
        )
    
    def _handle_prompts(self, path: str, method: str, headers: Dict[str, str], query_params: Dict[str, str]) -> func.HttpResponse:
        """Handle MCP prompts endpoint"""
        # Extract prompt name from path: /mcp/prompts/{prompt_name}
        parts = path.split('/')
        if len(parts) < 4:
            return func.HttpResponse(
                json.dumps({"error": "Invalid path"}),
                status_code=400,
                mimetype='application/json'
            )
        
        prompt_name = parts[3]
        
        # Find the prompt
        prompt = next((p for p in self._prompts if p['name'] == prompt_name), None)
        if not prompt:
            return func.HttpResponse(
                json.dumps({"error": f"Prompt '{prompt_name}' not found"}),
                status_code=404,
                mimetype='application/json'
            )
        
        if method == "GET":
            return func.HttpResponse(
                json.dumps({
                    "name": prompt['name'],
                    "description": prompt['description'],
                    "template": prompt['template'],
                    "arguments": prompt.get('arguments', [])
                }),
                status_code=200,
                mimetype='application/json'
            )
        else:
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                status_code=405,
                mimetype='application/json'
            )
    
    def _handle_completions(self, method: str, headers: Dict[str, str], query_params: Dict[str, str], body: Dict[str, Any]) -> func.HttpResponse:
        """Handle MCP completions endpoint"""
        if method != "POST":
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                status_code=405,
                mimetype='application/json'
            )
        
        # Extract prompt and context from body
        prompt_name = body.get('prompt')
        context = body.get('context', {})
        
        # Find the prompt
        prompt = next((p for p in self._prompts if p['name'] == prompt_name), None)
        if not prompt:
            return func.HttpResponse(
                json.dumps({"error": f"Prompt '{prompt_name}' not found"}),
                status_code=404,
                mimetype='application/json'
            )
        
        try:
            # Apply context to template
            template = prompt['template']
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
            
        except Exception as e:
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                status_code=500,
                mimetype='application/json'
            )
    
    def _handle_not_found(self, path: str) -> func.HttpResponse:
        """Handle 404 Not Found"""
        return func.HttpResponse(
            json.dumps({
                "error": f"Path '{path}' not found",
                "available_endpoints": [
                    "/mcp/health",
                    "/mcp/metadata",
                    "/mcp/tools",
                    "/mcp/resources",
                    "/mcp/prompts",
                    "/mcp/completions"
                ]
            }),
            status_code=404,
            mimetype='application/json'
        )
    
    def _handle_error(self, e: Exception) -> func.HttpResponse:
        """Handle errors"""
        return func.HttpResponse(
            json.dumps({
                "error": str(e),
                "type": type(e).__name__,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }),
            status_code=500,
            mimetype='application/json'
        )


# Create the MCP Server instance
mcp_server = MCPServer()

# Export for Azure Functions
app = mcp_server
