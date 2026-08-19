# 🏗️ MCP Framework - Internal Documentation

**For Framework Developers & Maintainers**

This documentation is intended for developers who are **working on the MCP Framework itself** - maintaining, extending, or contributing to the core framework code.

---

## 📚 Framework Architecture & Design

### Core Principles
- [Architecture Overview](docs/architecture/overview.md) - High-level framework architecture
- [Design Principles](docs/architecture/principles.md) - Core design decisions and philosophy
- [Component Architecture](docs/architecture/components.md) - Framework component structure
- [Data Flow](docs/architecture/data-flow.md) - How data moves through the framework
- [Security Architecture](docs/architecture/security.md) - Framework security design

### Platform Services
- [Framework Core](docs/modules/framework.md) - Main framework implementation
- [Authentication Service](docs/modules/authentication.md) - Authentication infrastructure
- [Authorization Service](docs/modules/authorization.md) - RBAC and policy management
- [Audit Logging](docs/modules/audit-logging.md) - Immutable audit trail
- [Telemetry Service](docs/modules/telemetry.md) - Monitoring and observability
- [Error Handling](docs/modules/error-handling.md) - Standardized error management
- [Configuration Management](docs/modules/configuration-management.md) - Configuration system
- [Data Classification](docs/modules/data-classification.md) - Data governance controls

### Connectivity Layer
- [Connectivity Overview](docs/modules/catalog-integration.md) - Data source connectivity
- [Semantic Models](docs/modules/semantic-models.md) - Semantic model integration
- [Warehouse Connectivity](docs/modules/warehouse-queries.md) - SQL warehouse connections
- [Lakehouse Connectivity](docs/modules/lakehouse-operations.md) - Delta lake integration
- [Fabric Connectivity](docs/modules/fabric-connectivity.md) - Microsoft Fabric integration

### API Reference (Internal)
- [Platform API](docs/api-reference/platform.md) - Core platform APIs
- [Authentication API](docs/api-reference/authentication.md) - Auth service APIs
- [Authorization API](docs/api-reference/authorization.md) - AuthZ service APIs
- [Telemetry API](docs/api-reference/telemetry.md) - Monitoring APIs
- [Audit API](docs/api-reference/audit.md) - Audit logging APIs
- [Connectivity API](docs/api-reference/connectivity.md) - Data connectivity APIs
- [Decorators Reference](docs/api-reference/decorators.md) - Framework decorators

---

## 🔧 Development & Contribution

### Getting Started for Contributors
- [Contribution Guidelines](docs/CONTRIBUTING.md) - How to contribute to the framework
- [Development Environment Setup](docs/getting-started/installation.md) - Setting up dev environment
- [Prerequisites](docs/getting-started/prerequisites.md) - Required tools and dependencies

### Development Practices
- [Best Practices](docs/best-practices/README.md) - Framework development best practices
- [Error Handling Patterns](docs/best-practices/errors.md) - How to handle errors in the framework
- [Performance Guidelines](docs/best-practices/performance.md) - Performance considerations
- [Security Best Practices](docs/best-practices/security.md) - Security guidelines
- [Testing Guidelines](docs/best-practices/testing.md) - Testing framework code
- [Monitoring Guidelines](docs/best-practices/monitoring.md) - Monitoring and observability

### Deployment (Framework Level)
- [Deployment Overview](docs/deployment/overview.md) - Framework deployment architecture
- [ARM Templates](docs/deployment/arm-templates.md) - Azure Resource Manager templates
- [Bicep Templates](docs/deployment/bicep-templates.md) - Bicep infrastructure as code
- [Pipeline Configuration](docs/deployment/pipeline-config.md) - CI/CD pipeline setup
- [Azure DevOps Integration](docs/deployment/azure-devops.md) - Azure DevOps pipelines
- [GitHub Actions Integration](docs/deployment/github-actions.md) - GitHub Actions workflows
- [Environment Management](docs/deployment/environments.md) - Multi-environment deployment

---

## 📖 Examples (Framework Usage)

These examples show how the framework is used internally:
- [Authentication Example](docs/examples/authentication.md) - Framework auth implementation
- [Authorization Example](docs/examples/authorization.md) - Framework authZ implementation
- [Donor Management Example](docs/examples/donor-management.md) - Domain implementation example
- [Warehouse Queries Example](docs/examples/warehouse-queries.md) - Data warehouse operations
- [Lakehouse Operations Example](docs/examples/lakehouse-operations.md) - Lakehouse connectivity
- [Semantic Models Example](docs/examples/semantic-models.md) - Semantic model usage
- [Tool Development Example](docs/examples/tool-development.md) - Tool implementation patterns

---

## 🎯 Framework Domain Ownership

The MCP Framework follows a **strict separation of concerns**:

### ✅ Framework Owns (This Documentation)
- Authentication & Authorization infrastructure
- Telemetry and monitoring
- Error handling and logging
- Configuration management
- Data classification and governance
- Connectivity to data sources (Fabric, Warehouse, Lakehouse)
- Tool registration and discovery
- Resource catalog management
- Audit trail

### ❌ Domains Own (See USER_GUIDE.md)
- Business logic
- Domain-specific ontologies
- Domain-specific semantic definitions
- Domain-specific tool implementations
- Domain-specific resource definitions

---

## 🔗 Quick Links

- [User Guide (USER_GUIDE.md)](USER_GUIDE.md) - **For MCP Server Developers**
- [Template Guide (TEMPLATE_GUIDE.md)](TEMPLATE_GUIDE.md) - **Quick Start Template**
- [Main README](../README.md) - **Project Overview**

---

## 📝 Documentation Standards

### For Framework Documentation
- Focus on **internal implementation details**
- Explain **how the framework works**
- Document **APIs and interfaces** for framework components
- Include **architecture decisions** and design rationale
- Target audience: **Framework contributors and maintainers**

### For User Documentation (USER_GUIDE.md)
- Focus on **how to use the framework**
- Provide **step-by-step guides**
- Include **code examples** for domain implementation
- Document **configuration options** for users
- Target audience: **MCP Server developers using this framework**

---

**💡 Remember**: If you're building an MCP server **using** this framework, see [USER_GUIDE.md](USER_GUIDE.md). If you're **contributing to** the framework itself, this is the right place.
