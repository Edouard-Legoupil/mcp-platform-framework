"""Configuration Manager for Azure"""
from typing import Dict, List, Any, Optional, Union, Callable
from .models import AppConfig, PlatformConfig, DomainConfig, Environment, ConfigValue, SecretReference
from .loader import ConfigLoader
import logging
import threading
import os

logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self, env: Environment = Environment.DEV, config_dir: str = "config", env_file: str = ".env"):
        self.env = env
        self.config_dir = config_dir
        self.env_file = env_file
        self._config: Optional[AppConfig] = None
        self._lock = threading.Lock()
        self._change_callbacks: List[Callable] = []
        self._load_config()
    
    def _load_config(self):
        loader = ConfigLoader(self.env, self.config_dir, self.env_file)
        self._config = loader.load_config()
    
    def get_config(self) -> AppConfig:
        with self._lock:
            if self._config is None:
                self._load_config()
            return self._config
    
    def get_platform_config(self) -> PlatformConfig:
        return self.get_config().platform
    
    def get_domain_config(self, domain: str) -> Optional[DomainConfig]:
        return self.get_config().domains.get(domain)
    
    def get_value(self, key: str, default: Any = None, domain: Optional[str] = None) -> Any:
        config = self.get_config()
        
        if domain and domain in config.domains:
            value = self._get_nested_value(config.domains[domain].settings, key)
            if value is not None:
                return value
        
        value = self._get_nested_value(config.platform.dict(), key)
        if value is not None:
            return value
        
        return default
    
    def _get_nested_value(self, data: Dict, key: str) -> Any:
        keys = key.split('.')
        current = data
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        return current
    
    def get_secret_reference(self, name: str, domain: Optional[str] = None) -> Optional[SecretReference]:
        config = self.get_config()
        if domain and domain in config.domains:
            if name in config.domains[domain].secrets:
                return config.domains[domain].secrets[name]
        if name in config.secrets:
            return config.secrets[name]
        return None
    
    def get_secret(self, name: str, domain: Optional[str] = None) -> Optional[str]:
        from .keyvault import get_key_vault_client
        ref = self.get_secret_reference(name, domain)
        if ref is None:
            return None
        
        client = get_key_vault_client()
        if client:
            return client.get_secret(ref)
        
        # Fallback to environment variable
        env_var_name = f"MCP_SECRET_{name.upper()}"
        return os.environ.get(env_var_name)
    
    def reload(self):
        with self._lock:
            self._load_config()
            self._notify_change()
    
    def on_change(self, callback: Callable):
        self._change_callbacks.append(callback)
    
    def _notify_change(self):
        for callback in self._change_callbacks:
            try:
                callback(self._config)
            except Exception as e:
                logger.error(f"Config change callback failed: {e}")

# Global config manager
_config_manager: Optional[ConfigManager] = None

def get_config_manager() -> ConfigManager:
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def get_config() -> AppConfig:
    return get_config_manager().get_config()

def get_platform_config() -> PlatformConfig:
    return get_config_manager().get_platform_config()

def get_domain_config(domain: str) -> Optional[DomainConfig]:
    return get_config_manager().get_domain_config(domain)

def get_config_value(key: str, default: Any = None, domain: Optional[str] = None) -> Any:
    return get_config_manager().get_value(key, default, domain)

def get_secret(name: str, domain: Optional[str] = None) -> Optional[str]:
    return get_config_manager().get_secret(name, domain)
