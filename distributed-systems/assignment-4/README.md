# Hotel Booking & Reservation Microservices System

A microservices-based hotel booking system built with Python, FastAPI, and structured for deployment on Kubernetes.

## Architecture

This system demonstrates a microservices architecture with four services:

- **API Gateway** (Port 8000): Unified entry point, request routing, and aggregation
- **Hotel Service** (Port 8001): Manages hotel inventory, rooms, and availability
- **User Service** (Port 8002): Handles user authentication and profiles
- **Booking Service** (Port 8003): Manages reservations and coordinates between Hotel and User services

### Service Boundaries

**Granularity Disintegrators:**

- Different scalability needs (bookings scale independently)
- Code volatility (hotel data vs. booking logic)
- Fault tolerance (service failures are isolated)

**Communication Pattern:**

- API Gateway routes external requests to appropriate services
- Synchronous REST APIs for inter-service communication
- Retry logic with exponential backoff
- Structured logging with correlation

## Prerequisites

### For Local Development

- Python 3.11
- pipenv
- SQLite (included with Python)

### For Docker Deployment

- Docker 20.10+
- Docker Compose 2.0+

### For Kubernetes Deployment

- kubectl
- Minikube v1.32.0 or similar Kubernetes cluster

## Setup Instructions

### 1. Install Dependencies

```bash
pipenv install
```

### 2. Activate Virtual Environment

```bash
pipenv shell
```

### 3. Initialize Hotel Data

```bash
./scripts/init_data.sh local
```

## Running the Services

### Option 1: Using Bash Scripts (Recommended)

The project includes reusable bash scripts that work across all deployment environments (local, Docker, Kubernetes).

**Start all services:**

```bash
./scripts/start_services.sh local
```

**Initialize data:**

```bash
./scripts/init_data.sh local
```

**Run tests:**

```bash
./scripts/test_services.sh local
```

**Stop services:**

```bash
./scripts/stop_services.sh local
```

See [scripts/README.md](scripts/README.md) for detailed documentation.

### Option 2: Manual Start

Each service needs to run in a separate terminal window.

#### Terminal 1: Hotel Service

```bash
cd services/hotel_service
python main.py
```

The service will start on `http://localhost:8001`

#### Terminal 2: User Service

```bash
cd services/user_service
python main.py
```

The service will start on `http://localhost:8002`

### Terminal 3: Booking Service

```bash
cd services/booking_service
python main.py
```

The service will start on `http://localhost:8003`

## Quick Start

### Local Development

The fastest way to get started:

```bash
# 1. Install dependencies
pipenv install

# 2. Activate environment
pipenv shell

# 3. Start all services
./scripts/start_services.sh local

# 4. In another terminal, initialize data
./scripts/init_data.sh local

# 5. Run automated tests
./scripts/test_services.sh local

# 6. Stop services when done
./scripts/stop_services.sh local
```

### Docker Deployment

Using Docker Compose for containerized deployment:

```bash
# 1. Build and start all services
docker-compose up --build

# 2. In another terminal, initialize data
./scripts/init_data.sh docker

# 3. Run tests
./scripts/test_services.sh docker

# 4. Stop services
docker-compose down
```

Or use the bash scripts:

```bash
./scripts/start_services.sh docker    # Runs docker-compose up
./scripts/init_data.sh docker
./scripts/test_services.sh docker
./scripts/stop_services.sh docker     # Runs docker-compose down
```

**Access services:**

- API Gateway: http://localhost:8000
- Hotel Service: http://localhost:8001
- User Service: http://localhost:8002
- Booking Service: http://localhost:8003

**View logs:**

```bash
docker-compose logs -f                    # All services
docker-compose logs -f hotel-service      # Specific service
```

**Check service health:**

```bash
docker-compose ps
curl http://localhost:8000/health         # API Gateway
```

## Automated Testing

After starting all services, run the automated test suite:

```bash
./scripts/test_services.sh local
```

This will:

1. Check health of all services
2. List available hotels
3. Check room availability
4. Register a test user
5. Create a booking
6. Retrieve user bookings
7. Cancel the booking

## API Endpoints

### API Gateway (http://localhost:8000)

The API Gateway provides a unified entry point for all services:

