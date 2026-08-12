"""Tool Registration Decorators for MCP Framework"""
import functools
import inspect
import logging
from typing import Callable, Optional, Any, Dict
from .models import ToolMetadata, ToolType, ParameterSchema
from .registry import get_tool_registry, RegistrationRequest

logger = logging.getLogger(__name__)

# Global domain context (set during framework initialization)
_domain_context: Optional[str] = None


def set_domain_context(domain: str):
    """Set the current domain context for tool registration"""
    global _domain_context
    _domain_context = domain


def get_domain_context() -> str:
    """Get the current domain context"""
    if _domain_context is None:
        raise ValueError("Domain context not set. Call set_domain_context() during framework initialization.")
    return _domain_context


def _extract_function_metadata(func: Callable) -> Dict[str, Any]:
    """Extract metadata from function signature and docstring"""
    sig = inspect.signature(func)
    docstring = inspect.getdoc(func) or ""
    
    # Parse docstring for description
    description = docstring.strip().split('\n')[0] if docstring.strip() else func.__name__
    
    # Extract parameters
    parameters = {}
    for name, param in sig.parameters.items():
        if name == 'self':
            continue
        param_type = param.annotation.__name__ if param.annotation != inspect.Parameter.empty else 'Any'
        parameters[name] = ParameterSchema(
            name=name,
            type=param_type,
            description=None,  # Could extract from docstring
            required=param.default == inspect.Parameter.empty,
            default=param.default if param.default != inspect.Parameter.empty else None
        )
    
    # Extract return type
    return_annotation = sig.return_annotation
    returns = return_annotation.__name__ if return_annotation != inspect.Parameter.empty else None
    
    return {
        'description': description,
        'parameters': parameters,
        'returns': returns
    }


def tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    tool_type: ToolType = ToolType.FUNCTION,
    classification: Optional[str] = None,
    requires_authentication: bool = True,
    requires_authorization: bool = True,
    timeout_seconds: int = 30,
    max_retries: int = 3,
    rate_limit: Optional[str] = None,
    owner: Optional[str] = None,
    maintainer: Optional[str] = None,
    sla: Optional[str] = None,
    tags: Optional[list] = None,
    categories: Optional[list] = None
):
    """
    Decorator to register a function as an MCP tool.
    
    Args:
        name: Tool name (defaults to function name)
        description: Tool description (defaults to docstring)
        tool_type: Type of tool (FUNCTION, QUERY, ACTION, RESOURCE)
        classification: Data classification level
        requires_authentication: Whether authentication is required
        requires_authorization: Whether authorization is required
        timeout_seconds: Maximum execution time
        max_retries: Maximum number of retries
        rate_limit: Rate limiting configuration
        owner: Tool owner
        maintainer: Tool maintainer
        sla: Service Level Agreement
        tags: List of tags for categorization
        categories: List of categories for grouping
    
    Example:
        @tool(description="Get donor portfolio health")
        def get_donor_portfolio_health(donor_id: str) -> dict:
            return {"health": "good"}
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # Extract metadata from function
        func_metadata = _extract_function_metadata(func)
        
        # Set default values
        tool_name = name or func.__name__
        tool_description = description or func_metadata['description']
        
        # Create tool metadata
        metadata = ToolMetadata(
            name=tool_name,
            description=tool_description,
            tool_type=tool_type,
            domain=get_domain_context(),
            classification=classification,
            requires_authentication=requires_authentication,
            requires_authorization=requires_authorization,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            rate_limit=rate_limit,
            owner=owner or get_domain_context(),
            maintainer=maintainer,
            sla=sla,
            parameters=func_metadata['parameters'],
            returns=func_metadata['returns'],
            tags=tags or [],
            categories=categories or []
        )
        
        # Register the tool
        try:
            registry = get_tool_registry()
            request = RegistrationRequest(
                metadata=metadata,
                handler=f"{func.__module__}.{func.__name__}"
            )
            result = registry.register_tool(request)
            if result.success:
                logger.info(f"Tool registered: {tool_name}")
                # Store registration info on the function for later reference
                wrapper._tool_id = result.tool_id
                wrapper._tool_metadata = metadata
            else:
                logger.error(f"Failed to register tool {tool_name}: {result.message}")
        except Exception as e:
            logger.error(f"Error registering tool {tool_name}: {str(e)}")
        
        return wrapper
    return decorator


def resource(
    name: Optional[str] = None,
    description: Optional[str] = None,
    classification: Optional[str] = None,
    **kwargs
):
    """
    Decorator to register a function as a resource tool.
    
    Example:
        @resource(description="Get donor data")
        def get_donor_data(donor_id: str) -> dict:
            return {"id": donor_id}
    """
    return tool(
        name=name,
        description=description,
        tool_type=ToolType.RESOURCE,
        classification=classification,
        **kwargs
    )


def query(
    name: Optional[str] = None,
    description: Optional[str] = None,
    classification: Optional[str] = None,
    **kwargs
):
    """
    Decorator to register a function as a query tool.
    
    Example:
        @query(description="Query donor contributions")
        def query_donor_contributions(donor_id: str, year: int) -> list:
            return []
    """
    return tool(
        name=name,
        description=description,
        tool_type=ToolType.QUERY,
        classification=classification,
        **kwargs
    )


def action(
    name: Optional[str] = None,
    description: Optional[str] = None,
    classification: Optional[str] = None,
    **kwargs
):
    """
    Decorator to register a function as an action tool.
    
    Example:
        @action(description="Update donor information")
        def update_donor_info(donor_id: str, data: dict) -> bool:
            return True
    """
    return tool(
        name=name,
        description=description,
        tool_type=ToolType.ACTION,
        classification=classification,
        **kwargs
    )