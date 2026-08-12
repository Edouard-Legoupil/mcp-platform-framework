# 🏷️ Data Classification Module

The Data Classification Module provides data classification controls and governance policy enforcement for the MCP Platform Framework, ensuring that sensitive data is properly protected and accessed only by authorized users.

## 🎯 Overview

The Data Classification Module handles:
- **Classification Levels**: PUBLIC, INTERNAL, CONFIDENTIAL, STRICTLY CONFIDENTIAL
- **Classification Decorators**: `@classification()` for tools and data
- **Governance Policy Enforcement**: Centralized policy definitions and automatic application
- **Framework Controls**: Classification validation, access restriction enforcement, audit logging integration

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│       Data Classification Module         │
├─────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Classification  │  │ Governance      │ │
│  │ Levels          │  │ Policy          │ │
│  └─────────────────┘  │ Enforcement     │ │
│                      └─────────────────┘ │
│  ┌─────────────────────────────────────┐ │
│  │         Framework Controls            │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## 🚀 Quick Start

### Basic Usage

```python
from platform.classification import classification, ClassificationLevel

@classification(ClassificationLevel.CONFIDENTIAL)
@requires_permission("finance.confidential")
def get_financial_reports():
    return finance_service.get_reports()
```

### Configuration

```python
# config/classification.py
from platform.classification.config import ClassificationConfig

CLASSIFICATION_CONFIG = ClassificationConfig(
    # Classification levels
    levels={
        "PUBLIC": {
            "level": 0,
            "access": "open",
            "audit": False,
            "encryption": False,
            "retention": "1 year"
        },
        "INTERNAL": {
            "level": 1,
            "access": "domain",
            "audit": True,
            "encryption": True,
            "retention": "3 years"
        },
        "CONFIDENTIAL": {
            "level": 2,
            "access": "permission",
            "audit": True,
            "encryption": True,
            "retention": "7 years",
            "watermark": True,
            "screening": True
        },
        "STRICTLY CONFIDENTIAL": {
            "level": 3,
            "access": "approval",
            "audit": True,
            "encryption": True,
            "retention": "10 years",
            "watermark": True,
            "screening": True,
            "justification": True
        }
    },
    
    # Default classification for tools
    default_classification="INTERNAL",
    
    # Classification inheritance
    inheritance_enabled=True,
    
    # Audit requirements
    audit_classifications=["CONFIDENTIAL", "STRICTLY CONFIDENTIAL"]
)
```

## 🔧 Configuration

### Environment Variables

```bash
# Classification Configuration
CLASSIFICATION_DEFAULT=INTERNAL
CLASSIFICATION_AUDIT_ENABLED=true
CLASSIFICATION_AUDIT_LEVELS=CONFIDENTIAL,STRICTLY CONFIDENTIAL

# Classification Levels
CLASSIFICATION_LEVEL_PUBLIC=0
CLASSIFICATION_LEVEL_INTERNAL=1
CLASSIFICATION_LEVEL_CONFIDENTIAL=2
CLASSIFICATION_LEVEL_STRICTLY_CONFIDENTIAL=3
```

### Configuration File

```yaml
# config/classification.yaml
classification:
  levels:
    PUBLIC:
      level: 0
      access: open
      audit: false
      encryption: false
      retention: "1 year"
      
    INTERNAL:
      level: 1
      access: domain
      audit: true
      encryption: true
      retention: "3 years"
      
    CONFIDENTIAL:
      level: 2
      access: permission
      audit: true
      encryption: true
      retention: "7 years"
      watermark: true
      screening: true
      
    STRICTLY CONFIDENTIAL:
      level: 3
      access: approval
      audit: true
      encryption: true
      retention: "10 years"
      watermark: true
      screening: true
      justification: true
      
  default: INTERNAL
  
  audit:
    enabled: true
    levels:
      - CONFIDENTIAL
      - STRICTLY CONFIDENTIAL
    
  inheritance:
    enabled: true
    
  policies:
    # Domain-specific classification policies
    donor:
      default: INTERNAL
      max: CONFIDENTIAL
      
    finance:
      default: CONFIDENTIAL
      max: STRICTLY CONFIDENTIAL
      
    supply:
      default: INTERNAL
      max: CONFIDENTIAL
```

## 🎯 API Reference

### Decorators

#### `@classification(level)`

Sets the classification level for a tool or function.

```python
from platform.classification import classification, ClassificationLevel

@classification(ClassificationLevel.CONFIDENTIAL)
def get_financial_reports():
    return finance_service.get_reports()

# With string level
@classification("CONFIDENTIAL")
def get_donor_data():
    pass

# With additional metadata
@classification(
    level=ClassificationLevel.CONFIDENTIAL,
    justification_required=True,
    audit=True
)
def get_confidential_data():
    pass
```

