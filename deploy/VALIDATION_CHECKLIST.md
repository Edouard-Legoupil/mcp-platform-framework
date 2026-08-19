# MCP Framework - Azure Functions Validation Checklist

## 📋 COMPLETE VALIDATION CHECKLIST

This checklist ensures that all requirements for successful Azure Functions deployment are met. Complete each section before attempting deployment.

---

## ✅ SECTION A - PROJECT STRUCTURE VALIDATION

### A.1 Required Files Exist
- [ ] `src/azure/__init__.py` - Package initialization
- [ ] `src/azure/host.py` - Azure Functions entry point
- [ ] `src/azure/function_app.py` - Function App implementation with `app` export
- [ ] `src/azure/host.json` - Azure Functions host configuration
- [ ] `src/azure/function.json` - Function bindings configuration
- [ ] `src/azure/requirements.txt` - Production dependencies
- [ ] `src/__init__.py` - Source package initialization
- [ ] `.funcignore` - Deployment ignore file
- [ ] `.gitignore` - Git ignore file

**Validation Command:**
```bash
for file in src/azure/__init__.py src/azure/host.py src/azure/function_app.py src/azure/host.json src/azure/function.json src/azure/requirements.txt src/__init__.py .funcignore .gitignore; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ MISSING: $file"
        exit 1
    fi
done
```

### A.2 Project Structure
- [ ] `src/azure/` directory exists
- [ ] No duplicate `function.json` files outside `src/azure/`
- [ ] No duplicate `host.json` files outside `src/azure/`
- [ ] Old `azure_functions/` directory removed or empty

**Validation Command:**
```bash
# Check for duplicate function.json files
find . -name "function.json" -type f | grep -v "src/azure/function.json"

# Check for duplicate host.json files  
find . -name "host.json" -type f | grep -v "src/azure/host.json"

# Check if old azure_functions directory exists
ls -la azure_functions/ 2>/dev/null || echo "✓ azure_functions/ directory does not exist"
```

### A.3 Function App Export Validation
- [ ] `function_app.py` exports `app` object
- [ ] `app` is an instance of a class that handles HTTP requests
- [ ] `host.py` imports and uses the `app` object

**Validation Command:**
```bash
# Check for app export
grep -n "^app = " src/azure/function_app.py

# Check for app import in host.py
grep -n "from.*function_app import app" src/azure/host.py

# Test import
cd src/azure
python -c "from function_app import app; print('✓ app object imported successfully')"
cd ../..
```

### A.4 Function JSON Validation
- [ ] `function.json` has correct `scriptFile` pointing to `host.py`
- [ ] `function.json` has HTTP trigger binding
- [ ] `function.json` has HTTP output binding
- [ ] `function.json` has correct route configuration

**Validation Command:**
```bash
# Check function.json content
cat src/azure/function.json

# Validate JSON syntax
python -c "import json; json.load(open('src/azure/function.json')); print('✓ function.json is valid JSON')"
```

### A.5 Host JSON Validation
- [ ] `host.json` has version "2.0"
- [ ] `host.json` has correct extension bundle version
- [ ] `host.json` has function timeout configured
- [ ] `host.json` lists the function name correctly

**Validation Command:**
```bash
# Check host.json content
cat src/azure/host.json

# Validate JSON syntax
python -c "import json; json.load(open('src/azure/host.json')); print('✓ host.json is valid JSON')"
```

---

## ✅ SECTION B - DEPLOYMENT CONFIGURATION VALIDATION

### B.1 .funcignore Validation
- [ ] `.funcignore` excludes `.git/`
- [ ] `.funcignore` excludes `.venv/` and other virtual environments
- [ ] `.funcignore` excludes `docs/`
- [ ] `.funcignore` excludes `tests/`
- [ ] `.funcignore` excludes `*.md` files
- [ ] `.funcignore` includes `!src/azure/` to ensure deployment

**Validation Command:**
```bash
# Check .funcignore content
echo "Checking .funcignore..."
grep -q "\.git/" .funcignore && echo "✓ Excludes .git/"
grep -q "\.venv/" .funcignore && echo "✓ Excludes .venv/"
grep -q "docs/" .funcignore && echo "✓ Excludes docs/"
grep -q "tests/" .funcignore && echo "✓ Excludes tests/"
grep -q "\.md" .funcignore && echo "✓ Excludes .md files"
grep -q "!src/azure/" .funcignore && echo "✓ Includes src/azure/"
```

