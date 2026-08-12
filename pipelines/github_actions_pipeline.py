"""GitHub Actions Pipeline Generator for MCP Framework"""
from typing import Optional, Dict, Any, List
from .pipeline_config import PipelineConfig, EnvironmentConfig


def get_github_actions_pipeline(config: Optional[PipelineConfig] = None) -> str:
    """
    Generate a GitHub Actions YAML pipeline for MCP Framework.
    
    Args:
        config: Pipeline configuration (defaults to test configuration)
    
    Returns:
        GitHub Actions YAML pipeline as string
    """
    if config is None:
        config = PipelineConfig(
            project_name="mcp-test",
            repository_name="mcp-platform-framework",
            branch_name="main"
        )
    
    lines = []
    
    # Add header
    lines.append("name: MCP Platform Framework CI/CD")
    lines.append("")
    lines.append("on:")
    lines.append("  push:")
    lines.append("    branches: [ " + ", ".join([f"'{config.branch_name}'", "'releases/**'"]) + "]")
    lines.append("    paths-ignore:")
    lines.append("      - 'docs/**'")
    lines.append("      - 'README.md'")
    lines.append("      - '.gitignore'")
    lines.append("      - 'LICENSE'")
    lines.append("")
    lines.append("  pull_request:")
    lines.append("    branches: [ " + ", ".join(["'feature/**'", "'bugfix/**'", "'hotfix/**'"]) + "]")
    lines.append("    paths-ignore:")
    lines.append("      - 'docs/**'")
    lines.append("      - 'README.md'")
    lines.append("")
    
    # Add environment variables
    lines.extend(get_environment_variables(config))
    lines.append("")
    
    # Add jobs
    lines.extend(get_jobs(config))
    
    return "\n".join(lines)


def get_environment_variables(config: PipelineConfig) -> List[str]:
    """Generate environment variables"""
    lines = [
        "env:",
        f"  PROJECT_NAME: {config.project_name}",
        f"  REPOSITORY_NAME: {config.repository_name}",
        f"  PYTHON_VERSION: {config.python_version}",
        f"  TEST_COVERAGE_THRESHOLD: {config.test_coverage_threshold}",
        f"  SECURITY_SCAN_ENABLED: {str(config.security_scan_enabled).lower()}"
    ]
    
    return lines


def get_jobs(config: PipelineConfig) -> List[str]:
    """Generate GitHub Actions jobs"""
    jobs = []
    
    # 1. Build Job
    jobs.extend(get_build_job(config))
    jobs.append("")
    
    # 2. Test Job
    jobs.extend(get_test_job(config))
    jobs.append("")
    
    # 3. Security Job
    jobs.extend(get_security_job(config))
    jobs.append("")
    
    # 4. Deployment Jobs for each environment
    for env_name, env_config in config.environments.items():
        if env_config.deploy:
            jobs.extend(get_deploy_job(config, env_name, env_config))
            jobs.append("")
    
    return jobs


