<a name="readme-top"></a>

<!-- PROJECT SHIELDS -->

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![License][license-shield]][license-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">

<h3 align="center">Hotel Booking & Reservation Microservices System</h3>

  <p align="center">
    A cloud-native microservices architecture with event-driven communication demonstrating distributed systems principles
    <br />
    <a href="https://github.com/vijethph/college-assignments"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="#usage">View Demo</a>
    ·
    <a href="https://github.com/vijethph/college-assignments/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/vijethph/college-assignments/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
        <li><a href="#architecture">Architecture</a></li>
        <li><a href="#key-features">Key Features</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#deployment">Deployment</a></li>
    <li><a href="#api-reference">API Reference</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

This project demonstrates a production-grade microservices architecture for a hotel booking and reservation system. It showcases modern distributed systems patterns including service mesh principles, event-driven communication via message broker, and comprehensive observability through structured logging.

The system implements four core microservices coordinated through an API Gateway, with asynchronous inter-service communication handled by RabbitMQ. Each service maintains its own SQLite database following the database-per-service pattern, ensuring loose coupling and independent scalability.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

- [![Python][Python.org]][Python-url] **Python 3.11** - Modern async/await support
- [![FastAPI][FastAPI.tiangolo.com]][FastAPI-url] **FastAPI** - High-performance web framework with automatic OpenAPI docs
- [![Docker][Docker.com]][Docker-url] **Docker** - Container runtime and orchestration
- [![Kubernetes][Kubernetes.io]][Kubernetes-url] **Kubernetes** - Container orchestration platform
- [![RabbitMQ][RabbitMQ.com]][RabbitMQ-url] **RabbitMQ** - Message broker for event-driven architecture
- [![SQLAlchemy][SQLAlchemy.org]][SQLAlchemy-url] **SQLAlchemy** - SQL toolkit and ORM
- **SQLite** - Lightweight per-service database
- **structlog** - Structured logging with JSON formatting
- **aiohttp** - Async HTTP client for API Gateway
- **aio-pika** - Async RabbitMQ client for event messaging
- **python-jose** - JWT token handling
- **passlib** - Secure password hashing with bcrypt
- **pipenv** - Dependency management

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Architecture

The system follows a microservices architecture with the following components:

#### Services

1. **API Gateway** (Port 8000)

   - Single entry point for all client requests
   - Request routing and proxying
   - Centralized error handling
   - Service discovery integration

2. **Hotel Service** (Port 8001)

   - Hotel and room management
   - Availability checking
   - Room inventory updates
   - Consumes booking cancellation events

3. **User Service** (Port 8002)

   - User registration and authentication
   - JWT token generation and verification
   - Profile management
   - Consumes booking creation events

4. **Booking Service** (Port 8003)

   - Booking creation and cancellation
   - Room availability validation
   - Price calculation
   - Publishes booking events to message broker

5. **Message Broker** (RabbitMQ - Ports 5672/15672)
   - Event routing via topic exchange
   - Asynchronous inter-service communication
   - Booking creation and cancellation events
   - Management UI for monitoring

#### Communication Patterns

- **Synchronous**: REST APIs for request-response patterns
- **Asynchronous**: RabbitMQ for event-driven communication
  - `booking.created` - Published by Booking Service, consumed by User Service
  - `booking.cancelled` - Published by Booking Service, consumed by Hotel Service

#### Data Management

- **Database-per-Service**: Each service has its own SQLite database
- **No shared databases**: Ensures service independence
- **Data consistency**: Eventually consistent via events

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Key Features

- **Microservices Architecture**: Independently deployable services with clear boundaries
- **Event-Driven Communication**: Asynchronous messaging via RabbitMQ
- **API Gateway Pattern**: Unified entry point with request routing
- **Service Mesh Concepts**: Structured logging, health checks, retry mechanisms
- **Containerization**: Docker images for all services
- **Orchestration**: Kubernetes manifests with ConfigMaps, Services, and Deployments
- **Observability**: JSON structured logging across all services
- **Security**: JWT-based authentication, password hashing with bcrypt
- **Resilience**: Retry logic, health checks, graceful degradation
- **Auto-Documentation**: Swagger UI for all service APIs
- **Multi-Environment**: Support for local, Docker, and Kubernetes deployments

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->

## Getting Started

Follow these instructions to get the project running on your local machine.

### Prerequisites

Choose your deployment method and install the required tools:

**For Local Development:**

- Python 3.11 or higher
  ```sh
  python --version
  ```
- pipenv
  ```sh
  pip install pipenv
  ```

**For Docker Deployment:**

- Docker 20.10+
  ```sh
  docker --version
  ```
- Docker Compose 2.0+
  ```sh
  docker-compose --version
  ```

**For Kubernetes Deployment:**

- kubectl
  ```sh
  kubectl version --client
  ```
- Minikube v1.32.0 or similar Kubernetes cluster
  ```sh
  minikube version
  ```
- Docker (for building images)

**For Message Broker (All Deployments):**

- RabbitMQ is included in Docker and Kubernetes deployments
- For local development, RabbitMQ runs on localhost:5672

### Installation

1. Clone the repository

   ```sh
   git clone https://github.com/vijethph/college-assignments.git
   cd distributed-systems/assignment-4
   ```

2. Install Python dependencies

   ```sh
   pipenv install
   ```

3. Activate the virtual environment

   ```sh
   pipenv shell
   ```

4. Make scripts executable

   ```sh
   chmod +x scripts/*.sh
   ```

5. Choose your deployment method and follow the appropriate section in [Deployment](#deployment)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->

## Usage

### Quick Start

The fastest way to get up and running:

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

## Usage

### Quick Start

The fastest way to get up and running:

```bash
# 1. Install dependencies
pipenv install

# 2. Activate environment
pipenv shell

# 3. Start all services (choose deployment mode)
./scripts/start_services.sh local

# 4. In another terminal, initialize data
./scripts/init_data.sh local

# 5. Run automated tests
./scripts/test_services.sh local

# 6. Stop services when done
./scripts/stop_services.sh local
```

### API Usage Examples

**1. List Available Hotels**

```bash
curl http://localhost:8000/api/hotels
```

**2. Register a New User**

```bash
curl -X POST http://localhost:8000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "name": "John Doe",
    "password": "secure123",
    "phone": "+353123456789"
  }'
```

**3. User Login**

```bash
curl -X POST http://localhost:8000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "secure123"
  }'
```

**4. Create a Booking**

```bash
curl -X POST http://localhost:8000/api/bookings \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "hotel_id": 1,
    "room_id": 1,
    "check_in": "2025-12-01",
    "check_out": "2025-12-05"
  }'
```

**5. View User Bookings**

```bash
curl http://localhost:8000/api/bookings/user/1
```

**6. Cancel a Booking**

```bash
curl -X PUT http://localhost:8000/api/bookings/1/cancel \
  -H "Content-Type: application/json" \
  -d '{"reason": "Plans changed"}'
```

### Interactive API Documentation

Each service provides Swagger UI documentation:

- **API Gateway**: http://localhost:8000/docs
- **Hotel Service**: http://localhost:8001/docs
- **User Service**: http://localhost:8002/docs
- **Booking Service**: http://localhost:8003/docs

### Message Broker Management

Access RabbitMQ Management UI:

- **URL**: http://localhost:15672
- **Username**: guest
- **Password**: guest

Monitor queues, exchanges, and message flow in real-time.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- DEPLOYMENT -->

## Deployment

The project supports three deployment modes with unified scripts.

### Local Development

Perfect for rapid development and testing:

```bash
# Start all services (including RabbitMQ via Docker)
./scripts/start_services.sh local

# Initialize data
./scripts/init_data.sh local

# Run tests
./scripts/test_services.sh local

# Stop services
./scripts/stop_services.sh local
```

**Access services:**

- API Gateway: http://localhost:8000
- Hotel Service: http://localhost:8001
- User Service: http://localhost:8002
- Booking Service: http://localhost:8003
- RabbitMQ Management: http://localhost:15672 (guest/guest)

**Note**: Local mode runs Python services directly and RabbitMQ in Docker.

### Docker Deployment

Containerized deployment with Docker Compose:

```bash
# Start all services (builds images automatically)
./scripts/start_services.sh docker

# Or manually
docker-compose up --build

# Initialize data
./scripts/init_data.sh docker

# Run tests
./scripts/test_services.sh docker

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f booking-service

# Stop services
./scripts/stop_services.sh docker
```

**Docker features:**

- Health checks for automatic recovery
- Volume persistence for databases
- Network isolation between services
- Resource limits and constraints
- RabbitMQ with management plugin
- Automatic restart policies

### Kubernetes Deployment

Production-ready orchestration with Kubernetes:

```bash
# Start Minikube (if not running)
minikube start

# Deploy all services
./scripts/start_services.sh kubernetes hotel-booking

# Or use the dedicated deployment script
./scripts/deploy_k8s.sh

# Get API Gateway URL
GATEWAY_URL=$(minikube service api-gateway -n hotel-booking --url)
echo $GATEWAY_URL

# Initialize data
./scripts/init_data.sh k8s $GATEWAY_URL

# Run tests
./scripts/test_services.sh k8s $GATEWAY_URL

# Check status
./scripts/k8s_status.sh

# View logs
kubectl logs -f deployment/api-gateway -n hotel-booking
kubectl logs -f deployment/booking-service -n hotel-booking
kubectl logs -f deployment/message-broker -n hotel-booking

# Scale services
kubectl scale deployment booking-service --replicas=3 -n hotel-booking

# Port forward RabbitMQ Management UI
kubectl port-forward -n hotel-booking svc/message-broker 15672:15672

# Clean up
./scripts/cleanup_k8s.sh
```

**Kubernetes features:**

- High availability with multiple replicas
- Automatic self-healing with liveness/readiness probes
- Rolling updates with zero downtime
- Service discovery via Kubernetes DNS
- Persistent volumes for RabbitMQ data
- ConfigMaps for environment configuration
- Resource limits and requests
- Namespace isolation

**Service URLs in Kubernetes:**

- API Gateway: `http://<minikube-ip>:30000`
- RabbitMQ Management: Port-forward to access at `http://localhost:15672`

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- API REFERENCE -->

## API Reference

### API Gateway Endpoints

**Base URL:** `http://localhost:8000` (Local/Docker) or `http://<minikube-ip>:30000` (Kubernetes)

#### Hotels

| Method | Endpoint                                        | Description              |
| ------ | ----------------------------------------------- | ------------------------ |
| GET    | `/health`                                       | Gateway health check     |
| GET    | `/api/hotels`                                   | List all hotels          |
| POST   | `/api/hotels`                                   | Create new hotel         |
| GET    | `/api/hotels/{id}`                              | Get hotel details        |
| GET    | `/api/hotels/{id}/rooms`                        | Get hotel rooms          |
| POST   | `/api/hotels/{id}/rooms`                        | Add room to hotel        |
| POST   | `/api/hotels/{id}/rooms/check-availability`     | Check room availability  |
| PUT    | `/api/hotels/{id}/rooms/{room_id}/availability` | Update room availability |

#### Users

| Method | Endpoint              | Description              |
| ------ | --------------------- | ------------------------ |
| POST   | `/api/users/register` | Register new user        |
| POST   | `/api/users/login`    | User login (returns JWT) |
| GET    | `/api/users/{id}`     | Get user profile         |
| PUT    | `/api/users/{id}`     | Update user profile      |
| POST   | `/api/users/verify`   | Verify JWT token         |

#### Bookings

| Method | Endpoint                       | Description         |
| ------ | ------------------------------ | ------------------- |
| POST   | `/api/bookings`                | Create new booking  |
| GET    | `/api/bookings/{id}`           | Get booking details |
| GET    | `/api/bookings/user/{user_id}` | Get user's bookings |
| PUT    | `/api/bookings/{id}/cancel`    | Cancel booking      |

### Hotel Service Endpoints

**Base URL:** `http://localhost:8001`

| Method | Endpoint                                          | Description                    |
| ------ | ------------------------------------------------- | ------------------------------ |
| GET    | `/health`                                         | Service health check           |
| GET    | `/hotels`                                         | List all hotels                |
| POST   | `/hotels`                                         | Create new hotel               |
| GET    | `/hotels/{hotel_id}`                              | Get hotel by ID                |
| GET    | `/hotels/{hotel_id}/rooms`                        | Get hotel rooms                |
| POST   | `/hotels/{hotel_id}/rooms`                        | Add room to hotel              |
| POST   | `/hotels/{hotel_id}/rooms/check-availability`     | Check room availability        |
| PUT    | `/hotels/{hotel_id}/rooms/{room_id}/availability` | Update availability (internal) |

**Query Parameters:**

- `/hotels`: `location`, `min_rating`
- `/hotels/{hotel_id}/rooms`: `room_type`, `min_capacity`, `max_price`

**Events Consumed:**

- `booking.cancelled` - Restores room availability when booking is cancelled

### User Service Endpoints

**Base URL:** `http://localhost:8002`

| Method | Endpoint           | Description             |
| ------ | ------------------ | ----------------------- |
| GET    | `/health`          | Service health check    |
| POST   | `/users/register`  | Register new user       |
| POST   | `/users/login`     | Login and get JWT token |
| GET    | `/users/{user_id}` | Get user profile        |
| PUT    | `/users/{user_id}` | Update user profile     |
| POST   | `/users/verify`    | Verify JWT token        |

**Events Consumed:**

- `booking.created` - Logs booking notification for user

### Booking Service Endpoints

**Base URL:** `http://localhost:8003`

| Method | Endpoint                        | Description          |
| ------ | ------------------------------- | -------------------- |
| GET    | `/health`                       | Service health check |
| POST   | `/bookings`                     | Create new booking   |
| GET    | `/bookings/{booking_id}`        | Get booking details  |
| GET    | `/bookings/user/{user_id}`      | Get user's bookings  |
| PUT    | `/bookings/{booking_id}/cancel` | Cancel booking       |

**Events Published:**

- `booking.created` - Published when booking is successfully created
- `booking.cancelled` - Published when booking is cancelled

### Message Broker Events

**RabbitMQ Exchange:** `hotel_booking_events` (topic)

#### Event Schemas

**booking.created**

```json
{
  "event_type": "booking.created",
  "booking_id": 1,
  "user_id": 1,
  "hotel_id": 1,
  "room_id": 2,
  "check_in": "2025-12-01",
  "check_out": "2025-12-05",
  "total_price": 600.0,
  "timestamp": "2025-11-15T10:30:00Z"
}
```

**booking.cancelled**

```json
{
  "event_type": "booking.cancelled",
  "booking_id": 1,
  "hotel_id": 1,
  "room_id": 2,
  "reason": "Plans changed",
  "timestamp": "2025-11-15T12:00:00Z"
}
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Use type hints throughout
- Write reStructuredText format for docstrings
- Add tests for new features
- Update documentation as needed
- Ensure all services remain independently deployable
- Test across all deployment modes (local, Docker, Kubernetes)
- Maintain backward compatibility for APIs
- Use structured logging with appropriate log levels

### Project Structure

```
.
├── services/              # Microservices
│   ├── api_gateway/       # API Gateway service
│   ├── hotel_service/     # Hotel management service
│   ├── user_service/      # User authentication service
│   └── booking_service/   # Booking management service
├── shared/                # Shared code across services
│   ├── models.py          # Pydantic models
│   ├── events.py          # Event schemas
│   ├── messaging.py       # RabbitMQ integration
│   ├── logging_config.py  # Structured logging setup
│   └── utils.py           # Utility functions
├── k8s/                   # Kubernetes manifests
│   ├── namespace.yaml
│   ├── message-broker/    # RabbitMQ deployment
│   ├── api-gateway/       # Gateway deployment
│   ├── hotel-service/     # Hotel service deployment
│   ├── user-service/      # User service deployment
│   └── booking-service/   # Booking service deployment
├── scripts/               # Automation scripts
│   ├── start_services.sh  # Start services
│   ├── stop_services.sh   # Stop services
│   ├── deploy_k8s.sh      # Kubernetes deployment
│   ├── init_data.sh       # Initialize sample data
│   └── test_services.sh   # Run tests
├── docker-compose.yml     # Docker Compose configuration
├── Pipfile                # Python dependencies
└── README.md              # This file
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->

## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->

## Contact

Project Link: [https://github.com/vijethph/college-assignments](https://github.com/vijethph/college-assignments)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->

## Acknowledgments

- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Excellent framework documentation
- [Kubernetes Documentation](https://kubernetes.io/docs/) - Comprehensive K8s guides
- [Docker Documentation](https://docs.docker.com/) - Container best practices
- [RabbitMQ Tutorials](https://www.rabbitmq.com/tutorials) - Message broker patterns
- [Microservices Patterns by Chris Richardson](https://microservices.io/) - Pattern catalog
- [Building Microservices by Sam Newman](https://www.oreilly.com/library/view/building-microservices-2nd/9781492034018/) - Design principles
- [Martin Fowler's Blog](https://martinfowler.com/) - Architectural insights
- [Best-README-Template](https://github.com/othneildrew/Best-README-Template) - README structure
- [Choose an Open Source License](https://choosealicense.com) - License guidance
- [Img Shields](https://shields.io) - README badges

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->

[contributors-shield]: https://img.shields.io/github/contributors/vijethph/college-assignments.svg?style=for-the-badge
[contributors-url]: https://github.com/vijethph/college-assignments/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/vijethph/college-assignments.svg?style=for-the-badge
[forks-url]: https://github.com/vijethph/college-assignments/network/members
[stars-shield]: https://img.shields.io/github/stars/vijethph/college-assignments.svg?style=for-the-badge
[stars-url]: https://github.com/vijethph/college-assignments/stargazers
[issues-shield]: https://img.shields.io/github/issues/vijethph/college-assignments.svg?style=for-the-badge
[issues-url]: https://github.com/vijethph/college-assignments/issues
[license-shield]: https://img.shields.io/github/license/vijethph/college-assignments.svg?style=for-the-badge
[license-url]: https://github.com/vijethph/college-assignments/blob/master/LICENSE.txt
[product-screenshot]: images/systemarchitecture.png
[Python.org]: https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/
[FastAPI.tiangolo.com]: https://img.shields.io/badge/FastAPI-0.104.1-009688?style=for-the-badge&logo=fastapi&logoColor=white
[FastAPI-url]: https://fastapi.tiangolo.com/
[Docker.com]: https://img.shields.io/badge/Docker-20.10+-2496ED?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://www.docker.com/
[Kubernetes.io]: https://img.shields.io/badge/Kubernetes-1.28-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white
[Kubernetes-url]: https://kubernetes.io/
[SQLAlchemy.org]: https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white
[SQLAlchemy-url]: https://www.sqlalchemy.org/
[RabbitMQ.com]: https://img.shields.io/badge/RabbitMQ-4.2-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white
[RabbitMQ-url]: https://www.rabbitmq.com/
