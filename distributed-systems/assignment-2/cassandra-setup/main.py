import time
from logger import setup_logging, logger
from database import get_cluster_connection, setup_keyspace, setup_schema
from data_loader import insert_initial_data
from replication_demo import demonstrate_write_concerns
from leaderless_demo import demonstrate_leaderless_writes
from consistency_demo import demonstrate_strong_consistency, demonstrate_eventual_consistency
from partition_demo import test_partition_tolerance
from config import SELECT_ALL_QUERY

def main():
    setup_logging()

    logger.info("--- Part A: Setup & Baseline -----")
    cluster, session = get_cluster_connection()
    setup_keyspace(session)
    setup_schema(session)
    insert_initial_data(session)

    logger.info("--- Part B: Replication Strategies -----")
    demonstrate_write_concerns(session)

    leaderless_clusters, leaderless_sessions = demonstrate_leaderless_writes()

    time.sleep(1)
    rows = session.execute(SELECT_ALL_QUERY)
    count = len(list(rows))
    logger.info("total_records_after_multi_node_writes", count=count)

    logger.info("--- Part C: Consistency Models -----")
    demonstrate_strong_consistency(session)
    demonstrate_eventual_consistency(session, leaderless_sessions[1])

    test_partition_tolerance(session)

    cluster.shutdown()
    for c in leaderless_clusters:
        c.shutdown()

if __name__ == "__main__":
    main()