def get_build_job(config: PipelineConfig) -> List[str]:
    """Generate build job"""
    lines = [
        "build:",
        "  name: Build and Package",
        "  runs-on: ubuntu-latest",
        "  strategy:",
        "    matrix:",
        f"      python-version: [{config.python_version}]",
        "  ",
        "  steps:",
        "    - name: Checkout repository",
        "      uses: actions/checkout@v4",
        "      with:",
        "        fetch-depth: 0",
        "    ",
        "    - name: Set up Python",
        "      uses: actions/setup-python@v4",
        "      with:",
        "        python-version: ${{{ matrix.python-version }}}",
        "        cache: 'pip'",
        "    ",
        "    - name: Upgrade pip",
        "      run: python -m pip install --upgrade pip",
        "    ",
        "    - name: Install dependencies",
        "      run: pip install -r requirements.txt",
        "    ",
        "    - name: Install dev dependencies",
        "      if: github.ref == 'refs/heads/' + env.BRANCH_NAME",
        "      run: pip install -r requirements-dev.txt",
        "    ",
        "    - name: Run unit tests",
        "      run: |",
        "        python -m pytest tests/unit/ --cov=platform --cov-report=xml --junitxml=test-results/unit.xml",
        "      continue-on-error: true",
        "    ",
        "    - name: Run integration tests",
        "      if: github.ref == 'refs/heads/' + env.BRANCH_NAME",
        "      run: python -m pytest tests/integration/ --junitxml=test-results/integration.xml",
        "      continue-on-error: true",
        "    ",
        "    - name: Upload unit test results",
        "      if: always()",
        "      uses: actions/upload-artifact@v3",
        "      with:",
        "        name: unit-test-results",
        "        path: test-results/unit.xml",
        "    ",
        "    - name: Upload integration test results",
        "      if: always()",
        "      uses: actions/upload-artifact@v3",
        "      with:",
        "        name: integration-test-results",
        "        path: test-results/integration.xml",
        "    ",
        "    - name: Upload coverage report",
        "      if: github.ref == 'refs/heads/' + env.BRANCH_NAME",
        "      uses: actions/upload-artifact@v3",
        "      with:",
        "        name: coverage-report",
        "        path: coverage/",
        "    ",
        "    - name: Build distribution packages",
        "      if: startsWith(github.ref, 'refs/tags/')",
        "      run: python setup.py sdist bdist_wheel",
        "    ",
        "    - name: Upload build artifacts",
        "      uses: actions/upload-artifact@v3",
        "      with:",
        "        name: drop",
        "        path: dist/"
    ]
    
    return lines


def get_test_job(config: PipelineConfig) -> List[str]:
    """Generate test job"""
    lines = [
        "test:",
        "  name: Run All Tests",
        "  needs: build",
        "  runs-on: ubuntu-latest",
        "  ",
        "  steps:",
        "    - name: Checkout repository",
        "      uses: actions/checkout@v4",
        "    ",
        "    - name: Set up Python",
        "      uses: actions/setup-python@v4",
        "      with:",
        f"        python-version: {config.python_version}",
        "        cache: 'pip'",
        "    ",
        "    - name: Install dependencies",
        "      run: pip install -r requirements.txt -r requirements-dev.txt",
        "    ",
        "    - name: Run all tests with coverage",
        "      run: |",
        "        python -m pytest tests/ --cov=platform --cov-report=xml --junitxml=test-results/all.xml -v",
        "    ",
        "    - name: Upload test results",
        "      if: always()",
        "      uses: actions/upload-artifact@v3",
        "      with:",
        "        name: test-results",
        "        path: test-results/",
        "    ",
        "    - name: Upload coverage report",
        "      uses: actions/upload-artifact@v3",
        "      with:",
        "        name: coverage-report",
        "        path: coverage/"
    ]
    
    return lines


def get_security_job(config: PipelineConfig) -> List[str]:
    """Generate security scanning job"""
    lines = [
        "security:",
        "  name: Security Scanning",
        "  needs: build",
        "  runs-on: ubuntu-latest",
        "  ",
        "  steps:",
        "    - name: Checkout repository",
        "      uses: actions/checkout@v4",
        "    ",
        "    - name: Set up Python",
        "      uses: actions/setup-python@v4",
        "      with:",
        f"        python-version: {config.python_version}",
        "        cache: 'pip'",
        "    ",
        "    - name: Install security tools",
        "      run: pip install safety bandit",
        "    ",
        "    - name: Run Safety dependency scan",
        "      run: safety check --full-report",
        "      continue-on-error: true",
        "    ",
        "    - name: Run Bandit code scan",
        "      run: bandit -r platform/ -f json -o bandit-results.json",
        "      continue-on-error: true",
        "    ",
        "    - name: Upload security reports",
        "      if: always()",
        "      uses: actions/upload-artifact@v3",
        "      with:",
        "        name: security-reports",
        "        path: ."
    ]
    
    return lines


