"""
Data models for Documentation Generator Module
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any


class OutputFormat(Enum):
    """
    Output formats supported by the Documentation Generator.
    """
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    OPENAPI = "openapi"
    JSON = "json"


class Classification(Enum):
    """
    Data classification levels for documentation.
    """
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    STRICTLY_CONFIDENTIAL = "STRICTLY_CONFIDENTIAL"


class SLATier(Enum):
    """
    Service Level Agreement tiers for documentation.
    """
    BRONZE = "Bronze"
    SILVER = "Silver"
    GOLD = "Gold"
    PLATINUM = "Platinum"


@dataclass
class ParameterMetadata:
    """
    Metadata for a parameter in documentation.
    """
    name: str
    type: str = "string"
    required: bool = False
    default: Optional[Any] = None
    description: str = ""
    example: Optional[str] = None
    
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
            
        return result


@dataclass
class DocumentationMetadata:
    """
    Complete metadata for documentation generation.
    """
    tool_name: str
    tool_description: str
    domain: str
    owner: str
    version: str
    classification: Classification
    sla_tier: SLATier
    parameters: List[ParameterMetadata] = field(default_factory=list)
    returns: str = ""
    raises: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # Generated fields
    generated_at: datetime = field(default_factory=datetime.utcnow)
    documentation_version: str = "1.0.0"
    
    # Source information
    source_file: Optional[str] = None
    source_line: Optional[int] = None
    
    # Cross-references
    related_tools: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "tool_name": self.tool_name,
            "tool_description": self.tool_description,
            "domain": self.domain,
            "owner": self.owner,
            "version": self.version,
            "classification": self.classification.value,
            "sla_tier": self.sla_tier.value,
            "parameters": [p.to_dict() for p in self.parameters],
            "returns": self.returns,
            "raises": self.raises,
            "examples": self.examples,
            "notes": self.notes,
            "tags": self.tags,
            "generated_at": self.generated_at.isoformat(),
            "documentation_version": self.documentation_version,
            "source_file": self.source_file,
            "source_line": self.source_line,
            "related_tools": self.related_tools,
            "dependencies": self.dependencies
        }