**Parameters:**
- `level` (ClassificationLevel or str): Classification level
- `justification_required` (bool, optional): Whether justification is required
- `audit` (bool, optional): Whether to audit access
- `encryption_required` (bool, optional): Whether encryption is required

#### `@classification_check`

Checks if the caller can access the specified classification level.

```python
from platform.classification import classification_check, ClassificationLevel

@classification_check(ClassificationLevel.CONFIDENTIAL)
def get_confidential_report():
    # Caller must have access to CONFIDENTIAL level
    return report_service.get_confidential_report()

# With custom error message
@classification_check(
    ClassificationLevel.CONFIDENTIAL,
    error_message="Access to confidential data requires higher clearance"
)
def get_confidential_data():
    pass
```

**Parameters:**
- `level` (ClassificationLevel or str): Required classification level
- `error_message` (str, optional): Custom error message
- `error_code` (str, optional): Custom error code

### Functions

#### `get_classification_level(name)`

Gets the classification level by name.

```python
from platform.classification import get_classification_level, ClassificationLevel

level = get_classification_level("CONFIDENTIAL")
# Returns: ClassificationLevel.CONFIDENTIAL

level = get_classification_level("STRICTLY CONFIDENTIAL")
# Returns: ClassificationLevel.STRICTLY_CONFIDENTIAL
```

**Parameters:**
- `name` (str): Classification level name

**Returns:**
- `ClassificationLevel`: The classification level

#### `can_access_classification(user_level, required_level)`

Checks if a user with a given classification level can access a required level.

```python
from platform.classification import can_access_classification, ClassificationLevel

# User with CONFIDENTIAL can access INTERNAL
can_access = can_access_classification(
    ClassificationLevel.CONFIDENTIAL,
    ClassificationLevel.INTERNAL
)
# Returns: True

# User with INTERNAL cannot access CONFIDENTIAL
can_access = can_access_classification(
    ClassificationLevel.INTERNAL,
    ClassificationLevel.CONFIDENTIAL
)
# Returns: False
```

**Parameters:**
- `user_level` (ClassificationLevel or str): User's classification level
- `required_level` (ClassificationLevel or str): Required classification level

**Returns:**
- `bool`: True if user can access the required level, False otherwise

#### `get_current_classification()`

Gets the current classification level from the request context.

```python
from platform.classification import get_current_classification

current_level = get_current_classification()
# Returns: ClassificationLevel.CONFIDENTIAL (or current context level)
```

**Returns:**
- `ClassificationLevel`: The current classification level

#### `set_current_classification(level)`

Sets the current classification level in the request context.

```python
from platform.classification import set_current_classification, ClassificationLevel

set_current_classification(ClassificationLevel.CONFIDENTIAL)
```

**Parameters:**
- `level` (ClassificationLevel or str): Classification level to set

### Classes

#### `ClassificationLevel`

Classification levels for data sensitivity.

```python
from platform.classification import ClassificationLevel

# Available levels
levels = [
    ClassificationLevel.PUBLIC,
    ClassificationLevel.INTERNAL,
    ClassificationLevel.CONFIDENTIAL,
    ClassificationLevel.STRICTLY_CONFIDENTIAL
]

# Compare levels
if ClassificationLevel.CONFIDENTIAL > ClassificationLevel.INTERNAL:
    print("CONFIDENTIAL is higher than INTERNAL")

# Get level value
level_value = ClassificationLevel.CONFIDENTIAL.value  # Returns: 2
```

**Values:**
- `PUBLIC`: 0 - Non-sensitive data, open access
- `INTERNAL`: 1 - Internal business data, domain access required
- `CONFIDENTIAL`: 2 - Sensitive business data, explicit permission required
- `STRICTLY_CONFIDENTIAL`: 3 - Highly sensitive data, special approval required

**Methods:**
- `from_string(name)`: Create ClassificationLevel from string
- `to_string()`: Convert to string

#### `ClassificationService`

Main service for classification management.

```python
from platform.classification import ClassificationService

# Create classification service
service = ClassificationService()

# Check if user can access classification
can_access = service.can_access(
    user="john.doe@my-org.org",
    required_level=ClassificationLevel.CONFIDENTIAL
)

# Get user's maximum classification
max_level = service.get_user_classification("john.doe@my-org.org")

# Check if tool requires justification
requires_justification = service.requires_justification(
    tool="GetFinancialReports",
    user="john.doe@my-org.org"
)
```