def get_deploy_job(config: PipelineConfig, env_name: str, env_config: EnvironmentConfig) -> List[str]:
    """Generate deployment job"""
    job_name = f"deploy_{env_name}"
    
    lines = [
        f"{job_name}:",
        f"  name: Deploy to {env_name.capitalize()}",
        "  needs: [test, security]",
        f"  if: {get_github_environment_condition(env_name, config)}",
        "  runs-on: ubuntu-latest",
        f"  environment: {env_config.environment_name}",
        "  ",
        "  steps:",
        "    - name: Checkout repository",
        "      uses: actions/checkout@v4",
        "    ",
        "    - name: Set up Python",
        "      uses: actions/setup-python@v4",
        "      with:",
        f"        python-version: {config.python_version}",
        "        cache: 'pip'",
        "    ",
        "    - name: Install dependencies",
        "      run: pip install -r requirements.txt",
        "    ",
        "    - name: Login to Azure",
        "      uses: azure/login@v1",
        "      with:",
        "        creds: ${{{ secrets.AZURE_CREDENTIALS }}",
        "    ",
        "    - name: Deploy Infrastructure",
        "      run: |",
        f"        az deployment group create \\",
        f"          --resource-group {env_config.resource_group} \\",
        f"          --template-file deployment/mcp-deployment.bicep \\",
        f"          --parameters \\",
        f"            projectName={config.project_name} \\",
        f"            environment={env_name} \\",
        f"            location={env_config.location} \\",
        f"            mcpDomain={env_config.mcp_domain} \\",
        f"            enableTelemetry={str(env_config.enable_telemetry).lower()} \\",
        f"            enableAudit={str(env_config.enable_audit).lower()} \\",
        f"            enableAuthentication={str(env_config.enable_authentication).lower()} \\",
        f"            enableAuthorization={str(env_config.enable_authorization).lower()} \\",
        f"            enableClassification={str(env_config.enable_classification).lower()}",
        "    ",
        "    - name: Deploy Function App",
        "      run: |",
        f"        az functionapp deployment source config-zip \\",
        f"          --resource-group {env_config.resource_group} \\",
        f"          --name {config.project_name}-{env_name}-func \\",
        "          --src drop/functionapp.zip",
        "    ",
        "    - name: Configure Function App Settings",
        "      run: |",
        f"        az functionapp config appsettings set \\",
        f"          --resource-group {env_config.resource_group} \\",
        f"          --name {config.project_name}-{env_name}-func \\",
        f"          --settings MCP_ENVIRONMENT={env_name}",
        "    ",
        "    - name: Run Post-Deployment Tests",
        "      if: github.ref == 'refs/heads/' + env.BRANCH_NAME",
        "      run: |",
        "        # Run health check",
        f"        curl -f https://{config.project_name}-{env_name}-func.azurewebsites.net/api/health || exit 1"
    ]
    
    return lines


def get_github_environment_condition(env_name: str, config: PipelineConfig) -> str:
    """Generate condition for GitHub Actions environment deployment"""
    if env_name == "dev":
        return "success()"
    elif env_name == "test":
        return "success() && github.ref == 'refs/heads/' + env.BRANCH_NAME"
    elif env_name == "prod":
        return "success() && startsWith(github.ref, 'refs/tags/')"
    else:
        return "success()"


def save_github_actions_pipeline(file_path: str, config: Optional[PipelineConfig] = None):
    """
    Save GitHub Actions pipeline to a file.
    
    Args:
        file_path: Path to save the pipeline
        config: Pipeline configuration
    """
    pipeline = get_github_actions_pipeline(config)
    
    with open(file_path, 'w') as f:
        f.write(pipeline)
    print(f"GitHub Actions pipeline saved to {file_path}")


if __name__ == "__main__":
    # Example usage
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
                environment_name="Development"
            ),
            "test": EnvironmentConfig(
                resource_group="mcp-donor-management-test-rg",
                location="eastus",
                mcp_domain="DonorManagement",
                deploy=True,
                environment_name="Test"
            ),
            "prod": EnvironmentConfig(
                resource_group="mcp-donor-management-prod-rg",
                location="eastus",
                mcp_domain="DonorManagement",
                deploy=True,
                environment_name="Production"
            )
        }
    )
    
    pipeline = get_github_actions_pipeline(config)
    print("Generated GitHub Actions Pipeline:")
    print(pipeline[:1000] + "..." if len(pipeline) > 1000 else pipeline)
    
    # Save to file
    save_github_actions_pipeline(".github/workflows/mcp-ci-cd.yml", config)