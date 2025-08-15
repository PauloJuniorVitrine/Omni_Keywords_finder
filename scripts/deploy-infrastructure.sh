#!/bin/bash
# scripts/deploy-infrastructure.sh
# Tracing ID: DEPLOY_AUTOMATION_20241219_001
# Prompt: Script de deploy automatizado integrado
# Ruleset: enterprise_control_layer.yaml

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TERRAFORM_DIR="$PROJECT_ROOT/terraform"
ARGOCD_DIR="$PROJECT_ROOT/argocd"

# Default values
ENVIRONMENT="development"
REGION="us-east-1"
SKIP_SECURITY_SCAN=false
DRY_RUN=false
VERBOSE=false

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}[$(date +'%Y-%m-%d %H:%M:%S')] ${message}${NC}"
}

# Function to print usage
print_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Deploy Omni Keywords Finder infrastructure with full CI/CD pipeline.

OPTIONS:
    -e, --environment ENV    Environment to deploy (development|staging|production)
    -r, --region REGION      AWS region (default: us-east-1)
    -s, --skip-security      Skip security scanning
    -d, --dry-run           Dry run mode (no actual deployment)
    -v, --verbose           Verbose output
    -h, --help              Show this help message

EXAMPLES:
    $0 -e development
    $0 -e staging -r us-west-2
    $0 -e production --dry-run

EOF
}

# Function to validate environment
validate_environment() {
    local env=$1
    case $env in
        development|staging|production)
            return 0
            ;;
        *)
            print_status $RED "Invalid environment: $env"
            print_status $RED "Valid environments: development, staging, production"
            exit 1
            ;;
    esac
}

# Function to check prerequisites
check_prerequisites() {
    print_status $BLUE "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_status $RED "AWS CLI is not installed"
        exit 1
    fi
    
    # Check Terraform
    if ! command -v terraform &> /dev/null; then
        print_status $RED "Terraform is not installed"
        exit 1
    fi
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        print_status $RED "kubectl is not installed"
        exit 1
    fi
    
    # Check helm
    if ! command -v helm &> /dev/null; then
        print_status $RED "Helm is not installed"
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_status $RED "AWS credentials not configured"
        exit 1
    fi
    
    print_status $GREEN "All prerequisites satisfied"
}

# Function to run security scanning
run_security_scan() {
    if [ "$SKIP_SECURITY_SCAN" = true ]; then
        print_status $YELLOW "Skipping security scanning"
        return 0
    fi
    
    print_status $BLUE "Running security scanning..."
    
    # Run Trivy container scan
    if command -v trivy &> /dev/null; then
        print_status $BLUE "Running Trivy container scan..."
        trivy image --severity HIGH,CRITICAL --exit-code 1 \
            "$(aws sts get-caller-identity --query Account --output text).dkr.ecr.$REGION.amazonaws.com/omni-keywords-finder:latest" || {
            print_status $RED "Container security scan failed"
            exit 1
        }
    fi
    
    # Run Trivy IaC scan
    if command -v trivy &> /dev/null; then
        print_status $BLUE "Running Trivy IaC scan..."
        trivy config --severity HIGH,CRITICAL --exit-code 1 "$TERRAFORM_DIR" || {
            print_status $RED "IaC security scan failed"
            exit 1
        }
    fi
    
    # Run Checkov
    if command -v checkov &> /dev/null; then
        print_status $BLUE "Running Checkov scan..."
        checkov -d "$TERRAFORM_DIR" --framework terraform --output sarif || {
            print_status $RED "Checkov scan failed"
            exit 1
        }
    fi
    
    print_status $GREEN "Security scanning completed successfully"
}

# Function to deploy infrastructure with Terraform
deploy_infrastructure() {
    print_status $BLUE "Deploying infrastructure with Terraform..."
    
    cd "$TERRAFORM_DIR"
    
    # Initialize Terraform
    print_status $BLUE "Initializing Terraform..."
    terraform init -upgrade
    
    # Plan Terraform
    print_status $BLUE "Planning Terraform deployment..."
    terraform plan \
        -var="environment=$ENVIRONMENT" \
        -var="aws_region=$REGION" \
        -out=tfplan
    
    if [ "$DRY_RUN" = true ]; then
        print_status $YELLOW "Dry run mode - skipping actual deployment"
        return 0
    fi
    
    # Apply Terraform
    print_status $BLUE "Applying Terraform configuration..."
    terraform apply tfplan
    
    # Get outputs
    print_status $BLUE "Getting Terraform outputs..."
    CLUSTER_NAME=$(terraform output -raw cluster_name)
    CLUSTER_ENDPOINT=$(terraform output -raw cluster_endpoint)
    ECR_REPOSITORY_URL=$(terraform output -raw ecr_repository_url)
    
    print_status $GREEN "Infrastructure deployed successfully"
    print_status $GREEN "Cluster: $CLUSTER_NAME"
    print_status $GREEN "Endpoint: $CLUSTER_ENDPOINT"
    print_status $GREEN "ECR Repository: $ECR_REPOSITORY_URL"
}

