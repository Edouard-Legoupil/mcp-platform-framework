# 📝 Audit API Reference

The Audit API provides comprehensive compliance logging and immutable audit trail capabilities for the MCP Platform Framework, ensuring that all sensitive operations are properly recorded for governance and compliance purposes.

## 🎯 Overview

The Audit API handles:

- **Immutable Audit Logging**: Tamper-proof logging of sensitive operations
- **Azure Blob Storage Integration**: Secure storage of audit records
- **Sensitive Access Tracking**: Automatic logging of sensitive data access
- **Compliance Monitoring**: Support for regulatory compliance requirements
- **Audit Record Management**: Query and analyze audit logs
- **Retention Policies**: Configurable audit log retention

## 🏗️ Core Classes

### AuditService

Main audit service that orchestrates all audit operations.

**Class Signature:**
```python
class AuditService:
    def __init__(
        self,
        config: Optional[AuditConfig] = None,
        storage_client: Optional[BlobServiceClient] = None
    ):
        """
        Initialize the Audit Service.
        
        Args:
            config: Audit configuration
            storage_client: Optional Azure Blob Storage client
        """
```

**Methods:**

#### `log_access()`
Log access to sensitive data or resources.

```python
async def log_access(
    self,
    action: str,
    resource: str,
    caller: Optional[CallerIdentity] = None,
    metadata: Optional[Dict[str, Any]] = None,
    classification: Optional[str] = None
) -> AuditRecord:
    """
    Log access to sensitive data or resources.
    
    Args:
        action: Action being performed (e.g., "read", "write", "delete")
        resource: Resource being accessed (e.g., "donor:12345", "report:annual")
        caller: Optional caller identity (defaults to current context)
        metadata: Additional metadata to log
        classification: Data classification level
        
    Returns:
        Created AuditRecord
    """
```

**Example:**
```python
from platform.audit import AuditService

audit_service = AuditService()

# Log sensitive data access
audit_record = await audit_service.log_access(
    action="read",
    resource="donor:12345",
    classification="CONFIDENTIAL",
    metadata={
        "tool": "GetDonorPortfolio",
        "domain": "DonorManagement",
        "query_parameters": {"include_history": True}
    }
)
```

#### `log_tool_access()`
Log access to an MCP tool.

```python
async def log_tool_access(
    self,
    tool_name: str,
    arguments: Optional[Dict[str, Any]] = None,
    caller: Optional[CallerIdentity] = None,
    classification: Optional[str] = None
) -> AuditRecord:
    """
    Log access to an MCP tool.
    
    Args:
        tool_name: Name of the tool being accessed
        arguments: Tool arguments (may be redacted for sensitive data)
        caller: Optional caller identity (defaults to current context)
        classification: Tool classification level
        
    Returns:
        Created AuditRecord
    """
```

**Example:**
```python
from platform.audit import AuditService

audit_service = AuditService()

# Log tool access
audit_record = await audit_service.log_tool_access(
    tool_name="GetDonorPortfolio",
    arguments={"donor_id": "12345"},
    classification="CONFIDENTIAL"
)
```

#### `log_data_access()`
Log access to specific data elements.

```python
async def log_data_access(
    self,
    data_type: str,
    data_id: str,
    access_type: str,
    caller: Optional[CallerIdentity] = None,
    classification: Optional[str] = None,
    fields_accessed: Optional[List[str]] = None
) -> AuditRecord:
    """
    Log access to specific data elements.
    
    Args:
        data_type: Type of data being accessed (e.g., "donor", "transaction")
        data_id: Identifier of the data being accessed
        access_type: Type of access (e.g., "read", "write", "export")
        caller: Optional caller identity (defaults to current context)
        classification: Data classification level
        fields_accessed: List of specific fields accessed
        
    Returns:
        Created AuditRecord
    """
```

**Example:**
```python
from platform.audit import AuditService

audit_service = AuditService()

# Log specific data field access
audit_record = await audit_service.log_data_access(
    data_type="donor",
    data_id="12345",
    access_type="read",
    classification="CONFIDENTIAL",
    fields_accessed=["name", "contact_info", "contribution_history"]
)
```

#### `query_audit_logs()`
Query audit logs with filtering and pagination.

```python
async def query_audit_logs(
    self,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    caller: Optional[str] = None,
    action: Optional[str] = None,
    resource: Optional[str] = None,
    classification: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> AuditQueryResult:
    """
    Query audit logs with filtering and pagination.
    
    Args:
        start_time: Start time for query (inclusive)
        end_time: End time for query (exclusive)
        caller: Filter by caller username
        action: Filter by action type
        resource: Filter by resource
        classification: Filter by classification level
        limit: Maximum number of records to return
        offset: Number of records to skip
        
    Returns:
        AuditQueryResult with matching records
    """
```

**Example:**
```python
from platform.audit import AuditService
from datetime import datetime, timedelta

audit_service = AuditService()

# Query recent audit logs
result = await audit_service.query_audit_logs(
    start_time=datetime.utcnow() - timedelta(days=7),
    end_time=datetime.utcnow(),
    caller="john.doe@unhcr.org",
    action="read",
    classification="CONFIDENTIAL",
    limit=50
)

for record in result.records:
    print(f"{record.timestamp}: {record.caller} accessed {record.resource}")
```

