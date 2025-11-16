#!/bin/bash

set -e

echo "Starting Kubernetes Deployment..."
echo ""

docker build -t hotel-service:latest -f services/hotel_service/Dockerfile .
docker build -t user-service:latest -f services/user_service/Dockerfile .
docker build -t booking-service:latest -f services/booking_service/Dockerfile .
docker build -t api-gateway:latest -f services/api_gateway/Dockerfile .

echo "Docker images built successfully"
echo ""

echo "Creating namespace..."
kubectl apply -f k8s/namespace.yaml

echo "Creating PersistentVolumeClaims..."
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/message-broker/pvc.yaml

echo ""
echo "Deploying Message Broker..."
kubectl apply -f k8s/message-broker/

echo ""
echo "Waiting for Message Broker to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/message-broker -n hotel-booking

echo ""
echo "Deploying services..."
kubectl apply -f k8s/hotel-service/
kubectl apply -f k8s/user-service/
kubectl apply -f k8s/booking-service/
kubectl apply -f k8s/api-gateway/

echo ""
echo "Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/hotel-service -n hotel-booking
kubectl wait --for=condition=available --timeout=300s deployment/user-service -n hotel-booking
kubectl wait --for=condition=available --timeout=300s deployment/booking-service -n hotel-booking
kubectl wait --for=condition=available --timeout=300s deployment/api-gateway -n hotel-booking

echo ""
echo "All deployments are ready"
echo ""

echo "Deployment Status:"
kubectl get all -n hotel-booking

echo "Deployment complete"