- `GET /health` - Gateway health check
- `GET /api/hotels/*` - Routes to Hotel Service
- `GET /api/users/*` - Routes to User Service
- `GET /api/bookings/*` - Routes to Booking Service

**Example using API Gateway:**

```bash
# List hotels through gateway
curl http://localhost:8000/api/hotels

# Create booking through gateway
curl -X POST http://localhost:8000/api/bookings \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "hotel_id": 1, "room_id": 1, "check_in": "2025-11-10", "check_out": "2025-11-12"}'
```

### Hotel Service (http://localhost:8001)

- `GET /health` - Health check
- `GET /hotels` - List all hotels (filters: location, min_rating)
- `GET /hotels/{hotel_id}` - Get hotel details
- `GET /hotels/{hotel_id}/rooms` - Get hotel rooms (filters: room_type, min_capacity, max_price)
- `POST /hotels/{hotel_id}/rooms/check-availability` - Check room availability
- `PUT /hotels/{hotel_id}/rooms/{room_id}/availability` - Update room availability (internal)

### User Service (http://localhost:8002)

- `GET /health` - Health check
- `POST /users/register` - Register new user
- `POST /users/login` - Login and get JWT token
- `GET /users/{user_id}` - Get user profile
- `PUT /users/{user_id}` - Update user profile

### Booking Service (http://localhost:8003)

- `GET /health` - Health check
- `POST /bookings` - Create new booking
- `GET /bookings/{booking_id}` - Get booking details
- `GET /bookings/user/{user_id}` - Get user's bookings
- `PUT /bookings/{booking_id}/cancel` - Cancel booking

## Manual Testing with curl

### 1. Register a User

```bash
curl -X POST http://localhost:8002/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "password": "password123",
    "phone": "+353123456789"
  }'
```

### 2. List Available Hotels

```bash
curl http://localhost:8001/hotels
```

### 3. Check Room Availability

```bash
curl -X POST http://localhost:8001/hotels/1/rooms/check-availability \
  -H "Content-Type: application/json" \
  -d '{
    "check_in": "2025-11-10",
    "check_out": "2025-11-12"
  }'
```

### 4. Create a Booking

```bash
curl -X POST http://localhost:8003/bookings \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "hotel_id": 1,
    "room_id": 1,
    "check_in": "2025-11-10",
    "check_out": "2025-11-12"
  }'
```

### 5. Get User Bookings

```bash
curl http://localhost:8003/bookings/user/1
```

### 6. Cancel a Booking

```bash
curl -X PUT http://localhost:8003/bookings/1/cancel \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Plans changed"
  }'
```

## Project Structure

```
microservices-assignment/
├── scripts/
│   ├── init_data.sh          # Initialize sample data (multi-env)
│   ├── start_services.sh     # Start services (multi-env)
│   ├── stop_services.sh      # Stop services (multi-env)
│   ├── test_services.sh      # Run tests (multi-env)
│   └── README.md             # Scripts documentation
├── services/
│   ├── api_gateway/
│   │   ├── main.py           # API Gateway application
│   │   ├── config.py         # Configuration
│   │   └── Dockerfile        # Container definition
│   ├── hotel_service/
│   │   ├── main.py           # FastAPI application
│   │   ├── models.py         # Pydantic models
│   │   ├── database.py       # SQLAlchemy models
│   │   ├── config.py         # Configuration
│   │   └── Dockerfile        # Container definition
│   ├── booking_service/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── database.py
│   │   ├── config.py
│   │   └── Dockerfile
│   └── user_service/
│       ├── main.py
│       ├── models.py
│       ├── database.py
│       ├── config.py
│       └── Dockerfile
├── shared/
│   ├── logging_config.py     # Structured logging setup
│   └── utils.py              # Retry logic and decorators
├── docker-compose.yml        # Multi-container orchestration
├── .dockerignore             # Docker build exclusions
├── .env.example              # Environment variables template
├── Pipfile                   # Dependencies
└── README.md
```

## Technologies Used

- **FastAPI**: Modern, high-performance web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **SQLite**: Lightweight database
- **structlog**: Structured logging
- **python-jose**: JWT token handling
- **passlib**: Password hashing
- **requests**: HTTP client for inter-service communication
- **aiohttp**: Async HTTP client for API Gateway
- **Docker**: Containerization platform
- **Docker Compose**: Multi-container orchestration

