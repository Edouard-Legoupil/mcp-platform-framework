"""Template Generator for MCP Framework"""
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from .domain_template import DomainTemplate, create_domain_template


class TemplateGenerator:
    """
    Generator for creating domain templates and generating files.
    
    This class can create complete domain repository structures based on templates.
    """
    
    def __init__(self, template: Optional[DomainTemplate] = None):
        """
        Initialize the template generator.
        
        Args:
            template: Domain template to use (creates default if None)
        """
        self.template = template or create_domain_template(
            name="DefaultDomain",
            description="Default domain template"
        )
    
    def generate_directory_structure(self, output_dir: str):
        """
        Generate the complete directory structure for a domain.
        
        Args:
            output_dir: Directory to create the structure in
        """
        structure = self.template.get_directory_structure()
        self._create_structure(structure, Path(output_dir))
    
    def _create_structure(self, structure: Dict[str, Any], base_path: Path):
        """
        Recursively create directory structure and files.
        
        Args:
            structure: Dictionary representing the structure
            base_path: Base path to create in
        """
        for name, content in structure.items():
            path = base_path / name
            
            if isinstance(content, dict):
                # This is a directory
                path.mkdir(parents=True, exist_ok=True)
                self._create_structure(content, path)
            else:
                # This is a file
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, 'w') as f:
                    f.write(content)
    
    def generate_template_files(self, output_dir: str):
        """
        Generate template configuration files.
        
        Args:
            output_dir: Directory to save template files
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save template configuration
        template_file = output_path / f"{self.template.repository_name}-template.json"
        self.template.save_to_file(str(template_file))
        
        # Save directory structure
        structure_file = output_path / f"{self.template.repository_name}-structure.json"
        with open(structure_file, 'w') as f:
            json.dump(self.template.get_directory_structure(), f, indent=2)
    
    def generate_from_template_file(self, template_file: str, output_dir: str):
        """
        Generate domain structure from a template file.
        
        Args:
            template_file: Path to template JSON file
            output_dir: Directory to create the structure in
        """
        template = DomainTemplate.from_file(template_file)
        self.template = template
        self.generate_directory_structure(output_dir)
    
    def create_domain_repository(self, output_dir: str, domain_name: str, **kwargs):
        """
        Create a complete domain repository.
        
        Args:
            output_dir: Directory to create the repository in
            domain_name: Name of the domain
            **kwargs: Additional template parameters
        """
        # Create the template
        self.template = create_domain_template(
            name=domain_name,
            **kwargs
        )
        
        # Generate the directory structure
        self.generate_directory_structure(output_dir)
        
        # Also save the template configuration
        template_dir = Path(output_dir) / ".mcp-template"
        template_dir.mkdir(parents=True, exist_ok=True)
        
        template_file = template_dir / "template.json"
        self.template.save_to_file(str(template_file))
        
        return str(template_file)
    
    def validate_template(self) -> List[str]:
        """
        Validate the current template.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required fields
        if not self.template.name:
            errors.append("Domain name is required")
        
        if not self.template.description:
            errors.append("Domain description is required")
        
        # Check repository name
        if not self.template.repository_name:
            errors.append("Repository name is required")
        
        # Check environments
        if not self.template.environments:
            errors.append("At least one environment is required")
        else:
            for env_name, env_config in self.template.environments.items():
                if not env_config.get('resource_group'):
                    errors.append(f"Environment {env_name} missing resource_group")
                if not env_config.get('location'):
                    errors.append(f"Environment {env_name} missing location")
        
        return errors
    
    def get_template_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current template.
        
        Returns:
            Dictionary with template summary
        """
        return {
            'name': self.template.name,
            'description': self.template.description,
            'version': self.template.version,
            'repository_name': self.template.repository_name,
            'mcp_version': self.template.mcp_version,
            'features': {
                'telemetry': self.template.enable_telemetry,
                'audit': self.template.enable_audit,
                'authentication': self.template.enable_authentication,
                'authorization': self.template.enable_authorization,
                'classification': self.template.enable_classification,
                'auto_discovery': self.template.auto_discover_tools
            },
            'environments': list(self.template.environments.keys()),
            'tool_paths': self.template.tool_paths,
            'dependencies_count': len(self.template.dependencies),
            'dev_dependencies_count': len(self.template.dev_dependencies)
        }


def generate_domain_template(
    domain_name: str,
    description: str,
    output_dir: str,
    author: str = "",
    maintainer: str = "",
    **kwargs
) -> str:
    """
    Generate a complete domain template and save to directory.
    
    Args:
        domain_name: Name of the domain
        description: Domain description
        output_dir: Directory to create the template in
        author: Author name
        maintainer: Maintainer email
        **kwargs: Additional template parameters
    
    Returns:
        Path to the generated template file
    """
    generator = TemplateGenerator()
    return generator.create_domain_repository(
        output_dir=output_dir,
        domain_name=domain_name,
        description=description,
        author=author,
        maintainer=maintainer,
        **kwargs
    )


def generate_template_files(
    domain_name: str,
    description: str,
    output_dir: str,
    **kwargs
) -> Dict[str, str]:
    """
    Generate template configuration files without creating full structure.
    
    Args:
        domain_name: Name of the domain
        description: Domain description
        output_dir: Directory to save template files
        **kwargs: Additional template parameters
    
    Returns:
        Dictionary with paths to generated files
    """
    template = create_domain_template(
        name=domain_name,
        description=description,
        **kwargs
    )
    
    generator = TemplateGenerator(template)
    generator.generate_template_files(output_dir)
    
    output_path = Path(output_dir)
    return {
        'template_file': str(output_path / f"{template.repository_name}-template.json"),
        'structure_file': str(output_path / f"{template.repository_name}-structure.json")
    }


if __name__ == "__main__":
    # Example usage
    print("Generating domain template...")
    
    # Create a donor management domain template
    template_file = generate_domain_template(
        domain_name="DonorManagement",
        description="Domain for managing donor information and relationships",
        output_dir="./donor-management-template",
        author="MCP Team",
        maintainer="mcp-team@example.com",
        mcp_version="1.0.0",
        enable_telemetry=True,
        enable_audit=True,
        enable_authentication=True,
        enable_authorization=True,
        enable_classification=True,
        auto_discover_tools=True
    )
    
    print(f"Domain template generated successfully!")
    print(f"Template configuration saved to: {template_file}")
    print(f"Repository structure created in: ./donor-management-template")