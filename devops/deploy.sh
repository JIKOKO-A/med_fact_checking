#!/bin/bash

# Medical Fact-Check Platform Deployment Script
# Supports local, Docker, cloud deployments

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🏥 Medical Fact-Check Platform - Deployment${NC}"
echo -e "${YELLOW}=========================================${NC}"

# Configuration
ENV=${1:-development}
ENVIRONMENT_FILE=".env.${ENV}"

# Check environment file
if [ ! -f "$ENVIRONMENT_FILE" ]; then
    echo -e "${RED}❌ Environment file not found: $ENVIRONMENT_FILE${NC}"
    exit 1
fi

source "$ENVIRONMENT_FILE"

# Function to deploy locally
deploy_local() {
    echo -e "${YELLOW}📦 Starting local development setup...${NC}"
    
    # Backend
    echo -e "${YELLOW}🔧 Setting up backend...${NC}"
    cd backend
    python -m venv venv || true
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    
    # Frontend
    echo -e "${YELLOW}🎨 Setting up frontend...${NC}"
    cd frontend
    npm install
    cd ..
    
    echo -e "${GREEN}✅ Local setup complete!${NC}"
    echo -e "${YELLOW}Starting services...${NC}"
    
    # Start backend
    cd backend
    python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    # Start frontend
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    echo -e "${GREEN}✅ Services started${NC}"
    echo -e "Backend:  http://localhost:8000 (PID: $BACKEND_PID)"
    echo -e "Frontend: http://localhost:3000 (PID: $FRONTEND_PID)"
}

# Function to deploy with Docker
deploy_docker() {
    echo -e "${YELLOW}🐳 Deploying with Docker...${NC}"
    
    # Create SSL certificates if not exist
    if [ ! -f "devops/ssl/cert.pem" ]; then
        echo -e "${YELLOW}🔐 Generating self-signed SSL certificates...${NC}"
        mkdir -p devops/ssl
        openssl req -x509 -newkey rsa:4096 -keyout devops/ssl/key.pem \
            -out devops/ssl/cert.pem -days 365 -nodes \
            -subj "/CN=localhost"
    fi
    
    echo -e "${YELLOW}🢇 Building Docker images...${NC}"
    docker-compose build
    
    echo -e "${YELLOW}🢇 Starting services...${NC}"
    docker-compose up -d
    
    echo -e "${GREEN}✅ Docker deployment complete!${NC}"
    echo -e "Services:"
    docker-compose ps
    
    echo -e "${YELLOW}Waiting for services to be ready...${NC}"
    sleep 10
    
    # Check health
    echo -e "${YELLOW}🔍 Checking health...${NC}"
    curl -s http://localhost:8000/api/v1/health/ | jq . || echo "Backend health check pending..."
}

# Function to deploy to AWS ECS
deploy_aws_ecs() {
    echo -e "${YELLOW}☁️  Deploying to AWS ECS...${NC}"
    
    AWS_REGION=${AWS_REGION:-us-east-1}
    ECR_REGISTRY=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
    
    echo -e "${YELLOW}Authenticating with ECR...${NC}"
    aws ecr get-login-password --region $AWS_REGION | docker login \
        --username AWS --password-stdin $ECR_REGISTRY
    
    echo -e "${YELLOW}Building and pushing images...${NC}"
    
    # Backend
    docker build -f devops/Dockerfile.backend -t $ECR_REGISTRY/medical-factcheck-backend:latest .
    docker push $ECR_REGISTRY/medical-factcheck-backend:latest
    
    # Frontend
    docker build -f devops/Dockerfile.frontend -t $ECR_REGISTRY/medical-factcheck-frontend:latest .
    docker push $ECR_REGISTRY/medical-factcheck-frontend:latest
    
    echo -e "${GREEN}✅ AWS ECS deployment images pushed${NC}"
}

# Function to deploy to Railway
deploy_railway() {
    echo -e "${YELLOW}🚂 Deploying to Railway...${NC}"
    
    if ! command -v railway &> /dev/null; then
        echo -e "${YELLOW}Installing Railway CLI...${NC}"
        npm install -g @railway/cli
    fi
    
    railway login
    railway init
    railway up
    
    echo -e "${GREEN}✅ Railway deployment started${NC}"
}

# Function to deploy to Vercel (Frontend only)
deploy_vercel() {
    echo -e "${YELLOW}⚡ Deploying frontend to Vercel...${NC}"
    
    if ! command -v vercel &> /dev/null; then
        echo -e "${YELLOW}Installing Vercel CLI...${NC}"
        npm install -g vercel
    fi
    
    cd frontend
    vercel deploy --prod
    cd ..
    
    echo -e "${GREEN}✅ Vercel deployment complete${NC}"
}

# Function to deploy to Render
deploy_render() {
    echo -e "${YELLOW}🎨 Deploying to Render...${NC}"
    
    echo "Please configure Render deployment in render.yaml"
    echo "See documentation for details"
}

# Main deployment logic
case $ENV in
    local|development)
        deploy_local
        ;;
    docker)
        deploy_docker
        ;;
    aws)
        deploy_aws_ecs
        ;;
    railway)
        deploy_railway
        ;;
    vercel)
        deploy_vercel
        ;;
    render)
        deploy_render
        ;;
    *)
        echo -e "${RED}❌ Unknown environment: $ENV${NC}"
        echo "Usage: $0 [local|docker|aws|railway|vercel|render]"
        exit 1
        ;;
esac

echo -e "${GREEN}✅ Deployment complete!${NC}"
