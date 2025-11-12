#!/bin/bash

NAMESPACE="hotel-booking"

echo "Kubernetes Cluster Status"
echo "-------------------------"
echo ""

echo "Namespace:"
kubectl get namespace $NAMESPACE 2>/dev/null || echo "Namespace not found"
echo ""

echo "Pods:"
kubectl get pods -n $NAMESPACE -o wide
echo ""

echo "Services:"
kubectl get services -n $NAMESPACE
echo ""

echo "Deployments:"
kubectl get deployments -n $NAMESPACE
echo ""

echo "PersistentVolumeClaims:"
kubectl get pvc -n $NAMESPACE
echo ""

echo "ConfigMaps:"
kubectl get configmaps -n $NAMESPACE
echo ""

echo "API Gateway Access:"
MINIKUBE_IP=$(minikube ip 2>/dev/null)
if [ -n "$MINIKUBE_IP" ]; then
    echo "URL: http://${MINIKUBE_IP}:30000"
    echo "Health: http://${MINIKUBE_IP}:30000/health"
else
    echo "Minikube not running or accessible"
fi
echo ""

echo "Resource Usage:"
kubectl top pods -n $NAMESPACE 2>/dev/null || echo "Metrics server not available"
echo ""

echo "Recent Events:"
kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' | tail -10
