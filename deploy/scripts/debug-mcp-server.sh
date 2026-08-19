#!/bin/bash

# MCP Server Debugging and Validation Script
# Based on the generic checklist for debugging MCP Server deployments on Azure Functions

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASSED++))
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    ((WARNINGS++))
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAILED++))
}

print_summary() {
    echo ""
    echo "=========================================="
    echo "MCP SERVER DEBUG SUMMARY"
    echo "=========================================="
    echo -e "${GREEN}Passed: $PASSED${NC}"
    echo -e "${RED}Failed: $FAILED${NC}"
    echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
    echo "=========================================="
    
    if [ $FAILED -gt 0 ]; then
        echo -e "${RED}DEBUGGING REQUIRED${NC}"
        echo "Please fix the failed checks before deployment."
        exit 1
    elif [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}DEBUGGING PASSED WITH WARNINGS${NC}"
        echo "Consider addressing the warnings before deployment."
        exit 0
    else
        echo -e "${GREEN}ALL CHECKS PASSED${NC}"
        echo "MCP Server is ready for deployment."
        exit 0
    fi
}

# ============================================================================
# SECTION 1: PROJECT STRUCTURE VERIFICATION
# ============================================================================

section_1() {
    log_info "=== SECTION 1: PROJECT STRUCTURE VERIFICATION ==="
    
    # ✅ Check for Duplicate FunctionApp Instances
    log_info "1.1 Checking for duplicate FunctionApp instances..."
    
    FUNCTION_APP_COUNT=$(grep -r "func.FunctionApp()" src/ 2>/dev/null | wc -l)
    FUNCTION_APP_COUNT=${FUNCTION_APP_COUNT:-0}
    if [ "$FUNCTION_APP_COUNT" -eq 1 ] 2>/dev/null; then
        log_success "Found exactly 1 FunctionApp instance"
        grep -r "func.FunctionApp()" src/ 2>/dev/null
    elif [ "$FUNCTION_APP_COUNT" -eq 0 ]; then
        log_error "No FunctionApp instance found. Expected: 1"
        log_info "Fix: Create a FunctionApp instance in your entry point file"
    else
        log_error "Found $FUNCTION_APP_COUNT FunctionApp instances. Expected: 1"
        log_info "Fix: Remove duplicate FunctionApp instances"
        grep -r "func.FunctionApp()" src/ 2>/dev/null
    fi
    
    # ✅ Check for @app.function_name decorators
    log_info "1.2 Checking for @app.function_name decorators..."
    
    DECORATOR_COUNT=$(grep -r "@app.function_name" src/ 2>/dev/null | wc -l)
    DECORATOR_COUNT=${DECORATOR_COUNT:-0}
    if [ "$DECORATOR_COUNT" -gt 0 ] 2>/dev/null; then
        log_success "Found $DECORATOR_COUNT @app.function_name decorators"
        grep -r "@app.function_name" src/ 2>/dev/null
    else
        log_warning "No @app.function_name decorators found. Using v2 programming model instead."
    fi
    
    # ✅ Verify Entry Point Configuration
    log_info "1.3 Verifying entry point configuration..."
    
    # Check host.json for scriptFile
    if [ -f "src/azure/host.json" ]; then
        SCRIPT_FILE=$(cat src/azure/host.json | grep -oP '(?<="scriptFile": ")[^"]+' || echo "NOT_FOUND")
        if [ "$SCRIPT_FILE" != "NOT_FOUND" ]; then
            log_success "host.json scriptFile: $SCRIPT_FILE"
            
            # Check if the script file exists
            if [ -f "src/azure/$SCRIPT_FILE" ]; then
                log_success "Entry point file exists: src/azure/$SCRIPT_FILE"
                
                # Check if it contains FunctionApp or function decorators
                if grep -q "func.FunctionApp()" "src/azure/$SCRIPT_FILE" 2>/dev/null; then
                    log_success "Entry point contains FunctionApp instance"
                elif grep -q "@app.function_name" "src/azure/$SCRIPT_FILE" 2>/dev/null; then
                    log_success "Entry point contains @app.function_name decorators"
                else
                    log_warning "Entry point does not contain FunctionApp or decorators"
                fi
            else
                log_error "Entry point file not found: src/azure/$SCRIPT_FILE"
            fi
        else
            log_error "host.json does not specify scriptFile"
        fi
    else
        log_error "host.json not found in src/azure/"
    fi
    
    # Check function.json
    if [ -f "src/azure/function.json" ]; then
        log_success "function.json exists"
        
        # Check scriptFile in function.json
        SCRIPT_FILE=$(cat src/azure/function.json | grep -oP '(?<="scriptFile": ")[^"]+' || echo "NOT_FOUND")
        if [ "$SCRIPT_FILE" != "NOT_FOUND" ]; then
            log_success "function.json scriptFile: $SCRIPT_FILE"
        else
            log_error "function.json does not specify scriptFile"
        fi
    else
        log_error "function.json not found in src/azure/"
    fi
    
    # Check for duplicate function directories
    log_info "1.4 Checking for duplicate function directories..."
    
    DUPLICATE_DIRS=("mcp_function" "functions" "functionapp" "azure_functions")
    FOUND_DUPLICATES=0
    
    for dir in "${DUPLICATE_DIRS[@]}"; do
        if [ -d "$dir/" ]; then
            log_warning "Found potential duplicate directory: $dir/"
            FOUND_DUPLICATES=1
        fi
    done
    
    if [ $FOUND_DUPLICATES -eq 0 ]; then
        log_success "No duplicate function directories found"
    fi
    
    # Check for multiple host.json files
    log_info "1.5 Checking for multiple host.json files..."
    
    HOST_JSON_COUNT=$(find . -name "host.json" -type f | wc -l)
    if [ "$HOST_JSON_COUNT" -eq 1 ]; then
        log_success "Found exactly 1 host.json file"
    else
        log_error "Found $HOST_JSON_COUNT host.json files. Expected: 1"
        find . -name "host.json" -type f
    fi
    
    # Check for multiple function.json files
    log_info "1.6 Checking for multiple function.json files..."
    
    FUNCTION_JSON_COUNT=$(find . -name "function.json" -type f | wc -l)
    if [ "$FUNCTION_JSON_COUNT" -eq 1 ]; then
        log_success "Found exactly 1 function.json file"
    else
        log_error "Found $FUNCTION_JSON_COUNT function.json files. Expected: 1"
        find . -name "function.json" -type f
    fi
}

