#!/bin/bash

# MCP Framework - Azure Functions Deployment Script
# This script deploys the MCP Framework as an Azure Function App

set -euo pipefail

# Configuration
RESOURCE_GROUP="${RESOURCE_GROUP:-mcp-dev-rg}"
LOCATION="${LOCATION:-eastus}"
FUNCTION_APP_NAME="${FUNCTION_APP_NAME:-mcp-dev-func}"
STORAGE_ACCOUNT_NAME="${STORAGE_ACCOUNT_NAME:-mcpdevstorage}"
APPLICATION_INSIGHTS_NAME="${APPLICATION_INSIGHTS_NAME:-mcp-dev-appinsights}"

# Tags - Required for enterprise deployment
APPLICATION_NAME="${APPLICATION_NAME:-MCPFramework}"
BUSINESS_OWNER="${BUSINESS_OWNER:-business-owner@example.com}"
COST_CENTRE="${COST_CENTRE:-CC001}"
ENVIRONMENT="${ENVIRONMENT:-Development}"
PROJECT="${PROJECT:-MCPPlatform}"
TECHNICAL_OWNER="${TECHNICAL_OWNER:-tech-owner@example.com}"

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
    
    log_info "Azure CLI version: $(az --version | head -1)"
}

# Login to Azure
azure_login() {
    log_info "Checking Azure authentication..."
    if ! az account show &> /dev/null; then
        log_info "Please login to Azure..."
        az login
    fi
    
    log_info "Logged in as: $(az account show --query user.name -o tsv)"
    log_info "Subscription: $(az account show --query name -o tsv)"
}

# Create resource group
create_resource_group() {
    log_info "Creating resource group: $RESOURCE_GROUP"
    
    if az group exists --name "$RESOURCE_GROUP"; then
        log_info "Resource group already exists"
    else
        az group create \
            --name "$RESOURCE_GROUP" \
            --location "$LOCATION" \
            --tags ApplicationName="$APPLICATION_NAME" \
                   BusinessOwner="$BUSINESS_OWNER" \
                   CostCentre="$COST_CENTRE" \
                   Environment="$ENVIRONMENT" \
                   Project="$PROJECT" \
                   TechnicalOwner="$TECHNICAL_OWNER"
        
        log_success "Resource group created"
    fi
}

# Create storage account
create_storage_account() {
    log_info "Creating storage account: $STORAGE_ACCOUNT_NAME"
    
    if az storage account show --name "$STORAGE_ACCOUNT_NAME" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
        log_info "Storage account already exists"
    else
        az storage account create \
            --name "$STORAGE_ACCOUNT_NAME" \
            --resource-group "$RESOURCE_GROUP" \
            --location "$LOCATION" \
            --sku Standard_LRS \
            --kind StorageV2 \
            --access-tier Hot \
            --enable-hierarchical-namespace false \
            --tags ApplicationName="$APPLICATION_NAME" \
                   BusinessOwner="$BUSINESS_OWNER" \
                   CostCentre="$COST_CENTRE" \
                   Environment="$ENVIRONMENT" \
                   Project="$PROJECT" \
                   TechnicalOwner="$TECHNICAL_OWNER"
        
        log_success "Storage account created"
    fi
}

# Create Application Insights
create_application_insights() {
    log_info "Creating Application Insights: $APPLICATION_INSIGHTS_NAME"
    
    if az resource show --name "$APPLICATION_INSIGHTS_NAME" --resource-group "$RESOURCE_GROUP" --resource-type "Microsoft.Insights/components" &> /dev/null; then
        log_info "Application Insights already exists"
    else
        az monitor app-insights create \
            --name "$APPLICATION_INSIGHTS_NAME" \
            --resource-group "$RESOURCE_GROUP" \
            --location "$LOCATION" \
            --kind web \
            --application-type web \
            --retention-time 90 \
            --tags ApplicationName="$APPLICATION_NAME" \
                   BusinessOwner="$BUSINESS_OWNER" \
                   CostCentre="$COST_CENTRE" \
                   Environment="$ENVIRONMENT" \
                   Project="$PROJECT" \
                   TechnicalOwner="$TECHNICAL_OWNER"
        
        log_success "Application Insights created"
    fi
}

