#!/bin/bash

# MCP Framework - Deployment Validation Script
# This script runs comprehensive validation checks before deployment

set -euo pipefail

# Configuration
FUNCTION_APP_NAME="${FUNCTION_APP_NAME:-mcp-dev-func}"
RESOURCE_GROUP="${RESOURCE_GROUP:-mcp-dev-rg}"
STORAGE_ACCOUNT_NAME="${STORAGE_ACCOUNT_NAME:-mcpdevstorage}"

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

# Print summary
print_summary() {
    echo ""
    echo "=========================================="
    echo "VALIDATION SUMMARY"
    echo "=========================================="
    echo -e "${GREEN}Passed: $PASSED${NC}"
    echo -e "${RED}Failed: $FAILED${NC}"
    echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
    echo "=========================================="
    
    if [ $FAILED -gt 0 ]; then
        echo -e "${RED}VALIDATION FAILED${NC}"
        echo "Please fix the failed checks before deployment."
        exit 1
    elif [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}VALIDATION PASSED WITH WARNINGS${NC}"
        echo "Consider addressing the warnings before deployment."
        exit 0
    else
        echo -e "${GREEN}VALIDATION PASSED${NC}"
        echo "All checks passed. Ready for deployment."
        exit 0
    fi
}

# Validate Section A - Project Structure
validate_section_a() {
    log_info "=== SECTION A - PROJECT STRUCTURE VALIDATION ==="
    
    # A.1 Required Files Exist
    log_info "A.1 Checking required files..."
    REQUIRED_FILES=(
        "src/azure/__init__.py"
        "src/azure/host.py"
        "src/azure/function_app.py"
        "src/azure/host.json"
        "src/azure/function.json"
        "src/azure/requirements.txt"
        "src/__init__.py"
        ".funcignore"
        ".gitignore"
    )
    
    for file in "${REQUIRED_FILES[@]}"; do
        if [ -f "$file" ]; then
            log_success "$file exists"
        else
            log_error "$file is missing"
        fi
    done
    
    # A.2 Project Structure
    log_info "A.2 Checking project structure..."
    
    # Check for duplicate function.json files
    DUPLICATE_FUNCTION_JSON=$(find . -name "function.json" -type f | grep -v "src/azure/function.json" || true)
    if [ -z "$DUPLICATE_FUNCTION_JSON" ]; then
        log_success "No duplicate function.json files"
    else
        log_error "Found duplicate function.json files: $DUPLICATE_FUNCTION_JSON"
    fi
    
    # Check for duplicate host.json files
    DUPLICATE_HOST_JSON=$(find . -name "host.json" -type f | grep -v "src/azure/host.json" || true)
    if [ -z "$DUPLICATE_HOST_JSON" ]; then
        log_success "No duplicate host.json files"
    else
        log_error "Found duplicate host.json files: $DUPLICATE_HOST_JSON"
    fi
    
    # Check if old azure_functions directory exists
    if [ -d "azure_functions/" ] && [ "$(ls -A azure_functions/ 2>/dev/null)" ]; then
        log_warning "Old azure_functions/ directory exists and is not empty"
    else
        log_success "No old azure_functions/ directory or it's empty"
    fi
    
    # A.3 Function App Export Validation
    log_info "A.3 Checking Function App exports..."
    
    if grep -q "^app = " src/azure/function_app.py; then
        log_success "function_app.py exports app object"
    else
        log_error "function_app.py does not export app object"
    fi
    
    if grep -q "from.*function_app import app" src/azure/host.py; then
        log_success "host.py imports app from function_app"
    else
        log_error "host.py does not import app from function_app"
    fi
    
    # A.4 Function JSON Validation
    log_info "A.4 Validating function.json..."
    
    if python -c "import json; json.load(open('src/azure/function.json'))" 2>/dev/null; then
        log_success "function.json is valid JSON"
    else
        log_error "function.json has invalid JSON syntax"
    fi
    
    if grep -q '"scriptFile": "host.py"' src/azure/function.json; then
        log_success "function.json references host.py"
    else
        log_error "function.json does not reference host.py"
    fi
    
    # A.5 Host JSON Validation
    log_info "A.5 Validating host.json..."
    
    if python -c "import json; json.load(open('src/azure/host.json'))" 2>/dev/null; then
        log_success "host.json is valid JSON"
    else
        log_error "host.json has invalid JSON syntax"
    fi
    
    if grep -q '"version": "2.0"' src/azure/host.json; then
        log_success "host.json has version 2.0"
    else
        log_error "host.json does not have version 2.0"
    fi
}

