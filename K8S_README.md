# Kubernetes Deployment (Minikube & Helm)

This guide shows how to deploy the Todo application on Minikube using Helm.

## Prerequisites
- Docker Desktop
- Minikube
- Kubectl
- Helm

## 🚀 Easy Deployment

Simply run the provided script in your WSL terminal:

```bash
chmod +x deploy-k8s.sh
./deploy-k8s.sh
```

This script will:
1. Start Minikube.
2. Build Docker images inside Minikube.
3. Deploy the Helm Chart.
4. Show you the access URLs.

## 🛠️ Manual Deployment

1. **Start Minikube**:
   ```bash
   minikube start
   ```

2. **Configure Docker Env**:
   ```bash
   eval $(minikube docker-env)
   ```

3. **Build Images**:
   ```bash
   docker build -t todo-backend:latest ./backend
   docker build -t todo-frontend:latest ./frontend
   ```

4. **Install Helm Chart**:
   ```bash
   helm install todo-app ./k8s/charts/todo-app
   ```

5. **Access Application**:
   ```bash
   minikube service todo-frontend --url
   ```

## 🧹 Cleanup

Run:
```bash
./cleanup-k8s.sh
```
