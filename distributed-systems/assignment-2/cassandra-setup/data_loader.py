import uuid
from datetime import datetime
from config import INSERT_QUERY
from logger import logger

def insert_initial_data(session):
    user_id_1 = uuid.uuid4()
    user_id_2 = uuid.uuid4()

    session.execute(INSERT_QUERY, (user_id_1, 'alice', 'alice@example.com', datetime.now()))
    session.execute(INSERT_QUERY, (user_id_2, 'bob', 'bob@example.com', datetime.now()))

    logger.info("initial_data_inserted", users=['alice', 'bob'])
    return user_id_1, user_id_2
