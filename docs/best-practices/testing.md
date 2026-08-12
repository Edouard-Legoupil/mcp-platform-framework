# 🧪 Testing Strategies

Comprehensive testing approaches and best practices for MCP services, ensuring reliability, security, and performance.

## 🎯 Overview

Testing is essential for building robust MCP services that handle sensitive business data and integrate with critical systems. This guide provides strategies for:

- **Unit Testing**: Testing individual components in isolation
- **Integration Testing**: Testing interactions between components
- **Performance Testing**: Ensuring services meet performance requirements
- **Security Testing**: Identifying and addressing security vulnerabilities
- **End-to-End Testing**: Testing complete user journeys
- **Test Automation**: Automating test execution and reporting

## 🧩 Unit Testing Best Practices

### ✅ Test Individual Functions and Methods

**⭐ Best Practice**: Write unit tests for all public functions and methods.

```python
import pytest
from unittest.mock import AsyncMock, patch
from platform.auth import AuthenticationService

# Good: Unit test for authentication service
class TestAuthenticationService:
    @pytest.fixture
    def auth_service(self):
        return AuthenticationService()
    
    @pytest.mark.asyncio
    async def test_validate_token_success(self, auth_service):
        # Mock token validation
        with patch.object(auth_service, '_validate_jwt', new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = {"sub": "user123", "exp": 9999999999}
            
            result = await auth_service.validate_token("valid.token.here")
            
            assert result.is_valid
            assert result.claims["sub"] == "user123"
    
    @pytest.mark.asyncio
    async def test_validate_token_failure(self, auth_service):
        with patch.object(auth_service, '_validate_jwt', new_callable=AsyncMock) as mock_validate:
            mock_validate.side_effect = Exception("Invalid token")
            
            with pytest.raises(AuthenticationError) as exc_info:
                await auth_service.validate_token("invalid.token.here")
            
            assert exc_info.value.error_code == "AUTH_001"
```

### ✅ Use Mocking for External Dependencies

**⭐ Best Practice**: Mock external services and dependencies in unit tests.

```python
from unittest.mock import AsyncMock, patch
import pytest

# Good: Mocking external dependencies
class TestDonorService:
    @pytest.fixture
    def mock_fabric_client(self):
        with patch('platform.connectivity.FabricClient') as mock_client:
            mock_semantic_model = AsyncMock()
            mock_semantic_model.execute.return_value = {"rows": [{"donor_id": "123", "name": "Test Donor"}]}
            mock_client.return_value.get_semantic_model.return_value = mock_semantic_model
            yield mock_client
    
    @pytest.mark.asyncio
    async def test_get_donor_data(self, mock_fabric_client):
        from platform.services import DonorService
        
        service = DonorService()
        result = await service.get_donor("123")
        
        assert result["donor_id"] == "123"
        assert result["name"] == "Test Donor"
        mock_fabric_client.return_value.get_semantic_model.return_value.execute.assert_called_once()
```

### ✅ Test Edge Cases and Error Conditions

**⭐ Best Practice**: Test edge cases, invalid inputs, and error conditions.

```python
import pytest
from platform.authorization import AuthorizationService, AuthorizationError

# Good: Testing edge cases and error conditions
class TestAuthorizationService:
    @pytest.fixture
    def authz_service(self):
        config = AuthzConfig(
            role_permissions={
                "admin": ["*"]
            }
        )
        return AuthorizationService(config=config)
    
    def test_check_permission_with_valid_permission(self, authz_service):
        # Setup: User has admin role which has all permissions
        caller = CallerIdentity(username="admin", roles=["admin"])
        
        result = authz_service.check_permission("donor.read", caller)
        assert result is True
    
    def test_check_permission_without_permission(self, authz_service):
        # Setup: User has no roles
        caller = CallerIdentity(username="user", roles=[])
        
        result = authz_service.check_permission("donor.read", caller)
        assert result is False
    
    def test_check_permission_with_invalid_permission(self, authz_service):
        # Setup: User has admin role
        caller = CallerIdentity(username="admin", roles=["admin"])
        
        # Should still work with wildcard permission
        result = authz_service.check_permission("invalid.permission", caller)
        assert result is True
```

### ✅ Use Parameterized Tests

**⭐ Best Practice**: Use parameterized tests to test multiple scenarios with the same test logic.

