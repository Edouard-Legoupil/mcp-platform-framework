# 📝 Audit Logging Module

The Audit Logging Module provides immutable audit logging for sensitive operations and compliance monitoring in the MCP Platform Framework.

## 🎯 Overview

The Audit Logging Module handles:
- **Automatic Audit Records**: User identification, tool name, parameters, timestamp, operation result
- **Sensitive Query Detection**: Pattern matching for sensitive data, automatic audit triggering
- **Compliance Monitoring**: Access pattern analysis, anomaly detection, compliance reporting
- **Immutable Storage**: Write-once, read-many storage, tamper-evident logging, long-term retention

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│          Audit Logging Module            │
├─────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Audit Record    │  │  Sensitive      │ │
│  │  Generation     │  │  Query Detection│ │
│  └─────────────────┘  └─────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Compliance      │  │ Immutable       │ │
│  │ Monitoring      │  │ Storage         │ │
│  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────┘
```

## 🚀 Quick Start

### Basic Usage

```python
from platform.audit import audit_log

@audit_log.sensitive_operation
@requires_permission("finance.confidential")
def get_top_contributions():
    # This operation will be automatically audited
    return contribution_service.get_top(10)
```

### Configuration

```python
# config/audit.py
from platform.audit.config import AuditConfig

AUDIT_CONFIG = AuditConfig(
    # Storage configuration
    storage_account="your-storage-account",
    container="audit-logs",
    
    # Retention
    retention_days=3650,  # 10 years
    
    # SIEM integration
    siem_enabled=True,
    siem_endpoint="https://siem.my-org.org/api/audit",
    
    # Sensitive operations
    sensitive_operations=[
        "GetTopDonorContributions",
        "GetFinancialReports",
        "DeleteDonor"
    ],
    
    # Classification levels that require auditing
    audit_classifications=["CONFIDENTIAL", "STRICTLY CONFIDENTIAL"]
)
```

## 🔧 Configuration

### Environment Variables

```bash
# Audit Storage
AUDIT_STORAGE_ACCOUNT=your-storage-account
AUDIT_STORAGE_CONNECTION_STRING=your-connection-string
AUDIT_CONTAINER=audit-logs

# Retention
AUDIT_RETENTION_DAYS=3650

# SIEM Integration
AUDIT_SIEM_ENABLED=true
AUDIT_SIEM_ENDPOINT=https://siem.my-org.org/api/audit
AUDIT_SIEM_CREDENTIALS=your-credentials
```

### Configuration File

```yaml
# config/audit.yaml
audit:
  storage:
    account: ${AUDIT_STORAGE_ACCOUNT}
    connection_string: ${AUDIT_STORAGE_CONNECTION_STRING}
    container: ${AUDIT_CONTAINER}
    
  retention:
    days: 3650
    legal_hold_enabled: true
    
  siem:
    enabled: true
    endpoint: ${AUDIT_SIEM_ENDPOINT}
    credentials: ${AUDIT_SIEM_CREDENTIALS}
    batch_size: 100
    batch_interval: 5
    
  sensitive_operations:
    - "GetTopDonorContributions"
    - "GetFinancialReports"
    - "DeleteDonor"
    - "*Confidential*"
    - "*Admin*"
    
  audit_classifications:
    - "CONFIDENTIAL"
    - "STRICTLY CONFIDENTIAL"
    
  patterns:
    sensitive_data:
      - "\\b\\d{4}[\\s-]?\\d{4}[\\s-]?\\d{4}[\\s-]?\\d{4}\\b"  # Credit card
      - "\\b\\d{3}-\\d{2}-\\d{4}\\b"  # SSN
      - "password"
      - "secret"
      - "token"
```

## 🎯 API Reference

### Decorators

#### `@sensitive_operation`

Marks a function as a sensitive operation that should be audited.

```python
from platform.audit import sensitive_operation

@sensitive_operation
def get_financial_reports():
    # This operation will be audited
    return finance_service.get_reports()

# With custom classification
@sensitive_operation(classification="STRICTLY CONFIDENTIAL")
def get_confidential_data():
    pass
```

**Parameters:**
- `classification` (str, optional): Data classification level
- `audit_condition` (callable, optional): Function to determine if operation should be audited

#### `@audit_log`

Automatically logs audit records for a function.

```python
from platform.audit import audit_log

