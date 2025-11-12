#!/bin/bash

set -e

MODE="${1:-local}"

case "$MODE" in
    local)
        BASE_URL="http://localhost:8000"
        ;;
    docker)
        BASE_URL="http://localhost:8000"
        ;;
    kubernetes|k8s)
        BASE_URL="${2}"
        if [ -z "$BASE_URL" ]; then
            echo "[ERROR] Gateway URL not provided for Kubernetes mode"
            echo ""
            echo "Usage: $0 k8s <gateway-url>"
            exit 1
        fi
        echo "[INFO] Using API Gateway at: $BASE_URL"
        ;;
    *)
        echo "Usage: $0 [local|docker|k8s <url>]"
        echo ""
        echo "Examples:"
        echo "  $0 local                           # Use localhost"
        echo "  $0 docker                          # Use Docker Compose services"
        echo "  $0 k8s http://127.0.0.1:12345      # Use Kubernetes"
        exit 1
        ;;
esac

echo "Initializing Sample Data"
echo "-------------------------------"
echo ""

echo "[1/6] Creating hotels..."
curl -s -X POST "$BASE_URL/api/hotels" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Grand Plaza Hotel",
        "location": "Dublin",
        "rating": 4.5,
        "description": "Luxury hotel in the heart of Dublin",
        "amenities": "WiFi, Pool, Gym, Restaurant, Bar, Spa"
    }' > /dev/null

curl -s -X POST "$BASE_URL/api/hotels" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Seaside Resort",
        "location": "Galway",
        "rating": 4.8,
        "description": "Beautiful resort by the Atlantic Ocean",
        "amenities": "WiFi, Beach Access, Pool, Restaurant, Water Sports"
    }' > /dev/null

curl -s -X POST "$BASE_URL/api/hotels" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Mountain Lodge",
        "location": "Killarney",
        "rating": 4.2,
        "description": "Cozy lodge in the Kerry mountains",
        "amenities": "WiFi, Fireplace, Hiking Trails, Restaurant"
    }' > /dev/null

echo "[PASS] Created 3 hotels"
echo ""

echo "[2/6] Adding rooms to Grand Plaza Hotel..."
for room_data in \
    '{"hotel_id":1,"room_type":"Single","price_per_night":150.0,"capacity":1,"available_count":10}' \
    '{"hotel_id":1,"room_type":"Double","price_per_night":180.0,"capacity":2,"available_count":15}' \
    '{"hotel_id":1,"room_type":"Suite","price_per_night":300.0,"capacity":4,"available_count":5}'
do
    curl -s -X POST "$BASE_URL/api/hotels/1/rooms" \
        -H "Content-Type: application/json" \
        -d "$room_data" > /dev/null
done

echo "[PASS] Added 3 room types to Grand Plaza Hotel"
echo ""

echo "[3/6] Adding rooms to other hotels..."
for room_data in \
    '{"hotel_id":2,"room_type":"Single","price_per_night":200.0,"capacity":1,"available_count":8}' \
    '{"hotel_id":2,"room_type":"Double","price_per_night":250.0,"capacity":2,"available_count":12}' \
    '{"hotel_id":2,"room_type":"Suite","price_per_night":400.0,"capacity":4,"available_count":6}'
do
    curl -s -X POST "$BASE_URL/api/hotels/2/rooms" \
        -H "Content-Type: application/json" \
        -d "$room_data" > /dev/null
done

for room_data in \
    '{"hotel_id":3,"room_type":"Single","price_per_night":120.0,"capacity":1,"available_count":12}' \
    '{"hotel_id":3,"room_type":"Double","price_per_night":160.0,"capacity":2,"available_count":10}' \
    '{"hotel_id":3,"room_type":"Suite","price_per_night":280.0,"capacity":4,"available_count":4}'
do
    curl -s -X POST "$BASE_URL/api/hotels/3/rooms" \
        -H "Content-Type: application/json" \
        -d "$room_data" > /dev/null
done

echo "[PASS] Added 6 room types to Seaside Resort and Mountain Lodge"
echo ""

echo "[4/6] Creating sample users..."

user1_response=$(curl -s -X POST "$BASE_URL/api/users/register" \
    -H "Content-Type: application/json" \
    -d '{
        "email": "john.doe@example.com",
        "name": "John Doe",
        "password": "password123",
        "phone": "+353871234567"
    }')
