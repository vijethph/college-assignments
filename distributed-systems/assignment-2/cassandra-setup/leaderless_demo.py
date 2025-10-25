import uuid
from datetime import datetime
from cassandra.cluster import Cluster
from config import INSERT_QUERY, CASSANDRA_PORT, KEYSPACE
from logger import logger

def demonstrate_leaderless_writes():
    logger.info("leaderless_model_demonstration_start")

    clusters = []
    sessions = []

    for i, node in enumerate(['cassandra-1', 'cassandra-2', 'cassandra-3'], 1):
        cluster = Cluster([node], port=CASSANDRA_PORT)
        session = cluster.connect(KEYSPACE)

        user_id = uuid.uuid4()
        session.execute(INSERT_QUERY, (user_id, f'node{i}_write', f'node{i}@example.com', datetime.now()))

        logger.info("write_to_node_completed", node=node)

        clusters.append(cluster)
        sessions.append(session)

    return clusters, sessions