@audit_log
def delete_donor(donor_id: str):
    # This operation will be audited
    return donor_service.delete(donor_id)

# With custom audit parameters
@audit_log(
    action="delete",
    resource_type="donor",
    classification="CONFIDENTIAL"
)
def delete_donor(donor_id: str):
    pass
```

**Parameters:**
- `action` (str, optional): Action being performed
- `resource_type` (str, optional): Type of resource
- `classification` (str, optional): Data classification level

### Functions

#### `log_audit_event(event)`

Logs an audit event.

```python
from platform.audit import log_audit_event, AuditEvent

event = AuditEvent(
    action="read",
    resource="donor:DON-12345",
    tool="GetDonorData",
    user="john.doe@my-org.org",
    result="Success",
    classification="CONFIDENTIAL"
)

log_audit_event(event)
```

**Parameters:**
- `event` (AuditEvent): The audit event to log

#### `log_data_access(user, resource, action, classification)`

Logs a data access event.

```python
from platform.audit import log_data_access

log_data_access(
    user="john.doe@my-org.org",
    resource="donor:DON-12345",
    action="read",
    classification="CONFIDENTIAL"
)
```

**Parameters:**
- `user` (str): User identity
- `resource` (str): Resource being accessed
- `action` (str): Action being performed
- `classification` (str): Data classification level
- `result` (str, optional): Result of the operation
- `metadata` (dict, optional): Additional metadata

#### `log_data_modification(user, resource, action, classification)`

Logs a data modification event.

```python
from platform.audit import log_data_modification

log_data_modification(
    user="john.doe@my-org.org",
    resource="donor:DON-12345",
    action="update",
    classification="CONFIDENTIAL",
    changes={"status": "active", "last_updated": "2026-05-01"}
)
```

**Parameters:**
- `user` (str): User identity
- `resource` (str): Resource being modified
- `action` (str): Action being performed (update, delete, create)
- `classification` (str): Data classification level
- `changes` (dict, optional): Changes being made
- `result` (str, optional): Result of the operation

### Classes

#### `AuditEvent`

Represents an audit event.

```python
from platform.audit import AuditEvent

event = AuditEvent(
    audit_id="aud-20260501-103000-001",
    user="john.doe@my-org.org",
    tool="GetTopDonorContributions",
    time=datetime.utcnow(),
    parameters={"year": 2026, "limit": 10},
    result="Success",
    classification="CONFIDENTIAL",
    ip_address="192.168.1.100",
    user_agent="MCP-Client/1.0",
    session_id="sess-20260501-100000-001"
)

# Convert to dictionary
event_dict = event.to_dict()

# Convert to JSON
event_json = event.to_json()
```

**Attributes:**
- `audit_id` (str): Unique audit ID
- `user` (str): User identity
- `tool` (str): Tool name
- `time` (datetime): Timestamp
- `parameters` (dict): Operation parameters
- `result` (str): Operation result
- `classification` (str): Data classification
- `ip_address` (str): Client IP address
- `user_agent` (str): Client user agent
- `session_id` (str): Session ID
- `error_code` (str): Error code (if error)
- `error_message` (str): Error message (if error)
- `action` (str): Action being performed
- `resource` (str): Resource being accessed
- `domain` (str): Domain name

**Methods:**
- `to_dict()`: Convert to dictionary
- `to_json()`: Convert to JSON string

#### `AuditStore`

Stores audit events with immutability guarantees.

```python
from platform.audit import AuditStore

# Create audit store
store = AuditStore(
    storage_account="your-storage-account",
    container="audit-logs"
)

# Store an audit event
audit_id = await store.store(event)

# Get an audit event
event = await store.get(audit_id)

# Search audit events
events = await store.search(
    user="john.doe@my-org.org",
    start_time=datetime(2026, 5, 1),
    end_time=datetime(2026, 5, 2)
)
```

**Parameters:**
- `storage_account` (str): Azure Storage account name
- `container` (str): Blob container name
- `connection_string` (str, optional): Storage connection string
- `retention_days` (int, optional): Retention period in days

**Methods:**
- `store(event)`: Store an audit event
- `get(audit_id)`: Get an audit event by ID
- `search(**kwargs)`: Search audit events
- `set_legal_hold(audit_id, tags)`: Set legal hold on an audit event
- `get_statistics()`: Get audit storage statistics

#### `AuditLogger`

High-level audit logging interface.

```python
from platform.audit import AuditLogger

