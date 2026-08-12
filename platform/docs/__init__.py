"""
Documentation Generator Module for MCP Platform Framework

This module provides automatic generation of comprehensive technical documentation
from MCP tool metadata, annotations, and code structure. It ensures that all deployed
tools have consistent, up-to-date documentation that follows organizational standards.

Key Features:
- Automatic generation from tool decorators and docstrings
- Support for multiple output formats (Markdown, HTML, PDF, API specs)
- Template-based customization
- Integration with catalog metadata
- Version-aware documentation
- Search and indexing capabilities
"""

from .generator import DocumentationGenerator
from .models import (
    OutputFormat, DocumentationMetadata, ParameterMetadata, 
    Classification, SLATier
)
from .templates import TemplateEngine
from .exceptions import (
    DocumentationError,
    DocumentationGenerationError,
    DocumentationTemplateError,
    DocumentationValidationError
)

__all__ = [
    'DocumentationGenerator',
    'OutputFormat',
    'DocumentationMetadata',
    'ParameterMetadata',
    'Classification',
    'SLATier',
    'TemplateEngine',
    'DocumentationError',
    'DocumentationGenerationError',
    'DocumentationTemplateError',
    'DocumentationValidationError',
    'generate_tool_docs',
    'generate_domain_docs',
    'generate_api_spec'
]

# Module version
__version__ = "1.3.0"

# Convenience functions
def generate_tool_docs(
    tool_name: str,
    output_formats: list = None,
    output_dir: str = None,
    **kwargs
) -> dict:
    """
    Generate documentation for a specific tool.
    
    Args:
        tool_name: Name of the tool to document
        output_formats: List of output formats to generate
        output_dir: Output directory
        **kwargs: Additional arguments passed to DocumentationGenerator
        
    Returns:
        Dictionary mapping format names to generated file paths
    """
    generator = DocumentationGenerator(**kwargs)
    return generator.generate_tool_docs(
        tool_name=tool_name,
        output_formats=output_formats,
        output_dir=output_dir
    )


def generate_domain_docs(
    domain: str,
    output_formats: list = None,
    output_dir: str = None,
    **kwargs
) -> dict:
    """
    Generate documentation for all tools in a domain.
    
    Args:
        domain: Domain name
        output_formats: List of output formats to generate
        output_dir: Output directory
        **kwargs: Additional arguments passed to DocumentationGenerator
        
    Returns:
        Dictionary mapping format names to lists of generated file paths
    """
    generator = DocumentationGenerator(**kwargs)
    return generator.generate_domain_docs(
        domain=domain,
        output_formats=output_formats,
        output_dir=output_dir
    )


def generate_api_spec(
    domain: str = None,
    output_path: str = None,
    **kwargs
) -> str:
    """
    Generate OpenAPI specification for tools.
    
    Args:
        domain: Specific domain to include (None for all domains)
        output_path: Output file path
        **kwargs: Additional arguments passed to DocumentationGenerator
        
    Returns:
        Path to generated OpenAPI specification file
    """
    generator = DocumentationGenerator(**kwargs)
    return generator.generate_api_spec(
        domain=domain,
        output_path=output_path
    )
