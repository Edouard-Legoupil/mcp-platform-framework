"""Key Vault Client for Azure"""
from typing import Optional, Dict, Any
from .models import SecretReference
import logging
import os

logger = logging.getLogger(__name__)

class KeyVaultClient:
    def __init__(self, key_vault_uri: Optional[str] = None, credential: Optional[Any] = None):
        self.key_vault_uri = key_vault_uri or os.environ.get("AZURE_KEY_VAULT_URI")
        self.credential = credential
        self._secret_cache: Dict[str, str] = {}
        self._initialized = False
        if self.key_vault_uri:
            self._initialize()
    
    def _initialize(self):
        try:
            from azure.identity import DefaultAzureCredential
            from azure.keyvault.secrets import SecretClient
            
            credential = self.credential or DefaultAzureCredential()
            self._client = SecretClient(vault_url=self.key_vault_uri, credential=credential)
            self._initialized = True
            logger.info(f"Initialized Key Vault client for: {self.key_vault_uri}")
        except Exception as e:
            logger.error(f"Failed to initialize Key Vault client: {e}")
            self._initialized = False
    
    def get_secret(self, reference: SecretReference) -> Optional[str]:
        if not self._initialized:
            logger.warning("Key Vault client not initialized")
            return None
        
        cache_key = f"{reference.source}:{reference.name}:{reference.version or 'latest'}"
        if cache_key in self._secret_cache:
            return self._secret_cache[cache_key]
        
        try:
            secret = self._client.get_secret(reference.name, version=reference.version)
            secret_value = secret.value
            self._secret_cache[cache_key] = secret_value
            return secret_value
        except Exception as e:
            logger.error(f"Failed to get secret {reference.name} from Key Vault: {e}")
            return None
    
    def set_secret(self, name: str, value: str) -> bool:
        if not self._initialized:
            logger.warning("Key Vault client not initialized")
            return False
        
        try:
            self._client.set_secret(name, value)
            cache_keys_to_remove = [k for k in self._secret_cache.keys() if k.startswith(f"keyvault:{name}:")]
            for key in cache_keys_to_remove:
                del self._secret_cache[key]
            return True
        except Exception as e:
            logger.error(f"Failed to set secret {name} in Key Vault: {e}")
            return False

# Global Key Vault client
_key_vault_client: Optional[KeyVaultClient] = None

def get_key_vault_client() -> Optional[KeyVaultClient]:
    global _key_vault_client
    if _key_vault_client is None:
        _key_vault_client = KeyVaultClient()
    return _key_vault_client

def set_key_vault_client(client: KeyVaultClient):
    global _key_vault_client
    _key_vault_client = client
