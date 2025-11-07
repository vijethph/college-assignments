#!/bin/bash

set -e

echo "Deploying backend-service..."
kubectl apply -f k8s/backend-deployment.yaml

echo "Deploying client-service..."
kubectl apply -f k8s/client-deployment.yaml

echo "Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=60s deployment/backend-service
kubectl wait --for=condition=available --timeout=60s deployment/client-service

echo "Deployment complete!"
echo ""
echo "Service status:"
kubectl get deployments
kubectl get services
kubectl get pods
