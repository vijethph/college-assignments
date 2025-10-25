CASSANDRA_NODES = ['cassandra-1', 'cassandra-2', 'cassandra-3']
CASSANDRA_PORT = 9042
KEYSPACE = 'fakehealthcareorg'
REPLICATION_FACTOR = 3

INSERT_QUERY = "INSERT INTO userprofile (user_id, username, email, last_login_time) VALUES (%s, %s, %s, %s)"
SELECT_ALL_QUERY = "SELECT * FROM userprofile"
SELECT_BY_ID_QUERY = "SELECT * FROM userprofile WHERE user_id = %s"