# ============================================================================
# SECTION 2: DEPLOYMENT CONFIGURATION VERIFICATION
# ============================================================================

section_2() {
    log_info "=== SECTION 2: DEPLOYMENT CONFIGURATION VERIFICATION ==="
    
    # ✅ Check .funcignore
    log_info "2.1 Checking .funcignore..."
    
    if [ ! -f ".funcignore" ]; then
        log_error "Missing .funcignore file"
        log_info "Fix: Create .funcignore file (see recommended content below)"
    else
        log_success ".funcignore exists"
        
        # Check for common patterns
        if ! grep -q "\.python_packages/" .funcignore 2>/dev/null; then
            log_warning "Missing .python_packages/ in .funcignore"
        else
            log_success ".funcignore excludes .python_packages/"
        fi
        
        if ! grep -q "__pycache__/" .funcignore 2>/dev/null; then
            log_warning "Missing __pycache__/ in .funcignore"
        else
            log_success ".funcignore excludes __pycache__/"
        fi
        
        if ! grep -q "\.venv/" .funcignore 2>/dev/null; then
            log_warning "Missing .venv/ in .funcignore"
        else
            log_success ".funcignore excludes .venv/"
        fi
        
        if ! grep -q "tests/" .funcignore 2>/dev/null; then
            log_warning "Missing tests/ in .funcignore"
        else
            log_success ".funcignore excludes tests/"
        fi
        
        if ! grep -q "docs/" .funcignore 2>/dev/null; then
            log_warning "Missing docs/ in .funcignore"
        else
            log_success ".funcignore excludes docs/"
        fi
        
        if ! grep -q "local.settings.json" .funcignore 2>/dev/null; then
            log_warning "Missing local.settings.json in .funcignore"
        else
            log_success ".funcignore excludes local.settings.json"
        fi
    fi
    
    # ✅ Check requirements.txt
    log_info "2.2 Checking requirements.txt..."
    
    if [ ! -f "src/azure/requirements.txt" ]; then
        log_error "Missing src/azure/requirements.txt"
    else
        log_success "src/azure/requirements.txt exists"
        
        # Check for Rust-dependent packages
        if grep -q "cryptography>=4[2-9]" src/azure/requirements.txt 2>/dev/null; then
            log_warning "cryptography>=42.0.0 requires Rust compiler (may hang Oryx)"
            log_info "Fix: Pin cryptography to <42.0.0: cryptography>=41.0.0,<42.0.0"
        else
            log_success "No Rust-dependent cryptography version found"
        fi
        
        # Check for multiple requirement files
        MULTIPLE_REQS=$(ls requirements-*.txt 2>/dev/null | wc -l)
    MULTIPLE_REQS=${MULTIPLE_REQS:-0}
        if [ "$MULTIPLE_REQS" -gt 0 ] 2>/dev/null; then
            log_warning "Found $MULTIPLE_REQS additional requirement files"
            ls requirements-*.txt 2>/dev/null
            log_info "Fix: Consolidate all dependencies into a single requirements.txt"
        else
            log_success "No duplicate requirement files found"
        fi
        
        # Check for development packages
        if grep -qE "black|flake8|mypy|pytest|isort" src/azure/requirements.txt 2>/dev/null; then
            log_warning "Development packages found in production requirements.txt"
            log_info "Fix: Remove development packages from production requirements.txt"
        else
            log_success "No development packages in production requirements.txt"
        fi
        
        # Check for azure-functions
        if grep -q "azure-functions" src/azure/requirements.txt 2>/dev/null; then
            log_success "azure-functions found in requirements.txt"
        else
            log_error "azure-functions not found in requirements.txt"
        fi
    fi
    
    # Check for .gitignore
    log_info "2.3 Checking .gitignore..."
    
    if [ ! -f ".gitignore" ]; then
        log_error "Missing .gitignore file"
    else
        log_success ".gitignore exists"
        
        # Check for common patterns
        if ! grep -q "__pycache__/" .gitignore 2>/dev/null; then
            log_warning "Missing __pycache__/ in .gitignore"
        else
            log_success ".gitignore excludes __pycache__/"
        fi
        
        if ! grep -q "\.venv/" .gitignore 2>/dev/null; then
            log_warning "Missing .venv/ in .gitignore"
        else
            log_success ".gitignore excludes .venv/"
        fi
    fi
}

