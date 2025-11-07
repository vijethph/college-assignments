#!/bin/bash

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

echo "Configuring backend for 30% failure rate and 30% latency..."
curl -s -X POST "${BACKEND_URL}/config/failure" \
  -H "Content-Type: application/json" \
  -d '{"failure_rate": 0.3, "status_code": 500}' > /dev/null
curl -s -X POST "${BACKEND_URL}/config/latency" \
  -H "Content-Type: application/json" \
  -d '{"delay_ms": 2000, "delay_rate": 0.3}' > /dev/null
echo ""

echo "Testing client service at: ${CLIENT_URL}"
echo ""

echo "=== Health Check ==="
RESPONSE=$(curl -s --max-time 5 "${CLIENT_URL}/health" 2>&1)
if [ $? -eq 0 ]; then
    echo "$RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE"
else
    echo "Health check failed or timed out"
    echo "Response: $RESPONSE"
fi
echo ""

echo "=== Fetching data 10 times to observe failures and delays ==="
for i in {1..10}; do
    echo "Request $i:"
    START=$(date +%s.%N)
    RESPONSE=$(curl -s --max-time 15 -w "\n%{http_code}" "${CLIENT_URL}/fetch-data" 2>&1)
    EXIT_CODE=$?
    END=$(date +%s.%N)
    DURATION=$(echo "$END - $START" | bc)

    if [ $EXIT_CODE -eq 0 ]; then
        HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
        BODY=$(echo "$RESPONSE" | head -n-1)
        echo "$BODY" | jq -c . 2>/dev/null || echo "$BODY"
        echo "HTTP Status: $HTTP_CODE"
    else
        echo "Request failed or timed out"
        echo "Response: $RESPONSE"
    fi

    echo "Duration: ${DURATION}s"
    echo "---"
    sleep 1
done
