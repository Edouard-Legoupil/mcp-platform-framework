"""Unit Tests for Authentication Module"""
import pytest
import json
import base64
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from platform.auth.models import (
    TokenClaims, 
    Identity, 
    AuthenticationResult,
    TokenType
)
from platform.auth.exceptions import (
    AuthenticationError, 
    TokenValidationError,
    TokenExpiredError,
    InvalidTokenError
)
from platform.auth.jwt_validation import JWTValidator
from platform.auth.entra_id import EntraIDAuthenticator
from platform.auth.managed_identity import ManagedIdentityAuthenticator
from platform.auth.decorators import authenticated_tool, requires_permission, requires_role


class TestTokenClaims:
    """Tests for TokenClaims model"""
    
    def test_token_claims_creation(self):
        """Test creating token claims"""
        claims = TokenClaims(
            iss="https://login.microsoftonline.com/tenant-id/v2.0",
            sub="user-id",
            aud="client-id",
            exp=datetime.utcnow() + timedelta(hours=1),
            iat=datetime.utcnow(),
            nbf=datetime.utcnow(),
            jti="token-id",
            name="User Name",
            preferred_username="user@example.com",
            oid="object-id",
            tid="tenant-id",
            roles=["User"],
            scopes=["api://default/.default"]
        )
        
        assert claims.iss == "https://login.microsoftonline.com/tenant-id/v2.0"
        assert claims.sub == "user-id"
        assert claims.aud == "client-id"
        assert claims.name == "User Name"
        assert claims.preferred_username == "user@example.com"
        assert claims.roles == ["User"]
        assert claims.scopes == ["api://default/.default"]
    
    def test_token_claims_is_expired(self):
        """Test token expiration check"""
        # Expired token
        expired_claims = TokenClaims(
            exp=datetime.utcnow() - timedelta(hours=1)
        )
        assert expired_claims.is_expired()
        
        # Valid token
        valid_claims = TokenClaims(
            exp=datetime.utcnow() + timedelta(hours=1)
        )
        assert not valid_claims.is_expired()
    
    def test_token_claims_is_not_before(self):
        """Test token not before check"""
        # Token not yet valid
        future_claims = TokenClaims(
            nbf=datetime.utcnow() + timedelta(hours=1)
        )
        assert future_claims.is_not_before()
        
        # Valid token
        valid_claims = TokenClaims(
            nbf=datetime.utcnow() - timedelta(hours=1)
        )
        assert not valid_claims.is_not_before()


