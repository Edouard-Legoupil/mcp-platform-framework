"""Configuration Models for Azure"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from enum import Enum

class Environment(str, Enum):
    DEV = "Dev"
    TEST = "Test"
    STAGING = "Staging"
    PROD = "Prod"
    LOCAL = "Local"

class ConfigSource(str, Enum):
    ENVIRONMENT = "environment"
    FILE = "file"
    KEYVAULT = "keyvault"
    DATABASE = "database"
    DEFAULT = "default"

class SecretReference(BaseModel):
    source: str
    name: str
    version: Optional[str] = None

class DomainConfig(BaseModel):
    domain: str
    environment: Environment
    settings: Dict[str, Any] = {}
    secrets: Dict[str, SecretReference] = {}

class PlatformConfig(BaseModel):
    environment: Environment = Environment.DEV
    debug: bool = False
    log_level: str = "INFO"
    auth_enabled: bool = True
    auth_provider: str = "entra_id"
    telemetry_enabled: bool = True
    telemetry_exporters: List[str] = ["console"]
    audit_enabled: bool = True
    audit_storage: str = "azure_blob"
    encryption_enabled: bool = True
    max_concurrent_requests: int = 100
    request_timeout: int = 30
    features: Dict[str, bool] = {}

class AppConfig(BaseModel):
    platform: PlatformConfig = PlatformConfig()
    domains: Dict[str, DomainConfig] = {}
    secrets: Dict[str, SecretReference] = {}
