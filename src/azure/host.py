"""
Azure Functions Host Configuration for MCP Framework
This is the main entry point for Azure Functions v2 programming model
"""
import azure.functions as func
import logging
import os
from typing import Optional

# Import the main function app
from .function_app import app

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
    This function is triggered by HTTP requests and routes to the MCP Function App.
    """
    return app.handle_request(req)

# For local testing and development
if __name__ == "__main__":
    logger.info("MCP Framework Azure Functions host starting...")
    # The app object is already created and can be used for local testing
    logger.info("Function App initialized successfully")