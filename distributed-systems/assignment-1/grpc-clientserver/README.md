# gRPC User Management System

A simple gRPC-based user management system implementing CRUD operations with SQLite database storage.

## System Design

### Architecture Overview

The system follows a client-server architecture using gRPC for synchronous communication between components:

- Server: Python gRPC server implementing user management operations
- Database: SQLite database for persistent user data storage
- Client: Python gRPC client for interacting with the server
- Protocol: Protocol Buffers (protobuf) for message serialization

### Components

#### Server (`server.py`)

- Implements `UserServiceServicer` with CRUD operations
- Uses SQLite database for data persistence
- Handles concurrent requests using ThreadPoolExecutor
- Provides error handling for database constraints and missing records

#### Database Layer

- SQLite database with users table (id, name, email, age)
- Database abstraction class for all SQL operations
- Automatic table creation on startup
- Unique email constraint enforcement

#### Protocol Definition (`proto/user_service.proto`)

- Defines User message structure
- Specifies request/response messages for each operation
- Declares UserService with 5 RPC methods

#### Generated Code (`generated/`)

- Auto-generated Python code from protobuf definitions
- Contains message classes and service stubs

## Synchronous Communication

### gRPC Synchronous Model

The system demonstrates synchronous communication through:

1. Request-Response Pattern: Each client request blocks until server responds
2. Immediate Feedback: Operations return success/failure status immediately
3. Error Propagation: Database errors and validation failures are communicated back to client
4. Sequential Operations: Client waits for each operation to complete before proceeding

### Communication Flow

```
Client Request → gRPC Channel → Server Processing → Database Operation → Response → Client
```

Each operation follows this synchronous flow:

- Client makes RPC call and waits
- Server processes request synchronously
- Database operation completes before response
- Client receives complete result before continuing

## API Operations

- CreateUser: Creates new user with validation
- GetUser: Retrieves user by ID
- UpdateUser: Updates existing user information
- DeleteUser: Removes user from database
- ListUsers: Returns all users in system

## Running the System

### Local Development

```bash
python server.py

python client.py

pytest test_grpc.py -v
```

### Docker Deployment

```bash
docker-compose up --build
```

## Testing

The system includes comprehensive tests covering:

- Service method invocation
- Data serialization/deserialization
- Error handling scenarios
- Database constraint validation

Each test demonstrates synchronous communication by verifying immediate responses to client requests.
