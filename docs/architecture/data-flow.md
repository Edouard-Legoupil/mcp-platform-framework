# 🔄 Data Flow Architecture

This document describes how data flows through the MCP Platform Framework, from request ingestion to response generation, including all cross-cutting concerns and integration points.

## 🏭 Overview

The MCP Platform Framework follows a **pipeline architecture** where each request passes through a series of processing stages. Each stage can enrich, validate, or transform the request before it reaches the domain logic.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA FLOW PIPELINE                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  REQUEST → [Ingress] → [Auth] → [AuthZ] → [Classification] → [Telemetry]│
│                   → [Domain Logic] → [Fabric] → [Audit] → RESPONSE      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 📥 Ingress Layer

### Function App Entry Point

All requests enter through the Azure Function App, which serves as the MCP server endpoint.

```python
# main.py - Function App Entry Point
import azure.functions as func
from platform.framework import MCPFramework
from platform.config import config

# Initialize the framework
framework = MCPFramework(
    domain=config.domain,
    environment=config.environment
)

# MCP Protocol Handler
@app.route(route="mcp", methods=["POST"])
def mcp_handler(req: func.HttpRequest) -> func.HttpResponse:
    """
    Main MCP protocol handler.
    All MCP requests are routed through this endpoint.
    """
    try:
        # Parse MCP request
        mcp_request = MCPRequest.from_http_request(req)
        
        # Process through framework pipeline
        response = framework.process_request(mcp_request)
        
        # Return HTTP response
        return response.to_http_response()
        
    except Exception as e:
        # Error handling
        error_response = framework.handle_error(e)
        return error_response.to_http_response()
```

### Request Parsing

```python
# MCP Request Structure
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "GetDonorPortfolioHealth",
    "arguments": {
      "year": 2026,
      "quarter": "Q1"
    }
  }
}
```

### Request Context Creation

```python
# Context object created for each request
request_context = RequestContext(
    request_id=generate_uuid(),
    correlation_id=get_correlation_id(),
    timestamp=datetime.utcnow(),
    environment=config.environment,
    domain=config.domain,
    workspace=get_workspace()
)
```

## 🔐 Authentication Stage

### JWT Token Validation

```python
# Authentication Pipeline
class AuthenticationStage:
    async def process(self, request: MCPRequest, context: RequestContext):
        # Extract token from Authorization header
        token = extract_bearer_token(request.headers)
        
        if not token:
            raise AuthenticationError(
                error_code="AUTH-001",
                message="Missing authentication token"
            )
        
        # Validate JWT token
        claims = jwt_validator.validate(token)
        
        # Extract caller identity
        caller = CallerIdentity(
            identity=claims.get("sub"),
            name=claims.get("name"),
            email=claims.get("email"),
            roles=claims.get("roles", []),
            permissions=claims.get("permissions", []),
            authentication_method=claims.get("amr", [])
        )
        
        # Attach to context
        context.caller = caller
        context.is_authenticated = True
        
        return request, context
```

### Entra ID Integration

```python
# Entra ID Configuration
class EntraIDConfig:
    tenant_id = config.azure.tenant_id
    client_id = config.azure.client_id
    audience = config.azure.audience
    issuer = f"https://login.microsoftonline.com/{tenant_id}/v2.0"

# Token Validation
class JWTValidator:
    def __init__(self, config: EntraIDConfig):
        self.config = config
        self.jwks_client = PyJWKClient(
            f"{config.issuer}/discovery/v2.0/keys"
        )
    
    def validate(self, token: str) -> dict:
        # Get signing key
        signing_key = self.jwks_client.get_signing_key_from_jwt(token)
        
        # Decode and verify
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=self.config.audience,
            issuer=self.config.issuer
        )
        
        # Additional validation
        self._validate_claims(claims)
        
        return claims
```

### Managed Identity Support

```python
# Managed Identity Token Acquisition
class ManagedIdentityAuth:
    @staticmethod
    async def get_access_token(resource: str) -> str:
        """
        Get access token using Managed Identity.
        Used for service-to-service authentication.
        """
        token_url = f"http://169.254.169.254/metadata/identity/oauth2/token"
        params = {
            "api-version": "2021-02-01",
            "resource": resource
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(token_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["access_token"]
                else:
                    raise AuthenticationError(
                        error_code="AUTH-002",
                        message="Failed to acquire Managed Identity token"
                    )
```