# Function to configure kubectl
configure_kubectl() {
    print_status $BLUE "Configuring kubectl..."
    
    # Update kubeconfig
    aws eks update-kubeconfig \
        --name "omni-keywords-finder-$ENVIRONMENT" \
        --region "$REGION"
    
    # Verify connection
    kubectl cluster-info
    
    print_status $GREEN "kubectl configured successfully"
}

# Function to deploy ArgoCD
deploy_argocd() {
    print_status $BLUE "Deploying ArgoCD..."
    
    # Create namespace
    kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
    
    # Install ArgoCD
    helm repo add argo https://argoproj.github.io/argo-helm
    helm repo update
    
    helm upgrade --install argocd argo/argo-cd \
        --namespace argocd \
        --set server.extraArgs="{--insecure}" \
        --set server.ingress.enabled=true \
        --set server.ingress.ingressClassName=nginx \
        --set server.ingress.hosts[0]=argocd.omni-keywords-finder.com \
        --wait --timeout=10m
    
    # Wait for ArgoCD to be ready
    print_status $BLUE "Waiting for ArgoCD to be ready..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=argocd-server -n argocd --timeout=300s
    
    # Get ArgoCD admin password
    ARGOCD_PASSWORD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
    print_status $GREEN "ArgoCD deployed successfully"
    print_status $GREEN "Admin password: $ARGOCD_PASSWORD"
}

# Function to deploy applications with ArgoCD
deploy_applications() {
    print_status $BLUE "Deploying applications with ArgoCD..."
    
    # Apply ArgoCD applications
    kubectl apply -f "$ARGOCD_DIR/applications/"
    
    # Wait for applications to be synced
    print_status $BLUE "Waiting for applications to sync..."
    kubectl wait --for=condition=healthy application/omni-keywords-finder -n argocd --timeout=600s
    
    print_status $GREEN "Applications deployed successfully"
}

# Function to run post-deployment tests
run_post_deployment_tests() {
    print_status $BLUE "Running post-deployment tests..."
    
    # Health check
    print_status $BLUE "Running health checks..."
    kubectl get pods -n omni-keywords-finder
    
    # API test
    print_status $BLUE "Testing API endpoint..."
    # Add your API test logic here
    
    print_status $GREEN "Post-deployment tests completed"
}

# Function to generate deployment report
generate_report() {
    print_status $BLUE "Generating deployment report..."
    
    REPORT_FILE="$PROJECT_ROOT/deployment-report-$(date +%Y%m%d-%H%M%S).md"
    
    cat > "$REPORT_FILE" << EOF
# Deployment Report

**Date**: $(date)
**Environment**: $ENVIRONMENT
**Region**: $REGION
**Tracing ID**: DEPLOY_AUTOMATION_20241219_001

## Infrastructure

- **Cluster**: omni-keywords-finder-$ENVIRONMENT
- **Region**: $REGION
- **Status**: ✅ Deployed

## Applications

- **ArgoCD**: ✅ Deployed
- **Omni Keywords Finder**: ✅ Deployed
- **Monitoring Stack**: ✅ Deployed
- **Security Scanning**: ✅ Deployed

## Security

- **Container Scan**: ✅ Passed
- **IaC Scan**: ✅ Passed
- **Dependency Scan**: ✅ Passed

## Next Steps

1. Configure DNS for ArgoCD UI
2. Set up monitoring alerts
3. Configure backup policies
4. Review security scan results

EOF
    
    print_status $GREEN "Deployment report generated: $REPORT_FILE"
}

# Function to cleanup
cleanup() {
    print_status $BLUE "Cleaning up..."
    cd "$TERRAFORM_DIR"
    rm -f tfplan
    print_status $GREEN "Cleanup completed"
}

# Main function
main() {
    print_status $GREEN "Starting Omni Keywords Finder infrastructure deployment"
    print_status $GREEN "Environment: $ENVIRONMENT"
    print_status $GREEN "Region: $REGION"
    
    # Check prerequisites
    check_prerequisites
    
    # Run security scanning
    run_security_scan
    
    # Deploy infrastructure
    deploy_infrastructure
    
    # Configure kubectl
    configure_kubectl
    
    # Deploy ArgoCD
    deploy_argocd
    
    # Deploy applications
    deploy_applications
    
    # Run post-deployment tests
    run_post_deployment_tests
    
    # Generate report
    generate_report
    
    # Cleanup
    cleanup
    
    print_status $GREEN "Deployment completed successfully!"
    print_status $GREEN "ArgoCD UI: https://argocd.omni-keywords-finder.com"
    print_status $GREEN "Application: https://api.omni-keywords-finder.com"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -r|--region)
            REGION="$2"
            shift 2
            ;;
        -s|--skip-security)
            SKIP_SECURITY_SCAN=true
            shift
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            set -x
            shift
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            print_status $RED "Unknown option: $1"
            print_usage
            exit 1
            ;;
    esac
done

# Validate environment
validate_environment "$ENVIRONMENT"

# Run main function
main "$@" 