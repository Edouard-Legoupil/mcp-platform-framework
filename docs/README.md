# 📚 MCP Framework Documentation

**Welcome to the MCP Framework Documentation Hub**

This documentation is organized to serve **two distinct audiences**. Please navigate to the appropriate section for your needs.

---

## 🎯 **For MCP Server Developers (Users of this Framework)**

If you're **building an MCP server using this framework**, you'll find everything you need in the **root directory documentation**:

### 📖 **Start Here**
- **[USER_GUIDE.md](../USER_GUIDE.md)** - **Complete guide for MCP server developers**
  - Quick start instructions
  - Tool implementation guides
  - Resource definition examples
  - Prompt template creation
  - Deployment walkthroughs
  - Testing strategies
  - Troubleshooting help

- **[TEMPLATE_GUIDE.md](../TEMPLATE_GUIDE.md)** - **Quick start template**
  - Step-by-step setup
  - Configuration examples
  - Deployment scripts

### 🎯 **What You'll Implement**
As an MCP Server Developer, you focus on:
- ✅ **Tools** - Your business functions that users can call
- ✅ **Resources** - Your data sources that users can access
- ✅ **Prompt Templates** - Your Copilot Studio templates
- ✅ **Domain Configuration** - Your server-specific settings

### 🏗️ **What the Framework Provides**
The framework handles all infrastructure concerns:
- ✅ **Authentication & Authorization** - Entra ID, JWT, RBAC
- ✅ **Telemetry & Monitoring** - Application Insights, OpenTelemetry
- ✅ **Error Handling** - Standardized errors, recovery, logging
- ✅ **Configuration** - Environment variables, Key Vault integration
- ✅ **Data Connectivity** - Fabric, Warehouse, Lakehouse connectors
- ✅ **Audit Logging** - Immutable audit trail
- ✅ **Data Classification** - Governance controls
- ✅ **MCP Protocol Compliance** - All required endpoints

---

## 🏗️ **For Framework Contributors (Framework Developers)**

If you're **contributing to the MCP Framework itself**, you'll find the internal documentation here:

### 📖 **Start Here**
- **[FRAMEWORK_DOCUMENTATION.md](../FRAMEWORK_DOCUMENTATION.md)** - **Complete internal framework documentation**
  - Architecture overview
  - Design principles
  - Module documentation
  - API references
  - Development guidelines
  - Contribution rules

### 🏗️ **Framework Documentation Structure**

```
docs/
├── architecture/                      # 🏗️ Framework Architecture
│   ├── overview.md                   # High-level architecture
│   ├── principles.md                 # Design principles
│   ├── components.md                 # Component structure
│   ├── data-flow.md                  # Data flow diagrams
│   └── security.md                   # Security architecture
│
├── modules/                          # 🏗️ Platform Services
│   ├── framework.md                  # Core framework
│   ├── authentication.md             # Auth infrastructure
│   ├── authorization.md              # Authorization services
│   ├── audit-logging.md              # Audit trail
│   ├── telemetry.md                  # Monitoring & observability
│   ├── error-handling.md             # Error management
│   ├── configuration-management.md   # Configuration system
│   ├── data-classification.md        # Data governance
│   ├── catalog-integration.md        # Resource catalog
│   ├── connectivity/                 # Data connectors
│   │   ├── fabric-connectivity.md    # Microsoft Fabric
│   │   ├── warehouse-queries.md      # SQL Warehouse
│   │   ├── lakehouse-operations.md   # Delta Lake
│   │   └── semantic-models.md        # Semantic models
│   └── deployment.md                 # Deployment module
│
├── api-reference/                    # 🏗️ Internal APIs
│   ├── platform.md                   # Platform API
│   ├── authentication.md             # Auth API
│   ├── authorization.md              # AuthZ API
│   ├── telemetry.md                  # Telemetry API
│   ├── audit.md                      # Audit API
│   ├── connectivity.md               # Connectivity API
│   └── decorators.md                 # Framework decorators
│
├── best-practices/                   # 🏗️ Development Guidelines
│   ├── README.md                     # Best practices index
│   ├── errors.md                     # Error handling patterns
│   ├── performance.md                # Performance guidelines
│   ├── security.md                   # Security best practices
│   └── testing.md                    # Testing guidelines
│
├── deployment/                       # 🏗️ Deployment Documentation
│   ├── README.md                    # Deployment overview
│   ├── overview.md                   # Deployment architecture
│   ├── arm-templates.md              # ARM template guides
│   ├── bicep-templates.md            # Bicep template guides
│   ├── environments.md               # Environment management
│   ├── function-app.md               # Function App deployment
│   ├── pipeline-config.md            # CI/CD pipeline config
│   ├── azure-devops.md               # Azure DevOps integration
│   └── github-actions.md             # GitHub Actions integration
│
└── examples/                         # 🏗️ Framework Usage Examples
    ├── README.md                    # Examples index
    ├── authentication.md            # Auth implementation example
    ├── authorization.md             # AuthZ implementation example
    ├── donor-management.md          # Domain implementation example
    ├── warehouse-queries.md          # Warehouse operations example
    ├── lakehouse-operations.md      # Lakehouse operations example
    ├── semantic-models.md            # Semantic models example
    └── tool-development.md           # Tool development patterns
```

### 🏗️ **What You'll Work On**
As a Framework Contributor, you focus on:
- 🏗️ **Platform Services** - Authentication, authorization, telemetry, etc.
- 🏗️ **Connectivity Layer** - Data source connectors
- 🏗️ **Infrastructure** - Deployment, CI/CD, monitoring
- 🏗️ **Core Framework** - Main framework implementation
- 🏗️ **Documentation** - Internal docs and examples