## 🛡️ Authorization Stage

### Permission Checking

```python
# Authorization Pipeline
class AuthorizationStage:
    async def process(self, request: MCPRequest, context: RequestContext):
        if not context.is_authenticated:
            raise AuthorizationError(
                error_code="AUTHZ-001",
                message="Request not authenticated"
            )
        
        # Get tool metadata
        tool_metadata = tool_registry.get_tool(request.params.name)
        
        # Check required permissions
        required_permissions = tool_metadata.get("required_permissions", [])
        
        for permission in required_permissions:
            if not context.caller.has_permission(permission):
                audit_log.log_authorization_failure(
                    caller=context.caller.identity,
                    tool=request.params.name,
                    required_permission=permission
                )
                raise AuthorizationError(
                    error_code="AUTHZ-002",
                    message=f"Permission denied: {permission} required",
                    details={"required_permission": permission}
                )
        
        # Check role requirements
        required_roles = tool_metadata.get("required_roles", [])
        for role in required_roles:
            if not context.caller.has_role(role):
                raise AuthorizationError(
                    error_code="AUTHZ-003",
                    message=f"Role required: {role}",
                    details={"required_role": role}
                )
        
        return request, context
```

### RBAC Engine

```python
# Role-Based Access Control
class RBACEngine:
    def __init__(self, policy_store: PolicyStore):
        self.policy_store = policy_store
        self.cache = TTLCache(maxsize=1000, ttl=300)
    
    def check_permission(self, caller: CallerIdentity, permission: str) -> bool:
        cache_key = f"{caller.identity}:{permission}"
        
        # Check cache
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Get caller's roles and permissions
        caller_permissions = set(caller.permissions)
        caller_roles = set(caller.roles)
        
        # Check direct permission
        if permission in caller_permissions:
            self.cache[cache_key] = True
            return True
        
        # Check role-based permissions
        for role in caller_roles:
            role_permissions = self.policy_store.get_role_permissions(role)
            if permission in role_permissions:
                self.cache[cache_key] = True
                return True
        
        # Check permission inheritance
        if self._check_permission_inheritance(permission, caller_permissions):
            self.cache[cache_key] = True
            return True
        
        self.cache[cache_key] = False
        return False
```

## 🏷️ Classification Stage

### Classification Checking

```python
# Classification Pipeline
class ClassificationStage:
    async def process(self, request: MCPRequest, context: RequestContext):
        # Get tool classification
        tool_metadata = tool_registry.get_tool(request.params.name)
        classification = tool_metadata.get("classification", "PUBLIC")
        
        # Get caller's maximum allowed classification
        max_classification = context.caller.get_max_classification()
        
        # Check if caller can access this classification
        if not can_access_classification(max_classification, classification):
            raise ClassificationError(
                error_code="CLASS-001",
                message=f"Access denied: {classification} classification required",
                details={
                    "required_classification": classification,
                    "caller_classification": max_classification
                }
            )
        
        # Set current classification in context
        context.current_classification = classification
        
        return request, context

# Classification Hierarchy
def can_access_classification(user_level: str, required_level: str) -> bool:
    hierarchy = {
        "PUBLIC": 0,
        "INTERNAL": 1,
        "CONFIDENTIAL": 2,
        "STRICTLY CONFIDENTIAL": 3
    }
    return hierarchy.get(user_level, 0) >= hierarchy.get(required_level, 0)
```

## 📊 Telemetry Stage

### Automatic Instrumentation

