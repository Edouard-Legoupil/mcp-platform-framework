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
"""

# Version information
__version__ = "1.0.0"
__author__ = "MCP Platform Team"
__description__ = "Infrastructure framework for MCP domain implementations"
