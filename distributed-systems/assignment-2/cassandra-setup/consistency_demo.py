import uuid
from datetime import datetime
import time
from cassandra.query import SimpleStatement, ConsistencyLevel
from config import INSERT_QUERY, SELECT_BY_ID_QUERY
from logger import logger

def demonstrate_strong_consistency(session):
    logger.info("strong_consistency_demonstration_start")

    test_id_strong = uuid.uuid4()
    write_stmt = SimpleStatement(INSERT_QUERY, consistency_level=ConsistencyLevel.QUORUM)
    session.execute(write_stmt, (test_id_strong, 'strong_test', 'strong@test.com', datetime.now()))
    logger.info("written_with_consistency", level="QUORUM")

    read_stmt = SimpleStatement(SELECT_BY_ID_QUERY, consistency_level=ConsistencyLevel.QUORUM)
    result = session.execute(read_stmt, (test_id_strong,))
    row = result.one()

    if row:
        logger.info("immediate_read_successful", username=row.username, consistent=True)

    return test_id_strong

def demonstrate_eventual_consistency(session, session_2):
    logger.info("eventual_consistency_demonstration_start")

    test_id_eventual = uuid.uuid4()
    write_eventual = SimpleStatement(INSERT_QUERY, consistency_level=ConsistencyLevel.ONE)
    session.execute(write_eventual, (test_id_eventual, 'eventual_test', 'eventual@test.com', datetime.now()))
    logger.info("written_with_consistency", level="ONE")

    read_eventual = SimpleStatement(SELECT_BY_ID_QUERY, consistency_level=ConsistencyLevel.ONE)

    max_attempts = 10
    for i in range(max_attempts):
        result = session_2.execute(read_eventual, (test_id_eventual,))
        row = result.one()
        if row:
            logger.info("read_successful", attempt=i+1, username=row.username)
            break
        else:
            logger.info("data_not_yet_propagated", attempt=i+1)
            time.sleep(0.1)

    return test_id_eventual
