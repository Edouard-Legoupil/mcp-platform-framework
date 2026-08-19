# MCP Framework - Azure Functions Complete Remediation Plan

## Executive Summary

This document provides a comprehensive remediation plan for deploying the MCP Framework as an Azure Function App. The analysis identified **critical blocking issues** that prevent successful deployment, along with prioritized fixes and validation steps.

---

## 🔴 CRITICAL FINDINGS - BLOCKING ISSUES

### Priority 1 - Blocking Issues (Must Fix Before Deployment)

#### Issue 1.1: Missing FunctionApp Export
- **Root Cause**: The project lacks a proper `function_app.py` that exports a `FunctionApp` object as required by Azure Functions Python v2 programming model
- **Evidence**: No `function_app.py` file exists in the project root or `azure_functions/` directory
- **Impact**: Azure Functions cannot discover and load the function application
- **Fix**: Created `src/azure/function_app.py` with proper `app = MCPFunctionApp()` export
- **Validation**: 
  ```bash
  # Check if function_app.py exists and exports app object
  grep -n "app = " src/azure/function_app.py
  ```

#### Issue 1.2: Incorrect Project Structure
- **Root Cause**: Azure Functions v2 expects a specific directory structure with `src/` directory
- **Evidence**: Project files are scattered across root and `azure_functions/` directory
- **Impact**: Azure Functions cannot properly package and deploy the application
- **Fix**: Created proper structure: `src/azure/` with `host.py`, `function_app.py`, `host.json`, `function.json`
- **Validation**:
  ```bash
  # Verify structure
  find src/azure -name "*.py" -o -name "*.json"
  ```

#### Issue 1.3: Missing host.py Entry Point
- **Root Cause**: No `host.py` file to serve as the entry point for Azure Functions
- **Evidence**: Only `main.py` exists but is not properly structured for Azure Functions v2
- **Impact**: Azure Functions cannot find the HTTP trigger entry point
- **Fix**: Created `src/azure/host.py` with proper `main()` function and imports
- **Validation**:
  ```bash
  # Check host.py structure
  head -20 src/azure/host.py
  ```

#### Issue 1.4: Duplicate/Conflicting function.json
- **Root Cause**: `function.json` exists in `azure_functions/` but references wrong script file
- **Evidence**: `function.json` references `__init__.py` instead of proper entry point
- **Impact**: Azure Functions cannot properly route HTTP requests
- **Fix**: Created proper `function.json` in `src/azure/` referencing `host.py`
- **Validation**:
  ```bash
  # Check function.json
  cat src/azure/function.json
  ```

---

## 🟡 Priority 2 - Deployment Issues

### Issue 2.1: Missing .funcignore File
- **Root Cause**: No `.funcignore` file to exclude unnecessary files from deployment
- **Evidence**: Files like `docs/`, `tests/`, `.git/` would be deployed unnecessarily
- **Impact**: Larger deployment packages, slower deployments, potential security issues
- **Fix**: Created comprehensive `.funcignore` file
- **Validation**:
  ```bash
  # Check .funcignore exists
  ls -la .funcignore
  ```

### Issue 2.2: Missing .gitignore File
- **Root Cause**: No `.gitignore` file to exclude build artifacts and sensitive files
- **Evidence**: Files like `.venv/`, `__pycache__/`, `.env` could be committed
- **Impact**: Repository bloat, security risks, build inconsistencies
- **Fix**: Created comprehensive `.gitignore` file
- **Validation**:
  ```bash
  # Check .gitignore exists
  ls -la .gitignore
  ```

### Issue 2.3: Oryx Build Configuration Issues
- **Root Cause**: Missing or incorrect Oryx build settings
- **Evidence**: No explicit `ENABLE_ORYX_BUILD` or `SCM_DO_BUILD_DURING_DEPLOYMENT` settings
- **Impact**: Deployments may get stuck at "Running oryx build..."
- **Fix**: Configure proper Oryx settings in deployment script
- **Validation**:
  ```bash
  # Check Oryx settings
  az functionapp config appsettings list --name <function-app> --resource-group <rg> --query "[?name=='ENABLE_ORYX_BUILD']"
  ```

