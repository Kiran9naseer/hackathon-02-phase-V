#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Todo App - Docker Setup${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}Error: Docker is not running${NC}"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

echo -e "${GREEN}✓ Docker is installed and running${NC}"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found${NC}"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo -e "${YELLOW}Please edit .env file with your actual values before continuing${NC}"
    echo "Press Enter when ready to continue..."
    read
fi

echo -e "${GREEN}Building and starting containers...${NC}"
echo ""

# Build and start containers
docker-compose up --build -d

# Wait for services to be healthy
echo ""
echo -e "${YELLOW}Waiting for services to start...${NC}"
sleep 5

# Check if containers are running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ Application is running!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "Frontend: ${GREEN}http://localhost:3000${NC}"
    echo -e "Backend API: ${GREEN}http://localhost:8000${NC}"
    echo -e "API Docs: ${GREEN}http://localhost:8000/docs${NC}"
    echo ""
    echo -e "To view logs: ${YELLOW}docker-compose logs -f${NC}"
    echo -e "To stop: ${YELLOW}docker-compose down${NC}"
    echo ""
else
    echo -e "${RED}Error: Containers failed to start${NC}"
    echo "Check logs with: docker-compose logs"
    exit 1
fi
