"""
Metadata Validator for Catalog Integration Module

This module provides validation functionality for MCP tool metadata
to ensure compliance with organizational standards and requirements.
"""

import logging
from typing import List, Optional, Dict, Any

from .models import ToolMetadata, ValidationResult, Classification, SLATier

logger = logging.getLogger(__name__)


class MetadataValidator:
    """
    Validator for MCP tool metadata.
    
    This class provides comprehensive validation of tool metadata to ensure
    it meets all organizational requirements before registration in the catalog.
    """
    
    def __init__(self):
        """Initialize the validator."""
        self._required_fields = [
            "name", "description", "classification", "domain", "owner"
        ]
        self._reserved_names = [
            "self", "cls", "context", "request", "response",
            "args", "kwargs", "func", "tool", "metadata"
        ]
        self._max_name_length = 100
        self._max_description_length = 500
        self._max_tag_length = 50
        self._max_tags_count = 20
        self._max_parameters_count = 50
        
    def validate(self, metadata: ToolMetadata) -> ValidationResult:
        """
        Validate tool metadata.
        
        Args:
            metadata: ToolMetadata to validate
            
        Returns:
            ValidationResult with validation status and messages
        """
        errors = []
        warnings = []
        messages = []
        
        # Validate required fields
        self._validate_required_fields(metadata, errors)
        
        # Validate field formats
        self._validate_field_formats(metadata, errors, warnings)
        
        # Validate classification
        self._validate_classification(metadata, errors)
        
        # Validate SLA tier
        self._validate_sla_tier(metadata, errors)
        
        # Validate parameters
        self._validate_parameters(metadata, errors, warnings)
        
        # Validate tags
        self._validate_tags(metadata, errors, warnings)
        
        # Validate dependencies
        self._validate_dependencies(metadata, errors, warnings)
        
        # Validate version
        self._validate_version(metadata, errors, warnings)
        
        # Validate URLs
        self._validate_urls(metadata, errors, warnings)
        
        # Check for best practices
        self._check_best_practices(metadata, warnings, messages)
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            messages=messages
        )
    
    def _validate_required_fields(self, metadata: ToolMetadata, errors: List[str]):
        """Validate that all required fields are present."""
        for field in self._required_fields:
            value = getattr(metadata, field, None)
            if not value or (isinstance(value, str) and not value.strip()):
                errors.append(f"Missing required field: {field}")
    
    def _validate_field_formats(self, metadata: ToolMetadata, errors: List[str], warnings: List[str]):
        """Validate field formats and lengths."""
        # Validate name
        if metadata.name:
            if len(metadata.name) > self._max_name_length:
                errors.append(f"Tool name exceeds maximum length of {self._max_name_length} characters")
            
            # Check for invalid characters
            if not self._is_valid_name(metadata.name):
                errors.append(f"Tool name contains invalid characters: {metadata.name}")
        
        # Validate description
        if metadata.description:
            if len(metadata.description) > self._max_description_length:
                warnings.append(f"Description exceeds recommended length of {self._max_description_length} characters")
        
        # Validate domain
        if metadata.domain:
            if not self._is_valid_domain(metadata.domain):
                errors.append(f"Invalid domain format: {metadata.domain}")
        
        # Validate owner
        if metadata.owner:
            if not self._is_valid_owner(metadata.owner):
                errors.append(f"Invalid owner format: {metadata.owner}")
    
    def _validate_classification(self, metadata: ToolMetadata, errors: List[str]):
        """Validate classification field."""
        try:
            Classification.from_string(metadata.classification.value)
        except ValueError as e:
            errors.append(f"Invalid classification: {str(e)}")
    
    def _validate_sla_tier(self, metadata: ToolMetadata, errors: List[str]):
        """Validate SLA tier field."""
        try:
            SLATier.from_string(metadata.sla_tier.value)
        except ValueError as e:
            errors.append(f"Invalid SLA tier: {str(e)}")
    
    def _validate_parameters(self, metadata: ToolMetadata, errors: List[str], warnings: List[str]):
        """Validate tool parameters."""
        # Check parameter count
        if len(metadata.parameters) > self._max_parameters_count:
            errors.append(f"Tool has {len(metadata.parameters)} parameters, maximum is {self._max_parameters_count}")
        
        # Check for duplicate parameter names
        param_names = [p.name for p in metadata.parameters]
        if len(param_names) != len(set(param_names)):
            errors.append("Parameter names must be unique")
        
        # Validate each parameter
        for param in metadata.parameters:
            self._validate_parameter(param, errors, warnings)
    
    def _validate_parameter(self, param: Any, errors: List[str], warnings: List[str]):
        """Validate a single parameter."""
        # Check parameter name
        if not param.name:
            errors.append("Parameter missing name")
        elif param.name.lower() in self._reserved_names:
            errors.append(f"Reserved parameter name: {param.name}")
        elif not self._is_valid_parameter_name(param.name):
            errors.append(f"Invalid parameter name: {param.name}")
        
        # Check parameter type
        if not param.type:
            errors.append(f"Parameter {param.name} missing type")
        elif not self._is_valid_parameter_type(param.type):
            errors.append(f"Invalid parameter type: {param.type}")
        
        # Check required field
        if param.required and not param.description:
            warnings.append(f"Required parameter {param.name} should have a description")
        
        # Check enum values
        if param.enum and not isinstance(param.enum, list):
            errors.append(f"Parameter {param.name} enum must be a list")
        
        # Check min/max values
        if param.min_value is not None and param.max_value is not None:
            if param.min_value >= param.max_value:
                errors.append(f"Parameter {param.name} min_value must be less than max_value")
    
    def _validate_tags(self, metadata: ToolMetadata, errors: List[str], warnings: List[str]):
        """Validate tool tags."""
        if len(metadata.tags) > self._max_tags_count:
            warnings.append(f"Tool has {len(metadata.tags)} tags, recommended maximum is {self._max_tags_count}")
        
        for tag in metadata.tags:
            if len(tag) > self._max_tag_length:
                warnings.append(f"Tag '{tag}' exceeds maximum length of {self._max_tag_length} characters")
            elif not self._is_valid_tag(tag):
                warnings.append(f"Tag '{tag}' contains invalid characters")
    
    def _validate_dependencies(self, metadata: ToolMetadata, errors: List[str], warnings: List[str]):
        """Validate tool dependencies."""
        for dependency in metadata.dependencies:
            if not dependency:
                errors.append("Empty dependency string")
            elif not self._is_valid_dependency(dependency):
                warnings.append(f"Dependency '{dependency}' may not be valid")
    
    def _validate_version(self, metadata: ToolMetadata, errors: List[str], warnings: List[str]):
        """Validate version field."""
        if not self._is_valid_semantic_version(metadata.version):
            warnings.append(f"Version '{metadata.version}' may not follow semantic versioning (MAJOR.MINOR.PATCH)")
    
    def _validate_urls(self, metadata: ToolMetadata, errors: List[str], warnings: List[str]):
        """Validate URL fields."""
        url_fields = ["documentation_url"]
        
        for field in url_fields:
            url = getattr(metadata, field, None)
            if url and not self._is_valid_url(url):
                warnings.append(f"Invalid {field}: {url}")
    
    def _check_best_practices(self, metadata: ToolMetadata, warnings: List[str], messages: List[str]):
        """Check for best practices compliance."""
        # Check if description is comprehensive
        if metadata.description and len(metadata.description.split()) < 10:
            warnings.append("Tool description should be more comprehensive (at least 10 words)")
        
        # Check if parameters have descriptions
        params_without_desc = [p.name for p in metadata.parameters if not p.description]
        if params_without_desc:
            warnings.append(f"Parameters without descriptions: {', '.join(params_without_desc)}")
        
        # Check if required parameters have examples
        required_without_examples = [p.name for p in metadata.parameters if p.required and not p.example]
        if required_without_examples:
            messages.append(f"Consider adding examples for required parameters: {', '.join(required_without_examples)}")
        
        # Check if classification matches typical patterns
        if metadata.classification == Classification.PUBLIC:
            messages.append("PUBLIC classification - ensure this tool handles only non-sensitive data")
        elif metadata.classification == Classification.STRICTLY_CONFIDENTIAL:
            messages.append("STRICTLY_CONFIDENTIAL classification - ensure proper access controls are in place")
        
        # Check SLA tier appropriateness
        if metadata.sla_tier == SLATier.PLATINUM:
            messages.append("PLATINUM SLA tier - ensure this tool meets the high availability requirements")
    
    def _is_valid_name(self, name: str) -> bool:
        """Check if name is valid."""
        import re
        # Allow alphanumeric, spaces, hyphens, underscores
        pattern = r'^[a-zA-Z0-9\s\-_]+$'
        return bool(re.match(pattern, name))
    
    def _is_valid_domain(self, domain: str) -> bool:
        """Check if domain is valid."""
        import re
        # Allow alphanumeric and hyphens, no spaces
        pattern = r'^[a-zA-Z0-9\-]+$'
        return bool(re.match(pattern, domain))
    
    def _is_valid_owner(self, owner: str) -> bool:
        """Check if owner is valid."""
        import re
        # Allow alphanumeric, hyphens, and underscores
        pattern = r'^[a-zA-Z0-9\-_]+$'
        return bool(re.match(pattern, owner))
    
    def _is_valid_parameter_name(self, name: str) -> bool:
        """Check if parameter name is valid."""
        import re
        # Allow alphanumeric and underscores, must start with letter or underscore
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
        return bool(re.match(pattern, name))
    
    def _is_valid_parameter_type(self, type_name: str) -> bool:
        """Check if parameter type is valid."""
        valid_types = [
            "string", "int", "float", "bool", "list", "dict", "any",
            "str", "integer", "boolean", "array", "object"
        ]
        return type_name.lower() in valid_types
    
    def _is_valid_tag(self, tag: str) -> bool:
        """Check if tag is valid."""
        import re
        # Allow alphanumeric, hyphens, underscores, and dots
        pattern = r'^[a-zA-Z0-9\-_.]+$'
        return bool(re.match(pattern, tag))
    
    def _is_valid_dependency(self, dependency: str) -> bool:
        """Check if dependency is valid."""
        import re
        # Allow alphanumeric, hyphens, underscores, and dots
        pattern = r'^[a-zA-Z0-9\-_.]+$'
        return bool(re.match(pattern, dependency))
    
    def _is_valid_semantic_version(self, version: str) -> bool:
        """Check if version follows semantic versioning."""
        import re
        # Basic semantic versioning pattern: MAJOR.MINOR.PATCH[-prerelease]
        pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$'
        return bool(re.match(pattern, version))
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid."""
        if not url:
            return False
        try:
            from urllib.parse import urlparse
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def validate_batch(self, tools: List[ToolMetadata]) -> Dict[str, ValidationResult]:
        """
        Validate multiple tools in a batch.
        
        Args:
            tools: List of ToolMetadata objects to validate
            
        Returns:
            Dictionary mapping tool names to their ValidationResult
        """
        results = {}
        
        for tool in tools:
            result = self.validate(tool)
            results[tool.name] = result
        
        return results