# Create Function App (Consumption Plan)
create_function_app() {
    log_info "Creating Function App: $FUNCTION_APP_NAME"
    
    if az functionapp show --name "$FUNCTION_APP_NAME" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
        log_info "Function App already exists"
    else
        # Get storage account connection string
        STORAGE_CONNECTION_STRING=$(az storage account show-connection-string \
            --name "$STORAGE_ACCOUNT_NAME" \
            --resource-group "$RESOURCE_GROUP" \
            --query connectionString \
            -o tsv)
        
        # Get Application Insights instrumentation key
        APP_INSIGHTS_KEY=$(az monitor app-insights show \
            --name "$APPLICATION_INSIGHTS_NAME" \
            --resource-group "$RESOURCE_GROUP" \
            --query instrumentationKey \
            -o tsv)
        
        az functionapp create \
            --name "$FUNCTION_APP_NAME" \
            --resource-group "$RESOURCE_GROUP" \
            --consumption-plan-location "$LOCATION" \
            --runtime python \
            --runtime-version 3.11 \
            --functions-version 4 \
            --storage-account "$STORAGE_ACCOUNT_NAME" \
            --os-type Linux \
            --tags ApplicationName="$APPLICATION_NAME" \
                   BusinessOwner="$BUSINESS_OWNER" \
                   CostCentre="$COST_CENTRE" \
                   Environment="$ENVIRONMENT" \
                   Project="$PROJECT" \
                   TechnicalOwner="$TECHNICAL_OWNER" \
            --app-insights "$APPLICATION_INSIGHTS_NAME"
        
        log_success "Function App created"
        
        # Configure Function App settings
        configure_function_app_settings
    fi
}

