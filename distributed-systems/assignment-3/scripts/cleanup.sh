#!/bin/bash

echo "Deleting deployments and services..."
kubectl delete -f k8s/client-deployment.yaml --ignore-not-found=true
kubectl delete -f k8s/backend-deployment.yaml --ignore-not-found=true

echo "Cleanup complete!"
