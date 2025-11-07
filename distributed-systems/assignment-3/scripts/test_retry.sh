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


echo "Retry with Exponential Backoff Test - Part B"
echo ""

echo "--- Phase 1: Transient Failures (50% failure rate) ---"
echo "Configuring backend for 50% transient failures (503)..."
curl -s -X POST "${BACKEND_URL}/config/failure" \
  -H "Content-Type: application/json" \
  -d '{"failure_rate": 0.5, "status_code": 503}' | jq .
curl -s -X POST "${BACKEND_URL}/config/latency" \
  -H "Content-Type: application/json" \
  -d '{"delay_ms": 0, "delay_rate": 0.0}' | jq .
echo ""

echo "Making 10 requests to observe retry behavior..."
echo ""

SUCCESS_COUNT=0
RETRY_COUNT=0

for i in {1..10}; do
    echo "--- Request $i ---"
    START=$(date +%s)
    RESPONSE=$(curl -s --max-time 30 "${CLIENT_URL}/fetch-data")
    END=$(date +%s)
    DURATION=$((END - START))

    STATUS=$(echo "$RESPONSE" | jq -r '.status')

    if [ "$STATUS" == "success" ]; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        if [ $DURATION -gt 2 ]; then
            echo "Status: SUCCESS (likely after retries, took ${DURATION}s)"
            RETRY_COUNT=$((RETRY_COUNT + 1))
        else
            echo "Status: SUCCESS (first attempt, took ${DURATION}s)"
        fi
    else
        MESSAGE=$(echo "$RESPONSE" | jq -r '.message')
        echo "Status: FAILED - $MESSAGE (took ${DURATION}s)"
    fi
    echo ""
    sleep 1
done

echo "Results: $SUCCESS_COUNT successes out of 10 requests"
echo "Estimated requests with retries: ~$RETRY_COUNT"
echo ""

echo "--- Phase 2: Intermittent 429 (Rate Limiting) ---"
echo "Configuring backend for 70% rate limit errors (429)..."
curl -s -X POST "${BACKEND_URL}/config/failure" \
  -H "Content-Type: application/json" \
  -d '{"failure_rate": 0.7, "status_code": 429}' | jq .
echo ""

echo "Making 5 requests to observe retry with backoff..."
echo ""

for i in {1..5}; do
    echo "--- Request $i ---"
    START=$(date +%s)
    RESPONSE=$(curl -s --max-time 30 "${CLIENT_URL}/fetch-data")
    END=$(date +%s)
    DURATION=$((END - START))

    STATUS=$(echo "$RESPONSE" | jq -r '.status')
    MESSAGE=$(echo "$RESPONSE" | jq -r '.message' 2>/dev/null || echo "")

    echo "Status: $STATUS"
    if [ -n "$MESSAGE" ] && [ "$MESSAGE" != "null" ]; then
        echo "Message: $MESSAGE"
    fi
    echo "Duration: ${DURATION}s"
    echo ""
    sleep 2
done

echo "--- Phase 3: Demonstrating Exponential Backoff ---"
echo "Configuring backend for 100% transient failures (503)..."
curl -s -X POST "${BACKEND_URL}/config/failure" \
  -H "Content-Type: application/json" \
  -d '{"failure_rate": 1.0, "status_code": 503}' | jq .
echo ""

echo "Making 3 requests - all will retry 3 times with exponential backoff..."
echo ""

for i in {1..3}; do
    echo "--- Request $i ---"
    START=$(date +%s)
    RESPONSE=$(curl -s --max-time 30 "${CLIENT_URL}/fetch-data")
    END=$(date +%s)
    DURATION=$((END - START))

    STATUS=$(echo "$RESPONSE" | jq -r '.status')
    MESSAGE=$(echo "$RESPONSE" | jq -r '.message')

    echo "Status: $STATUS"
    echo "Message: $MESSAGE"
    echo "Total duration: ${DURATION}s (should be ~7-10s with 3 retries)"
    echo ""
    sleep 2
done

echo "--- Phase 4: Quick Recovery Scenario ---"
echo "Configuring backend for 30% transient failures..."
curl -s -X POST "${BACKEND_URL}/config/failure" \
  -H "Content-Type: application/json" \
  -d '{"failure_rate": 0.3, "status_code": 503}' | jq .
echo ""

echo "Making 10 requests to see successful retries..."
echo ""

SUCCESS_FIRST=0
SUCCESS_RETRY=0
FAILED=0

for i in {1..10}; do
    START=$(date +%s)
    RESPONSE=$(curl -s --max-time 30 "${CLIENT_URL}/fetch-data")
    END=$(date +%s)
    DURATION=$((END - START))

    STATUS=$(echo "$RESPONSE" | jq -r '.status')

    if [ "$STATUS" == "success" ]; then
        if [ $DURATION -le 1 ]; then
            SUCCESS_FIRST=$((SUCCESS_FIRST + 1))
            echo "Request $i: SUCCESS (first attempt)"
        else
            SUCCESS_RETRY=$((SUCCESS_RETRY + 1))
            echo "Request $i: SUCCESS (after retry, ${DURATION}s)"
        fi
    else
        FAILED=$((FAILED + 1))
        echo "Request $i: FAILED (all retries exhausted)"
    fi
done

echo ""
echo "Results:"
echo "  - Success on first attempt: $SUCCESS_FIRST"
echo "  - Success after retry: $SUCCESS_RETRY"
echo "  - Failed after all retries: $FAILED"
echo ""

