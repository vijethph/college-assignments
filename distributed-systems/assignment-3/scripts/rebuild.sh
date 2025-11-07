#!/bin/bash

set -e

echo "Rebuilding and redeploying services..."

echo "Step 1: Setting up minikube environment..."
eval $(minikube docker-env)

echo "Step 2: Building backend-service image..."
docker build --no-cache -t backend-service:latest -f backend_service/Dockerfile .

echo "Step 3: Building client-service image..."
docker build --no-cache -t client-service:latest -f client_service/Dockerfile .

echo "Step 4: Restarting deployments..."
kubectl rollout restart deployment/backend-service
kubectl rollout restart deployment/client-service

echo "Step 5: Waiting for deployments to be ready..."
kubectl rollout status deployment/backend-service
kubectl rollout status deployment/client-service

echo ""
echo "=== Rebuild and redeploy complete! ==="
kubectl get pods