# Validate Section B - Deployment Configuration
validate_section_b() {
    log_info "=== SECTION B - DEPLOYMENT CONFIGURATION VALIDATION ==="
    
    # B.1 .funcignore Validation
    log_info "B.1 Validating .funcignore..."
    
    if grep -q "\.git/" .funcignore; then
        log_success ".funcignore excludes .git/"
    else
        log_error ".funcignore does not exclude .git/"
    fi
    
    if grep -q "\.venv/" .funcignore; then
        log_success ".funcignore excludes .venv/"
    else
        log_error ".funcignore does not exclude .venv/"
    fi
    
    if grep -q "docs/" .funcignore; then
        log_success ".funcignore excludes docs/"
    else
        log_error ".funcignore does not exclude docs/"
    fi
    
    if grep -q "tests/" .funcignore; then
        log_success ".funcignore excludes tests/"
    else
        log_error ".funcignore does not exclude tests/"
    fi
    
    if grep -q "!src/azure/" .funcignore; then
        log_success ".funcignore includes src/azure/"
    else
        log_error ".funcignore does not include src/azure/"
    fi
    
    # B.2 .gitignore Validation
    log_info "B.2 Validating .gitignore..."
    
    if grep -q "__pycache__/" .gitignore; then
        log_success ".gitignore excludes __pycache__/"
    else
        log_error ".gitignore does not exclude __pycache__/"
    fi
    
    if grep -q "\.pyc" .gitignore; then
        log_success ".gitignore excludes .pyc files"
    else
        log_error ".gitignore does not exclude .pyc files"
    fi
    
    if grep -q "\.venv/" .gitignore; then
        log_success ".gitignore excludes .venv/"
    else
        log_error ".gitignore does not exclude .venv/"
    fi
}

# Validate Section C - Dependencies
validate_section_c() {
    log_info "=== SECTION C - DEPENDENCY VALIDATION ==="
    
    # C.1 requirements.txt Validation
    log_info "C.1 Validating requirements.txt..."
    
    if grep -q "azure-functions" src/azure/requirements.txt; then
        log_success "requirements.txt contains azure-functions"
    else
        log_error "requirements.txt does not contain azure-functions"
    fi
    
    if grep -q "azure-identity" src/azure/requirements.txt; then
        log_success "requirements.txt contains azure-identity"
    else
        log_error "requirements.txt does not contain azure-identity"
    fi
    
    if grep -q "pydantic" src/azure/requirements.txt; then
        log_success "requirements.txt contains pydantic"
    else
        log_error "requirements.txt does not contain pydantic"
    fi
    
    # Check for development packages (should NOT be present)
    if grep -qE "black|flake8|mypy|pytest" src/azure/requirements.txt; then
        log_warning "requirements.txt contains development packages"
    else
        log_success "requirements.txt does not contain development packages"
    fi
    
    # C.2 Dependency Installation Test
    log_info "C.2 Testing dependency installation..."
    
    if python -m pip install -r src/azure/requirements.txt --dry-run 2>&1 | grep -iE "error|conflict" > /dev/null; then
        log_error "Dependency conflicts detected"
    else
        log_success "No dependency conflicts detected"
    fi
    
    # C.3 Azure Functions Compatibility
    log_info "C.3 Checking for incompatible packages..."
    
    INCOMPATIBLE_PACKAGES=("numpy" "pandas" "scipy" "tensorflow" "pytorch" "matplotlib" "seaborn")
    FOUND_INCOMPATIBLE=0
    
    for pkg in "${INCOMPATIBLE_PACKAGES[@]}"; do
        if grep -q "$pkg" src/azure/requirements.txt; then
            log_warning "Found potentially incompatible package: $pkg"
            FOUND_INCOMPATIBLE=1
        fi
    done
    
    if [ $FOUND_INCOMPATIBLE -eq 0 ]; then
        log_success "No known incompatible packages found"
    fi
}

# Validate Section D - Azure Configuration
validate_section_d() {
    log_info "=== SECTION D - AZURE CONFIGURATION VALIDATION ==="
    
    # D.1 Function App Configuration
    log_info "D.1 Validating Azure resource names..."
    
    # Function App name (2-60 chars, alphanumeric + hyphens)
    if [[ "$FUNCTION_APP_NAME" =~ ^[a-zA-Z0-9-]{2,60}$ ]]; then
        log_success "Function App name is valid: $FUNCTION_APP_NAME"
    else
        log_error "Function App name is invalid: $FUNCTION_APP_NAME"
    fi
    
    # Storage account name (3-24 chars, lowercase alphanumeric)
    if [[ "$STORAGE_ACCOUNT_NAME" =~ ^[a-z0-9]{3,24}$ ]]; then
        log_success "Storage account name is valid: $STORAGE_ACCOUNT_NAME"
    else
        log_error "Storage account name is invalid: $STORAGE_ACCOUNT_NAME"
    fi
    
    # D.2 Tag Validation
    log_info "D.2 Validating required tags..."
    
    REQUIRED_TAGS=("APPLICATION_NAME" "BUSINESS_OWNER" "COST_CENTRE" "ENVIRONMENT" "PROJECT" "TECHNICAL_OWNER")
    
    for tag in "${REQUIRED_TAGS[@]}"; do
        if [ -z "${!tag}" ]; then
            log_warning "Required tag $tag is not set"
        else
            log_success "Tag $tag is set: ${!tag}"
        fi
    done
}