**Parameters:**
- `config` (ClassificationConfig, optional): Classification configuration
- `policy_store` (PolicyStore, optional): Policy store for classification policies

**Methods:**
- `can_access(user, required_level)`: Check if user can access classification
- `get_user_classification(user)`: Get user's maximum classification level
- `get_tool_classification(tool)`: Get tool's classification level
- `requires_justification(tool, user)`: Check if tool requires justification
- `check_justification(user, resource, action)`: Check if user has justification
- `get_classification_requirements(resource)`: Get classification requirements for resource

#### `ClassificationPolicy`

Manages classification policies.

```python
from platform.classification import ClassificationPolicy

# Create classification policy
policy = ClassificationPolicy()

# Get classification for a resource
classification = policy.get_classification("finance:report:2026")

# Set classification for a resource
policy.set_classification("finance:report:2026", ClassificationLevel.CONFIDENTIAL)

# Get all classifications for a domain
classifications = policy.get_domain_classifications("finance")
```

**Methods:**
- `get_classification(resource)`: Get classification for a resource
- `set_classification(resource, level)`: Set classification for a resource
- `get_domain_classifications(domain)`: Get all classifications for a domain
- `get_default_classification(domain)`: Get default classification for a domain
- `get_max_classification(domain)`: Get maximum classification for a domain

## 📊 Classification Levels

### Level Comparison

| Level | Value | Access Requirements | Audit Required | Encryption Required | Retention |
|-------|-------|---------------------|----------------|---------------------|-----------|
| PUBLIC | 0 | None | No | No | 1 year |
| INTERNAL | 1 | Domain access | Yes | Yes | 3 years |
| CONFIDENTIAL | 2 | Explicit permission | Yes | Yes | 7 years |
| STRICTLY CONFIDENTIAL | 3 | Special approval | Yes | Yes | 10 years |

### Access Control Matrix

| User Level \\ Required Level | PUBLIC | INTERNAL | CONFIDENTIAL | STRICTLY CONFIDENTIAL |
|-------------------------------|--------|----------|--------------|------------------------|
| PUBLIC | ✅ | ❌ | ❌ | ❌ |
| INTERNAL | ✅ | ✅ | ❌ | ❌ |
| CONFIDENTIAL | ✅ | ✅ | ✅ | ❌ |
| STRICTLY CONFIDENTIAL | ✅ | ✅ | ✅ | ✅ |

## 🔐 Security Features

### Classification Enforcement

```python
from platform.classification import ClassificationEnforcer

# Create enforcer
enforcer = ClassificationEnforcer()

# Enforce classification for a tool
@enforcer.enforce_classification
@classification(ClassificationLevel.CONFIDENTIAL)
def get_confidential_data():
    pass

# Check classification before access
can_access = enforcer.check_access(
    user="john.doe@my-org.org",
    resource="finance:report:2026",
    action="read"
)
```

### Data Masking

```python
from platform.classification import DataMasker

# Create data masker
masker = DataMasker()

# Mask sensitive data based on classification
masked_data = masker.mask(
    data={"ssn": "123-45-6789", "name": "John Doe"},
    classification=ClassificationLevel.CONFIDENTIAL
)
# Returns: {"ssn": "***MASKED***", "name": "John Doe"}

# Mask with custom rules
masked_data = masker.mask_with_rules(
    data={"ssn": "123-45-6789", "email": "john@my-org.org"},
    rules={
        "ssn": "***SSN***",
        "email": "***EMAIL***"
    }
)
```

### Tokenization

```python
from platform.classification import DataTokenizationService

# Create tokenization service
tokenizer = DataTokenizationService()

# Tokenize sensitive data
tokenized_data = tokenizer.tokenize(
    data={"credit_card": "4111-1111-1111-1111"},
    patterns=[
        r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"
    ]
)
# Returns: {"credit_card": "[TOKENIZED_CARD]"}
```

## 📈 Monitoring and Compliance

### Key Metrics

| Metric | Description | Target | Alert Threshold |
|--------|-------------|--------|-----------------|
| Classification Violations | Attempts to access higher classification | 0 | > 5/day |
| Justification Requests | Requests requiring justification | Varies | > 10/hour |
| Data Access by Level | Data access grouped by classification | Varies | Unusual patterns |
| Classification Changes | Changes to classification levels | Varies | > 5/day |

### Compliance Reporting