## Logging

All services use structured logging with JSON output. Key log events:

- Service startup/shutdown
- Inter-service calls with latency
- Booking lifecycle events
- Errors with full context

## Error Handling

- Comprehensive try-except blocks
- HTTP exceptions with proper status codes
- Retry logic for inter-service calls (3 retries with exponential backoff)
- Compensating transactions (e.g., room availability rollback on booking failure)

## Development Notes

- Services are independently deployable
- Each service has its own database
- No shared code dependencies between services (except shared utilities)
- PEP 8 compliant code
- Type hints throughout

## Troubleshooting

### Local Development

**Services not connecting:**

- Ensure all services are running
- Check that ports 8001, 8002, 8003 are not in use: `lsof -ti:8001,8002,8003`
- Verify service URLs in config files
- Check logs: `tail -f /tmp/*-service.log` (when using bash scripts)

**Database errors:**

- Delete `*.db` files in service directories
- Run `./scripts/init_data.sh local` again
- Check file permissions in the service directories

**Import errors:**

- Ensure you're in the pipenv shell: `pipenv shell`
- Verify dependencies are installed: `pipenv install`
- Check that `sys.path` modifications in main.py are correct

**Script permission errors:**

```bash
chmod +x scripts/*.sh
```

### Docker Deployment

**Build failures:**

```bash
# Clean rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

**Container not starting:**

```bash
# Check logs
docker-compose logs <service-name>

# Check status
docker-compose ps
```

**Network issues:**

```bash
# Restart with fresh network
docker-compose down
docker network prune
docker-compose up
```

**Port conflicts:**

```bash
# Check what's using the ports
lsof -ti:8000,8001,8002,8003

# Change ports in docker-compose.yml if needed
```

**Volume issues:**

```bash
# Remove volumes and restart
docker-compose down -v
docker-compose up
```

## Multi-Environment Support

All bash scripts support three deployment modes:

### Local Development

```bash
./scripts/start_services.sh local
./scripts/test_services.sh local
./scripts/stop_services.sh local
```

### Docker (Part 2)

```bash
./scripts/start_services.sh docker
./scripts/init_data.sh docker
./scripts/test_services.sh docker
./scripts/stop_services.sh docker
```

### Kubernetes (Part 3)

```bash
./scripts/start_services.sh kubernetes hotel-booking
./scripts/init_data.sh kubernetes hotel-booking
./scripts/test_services.sh kubernetes hotel-booking
./scripts/stop_services.sh kubernetes hotel-booking
```

See [scripts/README.md](scripts/README.md) for detailed documentation.

## Kubernetes Deployment

### Prerequisites

Ensure you have Minikube and kubectl installed:

```bash
# Check Minikube
minikube version

# Check kubectl
kubectl version --client

# Start Minikube (if not already running)
minikube start
```

### Deploy to Kubernetes

**Quick Deploy:**

```bash
./scripts/deploy_k8s.sh
```

This script will:

1. Build Docker images in Minikube's Docker environment
2. Create the `hotel-booking` namespace
3. Create PersistentVolumeClaims for data storage
4. Deploy all services (hotel, user, booking, api-gateway)
5. Wait for all deployments to be ready
6. Display access information

**Manual Deployment:**

```bash
# Set Docker environment to Minikube
eval $(minikube docker-env)

# Build images
docker build -t hotel-service:latest -f services/hotel_service/Dockerfile .
docker build -t user-service:latest -f services/user_service/Dockerfile .
docker build -t booking-service:latest -f services/booking_service/Dockerfile .
docker build -t api-gateway:latest -f services/api_gateway/Dockerfile .

# Apply Kubernetes manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/hotel-service/
kubectl apply -f k8s/user-service/
kubectl apply -f k8s/booking-service/
kubectl apply -f k8s/api-gateway/

# Wait for deployments
kubectl wait --for=condition=available --timeout=300s deployment --all -n hotel-booking
```

### Access the Services

**API Gateway:**

The API Gateway is exposed via NodePort on port 30000:

```bash
# Get Minikube IP
minikube ip

