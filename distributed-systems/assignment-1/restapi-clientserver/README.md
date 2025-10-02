# FastAPI Users REST API

A simple FastAPI server for CRUD operations on users with SQLite database demonstrating synchronous client-server communication patterns.

## System Design & Architecture

### Communication Model

The system demonstrates synchronous communication through:

- HTTP Request-Response Pattern: Each client request receives an immediate response
- Blocking Operations: Database operations complete before responding to the client
- Sequential Processing: Requests are processed one after another in the order received
- Direct Communication: No message queues or asynchronous processing involved

### Architecture Components

#### 1. API Layer (FastAPI)

- Handles HTTP requests and responses
- Performs request validation using Pydantic models
- Manages routing and endpoint definitions
- Returns structured JSON responses with appropriate HTTP status codes

#### 2. Business Logic Layer

- Implements CRUD operations for user management
- Enforces business rules (automatic ID generation, data validation)
- Handles error scenarios and exception management
- Manages data transformation between API and database models

#### 3. Data Access Layer (SQLModel + SQLite)

- Provides ORM-based database interactions
- Handles database session management
- Ensures data persistence and transaction integrity
- Implements database schema definition and migrations

#### 4. Data Models

- UserBase: Common fields shared across operations
- UserCreate: Input model for user creation (excludes ID)
- UserUpdate: Partial update model with optional fields
- User: Complete database model with auto-generated ID

### Synchronous Communication Demonstration

#### Request Flow

1. Client sends HTTP request to server
2. FastAPI receives and validates the request
3. Business logic processes the request synchronously
4. Database operation executes and completes
5. Response is formatted and sent back to client
6. Client receives complete response before proceeding

#### Blocking Nature

- Each database operation blocks until completion
- Server processes one request at a time per worker
- Client waits for complete response before next action
- No callbacks, promises, or async/await patterns used

#### Error Handling

- Immediate error responses with appropriate HTTP status codes
- Synchronous exception propagation
- Clear error messages in response body

### Data Flow Architecture

```
Client Request → FastAPI Router → Pydantic Validation → Business Logic → SQLModel/SQLAlchemy → SQLite Database
                                                                                              ↓
Client Response ← JSON Serialization ← Response Model ← Data Processing ← Query Results ← Database Response
```

### Scalability Considerations

While this system uses synchronous communication, it provides:

- Horizontal Scaling: Multiple container instances can run behind a load balancer
- Connection Pooling: SQLAlchemy manages database connections efficiently
- Stateless Design: Each request is independent, enabling easy scaling
- Resource Predictability: Synchronous operations provide predictable resource usage

## Features

- Create, Read, Update, Delete users
- SQLite database with SQLModel
- Automatic ID generation
- Health check endpoint
- Docker support
- Comprehensive test suite
- Synchronous request-response communication

## Quick Start with Docker

### Using Docker Compose

```bash
docker-compose up --build

docker-compose up -d --build

docker-compose down
```

### Using Docker directly

```bash
docker build -t fastapi-users .

docker run -p 8000:8000 -v $(pwd)/data:/app/data fastapi-users
```

## API Endpoints

- `GET /healthcheck` - Health check
- `POST /users/` - Create a new user
- `GET /users/` - Get all users (with pagination)
- `GET /users/{user_id}` - Get a specific user
- `PATCH /users/{user_id}` - Update a user
- `DELETE /users/{user_id}` - Delete a user

## Access the API

Once running, visit:

- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/healthcheck

## Example Usage

### Create a user:

```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "age": 30,
    "email": "john@example.com"
  }'
```

### Get all users:

```bash
curl -X GET "http://localhost:8000/users/"
```

### Update a user:

```bash
curl -X PATCH "http://localhost:8000/users/1" \
  -H "Content-Type: application/json" \
  -d '{"age": 31}'
```
