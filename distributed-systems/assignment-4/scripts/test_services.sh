#!/bin/bash

set -e

MODE="${1:-local}"

case "$MODE" in
    local)
        GATEWAY_URL="http://localhost:8000"
        ;;
    docker)
        GATEWAY_URL="http://localhost:8000"
        ;;
    kubernetes|k8s)
        GATEWAY_URL="${2}"
        if [ -z "$GATEWAY_URL" ]; then
            echo "[ERROR] Gateway URL not provided for Kubernetes mode"
            echo ""
            echo "Usage: $0 k8s <gateway-url>"
            exit 1
        fi
        echo "[INFO] Using API Gateway at: $GATEWAY_URL"
        ;;
    *)
        echo "Usage: $0 [local|docker|k8s <url>]"
        echo ""
        echo "Examples:"
        echo "  $0 local                           # Test local services"
        echo "  $0 docker                          # Test Docker Compose services"
        echo "  $0 k8s http://127.0.0.1:12345      # Test Kubernetes services"
        exit 1
        ;;
esac

echo "Microservices Test"
echo "--------------------------------------------------"
echo "Mode: $MODE"
echo "Gateway URL: $GATEWAY_URL"
echo ""

CHECKIN=$(date -d "+7 days" +%Y-%m-%d 2>/dev/null || date -v+7d +%Y-%m-%d)
CHECKOUT=$(date -d "+10 days" +%Y-%m-%d 2>/dev/null || date -v+10d +%Y-%m-%d)

echo "[1/13] Testing API Gateway health..."
response=$(curl -s -w "\n%{http_code}" "$GATEWAY_URL/health")
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "200" ]; then
    echo "[PASS] API Gateway is healthy"
else
    echo "[FAIL] API Gateway not reachable (HTTP $http_code)"
    exit 1
fi
echo ""

echo "[2/13] Listing all hotels..."
response=$(curl -s -w "\n%{http_code}" "$GATEWAY_URL/api/hotels")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)
if [ "$http_code" = "200" ]; then
    hotel_count=$(echo "$body" | grep -o '"id":' | wc -l)
    HOTEL_ID=$(echo "$body" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    echo "[PASS] Found $hotel_count hotels (First ID: $HOTEL_ID)"
else
    echo "[FAIL] Failed to list hotels (HTTP $http_code)"
    exit 1
fi

if [ -z "$HOTEL_ID" ]; then
    echo "[WARNING] No hotels found. Run ./scripts/init_data.sh $MODE first"
    exit 1
fi
echo ""

echo "[3/13] Getting specific hotel details..."
response=$(curl -s -w "\n%{http_code}" "$GATEWAY_URL/api/hotels/$HOTEL_ID")
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "200" ]; then
    echo "[PASS] Retrieved hotel $HOTEL_ID details"
else
    echo "[FAIL] Failed to get hotel details (HTTP $http_code)"
fi
echo ""

echo "[4/13] Getting hotel rooms..."
response=$(curl -s -w "\n%{http_code}" "$GATEWAY_URL/api/hotels/$HOTEL_ID/rooms")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)
if [ "$http_code" = "200" ]; then
    ROOM_ID=$(echo "$body" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    room_count=$(echo "$body" | grep -o '"id":' | wc -l)
    echo "[PASS] Found $room_count rooms (First ID: $ROOM_ID)"
else
    echo "[FAIL] Failed to get rooms (HTTP $http_code)"
    exit 1
fi
echo ""

echo "[5/13] Checking room availability..."
response=$(curl -s -w "\n%{http_code}" -X POST "$GATEWAY_URL/api/hotels/$HOTEL_ID/rooms/check-availability" \
    -H "Content-Type: application/json" \
    -d "{\"check_in\": \"$CHECKIN\", \"check_out\": \"$CHECKOUT\"}")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)
if [ "$http_code" = "200" ]; then
    available_count=$(echo "$body" | grep -o '"room_id":' | wc -l)
    echo "[PASS] Found $available_count available rooms"
else
    echo "[FAIL] Failed to check availability (HTTP $http_code)"
fi
echo ""