```python
import pytest
from platform.classification import ClassificationService

# Good: Parameterized tests
@pytest.mark.parametrize("classification,expected_level", [
    ("PUBLIC", 0),
    ("INTERNAL", 1),
    ("CONFIDENTIAL", 2),
    ("STRICTLY_CONFIDENTIAL", 3)
])
def test_classification_levels(classification, expected_level):
    service = ClassificationService()
    level = service.get_classification_level(classification)
    assert level == expected_level

@pytest.mark.parametrize("input_value,expected_result", [
    ("valid@email.com", True),
    ("invalid-email", False),
    ("", False),
    (None, False)
])
def test_email_validation(input_value, expected_result):
    from platform.validation import validate_email
    result = validate_email(input_value)
    assert result == expected_result
```

### ✅ Test Asynchronous Code Properly

**⭐ Best Practice**: Use pytest-asyncio for testing async code.

```python
import pytest
from unittest.mock import AsyncMock, patch

# Good: Testing async code with pytest-asyncio
@pytest.mark.asyncio
async def test_async_tool_execution():
    from platform.telemetry import TelemetryService
    
    service = TelemetryService()
    
    with patch.object(service, 'track_tool_execution', new_callable=AsyncMock) as mock_track:
        await service.track_tool_execution(
            tool_name="TestTool",
            duration_ms=100.5,
            status="Success"
        )
        
        mock_track.assert_called_once_with(
            tool_name="TestTool",
            duration_ms=100.5,
            status="Success",
            success=True,
            metadata=None
        )
```

## 🔗 Integration Testing Best Practices

### ✅ Test Component Interactions

**⭐ Best Practice**: Test interactions between different components and modules.

```python
import pytest
from unittest.mock import AsyncMock, patch

# Good: Integration test for tool execution with decorators
@pytest.mark.asyncio
async def test_tool_with_decorators():
    from platform.auth import authenticated_tool
    from platform.authorization import requires_permission
    from platform.telemetry import track_tool_telemetry
    
    # Mock the dependencies
    with patch('platform.auth.get_caller_identity') as mock_caller, \
         patch('platform.authorization.AuthorizationService.check_permission') as mock_authz, \
         patch('platform.telemetry.TelemetryService.track_tool_execution') as mock_telemetry:
        
        mock_caller.return_value = CallerIdentity(username="testuser", roles=["admin"])
        mock_authz.return_value = True
        mock_telemetry.return_value = None
        
        @authenticated_tool
        @requires_permission("donor.read")
        @track_tool_telemetry
        async def get_donor_data(donor_id: str):
            return {"donor_id": donor_id, "name": "Test Donor"}
        
        result = await get_donor_data("123")
        
        assert result["donor_id"] == "123"
        mock_caller.assert_called_once()
        mock_authz.assert_called_once_with("donor.read", None)
        mock_telemetry.assert_called_once()
```

### ✅ Test Database Integration

**⭐ Best Practice**: Test database operations with real or test databases.

```python
import pytest
import asyncpg
from unittest.mock import AsyncMock, patch

# Good: Database integration test with mock
@pytest.mark.asyncio
async def test_database_operations():
    from platform.services import DonorService
    
    # Mock the database connection
    with patch('asyncpg.connect', new_callable=AsyncMock) as mock_connect:
        mock_conn = AsyncMock()
        mock_conn.fetchrow.return_value = {"donor_id": "123", "name": "Test Donor"}
        mock_connect.return_value = mock_conn
        
        service = DonorService()
        result = await service.get_donor_from_db("123")
        
        assert result["donor_id"] == "123"
        mock_conn.fetchrow.assert_called_once()

# For integration tests with real database (use test database)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_database_operations():
    # Setup test database connection
    conn = await asyncpg.connect(
        user="testuser",
        password="testpass",
        database="testdb",
        host="localhost"
    )
    
    try:
        # Create test data
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS test_donors (
                donor_id TEXT PRIMARY KEY,
                name TEXT
            )
        """)
        await conn.execute("INSERT INTO test_donors VALUES ('123', 'Test Donor')")
        
        # Test the operation
        result = await conn.fetchrow("SELECT * FROM test_donors WHERE donor_id = '123'")
        assert result["donor_id"] == "123"
        assert result["name"] == "Test Donor"
        
    finally:
        # Cleanup
        await conn.execute("DROP TABLE IF EXISTS test_donors")
        await conn.close()
```

### ✅ Test External Service Integration

**⭐ Best Practice**: Test integration with external services using mock servers or test environments.

