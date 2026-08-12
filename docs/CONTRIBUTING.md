# Contributing to MCP Platform Framework

## 🎉 Welcome Contributors!

Thank you for your interest in contributing to the MCP Platform Framework! This guide will help you get started with contributing to the project.

---

## 📋 Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before contributing.

---

## 🚀 Getting Started

### Prerequisites

Before you can contribute, ensure you have the following installed:

- **Python**: Version 3.9, 3.10, or 3.11
- **Git**: Version 2.30.0 or higher
- **Azure CLI**: Version 2.50.0 or higher
- **Azure Functions Core Tools**: Version 4.x
- **Docker**: For container-based development (optional)

### Setting Up Your Development Environment

1. **Fork the repository**: Create your own fork of the repository
2. **Clone your fork**: Clone your fork to your local machine
   ```bash
   git clone https://github.com/your-username/mcp-platform-framework.git
   cd mcp-platform-framework
   ```

3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

5. **Set up pre-commit hooks** (optional but recommended):
   ```bash
   pip install pre-commit
   pre-commit install
   ```

---

## 📝 How to Contribute

### Reporting Issues

If you find a bug or have a feature request, please [open an issue](https://github.com/unhcr/mcp-platform-framework/issues) in the repository. When reporting an issue, please include:

- A clear and descriptive title
- A detailed description of the issue
- Steps to reproduce the issue
- Expected vs. actual behavior
- Relevant logs or error messages
- Your environment (Python version, OS, etc.)
- Any other context that might be helpful

### Suggesting Enhancements

If you have an idea for a new feature or enhancement, please [open an issue](https://github.com/unhcr/mcp-platform-framework/issues) with the following information:

- A clear description of the feature
- The problem it solves or the value it provides
- Any relevant use cases or examples
- Potential implementation approaches (if you have ideas)

### Contributing Code

We welcome code contributions! Here's how to contribute:

1. **Find an issue**: Look for issues labeled `good first issue` or `help wanted`
2. **Comment on the issue**: Let others know you're working on it
3. **Create a branch**: Create a feature branch from the `main` branch
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/your-feature-name
   ```

4. **Make your changes**: Implement your feature or bug fix
5. **Write tests**: Add tests for your changes
6. **Update documentation**: Update relevant documentation
7. **Run tests**: Ensure all tests pass
   ```bash
   python -m pytest tests/ --cov=platform --cov-report=html
   ```

8. **Run linting**: Ensure your code follows our style guidelines
   ```bash
   python -m flake8 platform/
   python -m black --check platform/
   python -m isort --check platform/
   ```

9. **Commit your changes**: Use conventional commit messages
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

10. **Push your changes**: Push your branch to your fork
    ```bash
    git push origin feature/your-feature-name
    ```

11. **Open a Pull Request**: Open a PR from your branch to the `main` branch of the original repository

---

## 📁 Project Structure

```
mcp-platform-framework/
├── .github/                  # GitHub configuration
│   ├── workflows/           # GitHub Actions workflows
│   └── ISSUE_TEMPLATE/      # Issue templates
├── docs/                    # Documentation
│   ├── architecture/       # Architecture documentation
│   ├── deployment/         # Deployment documentation
│   ├── getting-started/    # Getting started guides
│   ├── modules/            # Module documentation
│   └── examples/           # Example documentation
├── platform/                # MCP Platform Framework
│   ├── auth/               # Authentication module
│   ├── authorization/      # Authorization module
│   ├── telemetry/          # Telemetry module
│   ├── audit/              # Audit logging module
│   ├── errors/             # Error handling module
│   ├── classification/    # Data classification module
│   ├── registration/       # Tool registration module
│   ├── connectivity/       # Fabric connectivity module
│   ├── config/             # Configuration management
│   ├── template/           # Template system
│   ├── catalog/            # Catalog integration module
│   ├── keyvault/           # Key Vault integration module
│   ├── docs/               # Documentation generator module
│   └── framework.py        # Main framework file
├── examples/                # Example implementations
│   └── donor_management/   # Example domain implementation
├── azure_functions/        # Azure Functions integration
│   ├── mcp_http_trigger/   # HTTP trigger implementation
│   └── mcp_tool_trigger/   # Tool trigger implementation
├── deployment/             # Deployment scripts and templates
│   ├── arm_template.py      # ARM template generator
│   ├── bicep_template.py    # Bicep template generator
│   └── parameters.py        # Parameter handling
├── tests/                  # Tests
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── .gitignore              # Git ignore file
├── README.md               # Project README
├── pyproject.toml          # Project configuration
├── requirements.txt        # Production dependencies
└── requirements-dev.txt    # Development dependencies
```

---

## 🎯 Contribution Guidelines

### Code Style

We follow the following code style guidelines:

- **PEP 8**: Follow [PEP 8](https://peps.python.org/pep-0008/) style guide
- **Type Hints**: Use type hints for all function parameters and return values
- **Docstrings**: Use Google-style docstrings for all public functions and classes
- **Line Length**: Maximum line length of 88 characters
- **Imports**: Group imports by type (standard library, third-party, local) with a blank line between each group

### Formatting

We use the following tools for code formatting:

- **Black**: For code formatting
- **isort**: For import sorting
- **flake8**: For linting

Run the following commands to format and lint your code:

```bash
# Format code
python -m black platform/

# Sort imports
python -m isort platform/

# Lint code
python -m flake8 platform/
```

### Testing

We use `pytest` for testing. All contributions should include tests for new functionality and ensure existing tests continue to pass.

```bash
# Run all tests
python -m pytest tests/

# Run tests with coverage
python -m pytest tests/ --cov=platform --cov-report=html

# Run specific test file
python -m pytest tests/unit/test_auth.py

# Run specific test
python -m pytest tests/unit/test_auth.py::test_authentication
```

### Documentation

All public APIs should be documented. Documentation should be:

- **Clear and concise**: Easy to understand
- **Comprehensive**: Cover all important aspects
- **Accurate**: Reflect the actual behavior of the code
- **Up-to-date**: Kept current with code changes

Documentation should include:

- **Purpose**: What the code does and why it exists
- **Usage**: How to use the code with examples
- **Parameters**: Description of all parameters
- **Returns**: Description of return values
- **Exceptions**: Description of exceptions that may be raised

### Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/) for commit messages. The following types are commonly used:

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc.)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests
- `chore`: Changes to the build process or auxiliary tools and libraries such as documentation generation

Example commit messages:

```
feat: add support for Azure Key Vault integration
fix: resolve authentication error in Entra ID module
docs: update deployment documentation for Function Apps
docs: add FAQ for common issues
style: format code with black and isort
refactor: extract authentication logic into separate module
test: add unit tests for catalog client
chore: update dependencies in requirements.txt
```

### Pull Requests

When opening a Pull Request, please:

1. **Use a clear title**: Describe the purpose of the PR
2. **Write a detailed description**: Explain what the PR does and why it's needed
3. **Reference related issues**: Link to any related issues
4. **Include screenshots** (if applicable): For UI changes or visual outputs
5. **Follow the PR template**: Fill out all sections of the PR template

Your PR will be reviewed by the maintainers. Please be responsive to feedback and be willing to make changes to your PR.

---

## 🔍 Code Review Process

All contributions will go through a code review process. Here's what to expect:

1. **Initial Review**: A maintainer will review your PR within a few business days
2. **Feedback**: You may receive feedback or requests for changes
3. **Revisions**: Make the requested changes and push them to your branch
4. **Approval**: Once all feedback is addressed, your PR will be approved
5. **Merge**: A maintainer will merge your PR into the `main` branch

### Review Criteria

Your PR will be reviewed for:

- **Functionality**: Does the code work as intended?
- **Code Quality**: Does the code follow our style guidelines?
- **Tests**: Are there adequate tests for the new functionality?
- **Documentation**: Is the code and any new features properly documented?
- **Performance**: Does the code perform well?
- **Security**: Are there any security concerns?
- **Compatibility**: Does the code work with existing functionality?

---

## 🏆 Recognition

All contributors will be recognized for their contributions. We maintain a list of contributors in the project's `CONTRIBUTORS.md` file (if one exists) or in the project's documentation.

---

## 📚 Additional Resources

- [MCP Platform Framework Documentation](README.md)
- [Architecture Overview](docs/architecture/overview.md)
- [Getting Started Guide](docs/getting-started/README.md)
- [Module Documentation](docs/modules/README.md)
- [Deployment Guide](docs/deployment/overview.md)
- [Examples](docs/examples/tool-development.md)
- [FAQ](docs/FAQ.md)

---

## 📞 Support

If you have questions about contributing, please:

1. **Check the documentation**: Review the existing documentation
2. **Ask in discussions**: Start a discussion in the GitHub repository
3. **Contact maintainers**: Reach out to the project maintainers

---

## 🔄 Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-05-01 | Initial contributing guide |