echo "[6/13] Registering new user..."
timestamp=$(date +%s)
TEST_EMAIL="test${timestamp}@example.com"
response=$(curl -s -w "\n%{http_code}" -X POST "$GATEWAY_URL/api/users/register" \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"$TEST_EMAIL\", \"name\": \"Test User $timestamp\", \"password\": \"password123\", \"phone\": \"+353123456789\"}")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)
if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
    USER_ID=$(echo "$body" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    echo "[PASS] User registered (ID: $USER_ID, Email: $TEST_EMAIL)"
else
    echo "[FAIL] User registration failed (HTTP $http_code)"
    echo "Response: $body"
    exit 1
fi
echo ""

echo "[7/13] User login..."
response=$(curl -s -w "\n%{http_code}" -X POST "$GATEWAY_URL/api/users/login" \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"$TEST_EMAIL\", \"password\": \"password123\"}")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)
if [ "$http_code" = "200" ]; then
    TOKEN=$(echo "$body" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    echo "[PASS] Login successful (Token received)"
else
    echo "[FAIL] Login failed (HTTP $http_code)"
    TOKEN=""
fi
echo ""

echo "[8/13] Getting user details..."
response=$(curl -s -w "\n%{http_code}" "$GATEWAY_URL/api/users/$USER_ID")
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "200" ]; then
    echo "[PASS] Retrieved user $USER_ID details"
else
    echo "[FAIL] Failed to get user details (HTTP $http_code)"
fi
echo ""

echo "[9/13] Updating user information..."
response=$(curl -s -w "\n%{http_code}" -X PUT "$GATEWAY_URL/api/users/$USER_ID" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"Updated Test User\", \"phone\": \"+353987654321\"}")
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "200" ]; then
    echo "[PASS] User information updated"
else
    echo "[FAIL] Failed to update user (HTTP $http_code)"
fi
echo ""

echo "[10/13] Creating booking..."
response=$(curl -s -w "\n%{http_code}" -X POST "$GATEWAY_URL/api/bookings" \
    -H "Content-Type: application/json" \
    -d "{\"user_id\": $USER_ID, \"hotel_id\": $HOTEL_ID, \"room_id\": $ROOM_ID, \"check_in\": \"$CHECKIN\", \"check_out\": \"$CHECKOUT\"}")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)
if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
    BOOKING_ID=$(echo "$body" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    total_price=$(echo "$body" | grep -o '"total_price":[0-9.]*' | cut -d':' -f2)
    echo "[PASS] Booking created (ID: $BOOKING_ID, Total: \$$total_price, Check-in: $CHECKIN, Check-out: $CHECKOUT)"
else
    echo "[FAIL] Booking creation failed (HTTP $http_code)"
    echo "Response: $body"
    exit 1
fi
echo ""

echo "[11/13] Getting booking details..."
response=$(curl -s -w "\n%{http_code}" "$GATEWAY_URL/api/bookings/$BOOKING_ID")
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "200" ]; then
    echo "[PASS] Retrieved booking $BOOKING_ID details"
else
    echo "[FAIL] Failed to get booking details (HTTP $http_code)"
fi
echo ""

echo "[12/13] Getting user bookings..."
response=$(curl -s -w "\n%{http_code}" "$GATEWAY_URL/api/bookings/user/$USER_ID")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)
if [ "$http_code" = "200" ]; then
    booking_count=$(echo "$body" | grep -o '"id":' | wc -l)
    echo "[PASS] Retrieved $booking_count booking(s) for user $USER_ID"
else
    echo "[FAIL] Failed to get user bookings (HTTP $http_code)"
fi
echo ""

echo "[13/13] Cancelling booking..."
response=$(curl -s -w "\n%{http_code}" -X PUT "$GATEWAY_URL/api/bookings/$BOOKING_ID/cancel" \
    -H "Content-Type: application/json" \
    -d '{"reason": "Testing cancellation"}')
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "200" ]; then
    echo "[PASS] Booking $BOOKING_ID cancelled successfully"
else
    echo "[FAIL] Failed to cancel booking (HTTP $http_code)"
fi
echo ""

echo "[SUCCESS] All tests completed successfully!"