### AuditConfig

Configuration for audit services.

```python
@dataclass
class AuditConfig:
    # Storage Configuration
    storage_account: Optional[str] = None
    container: str = "audit-logs"
    blob_prefix: str = "mcp-audit"
    
    # Logging Configuration
    log_access: bool = True
    log_tool_access: bool = True
    log_data_access: bool = True
    log_exceptions: bool = True
    
    # Retention Configuration
    retention_days: int = 365  # 1 year
    retention_enabled: bool = True
    
    # Security Configuration
    encryption_enabled: bool = True
    immutable_storage_enabled: bool = True
    
    # Performance Configuration
    batch_size: int = 100
    flush_interval_seconds: int = 60
    
    # Redaction Configuration
    redact_sensitive_data: bool = True
    sensitive_fields: List[str] = field(default_factory=lambda: [
        "password", "secret", "token", "key", "ssn", "credit_card"
    ])
```

### AuditRecord

Represents a single audit log entry.

```python
@dataclass
class AuditRecord:
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Action Information
    action: str
    resource: str
    
    # Caller Information
    caller_username: Optional[str] = None
    caller_object_id: Optional[str] = None
    caller_tenant_id: Optional[str] = None
    caller_ip: Optional[str] = None
    
    # Context Information
    domain: Optional[str] = None
    tool_name: Optional[str] = None
    classification: Optional[str] = None
    
    # Additional Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: str = "Success"
    
    # System Information
    environment: str = "unknown"
    version: str = "1.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)
```

### AuditQueryResult

Result of an audit log query.

```python
@dataclass
class AuditQueryResult:
    records: List[AuditRecord]
    total_count: int
    limit: int
    offset: int
    has_more: bool
    
    @property
    def next_offset(self) -> Optional[int]:
        if self.has_more:
            return self.offset + self.limit
        return None
```

## 🎪 Decorators

### `@audit_tool_access`
Decorator to automatically log access to a tool.

```python
def audit_tool_access(
    func: Optional[Callable] = None,
    *,
    classification: Optional[str] = None,
    log_arguments: bool = False,
    sensitive_fields: Optional[List[str]] = None
) -> Callable:
    """
    Decorator to automatically log access to a tool.
    
    Args:
        func: Function to decorate
        classification: Tool classification level
        log_arguments: Whether to log function arguments
        sensitive_fields: Fields to redact from arguments
        
    Returns:
        Decorated function
    """
```

**Example:**
```python
from platform.audit import audit_tool_access

@audit_tool_access(classification="CONFIDENTIAL")
def get_donor_portfolio(donor_id: str):
    # Tool access is automatically logged
    return donor_service.get_portfolio(donor_id)

@audit_tool_access(classification="STRICTLY_CONFIDENTIAL", log_arguments=False)
def get_sensitive_donor_data(donor_id: str):
    # Tool access logged without arguments
    return donor_service.get_sensitive_data(donor_id)
```

### `@audit_data_access()`
Decorator to automatically log access to specific data.

```python
def audit_data_access(
    data_type: str,
    access_type: str = "read",
    classification: Optional[str] = None,
    fields: Optional[List[str]] = None
) -> Callable:
    """
    Decorator to automatically log access to specific data.
    
    Args:
        data_type: Type of data being accessed
        access_type: Type of access (read, write, delete, etc.)
        classification: Data classification level
        fields: Specific fields being accessed
        
    Returns:
        Decorated function
    """
```

**Example:**
```python
from platform.audit import audit_data_access

@audit_data_access(
    data_type="donor",
    access_type="read",
    classification="CONFIDENTIAL",
    fields=["name", "contact_info", "contribution_history"]
)
def get_donor_info(donor_id: str):
    # Data access is automatically logged
    return donor_service.get_donor(donor_id)
```

## 🔧 Configuration

### Environment Variables

```bash
# Audit Storage Configuration
AUDIT_STORAGE_ACCOUNT=your-storage-account
AUDIT_CONTAINER=audit-logs
AUDIT_BLOB_PREFIX=mcp-audit

# Audit Configuration
AUDIT_ENABLED=true
AUDIT_LOG_ACCESS=true
AUDIT_LOG_TOOL_ACCESS=true
AUDIT_LOG_DATA_ACCESS=true

# Retention Configuration
AUDIT_RETENTION_DAYS=365
AUDIT_RETENTION_ENABLED=true

# Security Configuration
AUDIT_ENCRYPTION_ENABLED=true
AUDIT_IMMUTABLE_STORAGE_ENABLED=true
AUDIT_REDACT_SENSITIVE_DATA=true
```

### Configuration File