USER1_ID=$(echo "$user1_response" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

user2_response=$(curl -s -X POST "$BASE_URL/api/users/register" \
    -H "Content-Type: application/json" \
    -d '{
        "email": "jane.smith@example.com",
        "name": "Jane Smith",
        "password": "password123",
        "phone": "+353879876543"
    }')
USER2_ID=$(echo "$user2_response" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

user3_response=$(curl -s -X POST "$BASE_URL/api/users/register" \
    -H "Content-Type: application/json" \
    -d '{
        "email": "alice.johnson@example.com",
        "name": "Alice Johnson",
        "password": "password123",
        "phone": "+353861122334"
    }')
USER3_ID=$(echo "$user3_response" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -n "$USER1_ID" ] && [ -n "$USER2_ID" ] && [ -n "$USER3_ID" ]; then
    echo "[PASS] Created 3 sample users (IDs: $USER1_ID, $USER2_ID, $USER3_ID)"
else
    echo "[WARNING] Some users may not have been created. Continuing..."
    USER1_ID="${USER1_ID:-1}"
    USER2_ID="${USER2_ID:-2}"
    USER3_ID="${USER3_ID:-3}"
fi
echo ""

echo "[5/6] Creating sample bookings..."

CHECKIN=$(date -d "+14 days" +%Y-%m-%d 2>/dev/null || date -v+14d +%Y-%m-%d)
CHECKOUT=$(date -d "+17 days" +%Y-%m-%d 2>/dev/null || date -v+17d +%Y-%m-%d)

booking1_response=$(curl -s -X POST "$BASE_URL/api/bookings" \
    -H "Content-Type: application/json" \
    -d "{
        \"user_id\": $USER1_ID,
        \"hotel_id\": 1,
        \"room_id\": 2,
        \"check_in\": \"$CHECKIN\",
        \"check_out\": \"$CHECKOUT\"
    }")
BOOKING1_ID=$(echo "$booking1_response" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

CHECKIN2=$(date -d "+21 days" +%Y-%m-%d 2>/dev/null || date -v+21d +%Y-%m-%d)
CHECKOUT2=$(date -d "+25 days" +%Y-%m-%d 2>/dev/null || date -v+25d +%Y-%m-%d)

booking2_response=$(curl -s -X POST "$BASE_URL/api/bookings" \
    -H "Content-Type: application/json" \
    -d "{
        \"user_id\": $USER2_ID,
        \"hotel_id\": 2,
        \"room_id\": 5,
        \"check_in\": \"$CHECKIN2\",
        \"check_out\": \"$CHECKOUT2\"
    }")
BOOKING2_ID=$(echo "$booking2_response" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

CHECKIN3=$(date -d "+30 days" +%Y-%m-%d 2>/dev/null || date -v+30d +%Y-%m-%d)
CHECKOUT3=$(date -d "+32 days" +%Y-%m-%d 2>/dev/null || date -v+32d +%Y-%m-%d)

booking3_response=$(curl -s -X POST "$BASE_URL/api/bookings" \
    -H "Content-Type: application/json" \
    -d "{
        \"user_id\": $USER3_ID,
        \"hotel_id\": 3,
        \"room_id\": 7,
        \"check_in\": \"$CHECKIN3\",
        \"check_out\": \"$CHECKOUT3\"
    }")
BOOKING3_ID=$(echo "$booking3_response" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -n "$BOOKING1_ID" ] && [ -n "$BOOKING2_ID" ] && [ -n "$BOOKING3_ID" ]; then
    echo "[PASS] Created 3 sample bookings (IDs: $BOOKING1_ID, $BOOKING2_ID, $BOOKING3_ID)"
else
    echo "[WARNING] Some bookings may not have been created"
fi
echo ""

echo "[6/6] Verifying login for sample users..."
login_response=$(curl -s -X POST "$BASE_URL/api/users/login" \
    -H "Content-Type: application/json" \
    -d '{
        "email": "john.doe@example.com",
        "password": "password123"
    }')
TOKEN=$(echo "$login_response" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -n "$TOKEN" ]; then
    echo "[PASS] Sample user login verified"
else
    echo "[WARNING] Could not verify user login"
fi
echo ""

echo "[SUCCESS] Data Initialization Complete"

