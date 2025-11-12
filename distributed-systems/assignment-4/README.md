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
    A cloud-native microservices architecture demonstrating distributed systems principles
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

This project demonstrates a production-grade microservices architecture for a hotel booking and reservation system.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

- **Python 3.11** - Modern async/await support
- **FastAPI** - High-performance web framework with automatic OpenAPI docs
- **SQLAlchemy** - SQL toolkit and ORM
- **SQLite** - Lightweight per-service database
- **structlog** - Structured logging with JSON formatting
- **aiohttp** - Async HTTP client for API Gateway
- **requests** - Synchronous HTTP client for Booking Service
- **python-jose** - JWT token handling
- **passlib** - Secure password hashing (bcrypt)
- **Docker** - Container runtime
- **Kubernetes** - Container orchestration (Minikube)
- **pipenv** - Dependency management

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

### Installation

1. Clone the repository

   ```sh
   git clone https://github.com/vijethph/college-assignments.git
   cd distributed-systems/assignment-4
   ```

2. Install Python dependencies

   ```sh
   mkdir .venv
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

5. Start all services (Local mode)

   ```sh
   ./scripts/start_services.sh local
   ```

6. Initialize sample data (in a new terminal)

   ```sh
   ./scripts/init_data.sh local
   ```

7. Verify services are running
   ```sh
   ./scripts/test_services.sh local
   ```

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

**3. Create a Booking**

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

**4. View User Bookings**

```bash
curl http://localhost:8000/api/bookings/user/1
```

**5. Cancel a Booking**

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

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- DEPLOYMENT -->

## Deployment

The project supports three deployment modes with unified scripts.

### Local Development

Perfect for rapid development and testing:

```bash
# Start all services
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

# Stop services
./scripts/stop_services.sh docker
```

**Docker features:**

- Health checks for automatic recovery
- Volume persistence for databases
- Network isolation
- Resource limits

### Kubernetes Deployment

Production-ready orchestration with Kubernetes:

```bash
# Start Minikube (if not running)
minikube start

# Deploy all services
./scripts/start_services.sh kubernetes hotel-booking

# Or use the dedicated deployment script
./scripts/deploy_k8s.sh

# Initialize data
./scripts/init_data.sh kubernetes hotel-booking

# Run tests
./scripts/test_services.sh kubernetes hotel-booking

# Check status
./scripts/k8s_status.sh

# Get API Gateway URL
minikube service api-gateway -n hotel-booking --url

# View logs
kubectl logs -f deployment/api-gateway -n hotel-booking

# Scale services
kubectl scale deployment booking-service --replicas=3 -n hotel-booking

# Clean up
./scripts/cleanup_k8s.sh
```

**Kubernetes features:**

- High availability with multiple replicas
- Automatic self-healing with health probes
- Rolling updates with zero downtime
- Service discovery via Kubernetes DNS
- Persistent volumes for data storage
- Resource limits and requests
- ConfigMaps for environment configuration

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- API REFERENCE -->

## API Reference

### API Gateway Endpoints

**Base URL:** `http://localhost:8000` (Local/Docker) or `http://<minikube-ip>:30000` (Kubernetes)

| Method | Endpoint                    | Description                                 |
| ------ | --------------------------- | ------------------------------------------- |
| GET    | `/health`                   | Gateway health check                        |
| GET    | `/api/hotels`               | List hotels (proxied to Hotel Service)      |
| GET    | `/api/hotels/{id}`          | Get hotel details                           |
| POST   | `/api/users/register`       | Register user (proxied to User Service)     |
| POST   | `/api/users/login`          | User login                                  |
| POST   | `/api/bookings`             | Create booking (proxied to Booking Service) |
| GET    | `/api/bookings/user/{id}`   | Get user bookings                           |
| PUT    | `/api/bookings/{id}/cancel` | Cancel booking                              |

### Hotel Service Endpoints

**Base URL:** `http://localhost:8001`

| Method | Endpoint                                          | Description                    |
| ------ | ------------------------------------------------- | ------------------------------ |
| GET    | `/health`                                         | Service health check           |
| GET    | `/hotels`                                         | List all hotels                |
| GET    | `/hotels/{hotel_id}`                              | Get hotel by ID                |
| GET    | `/hotels/{hotel_id}/rooms`                        | Get hotel rooms                |
| POST   | `/hotels/{hotel_id}/rooms/check-availability`     | Check room availability        |
| PUT    | `/hotels/{hotel_id}/rooms/{room_id}/availability` | Update availability (internal) |

**Query Parameters:**

- `/hotels`: `location`, `min_rating`
- `/hotels/{hotel_id}/rooms`: `room_type`, `min_capacity`, `max_price`

### User Service Endpoints

**Base URL:** `http://localhost:8002`

| Method | Endpoint           | Description             |
| ------ | ------------------ | ----------------------- |
| GET    | `/health`          | Service health check    |
| POST   | `/users/register`  | Register new user       |
| POST   | `/users/login`     | Login and get JWT token |
| GET    | `/users/{user_id}` | Get user profile        |
| PUT    | `/users/{user_id}` | Update user profile     |

### Booking Service Endpoints

**Base URL:** `http://localhost:8003`

| Method | Endpoint                        | Description          |
| ------ | ------------------------------- | -------------------- |
| GET    | `/health`                       | Service health check |
| POST   | `/bookings`                     | Create new booking   |
| GET    | `/bookings/{booking_id}`        | Get booking details  |
| GET    | `/bookings/user/{user_id}`      | Get user's bookings  |
| PUT    | `/bookings/{booking_id}/cancel` | Cancel booking       |

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
- [Microservices Patterns by Chris Richardson](https://microservices.io/) - Pattern catalog
- [Building Microservices by Sam Newman](https://www.oreilly.com/library/view/building-microservices-2nd/9781492034018/) - Design principles
- [Martin Fowler's Blog](https://martinfowler.com/) - Architectural insights
- [Best-README-Template](https://github.com/othneildrew/Best-README-Template) - README structure
- [Choose an Open Source License](https://choosealicense.com) - License guidance
- [Img Shields](https://shields.io) - README badges

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->

[contributors-shield]: https://img.shields.io/github/contributors/yourusername/microservices-assignment.svg?style=for-the-badge
[contributors-url]: https://github.com/vijethph/college-assignments/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/yourusername/microservices-assignment.svg?style=for-the-badge
[forks-url]: https://github.com/vijethph/college-assignments/network/members
[stars-shield]: https://img.shields.io/github/stars/yourusername/microservices-assignment.svg?style=for-the-badge
[stars-url]: https://github.com/vijethph/college-assignments/stargazers
[issues-shield]: https://img.shields.io/github/issues/yourusername/microservices-assignment.svg?style=for-the-badge
[issues-url]: https://github.com/vijethph/college-assignments/issues
[license-shield]: https://img.shields.io/github/license/yourusername/microservices-assignment.svg?style=for-the-badge
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

