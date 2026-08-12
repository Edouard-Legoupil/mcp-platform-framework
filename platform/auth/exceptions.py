"""
Authentication Exceptions for Azure Environment
"""

class AuthenticationError(Exception):
    """Base authentication exception"""
    def __init__(self, message: str, error_code: str = "AUTH-001"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class TokenValidationError(AuthenticationError):
    """JWT token validation failed"""
    def __init__(self, message: str, error_code: str = "AUTH-002", details: dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class TokenExpiredError(AuthenticationError):
    """Token has expired"""
    def __init__(self, message: str = "Token has expired", error_code: str = "AUTH-003"):
        super().__init__(message, error_code)


class TokenNotYetValidError(AuthenticationError):
    """Token is not yet valid (nbf claim)"""
    def __init__(self, message: str = "Token is not yet valid", error_code: str = "AUTH-004"):
        super().__init__(message, error_code)


class InvalidSignatureError(AuthenticationError):
    """Token signature is invalid"""
    def __init__(self, message: str = "Invalid token signature", error_code: str = "AUTH-005"):
        super().__init__(message, error_code)


class InvalidIssuerError(AuthenticationError):
    """Token issuer is invalid"""
    def __init__(self, message: str = "Invalid token issuer", error_code: str = "AUTH-006"):
        super().__init__(message, error_code)


class InvalidAudienceError(AuthenticationError):
    """Token audience is invalid"""
    def __init__(self, message: str = "Invalid token audience", error_code: str = "AUTH-007"):
        super().__init__(message, error_code)


class InsufficientPermissionsError(AuthenticationError):
    """User lacks required permissions"""
    def __init__(self, required_permission: str, error_code: str = "AUTH-008"):
        self.required_permission = required_permission
        message = f"Insufficient permissions. Required: {required_permission}"
        super().__init__(message, error_code)


class InvalidTokenFormatError(AuthenticationError):
    """Token format is invalid"""
    def __init__(self, message: str = "Invalid token format", error_code: str = "AUTH-009"):
        super().__init__(message, error_code)


class ManagedIdentityError(AuthenticationError):
    """Managed Identity authentication failed"""
    def __init__(self, message: str = "Managed Identity authentication failed", error_code: str = "AUTH-010"):
        super().__init__(message, error_code)


class AzureADError(AuthenticationError):
    """Azure AD authentication failed"""
    def __init__(self, message: str = "Azure AD authentication failed", error_code: str = "AUTH-011"):
        super().__init__(message, error_code)
