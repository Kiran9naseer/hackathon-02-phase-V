#!/bin/bash
# Kubernetes Deployment Script for Minikube

echo "🚀 Starting Minikube..."
minikube start

echo "🐳 configuring Docker environment..."
eval $(minikube docker-env)

echo "🏗️ Building Backend Image..."
docker build -t todo-backend:latest ./backend

echo "🏗️ Building Frontend Image..."
docker build -t todo-frontend:latest ./frontend

echo "📦 Deploying Helm Chart..."
# Check if already installed
if helm list | grep -q todo-app; then
    helm upgrade todo-app ./k8s/charts/todo-app
else
    helm install todo-app ./k8s/charts/todo-app
fi

echo "✅ App deployed!"
echo "📡 Access Frontend at:"
minikube service todo-frontend --url

echo "📡 Access Backend at:"
minikube service todo-backend --url
