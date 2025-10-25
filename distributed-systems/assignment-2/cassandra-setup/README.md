## Distributed Systems - Cassandra Multi-Node Cluster

### Overview

Implementation of a 3-node Apache Cassandra cluster with Python client demonstrating:
- Replication strategies
- Consistency models
- CAP theorem trade-offs
- Network partition tolerance

### Quick Start

```bash
docker-compose up --build
```

### Components

- 3-node Cassandra cluster with RF=3
- UserProfile data model (user_id, username, email, last_login_time)
- Initial data insertion
- Optimized healthchecks (10s interval, 40s start period)

#### Replication Strategies
1. Write concern demonstration (ONE, QUORUM, ALL)
2. Leader-Follower: N/A (Cassandra is leaderless)
3. Leaderless multi-primary model demonstration

####  Consistency Models
1. Strong consistency with QUORUM (immediate consistency verification)
2. Eventual consistency with ONE (propagation demonstration)
3. Network partition/CAP theorem demonstration
4. Causal consistency: N/A (not natively supported)

### Testing

Run all experiments:
```bash
docker-compose up --build
```

Check cluster health:
```bash
docker exec -it cassandra-1 nodetool status
```

View application logs:
```bash
docker-compose logs python-app
```

Clean up:
```bash
docker-compose down -v
```