"""MCP Platform Framework - Main Integration Class"""
import logging
import os
import sys
from typing import Optional, Dict, Any, List, Callable, Type
from pathlib import Path
from dataclasses import dataclass, field
from .auth import (
    EntraIDAuthenticator, 
    ManagedIdentityAuthenticator,
    get_authenticator,
    set_domain_context as set_auth_domain_context
)
from .authorization import RBACEngine, get_rbac_engine
from .telemetry import TelemetryCollector, get_telemetry_collector
from .audit import AuditLogger, get_audit_logger
from .errors import ErrorHandler, get_error_handler
from .config import ConfigManager, get_config_manager
from .classification import ClassificationEngine, get_classification_engine
from .registration import (
    ToolRegistry, 
    get_tool_registry, 
    ToolDiscovery,
    set_domain_context as set_registration_domain_context
)
from .connectivity import FabricConnectors, get_fabric_connectors

logger = logging.getLogger(__name__)


@dataclass
class FrameworkConfig:
    """Configuration for the MCP Platform Framework"""
    domain: str
    environment: str = "Dev"
    enable_telemetry: bool = True
    enable_audit: bool = True
    enable_authentication: bool = True
    enable_authorization: bool = True
    enable_classification: bool = True
    auto_discover_tools: bool = True
    tool_paths: List[str] = field(default_factory=lambda: ["tools", "queries", "actions", "resources"])
    
    @classmethod
    def from_environment(cls) -> 'FrameworkConfig':
        """Create FrameworkConfig from environment variables"""
        domain = os.getenv('MCP_DOMAIN', 'unknown')
        environment = os.getenv('MCP_ENVIRONMENT', 'Dev')
        
        return cls(
            domain=domain,
            environment=environment,
            enable_telemetry=os.getenv('MCP_ENABLE_TELEMETRY', 'true').lower() == 'true',
            enable_audit=os.getenv('MCP_ENABLE_AUDIT', 'true').lower() == 'true',
            enable_authentication=os.getenv('MCP_ENABLE_AUTH', 'true').lower() == 'true',
            enable_authorization=os.getenv('MCP_ENABLE_AUTHORIZATION', 'true').lower() == 'true',
            enable_classification=os.getenv('MCP_ENABLE_CLASSIFICATION', 'true').lower() == 'true',
            auto_discover_tools=os.getenv('MCP_AUTO_DISCOVER_TOOLS', 'true').lower() == 'true'
        )


