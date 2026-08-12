"""Azure DevOps Pipeline Generator for MCP Framework"""
import json
from typing import Optional, Dict, Any, List
from .pipeline_config import PipelineConfig, EnvironmentConfig


def get_azure_devops_pipeline(config: Optional[PipelineConfig] = None) -> str:
    """
    Generate an Azure DevOps YAML pipeline for MCP Framework.
    
    Args:
        config: Pipeline configuration (defaults to test configuration)
    
    Returns:
        Azure DevOps YAML pipeline as string
    """
    if config is None:
        config = PipelineConfig(
            project_name="mcp-test",
            repository_name="mcp-platform-framework",
            branch_name="main"
        )
    
    pipeline = {
        "trigger": get_trigger_config(config),
        "pr": get_pr_trigger_config(config),
        "variables": get_variables(config),
        "stages": get_stages(config),
        "resources": get_resources(config)
    }
    
    return yaml.dump(pipeline, sort_keys=False)


def get_trigger_config(config: PipelineConfig) -> Dict[str, Any]:
    """Generate trigger configuration"""
    return {
        "branches": {
            "include": [
                f"{config.branch_name}",
                f"releases/*"
            ]
        },
        "paths": {
            "exclude": [
                "docs/*",
                "README.md",
                ".gitignore",
                "LICENSE"
            ]
        }
    }


def get_pr_trigger_config(config: PipelineConfig) -> Dict[str, Any]:
    """Generate PR trigger configuration"""
    return {
        "branches": {
            "include": [
                f"feature/*",
                f"bugfix/*",
                f"hotfix/*"
            ]
        },
        "paths": {
            "exclude": [
                "docs/*",
                "README.md"
            ]
        }
    }


def get_variables(config: PipelineConfig) -> Dict[str, Any]:
    """Generate pipeline variables"""
    variables = {
        "python.version": "3.11",
        "project.name": config.project_name,
        "repository.name": config.repository_name,
        "branch.name": "$(Build.SourceBranchName)",
        "is.main": "$[[ eq(variables['Build.SourceBranch'], 'refs/heads/' + variables['branch.name']) ]]",
        "is.pr": "$[[ eq(variables['Build.Reason'], 'PullRequest') ]]",
        "is.release": "$[[ startsWith(variables['Build.SourceBranch'], 'refs/tags/') ]]"
    }
    
    # Add environment-specific variables
    for env_name, env_config in config.environments.items():
        variables[f"environment.{env_name}.name"] = env_name
        variables[f"environment.{env_name}.resourceGroup"] = env_config.resource_group
        variables[f"environment.{env_name}.location"] = env_config.location
    
    return variables


def get_resources(config: PipelineConfig) -> Dict[str, Any]:
    """Generate pipeline resources"""
    resources = {
        "repositories": [
            {
                "repository": config.repository_name,
                "type": "git",
                "name": "MCP Platform Framework",
                "trigger": {
                    "branches": {
                        "include": [
                            f"{config.branch_name}"
                        ]
                    }
                }
            }
        ]
    }
    
    # Add container registry if configured
    if config.container_registry:
        resources["containers"] = [
            {
                "container": config.container_registry,
                "endpoint": config.container_registry_endpoint
            }
        ]
    
    return resources


def get_stages(config: PipelineConfig) -> List[Dict[str, Any]]:
    """Generate pipeline stages"""
    stages = []
    
    # 1. Build Stage
    stages.append({
        "stage": "Build",
        "displayName": "Build and Test",
        "dependsOn": [],
        "condition": "succeeded()",
        "jobs": [
            get_build_job(config)
        ]
    })
    
    # 2. Test Stage
    stages.append({
        "stage": "Test",
        "displayName": "Run Tests",
        "dependsOn": ["Build"],
        "condition": "succeeded()",
        "jobs": [
            get_test_job(config)
        ]
    })
    
    # 3. Security Scan Stage
    stages.append({
        "stage": "Security",
        "displayName": "Security Scanning",
        "dependsOn": ["Build"],
        "condition": "succeeded()",
        "jobs": [
            get_security_job(config)
        ]
    })
    
    # 4. Deployment Stages for each environment
    for env_name, env_config in config.environments.items():
        if env_config.deploy:
            stage_name = f"Deploy_{env_name.capitalize()}"
            stages.append({
                "stage": stage_name,
                "displayName": f"Deploy to {env_name}",
                "dependsOn": ["Test", "Security"],
                "condition": get_environment_condition(env_name, config),
                "jobs": [
                    get_deploy_job(config, env_name, env_config)
                ]
            })
    
    return stages