# Access gateway (replace with your Minikube IP)
curl http://$(minikube ip):30000/health

# Or use Minikube service
minikube service api-gateway -n hotel-booking
```

### Monitoring and Management

**Check Deployment Status:**

```bash
./scripts/k8s_status.sh
```

**View Resources:**

```bash
# All resources
kubectl get all -n hotel-booking

# Pods with details
kubectl get pods -n hotel-booking -o wide

# Services
kubectl get services -n hotel-booking

# Deployments
kubectl get deployments -n hotel-booking
```

**View Logs:**

```bash
# View logs for a specific service
kubectl logs -f deployment/api-gateway -n hotel-booking
kubectl logs -f deployment/hotel-service -n hotel-booking

# View logs for a specific pod
kubectl logs -f <pod-name> -n hotel-booking

# View logs from all pods of a service
kubectl logs -l app=booking-service -n hotel-booking
```

**Scale Services:**

```bash
# Scale booking service to 3 replicas
kubectl scale deployment booking-service --replicas=3 -n hotel-booking

# Verify scaling
kubectl get pods -n hotel-booking
```

**Test Pod Resilience:**

```bash
# Delete a pod (Kubernetes will recreate it)
kubectl delete pod <pod-name> -n hotel-booking

# Watch pods recover
kubectl get pods -n hotel-booking -w
```

**Rolling Updates:**

```bash
# Rebuild and update an image
eval $(minikube docker-env)
docker build -t hotel-service:latest -f services/hotel_service/Dockerfile .

# Restart deployment (triggers rolling update)
kubectl rollout restart deployment/hotel-service -n hotel-booking

# Watch rollout status
kubectl rollout status deployment/hotel-service -n hotel-booking
```

### Cleanup Kubernetes Resources

**Quick Cleanup:**

```bash
./scripts/cleanup_k8s.sh
```

**Manual Cleanup:**

```bash
# Delete all resources
kubectl delete -f k8s/api-gateway/
kubectl delete -f k8s/booking-service/
kubectl delete -f k8s/user-service/
kubectl delete -f k8s/hotel-service/
kubectl delete -f k8s/pvc.yaml
kubectl delete -f k8s/namespace.yaml

# Or delete namespace (removes everything)
kubectl delete namespace hotel-booking
```

### Kubernetes Architecture

The Kubernetes deployment includes:

- **Namespace**: `hotel-booking` - Logical isolation for all resources
- **Deployments**: Each service runs with 2 replicas for high availability
- **Services**: ClusterIP for internal services, NodePort for API Gateway
- **ConfigMaps**: Environment-specific configuration for each service
- **PersistentVolumeClaims**: Data persistence for SQLite databases
- **Health Probes**: Liveness and readiness checks for all services
- **Resource Limits**: CPU and memory limits for optimal resource usage

**Service Discovery:**

Services communicate using Kubernetes DNS:

- `http://hotel-service.hotel-booking.svc.cluster.local:8000`
- `http://user-service.hotel-booking.svc.cluster.local:8000`
- `http://booking-service.hotel-booking.svc.cluster.local:8000`

### Kubernetes Troubleshooting

**Pods not starting:**

```bash
# Check pod status
kubectl get pods -n hotel-booking

# Describe pod for events
kubectl describe pod <pod-name> -n hotel-booking

# Check logs
kubectl logs <pod-name> -n hotel-booking

# Check previous container logs (if crashed)
kubectl logs <pod-name> -n hotel-booking --previous
```

**Service not accessible:**

```bash
# Check service endpoints
kubectl get endpoints -n hotel-booking

# Test from within cluster
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -n hotel-booking -- \
  curl http://hotel-service:8000/health
```

**Image pull issues:**

```bash
# Ensure using Minikube's Docker
eval $(minikube docker-env)

# Rebuild images
docker build -t hotel-service:latest -f services/hotel_service/Dockerfile .

# Check images in Minikube
minikube ssh docker images | grep hotel-service
```

**Resource issues:**

```bash
# Check resource usage
kubectl top pods -n hotel-booking
kubectl top nodes

# Increase Minikube resources
minikube stop
minikube start --cpus=4 --memory=8192
```
