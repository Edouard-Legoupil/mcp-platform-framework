"""
Exceptions for Documentation Generator Module
"""


class DocumentationError(Exception):
    """Base exception for documentation errors."""
    
    def __init__(self, message: str = "Documentation error", details: str = None):
        """
        Initialize DocumentationError.
        
        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details
        self.error_code = "DOCS-000"
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - {self.details}"
        return self.message


class DocumentationGenerationError(DocumentationError):
    """Exception for documentation generation failures."""
    
    def __init__(self, message: str = "Documentation generation failed", details: str = None):
        super().__init__(message, details)
        self.error_code = "DOCS-001"


class DocumentationTemplateError(DocumentationError):
    """Exception for template-related errors."""
    
    def __init__(self, message: str = "Documentation template error", template_name: str = None, details: str = None):
        if template_name:
            message = f"Template error in '{template_name}': {message}"
        super().__init__(message, details)
        self.template_name = template_name
        self.error_code = "DOCS-002"


class DocumentationValidationError(DocumentationError):
    """Exception for validation errors in documentation generation."""
    
    def __init__(self, message: str = "Documentation validation failed", field: str = None, details: str = None):
        if field:
            message = f"Validation failed for field '{field}': {message}"
        super().__init__(message, details)
        self.field = field
        self.error_code = "DOCS-003"


class DocumentationIOError(DocumentationError):
    """Exception for I/O errors in documentation generation."""
    
    def __init__(self, message: str = "Documentation I/O error", file_path: str = None, details: str = None):
        if file_path:
            message = f"I/O error for file '{file_path}': {message}"
        super().__init__(message, details)
        self.file_path = file_path
        self.error_code = "DOCS-004"


class DocumentationDependencyError(DocumentationError):
    """Exception for missing dependencies in documentation generation."""
    
    def __init__(self, message: str = "Documentation dependency error", dependency: str = None, details: str = None):
        if dependency:
            message = f"Missing dependency: {dependency}"
        super().__init__(message, details)
        self.dependency = dependency
        self.error_code = "DOCS-005"
