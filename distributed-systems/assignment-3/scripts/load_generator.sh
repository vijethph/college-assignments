#!/bin/bash

CLIENT_URL="${1:-http://localhost:9090}"
INTERVAL="${2:-1}"

echo "Starting continuous load on client service: ${CLIENT_URL}"
echo "Request interval: ${INTERVAL} seconds"
echo "Press Ctrl+C to stop"
echo ""

REQUEST_NUM=0

while true; do
    REQUEST_NUM=$((REQUEST_NUM + 1))
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

    START=$(date +%s.%N)
    RESPONSE=$(curl -s --max-time 10 "${CLIENT_URL}/fetch-data" 2>&1)
    EXIT_CODE=$?
    END=$(date +%s.%N)
    DURATION=$(echo "$END - $START" | bc 2>/dev/null || echo "0")

    if [ $EXIT_CODE -eq 0 ]; then
        STATUS=$(echo "$RESPONSE" | jq -r '.status' 2>/dev/null || echo "unknown")
        if [ "$STATUS" == "success" ]; then
            echo "[$TIMESTAMP] Request #$REQUEST_NUM: SUCCESS (${DURATION}s)"
        else
            MESSAGE=$(echo "$RESPONSE" | jq -r '.message' 2>/dev/null || echo "error")
            echo "[$TIMESTAMP] Request #$REQUEST_NUM: FAILED - $MESSAGE (${DURATION}s)"
        fi
    else
        echo "[$TIMESTAMP] Request #$REQUEST_NUM: TIMEOUT or CONNECTION ERROR (${DURATION}s)"
    fi

    sleep $INTERVAL
done