```python
# Telemetry Pipeline
class TelemetryStage:
    async def process(self, request: MCPRequest, context: RequestContext):
        # Start timing
        context.start_time = time.time()
        
        # Initialize telemetry data
        context.telemetry = TelemetryData(
            tool=request.params.name,
            domain=context.domain,
            requester_identity=context.caller.identity if context.caller else None,
            requester_roles=context.caller.roles if context.caller else [],
            requester_permissions=context.caller.permissions if context.caller else [],
            environment=context.environment,
            workspace=context.workspace,
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            timestamp=context.timestamp
        )
        
        return request, context

    async def complete(self, request: MCPRequest, context: RequestContext, 
                      response: MCPResponse, error: Exception = None):
        # Calculate duration
        duration_ms = (time.time() - context.start_time) * 1000
        
        # Set telemetry data
        context.telemetry.duration_ms = duration_ms
        context.telemetry.status = "Success" if not error else "Error"
        context.telemetry.timestamp = datetime.utcnow()
        
        # Capture token usage if available
        if hasattr(response, 'token_usage'):
            context.telemetry.token_usage = response.token_usage
        
        # Send to telemetry service
        await telemetry_service.send(context.telemetry)
        
        # Also log to Application Insights
        if config.telemetry.application_insights_enabled:
            await app_insights.track_tool_call(context.telemetry)
```

### Telemetry Data Structure

```python
@dataclass
class TelemetryData:
    tool: str
    domain: str
    requester_identity: Optional[str]
    requester_roles: List[str]
    requester_permissions: List[str]
    environment: str
    workspace: str
    request_id: str
    correlation_id: str
    timestamp: datetime
    duration_ms: float = 0.0
    status: str = "Unknown"
    token_usage: Optional[TokenUsage] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "tool": self.tool,
            "domain": self.domain,
            "duration_ms": round(self.duration_ms, 2),
            "status": self.status,
            "requester": {
                "identity": self.requester_identity,
                "roles": self.requester_roles,
                "permissions": self.requester_permissions
            },
            "environment": self.environment,
            "workspace": self.workspace,
            "timestamp": self.timestamp.isoformat() + "Z",
            "request_id": self.request_id,
            "correlation_id": self.correlation_id,
            "token_usage": self.token_usage.to_dict() if self.token_usage else None,
            "error": {
                "code": self.error_code,
                "message": self.error_message
            } if self.error_code else None
        }
```

## 🎯 Domain Logic Stage

### Tool Discovery and Execution

```python
# Domain Logic Pipeline
class DomainLogicStage:
    async def process(self, request: MCPRequest, context: RequestContext):
        # Get tool from registry
        tool_name = request.params.name
        tool_func = tool_registry.get_tool_function(tool_name)
        
        if not tool_func:
            raise ToolNotFoundError(
                error_code="TOOL-001",
                message=f"Tool not found: {tool_name}"
            )
        
        # Extract arguments
        arguments = request.params.get("arguments", {})
        
        # Prepare context for tool execution
        execution_context = ToolExecutionContext(
            request_context=context,
            tool_name=tool_name,
            arguments=arguments,
            semantic_model_factory=context.semantic_model_factory,
            fabric_connector=context.fabric_connector,
            keyvault=context.keyvault
        )
        
        # Execute tool with error handling
        try:
            result = await self._execute_tool(tool_func, arguments, execution_context)
            
            # Create success response
            response = MCPResponse(
                id=request.id,
                result=result,
                tool=tool_name,
                status="success"
            )
            
            return response
            
        except Exception as e:
            # Handle tool execution errors
            error_response = self._handle_tool_error(e, tool_name, context)
            raise error_response

    async def _execute_tool(self, tool_func, arguments, context):
        # Apply tool decorators (if not already applied)
        wrapped_tool = self._apply_decorators(tool_func)
        
        # Execute with context
        return await wrapped_tool(**arguments, _context=context)
```

### Tool Decorator Application

```python
# Decorator Application
class ToolDecoratorApplier:
    def apply_decorators(self, tool_func):
        # Get tool metadata
        tool_metadata = getattr(tool_func, "_tool_metadata", {})
        
        # Apply decorators based on metadata
        decorated_func = tool_func
        
        # Apply classification decorator
        classification = tool_metadata.get("classification", "PUBLIC")
        if classification != "PUBLIC":
            decorated_func = classification_decorator(classification)(decorated_func)
        
        # Apply permission decorators
        required_permissions = tool_metadata.get("required_permissions", [])
        for permission in required_permissions:
            decorated_func = requires_permission(permission)(decorated_func)
        
        # Apply audit decorator for sensitive operations
        if tool_metadata.get("audit", False):
            decorated_func = audit_log.sensitive_operation(decorated_func)
        
        # Apply telemetry decorator
        decorated_func = telemetry.capture_tool_metrics(decorated_func)
        
        return decorated_func
```

