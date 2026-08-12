"""Main Entry Point for Azure Function App - MCP Framework"""
import os
import sys
import json
import logging
import traceback
from typing import Optional, Dict, Any, List
from datetime import datetime
import azure.functions as func

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import platform framework
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
            else:
                return self._handle_tool_execution(path, headers, body)
                
        except Exception as e:
            return self._handle_error(e, start_time)
    
    def _handle_tools_request(self, method: str, path: str, headers: Dict[str, str], 
                              query_params: Dict[str, str], body: Dict[str, Any]) -> func.HttpResponse:
        """Handle requests to /api/tools endpoint"""
        try:
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
                # This would typically be done through the framework, not via API
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
                'timestamp': datetime.utcnow().isoformat(),
                'framework': 'MCP Platform Framework',
                'version': '1.0.0'
            }
            
            # Add component health checks
            if self.framework:
                health_status['components'] = {
                    'authentication': 'healthy' if self.framework._authenticator else 'disabled',
                    'authorization': 'healthy' if self.framework._rbac_engine else 'disabled',
                    'telemetry': 'healthy' if self.framework._telemetry_collector else 'disabled',
                    'audit': 'healthy' if self.framework._audit_logger else 'disabled',
                    'fabric': 'healthy' if self.framework._fabric_connectors else 'disabled'
                }
            
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
            if not self.framework:
                return func.HttpResponse(
                    json.dumps({'error': 'Framework not initialized'}),
                    status_code=500,
                    mimetype='application/json'
                )
            
            metadata = {
                'domain': self.framework.get_domain(),
                'environment': self.framework.get_environment(),
                'version': '1.0.0',
                'timestamp': datetime.utcnow().isoformat(),
                'features': {
                    'authentication': self.framework.config.enable_authentication,
                    'authorization': self.framework.config.enable_authorization,
                    'telemetry': self.framework.config.enable_telemetry,
                    'audit': self.framework.config.enable_audit,
                    'classification': self.framework.config.enable_classification,
                    'auto_discovery': self.framework.config.auto_discover_tools
                }
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
            # Extract tool name from path (e.g., /GetDonorPortfolioHealth -> GetDonorPortfolioHealth)
            tool_name = path.lstrip('/')
            if not tool_name:
                return func.HttpResponse(
                    json.dumps({'error': 'Tool name not specified'}),
                    status_code=400,
                    mimetype='application/json'
                )
            
            # Get tool from registry
            registry = get_tool_registry()
            tool_registration = registry.get_tool_by_name(tool_name)
            
            if not tool_registration:
                return func.HttpResponse(
                    json.dumps({'error': f'Tool {tool_name} not found'}),
                    status_code=404,
                    mimetype='application/json'
                )
            
            # Check if tool is active
            if tool_registration.metadata.status.value != 'active':
                return func.HttpResponse(
                    json.dumps({'error': f'Tool {tool_name} is not active'}),
                    status_code=403,
                    mimetype='application/json'
                )
            
            # Authenticate the request
            auth_result = self._authenticate_request(headers, tool_registration)
            if not auth_result.success:
                return func.HttpResponse(
                    json.dumps({'error': auth_result.error}),
                    status_code=401,
                    mimetype='application/json'
                )
            
            # Execute the tool
            result = self._execute_tool(tool_registration, body, auth_result)
            
            # Track telemetry
            if self.framework and self.framework.config.enable_telemetry:
                track_tool_telemetry(tool_name, result)
            
            # Log audit
            if self.framework and self.framework.config.enable_audit:
                audit_tool_access(
                    user=auth_result.user_id,
                    tool=tool_name,
                    domain=tool_registration.metadata.domain,
                    success=result.get('success', True),
                    metadata={'request_id': headers.get('X-Request-ID')}
                )
            
            return func.HttpResponse(
                json.dumps(result),
                status_code=200,
                mimetype='application/json'
            )
            
        except Exception as e:
            logger.error(f"Error executing tool {path}: {str(e)}")
            return func.HttpResponse(
                json.dumps({'error': str(e)}),
                status_code=500,
                mimetype='application/json'
            )
    
    def _authenticate_request(self, headers: Dict[str, str], tool_registration: Any) -> AuthenticationResult:
        """Authenticate an incoming request"""
        try:
            if not tool_registration.metadata.requires_authentication:
                return AuthenticationResult(
                    success=True,
                    user_id="anonymous",
                    authenticated=False,
                    error=None
                )
            
            # Extract token from headers
            auth_header = headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return AuthenticationResult(
                    success=False,
                    user_id=None,
                    authenticated=False,
                    error="Authorization header missing or invalid"
                )
            
            token = auth_header[7:]  # Remove 'Bearer ' prefix
            
            # Authenticate using the framework
            if self.framework:
                auth_result = self.framework.auth.authenticate(token)
                if auth_result.success:
                    return AuthenticationResult(
                        success=True,
                        user_id=auth_result.identity.user_id,
                        authenticated=True,
                        error=None
                    )
                else:
                    return AuthenticationResult(
                        success=False,
                        user_id=None,
                        authenticated=False,
                        error=auth_result.error
                    )
            else:
                # Fallback to direct authenticator
                authenticator = get_authenticator()
                auth_result = authenticator.authenticate(token)
                if auth_result.success:
                    return AuthenticationResult(
                        success=True,
                        user_id=auth_result.identity.user_id,
                        authenticated=True,
                        error=None
                    )
                else:
                    return AuthenticationResult(
                        success=False,
                        user_id=None,
                        authenticated=False,
                        error=auth_result.error
                    )
                    
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return AuthenticationResult(
                success=False,
                user_id=None,
                authenticated=False,
                error=str(e)
            )
    
    def _execute_tool(self, tool_registration: Any, body: Dict[str, Any], auth_result: AuthenticationResult) -> Dict[str, Any]:
        """Execute a registered tool"""
        try:
            # Get the tool handler
            handler_path = tool_registration.handler
            if not handler_path:
                return {'error': 'Tool handler not configured'}
            
            # Import and execute the tool function
            module_name, function_name = handler_path.rsplit('.', 1)
            
            try:
                module = __import__(module_name, fromlist=[function_name])
                tool_func = getattr(module, function_name)
                
                # Execute the function with the request body as arguments
                result = tool_func(**body)
                
                return {
                    'success': True,
                    'tool': tool_registration.metadata.name,
                    'domain': tool_registration.metadata.domain,
                    'result': result,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
            except ImportError as e:
                logger.error(f"Error importing tool module {module_name}: {str(e)}")
                return {'error': f'Tool module not found: {module_name}'}
            except AttributeError as e:
                logger.error(f"Error finding tool function {function_name} in {module_name}: {str(e)}")
                return {'error': f'Tool function not found: {function_name}'}
            except Exception as e:
                logger.error(f"Error executing tool {tool_registration.metadata.name}: {str(e)}")
                return {'error': str(e)}
                
        except Exception as e:
            logger.error(f"Error in tool execution: {str(e)}")
            return {'error': str(e)}
    
    def _handle_error(self, error: Exception, start_time: datetime) -> func.HttpResponse:
        """Handle errors and return appropriate response"""
        try:
            error_handler = get_error_handler()
            error_response = error_handler.handle_error(error)
            
            # Log the error
            logger.error(f"Error: {str(error)}")
            logger.error(traceback.format_exc())
            
            # Track telemetry for error
            if self.framework and self.framework.config.enable_telemetry:
                telemetry = get_telemetry_collector()
                telemetry.track_error(
                    error_type=type(error).__name__,
                    error_message=str(error),
                    duration_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
                )
            
            return func.HttpResponse(
                json.dumps(error_response),
                status_code=error_response.get('status_code', 500),
                mimetype='application/json'
            )
            
        except Exception as e:
            logger.error(f"Error handling error: {str(e)}")
            return func.HttpResponse(
                json.dumps({'error': 'Internal server error'}),
                status_code=500,
                mimetype='application/json'
            )


# Create the Function App instance
mcp_app = MCPFunctionApp()


# Azure Functions HTTP trigger
def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Functions HTTP trigger for MCP Framework.
    
    This is the main entry point for the Function App.
    """
    return mcp_app.handle_request(req)


# For local testing
def local_main():
    """Local testing entry point"""
    import http.server
    import socketserver
    from urllib.parse import urlparse, parse_qs
    import json
    
    class MCPRequestHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.handle_request('GET')
        
        def do_POST(self):
            self.handle_request('POST')
        
        def handle_request(self, method):
            # Parse URL and query parameters
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)
            
            # Read headers
            headers = dict(self.headers)
            
            # Read body
            content_length = int(headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else b''
            
            try:
                body_json = json.loads(body.decode('utf-8')) if body else {}
            except:
                body_json = {}
            
            # Create a mock HttpRequest
            class MockHttpRequest:
                def __init__(self, method, path, headers, params, body):
                    self.method = method
                    self.path = path
                    self.headers = headers
                    self.params = params
                    self._body = body
                
                def get_json(self):
                    return self._body
                
                def get_body(self):
                    return json.dumps(self._body).encode('utf-8')
            
            mock_req = MockHttpRequest(
                method=method,
                path=path,
                headers=headers,
                params=query_params,
                body=body_json
            )
            
            # Handle the request
            response = main(mock_req)
            
            # Send response
            self.send_response(response.status_code)
            self.send_header('Content-type', response.headers.get('Content-Type', 'application/json'))
            self.end_headers()
            self.wfile.write(response.get_body())
    
    # Start local server
    PORT = 8080
    with socketserver.TCPServer(("", PORT), MCPRequestHandler) as httpd:
        print(f"Local MCP server started on port {PORT}")
        httpd.serve_forever()


if __name__ == "__main__":
    # Check if running in Azure Functions or locally
    if os.getenv('FUNCTIONS_WORKER_RUNTIME'):
        # Running in Azure Functions
        logger.info("MCP Framework running in Azure Functions")
    else:
        # Running locally
        logger.info("MCP Framework running locally")
        local_main()