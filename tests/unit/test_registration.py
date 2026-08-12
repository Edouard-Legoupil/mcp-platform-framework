"""Unit Tests for Registration Module"""
import pytest
from unittest.mock import patch, MagicMock
from platform.registration.models import (
    ToolType, 
    ToolStatus, 
    ParameterSchema,
    ToolMetadata,
    ToolRegistration,
    RegistrationRequest,
    RegistrationResult
)
from platform.registration.registry import ToolRegistry, set_tool_registry, get_tool_registry
from platform.registration.decorators import (
    tool, resource, query, action,
    set_domain_context, get_domain_context
)
from platform.registration.discovery import ToolDiscovery


class TestToolModels:
    """Tests for Tool models"""
    
    def test_tool_type_enum(self):
        """Test ToolType enum"""
        assert ToolType.FUNCTION == "function"
        assert ToolType.QUERY == "query"
        assert ToolType.ACTION == "action"
        assert ToolType.RESOURCE == "resource"
    
    def test_tool_status_enum(self):
        """Test ToolStatus enum"""
        assert ToolStatus.ACTIVE == "active"
        assert ToolStatus.INACTIVE == "inactive"
        assert ToolStatus.DEPRECATED == "deprecated"
        assert ToolStatus.MAINTENANCE == "maintenance"
    
    def test_parameter_schema_creation(self):
        """Test ParameterSchema creation"""
        param = ParameterSchema(
            name="user_id",
            type="string",
            description="User ID parameter",
            required=True,
            default="default_value"
        )
        
        assert param.name == "user_id"
        assert param.type == "string"
        assert param.description == "User ID parameter"
        assert param.required is True
        assert param.default == "default_value"
    
    def test_tool_metadata_creation(self):
        """Test ToolMetadata creation"""
        metadata = ToolMetadata(
            name="GetDonorData",
            description="Get donor information",
            tool_type=ToolType.FUNCTION,
            domain="DonorManagement",
            version="1.0.0",
            status=ToolStatus.ACTIVE,
            classification="CONFIDENTIAL",
            requires_authentication=True,
            requires_authorization=True,
            timeout_seconds=30,
            max_retries=3,
            rate_limit="100/hour",
            owner="DonorManagement",
            maintainer="team@example.com",
            sla="Gold",
            parameters={"user_id": ParameterSchema(name="user_id", type="string")},
            returns="dict",
            tags=["donor", "data"],
            categories=["Data Access"]
        )
        
        assert metadata.name == "GetDonorData"
        assert metadata.description == "Get donor information"
        assert metadata.tool_type == ToolType.FUNCTION
        assert metadata.domain == "DonorManagement"
        assert metadata.classification == "CONFIDENTIAL"
        assert metadata.requires_authentication is True
        assert len(metadata.parameters) == 1
    
    def test_tool_registration_creation(self):
        """Test ToolRegistration creation"""
        metadata = ToolMetadata(name="TestTool", description="Test")
        registration = ToolRegistration(
            tool_id="12345",
            metadata=metadata,
            endpoint="/api/TestTool",
            handler="module.function",
            is_loaded=True,
            load_error=None
        )
        
        assert registration.tool_id == "12345"
        assert registration.metadata == metadata
        assert registration.endpoint == "/api/TestTool"
        assert registration.handler == "module.function"
        assert registration.is_loaded is True
    
    def test_registration_request_creation(self):
        """Test RegistrationRequest creation"""
        metadata = ToolMetadata(name="TestTool", description="Test")
        request = RegistrationRequest(
            metadata=metadata,
            endpoint="/api/TestTool",
            handler="module.function"
        )
        
        assert request.metadata == metadata
        assert request.endpoint == "/api/TestTool"
        assert request.handler == "module.function"
    
    def test_registration_result_creation(self):
        """Test RegistrationResult creation"""
        result = RegistrationResult(
            success=True,
            tool_id="12345",
            message="Tool registered successfully",
            error=None
        )
        
        assert result.success is True
        assert result.tool_id == "12345"
        assert result.message == "Tool registered successfully"
        assert result.error is None