class TestIdentity:
    """Tests for Identity model"""
    
    def test_identity_creation(self):
        """Test creating identity"""
        identity = Identity(
            user_id="user@example.com",
            name="User Name",
            object_id="object-id",
            tenant_id="tenant-id",
            client_id="client-id",
            roles=["User"],
            permissions=["read", "write"],
            token_type=TokenType.BEARER,
            access_token="token",
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        
        assert identity.user_id == "user@example.com"
        assert identity.name == "User Name"
        assert identity.tenant_id == "tenant-id"
        assert identity.roles == ["User"]
        assert identity.permissions == ["read", "write"]
    
    def test_identity_is_authenticated(self):
        """Test authentication check"""
        # Authenticated identity
        auth_identity = Identity(user_id="user@example.com")
        assert auth_identity.is_authenticated()
        
        # Unauthenticated identity
        unauth_identity = Identity(user_id="")
        assert not unauth_identity.is_authenticated()
    
    def test_identity_has_role(self):
        """Test role check"""
        identity = Identity(roles=["User", "Admin"])
        
        assert identity.has_role("User")
        assert identity.has_role("Admin")
        assert not identity.has_role("Guest")
    
    def test_identity_has_permission(self):
        """Test permission check"""
        identity = Identity(permissions=["read", "write"])
        
        assert identity.has_permission("read")
        assert identity.has_permission("write")
        assert not identity.has_permission("delete")


class TestAuthenticationResult:
    """Tests for AuthenticationResult model"""
    
    def test_authentication_result_success(self):
        """Test successful authentication result"""
        identity = Identity(user_id="user@example.com")
        result = AuthenticationResult(
            success=True,
            identity=identity,
            error=None
        )
        
        assert result.success
        assert result.identity == identity
        assert result.error is None
    
    def test_authentication_result_failure(self):
        """Test failed authentication result"""
        result = AuthenticationResult(
            success=False,
            identity=None,
            error="Invalid token"
        )
        
        assert not result.success
        assert result.identity is None
        assert result.error == "Invalid token"


class TestJWTValidator:
    """Tests for JWTValidator"""
    
    def test_jwt_validator_initialization(self):
        """Test JWTValidator initialization"""
        validator = JWTValidator(
            tenant_id="tenant-id",
            client_id="client-id",
            issuer="https://login.microsoftonline.com/tenant-id/v2.0"
        )
        
        assert validator.tenant_id == "tenant-id"
        assert validator.client_id == "client-id"
        assert validator.issuer == "https://login.microsoftonline.com/tenant-id/v2.0"
    
    @patch('platform.auth.jwt_validation.JWTValidator._get_public_keys')
    def test_validate_token_success(self, mock_get_public_keys):
        """Test successful token validation"""
        # Mock public keys
        mock_public_key = MagicMock()
        mock_public_key.verify.return_value = True
        mock_get_public_keys.return_value = [mock_public_key]
        
        validator = JWTValidator(
            tenant_id="tenant-id",
            client_id="client-id",
            issuer="https://login.microsoftonline.com/tenant-id/v2.0"
        )
        
        # Create a mock token
        token = "header.payload.signature"
        
        # Mock the decode and verify
        with patch('platform.auth.jwt_validation.jwt.decode') as mock_decode:
            mock_decode.return_value = {
                "iss": "https://login.microsoftonline.com/tenant-id/v2.0",
                "sub": "user-id",
                "aud": "client-id",
                "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp(),
                "iat": datetime.utcnow().timestamp(),
                "nbf": datetime.utcnow().timestamp()
            }
            
            result = validator.validate_token(token)
            
            assert result.success
            assert result.claims is not None
    
    @patch('platform.auth.jwt_validation.JWTValidator._get_public_keys')
    def test_validate_token_expired(self, mock_get_public_keys):
        """Test validation of expired token"""
        mock_public_key = MagicMock()
        mock_get_public_keys.return_value = [mock_public_key]
        
        validator = JWTValidator(
            tenant_id="tenant-id",
            client_id="client-id",
            issuer="https://login.microsoftonline.com/tenant-id/v2.0"
        )
        
        with patch('platform.auth.jwt_validation.jwt.decode') as mock_decode:
            mock_decode.return_value = {
                "iss": "https://login.microsoftonline.com/tenant-id/v2.0",
                "sub": "user-id",
                "aud": "client-id",
                "exp": (datetime.utcnow() - timedelta(hours=1)).timestamp(),  # Expired
                "iat": datetime.utcnow().timestamp(),
                "nbf": datetime.utcnow().timestamp()
            }
            
            result = validator.validate_token("token")
            
            assert not result.success
            assert isinstance(result.error, TokenExpiredError)


class TestEntraIDAuthenticator:
    """Tests for EntraIDAuthenticator"""
    
    def test_entra_id_authenticator_initialization(self):
        """Test EntraIDAuthenticator initialization"""
        authenticator = EntraIDAuthenticator(
            tenant_id="tenant-id",
            client_id="client-id",
            client_secret="client-secret"
        )
        
        assert authenticator.tenant_id == "tenant-id"
        assert authenticator.client_id == "client-id"
    
    @patch('platform.auth.entra_id.EntraIDAuthenticator._get_token')
    def test_authenticate_success(self, mock_get_token):
        """Test successful authentication"""
        mock_token = "access-token"
        mock_get_token.return_value = mock_token
        
        authenticator = EntraIDAuthenticator(
            tenant_id="tenant-id",
            client_id="client-id",
            client_secret="client-secret"
        )
        
        with patch('platform.auth.entra_id.EntraIDAuthenticator._validate_token') as mock_validate:
            mock_validate.return_value = AuthenticationResult(
                success=True,
                identity=Identity(user_id="user@example.com"),
                error=None
            )
            
            result = authenticator.authenticate(mock_token)
            
            assert result.success
            assert result.identity.user_id == "user@example.com"


class TestManagedIdentityAuthenticator:
    """Tests for ManagedIdentityAuthenticator"""
    
    def test_managed_identity_authenticator_initialization(self):
        """Test ManagedIdentityAuthenticator initialization"""
        authenticator = ManagedIdentityAuthenticator(
            client_id="client-id"
        )
        
        assert authenticator.client_id == "client-id"


class TestDecorators:
    """Tests for authentication decorators"""
    
    def test_authenticated_tool_decorator(self):
        """Test @authenticated_tool decorator"""
        @authenticated_tool
        def test_tool():
            return "success"
        
        # The decorator should add metadata to the function
        assert hasattr(test_tool, '_requires_authentication')
        assert test_tool._requires_authentication is True
    
    def test_requires_permission_decorator(self):
        """Test @requires_permission decorator"""
        @requires_permission("read")
        def test_tool():
            return "success"
        
        assert hasattr(test_tool, '_required_permissions')
        assert "read" in test_tool._required_permissions
    
    def test_requires_role_decorator(self):
        """Test @requires_role decorator"""
        @requires_role("Admin")
        def test_tool():
            return "success"
        
        assert hasattr(test_tool, '_required_roles')
        assert "Admin" in test_tool._required_roles


if __name__ == "__main__":
    pytest.main([__file__, "-v"])