# Configure Function App settings
configure_function_app_settings() {
    log_info "Configuring Function App settings..."
    
    # Get storage account connection string
    STORAGE_CONNECTION_STRING=$(az storage account show-connection-string \
        --name "$STORAGE_ACCOUNT_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query connectionString \
        -o tsv)
    
    # Get Application Insights instrumentation key
    APP_INSIGHTS_KEY=$(az monitor app-insights show \
        --name "$APPLICATION_INSIGHTS_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query instrumentationKey \
        -o tsv)
    
    # Set required configuration
    az functionapp config appsettings set \
        --name "$FUNCTION_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --settings \
            AzureWebJobsStorage="$STORAGE_CONNECTION_STRING" \
            FUNCTIONS_WORKER_RUNTIME=python \
            FUNCTIONS_EXTENSION_VERSION=~4 \
            APPINSIGHTS_INSTRUMENTATIONKEY="$APP_INSIGHTS_KEY" \
            APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=$APP_INSIGHTS_KEY;IngestionEndpoint=https://$LOCATION.in.applicationinsights.azure.com/" \
            WEBSITE_RUN_FROM_PACKAGE=1 \
            ENABLE_ORYX_BUILD=true \
            SCM_DO_BUILD_DURING_DEPLOYMENT=true \
            PythonVersion=3.11
    
    # Set MCP Framework specific settings
    az functionapp config appsettings set \
        --name "$FUNCTION_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --settings \
            MCP_DOMAIN="MCPFramework" \
            MCP_ENVIRONMENT="$ENVIRONMENT" \
            MCP_VERSION="1.0.0" \
            MCP_ENABLE_TELEMETRY=true \
            MCP_ENABLE_AUDIT=true \
            MCP_ENABLE_AUTH=false \
            MCP_ENABLE_AUTHORIZATION=false \
            MCP_ENABLE_CLASSIFICATION=false
    
    log_success "Function App settings configured"
}

# Deploy the function app
deploy_function_app() {
    log_info "Deploying Function App..."
    
    # Check if we're using remote build (Oryx) or local build
    DEPLOYMENT_METHOD="${DEPLOYMENT_METHOD:-remote}"
    
    if [ "$DEPLOYMENT_METHOD" = "remote" ]; then
        log_info "Using remote build (Oryx)..."
        
        # Deploy from the src/azure directory
        az functionapp deployment source config-zip \
            --name "$FUNCTION_APP_NAME" \
            --resource-group "$RESOURCE_GROUP" \
            --src ./src/azure.zip
        
        log_success "Function App deployed using remote build"
    else
        log_info "Using local build..."
        
        # Create a deployment package
        cd src/azure
        zip -r ../azure-deployment.zip .
        cd ../..
        
        az functionapp deployment source config-zip \
            --name "$FUNCTION_APP_NAME" \
            --resource-group "$RESOURCE_GROUP" \
            --src ./src/azure-deployment.zip \
            --no-build
        
        log_success "Function App deployed using local build"
    fi
}

# Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check Function App status
    FUNCTION_APP_STATE=$(az functionapp show \
        --name "$FUNCTION_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query state \
        -o tsv)
    
    if [ "$FUNCTION_APP_STATE" = "Running" ]; then
        log_success "Function App is running"
    else
        log_error "Function App is not running. State: $FUNCTION_APP_STATE"
        exit 1
    fi
    
    # Check functions
    FUNCTIONS=$(az functionapp function list \
        --name "$FUNCTION_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query "[].name" \
        -o tsv)
    
    if [ -z "$FUNCTIONS" ]; then
        log_warning "No functions found. This might be expected during initial deployment."
    else
        log_info "Functions deployed: $FUNCTIONS"
    fi
    
    # Get Function App URL
    FUNCTION_APP_URL=$(az functionapp show \
        --name "$FUNCTION_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query defaultHostName \
        -o tsv)
    
    log_success "Function App URL: https://$FUNCTION_APP_URL"
    
    # Test health endpoint
    log_info "Testing health endpoint..."
    HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "https://$FUNCTION_APP_URL/api/health")
    
    if [ "$HEALTH_RESPONSE" = "200" ]; then
        log_success "Health endpoint is responding"
    else
        log_warning "Health endpoint returned HTTP $HEALTH_RESPONSE"
    fi
}

# Main deployment function
main() {
    log_info "Starting MCP Framework Azure Functions deployment..."
    
    # Check prerequisites
    check_azure_cli
    azure_login
    
    # Create infrastructure
    create_resource_group
    create_storage_account
    create_application_insights
    create_function_app
    
    # Deploy the application
    deploy_function_app
    
    # Verify deployment
    verify_deployment
    
    log_success "MCP Framework deployment completed successfully!"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --resource-group)
            RESOURCE_GROUP="$2"
            shift 2
            ;;
        --location)
            LOCATION="$2"
            shift 2
            ;;
        --function-app-name)
            FUNCTION_APP_NAME="$2"
            shift 2
            ;;
        --storage-account-name)
            STORAGE_ACCOUNT_NAME="$2"
            shift 2
            ;;
        --app-insights-name)
            APPLICATION_INSIGHTS_NAME="$2"
            shift 2
            ;;
        --deployment-method)
            DEPLOYMENT_METHOD="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --resource-group <name>           Azure resource group name"
            echo "  --location <location>             Azure region (default: eastus)"
            echo "  --function-app-name <name>       Function App name"
            echo "  --storage-account-name <name>   Storage account name"
            echo "  --app-insights-name <name>       Application Insights name"
            echo "  --deployment-method <method>     Deployment method: remote or local"
            echo ""
            echo "Environment variables:"
            echo "  APPLICATION_NAME          Application name for tagging"
            echo "  BUSINESS_OWNER           Business owner for tagging"
            echo "  COST_CENTRE              Cost centre for tagging"
            echo "  ENVIRONMENT               Environment for tagging"
            echo "  PROJECT                  Project name for tagging"
            echo "  TECHNICAL_OWNER          Technical owner for tagging"
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

# Clean up temporary files
rm -f ./src/azure-deployment.zip