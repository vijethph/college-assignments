import time
from cassandra.query import SimpleStatement, ConsistencyLevel
from cassandra import Unavailable, WriteTimeout, ReadTimeout
from config import INSERT_QUERY, SELECT_BY_ID_QUERY
from logger import logger
import uuid
from datetime import datetime

def test_partition_tolerance(session):
    logger.info("cap_theorem_demonstration_start")

    test_id = uuid.uuid4()
    write_stmt = SimpleStatement(INSERT_QUERY, consistency_level=ConsistencyLevel.QUORUM)

    try:
        session.execute(write_stmt, (test_id, 'cap_test', 'cap@test.com', datetime.now()))
        logger.info("write_successful_with_quorum")

        read_stmt = SimpleStatement(SELECT_BY_ID_QUERY, consistency_level=ConsistencyLevel.QUORUM)
        result = session.execute(read_stmt, (test_id,))
        row = result.one()

        if row:
            logger.info("read_successful_with_quorum", username=row.username)

    except (Unavailable, WriteTimeout, ReadTimeout) as e:
        logger.error("operation_failed_due_to_unavailability",
                    error=str(e),
                    cap_implication="System chose Consistency over Availability")

    return test_id
