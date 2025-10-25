import uuid
from datetime import datetime
import time
from cassandra.query import SimpleStatement, ConsistencyLevel
from config import INSERT_QUERY
from logger import logger

def demonstrate_write_concerns(session):
    logger.info("write_concern_demonstration_start")

    user_id_test = uuid.uuid4()
    stmt_one = SimpleStatement(INSERT_QUERY, consistency_level=ConsistencyLevel.ONE)
    start = time.time()
    session.execute(stmt_one, (user_id_test, 'test_one', 'test@one.com', datetime.now()))
    latency_one = (time.time() - start) * 1000
    logger.info("write_with_consistency", level="ONE", latency_ms=f"{latency_one:.2f}")

    user_id_test = uuid.uuid4()
    stmt_quorum = SimpleStatement(INSERT_QUERY, consistency_level=ConsistencyLevel.QUORUM)
    start = time.time()
    session.execute(stmt_quorum, (user_id_test, 'test_quorum', 'test@quorum.com', datetime.now()))
    latency_quorum = (time.time() - start) * 1000
    logger.info("write_with_consistency", level="QUORUM", latency_ms=f"{latency_quorum:.2f}")

    user_id_test = uuid.uuid4()
    stmt_all = SimpleStatement(INSERT_QUERY, consistency_level=ConsistencyLevel.ALL)
    start = time.time()
    session.execute(stmt_all, (user_id_test, 'test_all', 'test@all.com', datetime.now()))
    latency_all = (time.time() - start) * 1000
    logger.info("write_with_consistency", level="ALL", latency_ms=f"{latency_all:.2f}")