```python
import pytest
from unittest.mock import AsyncMock, patch
import aiohttp

# Good: External service integration test
@pytest.mark.asyncio
async def test_external_service_integration():
    from platform.services import ExternalDataService
    
    # Mock the HTTP client
    with patch('aiohttp.ClientSession') as mock_session_class:
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.json.return_value = {"status": "success", "data": "test data"}
        mock_response.status = 200
        mock_session.get.return_value = mock_response
        mock_session_class.return_value.__aenter__.return_value = mock_session
        
        service = ExternalDataService()
        result = await service.fetch_external_data("test-id")
        
        assert result["status"] == "success"
        mock_session.get.assert_called_once()

# For testing with real external services (use test environments)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_external_service():
    # Use test environment URL
    service_url = "https://test-api.example.com"
    
    async with aiohttp.ClientSession() as session:
        response = await session.get(f"{service_url}/test-endpoint")
        assert response.status == 200
        data = await response.json()
        assert "status" in data
```

## ⚡ Performance Testing Best Practices

### ✅ Test Performance Under Load

**⭐ Best Practice**: Use load testing tools to test performance under realistic conditions.

```python
import pytest
import time
import asyncio

# Good: Simple performance test
@pytest.mark.performance
@pytest.mark.asyncio
async def test_tool_performance():
    from platform.services import DonorService
    
    service = DonorService()
    
    # Warm up
    await service.get_donor("123")
    
    # Measure performance
    start_time = time.time()
    for _ in range(100):  # Test with 100 iterations
        await service.get_donor("123")
    end_time = time.time()
    
    duration = end_time - start_time
    avg_duration = duration / 100
    
    # Assert performance requirements
    assert avg_duration < 0.1  # Should be under 100ms per call
    print(f"Average duration: {avg_duration:.4f}s")

# Use pytest-benchmark for more sophisticated performance testing
@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_tool_performance_benchmark(benchmark):
    from platform.services import DonorService
    
    service = DonorService()
    
    # Benchmark the function
    result = await benchmark(service.get_donor, "123")
    
    assert result["donor_id"] == "123"
```

### ✅ Test Concurrent Operations

**⭐ Best Practice**: Test how your service performs under concurrent load.

```python
import pytest
import asyncio
import time

# Good: Concurrent operations test
@pytest.mark.performance
@pytest.mark.asyncio
async def test_concurrent_operations():
    from platform.services import DonorService
    
    service = DonorService()
    
    async def fetch_donor(donor_id: str):
        return await service.get_donor(donor_id)
    
    # Test with 50 concurrent requests
    donor_ids = [f"donor_{i}" for i in range(50)]
    
    start_time = time.time()
    results = await asyncio.gather(*[fetch_donor(donor_id) for donor_id in donor_ids])
    end_time = time.time()
    
    duration = end_time - start_time
    
    # Assert all requests completed successfully
    assert len(results) == 50
    assert all(result is not None for result in results)
    
    # Assert performance requirement (all 50 requests should complete in under 1 second)
    assert duration < 1.0
    print(f"50 concurrent requests completed in {duration:.4f}s")
```

### ✅ Test Memory Usage

**⭐ Best Practice**: Test memory usage, especially for operations that process large datasets.

```python
import pytest
import tracemalloc

# Good: Memory usage test
@pytest.mark.performance
def test_memory_usage():
    from platform.services import DataProcessingService
    
    service = DataProcessingService()
    
    # Start memory tracking
    tracemalloc.start()
    
    # Get initial memory usage
    snapshot1 = tracemalloc.take_snapshot()
    
    # Process data
    large_dataset = [{"id": i, "data": f"data_{i}"} for i in range(10000)]
    result = service.process_large_dataset(large_dataset)
    
    # Get final memory usage
    snapshot2 = tracemalloc.take_snapshot()
    
    # Calculate memory difference
    top_stats = snapshot2.compare_to(snapshot1, 'lineno')
    total_memory = sum(stat.size_diff for stat in top_stats)
    
    # Convert to MB
    memory_mb = total_memory / (1024 * 1024)
    
    # Assert memory usage is reasonable
    assert memory_mb < 100  # Should use less than 100MB
    print(f"Memory usage: {memory_mb:.2f}MB")
    
    tracemalloc.stop()
```

## 🔒 Security Testing Best Practices

### ✅ Test Authentication and Authorization

