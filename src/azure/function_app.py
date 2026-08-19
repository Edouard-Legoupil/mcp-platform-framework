"""
MCP Framework Azure Function App
This module exports the FunctionApp object required by Azure Functions Python v2
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

# Import platform framework components
try:
    from platform.framework import (
        get_framework, 
        initialize_framework,
        MCPFramework
    )
    from platform.auth import (
        get_authenticator,
        AuthenticationResult,
        AuthenticationError
    )
    from platform.registration import get_tool_registry
    from platform.telemetry import get_telemetry_collector, track_tool_telemetry
    from platform.audit import get_audit_logger, audit_tool_access
    from platform.errors import get_error_handler, MCPError
    from platform.config import get_config_manager
    PLATFORM_IMPORTS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Platform imports not available: {e}")
    PLATFORM_IMPORTS_AVAILABLE = False


class MCPFunctionApp:
    """
    Main class for MCP Function App.
    Handles HTTP requests, authentication, tool routing, and response generation.
    """
    
    def __init__(self):
        """Initialize the MCP Function App"""
        self.framework: Optional[MCPFramework] = None
        self._initialized = False
        
        # Initialize framework
        self._initialize_framework()
    
    def _initialize_framework(self):
        """Initialize the MCP Platform Framework"""
        if self._initialized:
            return
        
        try:
            # Get configuration from environment
            domain = os.getenv('MCP_DOMAIN', 'unknown')
            environment = os.getenv('MCP_ENVIRONMENT', 'Dev')
            
            # Initialize framework
            self.framework = initialize_framework(
                domain=domain,
                environment=environment
            )
            
            logger.info(f"MCP Framework initialized for domain: {domain}")
            self._initialized = True
            
        except Exception as e:
            logger.error(f"Error initializing MCP Framework: {str(e)}")
            raise
    
    def handle_request(self, req: func.HttpRequest) -> func.HttpResponse:
        """
        Handle an HTTP request to the MCP Function App.
        
        Args:
            req: Azure Functions HTTP request
            
        Returns:
            Azure Functions HTTP response
        """
        start_time = datetime.utcnow()
        
        try:
            # Extract request information
            method = req.method
            path = req.path
            headers = dict(req.headers)
            query_params = dict(req.params)
            
            # Parse request body
            try:
                body = req.get_json() if req.get_body() else {}
            except Exception:
                body = {}
            
            logger.info(f"Received {method} request for {path}")
            
            # Handle different endpoints
            if path.startswith('/api/tools'):
                return self._handle_tools_request(method, path, headers, query_params, body)
            elif path.startswith('/api/health'):
                return self._handle_health_request()
            elif path.startswith('/api/metadata'):
                return self._handle_metadata_request()
            elif path.startswith('/tools'):
                return self._handle_tool_execution(path, headers, body)
            else:
                return func.HttpResponse("Not found", status_code=404)
                
        except Exception as e:
            return self._handle_error(e, start_time)
    
    def _handle_tools_request(self, method: str, path: str, headers: Dict[str, str], 
                              query_params: Dict[str, str], body: Dict[str, Any]) -> func.HttpResponse:
        """Handle requests to /api/tools endpoint"""
        try:
            if not PLATFORM_IMPORTS_AVAILABLE:
                return func.HttpResponse(
                    json.dumps({'error': 'Platform framework not available'}),
                    status_code=500,
                    mimetype='application/json'
                )
                
            registry = get_tool_registry()
            
            if method == 'GET':
                # List all tools
                tools = registry.get_all_tools()
                tool_list = [
                    {
                        'id': tool.tool_id,
                        'name': tool.metadata.name,
                        'description': tool.metadata.description,
                        'domain': tool.metadata.domain,
                        'type': tool.metadata.tool_type.value,
                        'status': tool.metadata.status.value,
                        'classification': tool.metadata.classification,
                        'endpoint': tool.endpoint
                    }
                    for tool in tools
                ]
                
                return func.HttpResponse(
                    json.dumps({'tools': tool_list, 'count': len(tool_list)}),
                    status_code=200,
                    mimetype='application/json'
                )
            elif method == 'POST':
                # Register a new tool (admin only)
                return func.HttpResponse(
                    json.dumps({'error': 'Tool registration not supported via API'}),
                    status_code=405,
                    mimetype='application/json'
                )
            else:
                return func.HttpResponse(
                    json.dumps({'error': 'Method not allowed'}),
                    status_code=405,
                    mimetype='application/json'
                )
                
        except Exception as e:
            logger.error(f"Error handling tools request: {str(e)}")
            return func.HttpResponse(
                json.dumps({'error': str(e)}),
                status_code=500,
                mimetype='application/json'
            )
    
    def _handle_health_request(self) -> func.HttpResponse:
        """Handle health check requests"""
        try:
            health_status = {
                'status': 'healthy',
                'version': '1.0.0',
                'environment': os.environ.get('AZURE_FUNCTIONS_ENVIRONMENT', 'Dev'),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if self.framework:
                health_status['framework_status'] = 'initialized'
            else:
                health_status['framework_status'] = 'not_initialized'
            
            return func.HttpResponse(
                json.dumps(health_status),
                status_code=200,
                mimetype='application/json'
            )
        except Exception as e:
            return func.HttpResponse(
                json.dumps({'status': 'unhealthy', 'error': str(e)}),
                status_code=500,
                mimetype='application/json'
            )
    
    def _handle_metadata_request(self) -> func.HttpResponse:
        """Handle metadata requests"""
        try:
            metadata = {
                'name': 'MCP Framework',
                'version': '1.0.0',
                'description': 'Microsoft Cloud Platform Framework for Azure Functions',
                'domain': os.getenv('MCP_DOMAIN', 'unknown'),
                'environment': os.getenv('MCP_ENVIRONMENT', 'Dev')
            }
            
            return func.HttpResponse(
                json.dumps(metadata),
                status_code=200,
                mimetype='application/json'
            )
        except Exception as e:
            return func.HttpResponse(
                json.dumps({'error': str(e)}),
                status_code=500,
                mimetype='application/json'
            )
    
    def _handle_tool_execution(self, path: str, headers: Dict[str, str], body: Dict[str, Any]) -> func.HttpResponse:
        """Handle tool execution requests"""
        try:
            if not PLATFORM_IMPORTS_AVAILABLE:
                return func.HttpResponse(
                    json.dumps({'error': 'Platform framework not available'}),
                    status_code=500,
                    mimetype='application/json'
                )
            
            # Extract tool name from path
            parts = path.split('/')
            if len(parts) >= 2:
                tool_name = parts[1]
                if len(parts) >= 3 and parts[2] == 'execute':
                    return self._execute_tool(headers, body, tool_name)
                else:
                    return self._get_tool_metadata(tool_name)
            
            return func.HttpResponse(
                json.dumps({'error': 'Invalid path'}),
                status_code=400,
                mimetype='application/json'
            )
            
        except Exception as e:
            logger.error(f"Error handling tool execution: {str(e)}")
            return func.HttpResponse(
                json.dumps({'error': str(e)}),
                status_code=500,
                mimetype='application/json'
            )
    
    def _execute_tool(self, headers: Dict[str, str], body: Dict[str, Any], tool_name: str) -> func.HttpResponse:
        """Execute a specific tool"""
        try:
            if not PLATFORM_IMPORTS_AVAILABLE:
                return func.HttpResponse(
                    json.dumps({'error': 'Platform framework not available'}),
                    status_code=500,
                    mimetype='application/json'
                )
            
            arguments = body.get('arguments', {})
            registry = get_tool_registry()
            tool = registry.get_tool_by_name(tool_name)
            
            if not tool:
                return func.HttpResponse(
                    json.dumps({'error': f'Tool {tool_name} not found'}),
                    status_code=404,
                    mimetype='application/json'
                )
            
            # Execute tool
            module_name, func_name = tool.handler.rsplit('.', 1)
            import importlib
            module = importlib.import_module(module_name)
            tool_func = getattr(module, func_name)
            
            result = tool_func(**arguments)
            registry.increment_usage(tool.tool_id, success=True)
            
            return func.HttpResponse(
                json.dumps({'success': True, 'result': result}),
                status_code=200,
                mimetype='application/json'
            )
            
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            if PLATFORM_IMPORTS_AVAILABLE:
                from platform.errors import handle_exception
                error_response = handle_exception(e)
                return func.HttpResponse(
                    json.dumps(error_response.dict()),
                    status_code=500,
                    mimetype='application/json'
                )
            else:
                return func.HttpResponse(
                    json.dumps({'error': str(e)}),
                    status_code=500,
                    mimetype='application/json'
                )
    
    def _get_tool_metadata(self, tool_name: str) -> func.HttpResponse:
        """Get metadata for a specific tool"""
        try:
            if not PLATFORM_IMPORTS_AVAILABLE:
                return func.HttpResponse(
                    json.dumps({'error': 'Platform framework not available'}),
                    status_code=500,
                    mimetype='application/json'
                )
            
            registry = get_tool_registry()
            tool = registry.get_tool_by_name(tool_name)
            
            if not tool:
                return func.HttpResponse(
                    json.dumps({'error': f'Tool {tool_name} not found'}),
                    status_code=404,
                    mimetype='application/json'
                )
            
            return func.HttpResponse(
                json.dumps({
                    'name': tool.metadata.name,
                    'description': tool.metadata.description,
                    'domain': tool.metadata.domain,
                    'version': tool.metadata.version
                }),
                status_code=200,
                mimetype='application/json'
            )
            
        except Exception as e:
            logger.error(f"Error getting tool metadata: {str(e)}")
            return func.HttpResponse(
                json.dumps({'error': str(e)}),
                status_code=500,
                mimetype='application/json'
            )
    
    def _handle_error(self, e: Exception, start_time: datetime) -> func.HttpResponse:
        """Handle errors and return appropriate response"""
        try:
            if PLATFORM_IMPORTS_AVAILABLE:
                from platform.errors import handle_exception
                error_response = handle_exception(e)
                return func.HttpResponse(
                    json.dumps(error_response.dict()),
                    status_code=500,
                    mimetype='application/json'
                )
            else:
                return func.HttpResponse(
                    json.dumps({
                        'error': str(e),
                        'type': type(e).__name__,
                        'timestamp': datetime.utcnow().isoformat()
                    }),
                    status_code=500,
                    mimetype='application/json'
                )
        except Exception as inner_e:
            return func.HttpResponse(
                json.dumps({
                    'error': f'Error processing error: {str(inner_e)}',
                    'original_error': str(e)
                }),
                status_code=500,
                mimetype='application/json'
            )


# Create the FunctionApp instance - THIS IS REQUIRED FOR AZURE FUNCTIONS V2
app = MCPFunctionApp()

# Export the app object for Azure Functions
# This is the critical requirement for Python v2 programming model
