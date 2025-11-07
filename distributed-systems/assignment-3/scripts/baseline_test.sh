#!/bin/bash

set -e

echo "Setting up port-forward to backend and client services..."
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


echo "Baseline Test - Part A"
echo ""



echo "--- Test 1: Normal Operation (No Failures) ---"
echo "Configuring backend for 0% failure rate..."
curl -s -X POST "${BACKEND_URL}/config/failure" \
  -H "Content-Type: application/json" \
  -d '{"failure_rate": 0.0, "status_code": 500}' | jq .
curl -s -X POST "${BACKEND_URL}/config/latency" \
  -H "Content-Type: application/json" \
  -d '{"delay_ms": 0, "delay_rate": 0.0}' | jq .
echo ""
echo "Making 5 requests - expect all to succeed:"
for i in {1..5}; do
    echo -n "Request $i: "
    RESPONSE=$(curl -s --max-time 10 "${CLIENT_URL}/fetch-data")
    STATUS=$(echo "$RESPONSE" | jq -r '.status')
    echo "$STATUS"
done
echo ""

echo "=== Test 2: High Failure Rate (50%) ==="
echo "Configuring backend for 50% failure rate..."
curl -s -X POST "${BACKEND_URL}/config/failure" \
  -H "Content-Type: application/json" \
  -d '{"failure_rate": 0.5, "status_code": 500}' | jq .
echo ""
echo "Making 10 requests - expect ~5 failures:"
SUCCESS=0
FAIL=0
for i in {1..10}; do
    RESPONSE=$(curl -s --max-time 10 "${CLIENT_URL}/fetch-data")
    STATUS=$(echo "$RESPONSE" | jq -r '.status')
    if [ "$STATUS" == "success" ]; then
        SUCCESS=$((SUCCESS + 1))
        echo "Request $i: SUCCESS"
    else
        FAIL=$((FAIL + 1))
        echo "Request $i: FAILED"
    fi
done
echo "Results: $SUCCESS successes, $FAIL failures"
echo ""

echo "=== Test 3: High Latency (100% with 3 second delay) ==="
echo "Configuring backend for 100% latency with 3s delay..."
curl -s -X POST "${BACKEND_URL}/config/failure" \
  -H "Content-Type: application/json" \
  -d '{"failure_rate": 0.0, "status_code": 500}' | jq .
curl -s -X POST "${BACKEND_URL}/config/latency" \
  -H "Content-Type: application/json" \
  -d '{"delay_ms": 3000, "delay_rate": 1.0}' | jq .
echo ""
echo "Making 3 requests - expect all to be delayed:"
for i in {1..3}; do
    echo -n "Request $i: "
    START=$(date +%s)
    RESPONSE=$(curl -s --max-time 10 "${CLIENT_URL}/fetch-data")
    END=$(date +%s)
    DURATION=$((END - START))
    STATUS=$(echo "$RESPONSE" | jq -r '.status')
    echo "$STATUS (took ${DURATION}s)"
done
echo ""

echo "=== Test 4: Complete Failure (100% failure) ==="
echo "Configuring backend for 100% failure rate..."
curl -s -X POST "${BACKEND_URL}/config/failure" \
  -H "Content-Type: application/json" \
  -d '{"failure_rate": 1.0, "status_code": 500}' | jq .
curl -s -X POST "${BACKEND_URL}/config/latency" \
  -H "Content-Type: application/json" \
  -d '{"delay_ms": 0, "delay_rate": 0.0}' | jq .
echo ""
echo "Making 5 requests - expect all to fail:"
for i in {1..5}; do
    RESPONSE=$(curl -s --max-time 10 "${CLIENT_URL}/fetch-data")
    STATUS=$(echo "$RESPONSE" | jq -r '.status')
    MESSAGE=$(echo "$RESPONSE" | jq -r '.message')
    echo "Request $i: $STATUS - $MESSAGE"
done
echo ""