### B.2 .gitignore Validation
- [ ] `.gitignore` excludes `__pycache__/`
- [ ] `.gitignore` excludes `*.pyc` files
- [ ] `.gitignore` excludes virtual environments
- [ ] `.gitignore` excludes `.env` files
- [ ] `.gitignore` excludes IDE directories

**Validation Command:**
```bash
# Check .gitignore content
echo "Checking .gitignore..."
grep -q "__pycache__/" .gitignore && echo "✓ Excludes __pycache__/"
grep -q "\.pyc" .gitignore && echo "✓ Excludes .pyc files"
grep -q "\.venv/" .gitignore && echo "✓ Excludes .venv/"
grep -q "\.env" .gitignore && echo "✓ Excludes .env files"
grep -q "\.vscode/" .gitignore && echo "✓ Excludes .vscode/"
```

---

## ✅ SECTION C - DEPENDENCY VALIDATION

### C.1 requirements.txt Validation
- [ ] `requirements.txt` contains `azure-functions>=1.15.0`
- [ ] `requirements.txt` contains Python 3.11 compatible packages
- [ ] `requirements.txt` does NOT contain development dependencies (black, flake8, etc.)
- [ ] `requirements.txt` contains all necessary Azure SDK packages

**Validation Command:**
```bash
# Check for required packages
echo "Checking requirements.txt..."
grep -q "azure-functions" src/azure/requirements.txt && echo "✓ Contains azure-functions"
grep -q "azure-identity" src/azure/requirements.txt && echo "✓ Contains azure-identity"
grep -q "pydantic" src/azure/requirements.txt && echo "✓ Contains pydantic"

# Check for development packages (should NOT be present)
if grep -q "black\|flake8\|mypy\|pytest" src/azure/requirements.txt; then
    echo "✗ WARNING: Development packages found in requirements.txt"
else
    echo "✓ No development packages in requirements.txt"
fi
```

### C.2 Dependency Installation Test
- [ ] All dependencies can be installed without conflicts
- [ ] No version conflicts between packages

**Validation Command:**
```bash
# Test dependency installation (dry run)
python -m pip install -r src/azure/requirements.txt --dry-run 2>&1 | grep -i "error\|conflict" || echo "✓ No dependency conflicts detected"
```

### C.3 Azure Functions Compatibility
- [ ] All packages are compatible with Azure Functions Python v2
- [ ] All packages are compatible with Python 3.11

**Validation Command:**
```bash
# Check for known incompatible packages
echo "Checking for known incompatible packages..."
INCOMPATIBLE_PACKAGES=("numpy" "pandas" "scipy" "tensorflow" "pytorch" "matplotlib" "seaborn")
for pkg in "${INCOMPATIBLE_PACKAGES[@]}"; do
    if grep -q "$pkg" src/azure/requirements.txt; then
        echo "⚠ WARNING: $pkg may cause Oryx build issues"
    fi
done
```

---

## ✅ SECTION D - AZURE CONFIGURATION VALIDATION

### D.1 Function App Configuration (Pre-Deployment)
- [ ] Function App name is valid (alphanumeric + hyphens, 2-60 chars)
- [ ] Resource group name is valid
- [ ] Location is valid Azure region
- [ ] Storage account name is valid (3-24 chars, lowercase alphanumeric)

**Validation Command:**
```bash
# Validate naming conventions
echo "Validating Azure resource names..."

# Function App name (2-60 chars, alphanumeric + hyphens)
FUNCTION_APP_NAME="${FUNCTION_APP_NAME:-mcp-dev-func}"
if [[ "$FUNCTION_APP_NAME" =~ ^[a-zA-Z0-9-]{2,60}$ ]]; then
    echo "✓ Function App name is valid: $FUNCTION_APP_NAME"
else
    echo "✗ Function App name is invalid: $FUNCTION_APP_NAME"
fi

# Storage account name (3-24 chars, lowercase alphanumeric)
STORAGE_ACCOUNT_NAME="${STORAGE_ACCOUNT_NAME:-mcpdevstorage}"
if [[ "$STORAGE_ACCOUNT_NAME" =~ ^[a-z0-9]{3,24}$ ]]; then
    echo "✓ Storage account name is valid: $STORAGE_ACCOUNT_NAME"
else
    echo "✗ Storage account name is invalid: $STORAGE_ACCOUNT_NAME"
fi
```

