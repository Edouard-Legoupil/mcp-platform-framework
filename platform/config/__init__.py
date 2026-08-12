"""Configuration Management for Azure"""
from .models import Environment, ConfigValue, SecretReference, DomainConfig, PlatformConfig, AppConfig
from .loader import ConfigLoader
from .manager import ConfigManager, get_config_manager, get_config, get_platform_config, get_domain_config, get_config_value, get_secret
from .keyvault import KeyVaultClient, get_key_vault_client, set_key_vault_client

__all__ = [
    'Environment', 'ConfigValue', 'SecretReference', 'DomainConfig', 'PlatformConfig', 'AppConfig',
    'ConfigLoader', 'ConfigManager', 'get_config_manager', 'get_config', 'get_platform_config',
    'get_domain_config', 'get_config_value', 'get_secret', 'KeyVaultClient', 'get_key_vault_client', 'set_key_vault_client'
]
