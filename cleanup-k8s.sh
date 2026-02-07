#!/bin/bash
echo "🧹 Cleaning up Kubernetes deployment..."
helm uninstall todo-app
echo "🛑 Stopping Minikube..."
minikube stop
echo "✅ Done"
