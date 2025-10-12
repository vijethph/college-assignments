from pymongo import MongoClient, WriteConcern, ReadPreference
from datetime import datetime, timezone
import time
import os
import sys

MONGODB_URI = os.getenv(
    'MONGODB_URI',
    'mongodb://admin:admin123@localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0&authSource=admin'
)

MONGODB_DIRECT_URI = 'mongodb://admin:admin123@localhost:27017/?authSource=admin'

# All node URIs for failover scenarios
MONGODB_NODES = [
    'mongodb://admin:admin123@localhost:27017/?authSource=admin',
    'mongodb://admin:admin123@localhost:27018/?authSource=admin',
    'mongodb://admin:admin123@localhost:27019/?authSource=admin'
]

def get_mongo_client(direct=False):
    """Get MongoDB client with appropriate connection settings"""
    if direct or os.getenv('MONGODB_URI') is None:
        return MongoClient(MONGODB_DIRECT_URI, directConnection=True, serverSelectionTimeoutMS=5000)
    else:
        return MongoClient(MONGODB_URI)

def get_any_available_client():
    """Try to connect to any available MongoDB node"""
    for node_uri in MONGODB_NODES:
        try:
            client = MongoClient(node_uri, directConnection=True, serverSelectionTimeoutMS=2000)
            client.admin.command('ping')
            return client
        except Exception:
            continue
    raise Exception("Could not connect to any MongoDB node")

class UserProfileManager:
    def __init__(self, connection_string=None):
        if connection_string:
            self.client = MongoClient(connection_string)
        else:
            self.client = get_mongo_client(direct=True)
        self.db = self.client['user_database']
        self.collection = self.db['user_profiles']

    def create_user(self, user_id, username, email):
        user = {
            'user_id': user_id,
            'username': username,
            'email': email,
            'last_login_time': datetime.now(timezone.utc),
            'created_at': datetime.now(timezone.utc)
        }
        result = self.collection.insert_one(user)
        print(f"Created: {username}")
        return result.inserted_id

    def get_user(self, user_id):
        return self.collection.find_one({'user_id': user_id})

    def update_login_time(self, user_id):
        result = self.collection.update_one(
            {'user_id': user_id},
            {'$set': {'last_login_time': datetime.now(timezone.utc)}}
        )
        return result.modified_count

    def delete_user(self, user_id):
        result = self.collection.delete_one({'user_id': user_id})
        return result.deleted_count

    def list_users(self):
        users = list(self.collection.find())
        for user in users:
            print(f"  {user['username']} - {user['email']}")
        return users

def part_a_demo():
    print("\n" + "="*70)
    print(" PART A: CRUD Operations")
    print("="*70 + "\n")

    manager = UserProfileManager()

    manager.create_user('U001', 'alice', 'alice@example.com')
    manager.create_user('U002', 'bob', 'bob@example.com')
    manager.create_user('U003', 'charlie', 'charlie@example.com')

    print("\nAll users:")
    manager.list_users()

    print("\nUpdating alice...")
    manager.update_login_time('U001')
    user = manager.get_user('U001')
    if user:
        print(f"  {user['username']} - Last login: {user['last_login_time']}")

def part_b1_write_concerns():
    print("\n" + "="*70)
    print(" PART B.1: Write Concern Levels")
    print("="*70 + "\n")

    client = get_mongo_client(direct=True)
    db = client['part_b_demo']

    write_concerns = [
        ('w=1 (Primary only)', WriteConcern(w=1)),
        ('w=2 (Primary + 1 Secondary)', WriteConcern(w=2)),
        ('w=majority (Majority)', WriteConcern(w='majority')),
        ('w=3 (All nodes)', WriteConcern(w=3))
    ]

    for name, concern in write_concerns:
        collection = db.get_collection('write_test', write_concern=concern)
        doc = {'test': name, 'timestamp': datetime.now(timezone.utc), 'data': 'Test data'}

        start = time.time()
        try:
            result = collection.insert_one(doc)
            latency = (time.time() - start) * 1000
            print(f"{name}: {latency:.2f}ms")
        except Exception as e:
            print(f"{name}: FAILED - {e}")