## 🌐 Fabric Integration Stage

### Semantic Model Access

```python
# Semantic Model Execution
class SemanticModelExecutor:
    async def execute_query(self, model_name: str, query: str, 
                           parameters: dict = None, context: RequestContext = None):
        
        # Get semantic model
        semantic_model = semantic_model_factory.get_model(model_name)
        
        # Validate query
        self._validate_query(query, semantic_model)
        
        # Apply classification checks
        model_classification = semantic_model.classification
        if context and context.current_classification:
            # Ensure query classification doesn't exceed context classification
            query_classification = self._determine_query_classification(query)
            if not can_access_classification(context.current_classification, query_classification):
                raise ClassificationError(
                    error_code="CLASS-002",
                    message=f"Query classification {query_classification} exceeds context classification {context.current_classification}"
                )
        
        # Execute query
        try:
            result = await semantic_model.execute(query, parameters)
            
            # Log query execution
            if context:
                logger.info(
                    f"Semantic model query executed",
                    extra={
                        "model": model_name,
                        "query": query[:100] + "..." if len(query) > 100 else query,
                        "duration_ms": result.execution_time_ms,
                        "rows_returned": len(result.data)
                    }
                )
            
            return result
            
        except Exception as e:
            # Handle semantic model errors
            raise SemanticModelError(
                error_code="SEM-001",
                message=f"Semantic model execution failed: {str(e)}",
                details={"model": model_name, "query": query}
            )
```

### Warehouse and Lakehouse Access

```python
# Fabric Data Access
class FabricDataAccessor:
    async def query_warehouse(self, sql: str, warehouse_name: str = "GoldLayer",
                              context: RequestContext = None):
        """
        Execute SQL query against Fabric warehouse.
        Domains should prefer semantic models over direct warehouse access.
        """
        
        # Get warehouse connector
        warehouse = fabric_connector.get_warehouse(warehouse_name)
        
        # Validate access
        if not self._can_access_warehouse(warehouse_name, context):
            raise AccessDeniedError(
                error_code="FABRIC-001",
                message=f"Access denied to warehouse: {warehouse_name}"
            )
        
        # Execute query
        try:
            result = await warehouse.query(sql)
            return result
        except Exception as e:
            raise WarehouseError(
                error_code="FABRIC-002",
                message=f"Warehouse query failed: {str(e)}",
                details={"warehouse": warehouse_name, "sql": sql[:100]}
            )
    
    async def query_lakehouse(self, table: str, operation: str, 
                              parameters: dict = None, lakehouse_name: str = "Gold"):
        """
        Execute operation against Fabric lakehouse.
        """
        lakehouse = fabric_connector.get_lakehouse(lakehouse_name)
        
        try:
            if operation == "read":
                return await lakehouse.read_table(table, **parameters)
            elif operation == "write":
                return await lakehouse.write_table(table, parameters["data"])
            elif operation == "delete":
                return await lakehouse.delete_table(table, **parameters)
            else:
                raise ValueError(f"Unknown operation: {operation}")
        except Exception as e:
            raise LakehouseError(
                error_code="FABRIC-003",
                message=f"Lakehouse operation failed: {str(e)}",
                details={"lakehouse": lakehouse_name, "table": table, "operation": operation}
            )
```

## 📝 Audit Logging Stage

### Sensitive Operation Auditing

