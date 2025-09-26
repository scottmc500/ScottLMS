#!/bin/bash
# Script to get LoadBalancer IPs with fallback to 0.0.0.0
# This ensures Terraform can always create infrastructure, even on first run

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Getting LoadBalancer IPs for MongoDB access list...${NC}"

# Function to get LoadBalancer IP
get_loadbalancer_ip() {
    local service_name=$1
    local namespace=$2
    
    echo -e "${YELLOW}Checking for $service_name LoadBalancer IP...${NC}"
    
    # Try to get the IP
    local ip=$(kubectl get service "$service_name" -n "$namespace" -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
    
    if [ -n "$ip" ] && [ "$ip" != "null" ]; then
        echo -e "${GREEN}✓ Found $service_name IP: $ip${NC}"
        echo "${ip}/32"
    else
        echo -e "${YELLOW}⚠ $service_name IP not available yet, using 0.0.0.0/0 for open access${NC}"
        echo "0.0.0.0/0"
    fi
}

# Get API LoadBalancer CIDR
API_CIDR=$(get_loadbalancer_ip "scottlms-api-loadbalancer" "scottlms")

# Get Frontend LoadBalancer CIDR  
FRONTEND_CIDR=$(get_loadbalancer_ip "scottlms-frontend-loadbalancer" "scottlms")

# Create terraform.tfvars with the CIDR blocks
echo -e "${GREEN}Creating terraform.tfvars with LoadBalancer CIDR blocks...${NC}"

cat > terraform/terraform.tfvars << EOF
# LoadBalancer CIDR blocks for MongoDB access list
# Generated automatically by get-loadbalancer-ips.sh

# API LoadBalancer CIDR
api_cidr_block = "$API_CIDR"

# Frontend LoadBalancer CIDR  
frontend_cidr_block = "$FRONTEND_CIDR"

# MongoDB Atlas credentials (from GitHub Secrets)
atlas_public_key = "$ATLAS_PUBLIC_KEY"
atlas_private_key = "$ATLAS_PRIVATE_KEY"
atlas_org_id = "$ATLAS_ORG_ID"
atlas_project_id = "$ATLAS_PROJECT_ID"

# Linode credentials (from GitHub Secrets)
linode_token = "$LINODE_TOKEN"
linode_cluster_id = "$LINODE_CLUSTER_ID"

# Docker Hub credentials (from GitHub Secrets)
docker_hub_username = "$DOCKER_HUB_USERNAME"
docker_hub_password = "$DOCKER_HUB_PASSWORD"

# Application configuration
app_image_tag = "$APP_IMAGE_TAG"
EOF

echo -e "${GREEN}✓ terraform.tfvars created with LoadBalancer CIDR blocks${NC}"
echo -e "${GREEN}API CIDR: $API_CIDR${NC}"
echo -e "${GREEN}Frontend CIDR: $FRONTEND_CIDR${NC}"

# If we got real IPs, show security status
if [ "$API_CIDR" != "0.0.0.0/0" ] || [ "$FRONTEND_CIDR" != "0.0.0.0/0" ]; then
    echo -e "${GREEN}✓ Using actual LoadBalancer CIDR blocks - MongoDB access will be restricted${NC}"
else
    echo -e "${YELLOW}⚠ Using 0.0.0.0/0 - MongoDB access is open (not secure for production)${NC}"
    echo -e "${YELLOW}  Run this script again after deploying services to get real CIDR blocks${NC}"
fi