class TestToolRegistry:
    """Tests for ToolRegistry"""
    
    def setup_method(self):
        """Setup test method"""
        # Reset the global registry for each test
        set_tool_registry(ToolRegistry())
    
    def test_tool_registry_initialization(self):
        """Test ToolRegistry initialization"""
        registry = ToolRegistry()
        
        assert len(registry._tools) == 0
        assert len(registry._name_index) == 0
        assert len(registry._domain_index) == 0
    
    def test_register_tool(self):
        """Test registering a tool"""
        registry = get_tool_registry()
        
        metadata = ToolMetadata(
            name="TestTool",
            description="Test tool",
            domain="TestDomain"
        )
        request = RegistrationRequest(metadata=metadata)
        
        result = registry.register_tool(request)
        
        assert result.success is True
        assert result.tool_id is not None
        assert len(registry.get_all_tools()) == 1
    
    def test_get_tool_by_name(self):
        """Test getting tool by name"""
        registry = get_tool_registry()
        
        metadata = ToolMetadata(
            name="TestTool",
            description="Test tool",
            domain="TestDomain"
        )
        request = RegistrationRequest(metadata=metadata)
        registry.register_tool(request)
        
        tool = registry.get_tool_by_name("TestTool")
        
        assert tool is not None
        assert tool.metadata.name == "TestTool"
    
    def test_get_tools_by_domain(self):
        """Test getting tools by domain"""
        registry = get_tool_registry()
        
        # Register tools in different domains
        metadata1 = ToolMetadata(name="Tool1", description="Tool 1", domain="Domain1")
        metadata2 = ToolMetadata(name="Tool2", description="Tool 2", domain="Domain2")
        metadata3 = ToolMetadata(name="Tool3", description="Tool 3", domain="Domain1")
        
        registry.register_tool(RegistrationRequest(metadata=metadata1))
        registry.register_tool(RegistrationRequest(metadata=metadata2))
        registry.register_tool(RegistrationRequest(metadata=metadata3))
        
        domain1_tools = registry.get_tools_by_domain("Domain1")
        
        assert len(domain1_tools) == 2
        tool_names = [tool.metadata.name for tool in domain1_tools]
        assert "Tool1" in tool_names
        assert "Tool3" in tool_names
    
    def test_unregister_tool(self):
        """Test unregistering a tool"""
        registry = get_tool_registry()
        
        metadata = ToolMetadata(name="TestTool", description="Test tool", domain="TestDomain")
        request = RegistrationRequest(metadata=metadata)
        result = registry.register_tool(request)
        
        # Unregister the tool
        success = registry.unregister_tool(result.tool_id)
        
        assert success is True
        assert registry.get_tool(result.tool_id) is None
        assert registry.get_tool_by_name("TestTool") is None
    
    def test_update_tool_status(self):
        """Test updating tool status"""
        registry = get_tool_registry()
        
        metadata = ToolMetadata(
            name="TestTool",
            description="Test tool",
            domain="TestDomain",
            status=ToolStatus.ACTIVE
        )
        request = RegistrationRequest(metadata=metadata)
        result = registry.register_tool(request)
        
        # Update status
        success = registry.update_tool_status(result.tool_id, ToolStatus.DEPRECATED)
        
        assert success is True
        tool = registry.get_tool(result.tool_id)
        assert tool.metadata.status == ToolStatus.DEPRECATED
    
    def test_increment_usage(self):
        """Test incrementing tool usage"""
        registry = get_tool_registry()
        
        metadata = ToolMetadata(name="TestTool", description="Test tool", domain="TestDomain")
        request = RegistrationRequest(metadata=metadata)
        result = registry.register_tool(request)
        
        # Increment usage
        registry.increment_usage(result.tool_id, success=True)
        registry.increment_usage(result.tool_id, success=True)
        registry.increment_usage(result.tool_id, success=False)
        
        tool = registry.get_tool(result.tool_id)
        assert tool.metadata.usage_count == 3
        assert tool.metadata.error_count == 1


class TestDomainContext:
    """Tests for domain context"""
    
    def test_set_and_get_domain_context(self):
        """Test setting and getting domain context"""
        set_domain_context("TestDomain")
        
        domain = get_domain_context()
        assert domain == "TestDomain"
    
    def test_get_domain_context_not_set(self):
        """Test getting domain context when not set"""
        set_domain_context("TestDomain")
        # Reset by setting to None
        set_domain_context(None)
        
        with pytest.raises(ValueError):
            get_domain_context()


class TestDecorators:
    """Tests for registration decorators"""
    
    def setup_method(self):
        """Setup test method"""
        set_domain_context("TestDomain")
    
    def test_tool_decorator(self):
        """Test @tool decorator"""
        @tool(description="Test tool description")
        def test_function():
            return "success"
        
        assert hasattr(test_function, '_tool_metadata')
        assert test_function._tool_metadata.name == "test_function"
        assert test_function._tool_metadata.description == "Test tool description"
        assert test_function._tool_metadata.domain == "TestDomain"
        assert test_function._tool_metadata.tool_type == ToolType.FUNCTION
    
    def test_resource_decorator(self):
        """Test @resource decorator"""
        @resource(description="Test resource")
        def test_resource_function():
            return "success"
        
        assert hasattr(test_resource_function, '_tool_metadata')
        assert test_resource_function._tool_metadata.tool_type == ToolType.RESOURCE
    
    def test_query_decorator(self):
        """Test @query decorator"""
        @query(description="Test query")
        def test_query_function():
            return "success"
        
        assert hasattr(test_query_function, '_tool_metadata')
        assert test_query_function._tool_metadata.tool_type == ToolType.QUERY
    
    def test_action_decorator(self):
        """Test @action decorator"""
        @action(description="Test action")
        def test_action_function():
            return "success"
        
        assert hasattr(test_action_function, '_tool_metadata')
        assert test_action_function._tool_metadata.tool_type == ToolType.ACTION


class TestToolDiscovery:
    """Tests for ToolDiscovery"""
    
    def test_tool_discovery_initialization(self):
        """Test ToolDiscovery initialization"""
        discovery = ToolDiscovery(domain="TestDomain")
        
        assert discovery.domain == "TestDomain"
        assert len(discovery._discovered_tools) == 0
    
    def test_discover_from_directory(self):
        """Test discovering tools from directory"""
        set_domain_context("TestDomain")
        discovery = ToolDiscovery(domain="TestDomain")
        
        # This would require actual Python files to scan
        # For now, just test the method exists
        assert hasattr(discovery, 'discover_from_directory')
        assert hasattr(discovery, 'discover_and_register')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])