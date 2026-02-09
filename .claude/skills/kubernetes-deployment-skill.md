---
name: kubernetes-deployment-skill
description: Deploys and manages Todo Web App services on Kubernetes using Helm charts, manifests, and local clusters with monitoring and scaling
---

# Kubernetes Deployment Skill

## Instructions

### When to Use
- Deploying backend, frontend, and auxiliary services on Kubernetes
- Creating Helm charts for multi-environment deployment
- Defining resource limits, requests, and autoscaling
- Configuring ConfigMaps, Secrets, Services, Ingress, and PersistentVolumes
- Testing on Minikube or local Kubernetes clusters
- Monitoring pod health, readiness, and liveness
- Performing AI-assisted deployment optimizations

### What This Skill Does
Creates complete Kubernetes deployment setup including:
1. Helm chart templates for backend, frontend, and auxiliary services
2. Kubernetes manifests for Deployments, Services, StatefulSets, ConfigMaps, Secrets, and Ingress
3. Resource management (CPU/memory) and autoscaling configuration
4. Deployment strategies and rollout management
5. Monitoring and logging hooks per pod/service
6. Local cluster validation (Minikube) and troubleshooting
7. AI-suggested optimizations for YAML and resource allocation
8. Documentation for deployment and rollback procedures
9. Compliance with Phase-4B specifications
10. Clear separation of dev/test/prod configurations

### How Claude Should Behave
- Create Helm charts with templating and reusable components
- Use ConfigMaps, Secrets, and environment-specific values correctly
- Configure resource requests, limits, and HPA rules
- Integrate readiness and liveness probes for pods
- Suggest improvements for YAML, deployment efficiency, and anti-patterns
- Provide deployment instructions and rollback procedures
- NO application code; focus only on deployment infrastructure
- Ensure production-ready, reproducible cluster environments

### Example Usage

User: "Deploy backend, frontend, and database to local Kubernetes cluster using Helm"
Claude: Invokes kubernetes-deployment agent → Creates:

Helm charts for all services

Manifests for Deployments, Services, ConfigMaps, and Secrets

Resource requests, limits, and autoscaling

Readiness/liveness probes and monitoring hooks

Deployment instructions for dev/test clusters


## Examples

### Example 1: Helm Chart Deployment
**Scenario:** Deploy services to local Minikube cluster

**Input:**
Create Helm charts for:

FastAPI backend

Next.js frontend

PostgreSQL database


**Process:**
1. Template Helm charts with values.yaml for each environment
2. Define Deployments, Services, ConfigMaps, Secrets
3. Configure Ingress and PersistentVolumes
4. Validate pods on Minikube

**Output:** Working deployment on local Kubernetes cluster

### Example 2: Autoscaling and Resources
**Scenario:** Ensure efficient resource allocation

**Input:**
Optimize CPU and memory requests for all services


**Process:**
1. Define resource requests and limits
2. Configure HPA (Horizontal Pod Autoscaler)
3. Suggest improvements based on AI analysis
4. Update Helm templates

**Output:** Efficiently resourced, autoscaling deployment

### Example 3: Rollback Preparation
**Scenario:** Deploy updates safely with rollback options

**Input:**
Prepare deployment strategy with rollback


**Process:**
1. Define rollout strategy in Helm chart
2. Document rollback commands
3. Test deployment and rollback locally

**Output:** Safe and reproducible deployment with rollback capability

## Acceptance Criteria

- ✅ Helm charts created for all services
- ✅ Kubernetes manifests complete and accurate
- ✅ Resource requests, limits, and HPA configured
- ✅ ConfigMaps and Secrets properly used
- ✅ Readiness and liveness probes configured
- ✅ Monitoring and logging hooks integrated
- ✅ Local cluster deployment validated
- ✅ Clear deployment and rollback documentation
- ✅ Production-ready cluster deployment
- ✅ Compliant with Phase-4B specification