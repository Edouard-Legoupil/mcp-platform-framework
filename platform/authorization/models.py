"""Authorization Models"""
from pydantic import BaseModel
from typing import List, Dict, Optional
from enum import Enum

class PermissionLevel(str, Enum):
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"

class ResourceType(str, Enum):
    TOOL = "tool"
    DATA = "data"
    MODEL = "model"
    API = "api"

class Role(BaseModel):
    name: str
    description: str
    permissions: List[str] = []
    resource_types: List[ResourceType] = []

class Policy(BaseModel):
    name: str
    description: str
    rules: List[Dict] = []

class AccessRequest(BaseModel):
    user_id: str
    resource: str
    action: str
    context: Optional[Dict] = None

class AccessDecision(BaseModel):
    allowed: bool
    reason: Optional[str] = None
    required_permissions: List[str] = []
    missing_permissions: List[str] = []
