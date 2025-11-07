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

echo "Circuit Breaker Test - Part B"
echo ""

echo "--- Phase 1: Normal Operation ---"
echo "Configuring backend for 0% failure rate..."
curl -s -X POST "${BACKEND_URL}/config/failure" \
  -H "Content-Type: application/json" \
  -d '{"failure_rate": 0.0, "status_code": 500}' | jq .
curl -s -X POST "${BACKEND_URL}/config/latency" \
  -H "Content-Type: application/json" \
  -d '{"delay_ms": 0, "delay_rate": 0.0}' | jq .
echo ""

echo "Making 3 requests - all should succeed:"
for i in {1..3}; do
    echo -n "Request $i: "
    RESPONSE=$(curl -s --max-time 10 "${CLIENT_URL}/fetch-data")
    STATUS=$(echo "$RESPONSE" | jq -r '.status')
    echo "$STATUS"
done
echo ""

echo "Circuit breaker status:"
curl -s "${CLIENT_URL}/circuit-status" | jq .
echo ""

echo "--- Phase 2: Triggering Circuit Breaker to OPEN ---"
echo "Configuring backend for 100% failure rate..."
curl -s -X POST "${BACKEND_URL}/config/failure" \
  -H "Content-Type: application/json" \
  -d '{"failure_rate": 1.0, "status_code": 500}' | jq .
echo ""

echo "Making 10 requests to trigger circuit breaker..."
for i in {1..10}; do
    RESPONSE=$(curl -s --max-time 10 "${CLIENT_URL}/fetch-data")
    STATUS=$(echo "$RESPONSE" | jq -r '.status')
    MESSAGE=$(echo "$RESPONSE" | jq -r '.message')
    echo "Request $i: $STATUS - $MESSAGE"

    if [ $i -eq 5 ]; then
        echo ""
        echo "Current circuit breaker status:"
        curl -s "${CLIENT_URL}/circuit-status" | jq .
        echo ""
    fi

    sleep 1
done
echo ""

echo "Final circuit breaker status (should be OPEN):"
curl -s "${CLIENT_URL}/circuit-status" | jq .
echo ""

echo "--- Phase 3: Fast Failing (Circuit Breaker is OPEN) ---"
echo "Making 5 more requests while circuit is OPEN..."
echo "These should fail immediately without hitting backend:"
for i in {1..5}; do
    START=$(date +%s.%N)
    RESPONSE=$(curl -s --max-time 10 "${CLIENT_URL}/fetch-data")
    END=$(date +%s.%N)
    DURATION=$(echo "$END - $START" | bc 2>/dev/null || echo "0")
    STATUS=$(echo "$RESPONSE" | jq -r '.status')
    MESSAGE=$(echo "$RESPONSE" | jq -r '.message')
    echo "Request $i: $STATUS - $MESSAGE (${DURATION}s - should be fast)"
done
echo ""

echo "--- Phase 4: Waiting for HALF-OPEN State ---"
echo "Circuit breaker timeout is 30 seconds..."
echo "Waiting 31 seconds for circuit to attempt HALF-OPEN..."
for i in {30..1}; do
    echo -ne "Waiting... $i seconds remaining\r"
    sleep 1
done
echo ""
echo ""

echo "Circuit breaker status (should be ready for HALF-OPEN):"
curl -s "${CLIENT_URL}/circuit-status" | jq .
echo ""

echo "--- Phase 5: Backend Still Failing (Re-open Circuit) ---"
echo "Making 1 test request while backend still failing..."
RESPONSE=$(curl -s --max-time 10 "${CLIENT_URL}/fetch-data")
STATUS=$(echo "$RESPONSE" | jq -r '.status')
MESSAGE=$(echo "$RESPONSE" | jq -r '.message')
echo "Test request: $STATUS - $MESSAGE"
echo ""

echo "Circuit breaker status (should be OPEN again):"
curl -s "${CLIENT_URL}/circuit-status" | jq .
echo ""

echo "--- Phase 6: Backend Recovery ---"
echo "Configuring backend for 0% failure rate (recovery)..."
curl -s -X POST "${BACKEND_URL}/config/failure" \
  -H "Content-Type: application/json" \
  -d '{"failure_rate": 0.0, "status_code": 500}' | jq .
echo ""

echo "Waiting another 31 seconds for HALF-OPEN..."
for i in {31..1}; do
    echo -ne "Waiting... $i seconds remaining\r"
    sleep 1
done
echo ""
echo ""

echo "Making test request (should succeed and close circuit)..."
RESPONSE=$(curl -s --max-time 10 "${CLIENT_URL}/fetch-data")
STATUS=$(echo "$RESPONSE" | jq -r '.status')
MESSAGE=$(echo "$RESPONSE" | jq -r '.message' 2>/dev/null || echo "Success")
echo "Test request: $STATUS - $MESSAGE"
echo ""

echo "Circuit breaker status (should be CLOSED):"
curl -s "${CLIENT_URL}/circuit-status" | jq .
echo ""

echo "Making 5 more requests to confirm normal operation:"
for i in {1..5}; do
    echo -n "Request $i: "
    RESPONSE=$(curl -s --max-time 10 "${CLIENT_URL}/fetch-data")
    STATUS=$(echo "$RESPONSE" | jq -r '.status')
    echo "$STATUS"
done
echo ""
