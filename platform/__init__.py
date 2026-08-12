"""
MCP Platform Framework

This framework provides the infrastructure layer for MCP (Model Context Protocol) implementations,
enforcing strict separation between platform concerns and domain business capabilities.

Principles:
- Domains own business capabilities (business logic, ontologies, semantic definitions)
- Platform owns everything else (authentication, authorization, telemetry, error handling, connectivity)
- No domain forking - all domains use the same template from this central repository

Platform Modules:
- platform.auth: Authentication and identity management
- platform.authorization: Enterprise RBAC and policy enforcement
- platform.telemetry: Automatic observability and monitoring
- platform.audit: Immutable compliance logging
- platform.errors: Standardized error handling
- platform.config: Environment-aware configuration
- platform.connectivity: Fabric and semantic model connectors
- platform.registration: Automatic tool discovery and registration
- platform.classification: Data classification controls
- platform.framework: Main framework integration
"""

# Version information
__version__ = "1.0.0"
__author__ = "MCP Platform Team"
__description__ = "Infrastructure framework for MCP domain implementations"

# Import main framework components for convenience
from .framework import (
    MCPFramework, 
    FrameworkConfig,
    get_framework, 
    reset_framework,
    initialize_framework
)

# Import platform modules for convenience
from .auth import authenticated_tool, requires_permission, requires_role
from .classification import classification, classify_data, requires_classification
from .registration import tool, resource, query, action
from .connectivity import fabric, semantic_model
from .telemetry import track_tool_telemetry
from .audit import audit_tool_access, audit_data_access

__all__ = [
    # Framework
    'MCPFramework', 'FrameworkConfig',
    'get_framework', 'reset_framework', 'initialize_framework',
    # Decorators
    'authenticated_tool', 'requires_permission', 'requires_role',
    'classification', 'classify_data', 'requires_classification',
    'tool', 'resource', 'query', 'action',
    # Connectivity
    'fabric', 'semantic_model',
    # Telemetry and Audit
    'track_tool_telemetry', 'audit_tool_access', 'audit_data_access',
    # Metadata
    '__version__', '__author__', '__description__'
]