# Create audit logger
logger = AuditLogger(
    store=audit_store,
    siem_enabled=True,
    siem_endpoint="https://siem.my-org.org/api/audit"
)

# Log an event
logger.log(event)

# Log data access
logger.log_data_access(
    user="john.doe@my-org.org",
    resource="donor:DON-12345",
    action="read",
    classification="CONFIDENTIAL"
)

# Log authorization failure
logger.log_authorization_failure(
    user="john.doe@my-org.org",
    permission="finance.confidential",
    resource="finance:REP-2026-001"
)
```

**Parameters:**
- `store` (AuditStore): The audit store to use
- `siem_enabled` (bool, optional): Enable SIEM integration
- `siem_endpoint` (str, optional): SIEM endpoint URL
- `siem_credentials` (str, optional): SIEM credentials

**Methods:**
- `log(event)`: Log an audit event
- `log_data_access(**kwargs)`: Log a data access event
- `log_data_modification(**kwargs)`: Log a data modification event
- `log_authorization_failure(**kwargs)`: Log an authorization failure
- `log_authentication_event(**kwargs)`: Log an authentication event
- `log_security_event(**kwargs)`: Log a security event

## 📊 Audit Record Structure

### Standard Audit Record

```json
{
  "audit_id": "aud-20260501-103000-001",
  "user": "john.doe@my-org.org",
  "tool": "GetTopDonorContributions",
  "time": "2026-05-01T10:30:00Z",
  "parameters": {
    "year": 2026,
    "limit": 10
  },
  "result": "Success",
  "classification": "CONFIDENTIAL",
  "ip_address": "192.168.1.100",
  "user_agent": "MCP-Client/1.0",
  "session_id": "sess-20260501-100000-001",
  "domain": "DonorManagement",
  "action": "read",
  "resource": "donor:top-contributions"
}
```

### Error Audit Record

```json
{
  "audit_id": "aud-20260501-103001-002",
  "user": "john.doe@my-org.org",
  "tool": "DeleteDonor",
  "time": "2026-05-01T10:30:01Z",
  "parameters": {
    "donor_id": "DON-12345"
  },
  "result": "Failure",
  "classification": "CONFIDENTIAL",
  "error_code": "AUTHZ-002",
  "error_message": "Permission denied: donor.delete required",
  "ip_address": "192.168.1.100",
  "user_agent": "MCP-Client/1.0",
  "session_id": "sess-20260501-100000-001"
}
```

## 📈 Monitoring and Compliance

### Key Metrics

| Metric | Description | Target | Alert Threshold |
|--------|-------------|--------|-----------------|
| Audit Events | Number of audit events per day | Varies | < 1000/day |
| Sensitive Operations | Number of sensitive operations | Varies | > 100/hour |
| Authorization Failures | Number of authorization failures | 0 | > 10/hour |
| Data Access | Number of data access events | Varies | > 1000/hour |
| Storage Usage | Audit log storage usage | < 90% | > 95% |

### Compliance Reporting

```python
from platform.audit import ComplianceReporter

# Create compliance reporter
reporter = ComplianceReporter(audit_store)

# Generate compliance report
report = await reporter.generate_report(
    start_time=datetime(2026, 5, 1),
    end_time=datetime(2026, 5, 31),
    user="john.doe@my-org.org"
)

# Get access patterns
patterns = await reporter.get_access_patterns(
    user="john.doe@my-org.org",
    days=30
)

# Get anomaly detection results
anomalies = await reporter.detect_anomalies(
    start_time=datetime(2026, 5, 1),
    end_time=datetime(2026, 5, 31)
)
```

**Methods:**
- `generate_report(start_time, end_time, **kwargs)`: Generate a compliance report
- `get_access_patterns(user, days)`: Get access patterns for a user
- `detect_anomalies(start_time, end_time)`: Detect anomalous access patterns
- `get_sensitive_operations(start_time, end_time)`: Get sensitive operations
- `get_authorization_failures(start_time, end_time)`: Get authorization failures

## 🚀 Best Practices

### ⭐ Audit Sensitive Operations

Always audit operations that access sensitive data.

```python
# Good
@audit_log.sensitive_operation
@requires_permission("finance.confidential")
def get_financial_reports():
    pass

