"""CI/CD Pipelines for MCP Framework"""
from .azure_devops_pipeline import get_azure_devops_pipeline
from .github_actions_pipeline import get_github_actions_pipeline

__all__ = [
    'get_azure_devops_pipeline',
    'get_github_actions_pipeline'
]