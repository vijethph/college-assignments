#!/bin/bash

MODE="${1:-local}"

stop_local_services() {
    echo "Stopping local services..."

    for port in 8001 8002 8003; do
        pid=$(lsof -ti:$port 2>/dev/null || true)
        if [ -n "$pid" ]; then
            kill "$pid" 2>/dev/null || true
        fi
    done

    echo "Services stopped"
}

stop_docker_services() {
    if [ ! -f "docker-compose.yml" ]; then
        echo "ERROR: docker-compose.yml not found"
        exit 1
    fi

    echo "Stopping Docker services..."
    docker compose down
    docker rmi api-gateway:latest user-service:latest hotel-service:latest booking-service:latest 2>/dev/null || true
    echo "Services stopped"
}

stop_kubernetes_services() {
    NAMESPACE="${2:-hotel-booking}"

    if [ ! -d "k8s" ]; then
        echo "ERROR: k8s/ directory not found"
        exit 1
    fi

    echo "Stopping Kubernetes services..."
    kubectl delete -f k8s/ -n "$NAMESPACE" --ignore-not-found=true
    docker rmi api-gateway:latest user-service:latest hotel-service:latest booking-service:latest 2>/dev/null || true

    echo "Services stopped"
}

case "$MODE" in
    local)
        stop_local_services
        ;;
    docker)
        stop_docker_services
        ;;
    kubernetes|k8s)
        stop_kubernetes_services "$@"
        ;;
    all)
        echo "Stopping all services..."
        echo ""
        stop_local_services
        echo ""
        if [ -f "docker-compose.yml" ]; then
            stop_docker_services
        fi
        ;;
    *)
        echo "Usage: $0 [local|docker|kubernetes|all] [namespace]"
        exit 1
        ;;
esac
