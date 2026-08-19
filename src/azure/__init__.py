"""
MCP Framework Azure Functions Package
This package contains the Azure Functions implementation for the MCP Framework.
"""

# Import the app object for Azure Functions v2
from .function_app import app
from .host import main

__all__ = ['app', 'main']

# Version information
__version__ = "1.0.0"
__author__ = "MCP Framework Team"
__description__ = "Azure Functions implementation for MCP Framework"