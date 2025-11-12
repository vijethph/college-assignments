#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MODE="${1:-local}"

PIDS=()

cleanup() {
    echo "Stopping services..."
    for pid in "${PIDS[@]}"; do
        kill "$pid" 2>/dev/null || true
    done
    wait 2>/dev/null || true
    echo "All services stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

start_local_services() {
    echo "Starting services..."

    cd "$PROJECT_ROOT/services/hotel_service"
    SERVICE_PORT=8001 python main.py > /tmp/hotel-service.log 2>&1 &
    PIDS+=($!)

    cd "$PROJECT_ROOT/services/user_service"
    SERVICE_PORT=8002 python main.py > /tmp/user-service.log 2>&1 &
    PIDS+=($!)

    cd "$PROJECT_ROOT/services/booking_service"
    SERVICE_PORT=8003 python main.py > /tmp/booking-service.log 2>&1 &
    PIDS+=($!)

    sleep 3

    echo "Services started"

    wait
}

start_docker_services() {
    cd "$PROJECT_ROOT"

    if [ ! -f "docker-compose.yml" ]; then
        echo "ERROR: docker-compose.yml not found"
        exit 1
    fi

    echo "Starting Docker services..."
    docker-compose up --build
}

start_kubernetes_services() {
    NAMESPACE="${2:-hotel-booking}"
    cd "$PROJECT_ROOT"

    if [ ! -d "k8s" ]; then
        echo "ERROR: k8s/ directory not found"
        exit 1
    fi

    echo "Deploying to Kubernetes (namespace: $NAMESPACE)"
    kubectl create namespace "$NAMESPACE" 2>/dev/null || true
    kubectl apply -f k8s/ -n "$NAMESPACE"

    echo ""
    echo "Services deployed"
}

case "$MODE" in
    local)
        start_local_services
        ;;
    docker)
        start_docker_services
        ;;
    kubernetes|k8s)
        start_kubernetes_services "$@"
        ;;
    *)
        echo "ERROR: Unknown mode '$MODE'"
        echo "Usage: $0 [local|docker|kubernetes] [namespace]"
        exit 1
        ;;
esac
        ;;
    *)
        echo "Usage: $0 [local|docker|kubernetes] [namespace]"
        exit 1
        ;;
esac
    kubectl create namespace "$NAMESPACE" 2>/dev/null || true

    echo -e "${YELLOW}Applying Kubernetes manifests...${NC}"
    kubectl apply -f k8s/ -n "$NAMESPACE"

    echo ""
    echo -e "${GREEN}Kubernetes resources applied!${NC}"

}

case "$MODE" in
    local)
        start_local_services
        ;;

    docker)
        start_docker_services
        ;;

    kubernetes|k8s)
        start_kubernetes_services "$@"
        ;;

    *)
        echo -e "${RED}Error: Unknown mode '$MODE'${NC}"
        echo "Usage: $0 [local|docker|kubernetes] [namespace]"
        exit 1
        ;;
esac
