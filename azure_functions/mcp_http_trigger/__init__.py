"""
MCP HTTP Trigger for Azure Function Apps
"""
import azure.functions as func
import logging
import json
import os

logger = logging.getLogger(__name__)

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Main HTTP trigger for MCP tool execution"""
    import time
    start_time = time.time()
    
    try:
        from platform.auth import CallerIdentity, get_current_identity, set_current_identity
        from platform.telemetry import get_telemetry_collector
        from platform.errors import handle_exception
        from platform.registration import get_tool_registry
        
        # Extract identity
        identity = _extract_identity(req)
        set_current_identity(identity)
        
        # Parse path
        path = req.route_params.get("path", "")
        
        # Route requests
        if path.startswith("tools/"):
            return _handle_tools(req, path)
        elif path == "tools":
            return _list_tools(req)
        elif path == "health":
            return _health_check(req)
        else:
            return func.HttpResponse("Not found", status_code=404)
            
    except Exception as e:
        logger.error(f"Error: {e}")
        error_response = handle_exception(e)
        return func.HttpResponse(json.dumps(error_response.dict()), status_code=500)
    finally:
        set_current_identity(None)


def _extract_identity(req: func.HttpRequest) -> CallerIdentity:
    """Extract identity from request"""
    from platform.auth import CallerIdentity
    
    auth_header = req.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        try:
            from platform.auth import get_jwt_validator
            validator = get_jwt_validator()
            if validator:
                token_data = validator.validate_token(token)
                return CallerIdentity(
                    user_id=token_data.sub,
                    username=token_data.name,
                    email=token_data.email,
                    authentication_type="entra_id",
                    is_authenticated=True,
                    claims={"roles": token_data.roles, "scopes": token_data.scopes}
                )
        except:
            pass
    
    return CallerIdentity(user_id="anonymous", authentication_type="none", is_authenticated=False)


def _handle_tools(req: func.HttpRequest, path: str) -> func.HttpResponse:
    """Handle tool requests"""
    parts = path.split("/")
    if len(parts) >= 2:
        tool_name = parts[1]
        if len(parts) >= 3 and parts[2] == "execute":
            return _execute_tool(req, tool_name)
        else:
            return _get_tool_metadata(tool_name)
    return func.HttpResponse("Invalid path", status_code=400)


def _execute_tool(req: func.HttpRequest, tool_name: str) -> func.HttpResponse:
    """Execute a tool"""
    try:
        body = req.get_json() or {}
        arguments = body.get("arguments", {})
        
        registry = get_tool_registry()
        tool = registry.get_tool_by_name(tool_name)
        
        if not tool:
            return func.HttpResponse(f"Tool {tool_name} not found", status_code=404)
        
        # Execute tool
        module_name, func_name = tool.handler.rsplit(".", 1)
        import importlib
        module = importlib.import_module(module_name)
        tool_func = getattr(module, func_name)
        
        result = tool_func(**arguments)
        registry.increment_usage(tool.tool_id, success=True)
        
        return func.HttpResponse(json.dumps({"success": True, "result": result}))
        
    except Exception as e:
        error_response = handle_exception(e)
        return func.HttpResponse(json.dumps(error_response.dict()), status_code=500)


def _get_tool_metadata(self, tool_name: str) -> func.HttpResponse:
    """Get tool metadata"""
    registry = get_tool_registry()
    tool = registry.get_tool_by_name(tool_name)
    
    if not tool:
        return func.HttpResponse(f"Tool {tool_name} not found", status_code=404)
    
    return func.HttpResponse(json.dumps({
        "name": tool.metadata.name,
        "description": tool.metadata.description,
        "domain": tool.metadata.domain,
        "version": tool.metadata.version
    }))


def _list_tools(self, req: func.HttpRequest) -> func.HttpResponse:
    """List all tools"""
    registry = get_tool_registry()
    tools = registry.get_all_tools()
    
    tools_list = [{
        "id": tool.tool_id,
        "name": tool.metadata.name,
        "description": tool.metadata.description,
        "domain": tool.metadata.domain
    } for tool in tools]
    
    return func.HttpResponse(json.dumps({"tools": tools_list, "count": len(tools_list)}))


def _health_check(self, req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint"""
    return func.HttpResponse(json.dumps({
        "status": "healthy",
        "version": "1.0.0",
        "environment": os.environ.get("AZURE_FUNCTIONS_ENVIRONMENT", "Dev")
    }))