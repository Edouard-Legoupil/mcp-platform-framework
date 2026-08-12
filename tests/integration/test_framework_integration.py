"""Integration Tests for MCP Framework"""
import pytest
import os
import sys
from unittest.mock import patch, MagicMock
from platform.framework import (
    MCPFramework, 
    FrameworkConfig,
    get_framework, 
    reset_framework,
    initialize_framework
)
from platform.registration import get_tool_registry, set_domain_context
from platform.config import set_test_config


class TestFrameworkInitialization:
    """Tests for framework initialization"""
    
    def setup_method(self):
        """Setup test method"""
        reset_framework()
        # Set test configuration
        os.environ['MCP_DOMAIN'] = 'TestDomain'
        os.environ['MCP_ENVIRONMENT'] = 'Test'
    
    def teardown_method(self):
        """Teardown test method"""
        reset_framework()
        # Clean up environment variables
        for key in ['MCP_DOMAIN', 'MCP_ENVIRONMENT']:
            if key in os.environ:
                del os.environ[key]
    
    def test_framework_initialization_with_config(self):
        """Test framework initialization with explicit config"""
        config = FrameworkConfig(
            domain="TestDomain",
            environment="Test",
            enable_telemetry=True,
            enable_audit=True,
            enable_authentication=True,
            enable_authorization=True,
            enable_classification=True,
            auto_discover_tools=False
        )
        
        framework = MCPFramework(config)
        
        assert framework.get_domain() == "TestDomain"
        assert framework.get_environment() == "Test"
        assert framework.is_test() is True
        assert framework.is_development() is False
        assert framework.is_production() is False
    
    def test_framework_initialization_from_environment(self):
        """Test framework initialization from environment variables"""
        framework = MCPFramework()
        
        assert framework.get_domain() == "TestDomain"
        assert framework.get_environment() == "Test"
    
    def test_get_framework_singleton(self):
        """Test get_framework returns singleton"""
        framework1 = get_framework()
        framework2 = get_framework()
        
        assert framework1 is framework2
    
    def test_initialize_framework(self):
        """Test initialize_framework function"""
        framework = initialize_framework(
            domain="CustomDomain",
            environment="CustomEnv",
            enable_telemetry=False
        )
        
        assert framework.get_domain() == "CustomDomain"
        assert framework.get_environment() == "CustomEnv"
        assert framework.config.enable_telemetry is False
    
    def test_framework_context_manager(self):
        """Test framework as context manager"""
        with MCPFramework(FrameworkConfig(domain="Test", environment="Test")) as framework:
            assert framework.get_domain() == "Test"
            assert framework._initialized is True
        
        # After exiting context, framework should be shutdown
        assert framework._initialized is False


class TestFrameworkModules:
    """Tests for framework module access"""
    
    def setup_method(self):
        """Setup test method"""
        reset_framework()
        os.environ['MCP_DOMAIN'] = 'TestDomain'
        os.environ['MCP_ENVIRONMENT'] = 'Test'
    
    def teardown_method(self):
        """Teardown test method"""
        reset_framework()
        for key in ['MCP_DOMAIN', 'MCP_ENVIRONMENT']:
            if key in os.environ:
                del os.environ[key]
    
    def test_framework_auth_module(self):
        """Test framework auth module access"""
        framework = get_framework()
        
        # Auth module should be available
        assert hasattr(framework, 'auth')
        assert framework._authenticator is not None
    
    def test_framework_rbac_module(self):
        """Test framework RBAC module access"""
        framework = get_framework()
        
        # RBAC module should be available
        assert hasattr(framework, 'rbac')
        assert framework._rbac_engine is not None
    
    def test_framework_telemetry_module(self):
        """Test framework telemetry module access"""
        framework = get_framework()
        
        # Telemetry module should be available
        assert hasattr(framework, 'telemetry')
        assert framework._telemetry_collector is not None
    
    def test_framework_audit_module(self):
        """Test framework audit module access"""
        framework = get_framework()
        
        # Audit module should be available
        assert hasattr(framework, 'audit')
        assert framework._audit_logger is not None
    
    def test_framework_errors_module(self):
        """Test framework errors module access"""
        framework = get_framework()
        
        # Errors module should be available
        assert hasattr(framework, 'errors')
        assert framework._error_handler is not None
    
    def test_framework_config_module(self):
        """Test framework config module access"""
        framework = get_framework()
        
        # Config module should be available
        assert hasattr(framework, 'config')
        assert framework._config_manager is not None
    
    def test_framework_classification_module(self):
        """Test framework classification module access"""
        framework = get_framework()
        
        # Classification module should be available
        assert hasattr(framework, 'classification')
        assert framework._classification_engine is not None
    
    def test_framework_registry_module(self):
        """Test framework registry module access"""
        framework = get_framework()
        
        # Registry module should be available
        assert hasattr(framework, 'registry')
        assert framework._tool_registry is not None
    
    def test_framework_fabric_module(self):
        """Test framework fabric module access"""
        framework = get_framework()
        
        # Fabric module should be available
        assert hasattr(framework, 'fabric')
        assert framework._fabric_connectors is not None


class TestFrameworkToolDiscovery:
    """Tests for framework tool discovery"""
    
    def setup_method(self):
        """Setup test method"""
        reset_framework()
        set_domain_context("TestDomain")
        os.environ['MCP_DOMAIN'] = 'TestDomain'
        os.environ['MCP_ENVIRONMENT'] = 'Test'
    
    def teardown_method(self):
        """Teardown test method"""
        reset_framework()
        for key in ['MCP_DOMAIN', 'MCP_ENVIRONMENT']:
            if key in os.environ:
                del os.environ[key]
    
    def test_tool_discovery_disabled(self):
        """Test tool discovery when disabled"""
        config = FrameworkConfig(
            domain="TestDomain",
            environment="Test",
            auto_discover_tools=False
        )
        
        framework = MCPFramework(config)
        
        # Tool discovery should not be initialized
        assert framework._tool_discovery is None
    
    def test_tool_discovery_enabled(self):
        """Test tool discovery when enabled"""
        config = FrameworkConfig(
            domain="TestDomain",
            environment="Test",
            auto_discover_tools=True
        )
        
        framework = MCPFramework(config)
        
        # Tool discovery should be initialized
        assert framework._tool_discovery is not None
        assert framework.discovery is not None


class TestFrameworkShutdown:
    """Tests for framework shutdown"""
    
    def setup_method(self):
        """Setup test method"""
        reset_framework()
        os.environ['MCP_DOMAIN'] = 'TestDomain'
        os.environ['MCP_ENVIRONMENT'] = 'Test'
    
    def teardown_method(self):
        """Teardown test method"""
        reset_framework()
        for key in ['MCP_DOMAIN', 'MCP_ENVIRONMENT']:
            if key in os.environ:
                del os.environ[key]
    
    def test_framework_shutdown(self):
        """Test framework shutdown"""
        framework = get_framework()
        
        # Framework should be initialized
        assert framework._initialized is True
        
        # Shutdown the framework
        framework.shutdown()
        
        # Framework should no longer be initialized
        assert framework._initialized is False
    
    def test_reset_framework(self):
        """Test reset_framework function"""
        framework = get_framework()
        
        # Framework should be initialized
        assert framework._initialized is True
        
        # Reset the framework
        reset_framework()
        
        # Get a new framework instance
        new_framework = get_framework()
        
        # Should be a new instance
        assert new_framework is not framework


if __name__ == "__main__":
    pytest.main([__file__, "-v"])