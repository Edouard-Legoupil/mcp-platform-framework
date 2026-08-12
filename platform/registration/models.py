"""Registration Models"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class ToolType(str, Enum):
    FUNCTION = "function"
    QUERY = "query"
    ACTION = "action"
    RESOURCE = "resource"

class ToolStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    MAINTENANCE = "maintenance"

class ParameterSchema(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    required: bool = False
    default: Optional[Any] = None

class ToolMetadata(BaseModel):
    name: str
    description: str
    tool_type: ToolType = ToolType.FUNCTION
    domain: str
    version: str = "1.0.0"
    status: ToolStatus = ToolStatus.ACTIVE
    classification: Optional[str] = None
    requires_authentication: bool = True
    requires_authorization: bool = True
    timeout_seconds: int = 30
    max_retries: int = 3
    rate_limit: Optional[str] = None
    owner: str
    maintainer: Optional[str] = None
    sla: Optional[str] = None
    parameters: Dict[str, ParameterSchema] = {}
    returns: Optional[str] = None
    tags: List[str] = []
    categories: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    usage_count: int = 0
    error_count: int = 0

class ToolRegistration(BaseModel):
    tool_id: str
    metadata: ToolMetadata
    endpoint: Optional[str] = None
    handler: Optional[str] = None
    is_loaded: bool = False
    load_error: Optional[str] = None

class RegistrationRequest(BaseModel):
    metadata: ToolMetadata
    endpoint: Optional[str] = None
    handler: Optional[str] = None

class RegistrationResult(BaseModel):
    success: bool
    tool_id: Optional[str] = None
    message: str
    error: Optional[str] = None
