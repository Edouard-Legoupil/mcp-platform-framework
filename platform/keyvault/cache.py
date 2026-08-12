"""
Secret Cache for Key Vault Integration Module

This module provides caching functionality for secrets retrieved from
Azure Key Vault to improve performance and reduce API calls.
"""

import logging
import threading
import time
from datetime import datetime
from typing import Optional, Dict, Any

from .models import SecretCacheEntry, SecretType
from .exceptions import KeyVaultCacheError

logger = logging.getLogger(__name__)


class SecretCache:
    """
    Thread-safe cache for secrets retrieved from Azure Key Vault.
    
    This cache stores secrets with configurable TTL (time-to-live) and
    automatically expires and removes old entries.
    """
    
    def __init__(self, ttl_seconds: int = 300, max_size: int = 1000):
        """
        Initialize the secret cache.
        
        Args:
            ttl_seconds: Default time-to-live for cache entries in seconds
            max_size: Maximum number of entries in the cache
        """
        self._cache: Dict[str, SecretCacheEntry] = {}
        self._lock = threading.RLock()
        self._ttl_seconds = ttl_seconds
        self._max_size = max_size
        self._hits = 0
        self._misses = 0
        self._expired = 0
        
    def get(self, secret_name: str, vault_name: str = None) -> Optional[str]:
        """
        Get a secret from the cache.
        
        Args:
            secret_name: Name of the secret
            vault_name: Name of the vault (optional)
            
        Returns:
            The cached secret value, or None if not found or expired
        """
        cache_key = self._get_cache_key(secret_name, vault_name)
        
        with self._lock:
            if cache_key not in self._cache:
                self._misses += 1
                logger.debug(f"Cache miss for {cache_key}")
                return None
            
            entry = self._cache[cache_key]
            
            if entry.is_expired():
                # Remove expired entry
                del self._cache[cache_key]
                self._expired += 1
                logger.debug(f"Cache entry expired for {cache_key}")
                return None
            
            self._hits += 1
            logger.debug(f"Cache hit for {cache_key}")
            return entry.secret_value
    
    def set(
        self, 
        secret_name: str, 
        secret_value: str, 
        vault_name: str = None,
        secret_type: SecretType = SecretType.SECRET,
        ttl_seconds: Optional[int] = None
    ) -> SecretCacheEntry:
        """
        Store a secret in the cache.
        
        Args:
            secret_name: Name of the secret
            secret_value: Value of the secret
            vault_name: Name of the vault (optional)
            secret_type: Type of the secret
            ttl_seconds: Time-to-live for this entry (uses default if not provided)
            
        Returns:
            The created cache entry
        """
        cache_key = self._get_cache_key(secret_name, vault_name)
        ttl = ttl_seconds or self._ttl_seconds
        
        with self._lock:
            # Check if we need to evict old entries
            if len(self._cache) >= self._max_size:
                self._evict_expired_or_oldest()
            
            entry = SecretCacheEntry(
                secret_name=secret_name,
                vault_name=vault_name or "default",
                secret_value=secret_value,
                secret_type=secret_type,
                ttl_seconds=ttl
            )
            
            self._cache[cache_key] = entry
            logger.debug(f"Cached secret {cache_key}")
            return entry
    
    def remove(self, secret_name: str, vault_name: str = None) -> bool:
        """
        Remove a secret from the cache.
        
        Args:
            secret_name: Name of the secret
            vault_name: Name of the vault (optional)
            
        Returns:
            True if the secret was removed, False if not found
        """
        cache_key = self._get_cache_key(secret_name, vault_name)
        
        with self._lock:
            if cache_key in self._cache:
                del self._cache[cache_key]
                logger.debug(f"Removed {cache_key} from cache")
                return True
            return False
    
    def clear(self) -> int:
        """
        Clear all entries from the cache.
        
        Returns:
            Number of entries removed
        """
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"Cleared {count} entries from cache")
            return count
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired entries from the cache.
        
        Returns:
            Number of expired entries removed
        """
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items() 
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self._cache[key]
                
            count = len(expired_keys)
            if count > 0:
                logger.info(f"Cleaned up {count} expired cache entries")
            
            return count
    
    def _evict_expired_or_oldest(self):
        """Evict expired entries or the oldest entry if none are expired."""
        # First try to remove expired entries
        count = self.cleanup_expired()
        
        if count > 0:
            return
        
        # If no expired entries, remove the oldest
        if self._cache:
            oldest_key = min(
                self._cache.keys(), 
                key=lambda k: self._cache[k].cached_at
            )
            del self._cache[oldest_key]
            logger.debug(f"Evicted oldest cache entry: {oldest_key}")
    
    def _get_cache_key(self, secret_name: str, vault_name: str = None) -> str:
        """Generate a cache key for a secret."""
        if vault_name:
            return f"{vault_name}/{secret_name}"
        return secret_name
    
    def contains(self, secret_name: str, vault_name: str = None) -> bool:
        """
        Check if a secret is in the cache and not expired.
        
        Args:
            secret_name: Name of the secret
            vault_name: Name of the vault (optional)
            
        Returns:
            True if the secret is in cache and not expired
        """
        cache_key = self._get_cache_key(secret_name, vault_name)
        
        with self._lock:
            if cache_key not in self._cache:
                return False
            
            entry = self._cache[cache_key]
            return not entry.is_expired()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            total_entries = len(self._cache)
            expired_entries = sum(
                1 for entry in self._cache.values() 
                if entry.is_expired()
            )
            
            return {
                "total_entries": total_entries,
                "hits": self._hits,
                "misses": self._misses,
                "expired": self._expired,
                "hit_rate": self._calculate_hit_rate(),
                "expired_entries": expired_entries,
                "max_size": self._max_size,
                "default_ttl_seconds": self._ttl_seconds
            }
    
    def _calculate_hit_rate(self) -> float:
        """Calculate the cache hit rate."""
        total = self._hits + self._misses
        if total == 0:
            return 0.0
        return (self._hits / total) * 100
    
    def list_entries(self) -> List[Dict[str, Any]]:
        """
        List all cache entries (for debugging and monitoring).
        
        Returns:
            List of cache entry information (without secret values)
        """
        with self._lock:
            return [
                {
                    "cache_key": key,
                    "secret_name": entry.secret_name,
                    "vault_name": entry.vault_name,
                    "secret_type": entry.secret_type.value,
                    "cached_at": entry.cached_at.isoformat(),
                    "expires_at": entry.expires_at.isoformat(),
                    "is_expired": entry.is_expired()
                }
                for key, entry in self._cache.items()
            ]
    
    def cleanup(self):
        """Perform regular cache cleanup."""
        self.cleanup_expired()
        
        # Additional cleanup logic could be added here
        # For example, remove entries that haven't been accessed in a while
    
    def reset_stats(self):
        """Reset cache statistics."""
        with self._lock:
            self._hits = 0
            self._misses = 0
            self._expired = 0