**⭐ Best Practice**: Thoroughly test authentication and authorization mechanisms.

```python
import pytest
from unittest.mock import AsyncMock, patch
from platform.auth import AuthenticationService, AuthenticationError
from platform.authorization import AuthorizationService, AuthorizationError

# Good: Authentication and authorization testing
class TestSecurity:
    @pytest.mark.asyncio
    async def test_authentication_required(self):
        from platform.auth import authenticated_tool
        
        @authenticated_tool
        async def protected_tool():
            return "success"
        
        # Test without authentication
        with patch('platform.auth.get_caller_identity') as mock_caller:
            mock_caller.side_effect = AuthenticationError("AUTH_004", "Missing token")
            
            with pytest.raises(AuthenticationError):
                await protected_tool()
    
    @pytest.mark.asyncio
    async def test_authorization_required(self):
        from platform.authorization import requires_permission
        
        @requires_permission("donor.read")
        async def protected_tool():
            return "success"
        
        # Test without required permission
        with patch('platform.authorization.AuthorizationService.check_permission') as mock_check:
            mock_check.return_value = False
            
            with pytest.raises(AuthorizationError):
                await protected_tool()
    
    @pytest.mark.asyncio
    async def test_authorization_with_permission(self):
        from platform.authorization import requires_permission
        
        @requires_permission("donor.read")
        async def protected_tool():
            return "success"
        
        # Test with required permission
        with patch('platform.authorization.AuthorizationService.check_permission') as mock_check:
            mock_check.return_value = True
            
            result = await protected_tool()
            assert result == "success"
```

### ✅ Test Input Validation

**⭐ Best Practice**: Test that all inputs are properly validated.

```python
import pytest
from platform.validation import ValidationError

# Good: Input validation testing
class TestInputValidation:
    def test_valid_input(self):
        from platform.services import DonorService
        
        service = DonorService()
        
        # Test with valid input
        result = service.validate_donor_data({
            "donor_id": "123",
            "name": "Test Donor",
            "email": "test@example.com",
            "contribution": 1000.0
        })
        
        assert result is True
    
    def test_invalid_email(self):
        from platform.services import DonorService
        
        service = DonorService()
        
        # Test with invalid email
        with pytest.raises(ValidationError) as exc_info:
            service.validate_donor_data({
                "donor_id": "123",
                "name": "Test Donor",
                "email": "invalid-email",
                "contribution": 1000.0
            })
        
        assert exc_info.value.error_code == "VAL_003"
        assert exc_info.value.field == "email"
    
    def test_missing_required_field(self):
        from platform.services import DonorService
        
        service = DonorService()
        
        # Test with missing required field
        with pytest.raises(ValidationError) as exc_info:
            service.validate_donor_data({
                "donor_id": "123",
                "name": "Test Donor",
                # Missing email
                "contribution": 1000.0
            })
        
        assert exc_info.value.error_code == "VAL_002"
        assert exc_info.value.field == "email"
```

### ✅ Test Data Classification Enforcement

**⭐ Best Practice**: Test that data classification controls are properly enforced.

```python
import pytest
from platform.classification import ClassificationError

# Good: Data classification testing
class TestDataClassification:
    def test_classification_enforcement(self):
        from platform.classification import classification
        
        @classification("CONFIDENTIAL", enforce=True)
        async def confidential_tool():
            return "confidential data"
        
        # Test with proper classification
        result = confidential_tool()
        assert result == "confidential data"
    
    def test_classification_violation(self):
        from platform.classification import classify_data
        
        @classify_data(ssn="STRICTLY_CONFIDENTIAL")
        async def process_sensitive_data(data: dict):
            if "ssn" in data:
                raise ClassificationError("STRICTLY_CONFIDENTIAL", "SSN requires higher clearance")
            return "processed"
        
        # Test with sensitive data
        with pytest.raises(ClassificationError):
            process_sensitive_data({"ssn": "123-45-6789"})
```

### ✅ Test Security Headers and CORS

**⭐ Best Practice**: Test that security headers and CORS policies are properly configured.

```python
import pytest
from unittest.mock import AsyncMock, patch

# Good: Security headers testing
@pytest.mark.asyncio
async def test_security_headers():
    from platform.web import create_app
    
    app = create_app()
    
    # Test security headers
    with patch('platform.web.setup_security_headers') as mock_security:
        client = app.test_client()
        
        response = await client.get("/api/health")
        
        # Check security headers
        assert "Strict-Transport-Security" in response.headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "Content-Security-Policy" in response.headers
```