```python
# Audit Logging Pipeline
class AuditLoggingStage:
    async def process(self, request: MCPRequest, context: RequestContext, 
                      response: MCPResponse = None, error: Exception = None):
        
        # Check if this tool requires auditing
        tool_metadata = tool_registry.get_tool(request.params.name)
        requires_audit = tool_metadata.get("audit", False)
        
        # Also audit based on classification
        classification = tool_metadata.get("classification", "PUBLIC")
        if classification in ["CONFIDENTIAL", "STRICTLY CONFIDENTIAL"]:
            requires_audit = True
        
        if requires_audit:
            # Create audit record
            audit_record = AuditRecord(
                audit_id=generate_audit_id(),
                user=context.caller.identity if context.caller else "system",
                tool=request.params.name,
                time=datetime.utcnow(),
                parameters=request.params.get("arguments", {}),
                result="Success" if not error else "Failure",
                classification=classification,
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                session_id=context.request_id,
                error_code=error.error_code if error else None,
                error_message=str(error) if error else None
            )
            
            # Store audit record
            await audit_store.store(audit_record)
            
            # Send to SIEM if configured
            if config.audit.siem_integration_enabled:
                await siem_client.send_audit_record(audit_record)
        
        return response
```

### Audit Record Storage

```python
# Immutable Audit Storage
class AuditStore:
    def __init__(self, storage_account: str, container: str = "audit-logs"):
        self.storage_account = storage_account
        self.container = container
        self.blob_service = BlobServiceClient.from_connection_string(
            keyvault.get_secret("audit-storage-connection-string")
        )
    
    async def store(self, audit_record: AuditRecord):
        # Create blob name with timestamp
        blob_name = f"audit/{audit_record.time.strftime('%Y/%m/%d')}/{audit_record.audit_id}.json"
        
        # Convert to JSON
        json_data = audit_record.to_json()
        
        # Upload to blob storage
        blob_client = self.blob_service.get_blob_client(
            container=self.container,
            blob=blob_name
        )
        
        # Set immutable storage properties
        blob_properties = BlobProperties(
            content_type="application/json",
            content_disposition="attachment"
        )
        
        # Upload with write-once properties
        await blob_client.upload_blob(
            json_data,
            blob_properties=blob_properties,
            overwrite=False  # Ensure immutability
        )
        
        # Set blob immutability policy
        await blob_client.set_blob_immutability_policy(
            mode="unlocked",  # Will be locked after retention period
            retention_interval_days=3650  # 10 years
        )
```

## ❌ Error Handling Flow

### Error Classification and Handling

```python
# Error Handling Pipeline
class ErrorHandlingStage:
    async def handle_error(self, error: Exception, request: MCPRequest, 
                          context: RequestContext) -> MCPResponse:
        
        # Classify error
        if isinstance(error, AuthenticationError):
            error_type = "authentication"
            status_code = 401
        elif isinstance(error, AuthorizationError):
            error_type = "authorization"
            status_code = 403
        elif isinstance(error, ClassificationError):
            error_type = "classification"
            status_code = 403
        elif isinstance(error, ToolNotFoundError):
            error_type = "not_found"
            status_code = 404
        elif isinstance(error, ValidationError):
            error_type = "validation"
            status_code = 400
        else:
            error_type = "internal"
            status_code = 500
        
        # Create standardized error response
        error_response = MCPResponse(
            id=request.id if hasattr(request, 'id') else None,
            error={
                "code": getattr(error, 'error_code', 'INTERNAL-001'),
                "message": str(error),
                "type": error_type,
                "category": getattr(error, 'category', 'Internal'),
                "details": getattr(error, 'details', {}),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "request_id": context.request_id,
                "correlation_id": context.correlation_id
            },
            status="error"
        )
        
        # Log error
        logger.error(
            f"Error processing request: {error}",
            extra={
                "error_code": getattr(error, 'error_code', 'INTERNAL-001'),
                "error_type": error_type,
                "request_id": context.request_id,
                "tool": request.params.name if hasattr(request, 'params') else None,
                "user": context.caller.identity if context.caller else None
            }
        )
        
        # Update telemetry with error information
        if hasattr(context, 'telemetry'):
            context.telemetry.status = "Error"
            context.telemetry.error_code = getattr(error, 'error_code', 'INTERNAL-001')
            context.telemetry.error_message = str(error)
        
        return error_response
```

## 🔄 Complete Data Flow Example

### End-to-End Request Processing