# Bad - No audit logging
@requires_permission("finance.confidential")
def get_financial_reports():
    pass
```

### ⭐ Include Comprehensive Context

Include all relevant context in audit records.

```python
# Good - Comprehensive context
log_data_access(
    user="john.doe@my-org.org",
    resource="donor:DON-12345",
    action="read",
    classification="CONFIDENTIAL",
    ip_address="192.168.1.100",
    user_agent="MCP-Client/1.0",
    session_id="sess-20260501-100000-001"
)

# Bad - Missing context
log_data_access(
    user="john.doe@my-org.org",
    resource="donor:DON-12345"
)
```

### ⭐ Use Immutable Storage

Always use immutable storage for audit logs.

```python
# Good - Immutable storage
store = AuditStore(
    storage_account="your-storage-account",
    container="audit-logs",
    retention_days=3650,
    immutable=True
)

# Bad - Mutable storage
# Using regular storage without immutability
```

### ⭐ Set Appropriate Retention

Set retention periods based on compliance requirements.

```python
# Good - Appropriate retention
config = AuditConfig(
    retention_days=3650  # 10 years for compliance
)

# Bad - Insufficient retention
config = AuditConfig(
    retention_days=30  # Too short for compliance
)
```

### ⭐ Integrate with SIEM

Integrate audit logging with your SIEM system.

```python
# Good - SIEM integration
logger = AuditLogger(
    store=audit_store,
    siem_enabled=True,
    siem_endpoint="https://siem.my-org.org/api/audit"
)

# Bad - No SIEM integration
logger = AuditLogger(
    store=audit_store,
    siem_enabled=False
)
```

### ⭐ Monitor Audit Storage

Monitor audit storage health and usage.

```python
# Good - Storage monitoring
from platform.audit import AuditStorageMonitor

monitor = AuditStorageMonitor(audit_store)

# Check storage health
is_healthy = await monitor.is_healthy()

# Get storage statistics
stats = await monitor.get_statistics()

# Bad - No storage monitoring
# No monitoring of audit storage
```

## 🔍 Troubleshooting

### Common Issues

#### Audit Events Not Being Stored

**Symptoms:** No audit events in storage

**Causes:**
- Storage configuration incorrect
- Network connectivity issues
- Permission issues
- Storage account doesn't exist

**Solutions:**
1. Check storage configuration: `AUDIT_CONFIG`
2. Verify network connectivity to storage account
3. Check storage account permissions
4. Verify container exists

```python
# Debug audit storage
from platform.audit import AuditStore

store = AuditStore(
    storage_account="your-storage-account",
    container="audit-logs"
)

# Test storage
try:
    test_event = AuditEvent(
        audit_id="test-001",
        user="test",
        tool="TestTool",
        time=datetime.utcnow(),
        result="Success"
    )
    audit_id = await store.store(test_event)
    print(f"Storage test successful: {audit_id}")
except Exception as e:
    print(f"Storage test failed: {e}")
```

#### SIEM Integration Not Working

**Symptoms:** Audit events not appearing in SIEM

**Causes:**
- SIEM endpoint incorrect
- SIEM credentials invalid
- Network connectivity issues
- SIEM API rate limiting

**Solutions:**
1. Check SIEM endpoint: `AUDIT_SIEM_ENDPOINT`
2. Verify SIEM credentials: `AUDIT_SIEM_CREDENTIALS`
3. Check network connectivity to SIEM endpoint
4. Check SIEM API rate limits

```python
# Debug SIEM integration
from platform.audit import AuditLogger

logger = AuditLogger(
    store=audit_store,
    siem_enabled=True,
    siem_endpoint="https://siem.my-org.org/api/audit"
)

# Test SIEM logging
try:
    test_event = AuditEvent(
        audit_id="siem-test-001",
        user="test",
        tool="TestTool",
        time=datetime.utcnow(),
        result="Success"
    )
    await logger.log(test_event)
    print("SIEM logging test successful")
