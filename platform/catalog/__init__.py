"""
Catalog Integration Module for MCP Platform Framework

This module provides automatic registration of MCP services with the enterprise
registry and governance catalog. It ensures that all deployed MCP tools are
discoverable, properly classified, and compliant with organizational governance
policies.

Key Features:
- Automatic service registration on deployment
- Metadata validation and standardization
- Integration with enterprise governance catalog
- Classification enforcement
- Ownership and SLA tracking
- Search and discovery capabilities
"""

from .models import Classification, SLATier, ToolMetadata, ToolRegistration, ParameterMetadata
from .client import CatalogClient
from .validator import MetadataValidator
from .sync import CatalogSync

__all__ = [
    'Classification',
    'SLATier', 
    'ToolMetadata',
    'ToolRegistration',
    'ParameterMetadata',
    'CatalogClient',
    'MetadataValidator',
    'CatalogSync'
]

# Module version
__version__ = "1.2.0"