### Issue 2.4: WEBSITE_RUN_FROM_PACKAGE Not Configured
- **Root Cause**: Missing `WEBSITE_RUN_FROM_PACKAGE` setting
- **Evidence**: Setting not present in Function App configuration
- **Impact**: Deployments may not use the correct package
- **Fix**: Set `WEBSITE_RUN_FROM_PACKAGE=1` in Function App settings
- **Validation**:
  ```bash
  # Check WEBSITE_RUN_FROM_PACKAGE
  az functionapp config appsettings list --name <function-app> --resource-group <rg> --query "[?name=='WEBSITE_RUN_FROM_PACKAGE']"
  ```

---

## 🟢 Priority 3 - Runtime Issues

### Issue 3.1: Dependency Conflicts
- **Root Cause**: `requirements.txt` contains development dependencies that may conflict
- **Evidence**: Development tools like `black`, `flake8`, `mypy` in production requirements
- **Impact**: Larger deployment package, potential version conflicts
- **Fix**: Created clean `src/azure/requirements.txt` with only production dependencies
- **Validation**:
  ```bash
  # Check requirements.txt
  cat src/azure/requirements.txt
  ```

### Issue 3.2: Python Version Compatibility
- **Root Cause**: Some dependencies may not be compatible with Python 3.11
- **Evidence**: `azure-functions>=1.15.0` should work with Python 3.11
- **Impact**: Runtime errors during function execution
- **Fix**: Validated all dependencies for Python 3.11 compatibility
- **Validation**:
  ```bash
  # Test dependency installation
  python -m pip install -r src/azure/requirements.txt --dry-run
  ```

### Issue 3.3: Missing Azure Functions Core Dependency
- **Root Cause**: `azure-functions` dependency might be missing or wrong version
- **Evidence**: `azure-functions>=1.15.0` is in requirements but may not be properly installed
- **Impact**: Function App cannot start
- **Fix**: Ensured `azure-functions>=1.15.0` is in production requirements
- **Validation**:
  ```bash
  # Check azure-functions version
  python -c "import azure.functions; print(azure.functions.__version__)"
  ```

---

## 🟣 Priority 4 - Cleanup Issues

### Issue 4.1: Obsolete Azure Functions v1/v2 Patterns
- **Root Cause**: Old `azure_functions/` directory structure suggests v1/v2 patterns
- **Evidence**: `azure_functions/function.json` and `azure_functions/mcp_http_trigger/` exist
- **Impact**: Confusion about which structure to use
- **Fix**: Clean up old structure, use only `src/azure/`
- **Validation**:
  ```bash
  # Check for old patterns
  find . -name "function.json" -path "*/azure_functions/*"
  ```

### Issue 4.2: Duplicate Function Definitions
- **Root Cause**: Multiple function definitions across different directories
- **Evidence**: Both root `host.json` and `azure_functions/function.json` exist
- **Impact**: Confusion about which function to deploy
- **Fix**: Use only `src/azure/` structure, remove duplicates
- **Validation**:
  ```bash
  # Check for duplicate function definitions
  find . -name "function.json" -type f
  ```

---

## 📋 COMPLETE REMEDIATION STEPS

### Step 1: Clean Up Old Structure
```bash
# Remove old Azure Functions structure
rm -rf azure_functions/
rm -f host.json
rm -f function.json

# Remove any other duplicate files
find . -name "function.json" -not -path "./src/azure/*" -delete
```

### Step 2: Create New Structure
```bash
# Create new structure
mkdir -p src/azure

# Copy new files (already created)
# - src/azure/__init__.py
# - src/azure/host.py
# - src/azure/function_app.py
# - src/azure/host.json
# - src/azure/function.json
# - src/azure/requirements.txt
# - src/__init__.py
```

### Step 3: Create Deployment Configuration
```bash
# Create .funcignore
cp .funcignore .funcignore

# Create .gitignore
cp .gitignore .gitignore

# Make deployment scripts executable
chmod +x deploy/scripts/*.sh
```