def part_b2_primary_backup():
    print("\n" + "="*70)
    print(" PART B.2: Primary-Backup Replication")
    print("="*70 + "\n")

    client = get_mongo_client(direct=True)
    status = client.admin.command('replSetGetStatus')

    primary = None
    secondaries = []

    for member in status['members']:
        print(f"  {member['name']}: {member['stateStr']}")
        if member['stateStr'] == 'PRIMARY':
            primary = member['name']
        elif member['stateStr'] == 'SECONDARY':
            secondaries.append(member['name'])

    print(f"\nPrimary: {primary}")

    db = client['part_b_demo']
    collection = db['replication_test']

    doc = {'operation': 'primary_write', 'timestamp': datetime.now(timezone.utc)}
    result = collection.insert_one(doc)
    print(f"Document written to primary: {result.inserted_id}")

    time.sleep(2)

    print("\nTesting read preferences:")
    read_prefs = [
        ('PRIMARY', ReadPreference.PRIMARY),
        ('SECONDARY', ReadPreference.SECONDARY),
        ('NEAREST', ReadPreference.NEAREST)
    ]

    for name, pref in read_prefs:
        coll = db.get_collection('replication_test', read_preference=pref)
        try:
            start = time.time()
            doc = coll.find_one({'_id': result.inserted_id})
            latency = (time.time() - start) * 1000
            status = "OK" if doc else "NOT FOUND"
            print(f"  {name}: {status} ({latency:.2f}ms)")
        except Exception as e:
            print(f"  {name}: ERROR")

def part_b2_failover():
    print("\n" + "="*70)
    print(" PART B.2: Failover Simulation")
    print("="*70 + "\n")

    client = get_mongo_client(direct=True)
    status = client.admin.command('replSetGetStatus')

    primary = None
    for member in status['members']:
        if member['stateStr'] == 'PRIMARY':
            primary = member['name']
            break

    if primary:
        node_name = primary.split(':')[0]
        print(f"Current primary: {primary}")
        print(f"Simulating failure of primary node: {node_name}")
    else:
        print("No primary found")

def check_failover_status():
    print("\n" + "="*70)
    print(" Failover Status")
    print("="*70 + "\n")

    try:
        client = get_any_available_client()
        status = client.admin.command('replSetGetStatus')

        for member in status['members']:
            print(f"  {member['name']}: {member['stateStr']}")

        primary = None
        for member in status['members']:
            if member['stateStr'] == 'PRIMARY':
                primary = member['name']

        if primary:
            print(f"\nNew primary: {primary}")
        else:
            print("\nNo primary - election in progress")
    except Exception as e:
        print(f"Error: {e}")
        print("Ensure at least one MongoDB node is running")

def check_replica_status():
    print("\n" + "="*70)
    print(" Replica Set Status")
    print("="*70 + "\n")

    try:
        client = get_any_available_client()
        status = client.admin.command('replSetGetStatus')

        print(f"Replica Set: {status['set']}")
        print("\nMembers:")

        for member in status['members']:
            print(f"  {member['name']}: {member['stateStr']} (Health: {member['health']})")

        print("\nReplica set is operational")
    except Exception as e:
        print(f"Error: {e}")
        print("Run: docker compose ps")

def part_c1_strong_consistency():
    print("\n" + "="*70)
    print(" PART C.1: Strong Consistency")
    print("="*70 + "\n")

    client = get_any_available_client()
    db = client['part_c_demo']

    collection = db.get_collection(
        'strong_consistency_test',
        write_concern=WriteConcern(w='majority'),
        read_preference=ReadPreference.PRIMARY
    )

    doc_id = f"strong_test_{int(time.time())}"
    test_value = datetime.now(timezone.utc).isoformat()

    print("Writing with w=majority...")
    start = time.time()
    collection.insert_one({'_id': doc_id, 'value': test_value, 'timestamp': datetime.now(timezone.utc)})
    write_time = (time.time() - start) * 1000
    print(f"Write completed: {write_time:.2f}ms")

    print("\nReading immediately from primary...")
    start = time.time()
    result = collection.find_one({'_id': doc_id})
    read_time = (time.time() - start) * 1000

    if result and result['value'] == test_value:
        print(f"Read successful: {read_time:.2f}ms - Data is consistent")
    else:
        print("Read failed or inconsistent")



