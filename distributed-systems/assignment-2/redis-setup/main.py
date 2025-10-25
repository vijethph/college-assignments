import redis
import time
import sys
from logger import setup_logging, logger

setup_logging()


class RedisClusterDemo:
    def __init__(self):
        self.master = redis.Redis(host="redis-master", port=6379, decode_responses=True)
        self.replica1 = redis.Redis(
            host="redis-replica1", port=6379, decode_responses=True
        )
        self.replica2 = redis.Redis(
            host="redis-replica2", port=6379, decode_responses=True
        )

    def wait_for_connections(self):
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                self.master.ping()
                self.replica1.ping()
                self.replica2.ping()
                logger.info("all redis nodes connected")
                return True
            except Exception as e:
                logger.warning(
                    "connection attempt failed", attempt=attempt + 1, error=str(e)
                )
                time.sleep(2)
        logger.error("failed to connect to redis")
        return False

    def setup_initial_data(self):
        users = [
            {
                "user_id": "1",
                "username": "alice",
                "email": "alice@example.com",
                "last_login_time": "2025-10-25T10:00:00Z",
            },
            {
                "user_id": "2",
                "username": "bob",
                "email": "bob@example.com",
                "last_login_time": "2025-10-25T11:00:00Z",
            },
            {
                "user_id": "3",
                "username": "charlie",
                "email": "charlie@example.com",
                "last_login_time": "2025-10-25T12:00:00Z",
            },
        ]

        for user in users:
            key = f"user:{user['user_id']}"
            self.master.hset(key, mapping=user)
            logger.info(
                "user_created", user_id=user["user_id"], username=user["username"]
            )

        time.sleep(1)
        logger.info("initial data setup complete")

    def demonstrate_replication(self):
        logger.info("demonstrating replication")

        test_key = "user:100"
        test_data = {
            "user_id": "100",
            "username": "testuser",
            "email": "test@example.com",
            "last_login_time": "2025-10-25T15:00:00Z",
        }

        logger.info("writing to master", key=test_key)
        write_start = time.time()
        self.master.hset(test_key, mapping=test_data)
        write_time = time.time() - write_start
        logger.info("write completed", write_time_ms=round(write_time * 1000, 2))

        time.sleep(0.5)

        replica1_data = self.replica1.hgetall(test_key)
        logger.info("replica1 read", data=replica1_data)

        replica2_data = self.replica2.hgetall(test_key)
        logger.info("replica2 read", data=replica2_data)

    def demonstrate_strong_consistency(self):
        logger.info("demonstrating strong consistency")

        test_key = "strong:test:1"
        value = f"strong_value_{int(time.time())}"

        logger.info(
            "writing to master for strong consistency", key=test_key, value=value
        )
        write_start = time.time()
        self.master.set(test_key, value)
        result = self.master.wait(2, 1000)
        write_time = time.time() - write_start
        logger.info(
            "strong write completed",
            replicas_synced=result,
            write_time_ms=round(write_time * 1000, 2),
        )

        logger.info("immediately reading from replica")
        read_value = self.replica1.get(test_key)
        logger.info(
            "strong consistency read",
            expected=value,
            actual=read_value,
            consistent=read_value == value,
        )

    def demonstrate_eventual_consistency(self):
        logger.info("demonstrating eventual consistency")

        test_key = "eventual:test:1"
        value = f"eventual_value_{int(time.time())}"

        logger.info(
            "writing to master for eventual consistency", key=test_key, value=value
        )
        write_start = time.time()
        self.master.set(test_key, value)
        write_time = time.time() - write_start
        logger.info(
            "eventual write completed", write_time_ms=round(write_time * 1000, 2)
        )

        logger.info("immediately reading from replica without wait")
        read_value = self.replica1.get(test_key)
        is_consistent = read_value == value
        logger.info(
            "immediate read result",
            expected=value,
            actual=read_value,
            consistent=is_consistent,
        )

        if not is_consistent:
            logger.info("demonstrating eventual convergence")
            max_attempts = 10
            for attempt in range(max_attempts):
                time.sleep(0.1)
                read_value = self.replica1.get(test_key)
                logger.info(
                    "convergence attempt",
                    attempt=attempt + 1,
                    value=read_value,
                    consistent=read_value == value,
                )
                if read_value == value:
                    logger.info("eventual consistency achieved", attempts=attempt + 1)
                    break

    def demonstrate_write_latency(self):
        logger.info("demonstrating write latency with different concerns")

        logger.info("testing write without wait")
        key1 = "latency:test:1"
        start = time.time()
        self.master.set(key1, "value1")
        time_no_wait = time.time() - start
        logger.info(
            "write without wait completed", latency_ms=round(time_no_wait * 1000, 2)
        )

        logger.info("testing write with wait for 1 replica")
        key2 = "latency:test:2"
        start = time.time()
        self.master.set(key2, "value2")
        self.master.wait(1, 1000)
        time_wait_1 = time.time() - start
        logger.info(
            "write with 1 replica wait completed",
            latency_ms=round(time_wait_1 * 1000, 2),
        )

        logger.info("testing write with wait for 2 replicas")
        key3 = "latency:test:3"
        start = time.time()
        self.master.set(key3, "value3")
        self.master.wait(2, 1000)
        time_wait_2 = time.time() - start
        logger.info(
            "write with 2 replicas wait completed",
            latency_ms=round(time_wait_2 * 1000, 2),
        )

        logger.info(
            "write latency comparison",
            no_wait_ms=round(time_no_wait * 1000, 2),
            wait_1_replica_ms=round(time_wait_1 * 1000, 2),
            wait_2_replicas_ms=round(time_wait_2 * 1000, 2),
        )

    def demonstrate_leader_follower_model(self):
        logger.info("demonstrating leader follower model")

        test_key = "leader:test:1"
        value = "leader_value"

        logger.info("writing to master", key=test_key)
        self.master.set(test_key, value)

        time.sleep(0.5)

        logger.info("reading from replicas to verify propagation")
        replica1_val = self.replica1.get(test_key)
        replica2_val = self.replica2.get(test_key)
        logger.info(
            "propagation verified", replica1=replica1_val, replica2=replica2_val
        )

        logger.info("attempting write to replica")
        try:
            self.replica1.set("test:readonly", "value")
            logger.warning("replica write succeeded unexpectedly")
        except Exception as e:
            if "READONLY" in str(e):
                logger.info("replica correctly rejected write operation")
            else:
                logger.info("replica write behavior", error=str(e))

    def run_all_demonstrations(self):
        logger.info("starting redis cluster demonstrations")

        if not self.wait_for_connections():
            logger.error("cannot proceed without connections")
            sys.exit(1)

        self.setup_initial_data()

        self.demonstrate_replication()
        self.demonstrate_write_latency()
        self.demonstrate_leader_follower_model()

        self.demonstrate_strong_consistency()
        self.demonstrate_eventual_consistency()


if __name__ == "__main__":
    demo = RedisClusterDemo()
    demo.run_all_demonstrations()