except Exception as e:
    print(f"SIEM logging test failed: {e}")
```

#### High Audit Storage Usage

**Symptoms:** High storage costs, performance issues

**Causes:**
- Retention period too long
- Too many audit events
- Large audit event sizes

**Solutions:**
1. Reduce retention period (if compliance allows)
2. Implement sampling for high-volume operations
3. Compress audit event data
4. Archive old audit events

```python
# Reduce audit volume
config = AuditConfig(
    retention_days=1825,  # 5 years instead of 10
    sampling_rate=0.5,  # 50% sampling for high-volume operations
    compression_enabled=True
)
```

## 📚 Examples

### Complete Audit Logging Example

```python
from platform.auth import authenticated_tool, requires_permission
from platform.audit import audit_log, log_data_access, get_caller_identity

@authenticated_tool
@requires_permission("finance.confidential")
@audit_log.sensitive_operation
@capture_tool_metrics
def get_financial_report(report_id: str):
    """Get financial report with comprehensive audit logging"""
    
    # Get caller information
    caller = get_caller_identity()
    
    # Log data access
    log_data_access(
        user=caller.identity,
        resource=f"finance:report:{report_id}",
        action="read",
        classification="CONFIDENTIAL",
        ip_address=get_client_ip(),
        user_agent=get_user_agent()
    )
    
    # Get report
    report = await finance_service.get_report(report_id)
    
    # Log additional details
    log_data_access(
        user=caller.identity,
        resource=f"finance:report:{report_id}",
        action="read",
        classification="CONFIDENTIAL",
        metadata={
            "report_type": report.type,
            "report_period": report.period,
            "data_volume": len(report.data)
        }
    )
    
    return report
```

### Authorization Failure Logging

```python
from platform.auth import requires_permission, AuthorizationError
from platform.audit import log_authorization_failure, get_caller_identity

@requires_permission("finance.confidential")
def get_confidential_data():
    """Get confidential data with authorization failure logging"""
    pass

# Custom authorization check with logging
def check_finance_access(user, required_permission):
    """Check finance access with audit logging"""
    caller = get_caller_identity()
    
    if not caller.has_permission(required_permission):
        # Log authorization failure
        log_authorization_failure(
            user=caller.identity,
            permission=required_permission,
            resource="finance:confidential",
            ip_address=get_client_ip(),
            user_agent=get_user_agent()
        )
        
        raise AuthorizationError(
            error_code="AUTHZ-002",
            message=f"Permission denied: {required_permission} required"
        )
    
    return True
```

### Sensitive Data Access Pattern Detection

```python
from platform.audit import SensitivePatternDetector, log_data_access

# Create pattern detector
detector = SensitivePatternDetector(
    patterns=[
        r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",  # Credit card
        r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
        r"password",
        r"secret",
        r"token"
    ]
)

@audit_log.sensitive_operation
@requires_permission("donor.read")
def search_donors(query: str):
    """Search donors with sensitive pattern detection"""
    
    # Check for sensitive patterns in query
    sensitive_patterns = detector.detect(query)
    
    if sensitive_patterns:
        # Log potential sensitive data access
        log_data_access(
            user=get_caller_identity().identity,
            resource="donor:search",
            action="search",
            classification="CONFIDENTIAL",
            metadata={
                "query": query,
                "sensitive_patterns": sensitive_patterns,
                "warning": "Potential sensitive data in query"
            }
        )
    
    # Perform search
    results = await donor_service.search(query)
    
    return results
```

---

## 📖 API Reference

### Exceptions

| Exception | Description | Error Code |
|-----------|-------------|------------|
| `AuditError` | Base audit error | AUDIT-001 |
| `AuditStorageError` | Audit storage error | AUDIT-002 |
| `AuditConfigurationError` | Configuration error | AUDIT-003 |
| `AuditSIEMError` | SIEM integration error | AUDIT-004 |

### Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| AUDIT-001 | Audit error | 500 |
| AUDIT-002 | Storage error | 500 |
| AUDIT-003 | Configuration error | 500 |
| AUDIT-004 | SIEM error | 503 |

---

*⭐ = Best Practice | 🔒 = Security Requirement | ⚡ = Performance Consideration*