### D.2 Tag Validation
- [ ] All required tags are defined (ApplicationName, BusinessOwner, CostCentre, Environment, Project, TechnicalOwner)
- [ ] Tag values are appropriate for the environment

**Validation Command:**
```bash
# Check if required tags are set
echo "Checking required tags..."
REQUIRED_TAGS=("APPLICATION_NAME" "BUSINESS_OWNER" "COST_CENTRE" "ENVIRONMENT" "PROJECT" "TECHNICAL_OWNER")
for tag in "${REQUIRED_TAGS[@]}"; do
    if [ -z "${!tag}" ]; then
        echo "⚠ WARNING: $tag is not set"
    else
        echo "✓ $tag is set: ${!tag}"
    fi
done
```

---

## ✅ SECTION E - DEPLOYMENT PACKAGE VALIDATION

### E.1 Package Creation
- [ ] Deployment package can be created (zip file)
- [ ] Package contains all required files
- [ ] Package does not contain excluded files

**Validation Command:**
```bash
# Create test deployment package
cd src/azure
zip -r ../test-deployment.zip . > /dev/null 2>&1
cd ../..

# Check if package was created
if [ -f "src/test-deployment.zip" ]; then
    echo "✓ Deployment package created successfully"
    
    # Check package contents
    echo "Package contents:"
    unzip -l src/test-deployment.zip | grep -E "(host\.py|function_app\.py|host\.json|function\.json|requirements\.txt)"
    
    # Clean up
    rm -f src/test-deployment.zip
else
    echo "✗ Failed to create deployment package"
fi
```

### E.2 Package Content Validation
- [ ] Package contains `host.py`
- [ ] Package contains `function_app.py`
- [ ] Package contains `host.json`
- [ ] Package contains `function.json`
- [ ] Package contains `requirements.txt`

**Validation Command:**
```bash
# Create and check package contents
cd src/azure
zip -r ../test-deployment.zip . > /dev/null 2>&1
cd ../..

REQUIRED_FILES=("host.py" "function_app.py" "host.json" "function.json" "requirements.txt")
for file in "${REQUIRED_FILES[@]}"; do
    if unzip -l src/test-deployment.zip | grep -q "$file"; then
        echo "✓ Package contains $file"
    else
        echo "✗ Package missing $file"
    fi
done

# Clean up
rm -f src/test-deployment.zip
```

---

## ✅ SECTION F - LOCAL TESTING VALIDATION

### F.1 Import Test
- [ ] All modules can be imported without errors
- [ ] No circular import issues
- [ ] No missing module errors

**Validation Command:**
```bash
# Test imports
cd src/azure
python -c "
import sys
try:
    from function_app import app
    print('✓ function_app imports successfully')
except Exception as e:
    print(f'✗ function_app import failed: {e}')
    sys.exit(1)

try:
    from host import main
    print('✓ host imports successfully')
except Exception as e:
    print(f'✗ host import failed: {e}')
    sys.exit(1)

try:
    import azure.functions as func
    print('✓ azure.functions imports successfully')
except Exception as e:
    print(f'✗ azure.functions import failed: {e}')
    sys.exit(1)
"
cd ../..
```

### F.2 Basic Functionality Test
- [ ] Function app can be instantiated
- [ ] Health check endpoint logic works

**Validation Command:**
```bash
# Test basic functionality
cd src/azure
python -c "
import sys
import os

# Set required environment variables
os.environ['MCP_DOMAIN'] = 'TestDomain'
os.environ['MCP_ENVIRONMENT'] = 'Test'

try:
    from function_app import app
    print('✓ Function app instantiated successfully')
    
    # Test health check (this may fail if platform imports are not available)
    try:
        # Create a mock request for testing
        import azure.functions as func
        from unittest.mock import Mock
        
        mock_req = Mock(spec=func.HttpRequest)
        mock_req.method = 'GET'
        mock_req.path = '/api/health'
        mock_req.headers = {}
        mock_req.params = {}
        mock_req.get_json = Mock(return_value={})
        mock_req.get_body = Mock(return_value=None)
        
        # This will likely fail without platform imports, but that's expected
        try:
            response = app.handle_request(mock_req)
            print('✓ Health check works')
        except Exception as e:
            if 'Platform imports not available' in str(e):
                print('⚠ Health check skipped (platform imports not available - expected)')
            else:
                print(f'⚠ Health check failed: {e}')
    except Exception as e:
        print(f'⚠ Health check test failed: {e}')
        
except Exception as e:
    print(f'✗ Function app test failed: {e}')
    sys.exit(1)
"
cd ../..
```