def get_build_job(config: PipelineConfig) -> Dict[str, Any]:
    """Generate build job configuration"""
    return {
        "job": "Build",
        "displayName": "Build MCP Framework",
        "pool": {
            "vmImage": "ubuntu-latest"
        },
        "workspace": {
            "clean": "all"
        },
        "steps": [
            {
                "task": "UsePythonVersion@0",
                "displayName": "Use Python $(python.version)",
                "inputs": {
                    "versionSpec": "$(python.version)",
                    "addToPath": true
                }
            },
            {
                "bash": "python -m pip install --upgrade pip",
                "displayName": "Upgrade pip"
            },
            {
                "bash": "pip install -r requirements.txt",
                "displayName": "Install dependencies"
            },
            {
                "bash": "pip install -r requirements-dev.txt",
                "displayName": "Install dev dependencies",
                "condition": "eq(variables.is.main, true)"
            },
            {
                "bash": "python -m pytest tests/unit/ --cov=platform --cov-report=xml --junitxml=test-results/unit.xml",
                "displayName": "Run unit tests",
                "continueOnError": True
            },
            {
                "bash": "python -m pytest tests/integration/ --junitxml=test-results/integration.xml",
                "displayName": "Run integration tests",
                "continueOnError": True,
                "condition": "eq(variables.is.main, true)"
            },
            {
                "task": "PublishTestResults@2",
                "displayName": "Publish Unit Test Results",
                "inputs": {
                    "testResultsFormat": "JUnit",
                    "testResultsFiles": "test-results/unit.xml",
                    "failTaskOnFailedTests": False
                },
                "condition": "always()"
            },
            {
                "task": "PublishTestResults@2",
                "displayName": "Publish Integration Test Results",
                "inputs": {
                    "testResultsFormat": "JUnit",
                    "testResultsFiles": "test-results/integration.xml",
                    "failTaskOnFailedTests": False
                },
                "condition": "always()"
            },
            {
                "task": "PublishCodeCoverageResults@1",
                "displayName": "Publish Code Coverage",
                "inputs": {
                    "codeCoverageTool": "Cobertura",
                    "summaryFileLocation": "$(System.DefaultWorkingDirectory)/**/coverage.xml",
                    "reportDirectory": "$(System.DefaultWorkingDirectory)/coverage"
                },
                "condition": "eq(variables.is.main, true)"
            },
            {
                "bash": "python setup.py sdist bdist_wheel",
                "displayName": "Build distribution packages",
                "condition": "eq(variables.is.release, true)"
            },
            {
                "task": "PublishPipelineArtifact@1",
                "displayName": "Publish Build Artifacts",
                "inputs": {
                    "targetPath": "$(Build.ArtifactStagingDirectory)",
                    "artifact": "drop",
                    "publishLocation": "pipeline"
                }
            }
        ]
    }


