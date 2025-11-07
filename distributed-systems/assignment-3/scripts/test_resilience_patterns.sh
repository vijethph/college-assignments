#!/bin/bash

set -e

echo "Setting up port-forwards..."
kubectl port-forward svc/backend-service 8000:8000 > /dev/null 2>&1 &
BACKEND_PID=$!
kubectl port-forward svc/client-service 9090:9090 > /dev/null 2>&1 &
CLIENT_PID=$!

cleanup() {
    echo "Cleaning up port-forwards..."
    kill $BACKEND_PID 2>/dev/null
    kill $CLIENT_PID 2>/dev/null
}
trap cleanup EXIT

sleep 3

BACKEND_URL="http://localhost:8000"
CLIENT_URL="http://localhost:9090"


echo "Resilience Patterns Test - Part B"
echo ""

echo "--- Scenario 1: Normal Operation ---"
echo "Both patterns inactive, backend working normally"
echo ""
curl -s -X POST "${BACKEND_URL}/config/failure" \
  -H "Content-Type: application/json" \
  -d '{"failure_rate": 0.0, "status_code": 500}' > /dev/null
curl -s -X POST "${BACKEND_URL}/config/latency" \
  -H "Content-Type: application/json" \
  -d '{"delay_ms": 0, "delay_rate": 0.0}' > /dev/null

echo "Making 5 requests:"
for i in {1..5}; do
    RESPONSE=$(curl -s --max-time 10 "${CLIENT_URL}/fetch-data")
    STATUS=$(echo "$RESPONSE" | jq -r '.status')
    echo "  Request $i: $STATUS"
done
echo ""

echo "--- Scenario 2: Transient Failures (Retry Pattern Active) ---"
echo "Backend has 50% transient failures (503) - retries should help"
echo ""
curl -s -X POST "${BACKEND_URL}/config/failure" \
  -H "Content-Type: application/json" \
  -d '{"failure_rate": 0.5, "status_code": 503}' > /dev/null

echo "Making 10 requests (watch for retries in logs):"
SUCCESS=0
for i in {1..10}; do
    RESPONSE=$(curl -s --max-time 30 "${CLIENT_URL}/fetch-data")
    STATUS=$(echo "$RESPONSE" | jq -r '.status')
    echo "  Request $i: $STATUS"
    [ "$STATUS" == "success" ] && SUCCESS=$((SUCCESS + 1))
done
echo "Success rate: $SUCCESS/10 (retry pattern should improve this)"
echo ""

echo "--- Scenario 3: Systemic Failure (Circuit Breaker Activates) ---"
echo "Backend has 100% failures - circuit breaker should open"
echo ""
curl -s -X POST "${BACKEND_URL}/config/failure" \
  -H "Content-Type: application/json" \
  -d '{"failure_rate": 1.0, "status_code": 500}' > /dev/null

echo "Making 8 requests to trigger circuit breaker:"
for i in {1..8}; do
    START=$(date +%s.%N)
    RESPONSE=$(curl -s --max-time 30 "${CLIENT_URL}/fetch-data")
    END=$(date +%s.%N)
    DURATION=$(echo "$END - $START" | bc 2>/dev/null || echo "0")
    STATUS=$(echo "$RESPONSE" | jq -r '.status')
    MESSAGE=$(echo "$RESPONSE" | jq -r '.message' | cut -c1-50)
    echo "  Request $i: $STATUS - $MESSAGE (${DURATION}s)"

    if [ $i -eq 6 ]; then
        CB_STATE=$(curl -s "${CLIENT_URL}/circuit-status" | jq -r '.state')
        echo "  >> Circuit Breaker State: $CB_STATE"
    fi

    sleep 1
done
echo ""

CB_STATE=$(curl -s "${CLIENT_URL}/circuit-status" | jq -r '.state')
echo "Circuit Breaker State: $CB_STATE (should be OPEN)"
echo ""

echo "--- Scenario 4: Fast-Fail While Circuit is Open ---"
echo "Requests should fail immediately without retries"
echo ""

echo "Making 3 fast-fail requests:"
for i in {1..3}; do
    START=$(date +%s.%N)
    RESPONSE=$(curl -s --max-time 10 "${CLIENT_URL}/fetch-data")
    END=$(date +%s.%N)
    DURATION=$(echo "$END - $START" | bc 2>/dev/null || echo "0")
    STATUS=$(echo "$RESPONSE" | jq -r '.status')
    echo "  Request $i: $STATUS (${DURATION}s - should be < 0.1s)"
done
echo ""

echo "--- Scenario 5: Service Recovery ---"
echo "Restoring backend to healthy state..."
curl -s -X POST "${BACKEND_URL}/config/failure" \
  -H "Content-Type: application/json" \
  -d '{"failure_rate": 0.0, "status_code": 500}' > /dev/null
echo ""

echo "Waiting 31 seconds for circuit breaker to attempt half-open..."
for i in {31..1}; do
    echo -ne "  Waiting... $i seconds   \r"
    sleep 1
done
echo ""
echo ""

echo "Making test request (should transition to HALF-OPEN then CLOSED):"
RESPONSE=$(curl -s --max-time 10 "${CLIENT_URL}/fetch-data")
STATUS=$(echo "$RESPONSE" | jq -r '.status')
echo "  Test request: $STATUS"
echo ""

CB_STATE=$(curl -s "${CLIENT_URL}/circuit-status" | jq -r '.state')
echo "Circuit Breaker State: $CB_STATE (should be CLOSED)"
echo ""

echo "Making 5 more requests to confirm recovery:"
for i in {1..5}; do
    RESPONSE=$(curl -s --max-time 10 "${CLIENT_URL}/fetch-data")
    STATUS=$(echo "$RESPONSE" | jq -r '.status')
    echo "  Request $i: $STATUS"
done
echo ""

