"""Deployment Templates for MCP Framework"""
from .arm_template import get_arm_template
from .bicep_template import get_bicep_template
from .parameters import DeploymentParameters

__all__ = [
    'get_arm_template',
    'get_bicep_template', 
    'DeploymentParameters'
]