# Validate Section E - Deployment Package
validate_section_e() {
    log_info "=== SECTION E - DEPLOYMENT PACKAGE VALIDATION ==="
    
    log_info "E.1 Creating test deployment package..."
    
    # Create test deployment package
    cd src/azure
    zip -r ../test-deployment.zip . > /dev/null 2>&1
    cd ../..
    
    if [ -f "src/test-deployment.zip" ]; then
        log_success "Deployment package created successfully"
        
        # Check package contents
        REQUIRED_FILES=("host.py" "function_app.py" "host.json" "function.json" "requirements.txt")
        
        for file in "${REQUIRED_FILES[@]}"; do
            if unzip -l src/test-deployment.zip | grep -q "$file"; then
                log_success "Package contains $file"
            else
                log_error "Package missing $file"
            fi
        done
        
        # Clean up
        rm -f src/test-deployment.zip
    else
        log_error "Failed to create deployment package"
    fi
}

# Validate Section F - Local Testing
validate_section_f() {
    log_info "=== SECTION F - LOCAL TESTING VALIDATION ==="
    
    log_info "F.1 Testing imports..."
    
    # Test imports
    cd src/azure
    if python -c "from function_app import app" 2>/dev/null; then
        log_success "function_app imports successfully"
    else
        log_error "function_app import failed"
    fi
    
    if python -c "from host import main" 2>/dev/null; then
        log_success "host imports successfully"
    else
        log_error "host import failed"
    fi
    
    if python -c "import azure.functions as func" 2>/dev/null; then
        log_success "azure.functions imports successfully"
    else
        log_error "azure.functions import failed"
    fi
    cd ../..
}

# Validate Section G - Azure CLI (Post-Deployment)
validate_section_g() {
    log_info "=== SECTION G - AZURE CLI VALIDATION ==="
    
    # G.1 Azure CLI Availability
    log_info "G.1 Checking Azure CLI..."
    
    if command -v az &> /dev/null; then
        log_success "Azure CLI is installed"
        log_info "  Version: $(az --version | head -1)"
    else
        log_warning "Azure CLI is not installed (required for deployment)"
    fi
    
    # G.2 Azure Authentication
    log_info "G.2 Checking Azure authentication..."
    
    if az account show &> /dev/null; then
        log_success "Azure CLI is authenticated"
        log_info "  User: $(az account show --query user.name -o tsv)"
        log_info "  Subscription: $(az account show --query name -o tsv)"
    else
        log_warning "Azure CLI is not authenticated (required for deployment)"
    fi
    
    # G.3 Function App Status (only if deployed)
    log_info "G.3 Checking Function App status..."
    
    if az functionapp show --name "$FUNCTION_APP_NAME" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
        STATE=$(az functionapp show --name "$FUNCTION_APP_NAME" --resource-group "$RESOURCE_GROUP" --query state -o tsv)
        if [ "$STATE" = "Running" ]; then
            log_success "Function App is running"
        else
            log_error "Function App state: $STATE"
        fi
        
        RUNTIME=$(az functionapp show --name "$FUNCTION_APP_NAME" --resource-group "$RESOURCE_GROUP" --query "siteConfig.linuxFxVersion" -o tsv)
        if [[ "$RUNTIME" == "python|3.11" ]]; then
            log_success "Function App runtime: $RUNTIME"
        else
            log_error "Function App runtime: $RUNTIME (expected: python|3.11)"
        fi
    else
        log_info "Function App not yet deployed or does not exist"
    fi
}

# Main function
main() {
    # Parse command line arguments
    SECTION=""
    
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
                echo "  --section <A|B|C|D|E|F|G>   Run only specific section validation"
                echo "  --help, -h                  Show this help message"
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    log_info "Starting MCP Framework deployment validation..."
    echo ""
    
    # Run all sections or specific section
    if [ -z "$SECTION" ]; then
        # Run all sections
        validate_section_a
        echo ""
        validate_section_b
        echo ""
        validate_section_c
        echo ""
        validate_section_d
        echo ""
        validate_section_e
        echo ""
        validate_section_f
        echo ""
        validate_section_g
    else
        # Run specific section
        case $SECTION in
            A|a) validate_section_a ;;
            B|b) validate_section_b ;;
            C|c) validate_section_c ;;
            D|d) validate_section_d ;;
            E|e) validate_section_e ;;
            F|f) validate_section_f ;;
            G|g) validate_section_g ;;
            *)
                echo "Unknown section: $SECTION"
                echo "Valid sections: A, B, C, D, E, F, G"
                exit 1
                ;;
        esac
    fi
    
    # Print summary
    print_summary
}

# Run main function
main "$@"