class MCPFramework:
    """
    Main MCP Platform Framework class.
    
    This class integrates all platform modules and provides a unified interface
    for domain developers. It handles initialization, configuration, and lifecycle
    management of all platform services.
    
    Example:
        # Initialize the framework
        framework = MCPFramework(domain="DonorManagement")
        
        # Or use the global instance
        from platform.framework import get_framework
        framework = get_framework()
        
        # Access platform services
        framework.auth.authenticate(request)
        framework.telemetry.track_tool_execution(tool_name, duration)
        framework.audit.log_access(user, tool_name)
    """
    
    def __init__(self, config: Optional[FrameworkConfig] = None):
        """
        Initialize the MCP Platform Framework.
        
        Args:
            config: Framework configuration (defaults to environment-based config)
        """
        self.config = config or FrameworkConfig.from_environment()
        self._initialized = False
        
        # Platform modules
        self._authenticator: Optional[EntraIDAuthenticator] = None
        self._rbac_engine: Optional[RBACEngine] = None
        self._telemetry_collector: Optional[TelemetryCollector] = None
        self._audit_logger: Optional[AuditLogger] = None
        self._error_handler: Optional[ErrorHandler] = None
        self._config_manager: Optional[ConfigManager] = None
        self._classification_engine: Optional[ClassificationEngine] = None
        self._tool_registry: Optional[ToolRegistry] = None
        self._fabric_connectors: Optional[FabricConnectors] = None
        self._tool_discovery: Optional[ToolDiscovery] = None
        
        # Initialize the framework
        self.initialize()
    
    def initialize(self):
        """Initialize all platform modules"""
        if self._initialized:
            return
        
        logger.info(f"Initializing MCP Platform Framework for domain: {self.config.domain}")
        
        try:
            # Set domain context for registration
            set_registration_domain_context(self.config.domain)
            
            # Initialize modules
            self._config_manager = get_config_manager()
            self._tool_registry = get_tool_registry()
            self._error_handler = get_error_handler()
            
            if self.config.enable_telemetry:
                self._telemetry_collector = get_telemetry_collector()
                logger.info("Telemetry collector initialized")
            
            if self.config.enable_audit:
                self._audit_logger = get_audit_logger()
                logger.info("Audit logger initialized")
            
            if self.config.enable_authentication:
                self._authenticator = get_authenticator()
                logger.info("Authenticator initialized")
            
            if self.config.enable_authorization:
                self._rbac_engine = get_rbac_engine()
                logger.info("RBAC engine initialized")
            
            if self.config.enable_classification:
                self._classification_engine = get_classification_engine()
                logger.info("Classification engine initialized")
            
            # Initialize Fabric connectors
            self._fabric_connectors = get_fabric_connectors()
            logger.info("Fabric connectors initialized")
            
            # Auto-discover tools if enabled
            if self.config.auto_discover_tools:
                self._initialize_tool_discovery()
            
            self._initialized = True
            logger.info("MCP Platform Framework initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing MCP Platform Framework: {str(e)}")
            raise
    
    def _initialize_tool_discovery(self):
        """Initialize tool discovery for the domain"""
        try:
            # Create tool discovery instance
            self._tool_discovery = ToolDiscovery(
                domain=self.config.domain,
                module_paths=self.config.tool_paths
            )
            
            # Discover and register tools from the domain package
            domain_package = f"{self.config.domain.replace('-', '_')}"
            
            try:
                count = self._tool_discovery.discover_and_register(domain_package)
                logger.info(f"Discovered and registered {count} tools from package: {domain_package}")
            except ImportError as e:
                logger.warning(f"Could not import domain package {domain_package}: {str(e)}")
                # Try to discover from current directory structure
                current_dir = Path.cwd()
                count = self._tool_discovery.discover_from_directory(str(current_dir))
                logger.info(f"Discovered and registered {count} tools from directory: {current_dir}")
                
        except Exception as e:
            logger.error(f"Error during tool discovery: {str(e)}")
    
    @property
    def auth(self) -> EntraIDAuthenticator:
        """Get the authentication module"""
        if self._authenticator is None:
            raise RuntimeError("Authenticator not initialized")
        return self._authenticator
    
    @property
    def rbac(self) -> RBACEngine:
        """Get the RBAC engine"""
        if self._rbac_engine is None:
            raise RuntimeError("RBAC engine not initialized")
        return self._rbac_engine
    
    @property
    def telemetry(self) -> TelemetryCollector:
        """Get the telemetry collector"""
        if self._telemetry_collector is None:
            raise RuntimeError("Telemetry collector not initialized")
        return self._telemetry_collector
    
    @property
    def audit(self) -> AuditLogger:
        """Get the audit logger"""
        if self._audit_logger is None:
            raise RuntimeError("Audit logger not initialized")
        return self._audit_logger
    
    @property
    def errors(self) -> ErrorHandler:
        """Get the error handler"""
        if self._error_handler is None:
            raise RuntimeError("Error handler not initialized")
        return self._error_handler
    
    @property
    def config(self) -> ConfigManager:
        """Get the configuration manager"""
        if self._config_manager is None:
            raise RuntimeError("Configuration manager not initialized")
        return self._config_manager
    
    @property
    def classification(self) -> ClassificationEngine:
        """Get the classification engine"""
        if self._classification_engine is None:
            raise RuntimeError("Classification engine not initialized")
        return self._classification_engine
    
    @property
    def registry(self) -> ToolRegistry:
        """Get the tool registry"""
        if self._tool_registry is None:
            raise RuntimeError("Tool registry not initialized")
        return self._tool_registry
    
    @property
    def fabric(self) -> FabricConnectors:
        """Get the Fabric connectors"""
        if self._fabric_connectors is None:
            raise RuntimeError("Fabric connectors not initialized")
        return self._fabric_connectors
    
    @property
    def discovery(self) -> Optional[ToolDiscovery]:
        """Get the tool discovery instance"""
        return self._tool_discovery
    
    def get_domain(self) -> str:
        """Get the current domain"""
        return self.config.domain
    
    def get_environment(self) -> str:
        """Get the current environment"""
        return self.config.environment
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.config.environment.upper() == "PROD"
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.config.environment.upper() == "DEV"
    
    def is_test(self) -> bool:
        """Check if running in test environment"""
        return self.config.environment.upper() == "TEST"
    
    def shutdown(self):
        """Shutdown the framework and cleanup resources"""
        logger.info("Shutting down MCP Platform Framework")
        
        # Clean up modules
        if self._telemetry_collector:
            self._telemetry_collector.flush()
        
        if self._audit_logger:
            self._audit_logger.flush()
        
        self._initialized = False
        logger.info("MCP Platform Framework shutdown complete")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.shutdown()


# Global framework instance
_framework: Optional[MCPFramework] = None


def get_framework() -> MCPFramework:
    """Get the global MCP Platform Framework instance"""
    global _framework
    if _framework is None:
        _framework = MCPFramework()
    return _framework


def reset_framework():
    """Reset the global MCP Platform Framework instance"""
    global _framework
    if _framework is not None:
        _framework.shutdown()
    _framework = None


def initialize_framework(domain: str, environment: str = "Dev", **kwargs) -> MCPFramework:
    """
    Initialize the MCP Platform Framework with specific configuration.
    
    Args:
        domain: Domain name
        environment: Environment (Dev, Test, Prod)
        **kwargs: Additional framework configuration
    
    Returns:
        Initialized MCPFramework instance
    """
    global _framework
    
    config = FrameworkConfig(
        domain=domain,
        environment=environment,
        **kwargs
    )
    
    _framework = MCPFramework(config)
    return _framework


# Convenience imports for direct access
from .auth import authenticated_tool, requires_permission, requires_role
from .classification import classification, classify_data, requires_classification
from .registration import tool, resource, query, action
from .connectivity import fabric, semantic_model
from .telemetry import track_tool_telemetry
from .audit import audit_tool_access, audit_data_access


__all__ = [
    'MCPFramework', 'FrameworkConfig',
    'get_framework', 'reset_framework', 'initialize_framework',
    # Platform modules
    'authenticated_tool', 'requires_permission', 'requires_role',
    'classification', 'classify_data', 'requires_classification',
    'tool', 'resource', 'query', 'action',
    'fabric', 'semantic_model',
    'track_tool_telemetry',
    'audit_tool_access', 'audit_data_access'
]