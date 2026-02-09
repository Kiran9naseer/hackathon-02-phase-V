---
name: agentic-containerization-skill
description: Designs, builds, and manages containerized environments for Todo Web App services using Docker, Docker Compose, and AI-assisted optimization
---

# Agentic Containerization Skill

## Instructions

### When to Use
- Containerizing backend (FastAPI) and frontend (Next.js) services
- Managing multi-container environments with Docker Compose
- Optimizing images for size, speed, and security
- Handling environment variables and build-time secrets
- Managing local dev, test, and production containers
- Integrating logging and monitoring hooks per service
- Automating container build and deployment pipelines

### What This Skill Does
Creates complete containerization setup including:
1. Dockerfile creation for each service with multi-stage builds
2. Docker Compose configuration for multi-service orchestration
3. Networking, volumes, and service dependencies management
4. Environment configuration handling (env files, ARGs, secrets)
5. Logging integration per container/service
6. Monitoring hooks for resource usage
7. AI-assisted optimization of image layers and caching
8. Cleanup strategies for unused containers and images
9. Documentation for reproducible local and production environments
10. Compliance with Phase-4A specifications

### How Claude Should Behave
- Create optimized, reusable Dockerfiles and Compose setups
- Ensure separation of dev, test, and production environments
- Suggest layer caching strategies and redundant layer removal
- Include logging and monitoring setup for each service
- Ensure containerized services match specification requirements
- Provide clear documentation for container lifecycle and rebuilds
- NO application code; focus only on containerization
- Ensure services can be easily deployed and tested locally

### Example Usage

User: "Containerize backend and frontend for Phase-4A using Docker and Compose"
Claude: Invokes agentic-containerization agent → Creates:

Backend Dockerfile with multi-stage build

Frontend Dockerfile with optimized caching

docker-compose.yml with all services, volumes, and networks

Logging configuration for each container

Instructions for local dev and production deployment


## Examples

### Example 1: Multi-Service Setup
**Scenario:** Phase-4A local development with backend, frontend, and DB.

**Input:**


Containerize:

FastAPI backend

Next.js frontend

PostgreSQL database

Redis caching service


**Process:**
1. Create individual Dockerfiles
2. Configure Docker Compose for networking and dependencies
3. Set environment variables and secrets
4. Optimize builds with caching
5. Document container startup, shutdown, and logs

**Output:**
- Multi-container setup ready for local dev and testing

### Example 2: Image Optimization
**Scenario:** Reduce image size and rebuild time

**Input:**


Analyze backend Dockerfile for optimization


**Process:**
1. Remove redundant layers
2. Merge RUN commands where appropriate
3. Suggest base image alternatives
4. Implement caching for dependencies

**Output:** Optimized Docker images and updated Compose config

### Example 3: Deployment Prep
**Scenario:** Prepare containers for production deployment

**Input:**


Prepare all services for production deployment using Docker


**Process:**
1. Switch to production environment variables
2. Build production-ready images
3. Document instructions for deployment

**Output:** Production-ready container images with full documentation

## Acceptance Criteria

- ✅ Dockerfiles created for all services
- ✅ Multi-stage builds for image optimization
- ✅ Docker Compose file orchestrates all services
- ✅ Environment variables and secrets managed correctly
- ✅ Logging and monitoring hooks integrated
- ✅ Image layers optimized for size and rebuild speed
- ✅ Clear documentation for building, running, and cleaning containers
- ✅ Ready for Phase-4A deployment and testing
- ✅ Compliant with specification requirements