## 🎯 End-to-End Testing Best Practices

### ✅ Test Complete User Journeys

**⭐ Best Practice**: Test complete user journeys from authentication to final result.

```python
import pytest
from unittest.mock import AsyncMock, patch

# Good: End-to-end test
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_complete_user_journey():
    from platform.web import create_app
    
    app = create_app()
    client = app.test_client()
    
    # Mock authentication
    with patch('platform.auth.authenticate_request') as mock_auth:
        mock_auth.return_value = CallerIdentity(username="testuser", roles=["admin"])
        
        # Step 1: Authenticate
        auth_response = await client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "testpass"
        })
        assert auth_response.status_code == 200
        
        # Step 2: Get donor list
        donors_response = await client.get("/api/donors")
        assert donors_response.status_code == 200
        donors = await donors_response.json()
        assert isinstance(donors, list)
        
        # Step 3: Get specific donor
        if donors:
            donor_id = donors[0]["donor_id"]
            donor_response = await client.get(f"/api/donors/{donor_id}")
            assert donor_response.status_code == 200
            donor = await donor_response.json()
            assert donor["donor_id"] == donor_id
```

### ✅ Test Error Scenarios End-to-End

**⭐ Best Practice**: Test how the system handles errors from end-to-end.

```python
import pytest
from unittest.mock import AsyncMock, patch

# Good: End-to-end error scenario testing
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_error_scenarios():
    from platform.web import create_app
    
    app = create_app()
    client = app.test_client()
    
    # Test 404 for non-existent donor
    response = await client.get("/api/donors/nonexistent")
    assert response.status_code == 404
    error_data = await response.json()
    assert error_data["error"] == "NOT_FOUND"
    
    # Test 401 for unauthorized access
    with patch('platform.auth.authenticate_request') as mock_auth:
        mock_auth.side_effect = AuthenticationError("AUTH_004", "Missing token")
        
        response = await client.get("/api/donors")
        assert response.status_code == 401
        error_data = await response.json()
        assert error_data["error"] == "AUTH_004"
    
    # Test 403 for forbidden access
    with patch('platform.auth.authenticate_request') as mock_auth, \
         patch('platform.authorization.AuthorizationService.check_permission') as mock_authz:
        
        mock_auth.return_value = CallerIdentity(username="user", roles=[])
        mock_authz.return_value = False
        
        response = await client.get("/api/donors")
        assert response.status_code == 403
        error_data = await response.json()
        assert error_data["error"] == "AUTHZ_001"
```

## 🤖 Test Automation Best Practices

### ✅ Automate Test Execution

**⭐ Best Practice**: Set up automated test execution in your CI/CD pipeline.

```yaml
# Good: GitHub Actions workflow for automated testing
# .github/workflows/test.yml

name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov
    
    - name: Run unit tests
      run: |
        pytest tests/unit/ --cov=platform --cov-report=xml
    
    - name: Run integration tests
      run: |
        pytest tests/integration/ --cov=platform --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        token: ${{ secrets.CODECOV_TOKEN }}
        file: ./coverage.xml
```

### ✅ Use Test Coverage Tools

**⭐ Best Practice**: Use coverage tools to measure and improve test coverage.

```python
# Good: Coverage configuration
# pytest.ini

[pytest]
addopts = --cov=platform --cov-report=term-missing --cov-report=html

# .coveragerc
[run]
source = platform
omit = 
    */tests/*
    */__pycache__/*
    */site-packages/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if __name__ == .__main__.:

[html]
directory = htmlcov
```

### ✅ Generate Test Reports

**⭐ Best Practice**: Generate comprehensive test reports for analysis.

```yaml
# Good: Test reporting configuration
# In your CI/CD pipeline

- name: Generate test report
  run: |
    pytest tests/ --junitxml=test-results.xml --html=test-report.html --self-contained-html
    
- name: Upload test results
  uses: actions/upload-artifact@v3
  with:
    name: test-results
    path: |
      test-results.xml
      test-report.html
```

### ✅ Fail Fast on Test Failures

**⭐ Best Practice**: Configure tests to fail fast on the first failure.

```python
# Good: Fail fast configuration
# pytest.ini

[pytest]
addopts = -x  # Stop after first failure
```

## 📊 Test Organization Best Practices

