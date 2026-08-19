"""
Azure Functions Host Configuration for MCP Framework
This is the main entry point for Azure Functions v2 programming model

Supports both:
1. Legacy MCP Framework API endpoints (/api/tools, /api/health, etc.)
2. Standard MCP Protocol endpoints (/mcp/health, /mcp/tools, etc.)

Compatible with Microsoft Copilot and Copilot Studio
"""
import azure.functions as func
import logging
import os
from typing import Optional

# Import the main function app
from .function_app import app as legacy_app
from .mcp_server import app as mcp_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the Function App
def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Main entry point for Azure Functions.
    This function is triggered by HTTP requests and routes to the appropriate handler.
    
    Routes:
    - /mcp/* -> MCP Protocol endpoints (Copilot/Copilot Studio compatible)
    - /api/* -> Legacy MCP Framework API endpoints
    - /* -> MCP Protocol endpoints (fallback)
    """
    import json
    
    try:
        path = req.path
        method = req.method
        
        logger.info(f"Received {method} request for {path}")
        
        # Route to MCP Server for MCP protocol endpoints
        if path.startswith("/mcp/"):
            logger.info(f"Routing to MCP Server: {path}")
            return mcp_app.handle_request(req)
        
        # Route to legacy app for API endpoints
        elif path.startswith("/api/"):
            logger.info(f"Routing to Legacy App: {path}")
            return legacy_app.handle_request(req)
        
        # Route to MCP Server for root-level MCP endpoints
        elif path in ["/health", "/tools", "/resources", "/prompts", "/completions"]:
            # Redirect to MCP endpoints
            new_path = f"/mcp{path}"
            logger.info(f"Redirecting to MCP endpoint: {new_path}")
            
            # Create a new request with updated path
            from unittest.mock import Mock
            mock_req = Mock(spec=func.HttpRequest)
            mock_req.method = req.method
            mock_req.path = new_path
            mock_req.headers = dict(req.headers)
            mock_req.params = dict(req.params)
            mock_req.get_json = req.get_json
            mock_req.get_body = req.get_body
            
            return mcp_app.handle_request(mock_req)
        
        # Default to MCP Server
        else:
            logger.info(f"Routing to MCP Server (default): {path}")
            return mcp_app.handle_request(req)
            
    except Exception as e:
        logger.error(f"Error routing request: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": str(e),
                "type": type(e).__name__,
                "timestamp": __import__('datetime').datetime.utcnow().isoformat() + "Z"
            }),
            status_code=500,
            mimetype='application/json'
        )

# For local testing and development
if __name__ == "__main__":
    logger.info("MCP Framework Azure Functions host starting...")
    # The app objects are already created and can be used for local testing
    logger.info("Function App initialized successfully")
    logger.info("MCP Server initialized successfully")
    logger.info("Ready to handle requests on /mcp/* and /api/* endpoints")