# ============================================================================
# SECTION 3: MCP-SPECIFIC VERIFICATION
# ============================================================================

section_3() {
    log_info "=== SECTION 3: MCP-SPECIFIC VERIFICATION ==="
    
    # Check for MCP Server implementation
    log_info "3.1 Checking for MCP Server implementation..."
    
    if [ -f "src/azure/mcp_server.py" ]; then
        log_success "MCP Server implementation exists: src/azure/mcp_server.py"
        
        # Check for MCP protocol version
        if grep -q "MCP_PROTOCOL_VERSION" src/azure/mcp_server.py; then
            PROTOCOL_VERSION=$(grep "MCP_PROTOCOL_VERSION" src/azure/mcp_server.py | grep -oP '(?<=")[^"]+' || echo "NOT_FOUND")
            if [ "$PROTOCOL_VERSION" != "NOT_FOUND" ]; then
                log_success "MCP Protocol Version: $PROTOCOL_VERSION"
                
                # Check if it's the latest version
                if [ "$PROTOCOL_VERSION" = "2024-11-05" ]; then
                    log_success "Using latest MCP Protocol version"
                else
                    log_warning "Using MCP Protocol version $PROTOCOL_VERSION (latest: 2024-11-05)"
                fi
            fi
        else
            log_warning "MCP_PROTOCOL_VERSION not defined in mcp_server.py"
        fi
        
        # Check for MCP endpoints
        MCP_ENDPOINTS=("mcp/health" "mcp/metadata" "mcp/tools" "mcp/resources" "mcp/prompts" "mcp/completions")
        for endpoint in "${MCP_ENDPOINTS[@]}"; do
            if grep -q "$endpoint" src/azure/mcp_server.py; then
                log_success "MCP endpoint $endpoint implemented"
            else
                log_error "MCP endpoint $endpoint not found"
            fi
        done
        
        # Check for MCP Server class
        if grep -q "class MCPServer" src/azure/mcp_server.py; then
            log_success "MCPServer class found"
        else
            log_error "MCPServer class not found"
        fi
        
        # Check for MCP Server instance
        if grep -q "mcp_server = MCPServer()" src/azure/mcp_server.py; then
            log_success "MCPServer instance created"
        else
            log_error "MCPServer instance not created"
        fi
    else
        log_error "MCP Server implementation not found"
        log_info "Fix: Create src/azure/mcp_server.py with MCP protocol implementation"
    fi
    
    # Check for v4 FunctionApp implementation
    log_info "3.2 Checking for Azure Functions v4 implementation..."
    
    if [ -f "src/azure/function_app_v4.py" ]; then
        log_success "Azure Functions v4 implementation exists: src/azure/function_app_v4.py"
        
        # Check for FunctionApp instance
        if grep -q "app = func.FunctionApp()" src/azure/function_app_v4.py; then
            log_success "FunctionApp instance found in v4 implementation"
        else
            log_error "FunctionApp instance not found in v4 implementation"
        fi
        
        # Check for @app.function_name decorators
        DECORATOR_COUNT=$(grep -c "@app.function_name" src/azure/function_app_v4.py || echo "0")
        if [ "$DECORATOR_COUNT" -gt 0 ]; then
            log_success "Found $DECORATOR_COUNT @app.function_name decorators in v4 implementation"
        else
            log_error "No @app.function_name decorators found in v4 implementation"
        fi
        
        # Check for MCP endpoints in v4
        MCP_V4_ENDPOINTS=("mcp_health" "mcp_metadata" "mcp_tools_list" "mcp_tools_execute" "mcp_resources_list" "mcp_completions")
        for func_name in "${MCP_V4_ENDPOINTS[@]}"; do
            if grep -q "def $func_name" src/azure/function_app_v4.py; then
                log_success "MCP v4 function $func_name implemented"
            else
                log_error "MCP v4 function $func_name not found"
            fi
        done
    else
        log_warning "Azure Functions v4 implementation not found (using v2 model)"
    fi
    
    # Check for host_v4.json
    log_info "3.3 Checking for v4 host configuration..."
    
    if [ -f "src/azure/host_v4.json" ]; then
        log_success "host_v4.json exists"
        
        # Check for function list
        FUNCTION_COUNT=$(cat src/azure/host_v4.json | grep -oP '(?<="functions": \[)[^\]]+' | tr ',' '\n' | wc -l || echo "0")
        if [ "$FUNCTION_COUNT" -gt 0 ]; then
            log_success "host_v4.json lists $FUNCTION_COUNT functions"
        else
            log_error "host_v4.json does not list any functions"
        fi
    else
        log_warning "host_v4.json not found (using host.json)"
    fi
}