def get_test_job(config: PipelineConfig) -> Dict[str, Any]:
    """Generate test job configuration"""
    return {
        "job": "Test",
        "displayName": "Run All Tests",
        "pool": {
            "vmImage": "ubuntu-latest"
        },
        "steps": [
            {
                "task": "UsePythonVersion@0",
                "displayName": "Use Python $(python.version)",
                "inputs": {
                    "versionSpec": "$(python.version)",
                    "addToPath": true
                }
            },
            {
                "bash": "pip install -r requirements.txt",
                "displayName": "Install dependencies"
            },
            {
                "bash": "pip install -r requirements-dev.txt",
                "displayName": "Install dev dependencies"
            },
            {
                "bash": "python -m pytest tests/ --cov=platform --cov-report=xml --junitxml=test-results/all.xml -v",
                "displayName": "Run all tests with coverage"
            },
            {
                "task": "PublishTestResults@2",
                "displayName": "Publish Test Results",
                "inputs": {
                    "testResultsFormat": "JUnit",
                    "testResultsFiles": "test-results/all.xml",
                    "failTaskOnFailedTests": True
                }
            },
            {
                "task": "PublishCodeCoverageResults@1",
                "displayName": "Publish Code Coverage",
                "inputs": {
                    "codeCoverageTool": "Cobertura",
                    "summaryFileLocation": "$(System.DefaultWorkingDirectory)/**/coverage.xml"
                }
            }
        ]
    }


def get_security_job(config: PipelineConfig) -> Dict[str, Any]:
    """Generate security scanning job configuration"""
    return {
        "job": "Security",
        "displayName": "Security Scanning",
        "pool": {
            "vmImage": "ubuntu-latest"
        },
        "steps": [
            {
                "task": "UsePythonVersion@0",
                "displayName": "Use Python $(python.version)",
                "inputs": {
                    "versionSpec": "$(python.version)",
                    "addToPath": true
                }
            },
            {
                "bash": "pip install safety bandit",
                "displayName": "Install security tools"
            },
            {
                "bash": "safety check --full-report",
                "displayName": "Run Safety dependency scan",
                "continueOnError": True
            },
            {
                "bash": "bandit -r platform/ -f json -o bandit-results.json",
                "displayName": "Run Bandit code scan",
                "continueOnError": True
            },
            {
                "task": "PublishPipelineArtifact@1",
                "displayName": "Publish Security Reports",
                "inputs": {
                    "targetPath": "$(Build.SourcesDirectory)",
                    "artifact": "security-reports",
                    "publishLocation": "pipeline"
                },
                "condition": "always()"
            }
        ]
    }


def get_deploy_job(config: PipelineConfig, env_name: str, env_config: EnvironmentConfig) -> Dict[str, Any]:
    """Generate deployment job configuration"""
    job_name = f"Deploy_{env_name}"
    
    return {
        "job": job_name,
        "displayName": f"Deploy to {env_name}",
        "pool": {
            "vmImage": "ubuntu-latest"
        },
        "environment": env_config.environment_name,
        "steps": [
            {
                "task": "UsePythonVersion@0",
                "displayName": "Use Python $(python.version)",
                "inputs": {
                    "versionSpec": "$(python.version)",
                    "addToPath": true
                }
            },
            {
                "bash": "pip install -r requirements.txt",
                "displayName": "Install dependencies"
            },
            {
                "task": "AzureCLI@2",
                "displayName": "Login to Azure",
                "inputs": {
                    "azureSubscription": env_config.azure_service_connection,
                    "scriptType": "bash",
                    "scriptLocation": "inlineScript",
                    "inlineScript": "az account show"
                }
            },
            {
                "task": "AzureCLI@2",
                "displayName": "Deploy Infrastructure",
                "inputs": {
                    "azureSubscription": env_config.azure_service_connection,
                    "scriptType": "bash",
                    "scriptLocation": "inlineScript",
                    "inlineScript": f"""az deployment group create \\
    --resource-group {env_config.resource_group} \\
    --template-file deployment/mcp-deployment.bicep \\
    --parameters \\
        projectName={config.project_name} \\
        environment={env_name} \\
        location={env_config.location} \\
        mcpDomain={env_config.mcp_domain} \\
        enableTelemetry={str(env_config.enable_telemetry).lower()} \\
        enableAudit={str(env_config.enable_audit).lower()} \\
        enableAuthentication={str(env_config.enable_authentication).lower()} \\
        enableAuthorization={str(env_config.enable_authorization).lower()} \\
        enableClassification={str(env_config.enable_classification).lower()}"""
                }
            },
            {
                "task": "AzureCLI@2",
                "displayName": "Deploy Function App",
                "inputs": {
                    "azureSubscription": env_config.azure_service_connection,
                    "scriptType": "bash",
                    "scriptLocation": "inlineScript",
                    "inlineScript": f"""az functionapp deployment source config-zip \\
    --resource-group {env_config.resource_group} \\
    --name {config.project_name}-{env_name}-func \\
    --src $(Build.ArtifactStagingDirectory)/drop/functionapp.zip"""
                }
            },
            {
                "task": "AzureCLI@2",
                "displayName": "Configure Function App Settings",
                "inputs": {
                    "azureSubscription": env_config.azure_service_connection,
                    "scriptType": "bash",
                    "scriptLocation": "inlineScript",
                    "inlineScript": f"""# Set environment-specific configuration
az functionapp config appsettings set \\
    --resource-group {env_config.resource_group} \\
    --name {config.project_name}-{env_name}-func \\
    --settings MCP_ENVIRONMENT={env_name}"""
                }
            },
            {
                "task": "AzureCLI@2",
                "displayName": "Run Post-Deployment Tests",
                "inputs": {
                    "azureSubscription": env_config.azure_service_connection,
                    "scriptType": "bash",
                    "scriptLocation": "inlineScript",
                    "inlineScript": """# Run health check
curl -f https://$(az functionapp show --resource-group ${RESOURCE_GROUP} --name ${FUNCTION_APP_NAME} --query defaultHostName -o tsv) || exit 1
"""
                },
                "condition": "eq(variables.is.main, true)"
            }
        ]
    }