```python
# Complete flow for a tool call
async def process_tool_call(request: MCPRequest) -> MCPResponse:
    # 1. Create request context
    context = create_request_context(request)
    
    try:
        # 2. Authentication
        request, context = await authentication_stage.process(request, context)
        
        # 3. Authorization
        request, context = await authorization_stage.process(request, context)
        
        # 4. Classification
        request, context = await classification_stage.process(request, context)
        
        # 5. Telemetry start
        request, context = await telemetry_stage.process(request, context)
        
        # 6. Domain logic execution
        response = await domain_logic_stage.process(request, context)
        
        # 7. Audit logging (if required)
        response = await audit_stage.process(request, context, response)
        
        # 8. Telemetry completion
        await telemetry_stage.complete(request, context, response)
        
        return response
        
    except Exception as e:
        # Error handling
        error_response = await error_handling_stage.handle_error(e, request, context)
        
        # Telemetry completion for errors
        await telemetry_stage.complete(request, context, None, e)
        
        # Audit logging for errors
        await audit_stage.process(request, context, None, e)
        
        return error_response
```

### Visual Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    COMPLETE DATA FLOW DIAGRAM                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐              │
│  │   HTTP      │────▶│  MCP Request │────▶│  Request     │              │
│  │  Request    │     │   Parsing    │     │  Context     │              │
│  └─────────────┘     └─────────────┘     └──────────┬────┘              │
│                                                    │                    │
│                                                    ▼                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    PIPELINE STAGES                            │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │   │
│  │  │ Authentication│─▶│ Authorization │─▶│Classification│            │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘            │   │
│  │       │               │               │                        │   │
│  │       ▼               ▼               ▼                        │   │
│  │  ┌─────────────────────────────────────────────────────┐    │   │
│  │  │              CONTEXT ENRICHMENT                        │    │   │
│  │  │  - Caller identity added by Authentication             │    │   │
│  │  │  - Permissions validated by Authorization              │    │   │
│  │  │  - Classification level set by Classification           │    │   │
│  │  └─────────────────────────────────────────────────────┘    │   │
│  │                                                        │            │   │
│  │                                                        ▼            │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │   │
│  │  │  Telemetry  │─▶│ Domain Logic │─▶│   Fabric    │            │   │
│  │  │   Start     │  │  Execution   │  │ Integration │            │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘            │   │
│  │                                                        │            │   │
│  │                                                        ▼            │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │   │
│  │  │   Audit     │◀─│  Telemetry  │◀─│   Response   │            │   │
│  │  │  Logging    │  │  Completion │  │  Generation  │            │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘            │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                    │                    │
│                                                    ▼                    │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐              │
│  │   HTTP      │◀────│  MCP        │◀────│  Error       │              │
│  │  Response   │     │  Response    │     │  Handling    │              │
│  └─────────────┘     └─────────────┘     └─────────────┘              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 🎯 Performance Considerations

### Caching Strategy

```python
# Multi-level caching
class CachingStrategy:
    # Level 1: In-memory cache for frequently accessed data
    tool_registry_cache = TTLCache(maxsize=1000, ttl=60)
    
    # Level 2: Distributed cache for shared data
    redis_cache = RedisCache(host=config.cache.host, port=config.cache.port)
    
    # Level 3: Application Insights for monitoring
    app_insights_cache = AppInsightsCache()
    
    @classmethod
    async def get_tool(cls, tool_name: str):
        # Check L1 cache
        if tool_name in cls.tool_registry_cache:
            return cls.tool_registry_cache[tool_name]
        
        # Check L2 cache
        cached_tool = await cls.redis_cache.get(f"tool:{tool_name}")
        if cached_tool:
            cls.tool_registry_cache[tool_name] = cached_tool
            return cached_tool
        
        # Get from registry
        tool = await tool_registry.get_tool(tool_name)
        
        # Cache at both levels
        cls.tool_registry_cache[tool_name] = tool
        await cls.redis_cache.set(f"tool:{tool_name}", tool, ttl=300)
        
        return tool
```

### Connection Pooling