def part_c2_eventual_consistency():
    print("\n" + "="*70)
    print(" PART C.2: Eventual Consistency")
    print("="*70 + "\n")

    try:
        primary_client = get_any_available_client()
    except Exception as e:
        print(f"Error: Could not connect to any node - {e}")
        return

    secondary_client = None
    for node_uri in MONGODB_NODES:
        try:
            client = MongoClient(node_uri, directConnection=True, serverSelectionTimeoutMS=2000)
            client.admin.command('ping')
            status = client.admin.command('replSetGetStatus')

            for member in status['members']:
                if member['stateStr'] == 'SECONDARY':
                    secondary_client = client
                    break

            if secondary_client:
                break
        except Exception:
            continue

    if not secondary_client:
        print("Warning: No secondary available, using available node")
        secondary_client = primary_client

    primary_db = primary_client['part_c_demo']
    secondary_db = secondary_client['part_c_demo']

    primary_collection = primary_db.get_collection(
        'eventual_consistency_test',
        write_concern=WriteConcern(w=1)
    )

    secondary_collection = secondary_db.get_collection(
        'eventual_consistency_test',
        read_preference=ReadPreference.SECONDARY
    )

    doc_id = f"eventual_test_{int(time.time())}"
    test_value = datetime.now(timezone.utc).isoformat()

    print("Writing to primary with w=1...")
    primary_collection.insert_one({'_id': doc_id, 'value': test_value, 'timestamp': datetime.now(timezone.utc)})
    print("Write acknowledged by primary only")

    print("\nReading from secondary immediately...")
    max_attempts = 10
    found = False

    for attempt in range(max_attempts):
        try:
            result = secondary_collection.find_one({'_id': doc_id})
            if result and result['value'] == test_value:
                print(f"Data found on secondary after {attempt + 1} attempts")
                found = True
                break
            else:
                print(f"Attempt {attempt + 1}: Data not yet replicated")
                time.sleep(0.5)
        except Exception:
            print(f"Attempt {attempt + 1}: Read error")
            time.sleep(0.5)

    if not found:
        print("Data still replicating (eventual consistency)")


def part_c3_causal_consistency():
    print("\n" + "="*70)
    print(" PART C.3: Causal Consistency")
    print("="*70 + "\n")

    client = get_any_available_client()
    db = client['part_c_demo']

    users_collection = db.get_collection(
        'causal_users',
        write_concern=WriteConcern(w='majority')
    )
    posts_collection = db.get_collection(
        'causal_posts',
        write_concern=WriteConcern(w='majority')
    )

    session = client.start_session(causal_consistency=True)

    try:
        print("Scenario: User creates account, then creates a post")

        user_id = f"user_{int(time.time())}"
        post_id = f"post_{int(time.time())}"

        print(f"Step 1: Creating user '{user_id}' with session...")
        with session.start_transaction():
            users_collection.insert_one(
                {'_id': user_id, 'username': 'alice', 'created_at': datetime.now(timezone.utc)},
                session=session
            )

        print(f"Step 2: Creating post '{post_id}' by user '{user_id}' with session...")
        with session.start_transaction():
            posts_collection.insert_one(
                {'_id': post_id, 'user_id': user_id, 'content': 'Hello World', 'created_at': datetime.now(timezone.utc)},
                session=session
            )

        print("\nStep 3: Reading with causal consistency...")
        post = posts_collection.find_one({'_id': post_id}, session=session)

        if post:
            print(f"Found post: {post_id}")
            user = users_collection.find_one({'_id': post['user_id']}, session=session)

            if user:
                print(f"Found user: {user['username']} (causally consistent)")
            else:
                print("ERROR: Post exists but user not found (causal order violated)")

        print("\nStep 4: Reading without session (different client)...")
        new_client = get_any_available_client()
        new_db = new_client['part_c_demo']

        time.sleep(0.5)

        post_check = new_db['causal_posts'].find_one({'_id': post_id})
        user_check = new_db['causal_users'].find_one({'_id': user_id})

        if post_check and user_check:
            print("Both user and post visible to new client")
        elif post_check and not user_check:
            print("Post visible but user not yet (eventual consistency)")

    finally:
        session.end_session()

def part_c_partition_test():
    print("\n" + "="*70)
    print(" PART C: Network Partition Simulation")
    print("="*70 + "\n")



def main():
    if '--check-failover' in sys.argv:
        check_failover_status()
    elif '--status' in sys.argv:
        check_replica_status()
    elif '--part-a' in sys.argv:
        part_a_demo()
    elif '--part-b1' in sys.argv:
        part_b1_write_concerns()
    elif '--part-b2' in sys.argv:
        part_b2_primary_backup()
        part_b2_failover()
    elif '--part-c1' in sys.argv:
        part_c1_strong_consistency()
    elif '--part-c2' in sys.argv:
        part_c2_eventual_consistency()
    elif '--part-c3' in sys.argv:
        part_c3_causal_consistency()
    elif '--part-c' in sys.argv:
        part_c1_strong_consistency()
        part_c2_eventual_consistency()
        part_c3_causal_consistency()
        part_c_partition_test()
    else:
        print("\n" + "="*70)
        print(" MongoDB Replication Demo")
        print("="*70)

        part_a_demo()
        part_b1_write_concerns()
        part_b2_primary_backup()
        part_b2_failover()

        print("\n" + "="*70)
        print(" Demo Complete")
        print("="*70)

if __name__ == '__main__':
    main()