def get_environment_condition(env_name: str, config: PipelineConfig) -> str:
    """Generate condition for environment deployment"""
    if env_name == "dev":
        return "succeeded()"
    elif env_name == "test":
        return "and(succeeded(), eq(variables.is.main, true))"
    elif env_name == "prod":
        return "and(succeeded(), eq(variables.is.release, true))"
    else:
        return "succeeded()"


def save_azure_devops_pipeline(file_path: str, config: Optional[PipelineConfig] = None):
    """
    Save Azure DevOps pipeline to a file.
    
    Args:
        file_path: Path to save the pipeline
        config: Pipeline configuration
    """
    import yaml
    pipeline = yaml.safe_load(get_azure_devops_pipeline(config))
    
    with open(file_path, 'w') as f:
        yaml.dump(pipeline, f, sort_keys=False)
    print(f"Azure DevOps pipeline saved to {file_path}")


# Import yaml for template generation
try:
    import yaml
except ImportError:
    print("PyYAML not installed. Install with: pip install pyyaml")
    yaml = None


if __name__ == "__main__" and yaml:
    # Example usage
    from .pipeline_config import PipelineConfig, EnvironmentConfig
    
    config = PipelineConfig(
        project_name="mcp-donor-management",
        repository_name="mcp-donor-management",
        branch_name="main",
        environments={
            "dev": EnvironmentConfig(
                resource_group="mcp-donor-management-dev-rg",
                location="eastus",
                mcp_domain="DonorManagement",
                deploy=True,
                environment_name="Development",
                azure_service_connection="Azure-Dev-Service-Connection"
            ),
            "test": EnvironmentConfig(
                resource_group="mcp-donor-management-test-rg",
                location="eastus",
                mcp_domain="DonorManagement",
                deploy=True,
                environment_name="Test",
                azure_service_connection="Azure-Test-Service-Connection"
            ),
            "prod": EnvironmentConfig(
                resource_group="mcp-donor-management-prod-rg",
                location="eastus",
                mcp_domain="DonorManagement",
                deploy=True,
                environment_name="Production",
                azure_service_connection="Azure-Prod-Service-Connection"
            )
        }
    )
    
    pipeline = get_azure_devops_pipeline(config)
    print("Generated Azure DevOps Pipeline:")
    print(pipeline[:1000] + "..." if len(pipeline) > 1000 else pipeline)
    
    # Save to file
    save_azure_devops_pipeline("azure-pipelines.yml", config)