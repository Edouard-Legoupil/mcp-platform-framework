#!/bin/bash

# MCP Framework - Azure Functions Remediation Script
# This script provides commands to diagnose and fix common Azure Functions deployment issues

set -euo pipefail

# Configuration - can be overridden by environment variables
RESOURCE_GROUP="${RESOURCE_GROUP:-mcp-dev-rg}"
FUNCTION_APP_NAME="${FUNCTION_APP_NAME:-mcp-dev-func}"
STORAGE_ACCOUNT_NAME="${STORAGE_ACCOUNT_NAME:-mcpdevstorage}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Azure CLI is installed
check_azure_cli() {
    if ! command -v az &> /dev/null; then
        log_error "Azure CLI is not installed. Please install it from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
        exit 1
    fi
}

# Login to Azure
azure_login() {
    log_info "Checking Azure authentication..."
    if ! az account show &> /dev/null; then
        log_info "Please login to Azure..."
        az login
    fi
}

# SECTION D - Azure Configuration Validation
validate_azure_configuration() {
    log_info "=== SECTION D - Azure Configuration Validation ==="
    
    # 1. Validate Function App runtime
    log_info "1. Validating Function App runtime..."
    RUNTIME=$(az functionapp show \
        --name "$FUNCTION_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query "siteConfig.linuxFxVersion" \
        -o tsv 2>/dev/null || echo "NOT_FOUND")
    
    if [ "$RUNTIME" = "python|3.11" ] || [ "$RUNTIME" = "python|3.10" ] || [ "$RUNTIME" = "python|3.9" ]; then
        log_success "Function App runtime: $RUNTIME"
    else
        log_error "Function App runtime is incorrect: $RUNTIME"
        log_info "Expected: python|3.11"
        log_info "Fix: az functionapp update --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP --linux-fx-version 'python|3.11'"
    fi
    
    # 2. Validate Python version
    log_info "2. Validating Python version..."
    PYTHON_VERSION=$(az functionapp config show \
        --name "$FUNCTION_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query "pythonVersion" \
        -o tsv 2>/dev/null || echo "NOT_FOUND")
    
    if [ "$PYTHON_VERSION" = "3.11" ] || [ "$PYTHON_VERSION" = "3.10" ] || [ "$PYTHON_VERSION" = "3.9" ]; then
        log_success "Python version: $PYTHON_VERSION"
    else
        log_error "Python version is incorrect: $PYTHON_VERSION"
        log_info "Fix: az functionapp config set --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP --python-version 3.11"
    fi
    
    # 3. Validate LinuxFxVersion
    log_info "3. Validating LinuxFxVersion..."
    LINUX_FX_VERSION=$(az functionapp show \
        --name "$FUNCTION_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query "siteConfig.linuxFxVersion" \
        -o tsv 2>/dev/null || echo "NOT_FOUND")
    
    if [[ "$LINUX_FX_VERSION" == "python|3.11" ]]; then
        log_success "LinuxFxVersion: $LINUX_FX_VERSION"
    else
        log_error "LinuxFxVersion is incorrect: $LINUX_FX_VERSION"
        log_info "Fix: az functionapp update --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP --linux-fx-version 'python|3.11'"
    fi
    
    # 4. Validate FUNCTIONS_WORKER_RUNTIME
    log_info "4. Validating FUNCTIONS_WORKER_RUNTIME..."
    WORKER_RUNTIME=$(az functionapp config appsettings list \
        --name "$FUNCTION_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query "[?name=='FUNCTIONS_WORKER_RUNTIME'].value | [0]" \
        -o tsv 2>/dev/null || echo "NOT_FOUND")
    
    if [ "$WORKER_RUNTIME" = "python" ]; then
        log_success "FUNCTIONS_WORKER_RUNTIME: $WORKER_RUNTIME"
    else
        log_error "FUNCTIONS_WORKER_RUNTIME is incorrect: $WORKER_RUNTIME"
        log_info "Fix: az functionapp config appsettings set --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP --settings FUNCTIONS_WORKER_RUNTIME=python"
    fi
    
    # 5. Validate SCM_DO_BUILD_DURING_DEPLOYMENT
    log_info "5. Validating SCM_DO_BUILD_DURING_DEPLOYMENT..."
    BUILD_DURING_DEPLOYMENT=$(az functionapp config appsettings list \
        --name "$FUNCTION_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query "[?name=='SCM_DO_BUILD_DURING_DEPLOYMENT'].value | [0]" \
        -o tsv 2>/dev/null || echo "NOT_FOUND")
    
    if [ "$BUILD_DURING_DEPLOYMENT" = "true" ] || [ "$BUILD_DURING_DEPLOYMENT" = "True" ] || [ "$BUILD_DURING_DEPLOYMENT" = "1" ]; then
        log_success "SCM_DO_BUILD_DURING_DEPLOYMENT: $BUILD_DURING_DEPLOYMENT"
    else
        log_warning "SCM_DO_BUILD_DURING_DEPLOYMENT is not set to true: $BUILD_DURING_DEPLOYMENT"
        log_info "Fix: az functionapp config appsettings set --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true"
    fi
    
    # 6. Validate ENABLE_ORYX_BUILD
    log_info "6. Validating ENABLE_ORYX_BUILD..."
    ENABLE_ORYX=$(az functionapp config appsettings list \
        --name "$FUNCTION_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query "[?name=='ENABLE_ORYX_BUILD'].value | [0]" \
        -o tsv 2>/dev/null || echo "NOT_FOUND")
    
    if [ "$ENABLE_ORYX" = "true" ] || [ "$ENABLE_ORYX" = "True" ] || [ "$ENABLE_ORYX" = "1" ]; then
        log_success "ENABLE_ORYX_BUILD: $ENABLE_ORYX"
    else
        log_warning "ENABLE_ORYX_BUILD is not set to true: $ENABLE_ORYX"
        log_info "Fix: az functionapp config appsettings set --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP --settings ENABLE_ORYX_BUILD=true"
    fi
    
    # 7. Validate WEBSITE_RUN_FROM_PACKAGE
    log_info "7. Validating WEBSITE_RUN_FROM_PACKAGE..."
    RUN_FROM_PACKAGE=$(az functionapp config appsettings list \
        --name "$FUNCTION_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query "[?name=='WEBSITE_RUN_FROM_PACKAGE'].value | [0]" \
        -o tsv 2>/dev/null || echo "NOT_FOUND")
    
    if [ "$RUN_FROM_PACKAGE" = "1" ] || [ "$RUN_FROM_PACKAGE" = "true" ]; then
        log_success "WEBSITE_RUN_FROM_PACKAGE: $RUN_FROM_PACKAGE"
    else
        log_warning "WEBSITE_RUN_FROM_PACKAGE is not set to 1: $RUN_FROM_PACKAGE"
        log_info "Fix: az functionapp config appsettings set --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP --settings WEBSITE_RUN_FROM_PACKAGE=1"
    fi
    
    # 8. Validate AzureWebJobsStorage
    log_info "8. Validating AzureWebJobsStorage..."
    STORAGE_CONNECTION=$(az functionapp config appsettings list \
        --name "$FUNCTION_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query "[?name=='AzureWebJobsStorage'].value | [0]" \
        -o tsv 2>/dev/null || echo "NOT_FOUND")
    
    if [[ "$STORAGE_CONNECTION" == "DefaultEndpointsProtocol="* ]]; then
        log_success "AzureWebJobsStorage: Configured"
    else
        log_error "AzureWebJobsStorage is not configured properly"
        log_info "Fix: First create storage account, then set AzureWebJobsStorage"
    fi
}

# SECTION D - Generate Azure CLI commands for resource creation
generate_resource_commands() {
    log_info "=== SECTION D - Azure CLI Commands for Resource Creation ==="
    
    echo ""
    echo "# 1. Create a storage account"
    echo "az storage account create \\"
    echo "    --name $STORAGE_ACCOUNT_NAME \\"
    echo "    --resource-group $RESOURCE_GROUP \\"
    echo "    --location $LOCATION \\"
    echo "    --sku Standard_LRS \\"
    echo "    --kind StorageV2 \\"
    echo "    --access-tier Hot \\"
    echo "    --tags ApplicationName=\\\\