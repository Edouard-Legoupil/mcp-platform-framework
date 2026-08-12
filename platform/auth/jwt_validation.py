"""
JWT Validation for Azure AD Tokens

Handles JWT token validation specifically for Azure AD tokens in Function App environment.
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from .models import TokenData, CallerIdentity, AuthenticationResult
from .exceptions import (
    TokenValidationError, 
    TokenExpiredError, 
    TokenNotYetValidError,
    InvalidSignatureError,
    InvalidIssuerError,
    InvalidAudienceError,
    InvalidTokenFormatError
)
import logging
import requests
import json
from functools import lru_cache

logger = logging.getLogger(__name__)


class AzureADJWTValidator:
    """JWT validator specifically for Azure AD tokens"""
    
    def __init__(self, 
                 tenant_id: str, 
                 client_id: str, 
                 audience: str = "api://default",
                 issuer: Optional[str] = None,
                 algorithms: List[str] = ["RS256"]):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.audience = audience
        self.issuer = issuer or f"https://login.microsoftonline.com/{tenant_id}/v2.0"
        self.algorithms = algorithms
        self._public_keys: Optional[Dict[str, str]] = None
        self._jwks_uri = f"https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys"
        
    @property
    @lru_cache(maxsize=1)
    def public_keys(self) -> Dict[str, str]:
        """Get Azure AD public keys with caching"""
        if self._public_keys is None:
            self._public_keys = self._fetch_public_keys()
        return self._public_keys
    
    def _fetch_public_keys(self) -> Dict[str, str]:
        """Fetch public keys from Azure AD"""
        try:
            response = requests.get(self._jwks_uri, timeout=10)
            response.raise_for_status()
            jwks = response.json()
            
            public_keys = {}
            for key in jwks.get("keys", []):
                if key.get("kty") == "RSA" and key.get("use") == "sig":
                    kid = key.get("kid")
                    if kid:
                        # Convert JWK to PEM format
                        public_key = self._jwk_to_pem(key)
                        public_keys[kid] = public_key
            
            logger.info(f"Fetched {len(public_keys)} public keys from Azure AD")
            return public_keys
            
        except Exception as e:
            logger.error(f"Failed to fetch public keys from Azure AD: {e}")
            raise TokenValidationError(f"Failed to fetch public keys: {e}")
    
    def _jwk_to_pem(self, jwk: Dict[str, Any]) -> str:
        """Convert JWK to PEM format"""
        try:
            # Use cryptography library to convert JWK to PEM
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.backends import default_backend
            import base64
            
            # Extract key components
            n = base64.urlsafe_b64decode(jwk["n"].encode() + b'==')
            e = base64.urlsafe_b64decode(jwk["e"].encode() + b'==')
            
            # Create RSA public key
            public_key = rsa.RSAPublicNumbers(e, n).public_key(default_backend())
            
            # Serialize to PEM
            pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            return pem.decode('utf-8')
            
        except ImportError:
            # Fallback for environments without cryptography
            logger.warning("cryptography library not available, using jwt library")
            # This is less secure but works for basic validation
            return jwt.algorithms.RSAAlgorithm.from_jwk(jwk)
        except Exception as e:
            logger.error(f"Failed to convert JWK to PEM: {e}")
            raise TokenValidationError(f"Failed to convert JWK to PEM: {e}")
    
    def validate_token(self, token: str) -> TokenData:
        """Validate Azure AD JWT token and return decoded payload"""
        if not token or not isinstance(token, str):
            raise InvalidTokenFormatError()
        
        try:
            # Get kid from header to select correct public key
            header = jwt.get_unverified_header(token)
            kid = header.get("kid")
            
            if not kid:
                raise InvalidTokenFormatError("Token header missing kid")
            
            # Get the public key for this kid
            public_keys = self.public_keys
            if kid not in public_keys:
                # Try to refresh public keys
                self._public_keys = None  # Clear cache
                public_keys = self.public_keys
                if kid not in public_keys:
                    raise TokenValidationError(f"Unknown key ID: {kid}")
            
            public_key = public_keys[kid]
            
            # Decode and validate the token
            payload = jwt.decode(
                token,
                public_key,
                algorithms=self.algorithms,
                audience=self.audience,
                issuer=self.issuer,
                options={
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_nbf": True,
                    "verify_aud": True,
                    "verify_iss": True
                }
            )
            
            # Convert datetime strings to datetime objects if needed
            if isinstance(payload.get("exp"), (int, float)):
                payload["exp"] = datetime.fromtimestamp(payload["exp"])
            if isinstance(payload.get("iat"), (int, float)):
                payload["iat"] = datetime.fromtimestamp(payload["iat"])
            if isinstance(payload.get("nbf"), (int, float)):
                payload["nbf"] = datetime.fromtimestamp(payload["nbf"])
            
            return TokenData(**payload)
            
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError()
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {e}")
            raise TokenValidationError(f"Invalid token: {e}")
        except jwt.InvalidSignatureError:
            raise InvalidSignatureError()
        except jwt.InvalidIssuerError:
            raise InvalidIssuerError()
        except jwt.InvalidAudienceError:
            raise InvalidAudienceError()
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            raise TokenValidationError(f"Token validation failed: {e}")
    
    def get_identity_from_token(self, token: str) -> CallerIdentity:
        """Extract caller identity from validated Azure AD token"""
        token_data = self.validate_token(token)
        
        # Extract Azure AD specific claims
        claims = {
            "roles": token_data.roles or [],
            "scopes": token_data.scopes or [],
            "groups": token_data.groups or [],
            "oid": token_data.oid,
            "tid": token_data.tid,
            "appid": token_data.appid,
            "preferred_username": token_data.preferred_username,
            "iss": token_data.iss,
            "aud": token_data.aud
        }
        
        # Remove standard JWT claims from custom claims
        standard_claims = ['exp', 'iat', 'nbf', 'iss', 'aud', 'sub', 'name', 'email', 
                         'oid', 'tid', 'appid', 'appidacr', 'azp', 'azpacr', 'roles', 'scopes', 'groups']
        for claim in standard_claims:
            if claim in token_data.custom_claims:
                del token_data.custom_claims[claim]
        
        claims["custom"] = token_data.custom_claims
        
        return CallerIdentity(
            user_id=token_data.sub or token_data.oid or "unknown",
            username=token_data.name or token_data.preferred_username,
            email=token_data.email,
            object_id=token_data.oid,
            tenant_id=token_data.tid,
            authentication_type="entra_id",
            is_authenticated=True,
            claims=claims,
            scopes=token_data.scopes or [],
            roles=token_data.roles or [],
            groups=token_data.groups or []
        )
    
    def clear_cache(self):
        """Clear the public keys cache"""
        self._public_keys = None
        self.public_keys.cache_clear()


# Global JWT validator instance (initialized by framework)
_jwt_validator: Optional[AzureADJWTValidator] = None


def get_jwt_validator() -> Optional[AzureADJWTValidator]:
    """Get the global JWT validator"""
    return _jwt_validator


def set_jwt_validator(validators: AzureADJWTValidator):
    """Set the global JWT validator"""
    global _jwt_validator
    _jwt_validator = validators


# Alias for backward compatibility
JWTValidator = AzureADJWTValidator