```python
from platform.classification import ClassificationComplianceReporter

# Create compliance reporter
reporter = ClassificationComplianceReporter()

# Generate compliance report
report = await reporter.generate_report(
    start_time=datetime(2026, 5, 1),
    end_time=datetime(2026, 5, 31),
    domain="finance"
)

# Get classification violations
violations = await reporter.get_violations(
    start_time=datetime(2026, 5, 1),
    end_time=datetime(2026, 5, 31)
)

# Get access patterns by classification
patterns = await reporter.get_access_patterns(
    classification=ClassificationLevel.CONFIDENTIAL,
    days=30
)
```

**Methods:**
- `generate_report(start_time, end_time, **kwargs)`: Generate compliance report
- `get_violations(start_time, end_time)`: Get classification violations
- `get_access_patterns(classification, days)`: Get access patterns
- `get_classification_distribution(domain)`: Get classification distribution

## 🚀 Best Practices

### ⭐ Use Classification Decorators

Always use the `@classification` decorator for tools that access sensitive data.

```python
# Good
@classification(ClassificationLevel.CONFIDENTIAL)
@requires_permission("finance.confidential")
def get_financial_reports():
    pass

# Bad - No classification
@requires_permission("finance.confidential")
def get_financial_reports():
    pass
```

### ⭐ Enforce Classification Checks

Always enforce classification checks before accessing data.

```python
# Good - Classification check enforced
@classification_check(ClassificationLevel.CONFIDENTIAL)
def get_confidential_data():
    pass

# Bad - No classification check
@classification(ClassificationLevel.CONFIDENTIAL)
def get_confidential_data():
    pass
```

### ⭐ Use Appropriate Classification Levels

Use the most appropriate classification level for your data.

```python
# Good - Appropriate levels
@classification(ClassificationLevel.PUBLIC)
def get_public_data():
    pass

@classification(ClassificationLevel.INTERNAL)
def get_internal_data():
    pass

@classification(ClassificationLevel.CONFIDENTIAL)
def get_confidential_data():
    pass

# Bad - Inappropriate levels
@classification(ClassificationLevel.STRICTLY_CONFIDENTIAL)
def get_public_data():
    pass
```

### ⭐ Implement Justification for High Classification

Require justification for accessing STRICTLY CONFIDENTIAL data.

```python
# Good - Justification required
@classification(
    ClassificationLevel.STRICTLY_CONFIDENTIAL,
    justification_required=True
)
def get_strictly_confidential_data():
    pass

# Bad - No justification
@classification(ClassificationLevel.STRICTLY_CONFIDENTIAL)
def get_strictly_confidential_data():
    pass
```

### ⭐ Audit Classification Access

Always audit access to classified data.

```python
# Good - Audit enabled
@classification(
    ClassificationLevel.CONFIDENTIAL,
    audit=True
)
def get_confidential_data():
    pass

# Bad - No audit
@classification(ClassificationLevel.CONFIDENTIAL)
def get_confidential_data():
    pass
```

### ⭐ Use Classification Inheritance

Leverage classification inheritance for domain policies.

```python
# Good - Inheritance used
policy = ClassificationPolicy()
policy.set_domain_default("finance", ClassificationLevel.CONFIDENTIAL)
policy.set_domain_max("finance", ClassificationLevel.STRICTLY_CONFIDENTIAL)

# Bad - No inheritance
# Each resource must be classified individually
```

## 🔍 Troubleshooting

### Common Issues

#### Classification Access Denied

**Error:** `ClassificationError: Access denied: CONFIDENTIAL classification required`

**Causes:**
- User doesn't have required classification level
- Classification not properly configured
- User's classification level too low

**Solutions:**
1. Check user's classification level: `service.get_user_classification(user)`
2. Verify required classification: `get_tool_classification(tool)`
3. Check classification configuration
4. Request classification upgrade if needed

```python
# Debug classification access
from platform.classification import ClassificationService

service = ClassificationService()

# Get user's classification
user_level = service.get_user_classification("john.doe@my-org.org")
print(f"User classification: {user_level}")

# Get tool's classification
tool_level = service.get_tool_classification("GetFinancialReports")
print(f"Tool classification: {tool_level}")

# Check access
can_access = service.can_access("john.doe@my-org.org", tool_level)
print(f"Can access: {can_access}")
```

#### Classification Not Enforced

**Symptoms:** Users can access data without proper classification checks

**Causes:**
- Classification decorators not applied
- Classification checks not implemented
- Classification service not initialized

**Solutions:**
1. Apply `@classification` decorator to tools
2. Use `@classification_check` for enforcement
3. Initialize classification service
4. Check framework integration

```python
# Debug classification enforcement
from platform.classification import ClassificationEnforcer

enforcer = ClassificationEnforcer()

# Check if enforcement is working
try:
    @enforcer.enforce_classification
    @classification(ClassificationLevel.CONFIDENTIAL)
    def test_tool():
        pass
    
    # This should work if user has CONFIDENTIAL access
    test_tool()
    print("Classification enforcement working")
except ClassificationError as e:
    print(f"Classification enforcement failed: {e}")
```