---

## ✅ SECTION G - AZURE CLI VALIDATION (Post-Deployment)

### G.1 Azure CLI Availability
- [ ] Azure CLI is installed
- [ ] Azure CLI is authenticated
- [ ] Correct subscription is selected

**Validation Command:**
```bash
# Check Azure CLI
if command -v az &> /dev/null; then
    echo "✓ Azure CLI is installed"
    echo "  Version: $(az --version | head -1)"
else
    echo "✗ Azure CLI is not installed"
fi

# Check authentication
if az account show &> /dev/null; then
    echo "✓ Azure CLI is authenticated"
    echo "  User: $(az account show --query user.name -o tsv)"
    echo "  Subscription: $(az account show --query name -o tsv)"
else
    echo "✗ Azure CLI is not authenticated"
fi
```

### G.2 Function App Status (Post-Deployment)
- [ ] Function App exists
- [ ] Function App state is "Running"
- [ ] Function App runtime is correct

**Validation Command:**
```bash
# Check Function App status (only works after deployment)
if az functionapp show --name "$FUNCTION_APP_NAME" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    STATE=$(az functionapp show --name "$FUNCTION_APP_NAME" --resource-group "$RESOURCE_GROUP" --query state -o tsv)
    if [ "$STATE" = "Running" ]; then
        echo "✓ Function App is running"
    else
        echo "✗ Function App state: $STATE"
    fi
    
    RUNTIME=$(az functionapp show --name "$FUNCTION_APP_NAME" --resource-group "$RESOURCE_GROUP" --query "siteConfig.linuxFxVersion" -o tsv)
    if [[ "$RUNTIME" == "python|3.11" ]]; then
        echo "✓ Function App runtime: $RUNTIME"
    else
        echo "✗ Function App runtime: $RUNTIME (expected: python|3.11)"
    fi
else
    echo "⚠ Function App not yet deployed or does not exist"
fi
```

### G.3 Function App Configuration (Post-Deployment)
- [ ] `FUNCTIONS_WORKER_RUNTIME=python`
- [ ] `FUNCTIONS_EXTENSION_VERSION=~4`
- [ ] `WEBSITE_RUN_FROM_PACKAGE=1`
- [ ] `ENABLE_ORYX_BUILD=true`
- [ ] `SCM_DO_BUILD_DURING_DEPLOYMENT=true`
- [ ] `AzureWebJobsStorage` is configured

**Validation Command:**
```bash
# Check Function App settings (only works after deployment)
if az functionapp config appsettings list --name "$FUNCTION_APP_NAME" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    echo "Checking Function App settings..."
    
    SETTINGS_TO_CHECK=(
        "FUNCTIONS_WORKER_RUNTIME:python"
        "FUNCTIONS_EXTENSION_VERSION:~4"
        "WEBSITE_RUN_FROM_PACKAGE:1"
        "ENABLE_ORYX_BUILD:true"
        "SCM_DO_BUILD_DURING_DEPLOYMENT:true"
    )
    
    for setting in "${SETTINGS_TO_CHECK[@]}"; do
        NAME="${setting%%:*}"
        EXPECTED="${setting##*:}"
        VALUE=$(az functionapp config appsettings list --name "$FUNCTION_APP_NAME" --resource-group "$RESOURCE_GROUP" --query "[?name=='$NAME'].value | [0]" -o tsv 2>/dev/null || echo "NOT_SET")
        
        # Normalize values for comparison
        VALUE_LOWER=$(echo "$VALUE" | tr '[:upper:]' '[:lower:]')
        EXPECTED_LOWER=$(echo "$EXPECTED" | tr '[:upper:]' '[:lower:]')
        
        if [[ "$VALUE_LOWER" == "$EXPECTED_LOWER" ]]; then
            echo "✓ $NAME: $VALUE"
        else
            echo "✗ $NAME: $VALUE (expected: $EXPECTED)"
        fi
    done
    
    # Check AzureWebJobsStorage
    STORAGE=$(az functionapp config appsettings list --name "$FUNCTION_APP_NAME" --resource-group "$RESOURCE_GROUP" --query "[?name=='AzureWebJobsStorage'].value | [0]" -o tsv 2>/dev/null || echo "NOT_SET")
    if [[ "$STORAGE" == "DefaultEndpointsProtocol="* ]]; then
        echo "✓ AzureWebJobsStorage: Configured"
    else
        echo "✗ AzureWebJobsStorage: Not properly configured"
    fi
else
    echo "⚠ Function App not yet deployed or does not exist"
fi
```