```python
# Connection pooling for Fabric connectors
class FabricConnectionPool:
    def __init__(self, max_connections: int = 10):
        self.pool = Queue(maxsize=max_connections)
        self.connections = {}
    
    async def get_connection(self, connector_type: str, **kwargs):
        key = f"{connector_type}:{frozenset(kwargs.items())}"
        
        if key in self.connections:
            return self.connections[key]
        
        # Create new connection
        if connector_type == "semantic_model":
            connection = SemanticModelConnection(**kwargs)
        elif connector_type == "warehouse":
            connection = WarehouseConnection(**kwargs)
        elif connector_type == "lakehouse":
            connection = LakehouseConnection(**kwargs)
        
        self.connections[key] = connection
        return connection
    
    async def close_all(self):
        for connection in self.connections.values():
            await connection.close()
        self.connections.clear()
```

## 🔒 Security Considerations

### Data Flow Security

1. **Transport Security**: All communications use HTTPS/TLS 1.2+
2. **Token Security**: JWT tokens are validated and have short expiration
3. **Data Encryption**: Sensitive data is encrypted at rest and in transit
4. **Audit Trail**: All sensitive operations are logged immutably
5. **Input Validation**: All inputs are validated before processing
6. **Output Sanitization**: Outputs are sanitized to prevent data leakage

### Security Checkpoints

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SECURITY CHECKPOINTS                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. INGRESS SECURITY                                                │
│     ├── TLS validation                                             │
│     ├── Rate limiting                                               │
│     ├── IP allowlisting (optional)                                  │
│     └── Request size limits                                         │
│                                                                     │
│  2. AUTHENTICATION SECURITY                                         │
│     ├── JWT signature validation                                    │
│     ├── Token expiration check                                      │
│     ├── Audience validation                                         │
│     ├── Issuer validation                                           │
│     └── Claims validation                                           │
│                                                                     │
│  3. AUTHORIZATION SECURITY                                          │
│     ├── Permission validation                                       │
│     ├── Role validation                                             │
│     ├── Resource access checks                                      │
│     └── Least privilege enforcement                                 │
│                                                                     │
│  4. CLASSIFICATION SECURITY                                         │
│     ├── Data classification validation                              │
│     ├── Access level checks                                         │
│     └── Governance policy enforcement                               │
│                                                                     │
│  5. DATA ACCESS SECURITY                                            │
│     ├── Semantic model access controls                              │
│     ├── Warehouse access validation                                  │
│     ├── Lakehouse access validation                                  │
│     └── Query validation                                            │
│                                                                     │
│  6. EGRESS SECURITY                                                 │
│     ├── Response sanitization                                       │
│     ├── Sensitive data masking                                      │
│     └── Error information filtering                                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Monitoring and Observability

### Key Metrics

| Metric | Description | Target | Alert Threshold |
|--------|-------------|--------|-----------------|
| Request Volume | Requests per minute | Varies | > 1000 RPM |
| Average Latency | End-to-end request time | < 500ms | > 1000ms |
| Error Rate | Percentage of failed requests | < 1% | > 5% |
| Authentication Failures | Failed auth attempts | 0 | > 10/min |
| Authorization Failures | Failed authz attempts | 0 | > 5/min |
| Classification Violations | Blocked due to classification | 0 | > 1/min |
| Fabric Query Time | Average query execution time | < 200ms | > 500ms |
| Token Usage | Tokens consumed per request | < 1000 | > 5000 |

### Distributed Tracing

```python
# Distributed tracing with Application Insights
class DistributedTracer:
    def __init__(self):
        self.tracer = ApplicationInsightsTracer()
    
    def start_span(self, name: str, context: RequestContext = None):
        span = self.tracer.start_span(name)
        
        if context:
            # Link to parent span
            if context.correlation_id:
                span.set_parent(context.correlation_id)
            
            # Add context tags
            span.set_tag("request_id", context.request_id)
            span.set_tag("correlation_id", context.correlation_id)
            span.set_tag("domain", context.domain)
            span.set_tag("environment", context.environment)
            span.set_tag("user", context.caller.identity if context.caller else "system")
        
        return span
    
    def end_span(self, span, status: str = "success", error: Exception = None):
        if error:
            span.set_status("error")
            span.set_tag("error_code", getattr(error, 'error_code', 'UNKNOWN'))
            span.set_tag("error_message", str(error))
        else:
            span.set_status(status)
        
        span.finish()
```

---

*⭐ = Best Practice | 🔒 = Security Requirement | ⚡ = Performance Consideration*