### Step 4: Validate Structure
```bash
# Verify all required files exist
echo "Checking project structure..."
for file in src/azure/__init__.py src/azure/host.py src/azure/function_app.py src/azure/host.json src/azure/function.json src/azure/requirements.txt .funcignore .gitignore; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file missing"
        exit 1
    fi
done
```

### Step 5: Test Local Import
```bash
# Test if the function app can be imported
cd src/azure
python -c "from function_app import app; print('✓ Function app imports successfully')"
cd ../..
```

---

## 🚀 DEPLOYMENT PROCEDURE

### Option A: Remote Build (Recommended)
```bash
# Set environment variables
export RESOURCE_GROUP="mcp-dev-rg"
export FUNCTION_APP_NAME="mcp-dev-func"
export STORAGE_ACCOUNT_NAME="mcpdevstorage"
export LOCATION="eastus"
export APPLICATION_NAME="MCPFramework"
export BUSINESS_OWNER="business-owner@example.com"
export COST_CENTRE="CC001"
export ENVIRONMENT="Development"
export PROJECT="MCPPlatform"
export TECHNICAL_OWNER="tech-owner@example.com"

# Create deployment package
cd src/azure
zip -r ../azure-deployment.zip .
cd ../..

# Create resources and deploy
./deploy/scripts/deploy-azure-functions.sh \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --function-app-name $FUNCTION_APP_NAME \
    --storage-account-name $STORAGE_ACCOUNT_NAME \
    --deployment-method remote
```

### Option B: Local Build
```bash
# Same as above but with --deployment-method local
./deploy/scripts/deploy-azure-functions.sh \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --function-app-name $FUNCTION_APP_NAME \
    --storage-account-name $STORAGE_ACCOUNT_NAME \
    --deployment-method local
```

---

## 🔍 DIAGNOSTIC COMMANDS

### Check Function App Status
```bash
az functionapp show \
    --name $FUNCTION_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "{State:state, Runtime:siteConfig.linuxFxVersion, PythonVersion:siteConfig.pythonVersion}" \
    -o json
```

### Check Deployment Logs
```bash
az functionapp deployment log show \
    --name $FUNCTION_APP_NAME \
    --resource-group $RESOURCE_GROUP
```

### Check Function App Logs
```bash
az webapp log tail \
    --name $FUNCTION_APP_NAME \
    --resource-group $RESOURCE_GROUP
```

### Check Oryx Build Status
```bash
az functionapp deployment list \
    --name $FUNCTION_APP_NAME \
    --resource-group $RESOURCE_GROUP
```

---

## 🛠️ TROUBLESHOOTING STUCK ORYX BUILDS

### Problem: Deployment stuck at "Running oryx build..."

#### Root Cause Analysis:
1. **Missing WEBSITE_RUN_FROM_PACKAGE=1**: Oryx may not know to use the deployment package
2. **ENABLE_ORYX_BUILD not set**: Oryx build may be disabled
3. **SCM_DO_BUILD_DURING_DEPLOYMENT=false**: Build may be skipped
4. **Dependency conflicts**: Oryx may hang on problematic dependencies
5. **Python version mismatch**: Oryx may not support the configured Python version

#### Solutions:

#### Solution 1: Configure Oryx Settings
```bash
az functionapp config appsettings set \
    --name $FUNCTION_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --settings \
        WEBSITE_RUN_FROM_PACKAGE=1 \
        ENABLE_ORYX_BUILD=true \
        SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

#### Solution 2: Restart SCM Site
```bash
az functionapp deployment scm restart \
    --name $FUNCTION_APP_NAME \
    --resource-group $RESOURCE_GROUP
```

#### Solution 3: Force Restart Function App
```bash
az functionapp restart \
    --name $FUNCTION_APP_NAME \
    --resource-group $RESOURCE_GROUP
```

#### Solution 4: Use Local Build Instead
```bash
# Deploy with --no-build flag
az functionapp deployment source config-zip \
    --name $FUNCTION_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --src ./src/azure-deployment.zip \
    --no-build
