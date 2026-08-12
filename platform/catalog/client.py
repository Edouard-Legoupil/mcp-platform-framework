"""
Catalog Client for MCP Platform Framework

This module provides the main client for interacting with the enterprise
catalog API. It handles tool registration, updates, search, and management.
"""

import json
import logging
import os
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin

import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

from .models import (
    ToolMetadata, ToolRegistration, ValidationResult, SearchResult, 
    Classification, SLATier
)
from platform.config import ConfigManager
from platform.telemetry import telemetry

logger = logging.getLogger(__name__)


class CatalogClient:
    """
    Client for interacting with the enterprise catalog API.
    
    This client provides methods for:
    - Registering MCP tools in the catalog
    - Updating tool registrations
    - Searching for tools
    - Retrieving tool metadata
    - Managing tool lifecycle
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the CatalogClient.
        
        Args:
            config: Optional configuration dictionary. If not provided,
                   configuration will be loaded from environment.
        """
        self.config = config or self._load_config()
        self.session = requests.Session()
        self._initialize_session()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment and config files."""
        config_manager = ConfigManager()
        catalog_config = config_manager.get_config("catalog")
        
        return {
            "endpoint": os.getenv("CATALOG_ENDPOINT", catalog_config.get("endpoint", "https://catalog.my-org.org/api/v1")),
            "api_key": os.getenv("CATALOG_API_KEY", catalog_config.get("api_key")),
            "timeout": int(os.getenv("CATALOG_TIMEOUT", catalog_config.get("timeout", 30))),
            "retry_count": int(os.getenv("CATALOG_RETRY_COUNT", catalog_config.get("retry_count", 3))),
            "retry_backoff": int(os.getenv("CATALOG_RETRY_BACKOFF", catalog_config.get("retry_backoff", 2))),
            "batch_size": int(os.getenv("CATALOG_BATCH_SIZE", catalog_config.get("batch_size", 100))),
            "user_agent": f"MCP-Catalog-Client/{os.getenv('MCP_VERSION', '1.0.0')}"
        }
    
    def _initialize_session(self):
        """Initialize the HTTP session with headers and timeouts."""
        self.session.headers.update({
            "User-Agent": self.config["user_agent"],
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
        if self.config.get("api_key"):
            self.session.headers["Authorization"] = f"Bearer {self.config['api_key']}"
            
    def _get_url(self, path: str) -> str:
        """Construct full URL from endpoint and path."""
        return urljoin(self.config["endpoint"], path)
    
    def _make_request(
        self, 
        method: str, 
        path: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic and error handling.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API path
            data: Request body data
            params: Query parameters
            timeout: Request timeout in seconds
            
        Returns:
            Dictionary containing response data
            
        Raises:
            CatalogConnectionError: If connection to catalog fails
            CatalogRequestError: If request fails after retries
            CatalogAuthenticationError: If authentication fails
        """
        url = self._get_url(path)
        timeout = timeout or self.config["timeout"]
        
        max_retries = self.config["retry_count"]
        backoff_factor = self.config["retry_backoff"]
        
        for attempt in range(max_retries + 1):
            try:
                start_time = time.time()
                
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    timeout=timeout
                )
                
                duration_ms = (time.time() - start_time) * 1000
                
                # Track telemetry
                telemetry.track_request(
                    service="catalog",
                    method=method,
                    path=path,
                    status_code=response.status_code,
                    duration_ms=duration_ms
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    raise CatalogAuthenticationError("Authentication failed")
                elif response.status_code == 403:
                    raise CatalogAuthorizationError("Access denied")
                elif response.status_code == 404:
                    raise CatalogNotFoundError(f"Resource not found: {path}")
                elif response.status_code == 400:
                    error_data = response.json()
                    raise CatalogValidationError(error_data.get("message", "Bad request"))
                elif response.status_code >= 500:
                    if attempt < max_retries:
                        backoff_time = backoff_factor ** attempt
                        logger.warning(f"Request failed, retrying in {backoff_time}s... (attempt {attempt + 1}/{max_retries + 1})")
                        time.sleep(backoff_time)
                        continue
                    else:
                        raise CatalogServerError(f"Server error: {response.text}")
                else:
                    raise CatalogRequestError(f"Unexpected status code: {response.status_code}")
                    
            except (ConnectionError, Timeout) as e:
                if attempt < max_retries:
                    backoff_time = backoff_factor ** attempt
                    logger.warning(f"Connection failed, retrying in {backoff_time}s... (attempt {attempt + 1}/{max_retries + 1})")
                    time.sleep(backoff_time)
                    continue
                else:
                    raise CatalogConnectionError(f"Connection failed: {str(e)}")
                    
        # This should never be reached
        raise CatalogRequestError("Request failed after all retries")
    
    def register_tool(self, metadata: ToolMetadata) -> ToolRegistration:
        """
        Register a new tool in the enterprise catalog.
        
        Args:
            metadata: Complete tool metadata
            
        Returns:
            ToolRegistration with registration details
            
        Raises:
            CatalogRegistrationError: If registration fails
            ValidationError: If metadata is invalid
        """
        # Validate metadata first
        validation = self.validate_metadata(metadata)
        if not validation.is_valid:
            raise ValidationError(f"Metadata validation failed: {validation.errors}")
        
        # Prepare registration data
        registration_data = {
            "tool_metadata": metadata.to_dict(),
            "registration_source": "mcp-framework",
            "registration_version": "1.0.0"
        }
        
        try:
            response = self._make_request("POST", "/tools/register", registration_data)
            
            # Track successful registration
            telemetry.track_event(
                "catalog.tool.registered",
                {
                    "tool_name": metadata.name,
                    "domain": metadata.domain,
                    "classification": metadata.classification.value
                }
            )
            
            return ToolRegistration(
                tool_id=response["tool_id"],
                tool_name=metadata.name,
                domain=metadata.domain,
                owner=metadata.owner,
                registration_date=datetime.fromisoformat(response["registration_date"]),
                last_updated=datetime.fromisoformat(response["last_updated"]),
                status=response.get("status", "active"),
                catalog_version=response.get("catalog_version", "1.0.0")
            )
            
        except Exception as e:
            telemetry.track_exception(e, context={"operation": "register_tool"})
            raise CatalogRegistrationError(f"Failed to register tool: {str(e)}")
    
    def update_tool(self, tool_id: str, updates: Dict[str, Any]) -> ToolRegistration:
        """
        Update an existing tool registration.
        
        Args:
            tool_id: Unique tool identifier
            updates: Dictionary of fields to update
            
        Returns:
            Updated ToolRegistration
            
        Raises:
            CatalogNotFoundError: If tool is not found
            CatalogUpdateError: If update fails
        """
        try:
            response = self._make_request("PUT", f"/tools/{tool_id}", updates)
            
            telemetry.track_event(
                "catalog.tool.updated",
                {"tool_id": tool_id, "fields_updated": list(updates.keys())}
            )
            
            return ToolRegistration(
                tool_id=tool_id,
                tool_name=response["tool_name"],
                domain=response["domain"],
                owner=response["owner"],
                registration_date=datetime.fromisoformat(response["registration_date"]),
                last_updated=datetime.fromisoformat(response["last_updated"]),
                status=response.get("status", "active"),
                catalog_version=response.get("catalog_version", "1.0.0")
            )
            
        except CatalogNotFoundError:
            raise
        except Exception as e:
            telemetry.track_exception(e, context={"operation": "update_tool"})
            raise CatalogUpdateError(f"Failed to update tool: {str(e)}")
    
    def deregister_tool(self, tool_id: str) -> bool:
        """
        Remove a tool from the catalog.
        
        Args:
            tool_id: Unique tool identifier
            
        Returns:
            True if deregistration was successful
            
        Raises:
            CatalogNotFoundError: If tool is not found
            CatalogDeregistrationError: If deregistration fails
        """
        try:
            response = self._make_request("DELETE", f"/tools/{tool_id}")
            
            telemetry.track_event("catalog.tool.deregistered", {"tool_id": tool_id})
            
            return response.get("success", False)
            
        except CatalogNotFoundError:
            raise
        except Exception as e:
            telemetry.track_exception(e, context={"operation": "deregister_tool"})
            raise CatalogDeregistrationError(f"Failed to deregister tool: {str(e)}")
    
    def get_tool(self, tool_id: str) -> ToolMetadata:
        """
        Retrieve tool metadata by ID.
        
        Args:
            tool_id: Unique tool identifier
            
        Returns:
            ToolMetadata for the requested tool
            
        Raises:
            CatalogNotFoundError: If tool is not found
        """
        try:
            response = self._make_request("GET", f"/tools/{tool_id}")
            return ToolMetadata.from_dict(response["tool_metadata"])
            
        except CatalogNotFoundError:
            raise
        except Exception as e:
            telemetry.track_exception(e, context={"operation": "get_tool"})
            raise CatalogRetrievalError(f"Failed to retrieve tool: {str(e)}")
    
    def get_tool_by_name(self, tool_name: str) -> ToolMetadata:
        """
        Retrieve tool metadata by name.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            ToolMetadata for the requested tool
            
        Raises:
            CatalogNotFoundError: If tool is not found
        """
        try:
            response = self._make_request("GET", f"/tools/name/{tool_name}")
            return ToolMetadata.from_dict(response["tool_metadata"])
            
        except CatalogNotFoundError:
            raise
        except Exception as e:
            telemetry.track_exception(e, context={"operation": "get_tool_by_name"})
            raise CatalogRetrievalError(f"Failed to retrieve tool by name: {str(e)}")
    
    def search_tools(
        self, 
        query: str = "", 
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> SearchResult:
        """
        Search for tools in the catalog.
        
        Args:
            query: Search query string
            filters: Filter criteria (classification, domain, owner, etc.)
            limit: Maximum number of results to return
            offset: Offset for pagination
            
        Returns:
            SearchResult with matching tools
        """
        params = {
            "q": query,
            "limit": limit,
            "offset": offset
        }
        
        if filters:
            params["filters"] = json.dumps(filters)
        
        try:
            start_time = time.time()
            response = self._make_request("GET", "/tools/search", params=params)
            execution_time_ms = (time.time() - start_time) * 1000
            
            tools = [
                ToolMetadata.from_dict(tool_data) 
                for tool_data in response.get("results", [])
            ]
            
            telemetry.track_event(
                "catalog.tools.searched",
                {
                    "query": query,
                    "filters": str(filters),
                    "result_count": len(tools)
                }
            )
            
            return SearchResult(
                query=query,
                total_results=response.get("total_results", 0),
                results=tools,
                filters_applied=filters or {},
                execution_time_ms=execution_time_ms
            )
            
        except Exception as e:
            telemetry.track_exception(e, context={"operation": "search_tools"})
            raise CatalogSearchError(f"Failed to search tools: {str(e)}")
    
    def list_tools(
        self, 
        domain: Optional[str] = None,
        owner: Optional[str] = None,
        classification: Optional[Classification] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ToolMetadata]:
        """
        List all tools, optionally filtered by criteria.
        
        Args:
            domain: Filter by domain
            owner: Filter by owner
            classification: Filter by classification
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of ToolMetadata objects
        """
        filters = {}
        if domain:
            filters["domain"] = domain
        if owner:
            filters["owner"] = owner
        if classification:
            filters["classification"] = classification.value
        
        result = self.search_tools(filters=filters, limit=limit, offset=offset)
        return result.results
    
    def validate_metadata(self, metadata: ToolMetadata) -> ValidationResult:
        """
        Validate tool metadata before registration.
        
        Args:
            metadata: ToolMetadata to validate
            
        Returns:
            ValidationResult with validation status and messages
        """
        errors = []
        warnings = []
        messages = []
        
        # Check required fields
        required_fields = ["name", "description", "classification", "domain", "owner"]
        for field in required_fields:
            if not getattr(metadata, field):
                errors.append(f"Missing required field: {field}")
        
        # Validate classification
        try:
            Classification.from_string(metadata.classification.value)
        except ValueError as e:
            errors.append(str(e))
        
        # Validate SLA tier
        try:
            SLATier.from_string(metadata.sla_tier.value)
        except ValueError as e:
            errors.append(str(e))
        
        # Check parameter names are unique
        param_names = [p.name for p in metadata.parameters]
        if len(param_names) != len(set(param_names)):
            errors.append("Parameter names must be unique")
        
        # Check for reserved parameter names
        reserved_names = ["self", "cls", "context", "request", "response"]
        for param in metadata.parameters:
            if param.name.lower() in reserved_names:
                errors.append(f"Reserved parameter name: {param.name}")
        
        # Check version format
        if not self._is_valid_version(metadata.version):
            warnings.append(f"Version '{metadata.version}' may not follow semantic versioning")
        
        # Check tags for consistency
        for tag in metadata.tags:
            if len(tag) > 50:
                warnings.append(f"Tag '{tag}' exceeds maximum length of 50 characters")
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            messages=messages
        )
    
    def _is_valid_version(self, version: str) -> bool:
        """Check if version string follows semantic versioning pattern."""
        import re
        pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$'
        return bool(re.match(pattern, version))
    
    def register_tools_batch(self, tools: List[ToolMetadata]) -> List[ToolRegistration]:
        """
        Register multiple tools in a batch operation.
        
        Args:
            tools: List of ToolMetadata objects to register
            
        Returns:
            List of ToolRegistration objects for successfully registered tools
        """
        batch_size = self.config["batch_size"]
        registrations = []
        
        for i in range(0, len(tools), batch_size):
            batch = tools[i:i + batch_size]
            batch_data = [tool.to_dict() for tool in batch]
            
            try:
                response = self._make_request("POST", "/tools/register/batch", batch_data)
                
                for result in response.get("results", []):
                    if result.get("success"):
                        registration = ToolRegistration(
                            tool_id=result["tool_id"],
                            tool_name=result["tool_name"],
                            domain=result["domain"],
                            owner=result["owner"],
                            registration_date=datetime.fromisoformat(result["registration_date"]),
                            last_updated=datetime.fromisoformat(result["last_updated"]),
                            status=result.get("status", "active")
                        )
                        registrations.append(registration)
                    else:
                        logger.error(f"Failed to register tool {result.get('tool_name')}: {result.get('error')}")
                        
            except Exception as e:
                telemetry.track_exception(e, context={"operation": "register_tools_batch"})
                logger.error(f"Batch registration failed: {str(e)}")
        
        return registrations
    
    def force_sync(self) -> bool:
        """
        Force synchronization of catalog with governance systems.
        
        Returns:
            True if sync was successful
        """
        try:
            response = self._make_request("POST", "/sync/force")
            telemetry.track_event("catalog.sync.forced")
            return response.get("success", False)
            
        except Exception as e:
            telemetry.track_exception(e, context={"operation": "force_sync"})
            raise CatalogSyncError(f"Failed to force sync: {str(e)}")
    
    def get_sync_status(self) -> Dict[str, Any]:
        """
        Get current synchronization status.
        
        Returns:
            Dictionary with sync status information
        """
        try:
            response = self._make_request("GET", "/sync/status")
            return response
            
        except Exception as e:
            telemetry.track_exception(e, context={"operation": "get_sync_status"})
            raise CatalogSyncError(f"Failed to get sync status: {str(e)}")
    
    def tool_exists(self, tool_name: str) -> bool:
        """
        Check if a tool exists in the catalog.
        
        Args:
            tool_name: Name of the tool to check
            
        Returns:
            True if tool exists, False otherwise
        """
        try:
            self.get_tool_by_name(tool_name)
            return True
        except CatalogNotFoundError:
            return False
        except Exception:
            return False


# Custom Exceptions
class CatalogError(Exception):
    """Base exception for catalog errors."""
    pass


class CatalogConnectionError(CatalogError):
    """Exception for connection failures."""
    pass


class CatalogAuthenticationError(CatalogError):
    """Exception for authentication failures."""
    pass


class CatalogAuthorizationError(CatalogError):
    """Exception for authorization failures."""
    pass


class CatalogNotFoundError(CatalogError):
    """Exception for not found errors."""
    pass


class CatalogRegistrationError(CatalogError):
    """Exception for registration failures."""
    pass


class CatalogUpdateError(CatalogError):
    """Exception for update failures."""
    pass


class CatalogDeregistrationError(CatalogError):
    """Exception for deregistration failures."""
    pass


class CatalogRetrievalError(CatalogError):
    """Exception for retrieval failures."""
    pass


class CatalogSearchError(CatalogError):
    """Exception for search failures."""
    pass


class CatalogSyncError(CatalogError):
    """Exception for sync failures."""
    pass


class ValidationError(CatalogError):
    """Exception for validation failures."""
    pass