---

## 🎯 **Documentation Philosophy**

### For User Documentation (MCP Server Developers)

**Purpose:** Help users **build their own MCP servers** using this framework

**Characteristics:**
- 🎯 **Action-oriented** - Step-by-step guides, tutorials
- 🎯 **Example-driven** - Code examples, templates
- 🎯 **Practical** - Focus on solving user problems
- 🎯 **Simplified** - Hide framework complexity
- 🎯 **Prescriptive** - Clear recommendations, best practices

**Location:** Root directory (`USER_GUIDE.md`, `TEMPLATE_GUIDE.md`)

### For Framework Documentation (Framework Contributors)

**Purpose:** Help contributors **understand, maintain, and extend** the framework

**Characteristics:**
- 🏗️ **Technical** - Deep dives into implementation details
- 🏗️ **Architectural** - Design decisions, patterns, rationale
- 🏗️ **Comprehensive** - Complete API references, module docs
- 🏗️ **Internal** - Framework internals, implementation details
- 🏗️ **Collaborative** - Contribution guidelines, standards

**Location:** `docs/` directory and `FRAMEWORK_DOCUMENTATION.md`

---

## 🔍 **Documentation Map**

### User Documentation (MCP Server Developers)

| Need | Document | Location |
|------|----------|----------|
| Complete guide to building MCP servers | [USER_GUIDE.md](../USER_GUIDE.md) | Root |
| Quick start template | [TEMPLATE_GUIDE.md](../TEMPLATE_GUIDE.md) | Root |
| Environment configuration | [.env.example](../.env.example) | Root |
| Local development setup | [local.settings.json.example](../local.settings.json.example) | Root |
| Deployment script | [deploy.sh](../deploy/scripts/deploy.sh) | deploy/scripts/ |
| Production dependencies | [requirements.txt](../src/azure/requirements.txt) | src/azure/ |

### Framework Documentation (Framework Contributors)

| Need | Document | Location |
|------|----------|----------|
| Complete framework documentation | [FRAMEWORK_DOCUMENTATION.md](../FRAMEWORK_DOCUMENTATION.md) | Root |
| Architecture overview | [architecture/overview.md](./architecture/overview.md) | docs/architecture/ |
| Design principles | [architecture/principles.md](./architecture/principles.md) | docs/architecture/ |
| Module documentation | [modules/](./modules/) | docs/modules/ |
| API references | [api-reference/](./api-reference/) | docs/api-reference/ |
| Best practices | [best-practices/](./best-practices/) | docs/best-practices/ |
| Deployment guides | [deployment/](./deployment/) | docs/deployment/ |
| Usage examples | [examples/](./examples/) | docs/examples/ |
| Contribution guidelines | [CONTRIBUTING.md](./CONTRIBUTING.md) | docs/ |

---

## 📝 **Documentation Standards**

### User Documentation Standards

When creating or updating **user-facing documentation**:

✅ **Do:**
- Use simple, action-oriented language
- Provide step-by-step instructions
- Include working code examples
- Focus on user goals and outcomes
- Hide framework complexity
- Use consistent terminology
- Include troubleshooting tips

❌ **Don't:**
- Discuss framework internals
- Include implementation details of platform services
- Use technical jargon without explanation
- Assume knowledge of framework architecture

### Framework Documentation Standards

When creating or updating **framework documentation**:

✅ **Do:**
- Document design decisions and rationale
- Include architecture diagrams
- Explain implementation details
- Document APIs and interfaces
- Include code examples for contributors
- Reference related modules and dependencies

❌ **Don't:**
- Include user-specific examples
- Explain basic usage patterns
- Hide implementation complexity
- Assume knowledge of user requirements

---

## 🎯 **Quick Navigation**

### I'm an MCP Server Developer...
→ [USER_GUIDE.md](../USER_GUIDE.md) - **Start here!**

### I'm a Framework Contributor...
→ [FRAMEWORK_DOCUMENTATION.md](../FRAMEWORK_DOCUMENTATION.md) - **Start here!**

### I need to understand the architecture...
→ [architecture/overview.md](./architecture/overview.md)

### I need API documentation...
→ [api-reference/](./api-reference/)

### I need deployment help...
→ [deployment/README.md](./deployment/README.md)

---

## 🤝 **Contributing to Documentation**

We welcome contributions to both user and framework documentation!

### For User Documentation Contributions
- Focus on **clarity** and **practicality**
- Test all code examples
- Ensure step-by-step guides are accurate
- Add troubleshooting sections

### For Framework Documentation Contributions
- Document **design decisions**
- Include **architecture diagrams**
- Explain **implementation details**
- Document **APIs and interfaces**
- Add **code examples** for contributors

Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed contribution guidelines.

---

## 📞 **Getting Help**

### For MCP Server Developers
- 📖 [USER_GUIDE.md](../USER_GUIDE.md) - Complete user guide
- 📖 [TEMPLATE_GUIDE.md](../TEMPLATE_GUIDE.md) - Quick start template
- 💬 Open an issue in the repository

### For Framework Contributors
- 📖 [FRAMEWORK_DOCUMENTATION.md](../FRAMEWORK_DOCUMENTATION.md) - Internal documentation
- 📖 [CONTRIBUTING.md](./CONTRIBUTING.md) - Contribution guidelines
- 💬 Open an issue or pull request

---

**💡 Remember:** This documentation hub serves two audiences. Make sure you're in the right section for your needs!