### ✅ Organize Tests by Type and Component

**⭐ Best Practice**: Organize tests in a clear, logical structure.

```
tests/
├── unit/                    # Unit tests
│   ├── auth/               # Authentication tests
│   │   ├── test_service.py
│   │   └── test_decorators.py
│   ├── authorization/      # Authorization tests
│   │   └── test_service.py
│   ├── telemetry/          # Telemetry tests
│   │   └── test_service.py
│   └── ...
├── integration/            # Integration tests
│   ├── fabric/             # Fabric integration tests
│   │   └── test_connectivity.py
│   ├── database/           # Database integration tests
│   │   └── test_operations.py
│   └── ...
├── performance/            # Performance tests
│   ├── test_load.py
│   ├── test_concurrency.py
│   └── test_memory.py
├── security/               # Security tests
│   ├── test_auth.py
│   ├── test_validation.py
│   └── test_classification.py
├── e2e/                    # End-to-end tests
│   ├── test_user_journeys.py
│   └── test_error_scenarios.py
└── conftest.py             # Shared fixtures and configuration
```

### ✅ Use Shared Fixtures

**⭐ Best Practice**: Use shared fixtures for common test setup.

```python
import pytest
from unittest.mock import AsyncMock, patch

# Good: Shared fixtures in conftest.py
@pytest.fixture
def mock_fabric_client():
    with patch('platform.connectivity.FabricClient') as mock_client:
        mock_semantic_model = AsyncMock()
        mock_semantic_model.execute.return_value = {"rows": []}
        mock_client.return_value.get_semantic_model.return_value = mock_semantic_model
        yield mock_client

@pytest.fixture
def mock_auth_service():
    with patch('platform.auth.AuthenticationService') as mock_service:
        mock_service.return_value.validate_token.return_value = TokenValidationResult(
            claims={"sub": "testuser", "roles": ["admin"]},
            is_valid=True
        )
        yield mock_service

@pytest.fixture
def test_donor_data():
    return {
        "donor_id": "123",
        "name": "Test Donor",
        "email": "test@example.com",
        "contribution": 1000.0,
        "status": "active"
    }
```

### ✅ Use Test Data Builders

**⭐ Best Practice**: Use builder patterns for creating test data.

```python
from dataclasses import dataclass
from typing import Optional

# Good: Test data builder
@dataclass
class DonorBuilder:
    donor_id: str = "123"
    name: str = "Test Donor"
    email: str = "test@example.com"
    contribution: float = 1000.0
    status: str = "active"
    classification: str = "CONFIDENTIAL"
    
    def with_donor_id(self, donor_id: str) -> "DonorBuilder":
        self.donor_id = donor_id
        return self
    
    def with_name(self, name: str) -> "DonorBuilder":
        self.name = name
        return self
    
    def with_email(self, email: str) -> "DonorBuilder":
        self.email = email
        return self
    
    def with_status(self, status: str) -> "DonorBuilder":
        self.status = status
        return self
    
    def build(self) -> dict:
        return {
            "donor_id": self.donor_id,
            "name": self.name,
            "email": self.email,
            "contribution": self.contribution,
            "status": self.status,
            "classification": self.classification
        }

# Usage in tests
def test_donor_service():
    donor = DonorBuilder().with_donor_id("456").with_name("Special Donor").build()
    
    # Test with the donor data
    result = donor_service.process_donor(donor)
    assert result["donor_id"] == "456"
```

## 📋 Testing Checklist

### ✅ Pre-Deployment Testing Checklist

- [ ] Unit tests cover all public functions and methods
- [ ] Integration tests cover all component interactions
- [ ] Performance tests verify performance requirements
- [ ] Security tests verify authentication, authorization, and validation
- [ ] End-to-end tests cover complete user journeys
- [ ] Test coverage meets minimum requirements (e.g., 80%)
- [ ] All tests pass in the CI/CD pipeline
- [ ] Test reports are generated and reviewed
- [ ] Performance benchmarks are established
- [ ] Security vulnerabilities are identified and addressed

### ✅ Runtime Testing Checklist

- [ ] Tests are executed automatically on code changes
- [ ] Test failures are investigated and fixed promptly
- [ ] Performance is monitored against established benchmarks
- [ ] Security tests are run regularly
- [ ] Test coverage is maintained as code evolves
- [ ] Integration tests verify external service compatibility

## 🚨 Common Testing Pitfalls

