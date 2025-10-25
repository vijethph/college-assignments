from cassandra.cluster import Cluster
from config import CASSANDRA_NODES, CASSANDRA_PORT, KEYSPACE, REPLICATION_FACTOR
from logger import logger

def get_cluster_connection(nodes=None):
    if nodes is None:
        nodes = CASSANDRA_NODES
    cluster = Cluster(nodes, port=CASSANDRA_PORT)
    session = cluster.connect()
    return cluster, session

def setup_keyspace(session):
    session.execute(f"""
        CREATE KEYSPACE IF NOT EXISTS {KEYSPACE}
        WITH REPLICATION = {{ 'class' : 'SimpleStrategy', 'replication_factor' : {REPLICATION_FACTOR} }}
    """)
    session.set_keyspace(KEYSPACE)
    logger.info("keyspace_setup_complete", keyspace=KEYSPACE)

def setup_schema(session):
    session.execute("""
        CREATE TABLE IF NOT EXISTS userprofile (
            user_id UUID PRIMARY KEY,
            username TEXT,
            email TEXT,
            last_login_time TIMESTAMP
        )
    """)
    logger.info("schema_setup_complete", table="userprofile")
