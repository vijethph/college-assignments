#!/bin/bash

set -e

echo "Cleaning up Kubernetes deployment..."
echo ""

echo "Deleting services..."
kubectl delete -f k8s/api-gateway/ --ignore-not-found=true
kubectl delete -f k8s/booking-service/ --ignore-not-found=true
kubectl delete -f k8s/user-service/ --ignore-not-found=true
kubectl delete -f k8s/hotel-service/ --ignore-not-found=true
kubectl delete -f k8s/pvc.yaml --ignore-not-found=true
kubectl delete -f k8s/namespace.yaml --ignore-not-found=true