### ❌ Testing Implementation Details

**Problem**: Testing implementation details that may change.

**Solution**: Test behavior, not implementation.

```python
# Bad: Testing implementation details
def test_service_implementation():
    service = DonorService()
    # Testing that the service uses a specific method
    assert service._internal_method == expected_method  # Implementation detail

# Good: Testing behavior
def test_service_behavior():
    service = DonorService()
    result = service.get_donor("123")
    assert result["donor_id"] == "123"  # Testing behavior
```

### ❌ Slow Tests

**Problem**: Tests that take too long to run.

**Solution**: Optimize tests and use appropriate test types.

```python
# Bad: Slow test that hits real database
@pytest.mark.asyncio
async def test_slow_database_operation():
    # This test takes 10 seconds to run
    result = await real_database.query("SELECT * FROM large_table")
    assert len(result) > 0

# Good: Fast test with mock
@pytest.mark.asyncio
async def test_database_operation():
    with patch('database.query', new_callable=AsyncMock) as mock_query:
        mock_query.return_value = [{"id": 1}]
        result = await database.query("SELECT * FROM table")
        assert len(result) == 1
```

### ❌ Flaky Tests

**Problem**: Tests that pass or fail inconsistently.

**Solution**: Identify and fix flaky tests.

```python
# Bad: Flaky test that depends on timing
@pytest.mark.asyncio
async def test_flaky_timing():
    start = time.time()
    await some_async_operation()
    duration = time.time() - start
    assert duration < 0.1  # Might fail due to system load

# Good: More robust test
@pytest.mark.asyncio
async def test_timing_with_tolerance():
    start = time.time()
    await some_async_operation()
    duration = time.time() - start
    assert duration < 0.5  # More tolerant threshold
```

### ❌ Tests That Depend on Each Other

**Problem**: Tests that depend on the state or results of other tests.

**Solution**: Make tests independent and isolated.

```python
# Bad: Tests that depend on each other
class TestDonorOperations:
    def test_create_donor(self):
        donor_id = donor_service.create_donor({"name": "Test"})
        self.donor_id = donor_id  # Storing state for next test
    
    def test_get_donor(self):
        donor = donor_service.get_donor(self.donor_id)  # Depends on previous test
        assert donor["name"] == "Test"

# Good: Independent tests
class TestDonorOperations:
    def test_create_donor(self):
        donor_id = donor_service.create_donor({"name": "Test"})
        assert donor_id is not None
        
        # Clean up
        donor_service.delete_donor(donor_id)
    
    def test_get_donor(self):
        # Create donor in this test
        donor_id = donor_service.create_donor({"name": "Test"})
        
        try:
            donor = donor_service.get_donor(donor_id)
            assert donor["name"] == "Test"
        finally:
            # Clean up
            donor_service.delete_donor(donor_id)
```

### ❌ No Test Cleanup

**Problem**: Tests that leave data or state behind.

**Solution**: Always clean up after tests.

```python
# Bad: No cleanup
@pytest.mark.asyncio
async def test_create_donor():
    donor_id = await donor_service.create_donor({"name": "Test"})
    assert donor_id is not None
    # No cleanup - leaves test data in database

# Good: Proper cleanup
@pytest.mark.asyncio
async def test_create_donor():
    donor_id = await donor_service.create_donor({"name": "Test"})
    try:
        assert donor_id is not None
    finally:
        # Clean up
        await donor_service.delete_donor(donor_id)

# Better: Use fixture for cleanup
@pytest.fixture
async def test_donor():
    donor_id = await donor_service.create_donor({"name": "Test"})
    yield donor_id
    await donor_service.delete_donor(donor_id)

@pytest.mark.asyncio
async def test_donor_operations(test_donor):
    donor = await donor_service.get_donor(test_donor)
    assert donor["name"] == "Test"
```

## 📚 Related Documentation

- [Testing Framework Module](../modules/) - Testing capabilities
- [Telemetry API](../api-reference/telemetry.md) - Telemetry for test monitoring
- [CI/CD Pipeline Documentation](../deployment/) - CI/CD setup
- [Security Best Practices](security.md) - Security testing guidelines
- [Performance Best Practices](performance.md) - Performance testing guidelines

---

**🎉 Ready to implement comprehensive testing?** Use these testing strategies to build reliable, high-quality MCP services.

**Need more details?** Check the Testing Framework Module documentation for implementation details and advanced testing patterns.