#### Classification Configuration Issues

**Symptoms:** Classification levels not working as expected

**Causes:**
- Configuration file missing or incorrect
- Classification levels not properly defined
- Policy store not configured

**Solutions:**
1. Check configuration: `CLASSIFICATION_CONFIG`
2. Verify classification levels are defined
3. Check policy store configuration
4. Validate configuration with schema

```python
# Debug classification configuration
from platform.classification import ClassificationConfig

config = ClassificationConfig()
print(f"Levels: {config.levels}")
print(f"Default: {config.default}")
print(f"Audit enabled: {config.audit.enabled}")
print(f"Audit levels: {config.audit.levels}")
```

## 📚 Examples

### Complete Classification Example

```python
from platform.auth import authenticated_tool, requires_permission
from platform.classification import (
    classification, 
    classification_check, 
    ClassificationLevel,
    get_caller_identity
)
from platform.audit import audit_log

@authenticated_tool
@requires_permission("finance.confidential")
@classification(ClassificationLevel.CONFIDENTIAL)
@classification_check(ClassificationLevel.CONFIDENTIAL)
@audit_log.sensitive_operation
@capture_tool_metrics
def get_financial_report(report_id: str):
    """Get financial report with comprehensive classification controls"""
    
    # Get caller information
    caller = get_caller_identity()
    
    # Get report classification
    report = await finance_service.get_report_metadata(report_id)
    report_classification = report.classification
    
    # Check if user can access this classification
    if not can_access_classification(caller.max_classification, report_classification):
        raise ClassificationError(
            error_code="CLASS-001",
            message=f"Access denied: {report_classification} classification required",
            details={
                "required_classification": report_classification,
                "user_classification": caller.max_classification
            }
        )
    
    # Get report data
    report_data = await finance_service.get_report(report_id)
    
    # Mask sensitive data if needed
    if report_classification >= ClassificationLevel.CONFIDENTIAL:
        report_data = mask_sensitive_data(report_data)
    
    return report_data
```

### Dynamic Classification Checking

```python
from platform.auth import authenticated_tool
from platform.classification import (
    ClassificationService,
    ClassificationLevel,
    get_caller_identity
)

@authenticated_tool
def get_resource_data(resource_id: str):
    """Get resource data with dynamic classification checking"""
    
    # Get caller information
    caller = get_caller_identity()
    
    # Get resource classification
    service = ClassificationService()
    resource_classification = service.get_classification(resource_id)
    
    # Check access
    if not service.can_access(caller.identity, resource_classification):
        raise ClassificationError(
            error_code="CLASS-001",
            message=f"Access denied to {resource_id}",
            details={
                "resource": resource_id,
                "required_classification": resource_classification,
                "user": caller.identity
            }
        )
    
    # Get resource data
    data = await resource_service.get(resource_id)
    
    return data
```

### Classification-Based Data Masking

```python
from platform.auth import authenticated_tool
from platform.classification import (
    classification,
    ClassificationLevel,
    DataMasker
)

@authenticated_tool
@classification(ClassificationLevel.CONFIDENTIAL)
def get_donor_data(donor_id: str):
    """Get donor data with classification-based masking"""
    
    # Get donor data
    donor = await donor_service.get(donor_id)
    
    # Get current classification from context
    current_classification = get_current_classification()
    
    # Mask data based on classification
    masker = DataMasker()
    
    if current_classification < ClassificationLevel.CONFIDENTIAL:
        # Mask sensitive fields for lower classification
        masked_donor = masker.mask(
            donor,
            mask_fields=["ssn", "email", "phone", "address"]
        )
        return masked_donor
    else:
        # Return full data for CONFIDENTIAL and above
        return donor
```

---

## 📖 API Reference

### Exceptions

| Exception | Description | Error Code |
|-----------|-------------|------------|
| `ClassificationError` | Base classification error | CLASS-001 |
| `ClassificationAccessDeniedError` | Access denied due to classification | CLASS-002 |
| `ClassificationConfigurationError` | Configuration error | CLASS-003 |
| `JustificationRequiredError` | Justification required | CLASS-004 |

### Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| CLASS-001 | Classification error | 403 |
| CLASS-002 | Access denied | 403 |
| CLASS-003 | Configuration error | 500 |
| CLASS-004 | Justification required | 403 |

---

*⭐ = Best Practice | 🔒 = Security Requirement | ⚡ = Performance Consideration*