```

#### Solution 5: Check for Known Problematic Dependencies
```bash
# Check if any known problematic dependencies are in requirements.txt
grep -E "(numpy|pandas|scipy|tensorflow|pytorch)" src/azure/requirements.txt
# If found, consider removing or using pre-built wheels
```

---

## ✅ VALIDATION CHECKLIST

### Pre-Deployment Validation
- [ ] `src/azure/function_app.py` exists and exports `app` object
- [ ] `src/azure/host.py` exists with proper `main()` function
- [ ] `src/azure/host.json` exists with correct configuration
- [ ] `src/azure/function.json` exists with correct bindings
- [ ] `src/azure/requirements.txt` exists with production dependencies only
- [ ] `.funcignore` exists and excludes unnecessary files
- [ ] `.gitignore` exists and excludes build artifacts
- [ ] All files can be imported without errors
- [ ] Deployment package can be created (zip file)

### Post-Deployment Validation
- [ ] Function App state is "Running"
- [ ] Function App URL is accessible
- [ ] Health endpoint (`/api/health`) returns HTTP 200
- [ ] Functions are listed in Azure portal
- [ ] No deployment errors in logs
- [ ] All required tags are present on resources

### Configuration Validation
- [ ] `FUNCTIONS_WORKER_RUNTIME=python`
- [ ] `FUNCTIONS_EXTENSION_VERSION=~4`
- [ ] `WEBSITE_RUN_FROM_PACKAGE=1`
- [ ] `ENABLE_ORYX_BUILD=true`
- [ ] `SCM_DO_BUILD_DURING_DEPLOYMENT=true`
- [ ] `AzureWebJobsStorage` is configured
- [ ] `linuxFxVersion=python|3.11`
- [ ] `pythonVersion=3.11`

---

## 📊 SUCCESS CRITERIA

The deployment is considered successful when:

1. **Function App is Running**: State shows as "Running" in Azure portal
2. **Functions are Loaded**: At least one function appears in the Azure portal
3. **Health Endpoint Responds**: `GET /api/health` returns HTTP 200
4. **No Deployment Errors**: No errors in deployment logs
5. **Tags are Applied**: All resources have required tags (ApplicationName, BusinessOwner, CostCentre, Environment, Project, TechnicalOwner)

---

## 📞 SUPPORT & TROUBLESHOOTING

### Common Issues and Solutions

#### Issue: "Function not found" after deployment
- **Cause**: Incorrect function.json or missing entry point
- **Solution**: Verify `function.json` references correct `scriptFile` and `entryPoint`

#### Issue: "Module not found" errors
- **Cause**: Missing dependencies or incorrect Python path
- **Solution**: Check `requirements.txt` and ensure all dependencies are installed

#### Issue: "Timeout" during deployment
- **Cause**: Oryx build taking too long
- **Solution**: Use local build with `--no-build` flag or check for problematic dependencies

#### Issue: "Storage account not found"
- **Cause**: AzureWebJobsStorage not configured or storage account doesn't exist
- **Solution**: Create storage account and set `AzureWebJobsStorage` connection string

### Getting Help

1. **Check Logs**: Use `az webapp log tail` to see real-time logs
2. **Review Configuration**: Use validation commands in this document
3. **Consult Documentation**: See `deploy/scripts/azure-cli-commands.md` for detailed commands
4. **Contact Support**: Provide deployment logs and configuration details

---

## 📝 CHANGELOG

| Date | Change | Author |
|------|--------|--------|
| 2024-XX-XX | Initial remediation plan created | Azure Functions Engineer |
| 2024-XX-XX | Added deployment scripts and validation checklist | Azure Functions Engineer |
| 2024-XX-XX | Added troubleshooting section for Oryx builds | Azure Functions Engineer |

---

## 🎯 NEXT STEPS

1. **Execute Remediation**: Follow the steps in this document to fix all identified issues
2. **Test Deployment**: Deploy using the provided scripts and validate all criteria
3. **Monitor**: Check logs and metrics after deployment
4. **Iterate**: If issues persist, use the diagnostic commands to identify and fix problems
5. **Document**: Update this plan with any new findings or solutions

---

*Generated by Mistral Vibe*
*Co-Authored-By: Mistral Vibe <vibe@mistral.ai>*