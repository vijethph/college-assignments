from pymongo import MongoClient, WriteConcern, ReadPreference
from datetime import datetime, timezone
import time
import os
import sys

MONGODB_URI = os.getenv(
    'MONGODB_URI',
    'mongodb://x/?replicaSet=rs0&authSource=admin'
)

MONGODB_DIRECT_URI = 'mongodb://x/?authSource=admin'

MONGODB_NODES = [
    'mongodb://x/?authSource=admin',
    'mongodb://x/?authSource=admin',
    'mongodb://x/?authSource=admin'
]

def get_mongo_client(direct=False):
    if direct or os.getenv('MONGODB_URI') is None:
        return MongoClient(MONGODB_DIRECT_URI, directConnection=True, serverSelectionTimeoutMS=5000)
    else:
        return MongoClient(MONGODB_URI)

def get_any_available_client():
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
    else:
        print(" MongoDB Replication Demo")

        part_a_demo()
        part_b1_write_concerns()
        part_b2_primary_backup()
        part_b2_failover()

if __name__ == '__main__':
    main()