# ============================================================================
# SECTION 4: IMPORT AND DEPENDENCY VERIFICATION
# ============================================================================

section_4() {
    log_info "=== SECTION 4: IMPORT AND DEPENDENCY VERIFICATION ==="
    
    # Test importing the main modules
    log_info "4.1 Testing module imports..."
    
    # Test importing function_app
    if python -c "import sys; sys.path.insert(0, 'src'); from azure.function_app import app" 2>/dev/null; then
        log_success "function_app imports successfully"
    else
        log_error "function_app import failed"
        log_info "Fix: Check for missing dependencies or import errors"
    fi
    
    # Test importing mcp_server
    if python -c "import sys; sys.path.insert(0, 'src'); from azure.mcp_server import MCPServer" 2>/dev/null; then
        log_success "mcp_server imports successfully"
    else
        log_error "mcp_server import failed"
        log_info "Fix: Check for missing dependencies or import errors"
    fi
    
    # Test importing function_app_v4
    if [ -f "src/azure/function_app_v4.py" ]; then
        if python -c "import sys; sys.path.insert(0, 'src'); from azure.function_app_v4 import app" 2>/dev/null; then
            log_success "function_app_v4 imports successfully"
        else
            log_error "function_app_v4 import failed"
            log_info "Fix: Check for missing dependencies or import errors"
        fi
    fi
    
    # Test importing azure.functions
    if python -c "import azure.functions as func; print(func.__version__)" 2>/dev/null; then
        log_success "azure.functions imports successfully"
    else
        log_error "azure.functions import failed"
        log_info "Fix: Install azure-functions package: pip install azure-functions"
    fi
    
    # Test dependency installation
    log_info "4.2 Testing dependency installation..."
    
    if [ -f "src/azure/requirements.txt" ]; then
        if python -m pip install -r src/azure/requirements.txt --dry-run 2>&1 | grep -iE "error|conflict" > /dev/null; then
            log_error "Dependency conflicts detected"
            log_info "Fix: Resolve dependency conflicts in requirements.txt"
        else
            log_success "No dependency conflicts detected"
        fi
    fi
}

# ============================================================================
# SECTION 5: AZURE FUNCTIONS CONFIGURATION VERIFICATION
# ============================================================================

