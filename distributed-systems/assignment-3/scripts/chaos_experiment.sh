#!/bin/bash


echo "Chaos Engineering Experiment - Part C"
echo ""

kubectl port-forward svc/client-service 9090:9090 > /dev/null 2>&1 &
CLIENT_PF_PID=$!
sleep 2

cleanup() {
    echo ""
    echo "Cleaning up port-forward..."
    kill $CLIENT_PF_PID 2>/dev/null
}
trap cleanup EXIT

echo "Port-forward established to client service"
echo ""

echo "Testing client connectivity..."
for i in {1..3}; do
    RESPONSE=$(curl -s --max-time 5 http://localhost:9090/fetch-data)
    STATUS=$(echo "$RESPONSE" | jq -r '.status' 2>/dev/null)
    echo "  Pre-chaos request $i: $STATUS"
    sleep 1
done

echo ""
echo "Circuit breaker state before chaos:"
curl -s http://localhost:9090/circuit-status | jq .
echo ""

read -r

echo ""
echo "--- Chaos Injection Starting ---"
echo "Scaling backend to 0 replicas"
kubectl scale deployment/backend-service --replicas=0
echo ""
echo "Backend pods being terminated..."
kubectl get pods -l app=backend-service
echo ""

for i in {45..1}; do
    echo -ne "  Time remaining: ${i}s   \r"
    sleep 1
done
echo ""

echo ""
echo "Circuit Breaker State During Chaos"
CB_STATE=$(curl -s http://localhost:9090/circuit-status)
echo "$CB_STATE" | jq .
STATE=$(echo "$CB_STATE" | jq -r '.state')
FAILURE_COUNT=$(echo "$CB_STATE" | jq -r '.failure_count')

if [ "$STATE" == "OPEN" ]; then
    echo ""
    echo "SUCCESS: Circuit breaker is OPEN (as expected)"
    echo "  Failure count: $FAILURE_COUNT"
else
    echo ""
    echo "WARNING: Circuit breaker state is $STATE (expected: OPEN)"
fi
echo ""

echo "Recovery - Scaling backend to 1 replica"
kubectl scale deployment/backend-service --replicas=1
echo ""
echo "Waiting for backend pod to be ready..."
kubectl wait --for=condition=ready pod -l app=backend-service --timeout=60s
echo ""
kubectl get pods -l app=backend-service
echo ""

for i in {40..1}; do
    echo -ne "  Time remaining: ${i}s   \r"
    sleep 1
done
echo ""

echo "Final Circuit Breaker State"
CB_STATE=$(curl -s http://localhost:9090/circuit-status)
echo "$CB_STATE" | jq .
STATE=$(echo "$CB_STATE" | jq -r '.state')

if [ "$STATE" == "CLOSED" ]; then
    echo ""
    echo "SUCCESS: Circuit breaker is CLOSED (system recovered)"
else
    echo ""
    echo "Circuit breaker state is $STATE (expected: CLOSED)"
fi
echo ""

echo "Testing post-recovery connectivity..."
SUCCESS_COUNT=0
for i in {1..5}; do
    RESPONSE=$(curl -s --max-time 5 http://localhost:9090/fetch-data)
    STATUS=$(echo "$RESPONSE" | jq -r '.status' 2>/dev/null)
    echo "  Post-recovery request $i: $STATUS"
    [ "$STATUS" == "success" ] && SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    sleep 1
done

echo ""
if [ $SUCCESS_COUNT -ge 4 ]; then
    echo "System fully recovered ($SUCCESS_COUNT/5 successful)"
else
    echo "System partially recovered ($SUCCESS_COUNT/5 successful)"
fi
