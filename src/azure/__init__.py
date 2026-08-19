"""
MCP Framework Azure Functions Package
This package contains the Azure Functions implementation for the MCP Framework.

Compatible with Microsoft Copilot and Copilot Studio through MCP Protocol.
"""

# Import the app objects for Azure Functions v2
from .function_app import app as legacy_app
from .mcp_server import app as mcp_app
from .host import main

# For backward compatibility
app = mcp_app  # Default to MCP server for root-level imports

__all__ = ['app', 'main', 'legacy_app', 'mcp_app']

# Version information
__version__ = "1.0.0"
__author__ = "MCP Framework Team"
__description__ = "Azure Functions implementation for MCP Framework - Copilot/Copilot Studio Compatible"