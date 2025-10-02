# Socket Client-Server Application

Simple socket-based client-server application in Python.

## System Design & Architecture

### Overview

This application demonstrates synchronous TCP socket communication between a client and server using Python's built-in socket library. The system follows a traditional client-server architecture where:

- Server: Listens on localhost:8080 and handles multiple concurrent clients using threading
- Client: Connects to server and sends messages synchronously, waiting for responses
- Communication: Uses TCP protocol for reliable, ordered message delivery

### Synchronous Communication

The system demonstrates synchronous communication where:

1. Client sends a message and blocks until server response
2. Server processes each message sequentially per client thread
3. Request-response cycle completes before next message can be sent
4. No asynchronous callbacks or event loops - pure blocking I/O

## Files

- `server.py` - TCP socket server
- `client.py` - TCP socket client
- `test_server.py` - Basic test
- `socket_server.py` - WebSocket server
- `socket_client.html` - WebSocket client

## Usage

Start server:

```bash
python server.py
```

Start client:

```bash
python client.py
```

Run test:

```bash
python test_server.py
```

## Commands

- `hello` - Get greeting
- `quit` - Exit
- Any other text - Echo response
