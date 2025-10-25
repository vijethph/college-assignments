# Redis Distributed System

## Setup

This project demonstrates Redis replication strategies and consistency models using a master-replica configuration with 3 nodes.

### Architecture

- 1 Redis Master (port 6379)
- 2 Redis Replicas (ports 6380, 6381)
- Python application container

### Prerequisites

- Docker
- Docker Compose

## Running the Demonstrations

```bash
docker-compose up -d --build
docker-compose logs -f python-app
```

### Stopping the cluster

```bash
docker-compose down -v
```

## Components

- Redis cluster with 1 master and 2 replicas
- Simple UserProfile data model
- Initial data insertion
- Write latency comparison with different replication factors
- Leader-follower (primary-backup) model demonstration
- Data propagation from master to replicas
- Write operations restricted to master
- Strong consistency using Redis WAIT command
- Eventual consistency demonstration
- Latency trade-offs between consistency levels

## Key Observations

1. Redis master-replica architecture provides strong consistency when using the WAIT command
2. Without WAIT, eventual consistency is observed with lower write latency
3. Write latency increases proportionally with the number of replicas to wait for
4. Leader-follower model ensures a single source of truth for writes
5. Replicas provide read scalability and fault tolerance

## Data Model

UserProfile:

- user_id: Unique identifier
- username: User's name
- email: Email address
- last_login_time: Timestamp of last login
