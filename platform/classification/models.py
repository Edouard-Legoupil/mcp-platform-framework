"""Classification Models"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from enum import Enum

class ClassificationLevel(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    STRICTLY_CONFIDENTIAL = "STRICTLY_CONFIDENTIAL"

class ClassificationPolicy(BaseModel):
    level: ClassificationLevel
    description: str
    allowed_actions: List[str] = ["read"]
    requires_approval: bool = False
    requires_justification: bool = False
    encryption_required: bool = True
    audit_required: bool = True
    access_logging_required: bool = True
    retention_days: Optional[int] = None

class ClassifiedResource(BaseModel):
    resource_id: str
    resource_type: str
    classification: ClassificationLevel
    owner: str
    domain: str
    sensitivity_score: float = 0.0
    tags: List[str] = []
    metadata: Dict[str, Any] = {}
