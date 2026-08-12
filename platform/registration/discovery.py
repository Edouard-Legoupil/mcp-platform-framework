"""Automatic Tool Discovery for MCP Framework"""
import importlib
import importlib.util
import inspect
import logging
import pkgutil
from pathlib import Path
from typing import List, Optional, Set, Any, Callable
from .models import ToolMetadata, ToolType
from .registry import get_tool_registry, RegistrationRequest
from .decorators import set_domain_context

logger = logging.getLogger(__name__)


class ToolDiscovery:
    """
    Automatically discovers and registers MCP tools from domain modules.
    
    This class scans Python modules for functions decorated with @tool, @resource,
    @query, or @action decorators and registers them with the tool registry.
    """
    
    def __init__(self, domain: str, module_paths: Optional[List[str]] = None):
        """
        Initialize the tool discovery.
        
        Args:
            domain: The domain name for the tools being discovered
            module_paths: List of module paths to scan (e.g., ['tools', 'queries', 'actions'])
                        If None, scans the entire domain package
        """
        self.domain = domain
        self.module_paths = module_paths or []
        self._discovered_tools: Set[str] = set()
    
    def discover_and_register(self, package_name: str) -> int:
        """
        Discover and register all tools in the specified package.
        
        Args:
            package_name: The Python package name to scan (e.g., 'donor_management.tools')
        
        Returns:
            Number of tools discovered and registered
        """
        set_domain_context(self.domain)
        
        try:
            package = importlib.import_module(package_name)
            package_path = Path(package.__file__).parent
            
            # Get all modules in the package
            modules = self._find_modules_in_package(package_name, package_path)
            
            count = 0
            for module_name, module_path in modules:
                try:
                    module = importlib.import_module(module_name)
                    count += self._scan_module_for_tools(module, module_name)
                except Exception as e:
                    logger.error(f"Error loading module {module_name}: {str(e)}")
            
            return count
            
        except ImportError as e:
            logger.error(f"Error importing package {package_name}: {str(e)}")
            return 0
    
    def _find_modules_in_package(self, package_name: str, package_path: Path) -> List[tuple]:
        """Find all modules in a package"""
        modules = []
        
        # Add the package itself
        modules.append((package_name, package_path))
        
        # Find submodules
        for finder, name, ispkg in pkgutil.iter_modules([str(package_path)]):
            if ispkg:
                subpackage_name = f"{package_name}.{name}"
                try:
                    subpackage = importlib.import_module(subpackage_name)
                    subpackage_path = Path(subpackage.__file__).parent
                    modules.append((subpackage_name, subpackage_path))
                    
                    # Recursively find modules in subpackage
                    modules.extend(self._find_modules_in_package(subpackage_name, subpackage_path))
                except ImportError:
                    continue
            else:
                module_name = f"{package_name}.{name}"
                if not name.startswith('_'):  # Skip private modules
                    modules.append((module_name, package_path / name.replace('.', '/')))
        
        return modules
    
    def _scan_module_for_tools(self, module: Any, module_name: str) -> int:
        """Scan a module for tool functions"""
        count = 0
        
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) and self._is_tool_function(obj):
                try:
                    tool_metadata = self._extract_tool_metadata(obj, module_name)
                    if tool_metadata and self._register_tool(obj, tool_metadata):
                        count += 1
                        self._discovered_tools.add(tool_metadata.name)
                except Exception as e:
                    logger.error(f"Error processing tool {name} in {module_name}: {str(e)}")
        
        return count
    
    def _is_tool_function(self, func: Callable) -> bool:
        """Check if a function is a tool function (has tool metadata)"""
        return hasattr(func, '_tool_metadata') or hasattr(func, '_tool_id')
    
    def _extract_tool_metadata(self, func: Callable, module_name: str) -> Optional[ToolMetadata]:
        """Extract tool metadata from a decorated function"""
        if hasattr(func, '_tool_metadata'):
            metadata = func._tool_metadata
            # Ensure the domain is set correctly
            metadata.domain = self.domain
            return metadata
        return None
    
    def _register_tool(self, func: Callable, metadata: ToolMetadata) -> bool:
        """Register a tool with the registry"""
        try:
            registry = get_tool_registry()
            
            # Check if tool is already registered
            existing = registry.get_tool_by_name(metadata.name)
            if existing:
                logger.debug(f"Tool {metadata.name} already registered, skipping")
                return False
            
            request = RegistrationRequest(
                metadata=metadata,
                handler=f"{metadata.domain}.{func.__name__}"
            )
            
            result = registry.register_tool(request)
            if result.success:
                logger.info(f"Discovered and registered tool: {metadata.name}")
                return True
            else:
                logger.error(f"Failed to register discovered tool {metadata.name}: {result.message}")
                return False
                
        except Exception as e:
            logger.error(f"Error registering tool {metadata.name}: {str(e)}")
            return False
    
    def discover_from_directory(self, directory_path: str) -> int:
        """
        Discover and register tools from a directory.
        
        Args:
            directory_path: Path to the directory containing Python modules
        
        Returns:
            Number of tools discovered and registered
        """
        set_domain_context(self.domain)
        
        path = Path(directory_path)
        if not path.exists():
            logger.error(f"Directory not found: {directory_path}")
            return 0
        
        count = 0
        
        # Find all Python files in the directory
        for py_file in path.rglob('*.py'):
            if py_file.name.startswith('_'):
                continue
                
            try:
                # Convert file path to module name
                rel_path = py_file.relative_to(path)
                module_name = str(rel_path).replace('/', '.').replace('.py', '')
                
                # Import the module
                spec = importlib.util.spec_from_file_location(module_name, str(py_file))
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    count += self._scan_module_for_tools(module, module_name)
            except Exception as e:
                logger.error(f"Error loading {py_file}: {str(e)}")
        
        return count
    
    def get_discovered_tools(self) -> Set[str]:
        """Get the set of discovered tool names"""
        return self._discovered_tools.copy()
    
    def reset(self):
        """Reset the discovery state"""
        self._discovered_tools.clear()


def discover_and_register_domain_tools(domain: str, package_name: str) -> int:
    """
    Convenience function to discover and register all tools for a domain.
    
    Args:
        domain: The domain name
        package_name: The Python package name containing the domain tools
    
    Returns:
        Number of tools discovered and registered
    """
    discovery = ToolDiscovery(domain)
    return discovery.discover_and_register(package_name)


def discover_and_register_from_directory(domain: str, directory_path: str) -> int:
    """
    Convenience function to discover and register tools from a directory.
    
    Args:
        domain: The domain name
        directory_path: Path to the directory containing Python modules
    
    Returns:
        Number of tools discovered and registered
    """
    discovery = ToolDiscovery(domain)
    return discovery.discover_from_directory(directory_path)