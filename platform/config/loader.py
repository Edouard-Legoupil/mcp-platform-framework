"""Configuration Loader for Azure"""
from typing import Dict, List, Any, Optional, Union
from .models import AppConfig, PlatformConfig, DomainConfig, Environment
import os
import json
import yaml
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigLoader:
    def __init__(self, env: Environment = Environment.DEV, config_dir: str = "config", env_file: str = ".env"):
        self.env = env
        self.config_dir = Path(config_dir)
        self.env_file = Path(env_file)
    
    def load_config(self) -> AppConfig:
        config = AppConfig()
        
        # Load from files
        file_config = self._load_config_files()
        if file_config:
            config = self._merge_config(config, file_config)
        
        # Load from environment variables
        env_config = self._load_environment_variables()
        if env_config:
            config = self._merge_config(config, env_config)
        
        # Load environment-specific config
        env_specific_config = self._load_environment_specific_config()
        if env_specific_config:
            config = self._merge_config(config, env_specific_config)
        
        config.platform.environment = self.env
        return config
    
    def _load_config_files(self) -> Optional[Dict[str, Any]]:
        config = {}
        
        # Load platform config
        platform_config = self._load_file_config(self.config_dir / "platform.yaml")
        if platform_config:
            config["platform"] = platform_config
        
        # Load domain configs
        domain_dir = self.config_dir / "domains"
        if domain_dir.exists():
            for config_file in domain_dir.glob("*.yaml"):
                domain_name = config_file.stem
                domain_config = self._load_file_config(config_file)
                if domain_config:
                    if "domains" not in config:
                        config["domains"] = {}
                    config["domains"][domain_name] = domain_config
        
        # Load secrets references
        secrets_config = self._load_file_config(self.config_dir / "secrets.yaml")
        if secrets_config:
            config["secrets"] = secrets_config.get("secrets", {})
        
        return config if config else None
    
    def _load_file_config(self, path: Path) -> Optional[Dict[str, Any]]:
        if not path.exists():
            return None
        try:
            with open(path, 'r') as f:
                if path.suffix in ['.yaml', '.yml']:
                    return yaml.safe_load(f)
                elif path.suffix == '.json':
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config file {path}: {e}")
        return None
    
    def _load_environment_variables(self) -> Optional[Dict[str, Any]]:
        config = {}
        
        # Load from .env file
        if self.env_file.exists():
            try:
                with open(self.env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if '=' in line:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                value = value.strip().strip('"').strip("'")
                                self._set_nested_value(config, key, value)
            except Exception as e:
                logger.error(f"Failed to load .env file: {e}")
        
        # Load from system environment variables
        for key, value in os.environ.items():
            if key.startswith('MCP_'):
                config_key = key[4:].lower()
                self._set_nested_value(config, config_key, value)
        
        return config if config else None
    
    def _load_environment_specific_config(self) -> Optional[Dict[str, Any]]:
        env_config_file = self.config_dir / f"{self.env.value.lower()}.yaml"
        if env_config_file.exists():
            return self._load_file_config(env_config_file)
        return None
    
    def _set_nested_value(self, config: Dict, key: str, value: Any):
        keys = key.split('.')
        current = config
        for i, k in enumerate(keys[:-1]):
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = self._convert_value(value)
    
    def _convert_value(self, value: str) -> Any:
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
        elif value.lower() == 'null' or value.lower() == 'none':
            return None
        try:
            return int(value)
        except ValueError:
            pass
        try:
            return float(value)
        except ValueError:
            pass
        return value
    
    def _merge_config(self, base: AppConfig, override: Dict[str, Any]) -> AppConfig:
        base_dict = base.dict()
        merged = self._deep_merge(base_dict, override)
        return AppConfig(**merged)
    
    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