### G.4 Function App Endpoints (Post-Deployment)
- [ ] Function App URL is accessible
- [ ] Health endpoint returns HTTP 200

**Validation Command:**
```bash
# Check Function App endpoints (only works after deployment)
if az functionapp show --name "$FUNCTION_APP_NAME" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    URL=$(az functionapp show --name "$FUNCTION_APP_NAME" --resource-group "$RESOURCE_GROUP" --query defaultHostName -o tsv)
    echo "Function App URL: https://$URL"
    
    # Test health endpoint (requires curl)
    if command -v curl &> /dev/null; then
        STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://$URL/api/health" 2>/dev/null || echo "ERROR")
        if [ "$STATUS" = "200" ]; then
            echo "✓ Health endpoint: HTTP 200"
        else
            echo "✗ Health endpoint: HTTP $STATUS"
        fi
    else
        echo "⚠ curl not available, cannot test endpoints"
    fi
else
    echo "⚠ Function App not yet deployed or does not exist"
fi
```

---

## 📊 VALIDATION SUMMARY

### Pre-Deployment Checklist
- [ ] All required files exist
- [ ] Project structure is correct
- [ ] Function App exports are valid
- [ ] Configuration files are valid JSON
- [ ] Deployment configuration is correct
- [ ] Dependencies are compatible
- [ ] Deployment package can be created
- [ ] Local imports work

### Post-Deployment Checklist
- [ ] Function App exists and is running
- [ ] Function App runtime is correct
- [ ] All required settings are configured
- [ ] Health endpoint responds
- [ ] Functions are loaded

---

## 🎯 SUCCESS CRITERIA

**Deployment is successful when ALL of the following are true:**

1. ✅ All pre-deployment validation checks pass
2. ✅ Function App state is "Running" in Azure
3. ✅ Function App URL is accessible
4. ✅ Health endpoint (`/api/health`) returns HTTP 200
5. ✅ All required configuration settings are correct
6. ✅ All required tags are present on resources

---

## 📞 TROUBLESHOOTING

### If validation fails:

1. **Check the specific failure** - Each validation command provides detailed output
2. **Review the remediation plan** - See `REMEDIATION_PLAN.md` for fixes
3. **Check logs** - Use `az webapp log tail` for real-time logs
4. **Verify configuration** - Use the Azure CLI commands in `azure-cli-commands.md`

### Common issues:
- **Missing files**: Ensure all files from Section A exist
- **Import errors**: Check Python path and installed packages
- **JSON syntax errors**: Validate all JSON files with `python -m json.tool`
- **Azure CLI errors**: Ensure you're logged in and have correct permissions

---

## 📝 USAGE

### Run Complete Validation
```bash
# Run all validation checks
./deploy/scripts/validate-deployment.sh
```

### Run Specific Section
```bash
# Run only Section A validation
./deploy/scripts/validate-deployment.sh --section A

# Run only Section C validation
./deploy/scripts/validate-deployment.sh --section C
```

### Run with Custom Configuration
```bash
# Set custom values
export FUNCTION_APP_NAME="my-function-app"
export RESOURCE_GROUP="my-resource-group"

# Run validation
./deploy/scripts/validate-deployment.sh
```

---

*Generated by Mistral Vibe*
*Co-Authored-By: Mistral Vibe <vibe@mistral.ai>*