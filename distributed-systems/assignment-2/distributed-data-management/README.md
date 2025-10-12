# MongoDB Replica Set

A production-ready MongoDB replica set implementation with 3 nodes, demonstrating distributed database concepts including replication, write concerns, and automatic failover.

## About The Project

This project implements a distributed MongoDB cluster using replica sets to provide high availability, data redundancy, and automatic failover capabilities. The system consists of three MongoDB nodes configured in a primary-backup replication model with keyfile authentication.

Key features:

- Three-node MongoDB 8 replica set
- Automated initialization and configuration
- Keyfile-based authentication between nodes
- Write concern demonstrations (w=1, w=2, w=majority, w=3)
- Read preference examples (PRIMARY, SECONDARY, NEAREST)
- Automatic primary failover and recovery
- Python client application with CRUD operations
- Docker-based deployment for easy setup

### Built With

- [MongoDB 8](https://www.mongodb.com/) - NoSQL database
- [Python 3.11](https://www.python.org/) - Client application
- [PyMongo](https://pymongo.readthedocs.io/) - MongoDB driver for Python
- [Docker](https://www.docker.com/) - Containerization platform
- [Docker Compose](https://docs.docker.com/compose/) - Multi-container orchestration

## Getting Started

### Prerequisites

- Docker Engine 20.10+
- Docker Compose v2.0+
- Python 3.11+ (for local development)
- Pipenv (Python dependency management)

### Installation

1. Clone the repository

   ```bash
   git clone https://github.com/vijethph/college-assignments.git
   cd assignment-2/distributed-data-management
   ```

2. Start the MongoDB cluster

   ```bash
   docker compose up -d
   ```

3. Wait for initialization (30-60 seconds)

   ```bash
   docker compose logs -f mongo1
   ```

4. Install Python dependencies

   ```bash
   pipenv install
   ```

5. Verify cluster status
   ```bash
   pipenv run python main.py --status
   ```

## Usage

### Basic Operations

Run the complete demonstration:

```bash
pipenv run python main.py
```

### Individual Components

**CRUD Operations:**

```bash
pipenv run python main.py --part-a
```

**Write Concern Levels:**

```bash
pipenv run python main.py --part-b1
```

**Replication and Failover:**

```bash
pipenv run python main.py --part-b2
```

**Consistency Models:**

```bash
# All consistency demonstrations
pipenv run python main.py --part-c

# Strong consistency only
pipenv run python main.py --part-c1

# Eventual consistency only
pipenv run python main.py --part-c2
```

**Check Cluster Status:**

```bash
pipenv run python main.py --status
```

### Testing Failover

Simulate a primary node failure:

```bash
# 1. Check current primary
pipenv run python main.py --status

# 2. Stop the primary node (e.g., mongo1)
docker compose stop mongo1

# 3. Wait 10-30 seconds for election

# 4. Verify new primary
pipenv run python main.py --check-failover

# 5. Restart the stopped node
docker compose start mongo1
```

### Configuration

The default connection string can be overridden via environment variable:

```bash
export MONGODB_URI="mongodb://admin:admin123@localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0&authSource=admin"
pipenv run python main.py
```

## Architecture

### Cluster Topology

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   mongo1    │────▶│   mongo2    │────▶│   mongo3    │
│  PRIMARY    │     │  SECONDARY  │     │  SECONDARY  │
│  Port 27017 │     │  Port 27018 │     │  Port 27019 │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       └───────────────────┴───────────────────┘
                    Replica Set: rs0
```

### Replication Model

- **Primary Node:** Handles all write operations
- **Secondary Nodes:** Replicate data asynchronously from primary
- **Automatic Failover:** New primary elected if current primary fails
- **Election Time:** 10-30 seconds typical
- **Data Durability:** Configurable via write concerns

### Write Concerns

| Level      | Description             | Use Case                            | Typical Latency |
| ---------- | ----------------------- | ----------------------------------- | --------------- |
| w=1        | Primary only            | Fast writes, can tolerate data loss | 5-10ms          |
| w=2        | Primary + 1 secondary   | Balanced durability                 | 10-20ms         |
| w=majority | Majority of nodes (2/3) | Production recommended              | 15-25ms         |
| w=3        | All nodes               | Maximum durability                  | 20-30ms         |

### Read Preferences

- **PRIMARY:** Read from primary (always consistent)
- **SECONDARY:** Read from secondary (eventual consistency)
- **NEAREST:** Read from nearest node (lowest latency)

### Consistency Models

**Strong Consistency:**

- Write Concern: `w=majority`
- Read Preference: `PRIMARY`
- Guarantees: Reads always see latest committed writes
- Trade-off: May block during network partitions (CP in CAP theorem)

**Eventual Consistency:**

- Write Concern: `w=1`
- Read Preference: `SECONDARY`
- Guarantees: High availability and performance
- Trade-off: May read stale data temporarily
- Use Cases: Social media feeds, analytics, view counts

## Project Structure

```
.
├── main.py                 # Main application with all demonstrations
├── init_replica_set.py     # Replica set status checker utility
├── docker-compose.yml      # Multi-container orchestration
├── mongo-init.sh          # Automated MongoDB initialization
├── Dockerfile             # Python application container
├── Pipfile                # Python dependencies
└── speaker-notes.md       # Presentation guide
```

## Data Model

The UserProfile collection schema:

```python
{
    'user_id': str,              # Unique identifier
    'username': str,             # Username
    'email': str,                # Email address
    'last_login_time': datetime, # Last login timestamp (UTC)
    'created_at': datetime       # Creation timestamp (UTC)
}
```

## Performance Considerations

- **Write Latency:** Increases with higher write concerns
- **Read Scaling:** Distribute reads across secondaries
- **Replication Lag:** Typically <10ms in same datacenter
- **Failover Time:** 10-30 seconds for election
- **Network:** Cluster should be in same network for low latency

## Security Notes

**Default Credentials (Development Only):**

- Username: `admin`
- Password: `admin123`

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Acknowledgments

- [MongoDB Documentation](https://docs.mongodb.com/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [Docker Documentation](https://docs.docker.com/)
- [Raft Consensus Algorithm](https://raft.github.io/)
