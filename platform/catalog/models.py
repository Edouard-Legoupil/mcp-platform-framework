"""
Data models for Catalog Integration Module
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any


class Classification(Enum):
    """
    Data classification levels for MCP tools and data.
    
    These classifications determine access controls, handling requirements,
    and compliance obligations for data processed by MCP tools.
    """
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    STRICTLY_CONFIDENTIAL = "STRICTLY_CONFIDENTIAL"

    @classmethod
    def from_string(cls, value: str) -> 'Classification':
        """Convert string value to Classification enum."""
        value = value.upper()
        if value not in cls._value2member_map_:
            raise ValueError(
                f"Invalid classification: {value}. "
                f"Valid values: {list(cls._value2member_map_.keys())}"
            )
        return cls._value2member_map_[value]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "value": self.value,
            "name": self.name,
            "description": self.get_description()
        }

    def get_description(self) -> str:
        """Get description for classification level."""
        descriptions = {
            Classification.PUBLIC: "Public information - no restrictions",
            Classification.INTERNAL: "Internal operational data - authenticated access",
            Classification.CONFIDENTIAL: "Sensitive business data - authorized access only",
            Classification.STRICTLY_CONFIDENTIAL: "Highly sensitive data - strict access controls"
        }
        return descriptions.get(self, "Unknown classification")


class SLATier(Enum):
    """
    Service Level Agreement tiers for MCP tools.
    
    These tiers determine response time guarantees, availability targets,
    and support levels for MCP tools.
    """
    BRONZE = "Bronze"
    SILVER = "Silver"
    GOLD = "Gold"
    PLATINUM = "Platinum"

    @classmethod
    def from_string(cls, value: str) -> 'SLATier':
        """Convert string value to SLATier enum."""
        value = value.title()
        if value not in cls._value2member_map_:
            raise ValueError(
                f"Invalid SLA tier: {value}. "
                f"Valid values: {list(cls._value2member_map_.keys())}"
            )
        return cls._value2member_map_[value]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "value": self.value,
            "name": self.name,
            "response_time": self.get_response_time(),
            "availability": self.get_availability()
        }

    def get_response_time(self) -> str:
        """Get response time guarantee for SLA tier."""
        response_times = {
            SLATier.BRONZE: "< 24h",
            SLATier.SILVER: "< 4h", 
            SLATier.GOLD: "< 1h",
            SLATier.PLATINUM: "< 15min"
        }
        return response_times.get(self, "Unknown")

    def get_availability(self) -> str:
        """Get availability target for SLA tier."""
        availability = {
            SLATier.BRONZE: "99%",
            SLATier.SILVER: "99.5%",
            SLATier.GOLD: "99.9%", 
            SLATier.PLATINUM: "99.95%"
        }
        return availability.get(self, "Unknown")


@dataclass
class ParameterMetadata:
    """
    Metadata for MCP tool parameters.
    
    This class captures all metadata about a tool parameter for documentation
    and validation purposes.
    """
    name: str
    type: str = "string"
    required: bool = False
    default: Optional[Any] = None
    description: str = ""
    example: Optional[str] = None
    enum: Optional[List[str]] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    pattern: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "name": self.name,
            "type": self.type,
            "required": self.required,
            "description": self.description
        }
        
        if self.default is not None:
            result["default"] = self.default
        if self.example:
            result["example"] = self.example
        if self.enum:
            result["enum"] = self.enum
        if self.min_value is not None:
            result["min_value"] = self.min_value
        if self.max_value is not None:
            result["max_value"] = self.max_value
        if self.pattern:
            result["pattern"] = self.pattern
            
        return result


@dataclass
class ToolMetadata:
    """
    Complete metadata for an MCP tool.
    
    This class captures all metadata required for tool registration,
    documentation, and governance compliance.
    """
    name: str
    description: str
    classification: Classification
    domain: str
    owner: str
    version: str = "1.0.0"
    sla_tier: SLATier = SLATier.SILVER
    parameters: List[ParameterMetadata] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    documentation_url: Optional[str] = None
    support_contact: Optional[str] = None
    changelog: Optional[str] = None
    
    # Azure-specific metadata
    resource_group: Optional[str] = None
    subscription_id: Optional[str] = None
    function_app: Optional[str] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "classification": self.classification.value,
            "domain": self.domain,
            "owner": self.owner,
            "version": self.version,
            "sla_tier": self.sla_tier.value,
            "parameters": [p.to_dict() for p in self.parameters],
            "tags": self.tags,
            "dependencies": self.dependencies,
            "documentation_url": self.documentation_url,
            "support_contact": self.support_contact,
            "changelog": self.changelog,
            "resource_group": self.resource_group,
            "subscription_id": self.subscription_id,
            "function_app": self.function_app,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolMetadata':
        """Create ToolMetadata from dictionary."""
        parameters = [
            ParameterMetadata(**param) 
            for param in data.get("parameters", [])
        ]
        
        return cls(
            name=data["name"],
            description=data["description"],
            classification=Classification.from_string(data["classification"]),
            domain=data["domain"],
            owner=data["owner"],
            version=data.get("version", "1.0.0"),
            sla_tier=SLATier.from_string(data.get("sla_tier", "Silver")),
            parameters=parameters,
            tags=data.get("tags", []),
            dependencies=data.get("dependencies", []),
            documentation_url=data.get("documentation_url"),
            support_contact=data.get("support_contact"),
            changelog=data.get("changelog"),
            resource_group=data.get("resource_group"),
            subscription_id=data.get("subscription_id"),
            function_app=data.get("function_app")
        )


@dataclass
class ToolRegistration:
    """
    Registration information for a tool in the catalog.
    
    This class represents the registration status and details of a tool
    in the enterprise catalog.
    """
    tool_id: str
    tool_name: str
    domain: str
    owner: str
    registration_date: datetime
    last_updated: datetime
    status: str = "active"
    catalog_version: str = "1.0.0"
    sync_status: str = "synced"
    sync_date: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "tool_id": self.tool_id,
            "tool_name": self.tool_name,
            "domain": self.domain,
            "owner": self.owner,
            "registration_date": self.registration_date.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "status": self.status,
            "catalog_version": self.catalog_version,
            "sync_status": self.sync_status
        }
        
        if self.sync_date:
            result["sync_date"] = self.sync_date.isoformat()
            
        return result


@dataclass
class ValidationResult:
    """
    Result of metadata validation.
    """
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    messages: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "messages": self.messages
        }


@dataclass
class SearchResult:
    """
    Result of a catalog search query.
    """
    query: str
    total_results: int
    results: List[ToolMetadata] = field(default_factory=list)
    filters_applied: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "query": self.query,
            "total_results": self.total_results,
            "results": [r.to_dict() for r in self.results],
            "filters_applied": self.filters_applied,
            "execution_time_ms": self.execution_time_ms
        }
