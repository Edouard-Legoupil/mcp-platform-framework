"""
MCP Framework - Tools Package

This package contains example tools that can be used with the MCP Framework.
Each tool is a Python function that can be registered with the MCP server
and executed via the MCP protocol.

To create a new tool:
1. Create a new Python file in this directory
2. Define a function with the required signature
3. Register it in the platform.registration module

Example:
    from tools.example_tool import my_tool_function
    
    # In your registration code:
    registry.register_tool(
        name="my_tool",
        description="Description of my tool",
        handler="tools.example_tool.my_tool_function",
        domain="example"
    )
"""

__version__ = "1.0.0"