```yaml
# config/audit.yaml
audit:
  storage:
    account: your-storage-account
    container: audit-logs
    blob_prefix: mcp-audit
  
  logging:
    log_access: true
    log_tool_access: true
    log_data_access: true
    log_exceptions: true
  
  retention:
    enabled: true
    days: 365
  
  security:
    encryption_enabled: true
    immutable_storage_enabled: true
    redact_sensitive_data: true
    sensitive_fields:
      - password
      - secret
      - token
      - key
      - ssn
      - credit_card
  
  performance:
    batch_size: 100
    flush_interval_seconds: 60
```

## 🚀 Quick Start

### Basic Audit Setup

```python
from platform.audit import AuditService, AuditConfig

# Configure audit
config = AuditConfig(
    storage_account="your-storage-account",
    container="audit-logs",
    log_tool_access=True,
    log_data_access=True,
    retention_days=365
)

# Initialize audit service
audit_service = AuditService(config=config)

# Log tool access
audit_record = await audit_service.log_tool_access(
    tool_name="GetDonorPortfolio",
    classification="CONFIDENTIAL"
)
```

### Using Decorators

```python
from platform.audit import audit_tool_access, audit_data_access

# Audit tool access
@audit_tool_access(classification="CONFIDENTIAL")
def get_donor_portfolio(donor_id: str):
    return donor_service.get_portfolio(donor_id)

# Audit data access
@audit_data_access(
    data_type="donor",
    access_type="read",
    classification="CONFIDENTIAL"
)
def get_donor_info(donor_id: str):
    return donor_service.get_donor(donor_id)
```

### Azure Function Integration

```python
from platform.audit import AuditService, audit_tool_access
import azure.functions as func

# Initialize audit service
audit_service = AuditService()

@audit_tool_access(classification="CONFIDENTIAL")
def main(req: func.HttpRequest) -> func.HttpResponse:
    # Log custom audit event
    await audit_service.log_access(
        action="http_request",
        resource=f"function:{req.function_name}",
        metadata={
            "method": req.method,
            "path": req.path,
            "query_params": dict(req.params)
        }
    )
    
    # Process request
    donor_id = req.params.get("donor_id")
    donor_data = donor_service.get_donor(donor_id)
    
    return func.HttpResponse(f"Donor data: {donor_data}")
```

## ⭐ Best Practices

### Audit Logging Design

✅ **Log All Sensitive Operations**
```python
# Good: Audit all sensitive data access
@audit_tool_access(classification="CONFIDENTIAL")
def get_donor_financial_data(donor_id: str):
    pass

@audit_data_access(data_type="donor", access_type="read", classification="CONFIDENTIAL")
def get_donor_pii(donor_id: str):
    pass
```

❌ **Don't Miss Sensitive Operations**
```python
# Bad: Missing audit logging for sensitive operations
def get_donor_ssn(donor_id: str):  # No audit logging!
    pass
```

### Data Redaction

✅ **Redact Sensitive Data**
```python
# Good: Redact sensitive fields from audit logs
@audit_tool_access(
    classification="CONFIDENTIAL",
    log_arguments=True,
    sensitive_fields=["ssn", "credit_card", "password"]
)
def process_payment(payment_info: dict):
    pass
```

✅ **Configure Global Redaction**
```python
# Good: Configure sensitive fields globally
config = AuditConfig(
    redact_sensitive_data=True,
    sensitive_fields=["password", "secret", "token", "ssn", "credit_card"]
)
```

### Query Optimization

✅ **Use Efficient Queries**
```python
# Good: Use filters to limit query scope
result = await audit_service.query_audit_logs(
    start_time=datetime.utcnow() - timedelta(days=7),
    end_time=datetime.utcnow(),
    caller="john.doe@unhcr.org",
    action="read",
    limit=100
)
```

❌ **Avoid Broad Queries**
```python
# Bad: Query without filters (returns too much data)
result = await audit_service.query_audit_logs(limit=10000)  # Too broad!
```

## 🔍 Troubleshooting

### Common Issues

**Audit logs not appearing in storage**
- Verify that `AUDIT_STORAGE_ACCOUNT` is set correctly
- Check that the storage account has the correct permissions
- Ensure the container exists and is accessible

**Audit logs are incomplete**
- Verify that all required logging options are enabled
- Check that decorators are properly applied
- Ensure caller identity is properly extracted

**High storage costs**
- Review retention policies and reduce retention period if appropriate
- Enable data redaction to reduce storage requirements
- Consider sampling for very high-volume operations

**Performance issues with audit logging**
- Enable batching to reduce I/O operations
- Adjust flush interval based on volume
- Consider async logging for better performance

**Sensitive data in audit logs**
- Verify that redaction is enabled
- Check that sensitive fields are correctly configured
- Review audit logs to ensure no sensitive data is stored

## 📚 Related Documentation

- [Platform API](platform.md) - Core framework classes
- [Audit Logging Module](../modules/audit-logging.md) - Module overview
- [Security Best Practices](../best-practices/security.md) - Security recommendations
- [Compliance Best Practices](../best-practices/security.md#compliance) - Compliance guidelines

---

**🎉 Ready to implement audit logging?** Start with the `@audit_tool_access` decorator for automatic logging.

**Need more details?** Check the [Audit Logging Module](../modules/audit-logging.md) for comprehensive module documentation.