section_5() {
    log_info "=== SECTION 5: AZURE FUNCTIONS CONFIGURATION VERIFICATION ==="
    
    # Check FUNCTIONS_EXTENSION_VERSION
    log_info "5.1 Checking FUNCTIONS_EXTENSION_VERSION..."
    
    if [ -f "src/azure/host.json" ]; then
        EXTENSION_VERSION=$(cat src/azure/host.json | grep -oP '(?<="version": ")[^"]+' || echo "NOT_FOUND")
        if [ "$EXTENSION_VERSION" != "NOT_FOUND" ]; then
            log_success "Extension Bundle version: $EXTENSION_VERSION"
            
            # Check if it's valid
            if [[ "$EXTENSION_VERSION" == "[4.*"* ]] || [[ "$EXTENSION_VERSION" == "[5.0.0)" ]]; then
                log_success "Valid extension bundle version range"
            else
                log_error "Invalid extension bundle version: $EXTENSION_VERSION"
                log_info "Fix: Use '[4.*, 5.0.0)' for extension bundle version"
            fi
        else
            log_error "Extension bundle version not specified in host.json"
        fi
    fi
    
    # Check function timeout
    log_info "5.2 Checking function timeout..."
    
    if [ -f "src/azure/host.json" ]; then
        TIMEOUT=$(cat src/azure/host.json | grep -oP '(?<="functionTimeout": ")[^"]+' || echo "NOT_FOUND")
        if [ "$TIMEOUT" != "NOT_FOUND" ]; then
            log_success "Function timeout: $TIMEOUT"
        else
            log_warning "Function timeout not specified (default: 5 minutes)"
        fi
    fi
    
    # Check for Python version compatibility
    log_info "5.3 Checking Python version compatibility..."
    
    if grep -q "azure-functions>=1.21.0" src/azure/requirements.txt 2>/dev/null; then
        log_success "Using azure-functions>=1.21.0 (compatible with Python 3.11)"
    elif grep -q "azure-functions>=1.15.0" src/azure/requirements.txt 2>/dev/null; then
        log_warning "Using azure-functions>=1.15.0 (compatible but consider upgrading to >=1.21.0)"
    else
        log_error "azure-functions version not found or too old"
        log_info "Fix: Use azure-functions>=1.21.0 in requirements.txt"
    fi
}

# ============================================================================
# SECTION 6: DEPLOYMENT READINESS VERIFICATION
# ============================================================================

section_6() {
    log_info "=== SECTION 6: DEPLOYMENT READINESS VERIFICATION ==="
    
    # Check if deployment package can be created
    log_info "6.1 Testing deployment package creation..."
    
    cd src/azure
    if zip -r ../test-deployment.zip . > /dev/null 2>&1; then
        log_success "Deployment package created successfully"
        
        # Check package contents
        if unzip -l ../test-deployment.zip | grep -q "host.py" 2>/dev/null; then
            log_success "Package contains host.py"
        else
            log_error "Package missing host.py"
        fi
        
        if unzip -l ../test-deployment.zip | grep -q "function_app" 2>/dev/null; then
            log_success "Package contains function_app"
        else
            log_error "Package missing function_app"
        fi
        
        if unzip -l ../test-deployment.zip | grep -q "mcp_server" 2>/dev/null; then
            log_success "Package contains mcp_server"
        else
            log_warning "Package missing mcp_server (MCP endpoints won't work)"
        fi
        
        # Clean up
        rm -f ../test-deployment.zip
    else
        log_error "Failed to create deployment package"
    fi
    cd ../..
    
    # Check for Azure CLI
    log_info "6.2 Checking Azure CLI..."
    
    if command -v az &> /dev/null; then
        log_success "Azure CLI is installed"
    else
        log_warning "Azure CLI is not installed (required for deployment)"
    fi
    
    # Check for authentication
    log_info "6.3 Checking Azure authentication..."
    
    if az account show &> /dev/null; then
        log_success "Azure CLI is authenticated"
    else
        log_warning "Azure CLI is not authenticated (required for deployment)"
    fi
}

# ============================================================================
# MAIN FUNCTION
# ============================================================================

main() {
    log_info "Starting MCP Server Debugging and Validation..."
    echo ""
    
    # Run all sections
    section_1
    echo ""
    section_2
    echo ""
    section_3
    echo ""
    section_4
    echo ""
    section_5
    echo ""
    section_6
    
    # Print summary
    print_summary
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --section)
            SECTION="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --section <1-6>   Run only specific section"
            echo "  --help, -h        Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run main function
main "$@"
