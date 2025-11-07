#!/bin/bash

set -e

echo "Setting up minikube environment..."
eval $(minikube docker-env)

echo "Building backend-service image..."
docker build -t backend-service:latest -f backend_service/Dockerfile .

echo "Building client-service image..."
docker build -t client-service:latest -f client_service/Dockerfile .

echo "Images built successfully!"
docker images | grep -E "backend-service|client-service"
