"""
MCP Framework - Example Tool

This is an example tool that demonstrates how to create MCP-compatible tools.
Tools are simple Python functions that can be executed via the MCP protocol.
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def echo_tool(message: str, **kwargs: Any) -> Dict[str, Any]:
    """
    Example Echo Tool
    
    This tool simply echoes back the input message along with any additional
    keyword arguments. It's useful for testing MCP tool execution.
    
    Args:
        message: The message to echo back
        **kwargs: Additional keyword arguments to include in the response
        
    Returns:
        Dict containing the echoed message and any additional arguments
        
    Example:
        >>> echo_tool("Hello World", extra="value")
        {'message': 'Hello World', 'extra': 'value'}
    """
    result = {"message": message}
    result.update(kwargs)
    
    logger.info(f"Echo tool executed with message: {message}")
    
    return result


def calculate_sum(numbers: list, **kwargs: Any) -> Dict[str, Any]:
    """
    Example Calculation Tool
    
    This tool calculates the sum of a list of numbers.
    
    Args:
        numbers: List of numbers to sum
        **kwargs: Additional keyword arguments (ignored)
        
    Returns:
        Dict containing the sum and count of numbers
        
    Example:
        >>> calculate_sum([1, 2, 3, 4, 5])
        {'sum': 15, 'count': 5}
    """
    if not numbers:
        return {"sum": 0, "count": 0, "error": "No numbers provided"}
    
    total = sum(numbers)
    count = len(numbers)
    
    logger.info(f"Calculated sum of {count} numbers: {total}")
    
    return {
        "sum": total,
        "count": count,
        "numbers": numbers
    }


def get_environment_info(**kwargs: Any) -> Dict[str, Any]:
    """
    Example Environment Info Tool
    
    This tool returns information about the current environment.
    Useful for debugging and understanding the deployment context.
    
    Args:
        **kwargs: Additional keyword arguments (ignored)
        
    Returns:
        Dict containing environment information
        
    Example:
        >>> get_environment_info()
        {'environment': 'Development', 'server': 'MCP Framework Server', ...}
    """
    import os
    from datetime import datetime
    
    info = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "server_name": os.getenv('MCP_SERVER_NAME', 'MCP Framework Server'),
        "server_version": os.getenv('MCP_SERVER_VERSION', '1.0.0'),
        "protocol_version": os.getenv('MCP_PROTOCOL_VERSION', '2024-11-05'),
        "environment": os.getenv('MCP_ENVIRONMENT', 'Development'),
        "domain": os.getenv('MCP_DOMAIN', 'Unknown'),
        "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
        "platform": os.name
    }
    
    # Add Azure-specific info if available
    if os.getenv('WEBSITE_SITE_NAME'):
        info['azure_function_app'] = os.getenv('WEBSITE_SITE_NAME')
    if os.getenv('WEBSITE_INSTANCE_ID'):
        info['azure_instance_id'] = os.getenv('WEBSITE_INSTANCE_ID')
    
    logger.info("Environment info tool executed")
    
    return info


# Tool metadata for registration
TOOLS = [
    {
        "name": "echo",
        "description": "Echoes back the input message",
        "handler": "tools.example_tool.echo_tool",
        "domain": "example",
        "version": "1.0.0",
        "input_schema": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "The message to echo"}
            },
            "required": ["message"]
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            }
        }
    },
    {
        "name": "calculate_sum",
        "description": "Calculates the sum of a list of numbers",
        "handler": "tools.example_tool.calculate_sum",
        "domain": "example",
        "version": "1.0.0",
        "input_schema": {
            "type": "object",
            "properties": {
                "numbers": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "List of numbers to sum"
                }
            },
            "required": ["numbers"]
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "sum": {"type": "number"},
                "count": {"type": "integer"},
                "numbers": {"type": "array", "items": {"type": "number"}}
            }
        }
    },
    {
        "name": "get_environment_info",
        "description": "Returns information about the current environment",
        "handler": "tools.example_tool.get_environment_info",
        "domain": "example",
        "version": "1.0.0",
        "input_schema": {
            "type": "object",
            "properties": {}
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "timestamp": {"type": "string"},
                "server_name": {"type": "string"},
                "server_version": {"type": "string"},
                "protocol_version": {"type": "string"},
                "environment": {"type": "string"},
                "domain": {"type": "string"},
                "python_version": {"type": "string"},
                "platform": {"type": "string"}
            }
        }
    }
]
